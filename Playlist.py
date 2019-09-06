import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import warnings
import pickle
import tqdm
from collections import Counter, defaultdict
import spacy
nlp = spacy.load('en_core_web_lg')
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

class Playlist:
    def __init__(self, playlist_id):
        self.tids = self.fetch_playlist_tids(playlist_id)
        self.tracks = dbq.get_tracks(self.tids)
        self.data = self.convert_tracks_to_df(self.tracks)
        # also has playlist_word_counts, which is a dict with
        # TID: {WORD1: freq, WORD2: freq, ...}



    def 
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

    def rank_by_playlist_word_frequencies(self, words):
        doc = nlp(words)
        for tid, track_counts in self.playlist_word_counts.items():
            freqs = []
            for token in doc:
                if token.is_stop or not token.is_alpha:
                    continue
                lemma =  token.lemma_.strip().lower()
                freqs.append(track_counts.get(lemma, 0))
            avg_freq = np.mean(freqs)
            self.data.loc[tid, 'playlist_word_frequency'] = avg_freq
        return self.data.sort_values(by='playlist_word_frequency', ascending=False)

    def get_track_descriptions(self, track):
        descriptions = []
        for pid in track['playlists']:
            description = dbq.get_playlist_description(pid)
            if description:
                descriptions.append(description)
        return descriptions

    def get_description_similarity(self, descriptions, target):
        similarities = list()
        for description in descriptions:
            doc = nlp(description)
            similarity = doc.similarity(target)
            similarities.append(similarity)
        return np.mean(similarities)

    def rank_by_description_similarity(self, description):
        target = nlp(description)
        self.data['description_similarity'] = self.data.descriptions.apply(lambda x: self.get_description_similarity(x, target))
        return self.data.sort_values(by='description_similarity', ascending=False)

    def rank_by_lyric_similarity(self, lyrics):
        target = nlp(lyrics)
        self.data['lyrical_similarity'] = self.data.lyrics.apply(lambda x: nlp(x).similarity(target))
        return self.data.sort_values(by='lyrical_similarity', ascending=False)

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
            descriptions = self.get_track_descriptions(track)
            curr_track['descriptions'] = descriptions
            try:
                counts[track['_id']] = dbq.get_playlist_word_counts(track['_id'])
            except:
                counts[track['_id']] = 0
            parsed_tracks.append(curr_track)

        self.playlist_word_counts = counts
        return pd.DataFrame(parsed_tracks).set_index('_id')

    def get_tweet_sentiment(self, track):
        analyser = SentimentIntensityAnalyzer()
        pass

playlist = Playlist('5d4FPOzRUnPgoq1TKigtKm')
# playlist.data
playlist.rank_by_playlist_word_frequencies('summer is here')
playlist.rank_by_description_similarity('best music')
playlist.rank_by_lyric_similarity('i am the most fire rapper in th entire world')
# playlist.data
'''
syonym matching
cosine similarity
analyze lyrics -- sentiment matching.  if search term matches onf of sentiment, 0
also analyze playlist_word_Counts as a form of sentiment, also do descriptions
'''
