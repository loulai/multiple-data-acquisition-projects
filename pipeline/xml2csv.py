import sys
import untangle

def getdata():
    if len(sys.argv)==1: # if no file given, read from stdin
        data = sys.stdin.read()
    else:
        f = open(sys.argv[1], "r")
        data = f.read()
        f.close()
    return data.strip()

def readxml(data):
    """
       Read XML
       """


    xml = untangle.parse(data)

    # header
    headerRow = xml.file.headers.cdata.replace("_", " ")
    print(headerRow)

    # rest
    for i in range(len(xml.file.data)):
        rowObject = xml.file.data.record[i]
        row = []
        for k in range(len(rowObject)):
            row.append(rowObject.children[k].cdata)
        print(','.join(row))



readxml(getdata())