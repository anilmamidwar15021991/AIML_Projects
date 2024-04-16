import numpy as np
import pandas as pd

import os
import glob
import time
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
import psycopg2
import json

from sentence_transformers import SentenceTransformer,util
from langchain.embeddings import SentenceTransformerEmbeddings

import logging


class searchcontent:


    '''
    class for searching the content in documents

    '''
    def __init__(self,connection_string,collection_name,embeddings_func):
        self.connection_string=connection_string
        self.collection_name=collection_name
        self.embeddings_func=embeddings_func
    

    def search_query(self,query,K):
        'K = max search documents to be returned'

        try:
            pgvector_doc_search =PGVector(collection_name=self.collection_name,
                                          connection_string=self.connection_string,
                                          embedding_function=self.embeddings_func)
            
            retrived_docs=pgvector_doc_search.similarity_search_with_score(query,k=K)
            return retrived_docs
        
        except Exception as e:
            print(f"search query function failed for reason -{e}")
            #raise



'''
below is th code to test the class and methods
'''

db_connection_params = {
    "host": "localhost",
    "dbname": "test",
    "user": "postgres",
    "password": "admin",
    "port":"5432"
    
}

CONNECTION_STRING=(f'postgresql://{db_connection_params["user"]}:{db_connection_params["password"]}@{db_connection_params["host"]}:{db_connection_params["port"]}/{db_connection_params["dbname"]}')
collection_name='ppl_documents_allminiLM'
embeddings=SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

searchobject=searchcontent(connection_string=CONNECTION_STRING,
                            collection_name=collection_name,
                            embeddings_func=embeddings)


#query='leave policy for asia'
#semantic_response=searchobject.search_query(query,3)
#print(semantic_response)

# result={}
# for doc, score in semantic_response:
#     result[doc.page_content]={"metadata":doc.metadata,"score":score}
# print(result)
