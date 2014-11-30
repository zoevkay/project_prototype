"""
	API for getting tweets from Twitter hashtag feeds.
"""
import itertools
import os
from datetime import datetime
import pickle

import tweepy
from sqlalchemy.exc import SQLAlchemyError

import politwit.model as model

# tweepy api instance
api = None

POLITICAL_HASHTAGS = ["p2", "tcot", 'ferguson', 'pjnet', 'uniteblue', 'topprog', 'ccot', 'teaparty', 'ows', 'occupy', 'tgdn', 'rednationrising', '2a', 'tlot', 'libcrib', 'makedclisten', 'fightfor15', 'gpus', 'nwo', 'mmot', 'mmj', 'obama', 'gop', 'p2b', 'news', '1a', 'immigration', 'cashinin', 'nra', 'gunsense', 'ctl', 'nyc', 'inners', 'immigrationreform', 'tfb', 'maddow', 'cnn', 'conservatives', 'lnyhbt', 'legislatorinchief', 'darrenwilson', 'sot', 'mtvstars', 'gruber', '1u', 'amnesty', 'mikebrown', 'pdmfnb', 'notonemore', 'stopislam', 'impeachobama', 'tntweeters', 'fauxnews', 'foxnews', 'liberty', 'michaelbrown', 'stoprush', 'oo', 'climate', 'whiteprivilege', 'prolife', 'twill', 'youmightbealiberal', 'socialism', 'nsa', 'patriots', 'wiunion', 'un', 'aym', 'dontpayrush', 'uniteright', 'stayhigh', 'nato', 'thebearmanradioshow', 'greens', 'fail', 'isisisajoke', 'nonukes', 'fsaisajoke', 'obamaamnesty', 'egypt', 'redonred', 'usa', 'ndaa', 'sentedcruz', 'dems', 'syria', 'raisethewage', 'hardball', 'gitmo', 'unitelbue', 'freedom', 'tpot', 'waar', 'benghazi', 'molonlabe', 'edshow', 'reformislam', 'media', 'nytimes', 'agw', 'stribpol', 'rkba', 'sgp', 'elizabethlauten', 'immigrationaction', 'twisters', 'dnc', 'lol', 'politics', 'rw', 'renewus', 'tamirrice', 'rnc', 'ac360', 'vote2016', 'jokes', 'copolitics', 'video', 'election', 'fergusondecision', 'humor', 'chicago', 'defendtheduggars', 'pets', 'dem', 'unitedblue', 'cats', 'military', 'bigboss8', 'thisisislam', 'orpuw', 'guncontrol', 'connecttheleft', 'comedy', 'hamas', 'isis', 'food', 'woods', 'ffrnn', 'justice', 'smith', 'hipster', 'resist44', 'harbinger', 'citizensunited', 'doherty', 'elitism', 'viral', 'irs', 'muslim', 'immigrati', 'lookatthem', 'makeitright', 'getmoneyout', 'lgbt', 'british', 'gov', 'stevens', 'hedgeofprotection', 'ripoffs', 'chucktodd', 'whitegenocide', 'texas', 'opencarry', 'lot', 'solar', 'authors', 'wiright', 'us', 'tp4a', 'reagan', 'sadlittleman', 'blacklivesmatter', 'ttcot', 'boycott', 'mapoli', 'netneutrality', 'debt', 'india2014', 'democracy', 'consnc', 'alsharpton', 'pew', 'extortion17', 'iartg', 'clueless', 'emaciated', 'wethepeople', 'election2016', 'tpfa', 'fergusonprotests', 'climatecoverage', 'woodyallen', 'facebook', 'unitered', 'rnr', 'anystreet', 'patriotvoices', 'twitterstorm', 'thankful', 'settledscience', 'obamacare', 'voteblue', 'waarmedia', 'jihad', 'truth', 'stopobama', 'cpac', 'democrats', 'fisa', 'intimogate', 'mm', 'energy', 'securetheborder', 'opslam', 'tarot', 'njp', 'teamjesus', 'pantsupdontloot', 'hugsnotdrugs', 'whitehouse', 'boehner', 'thisisthenra', 'keystone', 'crude', 'sgpt', 'umn', 'amagi', 'hannity', 'jobs', 'ronpaul', 'cars', 'c2gthr', 'britishlaw', 'leadership', 'waronwomen', 'fns', 'finland', 'everytown', 'sjw', 'vettheprez', 'pran945', 'anarchist', 'globalwarming', 'jesustweeters', 'acca', 'pragobots', 'jesus', 'rino', 'epa', 'scandal', 'immigra', 'galtsgirl', 'union', 'liberals', 'music', 'momsdemand', 'glennbeck', 'repubs', 'iftheygunnedmedown', 'unitblue', 'looters', 'aca', 'actonclimate', 'jdl', 'noamnesty', 'ben', 'sierraclub', 'humanrightsabuse', 'macysparade', 'ibdcartoons', 'propaganda', 'ub', 'studentloan', 'aesthetics', 'israel', 'du1', 'fox', 'billcosby', 'stopthelies', 'mn', 'ew', 'rape', 'scotus', 'wearethepeople', 'documents', 'sharia', 'nyt', 'guns', 'youknowwhat', 'aclu', 'liberal', 'eff', 'economy', 'rnrdecal', 'oil', 'handsupdontshoot', 'yesallwomen', 'nannystate', 'evil', 'liberalhypocrisy', 'islamic', 'teapartytoldyouso', 'ethics', 'mba', 'christians', 'barackobama', 'ccw', 'occupywallstreet', 'thetwisters', 'laraza', 'atheism', 'newslinks', 'green', 'tpp', 'blacknews', 'michaelbriwn', 'peopleschamp', 'dod']
NONPOLITICAL_HASHTAGS = ["ff", "tbt"] #"nowplaying", "gameinsight","love", "win", "ipad"
EXCLUDE_HASHTAGS =  "-#RT -#rt -#TeamFollowBack -#followback"
TWEETS_TO_GET = 3000

