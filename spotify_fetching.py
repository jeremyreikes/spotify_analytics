import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import warnings
import pickle
import sys
from tqdm import tqdm
tqdm.pandas()
from collections import Counter, defaultdict
from spacy.lang.en import English
warnings.filterwarnings('ignore')
from api_keys import spotify_client_id, spotify_client_secret
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spacy
import glob
from timeout import timeout

nlp = spacy.load("en_core_web_sm")
client_id = spotify_client_id
client_secret = spotify_client_secret
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

path = '/Users/jeremy/Desktop/final_project/data' # use your path
all_files = glob.glob(path + "/*.csv")


def initialize_empty_dict():
    playlist_word_counts = Counter()
    playlist_descriptions = list()
    total_occurences = 0
    empty_dict = dict(playlist_word_counts = Counter(), playlist_occurences = list(), tweets = list())
    return empty_dict

@timeout(5)
def get_playlist_tracks(playlist_id):
    try:
        if playlist_id in parsed_playlists.keys():
            print(f'{playlist_id} already parsed')
            return None
        all_tids = list()
        playlist = sp.user_playlist(playlist_id = playlist_id, user = None)
        if not playlist:
            return None
        doc = nlp(playlist['name'])
        parsed_playlists[playlist_id] = playlist['description']
        tokens = [token.lemma_.lower() for token in doc if token.is_alpha]
        user_id = playlist['owner']['id']
        user_ids.add(user_id)
        tids = [track['track']['id'] for track in playlist['tracks']['items']]
        all_tids.extend(tids)
        i = 1
        while len(tids) == 100:
            if i == 5: #
                break
            if user_id:
                playlist = sp.user_playlist_tracks(user_id, playlist_id=playlist_id, offset = i*100)
                tids = [track['track']['id'] for track in playlist['items']]
                all_tids.extend(tids)
                i += 1
        for tid in set(all_tids):
            curr_track = all_songs.get(tid, False)
            if not curr_track:
                empty_dict = initialize_empty_dict()
                all_songs[tid] = empty_dict
                curr_track = all_songs[tid]
            curr_track['playlist_occurences'].append(playlist_id)
            counts = Counter()
            for token in tokens:
                counts[token] += 1
            curr_track['playlist_word_counts'] += counts
    except:
        unparsed_playlists.add(playlist_id)


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
test = df.iloc[5000:10000]

parsed_playlists = dict()
all_songs = defaultdict()
user_ids = set()
unparsed_playlists = set()

# test.playlist_ids.progress_apply(get_playlist_tracks)
list(all_songs.keys())

print(sys.getsizeof(all_songs))
all_songs['4fixebDZAVToLbUCuEloa2']

from pymongo import MongoClient
client = MongoClient()
db = client.spotify_db
tracks = db.tracks
# workflow
# three different collections
# ------ tracks, playlists
# playlists - {PID:  DESCRIPTION: str}}
# tracks - {TID: {NAME: str, }}
# playlist_words - {WORD: {TID: count}}
'''
When analyzing a library - do the following for all songs.
- parse tweets for sentiment, topics
-


tracks - {TID:
            {NAME: str, AUDIO FEATURES: dict, RELEASE DATE: datetime, TWEETS: list, PLAYLIST OCCURENCES: list, PLAYLIST WORD_COUNTS: dict}}
1 - check if TID is in
'''
