# BOX Configuration for Quilt

from .db2quilt import make_dir

#FILE_EXT='csv'
#BOX_ROOT='3G_Sunset'
#BOX_ROOTID=154982259864
#EXPIRY_DATE='2022-02-29'
#DATA_DIR="raw"
BOX_KEYS="client_id,client_secret,enterprise_id,jwt_key_id,rsa_private_key_file_sys_path,rsa_private_key_passphrase".split(',')

from boxsdk import Client, OAuth2, JWTAuth
from pyspark.sql import Row
from pyspark.sql.functions import udf,lit
from pyspark.sql.types import StringType
import os

def dir_row(folder):
  for file in folder.get_items():
    row = {
      "sf_id": folder.get().name,
      "box_file": file.name,
      "box_url": file.get().shared_link['url'],
      "box_id": file.id,
      "download_url": file.get().shared_link['download_url']
    }
    return row

def get_file_url(file, until):
    url = file.get_shared_link(access='open',unshared_at=until,allow_preview=True)
    return url

def get_secrets(cf, scope, keys):
    return {key: cf.get(f"spark.{scope}_{key}") for key in keys}

class BoxQuilt:

    def __init__(self, key, sort, cvm, config):
        self.spark = cvm.spark
        self.client = self.jwt_init() #token_init()#
        self.root = self.client.folder(config['root_id'])
        self.key = key
        self.sort = sort
        self.pkg = cvm.pkg
        self.dir = self.pkg.dir + config['data_dir']
        self.path = self.pkg.path + config['data_dir']
        self.until = config['expiration_date']
        self.root = config['root_folder']
        self.ext = config['file_ext']
        make_dir(self.path)
        self.rows = {}

    def token_init(self):
        cf = get_secrets(self.spark.conf, "token", ['client_id','client_secret','access_token'])
        auth = OAuth2(
          client_id=cf['client_id'],
          client_secret=cf['client_secret'],
          access_token=cf['access_token'],
        )
        client = Client(auth)
        me = client.user().get()
        print(f'BOX: Authenticated {me.name} with {me.id}')
        return client

    def jwt_init(self):
        cf = get_secrets(self.spark.conf, "box", BOX_KEYS)
        auth = JWTAuth(client_id=cf['client_id'],
          client_secret=cf['client_secret'],
          enterprise_id=cf['enterprise_id'],
          jwt_key_id=cf['jwt_key_id'],
          rsa_private_key_file_sys_path=cf['rsa_private_key_file_sys_path']
        )
        access_token = auth.authenticate_instance()
        client = Client(auth)
        user = client.user().get()
        print(f'box_init: Service Account user ID is {user.id} @ {user.login}')
        return client

    def get_file_urls(self, file_id):
        file = self.client.file(file_id)
        file_info = file.get()
        info = {
          "shared_link": file_info.shared_link,
          "get_download_url": file.get_download_url()
        }
        return info

    def save_groups(self, df, skipSave=False):
        if not skipSave:
            print("not skipSave")
            df.coalesce(1).sort(*self.sort).write.mode("overwrite").partitionBy(self.key).option("header", "true").csv(self.dir)
        files = os.listdir(self.path)
        msg = f"{self.key}: {self.pkg.now()} <{len(files)}>"
        print(msg)
        self.pkg.cleanup(msg, meta=files)
        return files

    def box_entries(self):
        return [dir_row(folder) for folder in self.root.get_items()]

    def load_groups(self):
      for root, dirs, files in os.walk(self.path, topdown = False):
         for file in files:
            if file.endswith(self.ext):
              sf_id = root.split("=")[1]
              path = os.path.join(root, file)
              filename = f'{self.root}_{sf_id}.{self.ext}'
              print(filename)
              self.rows[sf_id] = {"sf_id": sf_id, "dir": root, "db_file":file, "db_path":path, "box_file": filename}
      return self.rows

    def create_or_update_box(self, skipUpdate=False):
        children = self.root.get_items()
        folders = {item.name: item.id for item in children}
        box = list(folders.keys())
        dbfs = list(self.rows.keys())
        to_create = list(set(dbfs) - set(box))
        to_update = list(set(dbfs).intersection(box))
        print(f"create:{len(to_create)} update:{len(to_update)}")

        n = 0
        for name in to_create:
            n += 1
            row = self.rows[name]
            folder = self.root.create_subfolder(name)
            file = folder.upload(row["db_path"], file_name=row["box_file"], file_description=row["db_file"])
            row['box_url'] = get_file_url(file, self.until)
            print(f"{n} create[{file.id}]: {file.name}")

        n = 0
        for name in to_update:
            n += 1
            row = self.rows[name]
            file_path = row["db_path"]
            folder_id = folders[name]
            folder = self.client.folder(folder_id)
            for file in folder.get_items():
                print(f"{n} update[{file.id}]: {file.name}")
                if not skipUpdate:
                    file.update_contents(file_path)
                row['box_url'] = get_file_url(file)

        return self.rows

    def box_table(self):
        array = list(self.rows.values())
        return self.spark.createDataFrame([Row(**i) for i in array])
