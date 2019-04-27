from tfidf import *

zipfilename = sys.argv[1]
summarizefile = sys.argv[2]

myCorpusDict = load_corpus(zipfilename)

#print("============== loaded corpus ")

fittedTFIDF = compute_tfidf(myCorpusDict)

finalOutput = summarize(fittedTFIDF, myCorpusDict[summarizefile], 20)

for elem in finalOutput:
    print("{} {:.3f}".format(elem[0], elem[1]))

#print("============== tfidf computed ")
