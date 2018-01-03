import json

# the simple funtion to generate the JSON
def jsonSimpleGenerate(key, value):
    try:
        data = {}
        data[key] = value
        jsonData = json.dumps(data)
        return jsonData
    except Exception as e:
        return -1

def jsonSimpleParser(jsonStr, key):
    try:
        # print("String JSON: " + jsonStr)
        # print("key: " + key)
        if str.find(jsonStr, key) < 0:
            return None
        else:  
            try:
                return json.loads(jsonStr)[key] #.decode('utf-8')
            except Exception as e:
                return json.loads(jsonStr.decode('utf-8'))[key]
    except Exception as e:
        return -1

def jsonDoubleGenerate(json_1, json_2):
    try:
        dictA = json.loads(json_1)
        # print("dictA: " + str(dictA))
        dictB = json.loads(json_2)
        # print("dictA: " + str(dictB))
        merged = dictA.copy()
        # print("merged: " + str(merged))
        merged.update(dictB)
        # print("merged: " + str(merged))
        jsonData = json.dumps(merged)
        # print("JSONDATA: " + str(jsonData))
        return jsonData
    except Exception as e:
        return -1
