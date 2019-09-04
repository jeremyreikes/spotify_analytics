import sys
import spotipy
import spotipy.util as util
from api_keys import spotify_client_id, spotify_client_secret
from spotipy.oauth2 import SpotifyClientCredentials
import os
from json.decoder import JSONDecodeError
scope =  "user-modify-private"
redirect_uri = 'http://localhost/'
username = '12153126623'

os.remove(f".cache-{username}")

try:
    token = util.prompt_for_user_token(username, scope = scope, client_id=spotify_client_id, client_secret=spotify_client_secret, redirect_uri = redirect_uri)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope = scope, client_id=spotify_client_id, client_secret=spotify_client_secret, redirect_uri = redirect_uri)



print(token)

# client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
# sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

if token:
    sp = spotipy.Spotify(auth=token)

    results = sp.current_user_playlists()
    for playlist in results['items']:
        print(playlist)


# else:
#     print("Can't get token for", username)

#
#from api_keys import spotify_client_id, spotify_client_secret
#
# redirect_uri = 'http://localhost:8888'
# import spotipy
# import spotipy.util as util
# import spotipy.oauth2 as oauth2
# import sys
#
# if len(sys.argv) > 1:
#     username = sys.argv[1]
#
#
# token = util.prompt_for_user_token(
#         username=username,
#         client_id=spoitfy_client_id,
#         client_secret=spotify_client_secret,
#         redirect_uri=redirect_uri)
#
# spotify = spotipy.Spotify(auth=token)
#
# def get_playlists(username):
#     playlists = spotify.user_playlists(username)
#     check = 1
#
#     while True:
#         for playlist in playlists['items']:
#             # in rare cases, playlists may not be found, so playlists['next']
#             # is None. Skip these.
#             if playlist['name'] is not None:
#                 print('')
#                 print('playlist:')
#                 playlist_title = playlist['name'] + ' - ' + str(playlist['tracks']['total'])
#                 playlist_title += ' tracks'
#                 print(playlist_title)
#                 show_playlist(playlist)
#                 check += 1
#         if playlists['next']:
#             playlists = spotify.next(playlists)
#         else:
#             break
#
#
# def show_playlist(playlist):
#     results = spotify.user_playlist(
#         playlist['owner']['id'], playlist['id'], fields='tracks,next')
#
#     tracks = results['tracks']
#     show_tracks(tracks)
#
#
# def show_tracks(tracks):
#     n = 1
#     while True:
#         for item in tracks['items']:
#             track = item['track']
#             track_title = str(n) + '. '
#             track_title += track['name'] + ' - ' + track['artists'][0]['name']
#             print(track_title)
#             n += 1
#         # 1 page = 50 results
#         # check if there are more pages
#         if tracks['next']:
#             tracks = spotify.next(tracks)
#         else:
#             break
