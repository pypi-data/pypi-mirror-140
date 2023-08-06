import yaml
import os,shutil
from .db2quilt import cvm2pkg
from .cvm import CVM
from .cqml12 import ensure_v02

class CQML(CVM):
    def __init__(self, yaml_data, spark):
        super().__init__(yaml_data, spark)

    def do_run(self, action):
        runs = action['pipes']
        pkgs = {cqml:pkg_cqml(cqml, self.spark) for cqml in runs}
        return pkgs

    def do_save(self, action):
        pkg = cvm2pkg(cvm)
        return pkg

def upgrade_file(yaml_file):
    print("Upgrading "+yaml_file)
    with open(yaml_file) as data:
        raw_yaml = yaml.full_load(data)
        v02 = ensure_v02(raw_yaml)
    print(v02)
    with open(yaml_file, 'w') as file:
        yaml.dump(v02, file, sort_keys=False)

def from_file(yaml_file, spark):
    print("Loading "+yaml_file)
    with open(yaml_file) as data:
        raw_yaml = yaml.full_load(data)
        v02 = ensure_v02(raw_yaml)
        return CQML(v02, spark)

def make_frames(yaml_file, spark, debug=False):
    cvm = from_file(yaml_file, spark)
    if debug:
        cvm.debug = True
    cvm.run()
    return cvm

def load_cqml(name, spark, folder="pipes"):
    yaml_file=f"{folder}/{name}.yml"
    return from_file(yaml_file, spark)

def exec_cqml(name, spark, folder="pipes"):
    cvm = load_cqml(name, spark, folder)
    cvm.run()
    return cvm

def pkg_cqml(name, spark, folder="pipes"):
    print("\npkg_cqml: "+name)
    cvm = exec_cqml(name, spark, folder)
    pkg = cvm2pkg(cvm)
    return {'pkg': pkg, 'html': pkg.html,  'url': pkg.url, 'actions': cvm.actions}

def pkg_all(spark, folder="pipes"):
    files = os.listdir(folder)
    keys = [os.path.splitext(file)[0] for file in files if file.endswith("ml")]
    keys.sort()
    print(keys)
    pkgs = {key:pkg_cqml(key, spark, folder) for key in keys}
    return pkgs
