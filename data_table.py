import pandas as pd
from Playlist import playlist

def convertTime(millis):
    seconds=(millis/1000)%60
    seconds = round(seconds)
    minutes=millis/(1000*60)
    minutes = round(minutes)
    if seconds // 10 == 0:
        seconds = '0' + str(seconds)
    return str(minutes) + ':' + str(seconds)

audio_features = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence']

def convert_mode(mode):
    if mode == 1:
        return 'Major'
    elif mode == 0:
        return 'Minor'
    else:
        return 'Unknown'

# love_frequencies = playlist.score_playlist_word_frequencies('love')
data = playlist.data.copy()

def prepare_data(data):
    data['duration'] = data['duration_ms'].apply(convertTime)
    data['mode'] = data['mode'].apply(convert_mode)
    for feature in audio_features:
        data[feature] = data[feature].apply(lambda x: round(x, 2))
    data['tempo'] = data['tempo'].apply(lambda x: round(x))
    data.drop('duration_ms', axis=1, inplace=True)
    return data
    # data = data[['name', 'artist_name', 'duration', 'popularity', 'genres', 'mode', 'lyrics', 'tempo', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'danceability']]
    # display_data = data[['name', 'artist_name', 'duration', 'genres']]

data = prepare_data(data)

def display_basics(data):
    return data[['name', 'artist_name', 'duration', 'genres', 'popularity']]

display_basics(data)
