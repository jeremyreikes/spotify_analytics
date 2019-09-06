import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import pickle
import sys
from tqdm import tqdm
tqdm.pandas()
from collections import Counter, defaultdict
from api_keys import spotify_client_id, spotify_client_secret
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import glob
from timeout import timeout
from pymongo import MongoClient
client = MongoClient()
db = client.spotify_db
all_tracks = db.all_tracks
parsed_playlists = db.parsed_playlists

import spacy
nlp = spacy.load('en_core_web_sm')
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

path = '/Users/jeremy/Desktop/final_project/data' # use your path
all_files = glob.glob(path + "/*.csv")

def get_playlist_ids():
    dfs = []
    for filename in all_files:
        df = pd.read_csv(filename)
        df.drop('0', inplace=True, axis=1)
        df.drop_duplicates(inplace=True)
        df.columns = ['playlist_ids']
        dfs.append(df)
    df = pd.concat(dfs)
    df.drop_duplicates(inplace=True)
    return df

def initialize_track(tid, playlist_id):
    empty_dict = dict(_id=tid, playlists = list([playlist_id]))
    return empty_dict

def lemmatize_playlist(name):
    doc = nlp(name)
    lemmas = list()
    for token in doc:
        if token.is_stop or not token.is_alpha:
            continue
        lemma = token.lemma_.strip().lower()
        if lemma:
            lemmas.append(lemma)
    return lemmas

def insert_tracks(tids, playlist_id):
    for tid in set(tids):
        if not tid:
            continue
        if all_tracks.count_documents({'_id': tid}, limit = 1) != 0:
            all_tracks.update({'_id': tid}, {'$push': {'playlists': playlist_id}})
        else:
            new_track = initialize_track(tid, playlist_id)
            all_tracks.insert(new_track)

@timeout(10)
def add_playlist(playlist_id):
    if parsed_playlists.count_documents({'_id': playlist_id}, limit = 1) != 0:
        print(f'{playlist_id} already parsed')
        return None
    all_tids = list()
    playlist = sp.user_playlist(playlist_id=playlist_id, user=None)
    if not playlist:
        return None
    user_id = playlist['owner']['id']
    total_tracks = playlist['tracks']['total']
    if total_tracks > 700 or total_tracks == 0:
        print(f'Playlist is too long or empty, length - {total_tracks}')
        return None
    tids = [track['track']['id'] for track in playlist['tracks']['items']]
    all_tids.extend(tids)
    additional_pages = total_tracks // 100
    if total_tracks % 100 == 0:
        additional_pages -= 1
    for i in range(additional_pages):
        playlist = sp.user_playlist_tracks(playlist_id=playlist_id, user=None, offset = (i+1)*100)
        tids = [track['track']['id'] for track in playlist['items']]
        all_tids.extend(tids)
    insert_tracks(all_tids, playlist_id)
    name = playlist.get('name', '')
    description = playlist.get('description', '')
    lemmas = lemmatize_playlist(name)
    parsed_playlists.insert({'_id': playlist_id, 'tids': all_tids, 'description': description,
                             'name': name, 'lemmas': lemmas, 'user_id': user_id})

df = get_playlist_ids()
start = 0
end = 1000
data = df.iloc[start:end]
all_tracks.drop()
parsed_playlists.drop()
data.playlist_ids.progress_apply(add_playlist)
