#
# Utility Functions
#

from .keys import *

def mock_functions():
    from collections import namedtuple
    keys = "lit,col,desc,expr,sum,min,count,alias,concat_ws,current_date,current_time,current_timestamp,countDistinct,orderBy,over,partitionBy,row_number".split(',')
    func = namedtuple("Func",keys)
    f1 = func(*keys)
    l1 = [lambda *args, **kw: getattr(f1,key) for key in keys]
    f2 = func(*l1)
    l2 = [lambda *args, **kw: f2] * len(keys)
    return func(*l2)

try:
    import pyspark.sql.functions as f
    f.col('f')
except AttributeError:
    f = mock_functions()

def alias_columns(df, columns, table='.'):
    new_columns = []
    for col in columns:
        split = col.split(cAlias)
        col_name = split[0]
        alias_name = split[1] if len(split) > 1 else col_name
        meta = None if col_name == alias_name else { 'comment': f'WAS[{table}.{col_name}]' }
        entry = df[col_name].alias(alias_name,metadata=meta)
        new_columns.append(entry)
    return new_columns

def cast_columns(df, matching, type):
    for c in df.columns:
        if matching.lower() in c.lower():
            #print(f.col(c))
            df = df.withColumn(c, f.col(c).cast(type))
    return df

def drop_column(df, col):
    try:
        return df.drop(col)
    except AnalysisException:
        return df

def drop_table(spark, id):
    spark.sql(f'drop table if exists {DB}.{id}')

def flag2sql(action):
    where = action['where']
    condition = make_expr(where)
    action[kSQL] =f"CASE WHEN {condition} THEN true END"
    return action

def get_cols(action, df):
    return list(action[kCols].keys()) if kCols in action else df.columns

def make_list(col): return list([row[0] for row in col.collect()])

def make_aggregates(agg):
  aggs = []
  for field in agg:
    relation = agg[field]
    method = getattr(f, relation)
    col = method(field)
    meta = { 'comment': f'{field}: {relation}' }
    alias = f'n_{field}' if relation == 'count' else f'{relation}_{field}'
    name = col.alias(alias, metadata=meta)
    aggs.append(name)
  return aggs

def make_any(field, sub_query):
    any_expr = [sql_expr(field, op, value) for value, op in sub_query.items()]
    return f'({" OR ".join(any_expr)})'

def make_expr(query):
    field_expr = [make_any(field, query[field]) for field in query.keys()]
    return " AND ".join(field_expr)

def join_expr(df_into, df_from, joins):
  expression = join_item(df_into, df_from, joins[0])
  return expression

def join_item(df_into, df_from, item):
  key_into = item[0]
  key_from = item[1]
  if cAlias in key_from:
      key_from = key_from.split(cAlias)[1]
  expression = (df_into[key_into] == df_from[key_from])
  return expression

def sql_expr(field, op, value):
  if op == "contains":
    return f"({field} LIKE '%{value}%')"
  if op == "equals":
    return f"case {field} when {value} then true else null end"
  if op == "greater":
    return f"({field} > {value})"
  if op == "lesser":
    return f"({field} < {value})"
  if op == "notgreater":
    return f"({field} <= {value})"
  if op == "notlesser":
    return f"({field} >= {value})"
  if op == "not_contains":
    return f"({field} NOT LIKE '%{value}%')"
  if op == "is_not":
    return f"({field} IS NOT NULL)"
  if op == "is":
    return f"({field} IS NULL)"
  return f"sql_expr: ERROR Unknown operator {op}"

def summarize(df, table, col, count, now):
    dc = df.groupby(col).agg(f.countDistinct(count))
    dsum = dc.select(
      f.lit(table).alias('table'),
      f.lit(col).alias('column'),
      f.col(col).alias('value'),
      f.col(f'count({count})').alias('count'),
      f.current_date().alias('date'),
      f.lit(now).alias('timestamp'),
    )
    return dsum.orderBy('value')
