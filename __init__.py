# Required Dependencies
from gmusicapi import Mobileclient
import logging

from flask import Flask, render_template

from flask_ask import Ask, audio, statement

app = Flask(__name__)

# sets the google play Mobileclient Api to api
api = Mobileclient()

# The directory that you want this to run on
ask = Ask(app, "/googlemusic")

# set to DEBUG for when it breaks or for more info, use INFO for a less
# cluttered log.
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

# Build a credentials storage setup or something, fuck this plaintext shit
login = api.login('EMAIL', 'PASSWORD',
                  Mobileclient.FROM_MAC_ADDRESS)


# Login in to google music and use cached key if available
@ask.launch
def google_music_login():
    if api.is_authenticated() is True:
        return statement(render_template('welcome')) \
            .simple_card(title="Echo Play", content="Logged in successfully.")
    elif login is True:
        return statement(render_template('welcome')) \
            .simple_card(title="Echo Play", content="Logged in successfully.")
    else:
        return statement(render_template('login_failure')) \
            .simple_card(title="Echo Play",
                         content="Failed to login.")


class Song:
    def __init__(self, query):
        self.query = query
        self.url = ""
        self.info = ""

    @property
    def url_fetcher(self):
        try:
            if self.query is '':
                raise ValueError
            search_result = api.search(self.query)
            self.url = api.get_stream_url(search_result['song_hits'][0]
                                          ['track']['nid'], quality=u'hi')
            self.info = search_result['song_hits'][0]['track']['title']
            + " by " + search_result['song_hits'][0]['track']['artist']

        except ValueError as e:
            return statement(render_template('unable_to_find_song')) \
                .simple_card(title="Google Music",
                             content=e.with_traceback())


# Function to play a song
# return audio(speech = []).play([], offset=[number in milliseconds])
@ask.intent("PlaySingleSongIntent")
def play_single_song(query):
    try:
        if query is '':
            raise ValueError
        google_music_login()
        playing_message = "Playing" + Song.info(query)
        return audio(speech=playing_message).play(Song.url(query)) \
            .simple_card(title="Google Music",
                         content=playing_message)

    except (ValueError, IndexError) as e:
        return statement("Unable to queue the song") \
            .simple_card(title="Google Music",
                         content=e.with_traceback())


# BETA testing for queue support
@ask.intent("EnqueueSongIntent")
def enqueue_song(queue_query):
    try:
        if queue_query is '':
            raise ValueError

        search_result = api.search(queue_query)
        stream_url = api.get_stream_url(search_result['song_hits'][0]['track']
                                        ['nid'], quality=u'hi')
        song_info = "Queued " + search_result['song_hits'][0]['track']['title']
        + " by " + search_result['song_hits'][0]['track']['artist']

        return audio(speech="Queued").enqueue(stream_url) \
            .simple_card(title="Google Music",
                         content=song_info)

    except (ValueError, IndexError) as e:
        return statement("Unable to queue the song") \
            .simple_card(title="Google Music",
                         content=e.with_traceback())


'''
# Future functionality
# Add music to playlist through voice commands
# delete/create playlists

# BETA testing for playlist support


playlist = []

# ALPHA testing for radio support


@ask.intent("PlayArtistRadioIntent")
def start_radio(query):
    search_result = api.search(query)
    stream_url = api.get_stream_url(search_result['station_hits'][0]['track']
                                    ['nid'], quality=u'hi')
    return audio(speech=song_info).play(stream_url) \
        .simple_card(title="Google Music",
                     content=song_info)

# ALPHA testing for skip support


@ask.intent("PlayNextIntent")  # TODO Needs implementing
def play_next():
    return True

# ALPHA testing for pause support


@ask.intent("AMAZON.PauseIntent")
def pause_song():
    return audio().stop()

# ALPHA testing for resume support


@ask.intent("AMAZON.ResumeIntent")
def resume_song():
    return audio().resume()  # Restarts song when resumed, need to fix that

# ALPHA testing for skip song support


@ask.intent("SkipSongIntent")
def skip_song():
    return audio(speech="paused").s

# Some debug function that is needed by flask
'''

if __name__ == '__main__':
    app.run(debug=True)
