import pandas as pd
import numpy as np
import warnings
from tqdm import tqdm
from collections import Counter
tqdm.pandas()

from collections import Counter, defaultdict
warnings.filterwarnings('ignore')

from pymongo import MongoClient
client = MongoClient()
db = client.spotify_db
all_tracks = db.all_tracks
parsed_playlists = db.parsed_playlists


def get_playlist_word_counts(tid):
    word_counts = Counter()
    track = all_tracks.find_one({'_id': tid})
    playlists = track['playlists']
    # get description and playlist name
    for playlist in parsed_playlists.find({'_id': {'$in': playlists}}):
        lemmas = playlist['lemmas']
        for lemma in lemmas:
            word_counts[lemma] += 1
    return word_counts

counts = get_playlist_word_counts('2Fxmhks0bxGSBdJ92vM42m')
