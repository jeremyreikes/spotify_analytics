import pymongo

from pymongo import MongoClient
client = MongoClient()
db = client.spotify_db
db
songs = db.songs
song_collection


for song in playlist:
    counts = Counter()
    for word in playlist['name']:
        counts[word] += 1
    songs.update({ query: { 'tid' : song.tid }, update : { '$inc' : counts}, new: true, upsert: true})
