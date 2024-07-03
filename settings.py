import json

SETTINGS_PATH = "settings.json"


def saveSetting(name, value):
    with open(SETTINGS_PATH, 'r+') as f:
        data = json.load(f)
        data[name] = value
        f.seek(0)
        json.dump(data, f)
        f.truncate()


def getSetting(name):
    with open(SETTINGS_PATH, 'r') as f:
        try:
            return json.load(f)[name]
        except:
            saveSetting(name,"")
            return ""


def getSettings():
    with open(SETTINGS_PATH, 'r') as f:
        return json.load(f)
