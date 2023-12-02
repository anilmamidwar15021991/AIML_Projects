import flask; print(flask.__version__)
from flask import Flask, render_template, request
import os
import numpy as np
import pickle
import nltk
from nltk.corpus import stopwords
import string
from nltk.stem.porter import PorterStemmer
import pandas as pd
ps=PorterStemmer()    

app = Flask(__name__)
app.env = "production"
result = ""
print("Flask App intialized:", app.env)

@app.route('/', methods=['GET'])
def hello():
    #print("I am In hello. Made some changes")
    return render_template('index.html')


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





@app.route('/predict', methods=['POST'])
def predict():
    print("Request.method:", request.method)
    print("Request.TYPE", type(request))
    print("In the process of making a prediction.")
    if request.method == 'POST':
        print("Request.form: ", request.form)
        print(request.form['age'])
        

        SMSText = request.form['age']
        transformedText=transform_text(SMSText) 
        transformedText=np.array(transformedText)
        print(f"Transformed Text - {transformedText}")
        
        print(type(transformedText))
        tfid = pickle.load(open('vectorizer.pkl','rb'))
        vector_input = tfid.transform(transformedText.astype('str')).toarray()             
        
        print(f"vector input -{vector_input}")
        print(f"shape -{vector_input.shape}")
        vector_input = pd.DataFrame(vector_input,columns=tfid.get_feature_names_out())
        print(f"shape -{vector_input.shape}")
        model = pickle.load(open('mnb_spam_detector.pkl', 'rb'))
        print("Model Object: ", model)
        prediction = model.predict(vector_input)[0]
        print(prediction)
        predicted = "Spam" if prediction else "Ham" 
        result = f"The model has predicted that the result is: {predicted}"
        return render_template('index.html', result=result)
    return render_template('index.html')

app.run(host='localhost', port=5001, debug=False)
