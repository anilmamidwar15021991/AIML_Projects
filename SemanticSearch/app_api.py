import numpy as np
import pandas as pd

import os
import glob
import time
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
import psycopg2
from sentence_transformers import SentenceTransformer,util
from langchain.embeddings import SentenceTransformerEmbeddings



db_connection_params = {
    "host": "localhost",
    "dbname": "test",
    "user": "postgres",
    "password": "admin",
    "port":"5432"
    
}

CONNECTION_STRING=(f'postgresql://{db_connection_params["user"]}:{db_connection_params["password"]}@{db_connection_params["host"]}:{db_connection_params["port"]}/{db_connection_params["dbname"]}')

embeddings=SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


#function to read query and search the query vector in pgvector db

def user_query(query,collection_name='ppl_documents_allminiLM'):
    
    pgvector_doc_search=PGVector(collection_name=collection_name,
                                 connection_string=CONNECTION_STRING,
                                 embedding_function=embeddings)
    
    retrieved_docs=pgvector_doc_search.similarity_search_with_score(query,k=3)   
    
    
    
 
    




    

    

    
    


    

