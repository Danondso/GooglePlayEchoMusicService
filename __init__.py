from gmusicapi import Mobileclient
import logging

from flask import Flask, render_template

from flask_ask import Ask, audio, statement

app = Flask(__name__)

api = Mobileclient()

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


# Build a credentials storage setup or something, fuck this plaintext shit
def login():
    return api.login('email', 'password', 'android_id')


# def retrieve_single_song_result(query):
@ask.launch
def initialize_echo_play():
    if login() is True:
        return statement(render_template('welcome')) \
            .simple_card(title="Echo Play", content="Logged in successfully.")
    else:
        return statement(render_template('login_failure')) \
            .simple_card(title="Echo Play",
                         content="Failed to login.")  # TODO maybe print out the exception if there is one?


def get_single_song(query):
    try:
        if query is '':
            raise ValueError
        search_result = api.search(query)
        if search_result is None:
            raise ValueError
    except ValueError as e:
        return statement(render_template('unable_to_find_song')) \
            .simple_card(e.with_traceback())


@ask.intent("PlaySingleSongIntent")
def play_single_song(query):
    search_result = get_single_song(query)
    stream_url = api.get_stream_url(search_result['song_hits'][0]['track']['nid'], quality=u'hi')
    song_info = "Playing " + search_result['song_hits'][0]['track']['title'] \
                + " by " + search_result['song_hits'][0]['track']['artist']
    return audio(speech=song_info).play(stream_url=stream_url) \
        .simple_card(title="Google Music",
                     content=song_info)


@ask.intent("EnqueueSongIntent")
def enqueue_song(queue_query):
    search_result = get_single_song(queue_query)
    stream_url = api.get_stream_url(search_result['song_hits'][0]['track']['nid'], quality=u'hi')
    return audio(speech="").enqueue(stream_url=stream_url)


# @ask.intent("PlayArtistRadioIntent")
# def start_radio(query):
#     search_result = api.search(query)
#     stream_url = api.get_stream_url(search_result['station_hits'][0]['track']['nid'], quality=u'hi')
#     return audio(speech=song_info).play(stream_url=stream_url) \
#         .simple_card(title="Google Music",
#                      content=song_info)


#Future functionality
#Add music to playlist through voice commands
#delete/create playlists



@ask.intent("PlayNextIntent")
def play_next():
    return True


@ask.intent("AMAZON.PauseIntent")
def pause_song():
    return audio().stop()


@ask.intent("AMAZON.ResumeIntent")
def resume_song():
    return audio().resume()  # Restarts song when resumed, need to fix that


@ask.intent("SkipSongIntent")
def skip_song():
    return audio(speech="paused").s


if __name__ == '__main__':
    app.run(debug=True)
