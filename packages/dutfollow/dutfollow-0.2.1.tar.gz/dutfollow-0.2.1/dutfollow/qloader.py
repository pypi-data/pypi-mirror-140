import json

qloaded = {}

def qLoad(s: str):
    if s in qloaded:
        return qloaded[s]
    else:
        f = open(f"{s}.txt", "r")
        t = json.loads(f.read())
        f.close()
        qloaded[s] = t
        return t
