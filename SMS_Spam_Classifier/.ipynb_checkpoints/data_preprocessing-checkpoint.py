#the below entire code will be saved in this .py file and will be run on another server instance as created above 
import argparse
import os
import warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler,MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.exceptions import DataConversionWarning
#Lowercase,Tokenization,Removing Special chracters,Removing Stop words, Stemming
from nltk.corpus import stopwords
import string
from nltk.stem.porter import PorterStemmer
ps=PorterStemmer()
def transform_text(text):
    text=text.lower()
    y=[]
    #tokenization
    text=nltk.word_tokenize(text)
    for i in text:
        if i.isalnum():
            y.append(i)
    text=y[:]
    y.clear()
    #removing stopwords and punctuations
    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)
    text=y[:]
    y.clear()
    for i in text:
        y.append(ps.stem(i))
    return y

data_eda['transformed_text']=data_eda['text'].apply(transform_text)
data_eda.to_csv('/home/sagemaker-user/rawdata/','preprocessed_data.csv')

print(data_eda)
