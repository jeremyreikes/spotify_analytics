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
from database_querying import get_playlist_word_counts, get_top_n_tracks, get_tracks
import pandas as pd
from textblob import TextBlob
import numpy as np

my_playlist = '37i9dQZEVXbLRQDuF5jeBp'

def fetch_tids(playlist_id):
    all_tids = list()
    playlist = sp.user_playlist(playlist_id = playlist_id, user = None)
    if not playlist:
        return None
    user_id = playlist['owner']['id']
    tids = [track['track']['id'] for track in playlist['tracks']['items']]
    all_tids.extend(tids)
    i = 1
    while len(tids) == 100:
        if user_id:
            playlist = sp.user_playlist_tracks(user_id, playlist_id=playlist_id, offset = i*100)
            tids = [track['track']['id'] for track in playlist['items']]
            all_tids.extend(tids)
    return set(all_tids)

def generate_word_counts(playlist_id = None, tids=None):
    if playlist_id:
        tids = fetch_tids(playlist_id)
    all_counts = defaultdict(Counter)
    for tid in tids:
        try:
            counts = get_playlist_word_counts(tid)
            all_counts[tid] = counts
        except:
            print(f'{tid}   ----   not parsed yet.  Relax, dawg.')
    return all_counts


def rank_songs_by_word(word, all_counts):
    song_rankings = defaultdict(Counter)
    for key, counts in all_counts.items():
        song_rankings[tid] = counts[word]
    song_rankings += Counter()
    return song_rankings.most_common()

top_500 = get_top_n_tracks(500)
top_500_data = get_tracks(top_500)
top_500_data[0]['lyrics']
# x = spotify(popularity)
# y = actual popularity


rows = list()
for track in top_500_data:
    try:
        lyrical_sentiment = np.mean(TextBlob(track['lyrics']).sentiment)
    except:
        lyrical_sentiment = 0
    track_data = dict(
        title = track['name'] + ' | ' + track['artist_name'],
        spotify_popularity = track['popularity'],
        audio_sentiment = track['audio_features']['valence'],
        lyrical_sentiment = lyrical_sentiment
    )
    rows.append(track_data)

import pandas as pd
df = pd.DataFrame(rows)
import plotly.express as px
fig = px.scatter(df, x="lyrical_sentiment", y="audio_sentiment", hover_name='title', color='spotify_popularity')
fig = plot_playlist(my_playlist, 'lyrical_sentiment', 'audio_sentiment', 'popularity')
fig.show()




df
all_counts, tid_map = generate_word_counts(tids = top_500)


rank_songs_by_word('workout', all_counts)
