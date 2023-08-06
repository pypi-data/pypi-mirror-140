from functools import reduce
from operator import itemgetter
from .keys import *
from .helpers import *
from .vm import VM

try:
    import pyspark.sql.functions as f
    f.col('f')
except AttributeError:
    f = mock_functions()

HAS_TEMPO=True
try:
  from tempo import TSDF
except ImportError:
  HAS_TEMPO=False
  pass

HAS_BOX=True
try:
  from boxsdk import OAuth2, Client
  from boxquilt import BoxQuilt
except ImportError:
  HAS_BOX=False
  pass

class CVM(VM):
    def __init__(self, yaml, spark):
        super().__init__(yaml, spark)

    def do_assign(self, action):
        id, from_key = itemgetter('id','from')(action)
        df_from = self.get_frame(from_key)
        return df_from

    def do_box(self, action):
        print('do_box')
        from_key, group, config = itemgetter('from','group','box')(action)
        df_from = self.get_frame(from_key)
        if not HAS_BOX or not cvm.pkg:
            return df_from
        sort = action[kSort] if kSort in action else [group]
        self.log('do_box: init')
        bq = BoxQuilt(group, sort, cvm, config)
        self.log('do_box: save_groups')
        bq.save_groups(df_from, kSkipSave in action) #
        self.log('do_box: load_groups')
        bq.load_groups()
        self.log('do_box: create_or_update_box')
        bq.create_or_update_box(kSkipUpload in action) #
        self.log('do_box: box_table')
        df = bq.box_table()
        return df

    def do_call(self, action):
        fn, args  = itemgetter(kFunc,kArgs)(action)
        arglist = ",".join(args)
        action[kSQL] = f'{fn}({arglist})'
        return self.do_eval(action)

    def do_eval(self, action):
        id, from_key, sql = itemgetter('id','from',kSQL)(action)
        df_from = self.get_frame(from_key)
        self.log(' - do_eval: '+sql)
        meta = { 'comment': f'{id}: {sql}' }
        df = df_from.withColumn(id, f.expr(sql))
        return df

    def do_flag(self, action):
        sql_action = flag2sql(action)
        return self.do_eval(sql_action)

    # TODO: Optimize creating multiple columns
    def do_flags(self, action):
        """
        url='https://stackoverflow.com/questions/41400504/spark-scala-repeated-calls-to-withcolumn-using-the-same-function-on-multiple-c/41400588#41400588'
        window = Window.partitionBy("ID").orderBy("time")
        df.select(
            "*", # selects all existing columns
            *[
                F.sum(col).over(windowval).alias(col_name)
                for col, col_name in zip(["A", "B", "C"], ["cumA", "cumB", "cumC"])
            ]
        )
        expr_map = {f['id']: flag2sql(f)[kSQL] for f in flags}
        df = createColumns(df, expr_map)
        """

        from_key,flags = itemgetter('from','flags')(action)
        df = self.get_frame(from_key)
        for faction in flags:
            print(faction)
            sql_action = flag2sql(faction)
            id, sql = itemgetter('id',kSQL)(sql_action)
            self.log(sql)
            df = df.withColumn(id, f.expr(sql))
        return df

    def do_group(self, action):
        from_key,agg = itemgetter('from','agg')(action)
        df_from = self.get_frame(from_key)
        aggs = make_aggregates(agg)
        cols = get_cols(action, df_from)
        df = df_from.groupby(*cols).agg(*aggs)
        name = '_'.join(cols)
        df = df.withColumn(name, f.concat_ws(".", *cols))
        return df

    def do_latest(self, action, latest=True):
        name, tables = itemgetter('id', 'tables')(action)
        id = name.split('.')[0] if "." in name else name
        self.spark.catalog.setCurrentDatabase(id)
        group = [DATE_UNIQ] if kCols not in action else get_cols(action, None)
        for key in tables:
          if key not in self.df:
              table_name = tables[key]
              df = self.spark.table(table_name)
              if latest:
                  df = unique(df, DATE_COL, group)
              print(f" - {key}: {table_name}")
              self.set_frame(key, df)
        return self.df

    def do_load(self, action):
        df = self.do_latest(action, False)
        return df

    def do_loadfiles(self, action):
        folder, files = itemgetter('id', 'tables')(action)
        for key in files:
          file_name = files[key]
          path = f"file:{folder}/{file_name}"
          df = self.spark.read.format("csv").option("header","true").load(path)
          print(f" - {key}[{file_name}]: {path}")
          df = cast_columns(df, action[kCast], "int") if kCast in action else df
          self.set_frame(key, df)
        return self.df

    def do_merge(self, action):
        id, into, join = itemgetter('id', 'into', 'join')(action)
        join_how = action[kJoinType] if kJoinType in action else 'left'
        df_into = self.get_frame(into)
        df_from = self.do_select(action)
        cols = get_cols(action, df_from)
        if not df_from:
          return None
        join_into = join if isinstance(join, list) else [join]
        n_joins = len(join_into)
        join_from = cols[:n_joins]
        del cols[:n_joins]
        joins = list(zip(join_into, join_from))
        expression = join_expr(df_into, df_from, joins)
        df = df_into.join(df_from, expression, join_how)
        if kKeepJoin not in action:
            return df.drop(*join_from) if join_how == kInner else df.drop(*join_from, *join_into)
        keep = action[kKeepJoin]
        self.log(f'keep: {keep}')
        if keep == 'left':
            df = df.drop(*join_from)
        elif keep == 'right':
            df = df.drop(*join_into)
        return df

    def do_pivot(self, action):
        from_key, agg, pivot = itemgetter('from','agg','pivot')(action)
        df_from = self.get_frame(from_key)
        aggs = make_aggregates(agg)
        cols = get_cols(action, df_from)
        df = df_from.groupby(*cols).pivot(pivot).agg(*aggs)
        df = df.withColumn(action['id']+"_pkey", f.concat_ws(".", *cols))
        return df

    def do_rebin(self, action):
        values = action['values']
        clauses = []
        for value in values:
          condition = make_expr(values[value])
          sql = f"WHEN {condition} THEN '{value}'" # value must be a literal
          clauses.append(sql)
        action[kSQL] =f"CASE {' '.join(clauses)} END"
        return self.do_eval(action)

    def do_resample(self, action):
        from_key,ts,freq,func = itemgetter('from','time','freq','func')(action)
        cols = get_cols(action, df_from)
        df_from = self.get_frame(from_key)
        df_ts = TSDF(df_from,ts_col=ts,partition_cols=cols)
        df_re = df_ts.resample(freq=freq, func=func, fill=True)#.interpolate(method="linear")
        return df_re.df

    def do_select(self, action):
        from_key = itemgetter('from')(action)
        df = self.get_frame(from_key)
        cols = get_cols(action, df)
        if 'where' in action:
            expression = make_expr(action['where'])
            self.log(' - do_select: '+expression)
            df = df.filter(expression)
        if 'dedupe' in action:
            df = df.drop_duplicates([action['dedupe']])
        column_map = alias_columns(df, cols, from_key)
        return df.select(*column_map)

    def do_summary(self, action):
        from_key = action['from']
        df_from = self.get_frame(from_key)
        cols = get_cols(action, df_from)
        count = action['count']
        now = None
        now = f.current_timestamp()
        id = self.get_key(from_key)
        sums = [summarize(df_from, id, col, count, now) for col in cols]
        df = reduce(lambda x, y: x.union(y), sums)
        return df

    def do_unique(self, action):
        N = "windowIndx"
        id, key, sort = itemgetter('id', 'from', kSort)(action)
        df_from = self.get_frame(key)
        cols = get_cols(action, df_from)
        df = unique(df_from, sort, cols)
        return df

    def do_update(self, action):
        id, from_key, join = itemgetter('id','from','join')(action)
        old = self.spark.table(f'{DB}.{id}')
        new = self.get_frame(from_key)
        for c in new.columns:
            if c != join:
                old = drop_column(old, c)
        df = old.join(new, join)
        return df
