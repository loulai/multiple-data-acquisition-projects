from tfidf import *
import sys
from collections import Counter
import pprint

# load path and file name
fullPathToFile = sys.argv[1]
basename = os.path.basename(fullPathToFile)

# return dictionary {basename:xmltext,...}
xmltext = load_corpus(fullPathToFile)[basename]

# tokenize target xml text
arr = tokenizer(xmltext)

# generate counter tuples
output = Counter(arr)

# print 10 most common
for elem, value in output.most_common(10):
    print(elem, value)
