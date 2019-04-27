import sys
import re
import string
import os
import numpy as np
import codecs
from timeit import default_timer as timer
from collections import namedtuple
import operator

# From scikit learn that got words from:
# http://ir.dcs.gla.ac.uk/resources/linguistic_utils/stop_words
ENGLISH_STOP_WORDS = frozenset([
    "a", "about", "above", "across", "after", "afterwards", "again", "against",
    "all", "almost", "alone", "along", "already", "also", "although", "always",
    "am", "among", "amongst", "amoungst", "amount", "an", "and", "another",
    "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
    "around", "as", "at", "back", "be", "became", "because", "become",
    "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
    "below", "beside", "besides", "between", "beyond", "bill", "both",
    "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con",
    "could", "couldnt", "cry", "de", "describe", "detail", "do", "done",
    "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
    "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
    "everything", "everywhere", "except", "few", "fifteen", "fifty", "fill",
    "find", "fire", "first", "five", "for", "former", "formerly", "forty",
    "found", "four", "from", "front", "full", "further", "get", "give", "go",
    "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
    "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his",
    "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
    "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
    "latterly", "least", "less", "ltd", "made", "many", "may", "me",
    "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
    "move", "much", "must", "my", "myself", "name", "namely", "neither",
    "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
    "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on",
    "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
    "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
    "please", "put", "rather", "re", "same", "see", "seem", "seemed",
    "seeming", "seems", "serious", "several", "she", "should", "show", "side",
    "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhere", "still", "such",
    "system", "take", "ten", "than", "that", "the", "their", "them",
    "themselves", "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they", "thick", "thin",
    "third", "this", "those", "though", "three", "through", "throughout",
    "thru", "thus", "to", "together", "too", "top", "toward", "towards",
    "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
    "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby",
    "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
    "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
    "within", "without", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves"])


# load_glove("./data/glove.6B.300d.txt")
def load_glove(filename):
    """
    Read all lines from the indicated file and return a dictionary
    mapping word:vector where vectors are of numpy `array` type.
    GloVe file lines are of the form:

    the 0.418 0.24968 -0.41242 0.1217 ...

    So split each line on spaces into a list; the first element is the word
    and the remaining elements represent factor components. The length of the vector
    should not matter; read vectors of any length.
    """
    glovesDictionary = {}
    with open(filename) as f:
        allLines = f.readlines()  # read everything. Each line is one element of the allLines array.

        #allLines = allLines[0:5000] # subsetting for debugging #print(len(allLines))

        for line in allLines:  # iterate through allLines, one line at a time
            elements = line.split(" ")  # split up one line into elements
            key = elements[0]  # take the first element, which is the word
            value = np.array(elements[1:(len(elements) - 1)], dtype=float)  # put the rest into numpy array
            glovesDictionary[key] = value  # assign dictionary key value pairs
    return glovesDictionary


def filelist(root):
    """Return a fully-qualified list of filenames under root directory"""
    #i = 0
    allfiles = []
    test = []
    for path, subdirs, files in os.walk(root):
        #if i < 2:
        for name in files:
            #print("Path    : {}".format(path))
            #print("Subdirs : {}".format(subdirs))
            #print("Files   : {}".format(files))
            allfiles.append(os.path.join(path, name))
            #i = i + 1
    return allfiles


def get_text(filename):
    """
    Load and return the text of a text file, assuming latin-1 encoding as that
    is what the BBC corpus uses.  Use codecs.open() function not open().
    """
    f = codecs.open(filename, encoding='latin-1', mode='r')
    s = f.read()
    f.close()
    return s


def words(text):
    """
    Given a string, return a list of words normalized as follows.
    Split the string to make words first by using regex compile() function
    and string.punctuation + '0-9\\r\\t\\n]' to replace all those
    char with a space character.
    Split on space to get word list.
    Ignore words < 3 char long.
    Lowercase all words
    Remove English stop words
    """
    regex = re.compile('[' + re.escape(string.punctuation) + '0-9\\r\\t\\n]')
    nopunct = regex.sub(" ", text)  # delete stuff but leave at least a space to avoid clumping together
    words = nopunct.split(" ")
    words = [w.lower() for w in words if len(w) > 2 and w.lower() not in ENGLISH_STOP_WORDS]  # ignore a, an, to, at, be, and stopwords
    return words



def doc2vec(text, gloves):
    """
    Return the word vector centroid for the text. Sum the word vectors
    for each word and then divide by the number of words. Ignore words
    not in gloves.
    """
    allWords = words(text)

    coordinates = []
    # loop through all words in text
    for w in allWords:
        # if a word is in glove
        if w in gloves:
            coordinates.append(gloves[w])
    #print("#words: {}, #vectors: {}".format(len(text), len(coordinates)))
    averageCoordinate = np.average(coordinates, axis=0)
    return averageCoordinate

def load_articles(articles_dirname, gloves):
    """
    Load all .txt files under articles_dirname and return a table (list of tuples)
    where each record is a list of:

      (filename, title, article-text-minus-title, wordvec-centroid-for-article-text)

    We use gloves parameter to compute the word vectors and centroid.

    The filename is stripped of the prefix of the articles_dirname pulled in as
    script parameter sys.argv[2]. E.g., filename will be "business/223.txt"
    """
    File = namedtuple('File', 'filename title articleTextMinusTitle wordvecCentroidForArticleText')

    table = []
    #print(filelist(articles_dirname))
    filenameRegex = re.compile(r"(\w+/\d+.txt$)") # changes './data/bbc/politics/085.txt' to '/politics/085.txt'
    i = 0
    for fullFilepath in filelist(articles_dirname):

        # 0. COPYRIGHT
        if len(filenameRegex.findall(fullFilepath)) < 1:
            pass
        else:
            #if i < 2:
            # 1. filename
            filename = filenameRegex.findall(fullFilepath)[0]

            #2-3. title and rest
            f = open(fullFilepath, "r", encoding='utf-8', errors='ignore')
            header = f.readline().strip("\n")
            #print("{}. {}".format(i, header))
            rest = "\n".join(f.readlines()[1:]) # zero element extracts string
            f.close

            # 4. centriod
            centroid = doc2vec(rest, gloves)
            #print(centroid)
            myFileTuple = File(filename, header, rest, centroid)

            # Finally, append to table
            table.append(myFileTuple)
        #i = i + 1

    #print(["{} {}".format(elem.filename, elem.wordvecCentroidForArticleText) for elem in table])
    # might need to remove the first one, coz that has the damn empty copyright
    return table



def distances(article, articles):
    """
    Compute the euclidean distance from article to every other article and return
    a list of (distance, a) tuples for all a in articles. The article is one
    of the elements (tuple) from the articles list.
    """
    allDistances = []
    targetVec = article.wordvecCentroidForArticleText

    for a in articles:
        euclideanDist = np.linalg.norm(targetVec - a.wordvecCentroidForArticleText)
        allDistances.append((euclideanDist, a))

    # (optinal) come back and refactor to list comp
    return allDistances

# custom function for sorting, used for sorting tuples
def getKey(custom):
    return custom[0]

# articles == our tuple of articles
def recommended(article, articles, n):
    """
    Return a list of the n articles (records with filename, title, etc...)
    closest to article's word vector centroid. The article is one of the elements
    (tuple) from the articles list.
    """
    # get distances and sort
    allDistances = distances(article, articles)
    sortedDistances = sorted(allDistances, key=getKey)
    #allDistances.sort(key=operator.itemgetter(0), reverse=True)

    # >> (0.57, (tup, of, article, elems))
    return [a[1] for a in sortedDistances[1:(n+1)]]

#print("-------- >>>> ")
#start = timer()
#print(recommended(articles[1], articles, 3))
#end = timer()
#print("Time for recommended : {}s".format(round(end-start, 4)))