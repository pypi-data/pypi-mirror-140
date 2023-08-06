#!/usr/bin/env python3

"""
## db2quilt - integrating Quilt Packages into DataBricks
"""
import shutil, os, re, json
import pandas as pd
import quilt3 as q3
import nbformat as nbf
from .keys import *
from .helpers import *
from operator import itemgetter
from datetime import datetime,date,timezone
import pytz
time_format = "%A, %d %b %Y %H:%M:%S %p"

from pathlib import Path
import pprint
pp = pprint.PrettyPrinter(indent=4)
QPKG = q3.Package()

def cleanup_names(df):
    for c in df.columns:
        #print(c)
        if 'nam' in c.lower():
            df = df.withColumn(c, f.regexp_replace(c, ',.*$', ''))
    return df

try:
    import pyspark.sql.functions as f
    f.col('f')
except AttributeError:
    f = mock_functions()

#
# Package Directory
#

DBFS="/dbfs"
DELTA_TABLE="delta"
PYROOT=DBFS+"/FileStore"
PKG_DIR = "quilt"
TEMP_DIR="/FileStore/tmp_export"
PYTEMP=DBFS+TEMP_DIR
def to_dir(s): return s.replace(DBFS,'')

def save_table(df, name, mode="overwrite"):
    """saves into managed delta tables in default database"""
    table_name = f'{DB_NAME}.{name}'
    print(f"save_table[{mode}]: {table_name}")
    df = df.withColumn(DATE_COL, f.current_timestamp())
    df.write\
      .format(DELTA_TABLE) \
      .mode(mode) \
      .option("mergeSchema", "true") \
      .saveAsTable(table_name)
    return table_name

def show_dir(dir):
    for root, dirs, files in os.walk(dir):
       print(root)
       for name in files:
          f = os.path.join(root, name)
          print(f"{f}: {os.path.getmtime(f)}")
#print(PKG_DATA)
def make_dir(dir):
    os.makedirs(dir,exist_ok=True)
    #show_dir(dir)

#
# NoteBook Configuration
#

NB_SUMMARY="quilt_summarize.json"
NB_KERNEL = {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
 }
NB_IMPORT= """
import pandas as pd
import quilt3 as q3
import io
import os
from perspective import PerspectiveWidget
bucket = os.environ.get("QUILT_PKG_BUCKET")
handle = os.environ.get("QUILT_PKG_NAME")
top_hash = os.environ.get("QUILT_PKG_TOP_HASH")
"""
def make_notebook():
    nb = nbf.v4.new_notebook()
    nb['cells'] = []
    nb.metadata['kernelspec'] = NB_KERNEL
    return nb

def make_cell(data, flag=True):
    return nbf.v4.new_code_cell(data) if flag else nbf.v4.new_markdown_cell(data)

def make_slug(name): return re.sub(r'[^\w-]', '_', name.lower())

"""
Quilt Wrappers
"""

class Project:
    def __init__(self, config):
        org, bucket, project = itemgetter('org','s3.bucket','project')(config)
        pkg_dir = config['catalog'] if 'catalog' in config else PKG_DIR
        root = config['root'] if 'root' in config else PYROOT
        self.repo = "s3://"+bucket
        self.url = f"https://quilt.{org}.com/b/{bucket}/packages"
        self.name = project
        self.path = f"{root}/{pkg_dir}"

    def package(self, id):
        return Package(id, self)

