import twint
import nest_asyncio
nest_asyncio.apply()
import pandas as pd
import pickle
from tqdm import tqdm
from collections import defaultdict, Counter
import time
import re
import requests

pd.set_option('display.max_colwidth', -1)

def get_playlist_id(row):
    regex = re.findall(r'\bplaylist\b\/\w*', row)
    if regex:
        return regex[0][9:]

def scrape_playlists(until=None):
    c = twint.Config()
    c.Pandas = True
    c.Pandas_clean = True
    c.Hide_output = True
    c.Limit = 10000
    c.Until = until
    c.Search = 'open.spotify.com/playlist/'
    twint.run.Search(c)
    df = twint.storage.panda.Tweets_df
    until = df.iloc[-1].date[:10]
    df['playlist'] = df.tweet.apply(get_playlist_id)
    df.playlist.to_csv(f'all_playlist_ids{until}.csv', mode='a+', header=False)
    scrape_playlists(until)

# scrape_playlists()