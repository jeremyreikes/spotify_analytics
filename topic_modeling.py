import gensim
from gensim.test.utils import common_texts
from gensim.corpora.dictionary import Dictionary
from gensim.utils import simple_preprocess
import re


def sent_to_words(sentences):
    for sent in sentences:
        sent = re.sub('\s+', ' ', sent)  # remove newline chars
        sent = re.sub("\'", "", sent)  # remove single quotes
        sent = simple_preprocess(str(sent), deacc=True)
        yield(sent)

def get_topics(sentences, num_topics = 5):
    common_dictionary = Dictionary(common_texts)
    common_corpus = [common_dictionary.doc2bow(text) for text in common_texts]
    lda = gensim.models.ldamodel.LdaModel(common_corpus, num_topics=num_topics)
    data_words = list(sent_to_words(sentences))
    curr_corpus = [common_dictionary.doc2bow(text) for text in data_words]
    lda.update(curr_corpus)
    vectors = []
    for doc in curr_corpus:
        vector = lda[doc]
        vectors.append(vector)
    top_topics = []
    for vector in vectors:
        top_topic = sorted(vector, key = lambda x: x[1], reverse=True)[0]
        top_topics.append(top_topic)
    # topic_numbers = [topic[0] if (abs(topic[1] - (1/num_topics)) >= .01) else -1 for topic in top_topics]
    topic_numbers = [topic[0] for topic in top_topics]
    return topic_numbers
