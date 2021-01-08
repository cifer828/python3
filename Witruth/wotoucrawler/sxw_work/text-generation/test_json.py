import json
dictObj = {
    'andy': {
        'age': 23,
        'city': 'shanghai',
        'skill': 'python'
    },
    'william': {
        'age': 33,
        'city': 'hangzhou',
        'skill': 'js'
    }
}

jsObj = json.dumps(dictObj)

fileObject = open('jsonFile.txt', 'w')
fileObject.write(jsObj)
fileObject.close()