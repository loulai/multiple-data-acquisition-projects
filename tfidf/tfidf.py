import sys

import nltk
from nltk.stem.porter import *
from sklearn.feature_extraction import stop_words
import xml.etree.cElementTree as ET
from collections import Counter
import string
from sklearn.feature_extraction.text import TfidfVectorizer
import zipfile
import os
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
PARTIALS = False


def tokenize(text):
    """
    Tokenize text and return a non-unique list of tokenized words
    found in the text. Normalize to lowercase, strip punctuation,
    remove stop words, drop words of length < 3, strip digits.
    """
    regex = re.compile('[' + re.escape(string.punctuation) + '0-9\\r\\t\\n]')
    nopunct = regex.sub(" ", text)  # delete stuff but leave at least a space to avoid clumping together
    words = word_tokenize(nopunct) # divide string into substrings

    myStopWords = stop_words.ENGLISH_STOP_WORDS # get list of stopwords

    words = [w.lower() for w in words if len(w) > 2 and w.lower() not in myStopWords]  # ignore a, an, to, at, be, and stopwords

    return words


def stemwords(words):
    """
    Given a list of tokens/words, return a new list with each word
    stemmed using a PorterStemmer.
    """
    stemmer = PorterStemmer()
    return [stemmer.stem(w) for w in words]

# combine both tokenize and stemwords
def tokenizer(text):
    return stemwords(tokenize(text))

def compute_tfidf(corpus):
    """
    Create and return a TfidfVectorizer object after training it on
    the list of articles pulled from the corpus dictionary. The
    corpus argument is a dictionary mapping file name to xml text.
    """
    # tfidf specs
    tfidf = TfidfVectorizer(input='content',
                            analyzer='word',
                            preprocessor=gettext,
                            tokenizer=tokenizer,
                            stop_words='english',
                            strip_accents='ascii',
                            decode_error='ignore')
    #print("------------- past tfidf specs")

    # train vocab
    response = tfidf.fit(corpus.values())
    #print("------------- past vocab training")
    return response

def summarize(tfidf, text, n):
    """
    Given a trained TfidfVectorizer object and some XML text, return
    up to n (word,score) pairs in a list. Discard any terms with
    scores < 0.09.
    """
    # get transformed
    transTFIDF = tfidf.transform([text])

    # print names
    feature_names = tfidf.get_feature_names()

    finalTFIDF = [(feature_names[col], transTFIDF[0, col]) for col in transTFIDF.nonzero()[1] if transTFIDF[0, col] >= 0.09]
    #print("------------- past creating final TFIDF")

    sortedFinalTFIDF = sorted(finalTFIDF, key=lambda tup: tup[1], reverse=True)

    return(sortedFinalTFIDF[0:n])

def gettext(xmltext):
    """
    Parse xmltext and return the text from <title> and <text> tags
    """
    xmltext = xmltext.encode('ascii', 'ignore') # ensure there are no weird char
    root = ET.fromstring(xmltext)
    # create a string from all paragraphs inside <title></title>
    # test = [title.text for title in root.findall('title')] # long silly way
    titleText = root.find('title').text

    # create a string from all paragraphs inside <text></text>
    for rootText in root.iterfind("text"):
        textArray = [p.text for p in rootText]
        textArray.insert(0, titleText)

    return(' '.join(textArray))


def load_corpus(zipfilename):
    """
    Given a zip file containing root directory reuters-vol1-disk1-subset
    and a bunch of *.xml files, read them from the zip file into
    a dictionary of (word,xmltext) associations.

    Use namelist() from ZipFile object to get list of xml files in that zip file.
    Convert filename reuters-vol1-disk1-subset/foo.xml to foo.xml
    as the keys in the dictionary. The values in the dictionary are the
    raw XML text from the various files.
    """
    dict = {}

    if not zipfile.is_zipfile(zipfilename): # only happens when testing
        xmlText = open(zipfilename, "r").read()
        baseName = os.path.basename(zipfilename)  # extract basename
        dict[baseName] = gettext(xmlText)  # create new key value pair in dict
        #print("============== from load corps ===============")
        return dict

    else: # it's a zip yay
        reutersZip = zipfile.ZipFile(zipfilename)

        # Loop through all zip files
        for i, name in enumerate(reutersZip.namelist()):
            # skip the first file, which is blank for some reason
            if i > 0:
                pureXML = reutersZip.read(name).decode('ascii') # convert to text

                #textString = gettext(xmlText) # return for 'text' and 'title'

                baseName = os.path.basename(name) # extract basename
                dict[baseName] = pureXML # create new key value pair in dict
        #print(dict)
    return dict



