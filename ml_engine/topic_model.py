from pdfminer.high_level import extract_text
from gensim import corpora, models
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import logging

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

def extract_topics(text, num_topics=5, num_keywords=10):
    if not text:
        return []

    processed = preprocess_text(text)
    if not processed:
        return []

    dictionary = corpora.Dictionary([processed])
    corpus = [dictionary.doc2bow(processed)]
    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)

    topics = lda_model.print_topics(num_words=num_keywords)

    # Extract just the keywords from topics
    keywords = []
    for topic in topics:
        words = topic[1].split("+")
        for word in words:
            keyword = word.split("*")[1].strip().strip('"')
            if keyword not in keywords:
                keywords.append(keyword)

    return keywords
