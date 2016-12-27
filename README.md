# GooglePlayEchoMusicService #
Google Play Music Backend for Amazon Echo 
### NOTE ###
This is only set up for development right now as I'm sure this skill won't be published ever. I just really didn't want to buy another music subscription. 
## Setup Instructions: ##
(These were written from a linux install but I assume that it is similar for other platforms.)

### Things you'll need to install / have before setup: ###

[Python 3](https://www.python.org/downloads/) (the latest should work)
<br>
[Ngrok](https://ngrok.com/download) (secure tunneling over localhost)
<br>
A Google Play Subscription (haven't tested free accounts with this yet)
<br>
Amazon Echo, Tap, or Dot
<br>
[Screen](https://www.howtoforge.com/linux_screen) (This isn't necessary but makes it easier to keep the program running when you log off of your ssh session on linux.)

### Install these pip modules:  ###
- gmusicapi `pip install gmusicapi`
- flask `pip install flask`
- flask-ask `pip install flask-ask`

### Setup Instructions on local machine: ###

1. Clone the repo to your local machine.
2. Create a <a href="https://www.howtoforge.com/linux_screen" target="_blank">screen </a> instance.
3. Put your email and password for your google account in the loginCredentials.py file.
4. Start GoogleEchoMusicService.py.
5. Start Ngrok `./ngrok http 5000`.



### Setting up your Alexa Skill: ###

1. Create an AWS developer account at <a href="https://developer.amazon.com/" target="_blank">  Amazons Developer Site</a>
2. Create an Alexa Skills Kit
3. On the Skill Information page put `Google Music` in the Name field and `google music` for the Invocation Name. Check `yes` for "Does this skill use the audio player directives?"
4. On the "Interaction Model" page copy the Intent Schema and Sample Utterances to their respective fields.
5. On the "Configuration" page set "Service Endpoint Type:" to `HTTPS` and put your ngrok url in with `/googlemusic` added to the end
6. On the "SSL Certificate" page select "My development endpoint is a sub-domain of a domain that has a wildcard certificate from a certificate authority" and click next
7. Make sure on the "Test" page the skill is enabled for testing on your account and your ready to go!





