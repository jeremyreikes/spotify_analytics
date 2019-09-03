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

useless_features = ['type', 'uri', 'track_href', 'analysis_url', 'id']

def get_track(tid):
    return all_tracks.find_one({'_id': tid})

def get_playlist(pid):
    return parsed_playlists.find_one({'_id', pid})

def add_audio_features():
    all_tids = []
    for track in all_tracks.find({'audio_features': {'$exists': False}}):
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
    for track in all_tracks.find({'name': {'$exists': False}, 'artist_id': {'$exists': False}}):
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

def add_genres():
    all_tids = []
    for track in all_tracks.find({'genres': {'$exists': False}, 'artist_id': {'$exists': True}}):
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

def tokenize_playlists():
    for playlist in parsed_playlists.find({'lemmas': {'$exists': False}}):
        pid = playlist['_id']
        doc = nlp(playlist['name'])
        lemmas = list()
        for token in doc:
            if token.is_stop or not token.is_alpha:
                continue
            lemma = token.lemma_.strip().lower()
            if lemma:
                lemmas.append(lemma)
        parsed_playlists.find_one_and_update({'_id': pid}, {'$set': {'lemmas': lemmas}})



    # do this shit
def add_lyrics():
    genius = lyricsgenius.Genius(genius_client_access_token)
    genius.remove_section_headers = True
    genius.verbose = False
    for index, track in enumerate(all_tracks.find({'lyrics': {'$exists' : False}})):
        if index == 50:
            break
        try:
            tid = track['_id']
            track_name = track['name']
            artist_name = track['artist_name']
            song = genius.search_song(track_name, artist_name)
            if song:
                lyrics = song.lyrics
                if lyrics:
                    all_tracks.find_and_modify({'_id': tid}, {'$set': {'lyrics': lyrics}})
        except:
            print(f'Could not add lyrics for {tid}')





# track = add_audio_features(['0Svkvt5I79wficMFgaqEQJ'])
# all_tracks.find_one(limit=20)
# parsed_playlists.count()
#
# print(db.command("collstats", "all_tracks"))
# add_audio_features()
# add_name_and_artist()

# def build_database():
add_audio_features()
add_name_and_artist()
add_genres()
add_lyrics()
tokenize_playlists()




all_tracks.find_one({'_id': '2Fxmhks0bxGSBdJ92vM42m'})







most
most_tid
'''
schedule-
 twitter_scrape to get playlist names
 Get_playlist_tracks in spotify_fetching to get tracks and playlists

  build_database
  add_name_and_artist AND ALSO add_audio_features IN ANY ORDER
  ONCE A SONG HAS ARTIST NAME, get_gneres()
  ONCE A SONG HAS TRACKNAME AND ARTIST NAME, get lyrics


'''
# build_database()
