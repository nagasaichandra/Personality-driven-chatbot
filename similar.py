import pandas as pd
import nltk
import random
import sys
import os
import re
# from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle
nltk.download('punkt')
#print(os.getcwd())
data_frame = pd.read_csv('sample_data.csv')
tf_transformer = pickle.load(open('Model/tfidflyrics.pkl', 'rb'))
matrix = tf_transformer.transform(data_frame['lyrics'])

def similar_songs(lyric):
    tf_new = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), stop_words='english', lowercase=True, vocabulary = tf_transformer.vocabulary_)
    x_matrix = tf_new.fit_transform([lyric])
    cosine_similarities = linear_kernel(matrix, x_matrix).flatten()
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1]]
    list_2_similar_songs = [(index, cosine_similarities[index]) for index in related_docs_indices][0:2]
    output = list()
    for i in list_2_similar_songs:
        dict_m = {'song': data_frame.iloc[i[0]]['song'], 'lyrics': data_frame.iloc[i[0]]['lyrics'],
                  'artist': data_frame.iloc[i[0]]['artist'], 'genre': data_frame.iloc[i[0]]['genre']}
        output.append(dict_m)
    return output
nltk.download('stopwords')
stopwords = set(stopwords.words('english'))
# print(stopwords)
def remove_stopwords(text):
  new_string = str()
  for word in nltk.word_tokenize(text):
    if word.lower() not in stopwords:
      new_string = new_string + ' ' + word.lower()
  return new_string


def regex_match(text, similar_songs):
  return None


text = 'Are bob and sue items?'
text = remove_stopwords(text)
# print(text)
similar_songs = similar_songs(text)
# details = get_song_details(similar_songs)
# for i in similar_songs:
#   lyrics = i['lyrics']
#   sent_tokenizer = 
