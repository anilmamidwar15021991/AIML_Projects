import numpy as np
import pandas as pd
import streamlit as st
import os
import sys;sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from dotenv import dotenv_values,load_dotenv
import glob
import time
from urllib.parse import unquote
from PyPDF2 import PdfReader

import asyncio
from tqdm import tqdm
import psycopg2
from sharepoint_service import sharepoint_connect,sharepoint_restapi,sp_model,sharepoint_connect_New,sharepoint_restapi_New

from psycopg2 import sql
from sqlalchemy import create_engine,text
from sentence_transformers import SentenceTransformer,util
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.document_loaders import PyPDFLoader,DirectoryLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings


env_config=dotenv_values('config\.env')


print('Creating SQL connection to PostGreSQL')

db_connection_params = {
    "host": "localhost",
    "dbname": "ppl",
    "user": "postgres",
    "password": "admin",
    "port":"5432"
    
}


async def vector_embedding_spfiles():

    sp=sharepoint_connect_New.SharepointConnector(env_config['site_url'],env_config['App_Id'],env_config['App_Secret'],env_config['base_url'],env_config['Access_Tokenurl'])
    sp_token= await sharepoint_restapi_New.acquire_token(sp)
    for file_detail in await sp.get_sp_files(sp_token):
        web_url=file_detail.web_url
        file_path='test.txt'

        '''
        writing the file names with their relative path to local txt file
        '''
        with open(file_path, 'r') as file:
            existing_content = file.read()
        
        # Append new text to the existing content
        amended_content = existing_content +f"\n {web_url}"

        # Write amended content back to the file
        with open(file_path, 'w') as file:
            file.write(amended_content)
        
        
        """
        reading only pdf files for now 
        """

        if web_url.endswith('.pdf'):
            
            print(f"pdf file -- {web_url}")
            # code to extract relative path from sp web url
            index= web_url.find(env_config['drive_name'])
            relative_path=unquote(web_url[index +len(env_config['drive_name']):].strip())
            pdf_content=await sp.get_file_content(sp_token,relative_path,'pdf')
            print("pdf")







def main():
    
    folder_localpath=r'\\Cviadpaea04\c\CSE\temp_files'
    pdf_files=glob.glob(os.path.join(folder_localpath,'*pdf'))
    ppl_hyperlink_data='PPL_Data_formated.xlsx'


    raw_input_df= pd.read_excel(f"{folder_localpath}\{ppl_hyperlink_data}")



    table_name = 'ppl_pdf_contents'

    # 'looping through all pDFs inside directory'

    CONNECTION_STRING=(f'postgresql://{db_connection_params["user"]}:{db_connection_params["password"]}@{db_connection_params["host"]}:{db_connection_params["port"]}/{db_connection_params["dbname"]}')
    #embeddings=SentenceTransformerEmbeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v1")
    embeddings=SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


    for pdf_file in pdf_files:    
        
        pdf_name= os.path.basename(pdf_file)
        print(f"PDF file name is  - {pdf_name}")
        searched_row=raw_input_df.query("Name==@pdf_name")
        if not searched_row.empty:
            ppl_region='Global' if pd.isna(raw_input_df.query("Name == @pdf_name")['Region'].iloc[0]) else raw_input_df.query("Name == @pdf_name")['Region'].iloc[0]
        else:
            print(f"unable to find pdf file name in xl document")
            ppl_region='Global'
        print(ppl_region)
        '''
        pass each PDF file to read the PDF content and and store vector in pgvector db'''
        try:
            loader=PyPDFLoader(pdf_file)
            documents=loader.load()

            'adding the ppl file name to page_contents metadata of documents'
            new_documents=[]
            for doc in documents:
                temp_doc=doc.copy(update= {'page_content':f"{doc.page_content} \n {pdf_name}"})
                new_documents.append(temp_doc)
            
            text_splitter=RecursiveCharacterTextSplitter(chunk_size=20000,chunk_overlap=0)
            text_chunks=text_splitter.split_documents(new_documents)   

            

            COLLECTION_NAME="ppl_documents_allminiLM"
                

            #create the vector store
            start_time=time.time()
            vectordb=PGVector.from_documents(documents=text_chunks,
                                            embedding=embeddings,
                                            collection_name=COLLECTION_NAME,
                                            connection_string=CONNECTION_STRING,
                                            pre_delete_collection=False)       
            

        except Exception as e:

            print(f" error for file {e}")
        finally:
            print("")
        



    'using langchain to store evectors in postgres'

    # def calculate_average_execution_time(func,*args,**kwargs):
    #     total_execution_time=0
    #     num_runs=10
    #     for _ in range(num_runs):
    #         start_time=time.time()
    #         results=func(*args,**kwargs) #execute the function with its arguments
    #         end_time=time.time()
    #         execution_time=end_time-start_time
    #         total_execution_time+=execution_time
    #     average_execution_time=round(total_execution_time/num_runs,2)
    #     #print(results)
    #     print(f"\nthe function took an avearge of {average_execution_time} seconds to execute")
    #     return results



    #load the store


'semantic search using sentence tarnsformer methods'

# conn=psycopg2.connect(CONNECTION_STRING)
# cursor=conn.cursor()
# model=SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v1")
# #print(embeddings.embed_query(query))

# corpus_embedding_query=f"select embedding from langchain_pg_embedding"
# cursor.execute(corpus_embedding_query)
# corpus_embedding_string=cursor.fetchall()
# print(corpus_embedding_string)
# import torch
# import ast

# 'converting list of string (vectors) from pg to tensors'
# tensors = []
# for tuple_ in corpus_embedding_string:
#     tensor = []
#     for x in tuple_:
#         # Check if the element is a string
#         if isinstance(x, str):
#             # Convert the string representation of the list to a Python list
#             x_list = ast.literal_eval(x)
#             # Convert each element in the list to float
#             x_list = [float(item) for item in x_list]
#             tensor.extend(x_list)  # Extend the tensor with the list elements
#         else:
#             tensor.append(x)  # Append non-string elements directly
#     tensors.append(torch.tensor(tensor))


# corpus_embedding_tensor=torch.stack(tensors)

# prompt_embedding=model.encode(query,convert_to_tensor=True)

# cos_scores=util.semantic_search(prompt_embedding,corpus_embedding_tensor,top_k=3)
# top_results=torch.topk(cos_scores,k=3)


if __name__=='__main__':
    asyncio.run(vector_embedding_spfiles())
    #asyncio.run(main())


