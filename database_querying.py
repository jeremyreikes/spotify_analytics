import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from tqdm import tqdm
tqdm.pandas()
from collections import Counter, defaultdict
from timeout import timeout

from pymongo import MongoClient
client = MongoClient(readPreference='secondary')
db = client.spotify_db
all_tracks = db.all_tracks
parsed_playlists = db.parsed_playlists

''' TRACK METHODS '''

def get_track(tid):
    return all_tracks.find_one({'_id': tid})

def get_track_playlists(tid):
    track = get_track(tid)
    return track['playlists']

def get_audio_features(tid):
    track = get_track(tid)
    return track['audio_features']

def get_genres(tid):
    track = get_track(tid)
    return track['genres']

def get_tweets(tid):
    track = get_track(tid)
    return track['tweets']

def get_tracks(tids):
    tracks = []
    for tid in tids:
        track = get_track(tid)
        if track:
            tracks.append(track)
    return tracks

def get_playlist_word_frequencies(tid, target_word=None):
    word_counts = Counter()
    playlist_ids = get_track_playlists(tid)
    total_occurences = len(playlist_ids)
    for playlist_id in playlist_ids:
        lemmas = get_playlist_lemmas(playlist_id)
        for lemma in lemmas:
            word_counts[lemma] += 1
    for word in word_counts:
        word_counts[word] /= total_occurences
    if target_word:
        return word_counts.get(target_word, 0)
    return word_counts

def get_frequencies_for_word(word, tid_subset=None):
    all_tids = list()
    playlist_occurences = Counter()
    playlists = parsed_playlists.find({'lemmas': word})
    for playlist in playlists:
        tids = playlist['tids']
        for tid in tids:
            playlist_occurences[tid] += 1
        all_tids.extend(tids)
    if tid_subset:
        all_tids = set(all_tids).intersection(set(tid_subset))
    else:
        all_tids = list(set(all_tids))
    for track in all_tracks.find({'_id': {'$in': all_tids}}, {'_id': 1, 'playlists': 1}):
        length = len(track['playlists'])
        if tid_subset or length >= 10: # arbitrary length to filter out rare songs that may have high frequencies
            playlist_occurences[track['_id']] /= length
        else:
            del playlist_occurences[track['_id']]
    if playlist_occurences.get(None, False):
        del playlist_occurences[None]
    return playlist_occurences

def get_top_n_tids(num_tracks):
    top_counts = Counter()
    for track in all_tracks.find():
        top_counts[track['_id']] = len(track['playlists'])
    return [x[0] for x in top_counts.most_common(num_tracks)]

# def get_artist_tracks(artist_name = None, artist_id = None):
#     if artist_id:
#         return all_tracks.find({'artist_id': artist_id})
#     elif artist_name:
#         return all_tracks.find({'artist_name': artist_name})
#     else:
#         return None

def get_track_from_name(name):
    return all_tracks.find_one({'name': name})

'''  PLAYLIST METHODS '''

def get_playlist(pid):
    return parsed_playlists.find_one({'_id': pid})

def get_playlist_lemmas(pid):
    playlist = get_playlist(pid)
    try:
        return playlist['lemmas']
    except:
        return list()

def get_playlist_description(pid):
    playlist = get_playlist(pid)
    try:
        return playlist['description']
    except:
        return ''

def get_playlist_name(pid):
    playlist = get_playlist(pid)
    try:
        return playlist['name']
    except:
        return ''

def get_playlist_user_id(pid):
    playlist = get_playlist(pid)
    try:
        return playlist['user_id']
    except:
        return ''

def get_playlist_tids(pid):
    playlist = get_playlist(pid)
    try:
        return playlist['tids']
    except:
        return list()

def get_playlist_tracks(pid):
    tids = get_playlist_tids(pid)
    return all_tracks.find({'_id': {'$in': tids}})

freqs = get_frequencies_for_word('sex')
freqs
