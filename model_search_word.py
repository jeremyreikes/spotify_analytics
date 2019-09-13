
class Model:
    def __init__(self, word, tids = None):
        self.word = word
        self.word_playlist_frequencies, self.all_playlist_frequencies= dbq.get_frequencies_for_word(word)
        self.all_scores = self.calc_scores()
        # if tids:
            # self.playlist_scores = self.get_playlist_scores(tids)

    def calc_scores(self):
        scores = dict()
        for tid, val in self.all_playlist_frequencies.items():
            product = self.word_playlist_frequencies[tid] * val
            # data is not normally distributed - log-transform the product to normalize
            # maybe log normalize product?
            scores[tid] = product
        return sorted(scores.items(), key=lambda x: x[1])

    def get_playlist_scores(self, tids):
        playlist_scores = dict()
        for tid in tids:
            score = self.all_scores.get(tid, 0)
            playlist_scores[tid] = score
        return sorted(playlist_scores.items(), key=lambda x: x[1])

    def construct_model_data(self):
        datapoints = list(all_tracks.find({}, {'audio_features': 1, 'popularity': 1, 'release_date': 1, 'genres': 1}))
        df = json_normalize(datapoints)
        df.set_index('_id', inplace=True)
        return df



    # def show_top_n(self,  n):

# total_occurences = dbq.get_total_track_occurences() # replace this with a COUNT field in all_tracks
# df = model.construct_model_data()
# new_df = df.drop('audio_features', axis=1)
# new_df = new_df.drop('release_date', axis=1)
# new_df = new_df.drop('genres', axis=1)











# playlist = Playlist('37i9dQZEVXbMDoHDwVN2tF', get_lyrics = False)
model = Model('revolution')

















# my_tids = playlist.tids
for id, target in model.all_scores:
    new_df.loc[id, 'target'] = target
new_df = new_df.fillna(0)
hurdle = Hurdle()
hurdle.fit(new_df.drop('target', axis=1), new_df['target'])
preds = hurdle.predict_expected_value(new_df.drop('target', axis=1))
new_df['preds'] = preds
track_significance = dict()
for key, val in model.all_playlist_frequencies.items():
    product = model.word_playlist_frequencies[key] * val
    track_name = all_tracks.find_one({'_id': key}, {'name': 1, 'artist_name': 1})
    track_significance[track_name['name'] + ' - ' + track_name['artist_name']] = product
track_significance = Counter(track_significance)
my_top_tracks = Counter()
for tid in my_tids:
    try:
        track_name = all_tracks.find_one({'_id': tid}, {'name': 1, 'artist_name': 1})
        my_top_tracks[track_name['name'] + ' - ' + track_name['artist_name']] = model.all_playlist_frequencies[tid]
    except:
        # print(f'cant get track {tid}')
        pass





























# my_top_tracks.most_common(20)




track_significance.most_common(100)
