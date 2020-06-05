FROM python:3.8

WORKDIR /ircbot

COPY requirements.txt ./

# install all the things
RUN pip install --no-cache-dir -r requirements.txt

# download all the things
RUN python -m nltk.downloader \
    wordnet \
    stopwords \
    treebank \
    averaged_perceptron_tagger \
    punkt \
    && \
    python -m spacy download en_core_web_sm \
    && \
    wget https://storage.googleapis.com/allennlp-public-models/bert-base-srl-2020.03.24.tar.gz

# copy over the source code
COPY . .

CMD [ "python", "main.py" ]

