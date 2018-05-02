import itertools
import threading
import time
import sys
import spotipy
import spotipy.util as util
import urllib2
from bs4 import BeautifulSoup


done = False
#here is the animation
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rloading ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')

t = threading.Thread(target=animate)
t.start()

#long process here

#finds if the artist has an event on
def getUnderTheRadar(searched, artist):
    Url = "http://www.undertheradar.co.nz/index.php?task=searchall&q="+searched
    try:
        html = urllib2.urlopen(Url)
    except urllib2.HTTPError as e:
        print("error opening url")
        return None
    try:
        soup = BeautifulSoup(html.read(), "html.parser")
        main = soup.find("div", class_="er ror-oran ge")
        if main == None:
            main = soup.find("div", class_="gig-title")
            s = main.get_text()
            search = artist[0]
            search = search.encode('ascii','ignore')
            if(s.find(search)!=-1):
                main = main.find('a')
                text = "Gig on \nLink:  http://www.undertheradar.co.nz" + main.get('href')
                return text
            for e in artist[1:]:
                e = e.encode('ascii','ignore')
                search= e
                if(s.find(search)!=-1):
                    main = main.find('a')
                    text = "Gig on \nLink:  http://www.undertheradar.co.nz" + main.get('href')
                    return text
        else:
            main = main.find('em')
            text = "No Gig"
    except AttributeError as e:
        print(e)
        print("error beauty soup")
        return None
    return "No Gig"

def getEventFinda(searched, artist):
    Url = "https://www.eventfinda.co.nz/search?q="+searched
    try:
        html = urllib2.urlopen(Url)
    except urllib2.HTTPError as e:
        print("error opening url")
        return None
    try:
        soup = BeautifulSoup(html.read(), "html.parser")
        current = soup.find("h3")
        main = soup.find("div", class_="media-body")
        if current.get_text()!="Past events":
            if main != None:
                main = soup.find("h4", class_="media-heading")
                keyWords = main.find_all("em")
                if keyWords != []:
                    title = main.get_text()
                    
                    search = artist[0]
                    search = search.encode('ascii','ignore')
                    for e in artist[1:]:
                        e = e.encode('ascii','ignore')
                        search= search+" "+e
                    if(title.find(search)!=-1):
                        main = main.find('a')
                        text = "Gig on \nLink:  https://www.eventfinda.co.nz" + main.get('href')
                        return text
                else:
                    text = "No Gig"
                    return text
        else:
            #main = main.find('em')
            text = "No Gig"
    except AttributeError as e:
        print(e)
        print("error beauty soup")
        return None
    return "No Gig"

#starts a search for events with a list of artists
def searchEvent(artist):
    search = artist[0]
    search = search.encode('ascii','ignore')
    for e in artist[1:]:
        e = e.encode('ascii','ignore')
        search= search+"+"+e
    
    underTheRadar = getUnderTheRadar(search, artist)
    if underTheRadar == None or underTheRadar == "No Gig":
        eventFinda = getEventFinda(search, artist)
        if eventFinda == None:
            print("UnderTheRadar")
            print("Page not found")
            return None
        elif eventFinda == "No Gig":
            return None
        else:
            return search+"\n"+eventFinda
    else:
        return search+"\n"+underTheRadar

#set up authentication
#Need to go to https://developer.spotify.com/ and sign up to receive a client ID and client Secret
token = util.prompt_for_user_token(username='Replace with username',scope='user-follow-read',client_id='Replace with client ID',client_secret='Replace with client ID',redirect_uri='https://www.google.com/')
spotify = spotipy.Spotify(auth=token)

#initialise variables
listArtists = []
artists = spotify.current_user_followed_artists(limit=50);

#iterate till at the end to get around the 50 limit
while artists['artists']['items']!=[]:
    for key in artists['artists']['items']:
        #gets name of each artist and splits it into words
        data = key['name']
        words = data.split()
        listArtists.append(words)
        #checks if last artist
        if key == artists['artists']['items'][-1]:
            after = key['id']
    #find next 50 artists
    artists = spotify.current_user_followed_artists(limit=50,after=after);

gigs = []
for rows in listArtists:
    result = searchEvent(rows)
    print("loading")
    if result != None:
        gigs.append(result)

done = True

for rows in gigs:
    print(rows)

raw_input()
