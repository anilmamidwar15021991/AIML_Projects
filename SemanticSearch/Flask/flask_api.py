import sys
import json
import os

#code to include parent and child directory to sys path bso that all scripts can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))


from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.pgvector import PGVector
import psycopg2
from sentence_transformers import SentenceTransformer,util
from langchain.embeddings import SentenceTransformerEmbeddings
import flask
from flask import Flask,request,jsonify
from flask_restful import Api, Resource ,marshal_with,fields
from search_content import searchcontent #user defined class



print(flask.__version__)
app=Flask(__name__)
app.env='Development'
api=Api(app)
result={}
print(f"Flask API running : {app.env}")

db_connection_params = {
    "host": "localhost",
    "dbname": "test",
    "user": "postgres",
    "password": "admin",
    "port":"5432"
    
}
collection_name='ppl_documents_allminiLM'
CONNECTION_STRING=(f'postgresql://{db_connection_params["user"]}:{db_connection_params["password"]}@{db_connection_params["host"]}:{db_connection_params["port"]}/{db_connection_params["dbname"]}')
print("Embedding model loaded")
embeddings=SentenceTransformerEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


class Policydocs(Resource):
    @marshal_with()


@app.route('/',methods=['GET'])
def init():
    print(f"Welcome to the PPL docs API page ")
    return ({"message":"Welcome to the PPL docs API page"})

@app.route('/Ssearch',methods=['GET'])
def Ssearch():
    print(F"Request method is {request.method}")
    
    try:
        if request.method=='GET':
            query=request.args.get('query')
            if query is None:
                return jsonify({"error":"Input query is missing"}),400
            'call the semantic search function here  '
        searchobject=searchcontent(connection_string=CONNECTION_STRING,
                                collection_name=collection_name,
                                embeddings_func=embeddings)
        
    
        semantic_response=searchobject.search_query(query,3)
        #print(semantic_response)
        
        for doc,score in semantic_response:
            result[doc.page_content]={"metadata":doc.metadata,"score":score}
        print(result)
        #json_response=jsonify(semantic_response),200
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error occured : {str(e)}")
        return jsonify({"error":e},500)

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error":"Resource bot found"},404)
    
if __name__=='__main__':
    app.run(debug=True)

