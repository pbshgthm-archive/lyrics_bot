import tweepy
from bot_conf import *
from lyric_engine import Engine

handle="bot_c137"

class StreamListener(tweepy.StreamListener):

	def on_status(self, status):
		global handle
		try:
			if status.user.screen_name==handle:
				return
			
			#if status.entities['user_mentions'][0]['screen_name']==handle:
			if True:	
				
				api.create_favorite(status.id)

				tweet={}
				tweet['screen_name']=status.user.screen_name
				tweet['tweet_id']=status.id
				tweet['input_line']=status.text.replace("@"+handle,"").replace("\n","")
				
				response=Engine(tweet)
				print(response.process())
				reply=response.reply()
				quote=response.quote()

				api.update_status(status=reply, 
				in_reply_to_status_id = status.id,
				auto_populate_reply_metadata=True)

				if not quote="TLTQ":
					api.update_status(status=quote)
				
				api.create_friendship(tweet['screen_name'])

		except Exception as e:
			print(e)


	def on_error(self, status_code):
		if status_code == 420:
			return False



auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#stream_listener = StreamListener()
#stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
#stream.filter(track=[handle])

