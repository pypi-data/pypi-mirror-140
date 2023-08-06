import time, yaml
from operator import itemgetter
from .keys import *
from .helpers import *

def flags_compile(flags):
    first = flags[0]
    faction = {
        "id": f"compile_flags_{len(flags)}",
        "do": "flags",
        "from": first["from"],
        "flags":  flags,
    }
    return faction

class ActionTimer:
    def __init__(self, times):
        self.times = times
        self.reset()

    def reset(self):
        self.start = time.perf_counter()
        self.end = self.start

    def update(self, action):
        self.end = time.perf_counter()
        self.times[action['id']] = self.end - self.start
        self.start = self.end

#
# CQML Virtual Machine
#

class VM:
    def __init__(self, yaml, spark):
        self.spark = spark
        self.yaml = yaml
        self.actions= yaml["actions"]
        self.cactions = []
        self.macros = {}
        self.compile(self.actions)
        self.last = self.cactions[0]
        self.debug = False
        self.skip_errors = False
        self.df = {}
        self.sizes = {}
        self.times = {}

    def key_actions(self, key):
      return {a['id']: a[key] for a in self.cactions if (key in a) and (kSkip not in a)}

    def saveable(self):
      saves = self.key_actions(kSave)
      for id, save in saves.items():
        if save != 'series':
          drop_table(self.spark, id)
      return saves

    def save(self, id, df, type):
        size = df.count()
        action = {
            "id": id,
            "do": kSave,
            "size": size,
            kSkip: True
        }
        if size > 0:
          action[kSave] = type
        #print(action)
        self.cactions[:0] = [action]
        self.df[id] = df
        return df

    def log(self, str, name=False):
      if self.debug:
         if name: print(name)
         print(str)

    def macro(self, todo, action):
        mdef = todo.split("|")
        mcall = todo.split(".")

        if len(mdef) > 1:
            action['do'] = mdef[1]
            self.macros[action['id']] = yaml.dump(action)
            return 0
        key = mcall[1]
        template = self.macros[key]
        expanded = template.format(**action)
        #print(expanded)
        dict = yaml.safe_load(expanded)
        dict['id'] = action['id']
        self.cactions.append(dict)
        return 1

    def compile(self, action_dict):
        flags = []
        for id, action in action_dict.items():
            action['id'] = id
            todo = action['do']

            if (todo=='flag') and (action['from'] == "$id"):
                flags.append(action)
            elif len(flags) > 0:
                faction = flags_compile(flags)
                self.cactions.append(faction)
                self.cactions.append(action)
                flags = []
            elif 'macro' in todo:
                self.macro(todo, action)
            else:
                self.cactions.append(action)

        if len(flags) > 0:
            faction = flags_compile(flags)
            self.cactions.append(faction)
        return self.cactions

    def run(self, only=None):
      out = None
      timer = ActionTimer(self.times)
      for action in self.cactions:
          self.log(f"run[{action['id']}]: action['do']")
          if kSkip not in action:
            #if only and action['do'] == only:
              out = self.perform(action)
              timer.update(action)
      return out

    def get_key(self, name):
        key = self.last[name[1:]] if name[0] == '$' else name
        #self.log(f"get_key: {name} -> {key}")
        return key

    def get_frame(self, name):
        key = self.get_key(name)
        return self.df[key]

    def set_frame(self, name, frame):
        key = self.get_key(name)
        self.df[key] = frame

    def test_action(self, n, show=False):
        action = self.cactions[n]
        id = action['id']
        return test_id(self, id, show)

    def test_id(self, id, show=False):
        action = self.actions[id]
        self.log(f"# {id}: {action}")
        self.perform(action)
        df = self.df[id]
        if show and not isinstance(df, dict):
            df.show()
        return df

    def ensure_unique(self, df, key):
        all = df.select(key)
        #print(all)
        unique = all.distinct()
        #print(unique)
        n_dupes = all.count() - unique.count()
        if (n_dupes != 0):
          msg = f"ensure_unique.{key}[{n_dupes}] = {all.count()} - {unique.count()}"
          self.log(msg)
          if not self.skip_errors:
            raise Exception("FAIL."+msg)
        return df

    def perform(self, action):
        id, do = itemgetter('id', 'do')(action)
        print(f'perform[{do}]: {id}')
        method = getattr(self, f'do_{do}')
        df = method(action)
        self.sizes[id] = len(df) if isinstance(df, dict) else df.count()
        df = self.ensure_unique(df, action[kUniq]) if kUniq in action else df
        df = df.sort(df[action[kSort]].desc()) if kSort in action else df
        self.set_frame(id, df)
        self.last = action
        return df
