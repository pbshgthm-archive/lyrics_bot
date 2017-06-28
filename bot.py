import tweepy
from config import bot_auth, engine_conf
from lyric_engine import Engine

class StreamListener(tweepy.StreamListener):

	def set_conf(self,conf):
		self.conf=conf
		self.handle=conf['handle']
	def on_status(self, status):
		try:
			if status.user.screen_name==self.handle:
				return

			'''
			if not status.lang=="en":
				return
			if len(status.text) > 50:
				return
			#'''

			bot.create_favorite(status.id)
			bot.create_friendship(status.user.screen_name)

			tweet={}
			tweet['screen_name']=status.user.screen_name
			tweet['tweet_id']=status.id
			line=status.text.replace("@"+self.handle,"").replace("\n","")
			line=line.replace("#"+self.handle,"")
			
			'''
			words=status.text.split(" ")
			line=[]
			for i in words:
				if not (i[0]=="#" or i[0]=="@"):
					if not "http" in i:
						if not ".com" in i:
							line.append(i)
						else:
							return
					else:
						return
				else:
					return

			line=" ".join(line).replace("\n"," ")
			#'''



			tweet['input_line']=line
			print(tweet['input_line'])

			response=Engine(tweet,self.conf)
			response.process()
			if response.state=="song_not_found":
				bot.update_status(status=response.not_found,
					in_reply_to_status_id = status.id,
					auto_populate_reply_metadata=True)

			if not response.allokay():
					return

			reply=response.reply()
			quote=response.quote()
			print(reply)
			bot.update_status(status=reply, 
			in_reply_to_status_id = status.id,
			auto_populate_reply_metadata=True)

			if not quote=="TLTQ":
				bot.update_status(status=quote)
				
		except Exception as e:
			print(e)


	def on_error(self, status_code):
		if status_code == 420:
			return False







class Bot(tweepy.API):


	def set_conf(self,config):
		self.engine_conf=config
		self.handle=config['handle']

	def listen_lyric(self):
		stream_listener = StreamListener()
		stream_listener.set_conf(self.engine_conf)
		stream = tweepy.Stream(auth=auth, listener=stream_listener)
		#stream.filter(track=["love"])
		stream.filter(track=[self.handle])	


	def clean_up_timeline(self):
		for tweet in tweepy.Cursor(self.user_timeline).items():
			if tweet.is_quote_status:
				try:
					quoted_id=tweet.entities['urls'][0]['expanded_url']
					quoted_id=int(quoted_id.split("/")[-1])
					src=self.get_status(quoted_id)
				except:
					self.destroy_status(tweet.id)

	def follow_followers(self):
		self.followers_list=self.followers_ids()
		for follower in self.followers_list:
			self.create_friendship(follower)

	def unfollow_nonfollowers(self):
		self.followers_list=self.followers_ids()
		self.following_list=self.friends_ids()
		for user in self.following_list:
			if user not in self.followers_list:
				self.destroy_friendship(user)





auth = tweepy.OAuthHandler(bot_auth['consumer_key'], bot_auth['consumer_secret'])
auth.set_access_token(bot_auth['access_token'], bot_auth['access_token_secret'])

bot=Bot(auth)
bot.set_conf(engine_conf)
bot.listen_lyric()
#bot.clean_up_timeline()
#bot.follow_followers()
#bot.unfollow_nonfollowers()



	