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
    trackname = track.trackname
    artist = track.artist
    song = genius.search_song(trackname, artist)
    if song:
        lyrics = song.lyrics
        stripped = ' '.join(lyrics.split('\n'))
        regex = re.compile('([\][])')
        clean_lyrics = re.sub(regex, '', stripped)
        track['lyrics'] = clean_lyrics
    else:
        track['lyrics'] = None
    return track
