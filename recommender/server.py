# Launch with
#
#gunicorn -D --threads 4 -b 0.0.0.0:5000 --access-logfile server.log --timeout 60 server:app glove.6B.300d.txt bbc

from flask import Flask, render_template
from doc2vec import *
import sys
from timeit import default_timer as timer
app = Flask(__name__)

@app.route("/")
def articles():
    """Show a list of article titles"""
    return render_template('articles.html', documents=articles)


@app.route("/article/<topic>/<filename>")
def article(topic,filename):
    """
    Show an article with relative path filename. Assumes the BBC structure of
    topic/filename.txt so our URLs follow that.
    """
    article = [tup for tup in articles if tup.filename == (topic + "/" + filename)][0]
    #print(article.filename)

    return render_template('article.html', mainArticle=article, recommendedArticles=recommended(article, articles, 5))

# initialization
i = sys.argv.index('server:app')
glove_filename = sys.argv[1+i]
articles_dirname = sys.argv[2+i]

print("-------- running load_glove()")
start = timer()
gloves = load_glove(glove_filename)
end = timer()
print("----------- time load_glove() : {}s".format(round(end-start, 3)))

print("\n--- running load_articles()")
startLoad = timer()
articles = load_articles(articles_dirname, gloves)
endLoad = timer()
print("-------- time load_articles() : {:06.3f}s".format(round(endLoad-startLoad, 3)))

#app.run('0.0.0.0', port=3002)
