def get_tids_from_playlist(playlist):
    tids = list()
    for track in playlist['tracks']['items']:
        try:
            tids.append(track['track']['id'])
        except:
            continue
    return tids


def get_tids_from_playlist_tracks(playlist):
    tids = list()
    for track in playlist['items']:
        try:
            tids.append(track['track']['id'])
        except:
            continue
    return tids
