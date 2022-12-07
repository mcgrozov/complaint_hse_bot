import pickle
import re
import nltk
from nltk.corpus import stopwords
from razdel import tokenize
import pandas as pd
from pymystem3 import Mystem


nltk.download('stopwords')
ru_stopwords = set(stopwords.words('russian'))
ru_stopwords.add('это')


class TextPreprocessing:
    def __init__(self,
                 stopwords_removing=False,
                 lemmatizing=False):

        self.stopwords_removing = stopwords_removing
        self.lemmatizing = lemmatizing
        if lemmatizing:
            self.lemmatizer = Mystem()

    def keep_cyrillic_only(self, texts):
        pattern = re.compile('[^А-Яа-яё \n]')
        return [re.sub(pattern, '', text) for text in texts]

    def remove_backslash_n(self, texts):
        pattern = re.compile('\n')
        return [re.sub(pattern, ' ', text.strip()) for text in texts]

    def tokenize(self, texts):
        return [[tokenized.text for tokenized in tokenize(text)] for text in texts]

    def lemmatize(self, texts):
        return [''.join(self.lemmatizer.lemmatize(text)) for text in texts]

    def remove_stopwords(self, texts):
        return [[w for w in text if w not in ru_stopwords] for text in texts]

    def transform(self, texts):

        texts = self.keep_cyrillic_only(texts)
        texts = [text.lower() for text in texts]

        if self.lemmatizing:
            texts = self.lemmatize(texts)

        texts = self.remove_backslash_n(texts)
        texts = self.tokenize(texts)

        if self.stopwords_removing:
            texts = self.remove_stopwords(texts)

        return [' '.join(t) for t in texts]


class MessageClassifier:
    def __init__(self,
                 clf_path='',
                 tfidf_path=''):
        self.preproc = TextPreprocessing(stopwords_removing=True,
                                         lemmatizing=True)

        with open(tfidf_path, 'rb') as f:
            self.tfidf = pickle.load(f)

        with open(clf_path, 'rb') as f:
            self.clf = pickle.load(f)

    def predict(self,
                message: str):
        text = self.preproc.transform([message])
        print(text)
        encoded_text = self.tfidf.transform(text)
        return self.clf.predict(pd.DataFrame(encoded_text.toarray(),
                                             columns=self.tfidf.get_feature_names_out()))


if __name__ == '__main__':
    m_clf = MessageClassifier('clf.pkl', 'tfidf.pkl')
    message = input()
    m_clf.predict(message)
