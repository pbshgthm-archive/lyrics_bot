import tweepy
from googleapiclient.discovery import build
import urllib.request
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
import re
from conf import *


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)




def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']


def get_lyric(url):
    
    page=urllib.request.urlopen(url).read()
    soup=BeautifulSoup(page,"xml")
    soup=str(soup)

    l_fp="<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->"
    l_rp="<!-- MxM banner -->"

    lyric = re.findall ( l_fp+'(.*?)'+l_rp,soup, re.DOTALL)[0]
    l_clean=re.compile('<.*?>|\[.*?\]') 
    lyric=re.sub(l_clean,'',lyric)

    t_fp='<div class="div-share"><h1>"'
    t_rp='" lyrics</h1></div>'


    title = re.findall ( t_fp+'(.*?)'+t_rp,soup, re.DOTALL)[0]
    t_clean=re.compile('\[.*?\]')   
    title=re.sub(t_clean,'',title).replace(" ","")

    a_fp='<h2><b>'
    a_rp=' Lyrics</b></h2>'


    artist = re.findall ( a_fp+'(.*?)'+a_rp,soup, re.DOTALL)[0]
    a_clean=re.compile('\[.*?\]')   
    artist=re.sub(a_clean,'',artist).replace(" ","")


    lyric=[x for x in lyric.split('\n') if x!=""]
    return artist,title,lyric


def get_line(search_key):
    
    search_api_key = "AIzaSyCeFrueNhxoZwi0oD_KzefkwCq7y-NmN3I"
    cse_id = "001801730276603322393:x4voe23cbsi"

    results = google_search(search_key, search_api_key, cse_id, num=2)
    url="http://"+results[0]['formattedUrl']
    artist,title,lyrics=get_lyric(url)

    sim_score=[]
    for i in lyrics:
        sim_score.append(SequenceMatcher(None,i,search_key).ratio())
    ind=sim_score.index(max(sim_score))
    
    if ind==len(lyrics)-1:
        ind=ind-2
        print("last")
    if ind==len(lyrics)-2:
        ind=ind-1
        print("lastbefore")

    return(artist,title,lyrics[ind]+"\n"+lyrics[ind+1]+"\n"+lyrics[ind+2]+"...")


class StreamListener(tweepy.StreamListener):

    def on_status(self, status):
        global handle
        try:
            if status.entities['user_mentions'][0]['screen_name']==handle:
                user=status.user.screen_name
                line=status.text.replace("@"+handle,"").replace("\n","")
                print(line)
                artist,song,lyric=get_line(line)
                
                #api.update_status(status=".@"+user+"\n"+lyric, in_reply_to_status_id = status.id)
                meta="\n#"+artist+"  #"+song+"\n#"+handle
                print(lyric,len(lyric),"\n")
                api.create_favorite(status.id)
                try:
                    api.update_status(status=lyric+meta, in_reply_to_status_id = status.id,auto_populate_reply_metadata=True)
                except:
                    lyric="\n".join(lyric.split("\n")[1:])
                    try:    
                        api.update_status(status=lyric+meta, in_reply_to_status_id = status.id,auto_populate_reply_metadata=True)
                    except:
                        lyric="\n".join(lyric.split("\n")[1:])    
                        api.update_status(status=lyric+meta, in_reply_to_status_id = status.id,auto_populate_reply_metadata=True)


                quote="https://twitter.com/"+user+"/status/"+str(status.id)
                #print(quote)
                try:
                    api.update_status(status=lyric+meta+"\n"+quote)
                except:
                    lyric="\n".join(lyric.split("\n")[1:])
                    api.update_status(status=lyric+meta+"\n"+quote)
                api.create_friendship(user)
                print(lyric)
        except Exception as e:
            print(e)
        
    def on_error(self, status_code):
        if status_code == 420:
            return False


stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
stream.filter(track=[handle])
