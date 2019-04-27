import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import defaultdict
import pprint
from timeit import default_timer as timer
import operator
import statistics


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    consumer_key, consumer_secret, access_token, access_token_secret \
    = loadkeys(twitter_auth_filename)

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    # setup
    myDict = defaultdict()
    analyzer = SentimentIntensityAnalyzer()

    # get user information
    user = api.get_user(name)
    print("--- from fetch_tweets")
    print(user)
    print("--- ")
    myDict['user'] = name
    print(name)
    myDict['count'] = user.statuses_count

    # get tweets information
   # user_tweets = tweepy.Cursor(api.user_timeline(name)).items(100)
    #user_tweets = [tweet for tweet in tweepy.Cursor(api.user_timeline(screen_name=name)).items(100)]

    t20 = api.user_timeline(screen_name=name) # 1-20
    idLast = t20[-1].id
    t40 = api.user_timeline(screen_name=name, max_id=idLast)[1:] # 20-39
    idLast = t40[-1].id
    t60 = api.user_timeline(screen_name=name, max_id=idLast)[1:] # 39-58
    idLast = t60[-1].id
    t80 = api.user_timeline(screen_name=name, max_id=idLast)[1:] # 58-77
    idLast = t80[-1].id
    t100 = api.user_timeline(screen_name=name, max_id=idLast)[1:]  # 77-96
    idLast = t100[-1].id
    tOverflow =  api.user_timeline(screen_name=name, max_id=idLast)[1:5]  # 96-100

    #user_tweets = api.statuses_lookup(user)

    print("------------------------------------------ t20")
    print(len(t20))
    print([t.text for t in t20])

    print("------------------------------------------ t40")
    print(len(t40))
    print([t.text for t in t40])

    print("------------------------------------------ t60")
    print(len(t60))
    print([t.text for t in t60])

    print("------------------------------------------ t80")
    print(len(t80))
    print([t.text for t in t80])

    print("------------------------------------------ t100")
    print(len(t100))
    print([t.text for t in t100])

    print("------------------------------------------ tOverflow")
    print(len(tOverflow))
    print([t.text for t in tOverflow])

    user_tweets = t20 + t40 + t60 + t80 + t100 + tOverflow
    print("------------------------------------------ len of user tweets")
    print(len(user_tweets))
    tweets = []
    for tweet in user_tweets:
        d = defaultdict()
        d['id'] = tweet.id
        d['created'] = tweet.created_at
        d['retweeted'] = tweet.retweet_count
        d['text'] = tweet.text
        d['hashtags'] = tweet.entities['hashtags']
        d['urls'] = tweet.entities['urls']
        d['mentions'] = tweet.entities['user_mentions']
        d['score'] = analyzer.polarity_scores(tweet.text)['compound']
        tweets.append(d)

    myDict['tweets'] = tweets
    allScores = [t['score'] for t in myDict['tweets']]
    myDict['median'] = statistics.median(allScores)
    print(allScores)
    print(myDict['median'])
    return myDict



def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get a list of "friends IDs" then get
    the list of users for each of those.
    """

    friendsIDs = api.friends_ids(name)

    start = timer()
    friends = [api.get_user(f) for f in friendsIDs]
    end = timer()
    print("----------------- (done getting users) {}s".format(end-start))

    final_list = []

    for f in friends:
        d = defaultdict()
        d['name'] = f.name
        d['screen_name'] = f.screen_name
        d['followers'] = f.followers_count
        d['created'] = f.created_at
        d['image'] = f.profile_image_url
        final_list.append(d)

    #pp = pprint.PrettyPrinter(indent=1)
    #pp.pprint(final_list)
    #print(len(final_list))
    #print(api.get_user(name).followers_count)
    return final_list

def sort_by_followers(list_of_followers):
    return sorted(list_of_followers, key=operator.itemgetter('followers'), reverse=True)


#twitter_auth_filename = sys.argv[1] # e.g., "/Users/parrt/Dropbox/licenses/twitter.csv"
#api = authenticate(twitter_auth_filename)
#fetch_tweets(api, "realdonaldtrump")

#thinglist = fetch_following(api, "realDonaldTrump")

#sortedThing = sort_by_followers(thinglist)

#pp = pprint.PrettyPrinter(indent=1)
#pp.pprint(sortedThing)
