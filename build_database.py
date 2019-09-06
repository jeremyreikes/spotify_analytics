import pandas as pd
import numpy as np
import warnings
import sys
from tqdm import tqdm
tqdm.pandas()
warnings.filterwarnings('ignore')
import spacy
nlp = spacy.load('en_core_web_sm')
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import lyricsgenius
import re
from api_keys import spotify_client_id, spotify_client_secret, genius_client_access_token
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
from pymongo import MongoClient
client = MongoClient()
db = client.spotify_db
all_tracks = db.all_tracks
parsed_playlists = db.parsed_playlists
from time import sleep
import re

useless_features = ['type', 'uri', 'track_href', 'analysis_url', 'id']

def update_audio_features(subset=None):
    if subset:
        cursor = all_tracks.find({'_id': {'$in': subset}, 'audio_features': {'$exists': False}})
    else:
        cursor = all_tracks.find({'audio_features': {'$exists': False}})
    all_tids = list()
    for track in cursor:
        all_tids.append(track['_id'])
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    for i in tqdm(range(0,(len(all_tids) // 50) + 1)):
        offset = i*50
        curr_ids = get_curr_ids(all_tids, offset)
        for _ in range(5):
            try:
                audio_features = sp.audio_features(curr_ids)
                continue
            except:
                sleep(2)
                audio_features = list()
        for index, curr_features in enumerate(audio_features):
            if not curr_features:
                try:
                    all_tracks.find_one_and_update({'_id': curr_ids[index]}, {'$set': {'audio_features': None}})
                except:
                    print('')
            else:
                for feature in useless_features:
                    del curr_features[feature]
                all_tracks.find_one_and_update({'_id': curr_ids[index]}, {'$set': {'audio_features': curr_features}})


def get_curr_ids(all_tids, offset):
    try:
        curr_ids = all_tids[offset:offset+50]
    except:
        curr_ids = all_tids[offset:]
    return curr_ids


def update_name_and_artist(subset=None):
    if subset:
        cursor = all_tracks.find({'_id': {'$in': subset}, 'name': {'$exists': False}, 'artist_id': {'$exists': False}})
    else:
        cursor = all_tracks.find({'name': {'$exists': False}, 'artist_id': {'$exists': False}})
    all_tids = list()
    for track in cursor:
        all_tids.append(track['_id'])
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    for i in tqdm(range(0,(len(all_tids) // 50) + 1)):
        offset = i*50
        curr_ids = get_curr_ids(all_tids, offset)
        for _ in range(5):
            try:
                raw_tracks = sp.tracks(curr_ids)['tracks']
                continue
            except:
                sleep(2)
                raw_tracks = list()
        for curr_track in raw_tracks:
            if not curr_track:
                continue
            tid = curr_track['id']
            name = curr_track['name']
            artist_id = curr_track['album']['artists'][0]['id']
            artist_name = curr_track['album']['artists'][0]['name']
            release_date = curr_track['album']['release_date']
            popularity = curr_track['popularity']
            all_tracks.find_one_and_update({'_id': tid}, {'$set': {'name': name, 'artist_name': artist_name, 'artist_id': artist_id, 'release_date': release_date, 'popularity': popularity}})


def update_genres(subset=None):
    if subset:
        cursor = all_tracks.find({'_id': {'$in': subset}, 'genres': {'$exists': False}, 'artist_id': {'$exists': True}})
    else:
        cursor =  all_tracks.find({'genres': {'$exists': False}, 'artist_id': {'$exists': True}})
    all_tids = list()
    for track in cursor:
        tid = track['_id']
        artist_id = track['artist_id']
        if artist_id:
            all_tids.append((tid, artist_id))
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    for i in tqdm(range(0,(len(all_tids) // 50) + 1)):
        offset = i*50
        curr_ids = get_curr_ids(all_tids, offset)
        tids = [curr_id[0] for curr_id in curr_ids]
        artist_ids = [curr_id[1] for curr_id in curr_ids]
        for _ in range(5):
            try:
                curr_artists = sp.artists(artist_ids)['artists']
                continue
            except:
                sleep(2)
                curr_artists = list()
        for index, curr_artist in enumerate(curr_artists):
            if not curr_artist:
                all_tracks.find_one_and_update({'_id': tids[index]}, {'$set': {'genres': None}})
            else:
                genres = curr_artist['genres']
                all_tracks.find_one_and_update({'_id': tids[index]}, {'$set': {'genres': genres}})

    # do this shit
def update_lyrics(subset = None):
    genius = lyricsgenius.Genius(genius_client_access_token)
    genius.remove_section_headers = True
    genius.verbose = False
    regex = re.compile('([\][])')
    if subset:
        cursor = all_tracks.find({'_id': {'$in': subset}, 'lyrics': {'$exists' : False}, 'name': {'$exists': True}, 'artist_name': {'$exists': True}})
    else:
        cursor = all_tracks.find({'lyrics': {'$exists' : False}, 'name': {'$exists': True}, 'artist_name': {'$exists': True}})
    for track in tqdm(cursor):
        tid = track['_id']
        track_name = track['name']
        artist_name = track['artist_name']
        try:
            song = genius.search_song(track_name, artist_name)
            lyrics = song.lyrics
            lyrics = lyrics.replace('\n', '. ')
            lyrics = re.sub(regex, '', lyrics)
            lyrics = lyrics.replace('. .', '.')
            all_tracks.find_one_and_update({'_id': tid}, {'$set': {'lyrics': lyrics}})
        except:
            all_tracks.find_one_and_update({'_id': tid}, {'$set': {'lyrics': None}})



# def build_database():

# update_lyrics()
# build_database()
# top_10000 = get_top_n_tids(10000)
# update_lyrics()
#
# def update_database():
# update_audio_features()
# update_name_and_artist()
# update_genres()
# update_lyrics()


'''
DEPENDENCIES:
update_audio_features - none
update_name_and_artist - none
update_genres - must do update_name_and_artist before
update_lyrics - must do update_name_and_artist before


'''
