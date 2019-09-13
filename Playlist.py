import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import warnings
import pickle
import tqdm
from collections import Counter, defaultdict
import spacy
nlp = spacy.load('en_core_web_sm')
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
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from parse_playlists import add_playlist
from build_database import update_genres, update_lyrics, update_audio_features, update_name_and_artist
class Playlist:
    def __init__(self, playlist_id, get_lyrics=True):
        self.tids = add_playlist(playlist_id, user=True)
        update_name_and_artist(self.tids)
        update_audio_features(self.tids)
        update_genres(self.tids)
        if get_lyrics:
            update_lyrics(self.tids)
        self.tracks = dbq.get_tracks(self.tids)
        self.data = self.convert_tracks_to_df(self.tracks)
        # also has playlist_word_counts, which is a dict with
        # TID: {WORD1: freq, WORD2: freq, ...}

    def fetch_playlist_tids(self, playlist_id):
        playlist = sp.user_playlist(playlist_id=playlist_id, user=None)
        total_tracks = playlist['tracks']['total']
        all_tids = get_tids_from_playlist(playlist)
        if total_tracks == 0 or not all_tids:
            return None
        additional_pages = total_tracks // 100
        if total_tracks % 100 == 0:
            additional_pages -= 1
        for i in range(additional_pages):
            playlist = sp.user_playlist_tracks(playlist_id=playlist_id, user=None, offset = (i+1)*100)
            tids = get_tids_from_playlist_tracks(playlist)
            all_tids.append(tids)
        return all_tids

    def get_track_descriptions(self, track):
        descriptions = []
        for pid in track['playlists']:
            description = dbq.get_playlist_description(pid)
            if description:
                descriptions.append(description)
        return descriptions

    def convert_tracks_to_df(self, tracks):
        counts = defaultdict(Counter)
        descriptions = dict()
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
            curr_descriptions = self.get_track_descriptions(track)
            descriptions[track['_id']] = curr_descriptions
            try:
                counts[track['_id']] = dbq.get_playlist_word_frequencies(track['_id'])
            except:
                counts[track['_id']] = 0
            parsed_tracks.append(curr_track)

        self.playlist_word_frequencies = counts
        self.playlist_descriptions = descriptions
        df = pd.DataFrame(parsed_tracks).set_index('_id')
        # add song to the database, but don't include in recommendations
        # df = df[df.playlists.count != 1]
        return df


# playlist = Playlist('0BYYlB7IgauqGfa34Zy7Pv', get_lyrics=False)
# parsed_playlists.find_one()
# ASK IF YOU WANT T
# playlist.score_playlist_word_frequencies('sleep')
 # playlist.rank_by_description_similarity('I am sad i want to die')
# playlist.rank_by_lyric_similarity('bad guy')
#
#
# playlist.data.iloc[0].playlists

# playlist.data.lyrics
'''
it's adding a playlist to a songs playlists field, but that playlist is not being entered into parsed playlits
syonym matching
cosine similarity
analyze lyrics -- sentiment matching.  if search term matches onf of sentiment, 0
also analyze playlist_word_Counts as a form of sentiment, also do descriptions
'''
