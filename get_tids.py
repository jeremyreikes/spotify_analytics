def get_tids_from_playlist(playlist):
    return [track['track']['id'] for track in playlist['tracks']['items']]

def get_tids_from_playlist_tracks(playlist):
    return [track['track']['id'] for track in playlist['items']]
