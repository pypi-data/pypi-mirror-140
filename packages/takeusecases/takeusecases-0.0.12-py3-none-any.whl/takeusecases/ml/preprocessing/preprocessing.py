import pandas as pd
import logging
import spacy
import re
from takeusecases.ml.preprocessing.preprocessing_messages import Vectorizer


class Preprocessing:

    def clean_data(self, df: pd.DataFrame, stopwords, selected):
        """
        Perform data cleansing.

        Parameters
        ----------
        df  :   pd.Dataframe
                Dataframe to be processed
        stopwords : pickle loaded file of stopwords
        selected : pickle loaded file of selected words

        Returns
    	-------
        pd.Dataframe
            Clean Data Frame
        """
        logging.info("Cleaning data")
        df_copy = df.copy()
        df_copy['Message'] = df_copy['Message'].apply(lambda x: re.sub(r'[^\w\s]','',x) )
        nlp = spacy.load('pt_core_news_sm')
        df_copy['Message'] = df_copy['Message'].apply(lambda x: [word.lemma_ for word in nlp(x) ] )
        df_copy['Message'] = df_copy['Message'].apply(lambda x: [word for word in x if word in selected] )
        df_copy.Message = df_copy.Message.apply(lambda x: [word for word in x if word not in stopwords])
        df_copy = df_copy[df_copy['Message'].map(len)>0]
        return df_copy




    def get_vectors(self, df: pd.DataFrame):
        """
        Perform vectorizer of the textual data

        Parameters
        ----------
        df  :   pd.Dataframe
                Dataframe to be processed

        Returns
    	-------
        pd.Dataframe
            Vectorized Data Frame
        """
        path = '../output/fasttext/titan_v2_after_correction_fasttext_window4_mincount20_cbow.kv'
        preprocessing = Vectorizer(path)
        df = preprocessing.process(df)
