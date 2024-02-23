from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import json
from langchain.memory import CassandraChatMessageHistory
from astrapy.db import AstraDB
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
import os
import streamlit as st

# APY OPENAI
os.environ["OPENAI_API_KEY"] = "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"

def conexion_cassandra(secure_connect, token):
  cloud_config= {
    'secure_connect_bundle': secure_connect
      }
  
  with open(token) as f:
      secrets = json.load(f)

  CLIENT_ID = secrets["clientId"]
  CLIENT_SECRET = secrets["secret"]

  auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
  cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
  session = cluster.connect()

  row = session.execute("select release_version from system.local").one()
  if row:
    print(row[0])
  else:
    print("An error occurred.")
  return session

def conexion_cassandra_vector():
   db = AstraDB(
       token="AstraCS:DZLNwDFMqTEXaZgXayJLCnNZ:28f5cdba8aff2cfff59b42e86c893f6a841a4669cdf06fc29a6bc6a5d4cffeba",
       api_endpoint="https://9c716385-228f-4a90-9ea5-594d44b69b4b-us-east1.apps.astra.datastax.com",
       namespace="chat_app_vector")
   return(f"Connected to Astra DB: {db.get_collections()}")

@st.cache_resource(show_spinner='Connecting to Astra')
def cargar_vector_store():
   _vector_store = AstraDBVectorStore(
    embedding=OpenAIEmbeddings(),
    collection_name="docsearch_vector",
    api_endpoint="https://9c716385-228f-4a90-9ea5-594d44b69b4b-us-east1.apps.astra.datastax.com",
    token="AstraCS:DZLNwDFMqTEXaZgXayJLCnNZ:28f5cdba8aff2cfff59b42e86c893f6a841a4669cdf06fc29a6bc6a5d4cffeba",
    namespace="chat_app_vector",)
   return _vector_store


class CassandraDBChatCMessageHistory:
    def __init__(self, session):
        self.session = session

    def obtener_sesiones(self):
        query = """SELECT partition_id as Sesiones
                FROM chat_app.message_store
                GROUP BY partition_id;
                """
        lista_sesiones = self.session.execute(query)
        #Retorna True si no existe
        return lista_sesiones
        
    def get_chat_history(self, session_id):
        #METODO DE OBTENCION PARA EL CHAT, **NO PARA LA IA** (EXPLICACION MUY IMPORTANTE)!!
        message_history = CassandraChatMessageHistory(
            session_id=session_id,
            session=self.session,
            keyspace="chat_app",
            )
        chat_history = message_history.messages
        return chat_history
   
    def add_user_msj(self, session_id, question):
       message_history = CassandraChatMessageHistory(
            session_id=session_id,
            session=self.session,
            keyspace="chat_app"
            )
       message_history.add_user_message(question)
       return question
    
    def add_ai_msj(self,session_id, answer):
       message_history = CassandraChatMessageHistory(
          session_id=session_id,
            session=self.session,
            keyspace="chat_app"
            )
       message_history.add_ai_message(answer)
       return answer
    
      
       
