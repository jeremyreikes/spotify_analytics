import pickle
import pandas as pd
import lyricsgenius
import numpy as np
import lyricsgenius
import re
from api_keys import genius_client_access_token

genius = lyricsgenius.Genius(genius_client_access_token)
genius.remove_section_headers = True
genius.verbose = False

def get_lyrics(track):
    try:
        tid = track['_id']
        track_name = track['name']
        artist_name = track['artist_name']
        song = genius.search_song(track_name, artist_name)
        if song:
            lyrics = song.lyrics
            if lyrics:
                lyrics = lyrics.replace('\n', '. ')
                regex = re.compile('([\][])')
                lyrics = re.sub(regex, '', lyrics)
                lyrics = lyrics.replace('. .', '.')
                return lyrics
        return None
    except:
        return None
