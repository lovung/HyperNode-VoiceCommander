import json

# the simple funtion to generate the JSON
def jsonSimpleGenerate(key, value):
    data = {}
    data[key] = value
    jsonData = json.dumps(data)
    return jsonData
