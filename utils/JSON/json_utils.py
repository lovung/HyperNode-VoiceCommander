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

def jsonSimpleParsor(jsonStr, key):
    try:
        print("String JSON: " + jsonStr)
        print("key: " + key)
        return json.loads(jsonStr)[key] #.decode('utf-8')
    except Exception as e:
        raise e
        return -1
