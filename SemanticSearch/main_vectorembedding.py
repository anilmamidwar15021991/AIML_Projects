import numpy as np
import pandas as pd
import streamlit as st
import os
import io
import sys;sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from dotenv import dotenv_values,load_dotenv
import glob
import time
from urllib.parse import unquote
from PyPDF2 import PdfReader,PdfFileReader

import asyncio
from tqdm import tqdm
import psycopg2
from sharepoint_service import sp_model,sharepoint_connect_New,sharepoint_restapi_New

from psycopg2 import sql
from sqlalchemy import create_engine,text
from sentence_transformers import SentenceTransformer,util
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_core.document_loaders import Blob,BaseBlobParser
from langchain_core.documents import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from typing import AsyncIterator, Iterator


env_config=dotenv_values('config\.env')


print('Creating SQL connection to PostGreSQL')

db_connection_params = {
    "host": "localhost",
    "dbname": "ppl",
    "user": "postgres",
    "password": "admin",
    "port":"5432"
    
}

vector_dbname='ppl_pdf_contents'


CONNECTION_STRING=(f'postgresql://{db_connection_params["user"]}:{db_connection_params["password"]}@{db_connection_params["host"]}:{db_connection_params["port"]}/{db_connection_params["dbname"]}')
#embeddings=SentenceTransformerEmbeddings(model_name="sentence-transformers/distiluse-base-multilingual-cased-v1")
embeddings=SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


async def vector_embedding_spfiles():

    sp=sharepoint_connect_New.SharepointConnector(env_config['site_url'],env_config['App_Id'],env_config['App_Secret'],env_config['base_url'],env_config['Access_Tokenurl'])
    sp_token= await sharepoint_restapi_New.acquire_token(sp)

    '''
    get all the document list from the sharepoint site and loop through documnet list of type 'documentLibrary'
    '''

    #list_items=await sp.get_lists(sp_token)
    # documenttype_listitem = [listitem for listitem in list_items.value if listitem['template']=='documentLibrary']
    # print(f"no of document libraries available are -{documenttype_listitem.count_items()}")
    # if documenttype_listitem.count_items()!=0:
    #     "loop through each list id to get all drive items"
        
    # else :
    #     print(f"No document libraries are available ")

    '''
    Looping through each files of sharepoint
    '''
    for file_detail in await sp.get_sp_files(sp_token):
        try:

            web_url=file_detail.web_url
            
            file_path='test.txt'

            '''
            writing the file names with their relative path to a local txt file
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
                drive_id=file_detail.drive_id
                item_id=file_detail.item_id
                print(f"pdf file -- {web_url}")
                # code to extract relative path from sp web url
                # index= web_url.find(env_config['drive_name'])
                # relative_path=unquote(web_url[index +len(env_config['drive_name']):].strip())

                pdf_binary_content=await sp.get_file_content(sp_token,drive_id,item_id,'pdf')  
                
                documents=""
                if pdf_binary_content is not None:

                    pdf_data=PdfReader(io.BytesIO(pdf_binary_content))
                    print(f"Total no of pages are - {len(pdf_data.pages)}")
                    pdf_text=" "
                    documents=[]
                    for page_num in range(len(pdf_data.pages)):
                        page=pdf_data.pages[page_num]
                        pdf_text =page.extract_text()
                        document=Document(page_content=pdf_text,
                                        metadata={"source":web_url, "page_number":page_num})
                        documents.append(document)
                    
                    
                        # blob=Blob(data=pdf_text)                
                        # parser=MyParser()
                        # document=parser.lazy_parse(blob,page_num,web_url)
                        # documents.append(document)

                        # new_documents=[]
                        # for doc in documents:
                        #     temp_doc=doc.copy(update= {'page_content':f"{doc.page_content} \n {web_url}"})
                        #     new_documents.append(temp_doc)

                    text_splitter=RecursiveCharacterTextSplitter(chunk_size=20000,chunk_overlap=0)
                    text_chunks=text_splitter.split_documents(documents) 
                    COLLECTION_NAME="ppl_documents_allminiLM1"
                    

                    #create the vector store
                    start_time=time.time()
                    vectordb=PGVector.from_documents(documents=text_chunks,
                                                    embedding=embeddings,
                                                    collection_name=COLLECTION_NAME,
                                                    connection_string=CONNECTION_STRING,
                                                    pre_delete_collection=False) 
                    
                else:
                    print("unable to read file content") 

                
        except Exception as e:
            print(f"unable to read the file- {e}")

        finally:
            print("Process completed")            
                

            


def main():
    
    folder_localpath=r'\\Cviadpaea04\c\CSE\ppl_pdffiles'
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

            

            COLLECTION_NAME="ppl_documents_allminiLM1"
                

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


if __name__=='__main__':
    asyncio.run(vector_embedding_spfiles())
    #main()




