import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle
nltk.download('punkt')
data_frame = pd.read_csv('sample_data.csv')
tf_transformer = pickle.load(open('Model/tfidflyrics.pkl', 'rb'))
matrix = tf_transformer.transform(data_frame['lyrics'])

def similar_songs(lyric):
    tf_new = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), stop_words='english', lowercase=True, vocabulary = tf_transformer.vocabulary_)
    x_matrix = tf_new.fit_transform([lyric])
    cosine_similarities = linear_kernel(matrix, x_matrix).flatten()
    related_doc_index = cosine_similarities.argmax()
    i = related_doc_index
    song = remove_swear(data_frame.iloc[i]['song'])
    lyric = remove_swear(data_frame.iloc[i]['lyrics'])
    dict_m = {'song': song, 'lyrics': lyric, 'artist': data_frame.iloc[i]['artist'], 'genre': data_frame.iloc[i]['genre'], 'year': data_frame.iloc[i]['year']}
    return dict_m

nltk.download('stopwords')

def remove_stopwords(text):
  sen_new = " ".join([i.lower() for i in nltk.word_tokenize(text) if i.lower() not in stopwords.words('english')])
  return sen_new



def remove_swear(text):
  swear_words = ['anal', 'anus', 'arse','ass','ballsack','balls','bastard','bitch','biatch','bloody','blowjob', 'blow job', 'bollock','bollok','boner','boob','bugger','bum','butt','buttplug','clitoris','cock','coon','crap','cunt','damn',
  'dick','dildo','dyke','fag','feck','fellate','fellatio','felching','fuck','f u c k','fudgepacker','fudge','packer','flange','Goddamn','God damn hell','homo',	'jerk',	'jizz',	'knobend','knob','end	labia',	'lmao','lmfao','muff','nigger','nigga','omg','penis','piss','poop','prick','pube','pussy','queer','scrotum','sex','shit','s hit','sh1t','slut','smegma','spunk','tit','tosser','turd','twat','vagina','wank','whore','wtf']

  # split_list = swear_words.split(sep='\t')
  for word in swear_words:
    # if word in text:
    text = text.replace(word, '*'*len(word))
  return text


def sing(song_details, text):
  """

  The way it works is 

  >>> (optional) user commands tweety to sing
  >>> tweety: "la la la la la"
  >>> user: "what is that song?"
  >>> tweety: "I'm singing {song_name} by {artist}"

  TODO: given question, lookup song_details & return... also sing?

  Args:
      text: the user's message 
      song_details: a dictionary of {
        "genre": "...", 
        "lyrics":"...",
        "artist":"...",
        "song_name": "...",
        "year": "...",
      }
  """
  for word in nltk.word_tokenize(text):  
    lines = song_details['lyrics'].split('\n')
    # print(lines)
    for i in range(len(lines)):
      if word in lines[i].lower():
        if i != 0:
          return lines[i-1] + ' -- ' + lines[i]
        else:
          return lines[i] + ' -- ' + lines[i+1]




def similar(text):
  text = remove_stopwords(text)
  similar_song = similar_songs(text)
  # similar_song = remove_swear(similar_song)
  similar_song['output'] =  sing(similar_song, text)
  return similar_song


print(similar('You are dangerous'))