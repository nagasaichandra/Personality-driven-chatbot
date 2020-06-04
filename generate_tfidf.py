import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

data_path = "sample_data.csv"
dataset = pd.read_csv(data_path, encoding="utf-8")
sample = dataset.sample(n=5000)
tfidf = TfidfVectorizer(
    analyzer="word", ngram_range=(1, 3), stop_words="english", lowercase=True
)
tf_transformer = tfidf.fit(sample["lyrics"])
# print(tf_transformer)
pickle.dump(tf_transformer, open("models/tfidflyrics.pkl", "wb"))
