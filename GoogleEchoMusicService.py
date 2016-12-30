# Required Dependencies
import time
from flask import Flask, render_template, json

from flask_ask import Ask, audio, statement, current_stream, logger, question

import logging

# imports functions from song.py
from song import google_music_login, QueueManager

queue = QueueManager()

app = Flask(__name__)

# The directory that you want this to run on
ask = Ask(app, "/googlemusic")

# set to DEBUG for when it breaks or for more info, use INFO for a less
# cluttered log.
logging.getLogger("flask_ask").setLevel(logging.DEBUG)


# Login in to google music and use cached key if available
@ask.launch
def login():
    text = 'Welcome to Google Music. Try asking me to play a song'
    prompt = 'You can ask me to play a song. For example say, play Scar Tissue'
    if google_music_login() is True:
        return question(text).reprompt(prompt) \
            .simple_card(title='Google Music',
                         content=text)
    else:
        return statement(render_template('login_failed')) \
            .simple_card(title="Google Music",
                         content=render_template('login_failed'))


# Function to play a song
# return audio(speech = []).play([], offset=[number in milliseconds])
@ask.intent("PlaySingleSongIntent")
def play_single_song(query):
    try:
        if query is '':
            raise ValueError
        queue.reset()
        # queue.add_playlist_tracks()
        queue.format_for_single_track(query)
        stream = queue.start()
        queue.songacquiredtimestamp = int(round(time.time()) * 1000)
        playing_message = "Playing " + queue.song_info()
        return audio(speech=playing_message).play(stream) \
            .simple_card(title="Google Music",
                         content=playing_message)

    except (ValueError, IndexError):
        queue.revert()
        return statement(render_template('unable_to_find_song')) \
            .simple_card(title="Google Music",
                         content=render_template('unable_to_find_song'))


# BETA testing for queue support
@ask.intent("EnqueueSongIntent")
def enqueue_song(query):
    try:
        if query is '':
            raise ValueError
        queue.format_for_single_track(query)
        queue.add(query)

        return statement("")

    except (ValueError, IndexError):
        queue.revert()
        return statement("Unable to queue the song") \
            .simple_card(title="Google Music",
                         content=query + "Song failed to queue.")


@ask.intent("PlayPlaylistIntent")
def play_playlist(customPlaylists):
    try:
        if customPlaylists is '':
            raise ValueError
        queue.reset()
        queue.find_playlist(customPlaylists)
        stream = queue.start()
        playing_message = "Playing songs from " + queue.playlistname
        return audio(speech=playing_message).play(stream) \
            .simple_card(title="Google Music",
                         content=playing_message)

    except (ValueError, IndexError):
        msg = "No playlist was found by the name of " + customPlaylists
        queue.reset()
        return statement(msg) \
            .simple_card(title="Google Music",
                         content=render_template('unable_to_find_song'))


@ask.on_playback_nearly_finished()
def nearly_finished():
    if queue.up_next:
        _infodump('Alexa is now ready for a Next or Previous Intent')
        next_stream = queue.up_next
        return audio().enqueue(next_stream)
    else:
        _infodump('Nearly finished with last song in playlist')


@ask.on_playback_finished()
def play_back_finished():
    _infodump('FINISHED Audio stream from {}'.format(current_stream.url))
    if queue.up_next:
        queue.step()
    else:
        return statement('')


@ask.intent('AMAZON.NextIntent')
def next_song():
    if queue.up_next:
        speech = 'ok'
        next_stream = queue.step()
        return audio(speech).play(next_stream)
    else:
        return audio('There are no more songs in the queue')


@ask.intent('AMAZON.PreviousIntent')
def previous_song():
    if queue.previous:
        speech = 'playing previously played song'
        prev_stream = queue.step_back()
        return audio(speech).play(prev_stream)

    else:
        return audio('There are no songs in your playlist history.')


@ask.intent('AMAZON.StartOverIntent')
def restart_track():
    if queue.current:
        speech = 'Restarting current track'
        return audio(speech).play(queue.song_url(), offset=0)
    else:
        return statement('There is no current song')


@ask.intent('AMAZON.PauseIntent')
def pause():
    msg = 'Paused the Playlist on track {}'.format(queue.current_position)
    queue.songoffset = int(round(time.time()) * 1000) - queue.songacquiredtimestamp
    return audio('Pausing.').stop().simple_card(msg)


@ask.intent('AMAZON.ResumeIntent')
def resume():
    msg = 'Resuming the Playlist on track {}'.format(queue.current_position)
    return audio('Resuming.').play(stream_url=queue.song_url(), offset=(queue.songoffset)).simple_card(msg)


# This is all ALPHA functionality that may or may not be included
# in a future release
'''
# Future functionality
# Add music to playlist through voice commands
# delete/create playlists
# shuffle playlist

# SUPER ALPHA
# testing for radio support
@ask.intent("PlayArtistRadioIntent")
def start_radio(query):
    search_result = api.search(query)
    stream_url = api.get_stream_url(search_result['station_hits'][0]['track']
                                    ['nid'], quality=u'hi')
    return audio(speech=song_info).play(stream_url) \
        .simple_card(title="Google Music",
                     content=song_info)
'''


@ask.session_ended
def session_ended():
    return "", 200


def _infodump(obj, indent=2):
    msg = json.dumps(obj, indent=indent)
    logger.info(msg + '\n')


if __name__ == '__main__':
    app.run(debug=True)
