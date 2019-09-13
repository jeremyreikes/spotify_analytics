from pymongo import MongoClient
client = MongoClient(readPreference='secondary')
db = client.spotify_db
all_tracks = db.all_tracks
parsed_playlists = db.parsed_playlists
from pandas.io.json import json_normalize
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
from scipy.sparse import csr_matrix

import numpy as np
from kmodes.kmodes import KModes
from kmodes.util.dissim import matching_dissim, euclidean_dissim, ng_dissim

from kmodes.kprototypes import KPrototypes
import numpy as np

tqdm.pandas()
from sklearn.preprocessing import MultiLabelBinarizer
mlb = MultiLabelBinarizer()
def construct_model_data():
    datapoints = list(all_tracks.find({}, {'genres': 1}))
    df = json_normalize(datapoints)
    df.set_index('_id', inplace=True)
    return df

raw_df = construct_model_data()
df = raw_df.sample(139500)

df = df[df['genres'].map(lambda d: len(d)) > 0]
# df.head()

all_genres = set()

def add_genres(genres):
    if genres:
        if type(genres) == float:
            pass
        else:
            for genre in genres:
                all_genres.add(genre)
df.genres.apply(add_genres)

def count_genres(df):
    counts = Counter()
    df.genres.apply(lambda x: increment_genres(x, counts))
    return counts

def increment_genres(genres, counts):
    if genres:
        if type(genres) == float:
            pass
        else:
            for genre in genres:
                counts[genre] += 1



len(df)
genre_counts = count_genres(df)
top_20 = pd.DataFrame(genre_counts.most_common(20))
top_20.columns = ['genre', 'count']

top_20 = top_20.iloc[0]
top_20
import plotly_express as px
x = [cat[0] for cat in top_20]
y = [cat[1] for cat in top_20]

top_20
help(px.bar)
fig = px.bar(top_20, x='genre', y='count', title='Track genres per 100000 songs')

fig.show()
# rows = list()
# cols = list()
# data = list()
# genre_map = dict()
# for index, genre in enumerate(all_genres):
#     genre_map[genre] = index
#
# for index, genres in enumerate(df.genres):
#     if genres:
#         if type(genres) == float:
#             pass
#         else:
#             for genre in genres:
#                 genre_index = genre_map[genre]
#                 rows.append(index)
#                 cols.append(genre_index)
#                 data.append(1)
#
# mat
#
# mat = csr_matrix((data, (rows, cols)), shape=(len(df), len(all_genres)), dtype=bool)
# from sklearn.decomposition import TruncatedSVD
# svd = TruncatedSVD(n_components=50, n_iter=7, random_state=42)
# # svd.fit(mat)
# mat_df = pd.DataFrame(data=svd.transform(mat))
#
# # print(svd.explained_variance_ratio_)
# # print(svd.singular_values_)
# df = df.reset_index()
# df = df.drop('_id', axis=1)
# all_df = pd.concat([mat_df, df], ignore_index=True, axis=1)
# dense_mat = mat.todense()
# dense_mat.astype(int).dtype
#
# km = KModes(n_clusters=4, init='Cao', n_init=1, cat_dissim=ng_dissim)
#
# km.cluster_centroids_.shape
#
# clusters = km.fit_predict(dense_mat)
#
# # Print the cluster centroids
#
# from sklearn.cluster import AgglomerativeClustering, SpectralClustering
#
# ac = SpectralClustering(n_clusters=5).fit(dense_mat)
# ac.labels_
# pd.options.display.max_rows = 4000
# print(km.cluster_centroids_)
# from collections import Counter
# counts = Counter()
# for label in ac.labels_:
#     counts[label]+= 1
# counts
#
# print(km.labels_)
# # df.genres.progress_apply(get_genre_indices)
# km.labels_
#
#
# import mca
# mca_ben = mca.MCA(pd.DataFrame(dense_mat))
# mca_ben
# len(mca_ben.L)
# pd.DataFrame(mca_ben.L)
#


import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel



def get_genre_tuples(genres):
    tups = []
    if genres:
        if type(genres) == float:
            pass
        else:
            for genre in genres:
                genre_index = word2id[genre]
                tups.append((genre_index, 1))
    return tups

id2word = corpora.Dictionary(df.genres)
word2id = {v: k for k, v in id2word.items()}
corpus = [id2word.doc2bow(genres) for genres in df.genres]

lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=20,
                                           random_state=100,
                                           update_every=1,
                                           passes=5,
                                           alpha='auto',
                                           per_word_topics=True)


import pyLDAvis
import pyLDAvis.gensim  # don't skip this
import matplotlib.pyplot as plt
%matplotlib inline
pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim.prepare(lda_model, corpus, id2word)
vis