def connect_to_API():
	"""
	Create instance of tweepy API class with OAuth keys and tokens.
	"""
	global api
	# initialize tweepy api object with auth, OAuth
	TWITTER_API_KEY=os.environ.get('TWITTER_API_KEY')
	TWITTER_SECRET_KEY=os.environ.get('TWITTER_SECRET_KEY')
	TWITTER_ACCESS_TOKEN=os.environ.get('TWITTER_ACCESS_TOKEN')
	TWITTER_SECRET_TOKEN=os.environ.get('TWITTER_SECRET_TOKEN')

	auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_SECRET_KEY, secure=True)
	auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_SECRET_TOKEN)
	api = tweepy.API(auth, cache=None) #removed wait_on_rate_limit=True, wait_on_rate_limit_notify=True

	return api


def get_tweets_by_query(api, query, max_tweets):
	"""
	search for {max_tweets} tweets labeled by a particular hashtag {query}

	Parameters:
	----------
	Api: the Tweepy API instance.
	Query: hashtag to search for, as a string, prefixed by "#"
	Max_tweets: the total number of tweets requested.

	Output:
	------
	List of JSON statuses

	Note:
	----
	Per 15 minutes, app can make 450 requests.
	Number of tweets per page defaults to 15. "Count" maximum is 100.

	"""
	searched_tweets = []

	max_id = -1

	while len(searched_tweets) < max_tweets:
	    count = max_tweets - len(searched_tweets)
	    try:
	        new_tweets = api.search(q=query, lang="en", count=count, include_entities=True, max_id=str(max_id - 1))
	        if not new_tweets:
	            break

	        for tweet in new_tweets:
	        	tweet = tweet._json
	        	searched_tweets.append(tweet)

	        max_id = new_tweets[-1].id
	        since_id = new_tweets[0].id

	        print "max_id:", max_id
	        print "since_id", since_id

	    except tweepy.TweepError as e:
	        # depending on TweepError.code --> retry or wait
        	# for now give up on an error
        	break
	return searched_tweets



def load_tweets(session, statuses, label):
	"""
	Loads search results into database, eliminating duplicates.

	Parameters:
	-----------
	SQLA session instance
	List of statuses from query
	Label associated with hashtag stream (manually assigned)

	Output:
	-------
	Tweets and hashtags committed to database, one transaction per tweet.
	This eliminates duplicates by rolling back commits of dupes and continuing.

	"""

	for status in statuses:

		tweet = model.Status()
		tweet.tw_tweet_id = status["id"]
		# print "TWEET_ID", tweet.id
		tweet.tw_user_id = status["user"]["id"]
		# print "USER", tweet.user_id
		tweet.text = status["text"]
		# print "TEXT", tweet.text
		tweet.label = label
		created_at = status["created_at"][:10] + status["created_at"][25:]
		created_at = datetime.strptime(created_at, "%a %b %d %Y")
		tweet.created_at = created_at

		print "TWEET TO ADD", tweet

		try:
			session.add(tweet)
			session.commit()
		except SQLAlchemyError:
			pass
		finally:
			session.close()


def get_political_hashtags(api, session):

	for hashtag in POLITICAL_HASHTAGS:
		htg_tweets = get_tweets_by_query(api, hashtag, TWEETS_TO_GET/4)
		load_tweets(session, htg_tweets, "p")

def get_nonpolitical_hashtags(api, session):

	for hashtag in NONPOLITICAL_HASHTAGS:
		htg_tweets = get_tweets_by_query(api, ("#" + hashtag + " -#p2 -#tcot " + EXCLUDE_HASHTAGS), TWEETS_TO_GET)
		load_tweets(session, htg_tweets, "np")


def main(session):
	print "running main"
	api = connect_to_API()
	get_political_hashtags(api, session)
	# get_nonpolitical_hashtags(api, session)

if __name__ == "__main__":
	s = model.connect()
	main(s)




