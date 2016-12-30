from gmusicapi import Mobileclient
import loginCredentials


api = Mobileclient()
f = open("Playlist_names_to_copy.txt", "w")
api.login(loginCredentials.username, loginCredentials.password,
          Mobileclient.FROM_MAC_ADDRESS)

playlists = api.get_all_user_playlist_contents()
for list in playlists:
    f.write(str(list['name']) + "\n")
f.close()
