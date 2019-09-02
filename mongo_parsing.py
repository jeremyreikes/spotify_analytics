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

from api_keys import spotify_client_id, spotify_client_secret
client_id = spotify_client_id
client_secret = spotify_client_secret
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)

from pymongo import MongoClient
client = MongoClient()
db = client.spotify_db
all_tracks = db.all_tracks
parsed_playlists = db.parsed_playlists

useless_features = ['type', 'uri', 'track_href', 'analysis_url', 'id']


def get_track(tid):
    return all_tracks.find_one({'tid': tid})

''' parsed_playlists
{'_id': ObjectId('5d6aa573adfc1383ef50f1fa'),
 'pid': '6yd4iCpwXDECokvtTe0pCV',
 'description': 'Everything you need from an electronic music playlist. This playlist rotates 5 tracks, once per week.',
 'name': 'Electrovariety',
 'user_id': 'z6hfytr7q1i9ezs8l0uuj79h1'}
'''
def analyze_tweets(track):
    tweets = track['tweets']

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
        raw_tracks = sp.tracks(curr_ids)['tracks']
        for curr_track in raw_tracks:
            if not curr_track:
                continue
            tid = curr_track['id']
            name = curr_track['name']
            artist_id = curr_track['album']['artists'][0]['id']
            release_date = curr_track['album']['release_date']
            popularity = curr_track['popularity']
            all_tracks.find_and_modify({'_id': tid}, {'$set': {'name': name, 'artist_id': artist_id, 'release_date': release_date, 'popularity': popularity}})
# 
# def add_genres():
#     all_tids = []
#     for track in all_tracks.find():
#         all_tids.append(track['_id'])
#     sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
#     for i in tqdm(range(0,(len(all_tids) // 50) + 1)):
#         offset = i*50
#         try:
#             curr_ids = all_tids[offset:offset+50]
#         except:
#             curr_ids = all_tids[offset:]
#         raw_tracks = sp.tracks(curr_ids)['tracks']
#         for curr_track in raw_tracks:
#             if not curr_track:
#                 continue
#             tid = curr_track['id']
#             name = curr_track['name']
#             artist_id = curr_track['album']['artists'][0]['id']
#             release_date = curr_track['album']['release_date']
#             popularity = curr_track['popularity']
#             all_tracks.find_and_modify({'_id': tid}, {'$set': {'name': name, 'artist_id': artist_id, 'release_date': release_date, 'popularity': popularity}})
    # do this shit

# track = add_audio_features(['0Svkvt5I79wficMFgaqEQJ'])
# all_tracks.find_one(limit=20)
# parsed_playlists.count()
#
# print(db.command("collstats", "all_tracks"))
add_audio_features()
add_name_and_artist()
all_tracks.find_one()

def build_database():
    add_audio_features()
    add_name_and_artist()
    add_genres()
