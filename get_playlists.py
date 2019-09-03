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
import spacy
import glob
from timeout import timeout

from pymongo import MongoClient
client = MongoClient()
db = client.spotify_db
all_tracks = db.all_tracks
parsed_playlists = db.parsed_playlists


client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

path = '/Users/jeremy/Desktop/final_project/data' # use your path
all_files = glob.glob(path + "/*.csv")

def initialize_track(tid):
    empty_dict = dict(_id=tid, playlists = list())
    return empty_dict

@timeout()
def get_playlist_tracks(playlist_id):
    try:
        if parsed_playlists.count_documents({'_id': playlist_id}, limit = 1) != 0:
            print(f'{playlist_id} already parsed')
            return None
        all_tids = list()
        playlist = sp.user_playlist(playlist_id = playlist_id, user = None)
        if not playlist:
            return None
        user_id = playlist['owner']['id']
        parsed_playlists.insert({'_id': playlist_id, 'description': playlist['description'], 'name': playlist['name'], 'user_id': user_id})
        tids = [track['track']['id'] for track in playlist['tracks']['items']]
        all_tids.extend(tids)
        i = 1
        while len(tids) == 100:
            if i == 5: # if more than 500 songs in a playlist, disregard
                break
            if user_id:
                playlist = sp.user_playlist_tracks(user_id, playlist_id=playlist_id, offset = i*100)
                tids = [track['track']['id'] for track in playlist['items']]
                all_tids.extend(tids)
                i += 1
        for tid in set(all_tids):
            if not tid:
                continue
            if all_tracks.count_documents({'_id': tid}, limit = 1) != 0:
                all_tracks.update({'_id': tid}, {'$push': {'playlists': playlist_id}})
            else:
                new_track = initialize_track(tid)
                new_track['playlists'].append(playlist_id)
                all_tracks.insert(new_track)
    except:
        print(f'{playlist_id} encountered an error!')


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


df = get_playlist_ids()
df.head()
start = 40000
end = 50000
data = df.iloc[start:end]
data.playlist_ids.progress_apply(get_playlist_tracks)
