# Mock DataBricks spark API for testing
from copy import deepcopy

class MockCol(object):
    def __init__(self, name):
        self.name = name

    def alias(self, name,metadata={"meta":"data"}):
        return name

    def contains(self, value):
        return True

    def desc(self):
        return True

class MockWriter(object):
    def __init__(self, df): self.df = df
    def csv(self, arg): return self
    def mode(self, arg): return self
    def option(self, *arg): return self
    def format(self, arg): return self
    def saveAsTable(self, arg): return self

class MockFrame(object):
    def __init__(self):
        self.items = {}
        self.columns = []
        self.write = MockWriter(self)

    def __getitem__(self, item):
        return self.items[item] if item in self.items else MockCol(item)

    def select(self, *input):
        columns = list(input.values()) if isinstance(input, dict) else input
        self.columns = columns
        for col in columns:
            mcol = MockCol(col)
            setattr(self, col, mcol)
            self.items[col] = mcol
        return self

    def drop(self, col):
        try:
            cols = list(self.columns)
            cols.remove(col)
            self.columns = cols
        except ValueError: print("skipping: drop")
        return self

    def agg(self, *aggs): return self
    def count(self): return 1
    def coalesce(self, arg): return self
    def distinct(self): return self
    def filter(self, arg): return self
    def groupby(self, *arg): return self
    def join(self, df_from, join, how): return deepcopy(df_from)
    def orderBy(self, arg): return self
    def pivot(self, arg): return self
    def sort(self, arg): return self
    def union(self, arg): return self
    def withColumn(self, *arg): return self

class MockSpark(object):
    def __init__(self):
        self.columns = []
    def setCurrentDatabase(self, db):
        print(f"setCurrentDatabase: {db}")

    def table(self, table_name):
        df = MockFrame()
        df.name = table_name
        return df

spark = MockSpark()
spark.catalog = spark#.setCurrentDatabase
