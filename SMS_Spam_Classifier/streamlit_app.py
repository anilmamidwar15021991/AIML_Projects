import streamlit as st
from PIL import Image
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

nltk.download('punkt')
nltk.download('stopwords')



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




#remove SMS_Spam_Classifier name from path while deploying locally 

tfidf=pickle.load(open('SMS_Spam_Classifier/vectorizer.pkl','rb'))
model=pickle.load(open('SMS_Spam_Classifier/mnb_spam_detector.pkl','rb'))

st.title("SMS Spam classifier")

#content

st.image(Image.open('SMS_Spam_Classifier/spam_image.jpeg'))

st.write("""
A spam classifier uses machine learning to distinguish between legitimate and unsolicited emails . it employs algorithm to analyze content and other features to flag emails spam or not spam.

Algorithm used to train the model is stacking classifier(SVM,NB,Xgboost)

"""
 
)




input_sms= st.text_area("Enter the message to check")


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
        

c1,c2,c3 = st.columns(3)
with c1:
    st.info('**GitHub:[@anilremo23](https://github.com/anilremo23)**',icon="🧠")
with c2:
    st.info('**Kaggle:[@remoanil](https://www.kaggle.com/remoanil)**',icon="💻")
with c3:
    st.info('**LinkedIn:[@AnilMamidwar](https://www.linkedin.com/in/anil-mamidwar-001b6418/)**',icon="👨‍💼")
    
      
