# Required Dependencies
from flask import Flask, render_template

from flask_ask import Ask, audio, statement

import logging
# imports functions from song.py
from song import Song, google_music_login

app = Flask(__name__)

# The directory that you want this to run on
ask = Ask(app, "/googlemusic")

# set to DEBUG for when it breaks or for more info, use INFO for a less
# cluttered log.
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


# Login in to google music and use cached key if available
@ask.launch
def login():
    if google_music_login() is True:
        return statement(render_template('welcome')) \
            .simple_card(title='Google Music',
                         content='Welcome to Google Music. \
                                 Try asking me to play a song.')
    else:
        return statement(render_template('login_failed')) \
            .simple_card(title="Google Music",
                         content="Failed to login.")


# Function to play a song
# return audio(speech = []).play([], offset=[number in milliseconds])
@ask.intent("PlaySingleSongIntent")
def play_single_song(query):
    try:
        if query is '' or google_music_login() is False:
            raise ValueError
        song = Song(query)
        playing_message = "Playing" + song.info
        return audio(speech=playing_message).play(song.url) \
            .simple_card(title="Google Music",
                         content=playing_message)

    except (ValueError):
        return statement(render_template('unable_to_find_song')) \
            .simple_card(title="Google Music",
                         content=render_template('unable_to_find_song'))


# BETA testing for queue support
@ask.intent("EnqueueSongIntent")
def enqueue_song(query):
    try:
        if query is '':
            raise ValueError
        song = Song(query)
        queue_message = "Queued " + song.info
        return audio(speech="Queued").enqueue(song.url) \
            .simple_card(title="Google Music",
                         content=queue_message)

    except (ValueError, IndexError) as e:
        return statement("Unable to queue the song") \
            .simple_card(title="Google Music",
                         content=e.with_traceback())


# This is all ALPHA functionality that may or may not be included
# in a future release
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
