import sys
import os

# set up jinja
from jinja2 import Environment, FileSystemLoader

# capture current directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

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
    Read CSV with header from data string and return a
    HTML table
    """

    # set up headers and rest
    headers = []
    rest = []
    rows = data.split('\n')

    for i, row in enumerate(rows):
        if (i < 1):
            headers = row.split(",")
        else:
            rest.append(row.split(","))

    # translate to HTML
    HTML = """
    <html>
    <body>
    <table>
    <tr>{%for colName in headerRow%}<th>{{ colName }}</th>{% endfor %}</tr>
    {%for row in rows%}<tr>{%for element in row%}<td>{{ element }}</td>{% endfor %}</tr>
    {% endfor %}</table>
    </body>
    </html>
    """
    print(Environment().from_string(HTML).render(headerRow=headers, rows=rest))

readcsv(getdata())
