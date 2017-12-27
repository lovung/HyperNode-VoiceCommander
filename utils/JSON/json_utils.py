import json

# the simple funtion to generate the JSON
def jsonSimpleGenerate(key, value):
    try:
        data = {}
        data[key] = value
        jsonData = json.dumps(data)
        return jsonData
    except Exception as e:
        raise e
        return -1

def jsonSimpleParser(jsonStr, key):
    try:
        print("String JSON: " + jsonStr)
        print("key: " + key)
        return json.loads(jsonStr)[key] #.decode('utf-8')
    except Exception as e:
        raise e
        return -1

def jsonDoubleGenerate(json_1, json_2):
    try:
        jsonData = json.dumps(json_1)
        jsonData = json.dumps(json_2)
        print(str(jsonData))
        return jsonData
    except Exception as e:
        raise e
        return -1
