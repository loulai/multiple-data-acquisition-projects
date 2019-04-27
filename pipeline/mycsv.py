import sys

def getdata():
    if len(sys.argv)==1: # if no file given, read from stdin
        data = sys.stdin.read()
    else:
        f = open(sys.argv[1], "r")
        data = f.read()
        f.close()
    return data.strip()

def readcsv(data):
    """
    Read CSV with header from data string and return a header list
    containing a list of names and also return the list of lists
    containing the data.
    """
    headers = []
    rest = []
    rows = data.split('\n')

    for i, row in enumerate(rows):
        if(i < 1):
            headers = row.split(",")
        else:
            rest.append(row.split(","))

    #print(headers)
    #print(rest)
    return headers, rest
