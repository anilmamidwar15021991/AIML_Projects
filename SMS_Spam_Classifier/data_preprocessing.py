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
os.system('pip install nltk')
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
import string
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.porter import PorterStemmer
ps=PorterStemmer()
cv=CountVectorizer()


#defining the function for data preprocessing
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


if __name__=='__main__':
    #passing input arguments and reading them args variable
    parser=argparse.ArgumentParser()
    parser.add_argument('--train-test-split-ratio',type=float,default=0.3)
    parser.add_argument('--random-split',type=int,default=0)
    args,_=parser.parse_known_args()
    print(f"Received arguments {args}")
    
    #reading the csv file from the path within instance 
    input_data_path=os.path.join('/opt/ml/processing/input','EDAprocessed.csv')
    print(f"reading data from {input_data_path}")
    df=pd.read_csv(input_data_path)
    print(df.shape)
    
    #function to perform data preprocessing
    df['transformed_text']=df['text'].apply(transform_text)
    X=df['transformed_text']
    y=df['label'].values
    
    #converting words to numerical form using Countvector
    print(f"converting words to numerical form using Countvector")
    X=cv.fit_transform(X.astype('str')).toarray()
    
    #creating X dataframe using above nd.array output with column names
    X=pd.DataFrame(X,columns=cv.get_feature_names())
    
    #assigning the args values to variables
    split_ratio=args.train_test_split_ratio
    random_state=args.random_split
    
    #train test split the dataframe 
    print(f"Train test split started ")
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=split_ratio,random_state=random_state)
    
    #concatting the train and test series into dataframe as one
    print(f"Type of X_train-{type(X_train)},y_train-{type(y_train)}")
    
    y_train=pd.Series(y_train,name='label')
    print(f"{y_train.shape}")
    train_full =pd.concat([y_train,X_train],axis=1)
    print(f" Train full shape -{train_full.shape}")
    
    test_full=pd.concat([pd.Series(y_test,name='label'),X_test],axis=1)
    
    print(f"Train data shape after preprocessing: {train_full.shape}")
    print(f"Test data shape after preprocessing: {test_full.shape}")
    
    
    #saving all dataframes in csv format to instance location
    train_features_headers_output_path=os.path.join('/opt/ml/processing/train_headers','train_data_with_headers.csv')
    train_features_output_path=os.path.join('/opt/ml/processing/train','train_data.csv')
    test_features_output_path=os.path.join('/opt/ml/processing/test','test_data.csv')
    print(f"saving training features to {train_features_output_path}")
    train_full.to_csv(train_features_output_path,header=False,index=False)
    
    print(f"saving training features with headers to {train_features_output_path}")
    train_full.to_csv(train_features_headers_output_path,index=False)
    
    print(f"saving test features to {train_features_output_path}")
    test_full.to_csv(test_features_output_path,header=False,index=False)
    print("Preprocessing Completed") 
