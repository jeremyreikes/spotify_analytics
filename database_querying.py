import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from tqdm import tqdm
tqdm.pandas()
from collections import Counter, defaultdict
import spacy
from timeout import timeout

from pymongo import MongoClient
client = MongoClient()
db = client.spotify_db
all_tracks = db.all_tracks
parsed_playlists = db.parsed_playlists

def get_track(tid):
    return all_tracks.find_one({'_id': tid})

def get_tracks(tids):
    tracks = []
    for tid in tids:
        track = get_track(tid)
        if track:
            tracks.append(track)
    return tracks

def get_top_n_tracks(num_tracks):
    top_counts = Counter()
    for track in all_tracks.find():
        top_counts[track['_id']] = len(track['playlists'])
    return [x[0] for x in top_counts.most_common(num_tracks)]

def get_playlist(pid):
    return parsed_playlists.find_one({'_id':  pid})

def get_artist_tracks(artist_name = None, artist_id = None):
    if artist_id:
        return all_tracks.find({'artist_id': artist_id})
    elif artist_name:
        return all_tracks.find({'artist_name': artist_name})
    else:
        return None

def get_playlist_word_counts(tid):
    word_counts = Counter()
    track = get_track(tid)
    playlist_ids = track['playlists']
    total_occurences = len(playlist_ids)
    for playlist_id in playlist_ids:
        playlist = get_playlist(playlist_id)
        lemmas = playlist['lemmas']
        for lemma in lemmas:
            word_counts[lemma] += 1
    for word in word_counts:
        word_counts[word] /= total_occurences
    return word_counts, track['name'], track['artist_name']
