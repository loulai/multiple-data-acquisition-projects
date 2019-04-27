import sys
import os

# set up jinja
from jinja2 import Environment

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
    XML table
    """

    # set up headers and rest
    headers = []
    rest = []
    rows = data.split('\n')

    for i, row in enumerate(rows):
        if (i < 1):
            headersForActualHeader = row.split(",")  # for actual header, don't replace space
            headersForTags = row.replace(" ", "_").split(",") # replace space for tags
        else:
            rest.append(row.split(","))

    # translate to XML
    XML = """<?xml version="1.0"?>
<file>
  <headers>{% for colName in headerRowForActualHeader %}{{colName}}{% if loop.last == false %},{% endif %}{% endfor %}</headers>
  <data>{% for row in rows%}
    <record>
      {% for header in headerRowForTags%}<{{header}}>{{row[loop.index0]}}</{{header}}>{% endfor %}
    </record>{% endfor %}
  </data>
</file>
"""
    print(Environment().from_string(XML).render(headerRowForActualHeader=headersForActualHeader, headerRowForTags = headersForTags, rows=rest))

readcsv(getdata())
