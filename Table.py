import pandas as pd
import numpy as np
import spacy
import database_querying as dbq
import pickle
audio_features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']
# playlist = pickle.load(open('sample.p', 'rb'))

class Table:
    def __init__(self, playlist):
        self.data = self.prepare_data(playlist.data.copy())
        self.playlist_descriptions = playlist.playlist_descriptions
        self.playlist_word_frequencies = playlist.playlist_word_frequencies
        self.nlp = spacy.load('en_core_web_sm')

    def prepare_data(self, data):
        data['mode'] = data['mode'].apply(self.convert_mode)
        data['duration'] = data['duration_ms'].apply(self.convertTime)
        data.drop('duration_ms', axis=1, inplace=True)
        for feature in audio_features:
            data[feature] = data[feature].apply(lambda x: round(x, 2))
        data['tempo'] = data['tempo'].apply(lambda x: round(x))
        return data

    def convertTime(self, millis):
        seconds = (millis/1000) % 60
        seconds = round(seconds)
        minutes = millis / (1000*60)
        minutes = round(minutes)
        if seconds // 10 == 0:
            seconds = '0' + str(seconds)
        return str(minutes) + ':' + str(seconds)

    def convert_mode(self, mode):
        if mode == 1:
            return 'Major'
        elif mode == 0:
            return 'Minor'
        else:
            return 'Unknown'

    def score_playlist_word_frequencies(self, target_words):
        words_doc = self.nlp(target_words)
        frequencies = dict()
        for tid, track_counts in self.playlist_word_frequencies.items():
            freqs = []
            for token in words_doc:
                if token.is_stop or not token.is_alpha:
                    continue
                lemma =  token.lemma_.strip().lower()
                freqs.append(track_counts.get(lemma, 0))
            avg_freq = np.mean(freqs)
            frequencies[tid] = avg_freq
        return frequencies, target_words

    def score_description_similarity(self, target_description):
        all_similarities = dict()
        target_description_doc = self.nlp(target_description)
        for tid, descriptions in self.playlist_descriptions.items():
            similarities = list()
            for description in descriptions:
                doc = self.nlp(description)
                similarity = doc.similarity(target_description_doc)
                similarities.append(similarity)
            all_similarities[tid] =  np.mean(similarities)
        return all_similarities, target_description

    def score_lyric_similarity(self, target_lyrics):
        target_lyrics_doc = self.nlp(target_lyrics)
        lyrical_similarities = dict()
        for tid, curr_lyrics in self.data.lyrics.iteritems():
            try:
                curr_similarity = self.nlp(curr_lyrics).similarity(target_lyrics_doc)
                lyrical_similarities[tid] = curr_similarity
            except:
                lyrical_similarities[tid] = None
        return lyrical_similarities, target_lyrics




# import pickle
# table = Table(playlist)
# pickle.dump(table, open('test_table.p', 'wb'))
# t = pickle.load(open('test_table.p', 'rb'))
#
# table.data
# table.score_playlist_word_frequencies('playlist')
#
#
# # love_frequencies = playlist.score_playlist_word_frequencies('love')
# data = playlist.data.copy()
#
#     # data = data[['name', 'artist_name', 'duration', 'popularity', 'genres', 'mode', 'lyrics', 'tempo', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'danceability']]
#     # display_data = data[['name', 'artist_name', 'duration', 'genres']]
#
# def display_basics(data):
#     return data[['name', 'artist_name', 'duration', 'genres', 'popularity']]
#
# display_basics(data)
# for row in data.lyrics.iteritems():
