from gmusicapi import Mobileclient
import logging

from flask import Flask, render_template

from flask_ask import Ask, audio, statement

app = Flask(__name__)

api = Mobileclient()

ask = Ask(app, "/")
# logging.DEBUG for when breaks
logging.getLogger("flask_ask").setLevel(logging.INFO)


# Build a credentials storage setup or something, fuck this plaintext shit
login = api.login('USERNAME', 'PASSWORD', Mobileclient.FROM_MAC_ADDRESS)

# def retrieve_single_song_result(query):
@ask.launch
def initialize_echo_play():
    if api.is_authenticated() is True:
        return statement(render_template('welcome')) \
            .simple_card(title="Echo Play", content="Logged in successfully.")
    elif login is True:
        return statement(render_template('welcome')) \
            .simple_card(title="Echo Play", content="Logged in successfully.")
    else:
        return statement(render_template('login_failure')) \
            .simple_card(title="Echo Play",
                         content="Failed to login.")  # TODO maybe print out the exception if there is one?

#return audio(speech = []).play([], offset=[number in milliseconds])
@ask.intent("PlaySingleSongIntent")
def play_single_song(query):
    try:
        if query is '':
            raise ValueError

        search_result = api.search(query)

        stream_url = api.get_stream_url(search_result['song_hits'][0]['track']['nid'], quality=u'hi')

        song_info = "Playing " + search_result['song_hits'][0]['track']['title'] \
                    + " by " + search_result['song_hits'][0]['track']['artist']

        return audio(speech=song_info).play(stream_url) \
            .simple_card(title="Google Music",
                         content=song_info)

    except (ValueError, IndexError) as e:
        return statement(render_template('unable_to_find_song')) \
            .simple_card(e.with_traceback())

@ask.intent("PlayArtistRadioIntent")
def start_radio(query):
    search_result = api.search(query)
    stream_url = api.get_stream_url(search_result['station_hits'][0]['track']['nid'], quality=u'hi')
    return audio(speech='song_info').play(stream_url) \
        .simple_card(title="Google Music", content="song_info")

# Need to make a dictionary or something

@ask.intent("EnqueueSongIntent")
def enqueue_song(queue_query):
    try:
        if queue_query is '':
            raise ValueError

        search_result = api.search(queue_query)
        stream_url = api.get_stream_url(search_result['song_hits'][0]['track']['nid'], quality=u'hi')
        queue_phrase = "Queuing " + search_result['song_hits'][0]['track']['title']

        return audio(speech=queue_phrase).enqueue(stream_url) \
                .simple_card(title="Google Music",
                             content=queue_phrase)

    except (ValueError, IndexError) as e:
        return statement("Unable to queue the song") \
            .simple_card(title="Google Music",
                         content= e.with_traceback())

@ask.intent("PlayNextIntent")  # TODO Needs implementing
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
