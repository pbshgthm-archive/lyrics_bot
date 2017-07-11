from googleapiclient.discovery import build
import urllib.request
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
import re



class Engine():

	conf=None
	meta=None

	input_line=None
	url=None
	full_lyric=None
	q_lyric=None
	r_lyric=None
	
	track=None
	artist=None

	state=None
	not_found="Sorry! couldn't find the song"

	def __init__(self,tweet,conf):
	
		self.input_line=tweet['input_line']
		self.conf=conf
		self.meta=tweet
		self.state="initialized"
		

	def find_song(self):

		service = build("customsearch", "v1", 
					developerKey=self.conf['api_key'])
		try:
			results = service.cse().list(q=self.input_line, 
					cx=self.conf['cse_id'], num=2).execute()
			self.url = "http://"+results['items'][0]['formattedUrl']
			self.state="song_found"
		except Exception as e:
			if str(e)=="'items'":	
				self.state="song_not_found"
			else:
				self.sate="search_engine_failed"

	def get_lyric(self):

		try:
			page=urllib.request.urlopen(self.url).read()
			soup=BeautifulSoup(page,"xml")
			soup=str(soup)
			lyric = re.findall ( self.conf['l_fp']+'(.*?)'+
						self.conf['l_rp'],soup, re.DOTALL)[0]
			l_clean=re.compile('<.*?>|\[.*?\]') 
			lyric=re.sub(l_clean,'',lyric)
			self.full_lyric=[x for x in lyric.split('\n') if x!=""]
		
			title = re.findall ( self.conf['t_fp']+'(.*?)'
						+self.conf['t_rp'],soup, re.DOTALL)[0]
			t_clean=re.compile('\[.*?\]')
			title=re.sub(t_clean,'',title).replace(" ","")
			self.track=re.sub(r'[^a-zA-Z0-9]','', title)

			artist = re.findall ( self.conf['a_fp']+'(.*?)'+
					self.conf['a_rp'],soup, re.DOTALL)[0]
			a_clean=re.compile('\[.*?\]')
			artist=re.sub(a_clean,'',artist).replace(" ","")
			self.artist=re.sub(r'[^a-zA-Z0-9]','', artist)
			self.state="lyrics_fetched"

		except Exception as e:
			print(e)
			self.state="lyric_fetch_failed"


	def len_lyr(self,ind,num):
		length=len(self.full_lyric[ind])+len(self.full_lyric[ind+1])
		length+=len(self.full_lyric[ind+2])+3
		if num<=2:
			length-=len(self.full_lyric[ind])+1
		if num==1:
			length-=len(self.full_lyric[ind+3])+1
		return length

	def concat_lyr(self,ind,num):
		lyric=self.full_lyric[ind+1]+"\n"
		if num>=2:
			lyric=lyric+self.full_lyric[ind+2]+"\n"
		if num==3:
			lyric=self.full_lyric[ind]+"\n"+lyric

		return lyric


	def get_line(self):
		
		sim_score=[]
		for i in self.full_lyric:
			sim_score.append(SequenceMatcher(None,i,self.input_line).ratio())
			ind=sim_score.index(max(sim_score))
		print(max(sim_score))
		if ind==len(self.full_lyric)-1:
			ind=ind-2
		
		if ind==len(self.full_lyric)-2:
			ind=ind-1
	
		extra_len=len(self.artist)+len(self.track)+3
		
		if extra_len+self.len_lyr(ind=ind,num=3)<=140:
			self.r_lyric=self.concat_lyr(ind=ind,num=3)
			self.response="rep_3"
		
		elif extra_len+self.len_lyr(ind=ind,num=2)<=140:
			self.r_lyric=self.concat_lyr(ind=ind,num=2)
			self.response="rep_2"
		
		elif extra_len+self.len_lyr(ind=ind,num=1)<=140:
			self.r_lyric=self.concat_lyr(ind=ind,num=1)
			self.response="rep_1"
		else:
			self.response="rep_too_long"

		self.state="rep_ok|qte_no"


		quote_len=30+len(self.meta['screen_name'])
		quote_len+=len(str(self.meta['tweet_id']))
		extra_len+=quote_len
		
		if extra_len+self.len_lyr(ind=ind,num=3)<=140:
			self.q_lyric=self.concat_lyr(ind=ind,num=3)
			self.response+="|qte_3"
		
		elif extra_len+self.len_lyr(ind=ind,num=2)<=140:
			self.q_lyric=self.concat_lyr(ind=ind,num=2)
			self.response+="|qte_2"
		
		elif extra_len+self.len_lyr(ind=ind,num=1)<=140:
			self.q_lyric=self.concat_lyr(ind=ind,num=1)
			self.response+="|qte_1"
		else:
			self.response+="|qte_too_long|ready"

		self.state="rep_ok|qte_ok"

	def process(self):

		if not self.state=="initialized":
			return "uninitialised"
		
		self.find_song()
		self.log()
		if not self.state=="song_found":
			return self.state
				
		self.get_lyric()
		self.log()
		if not self.state=="lyrics_fetched":
			return self.state
		try:
			self.get_line()
			self.log()
		except:
			pass
			print(self.state)

		if not self.state.split("|")[1][:3]=="qte":
			return "lyric_creation_failed"
		self.log()
		return "response_created"


	def reply(self):
		
		if not self.response.split("|")[0]=="rep_too_long":
			decors="#"+self.artist+" #"+self.track
			return self.r_lyric+decors

		return decors

	def quote(self):

		if not self.response.split("|")[1]=="qte_too_long":
			decors="#"+self.artist+" #"+self.track
			q="\nhttps://twitter.com/"+self.meta['screen_name']
			q+="/status/"+str(self.meta['tweet_id'])
			self.state="completed"
			return self.q_lyric+decors+q

		
		return "TLTQ"

	def log(self):
		
		print(self.state)

	def allokay(self):
		try:
			if not self.state.split("|")[1][:3]=="qte":
				return False
			
			return True 
		except:
			return False