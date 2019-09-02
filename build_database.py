import pandas as pd
import numpy as np
import warnings
import sys
from tqdm import tqdm
from spotify_fetching import df
tqdm.pandas()
warnings.filterwarnings('ignore')
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import numpy as np
import re
from api_keys import genius_client_access_token
from api_keys import spotify_client_id, spotify_client_secret
client_id = spotify_client_id
client_secret = spotify_client_secret
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
from pymongo import MongoClient
client = MongoClient()
db = client.spotify_db
all_tracks = db.all_tracks
parsed_playlists = db.parsed_playlists
from time import sleep
useless_features = ['type', 'uri', 'track_href', 'analysis_url', 'id']


def get_track(tid):
    return all_tracks.find_one({'_id': tid})

def get_playlist(pid):
    return parsed_playlists.find_one({'_id', pid})

def add_audio_features():
    all_tids = []
    for track in all_tracks.find():
        all_tids.append(track['_id'])
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    for i in tqdm(range(0,(len(all_tids) // 50) + 1)):
        offset = i*50
        try:
            curr_ids = all_tids[offset:offset+50]
        except:
            curr_ids = all_tids[offset:]
        try:
            all_audio_features = sp.audio_features(curr_ids)
        except:
            sleep(30)
            all_audio_features = sp.audio_features(curr_ids)
        for curr_features in all_audio_features:
            if not curr_features:
                continue
            tid = curr_features['id']
            for feature in useless_features:
                del curr_features[feature]
            all_tracks.find_and_modify({'_id': tid}, {'$set': {'audio_features': curr_features}})


def add_name_and_artist():
    all_tids = []
    for track in all_tracks.find():
        all_tids.append(track['_id'])
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    for i in tqdm(range(0,(len(all_tids) // 50) + 1)):
        offset = i*50
        try:
            curr_ids = all_tids[offset:offset+50]
        except:
            curr_ids = all_tids[offset:]
        try:
            raw_tracks = sp.tracks(curr_ids)['tracks']
        except:
            sleep(30)
            raw_tracks = sp.tracks(curr_ids)['tracks']
        for curr_track in raw_tracks:
            if not curr_track:
                continue
            tid = curr_track['id']
            name = curr_track['name']
            artist_id = curr_track['album']['artists'][0]['id']
            artist_name = curr_track['album']['artists'][0]['name']
            release_date = curr_track['album']['release_date']
            popularity = curr_track['popularity']
            all_tracks.find_and_modify({'_id': tid}, {'$set': {'name': name, 'artist_name': artist_name, 'artist_id': artist_id, 'release_date': release_date, 'popularity': popularity}})
#
def add_genres():
    all_tids = []
    for track in all_tracks.find({'genres': {'$exists': False}, 'artist_id': {'$exists': False}}):
        tid = track['_id']
        artist_id = track['artist_id']
        all_tids.append((tid, artist_id))
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    for i in tqdm(range(0,(len(all_tids) // 50) + 1)):
        offset = i*50
        try:
            curr_ids = all_tids[offset:offset+50]
        except:
            curr_ids = all_tids[offset:]
        tids = [curr_id[0] for curr_id in curr_ids]
        artist_ids = [curr_id[1] for curr_id in curr_ids]
        try:
            curr_artists = sp.artists(artist_ids)['artists']
        except:
            sleep(30)
            curr_artists = sp.artists(artist_ids)['artists']
        for index, curr_artist in enumerate(curr_artists):
            if not curr_artist:
                continue
            genres = curr_artist['genres']
            all_tracks.find_and_modify({'_id': tids[index]}, {'$set': {'genres': genres}})

    # do this shit
def update_lyrics():
    genius = lyricsgenius.Genius(genius_client_access_token)
    genius.remove_section_headers = True
    genius.verbose = False
    for track in all_tracks.find({'lyrics': {'$exists' : False}}):
        try:
            tid = track['_id']
            track_name = track['name']
            artist_name = track['artist_name']
            song = genius.search_song(track_name, artist_name)
            if song:
                lyrics = song.lyrics
                stripped = ' '.join(lyrics.split('\n'))
                regex = re.compile('([\][])')
                clean_lyrics = re.sub(regex, '', stripped)
                all_tracks.find_and_modify({'_id': tid}, {'$set': {'lyrics': clean_lyrics}})





# track = add_audio_features(['0Svkvt5I79wficMFgaqEQJ'])
# all_tracks.find_one(limit=20)
# parsed_playlists.count()
#
# print(db.command("collstats", "all_tracks"))
# add_audio_features()
# add_name_and_artist()
all_tracks.find_one()

add_audio_features()
add_name_and_artist()
add_genres()
add_lyrics()

# all_tracks.drop()
# parsed_playlists.drop()
# build_database()
# for index, track in enumerate(all_tracks.find()):
#     if index == 50:
#         break
#     print(track)

'''
schedule-
 twitter_scrape to get playlist names
 Get_playlist_tracks in spotify_fetching to get tracks and playlists

  build_database
  add_name_and_artist AND ALSO add_audio_features IN ANY ORDER
  ONCE A SONG HAS ARTIST NAME, get_gneres()
  ONCE A SONG HAS TRACKNAME AND ARTIST NAME, get lyrics


'''
