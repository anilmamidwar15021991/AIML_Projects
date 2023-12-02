import streamlit as st

import pickle
import pandas as pd
import numpy as np
import string
import nltk
from nltk.corpus import stopwords
import string
from nltk.stem.porter import PorterStemmer
import pandas as pd
ps=PorterStemmer()   
from xgboost import XGBClassifier


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
    
        #stemming applied on text
        for i in text:
            y.append(ps.stem(i))
        return y





tfidf=pickle.load(open('SMS_Spam_Classifier/vectorizer.pkl','rb'))
model=pickle.load(open('SMS_Spam_Classifier/mnb_spam_detector.pkl','rb'))

st.title("SMS Spam classifier")
input_sms= st.text_area("Enter the message")


if st.button('Predict'):

    #1.preprocess    
    transform_sms=transform_text(input_sms)
    print(type(transform_sms))
    transform_sms=np.array(transform_sms)
    #2.vectorize
    vector_input=tfidf.transform(transform_sms.astype('str')).toarray()
    print(type(vector_input))
    print(vector_input)
    vector_input = pd.DataFrame(vector_input,columns=tfidf.get_feature_names_out())

    #3.predict

    prediction= model.predict(vector_input)[0]
    #4.display
    #st.header("Spam") if prediction else st.header("Not Spam")
    if prediction==1:
        st.header("Spam")
    else:
        st.header("Not Spam")
      
