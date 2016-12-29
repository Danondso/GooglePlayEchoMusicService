# Required Dependencies
from gmusicapi import Mobileclient

import loginCredentials

# sets the google play Mobileclient Api to api
api = Mobileclient()

# accesses loginCredentials.py for username and password
login = api.login(loginCredentials.username, loginCredentials.password,
                  Mobileclient.FROM_MAC_ADDRESS)


# gets the song data like url and artist
class Song:
    def __init__(self, query):
        self.query = query
        self.url = None
        self.info = None
        self.id = None
        google_music_login()
        self.id_fecher()
        self.url_link()
        self.song_info()

    def id_fecher(self):
            self.id = api.search(self.query)

    def url_link(self):
            self.url = api.get_stream_url(self.id['song_hits'][0]
                                          ['track']['nid'], quality=u'hi')

    def song_info(self):
            self.info = self.id['song_hits'][0]['track']['title'] + " by " + \
                self.id['song_hits'][0]['track']['artist']


# Login in to google music and use cached key if available
def google_music_login():
    if api.is_authenticated() is True:
        return True
    elif login is True:
        return True
    else:
        return False
