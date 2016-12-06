from gmusicapi import Mobileclient
from flask import Flask

app = Flask(__name__)

api = Mobileclient()

def search(query):
    if query is not None:
        return api.search(query.encode("UTF-8"))

def retrieve_single_song_result(search_result):
    return api.get_stream_url(search_result['song_hits'][0]['track']['nid'], quality=u'hi')

search_result = search("Don't fear the reaper")
stream_result = retrieve_single_song_result(search_result)

print(stream_result)
