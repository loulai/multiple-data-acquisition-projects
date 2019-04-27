import sys
import json

def getdata():
    if len(sys.argv)==1: # if no file given, read from stdin
        data = sys.stdin.read()
    else:
        f = open(sys.argv[1], "r")
        data = f.read()
        f.close()
    return data.strip()

def readjson(data):
    """
       Read JSON
       """
    root = json.loads(data)

    # header
    print(",".join(root['headers']).replace("_", " "))

    # rest
    for k in range(len(root['data'])):
        jsonRowObject = root['data'][k]
        rowElements = []
        for key in jsonRowObject:
            rowElements.append(jsonRowObject[key])
        print(",".join(rowElements))

readjson(getdata())