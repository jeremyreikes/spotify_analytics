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
import os

def combine_all_songs(all_songs, new_songs):
    for tid, values in new_songs.items():
        if tid not in all_songs.keys():
            all_songs[tid] = values
        else:
            all_songs[tid]['playlist_word_counts'] += new_songs[tid]['playlist_word_counts']
            all_songs[tid]['playlists'].extend(new_songs[tid]['playlists'])
    return all_songs

def combine_parsed_playlists(pp1, pp2):
    pp2.update(pp1)
    return pp1

def combine_unparsed_playlists(up1, up2):
    return up1.union(up2)

def combine_user_ids(uids1, uids2):
    return uids1.union(uids2)

def combine_everything():
    structures = [('all_songs_data', combine_all_songs), ('parsed_playlists_data', combine_parsed_playlists), ('unparsed_playlists_data', combine_unparsed_playlists), ('user_ids_data', combine_user_ids)]
    for path_end, f in structures:
        path = f'/Users/jeremy/Desktop/final_project/{path_end}'
        all_files = glob.glob(path + "/*.p")
        master_file = pickle.load(open(f'{path}/master.p', 'rb'))
        for filename in all_files:
            if filename != f'{path}/master.p':
                curr_file = pickle.load(open(f'{filename}', 'rb'))
                master_file = f(master_file, curr_file)
                os.remove(filename)
                print(filename, 'removed')
        pickle.dump(master_file, open(f'{path}/master.p', 'wb'))

# combine_everything()

f = pickle.load(open(f'all_songs_data/master.p', 'rb'))
f['0UbBJGDeQSiGhfdOWFa7WL']
keys = list(f.keys())
keys[:100]
