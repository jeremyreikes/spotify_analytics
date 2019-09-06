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
from get_tids import *

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
            all_tracks.update_one({'_id': tid}, {'$push': {'playlists': playlist_id}})
        else:
            new_track = initialize_track(tid, playlist_id)
            all_tracks.insert_one(new_track)

@timeout(10)
def add_playlist(playlist_id):
    if parsed_playlists.count_documents({'_id': playlist_id}, limit = 1) != 0:
        # print(f'{playlist_id} already parsed')
        return parsed_playlists.find_one({'_id': playlist_id})['tids']
    try:
        playlist = sp.user_playlist(playlist_id=playlist_id, user=None)
    except:
        return None
    user_id = playlist['owner']['id']
    total_tracks = playlist['tracks']['total']
    if total_tracks > 700 or total_tracks < 3:
        # print(f'Too many (or few!) songs.  Not adding {playlist_id} to database')
        return None
    all_tids = get_tids_from_playlist(playlist)
    additional_pages = total_tracks // 100
    if total_tracks % 100 == 0:
        additional_pages -= 1
    for i in range(additional_pages):
        try:
            playlist = sp.user_playlist_tracks(user_id, playlist_id=playlist_id, offset = (i+1)*100)
            curr_tids = get_tids_from_playlist_tracks(playlist)
            all_tids.extend(curr_tids)
        except:
            print('Pagination Error')
    insert_tracks(all_tids, playlist_id)
    name = playlist.get('name', '')
    description = playlist.get('description', '')
    lemmas = lemmatize_playlist(name)
    parsed_playlists.insert_one({'_id': playlist_id, 'tids': all_tids, 'description': description,
                             'name': name, 'lemmas': lemmas, 'user_id': user_id})
    return all_tids

# df = get_playlist_ids()
# start = 30000
# end = 50000
# data = df.iloc[start:end]
# data.playlist_ids.progress_apply(add_playlist)
