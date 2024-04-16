import numpy as np
import pandas as pd
import streamlit as st
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
    
    print(retrieved_docs)
    col1,col2,col3= st.columns(3)
    col1,col2,col3=st.columns([2,2,2]) 
    col1.write(retrieved_docs[0][0].metadata["source"]+ "\n\n" + retrieved_docs[0][0].page_content)
    
    col2.write(retrieved_docs[1][0].metadata["source"] + "\n\n" + retrieved_docs[1][0].page_content )
    col3.write(retrieved_docs[2][0].metadata["source"] + "\n\n" + retrieved_docs[2][0].page_content )
    
    # for doc, score in retrieved_docs:
    #     print("Score",score)
    #     #print(doc.page_content)
    #     print(doc.metadata["source"])

    #print(retrieved_docs[0][0].metadata["source"])
    #print(retrieved_docs[1][0].metadata["source"])
    #print(retrieved_docs[2][0].metadata["source"])

#user_query("paternity leave for asia")

    
def main():
    try:
        st.set_page_config("Semantic Search PPL Docs")
        st.header("Search PPL docs")

        user_question= st.text_input("Search anything related to comscore policies")

        
        if user_question:
            start_time=time.time()
            user_query(user_question) 
            end_time=time.time()
        #total_timetaken=end_time-start_time


    except Exception as e:
        
        print(f"error at searching the docs-",e)
    
    finally:
        
        print(f"")

    

if __name__=="__main__":
    main()




    

    

    
    


    

