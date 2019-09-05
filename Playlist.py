import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import warnings
import pickle
import tqdm
from collections import Counter, defaultdict
from spacy.lang.en import English
warnings.filterwarnings('ignore')
import time
from api_keys import spotify_client_id, spotify_client_secret
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
import database_querying as dbq
import pandas as pd
from textblob import TextBlob
import numpy as np
from get_tids import *
# from pymongo import MongoClient
# client = MongoClient(readPreference='secondary')
# db = client.spotify_db
# all_tracks = db.all_tracks
# parsed_playlists = db.parsed_playlists

class Playlist:
    def __init__(self, playlist_id):
        self.tids = self.fetch_playlist_tids(playlist_id)
        self.tracks = dbq.get_tracks(self.tids)
        self.data = self.convert_tracks_to_df(self.tracks)


    def fetch_playlist_tids(self, playlist_id):
        playlist = sp.user_playlist(playlist_id=playlist_id, user=None)
        total_tracks = playlist['tracks']['total']
        all_tids = get_tids_from_playlist(playlist)
        if total_tracks == 0 or not all_tids:
            print(f'Unable to parse {playlist_id}')
            return None
        additional_pages = total_tracks // 100
        if total_tracks % 100 == 0:
            additional_pages -= 1
        for i in range(additional_pages):
            playlist = sp.user_playlist_tracks(playlist_id=playlist_id, user=None, offset = (i+1)*100)
            tids = get_tids_from_playlist_tracks(playlist)
            all_tids.append(tids)
        return all_tids

    def rank_tracks_by_playlist_word_frequencies(self, word):
        for tid, track_counts in self.playlist_word_counts.items():
            self.data.loc[tid, 'playlist_word_frequency'] = track_counts.get(word, 0)
        return self.data.sort_values(by='playlist_word_frequency', ascending=False)


    def convert_tracks_to_df(self, tracks):
        counts = defaultdict(Counter)
        parsed_tracks = list()
        for track in tracks:
            curr_track = dict()
            for key, val in track.items():
                if key != 'audio_features':
                    curr_track[key] = val
            audio_features = track.get('audio_features', False)
            if audio_features:
                for key, val in audio_features.items():
                    curr_track[key] = val
            try:
                counts[track['_id']] = dbq.get_playlist_word_counts(track['_id'])
            except:
                counts[track['_id']] = 0
            parsed_tracks.append(curr_track)
        self.playlist_word_counts = counts
        return pd.DataFrame(parsed_tracks).set_index('_id')


playlist = Playlist('0tM6KltCDuAY4gY9SkzGa3')
playlist.data
playlist.rank_tracks_by_playlist_word_frequencies('sex')
playlist.data
