import tweepy
import os
import time
from random import randint

TWITTER_API_KEY=os.environ.get('TWITTER_API_KEY')
TWITTER_SECRET_KEY=os.environ.get('TWITTER_SECRET_KEY')
TWITTER_ACCESS_TOKEN=os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_SECRET_TOKEN=os.environ.get('TWITTER_SECRET_TOKEN')

auth = None
api = None

def init_api():
	"""
	Create global tweepy API object with OAuth keys and tokens.
	Call this function from flask server
	"""
	global api
	auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_SECRET_KEY, secure=True)
	auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_SECRET_TOKEN)
	api = tweepy.API(auth, cache=None) #removed wait_on_rate_limit=True, wait_on_rate_limit_notify=True
	return auth, api

def get_feed():
	# returns 20 most recent statuses from authenticated user feed
	public_tweets = api.home_timeline()
	for tweet in public_tweets:
		pass

def get_timeline(uid, count):
	"""Get n number of tweets by passing in user id and number of statuses.
		If user has protected tweets, returns [] rather than break the program.
	"""
	try:
		feed = tweepy.Cursor(api.user_timeline, id=uid).items(count)
		return feed

	except tweepy.TweepError as e:
		print e.message[0]["error"]
		return []

def get_user_by_id(uid):
	"""
	get_user can take screen_name or user_id
	id is the generic case (could be either type)
	"""
	user = api.get_user(uid)
	return user

def get_friends(uid):
	"""returns list of integers (friends_ids) of people that user (uid) is following"""
	# print TWITTER_API_KEY, TWITTER_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_SECRET_TOKEN
	# print repr(uid)
	friends_ids = api.friends_ids(uid)
	return friends_ids

def get_links(id):
	link_dictionary = {}
	# a tweet is a status object <class 'tweepy.models.Status'>
	feed = tweepy.Cursor(api.user_timeline, id=id, include_entities=True).items(20)
	for status in feed:
		for url in status.entities.setdefault("urls", []):
			print url['expanded_url']
		# link_dictionary.setdefault(key, tweet["entities"]["urls"])
	return link_dictionary

def assign_score():
	score = randint(0, 100)
	return score

def assign_all_friend_scores(friendlist):
	pass
	scores = {}
	for friend_id in friendlist:
		scores.setdefault(friend_id, assign_score())
	return scores

def timer():
	time.sleep(900)
	print "It's been 900 seconds"


def main():
	init_api()
	# timer()
	# friends = get_friends("bookstein")
	# friend_id = get_user_by_id(friends[0]).id
	# print friend_id
	# tweets = get_timeline(friend_id)
	# print tweets
	# print get_links(friend_id)
	# print assign_all_friend_scores(friends)
	print get_timeline("maddow", 400)


if __name__ == "__main__":
	main()



