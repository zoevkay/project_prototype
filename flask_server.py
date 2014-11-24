import os
import logging
import time#, threading

from flask import Flask, request, render_template, redirect
import tweepy

from friends import User

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


TIME_TO_WAIT = 900/180 # 15 minutes divided into 180 requests
NUM_RETRIES = 2
RATE_LIMITED_RESOURCES =[("statuses", "/statuses/user_timeline")]

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/test.json")
def test_json():
	# Or - just do an object2json function of some sort and there's a shortcut to return that
	return render_template("test.json", obj_list = [{'handle': '@whoever', 'score': 10}, {'handle': '@blah', 'score': 20}])

@app.route("/display", methods=["GET", "POST"])
def display_friends():
	if request.method == "POST":
		screen_name = request.form.get("screenname")
		print screen_name
		api = connect_to_API()

		user = User(api, central_user=screen_name, user_id=screen_name)
		print user.SCORE

		try:
			friends_ids = user.get_friends_ids(screen_name)
			print friends_ids

			friendlist = []

			for page in user.paginate_friends(friends_ids, 100):
				friends = process_friend_batch(user, page, api)
				print check_rate_limit(api)
				friendlist.extend(friends)

			if len(friendlist) > user.MAX_NUM_FRIENDS:
				friendlist = get_top_influencers(user.MAX_NUM_FRIENDS)

			return render_template("index.html", display = friendlist)


		except tweepy.TweepError as e:
			print "ERROR!!!!!", e
			# if e.message[0]["code"] == 88:
			# # {"errors":[{"message":"Rate limit exceeded","code":88}]}
			# 	print "EXCEEDED RATE LIMIT", e

			return render_template("index.html", display = e)

def process_friend_batch(user, page, api):
	"""
	Create User object for each friend in batch of 100 (based on pagination)
	"""
	batch = []
	friend_objs = user.lookup_friends(f_ids=page)
	for f in friend_objs:
		friend = User(api, central_user=user.CENTRAL_USER, user_id=f.id)
		friend.NUM_FOLLOWERS = f.followers_count
		print friend.NUM_FOLLOWERS
		# print "friend created"
		batch.append(friend)
	return batch

def get_top_influencers(count):
	"""
	Get top influencers from user friends, as measured by # of followers.

	After requesting paginated friends, check "followers_count" attribute of
	each friend.

	Note:
	-----
	Run this function only if user has more than {count} friends.
	Currently, Twitter limits user timeline requests to 300
	(application auth) or 180 requests (user auth).

	Parameters:
	----------
	Number of top influencers to output.

	Output:
	-------
	List of {count} most influential friends

	"""

	sorted_by_influence = sorted(friendlist, key=lambda x: x.NUM_FOLLOWERS)
	friendlist = sorted_by_influence[:count]

	return friendlist

def check_rate_limit(api):
	"""
	Check Twitter API rate limit status for "statuses" (timeline) requests
	Print number of requests remaining per time period
	"""
	limits = api.rate_limit_status()
	stats = limits["resources"]["statuses"]
	for resource in stats.keys():
		if stats[resource]["remaining"] == 0:
			print "EXPIRED:", resource
		else:
			print resource, ":", stats[resource]["remaining"], "\n"

	# users = limits["resources"]["users"]
	# for resource in users.keys():
	# 	if stats[resource]["remaining"] == 0:
	# 		print "EXPIRED:", resource
	# 	else:
	# 		print resource, ":", stats[resource]["remaining"], "\n"

	# threading.Timer(self.TIME_TO_WAIT, self.check_rate_limit).start()

def connect_to_API():
	"""
	Create instance of tweepy API class with OAuth keys and tokens.
	"""
	# initialize tweepy api object with auth, OAuth
	TWITTER_API_KEY=os.environ.get('TWITTER_API_KEY')
	TWITTER_SECRET_KEY=os.environ.get('TWITTER_SECRET_KEY')
	TWITTER_ACCESS_TOKEN=os.environ.get('TWITTER_ACCESS_TOKEN')
	TWITTER_SECRET_TOKEN=os.environ.get('TWITTER_SECRET_TOKEN')

	auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_SECRET_KEY, secure=True)
	auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_SECRET_TOKEN)
	api = tweepy.API(auth, cache=None) #removed wait_on_rate_limit=True, wait_on_rate_limit_notify=True

	return api

if __name__ == "__main__":
	app.run(debug=True)
