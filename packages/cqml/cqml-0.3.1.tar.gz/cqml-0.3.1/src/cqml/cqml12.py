from .keys import *

kDoc_OLD="doc"

def is_v02(yaml_data): return isinstance(yaml_data, dict)

def convert_action(action):
    if kDoc_OLD in action:
        doc = action.pop(kDoc_OLD)
        action[kDoc] = doc
    if kCols in action:
        cols = action.pop(kCols)
        if cols != "all":
            colmap = {key: "tbd" for key in cols}
            action[kCols] = colmap
    return action

def upgrade(cqml1):
    actions = {}
    for action in cqml1:
        print(action)
        id = action["id"]
        action.pop("id")
        new_action = convert_action(action)
        actions[id] = action
    cqml2 = {
      "cqml": 0.2,
      "actions": actions
    }
    return cqml2

def ensure_v02(yaml_data):
    return yaml_data if is_v02(yaml_data) else upgrade(yaml_data)