class Package:
    def __init__(self, id, proj, reset=False):
        self.id = id
        self.name = f"{proj.name}/{id}"
        self.proj = proj
        self.url = f"{proj.url}/{self.name}/"
        self.path = f"{proj.path}/{self.name}/"
        self.dir = to_dir(self.path)
        if reset:
            shutil.rmtree(self.path,ignore_errors=True)
        make_dir(self.path)
        self.summaries={}

    def setup(self):
        QPKG.install(self.name, registry=self.proj.repo, dest=self.path)

    def read_csv(self, filename):
        path = self.path+filename
        print(path)
        df = pd.read_csv(path)
        self.proj.cleanup_dates(df)
        return df

    def cleanup(self, msg, meta = {"db2quilt":"v0.1"}):
        self.write_summary()
        QPKG.set_dir('/',path=self.path, meta=meta)
        QPKG.push(self.name, self.proj.repo, message=msg, force=True)
        #shutil.rmtree(self.path)
        self.html = f'Published <a href="{self.url}">{self.name}</a> for <b>{msg}</b>'
        return self

    def export(self, dfs, key):
        pfile = f"{key}.parquet"
        cfile = f"{key}.csv"
        df = cleanup_names(dfs[key])
        save_table(df, key)
        self.save_file(df, cfile)
        msg = self.save_file(df, pfile)
        doc = self.to_report(pfile, msg)
        return doc

    def copy_file(self, source, dest_name=False):
        """into package"""
        path = self.path + (dest_name if dest_name else source)
        print(path)
        shutil.copy(source, path)

    def save_file(self, df, filename):
        """stores spark dataframes in dbfs"""
        is_pq = filename.endswith(".parquet")
        type = ".parquet" if is_pq else ".csv"
        path = self.path+filename
        print(path)
        writer = df.coalesce(1).write.mode('overwrite').option("header", "true")
        writer.parquet(TEMP_DIR) if is_pq else writer.csv(TEMP_DIR)
        try:
            files = os.listdir(PYTEMP)
            file_path = next(f"{PYTEMP}/{f}" for f in files if f.endswith(type))
            shutil.copy(file_path, path)
            shutil.rmtree(PYTEMP)
        except os.error:
            print(f'os.error: "{PYTEMP}" not found')
        return path

    def save_dict(self, dict, key):
        path = f"{self.path}{key}.json"
        json_string = json.dumps(dict)
        with open(path, 'w') as outfile:
            outfile.write(json_string)
        return path

    def to_report(self, datafile, doc='Auto-Generated Report'):
        name = Path(datafile).resolve().stem
        cell_pairs=[
            [False, doc],
            [False, f"Rendering {datafile}"],
            [True, NB_IMPORT],
            [True, f"%%capture\npkg = q3.Package.browse(handle, 's3://'+bucket, top_hash=top_hash)"],
            [True, f"data = pkg['{datafile}']()"],
            [True, f"PerspectiveWidget(data)"]
        ]
        return self.to_notebook(name, cell_pairs)

    def to_notebook(self, name, cell_pairs):
        print("to_notebook: "+name)
        title = f"# {name}"
        cell_pairs.insert(0, [False, title])
        nb = make_notebook()
        for row in cell_pairs:
            cell = make_cell(row[1], row[0])
            nb['cells'].append(cell)
        path = self.write_notebook(name, nb)
        self.summaries[name] = path
        return f"{self.now()}: {path}"

    def now(self, zone='US/Pacific'):
        tz = pytz.timezone(zone)
        now = datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=tz)
        return now.strftime(time_format) + f' ({zone})'

    def write_notebook(self, name, nb):
        slug = make_slug(name)
        filename = slug + ".ipynb"
        path = self.path+filename#
        print('write_notebook: '+path)
        with open(path, 'w') as f: nbf.write(nb, f)
        return filename

    def write_summary(self):
        entries = []
        for title, file in self.summaries.items():
            entry = {
                "title": title,
                "path": file,
                "types": ["voila"]
            }
            entries.append(entry)
        path = self.path+NB_SUMMARY
        with open(path, 'w') as f:
            jsonString = json.dumps(entries)
            f.write(jsonString + "\n")
        print(path)
        return path

#
# Helpers
#


def save_ext(pkg, dfs, key, ext, debug=False):
    print(f'save_ext: {ext} for {key} in {pkg.name}')
    id = f'{key}_debug' if debug else key
    if ext == "report":
        return pkg.export(dfs, key)
    elif ext == "table":
        return save_table(dfs[key], id)
    elif ext == "daily":
        return save_table(dfs[key], id, "append")
    return pkg.save_file(dfs[key], f'{id}.{ext}')

def exract_pkg(cvm):
    id, config = itemgetter('id','meta')(cvm.yaml)
    proj = Project(config)
    pkg_id = id + "-debug" if cvm.debug == True else id
    print("exract_pkg: "+pkg_id)
    pkg = proj.package(pkg_id)
    return pkg

def cvm2pkg(cvm):
    pkg = exract_pkg(cvm)
    cvm.pkg = pkg
    cvm.run()
    doc = cvm.key_actions('doc')
    doc["cvm.actions"] = cvm.actions
    pkg.save_dict(cvm.actions, pkg.id)
    msg = pkg.now()
    files = cvm.saveable()
    for key in files:
        ext = files[key]
        save_ext(pkg, cvm.df, key, ext, cvm.debug)
    try:
        pkg.copy_file(f'{pkg.id}.md','README.md')
        pkg.copy_file(f'REPORT_HELP.md')
    except FileNotFoundError as err:
        print(err)
        #cvm.log(err)
    return pkg.cleanup(msg, doc)
