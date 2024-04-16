db_connection_params = {
    "host": "localhost",
    "dbname": "test",
    "user": "postgres",
    "password": "admin",
    "port":"5432"
    
}
CONNECTION_STRING=(f'postgresql://{db_connection_params["user"]}:{db_connection_params["password"]}@{db_connection_params["host"]}:{db_connection_params["port"]}/{db_connection_params["dbname"]}')
conn=psycopg2.connect(CONNECTION_STRING)
cursor=conn.cursor()

'used sentence transformer model to get embeddings'
model =SentenceTransformerEmbeddings(model_name='sentence-transformers/distiluse-base-multilingual-cased-v1')
prompt_embeddding = model.embed_query(query)
#prompt_embeddding=np.array(prompt_embeddding
                           
print(f"select * from langchain_pg_embedding where 1- (embedding <=> '{prompt_embeddding}') >=0.3")
cursor.execute(

    f"select * from langchain_pg_embedding where 1- (embedding <=> '{prompt_embeddding}') >=0.3"

)
result=cursor.fetchall()


# # Insert values onto table from pandas dataframe
# for index,row in df.iterrows():
#     try:
#         insert_query=text(f"""INSERT INTO {table_name}
#                          (pdf_name,pdf_content)
#                          values(:pdf_name,:pdf_content)""")
#         connection.execute(insert_query,parameters={"pdf_name":row['pdf_name'],"pdf_content":row['pdf_content']})
#         connection.commit()
#     except Exception as e:
#         print(f" Insert sqljob failed , may be data already available in table \n -{e}")