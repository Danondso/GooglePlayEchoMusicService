# Required Dependencies
from gmusicapi import Mobileclient

from fuzzywuzzy import fuzz, process

import collections

import loginCredentials

import pprint
pp = pprint.PrettyPrinter(indent=4)
# pp.pprint()
# sets the google play Mobileclient Api to api
api = Mobileclient()

# accesses loginCredentials.py for username and password
login = api.login(loginCredentials.username, loginCredentials.password,
                  Mobileclient.FROM_MAC_ADDRESS)


# gets the song data like url and artist
class QueueManager:
    def __init__(self):
        # self._sid = []
        self._queued = collections.deque()
        self._history = collections.deque()
        self._current = None
        self.songurl = None
        self.songinfo = None
        self.songartist = None
        self.songname = None
        self.songoffset = None
        self.playlistid = None
        self.playlistname = None

    def status(self):
        status = {
            'Current Position': self.current_position,
            'Current Song ID': self.current,
            'Next Song ID': self.up_next,
            'Previous Song ID': self.previous,
            'History': list(self.history)
        }
        return status

    @property
    def up_next(self):
        """Returns the song id at the front of the queue"""
        qcopy = self._queued.copy()
        try:
            return song_url(qcopy.popleft())
        except IndexError:
            return False

    @property
    def current(self):
        return self._current

#    @current.setter
#    def current(self, sid):
#        self._save_to_history()
#        self._current = sid

    @property
    def history(self):
        return self._history

    @property
    def previous(self):
        hcopy = self.history.copy()
        try:
            return hcopy.pop()
        except IndexError:
            return None

    def add(self, query):
        # self._sid.append(sid)
        self._queued.append(query)

#    def extend(self, sid):
#         self._sid.extend(sid)
#        self._queued.extend(sid)

    def _save_to_history(self):
        if self._current:
            self._history.append(self._current)

    def end_current(self):
        self._save_to_history()
        self._current = None

    def step(self):
        self.end_current()
        self._current = self._queued.popleft()
        return self.song_url()

    def step_back(self):
        self._queued.appendleft(self._current)
        self._current = self._history.pop()
        return self.song_url()

    def reset(self):
        self._queued = collections.deque()
        self._history = collections.deque()
        self._current = None

    def start(self):
        return self.step()

    @property
    def current_position(self):
        return len(self._history) + 1

    def id_fecher(self, query):
        google_music_login()
        self.id = api.search(query)
        return self.id

    def song_url(self):
        try:
            self.songurl = api.get_stream_url(self._current['track']
                                              ['storeId'], quality=u'hi')
            return self.songurl
        except KeyError:
            self.songurl = api.get_stream_url(self._current['trackId'],
                                              quality=u'hi')
            return self.songurl

    def song_info(self):
        self.songinfo = self._current['track']['title'] + " by " +  \
            self._current['track']['artist']
        return self.songinfo

    def revert(self):
        try:
            return self._queued.pop()
        except IndexError:
            return None

    def format_for_single_track(self, query):
        query = self.id_fecher(query)
        query = query['song_hits'][0]
        return self.add(query)

    def add_playlist_tracks(self, number):
        self.playlistname = self.playlistid[number]['name']
        self.playlistid = self.playlistid[number]['tracks']
        count = 0
        pp.pprint(self.playlistid)
        for tracks in self.playlistid:
            # pp.pprint(self.playlistid[count])
            self.add(self.playlistid[count])
            count += 1

    def find_playlist(self, query):
        self.playlistid = api.get_all_user_playlist_contents()
        count = 0
        best_playlist = None
        best_score = 0
        for list in self.playlistid:
            score = fuzz.ratio(list['name'].lower().replace(" ", ""),
                               query.lower().replace(" ", ""))
            if score > best_score:
                best_playlist = count
                best_score = score
            count += 1
        return self.add_playlist_tracks(best_playlist)


def song_url(nid):
    try:
        songurl = api.get_stream_url(nid['track']['storeId'],
                                     quality=u'hi')
        return songurl
    except KeyError:
        songurl = api.get_stream_url(nid['trackId'],
                                     quality=u'hi')
    return songurl


# Login in to google music and use cached key if available
def google_music_login():
    if api.is_authenticated() is True:
        return True
    elif login is True:
        return True
    else:
        return False


# api.create_station(name, track_id=None, artist_id=None, album_id=None,
# genre_id=None, playlist_token=None, curated_station_id=None)
