import streamlit as st
from clase_sql_nosql import CassandraDBChatCMessageHistory, conexion_cassandra, conexion_cassandra_vector, cargar_vector_store
from clase_asesores import CrearAsesores
from clase_retrievers import CrearRetriever
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import HumanMessage, AIMessage
from langchain.schema.runnable import RunnableMap
from astrapy.db import AstraDB
from langchain_openai import OpenAIEmbeddings

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.container.markdown(self.text + "▌")

#APYS
import os
os.environ["OPENAI_API_KEY"] = "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"
os.environ["TAVILY_API_KEY"] = "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"

# Conexion a Cassandra
secure_connect = 'C:/Users/nicos/Downloads/secure-connect-asesoria.zip'
token = "C:/Users/nicos/Downloads/asesoria-token.json"
session = conexion_cassandra(secure_connect, token)

#Chat History
historial = CassandraDBChatCMessageHistory(session)

#Conexion Cassandra VectorStore
#db = conexion_cassandra_vector()

# Vector Store
_vector_store = cargar_vector_store()

# Obtener sesiones de chat
sesiones = historial.obtener_sesiones()
lista_sesiones = []
for sesion in sesiones:
    lista_sesiones.append(sesion[0])

st.title("Tu Asesoría personal ha llegado..")
st.markdown("""La IA generarativa es considerada como la nueva revolucion industrial.  
Por que? Estudios más resientes muestran un **37% de eficiencia** en las actividades laborales y cotidianas!""")

# Include the upload form for new data to be Vectorized
with st.sidebar:
    with st.form('upload'):
        documentos = st.file_uploader('Proporciona documentación adicional para establecer más contexto', type=['pdf'])
        submitted = st.form_submit_button('Almacenar en tus datos')
        if submitted:
            retrievers = CrearRetriever(documentos)
            retrievers.vectorize_text(documentos, _vector_store)

@st.cache_resource(show_spinner='Getting retriever')
def load_retriever(_vector_store):
        _retriever = _vector_store.as_retriever(
        search_kwargs={"k": 5}
        )
        return _retriever

_retriever = load_retriever(_vector_store)

# Dibujar las sesiones de chat en el panel lateral izquierdo
st.sidebar.title("Sesiones de chat existentes:")
session_selected = st.sidebar.selectbox("Seleccionar sesión:", lista_sesiones)

# Mostrar el historial de chat correspondiente cuando se selecciona una sesión
if session_selected:
    st.title(f"Historial de chat para la sesión: {session_selected}")
    chat_sesion = historial.get_chat_history(session_selected)
    for mensaje in chat_sesion:
        if isinstance(mensaje, HumanMessage):
            with st.chat_message('human'):
                st.write("Usuario:", mensaje.content)
        elif isinstance(mensaje, AIMessage):
            with st.chat_message('assistant'):
                st.write("Asesor:", mensaje.content)
        st.write("---")

# Draw the chat input box
if question := st.chat_input("Consulta asesor"):
    
    # Store the user's question in a session object for redrawing next time
    historial.add_user_msj(session_selected, question)

    # Draw the user's question
    with st.chat_message('human'):
        st.markdown(question)

    # UI placeholder to start filling with agent response
    with st.chat_message('assistant'):
        response_placeholder = st.empty()

    asesores = CrearAsesores(_retriever)
    asesor_personal = asesores.CrearAsesor(_retriever)
    result = asesor_personal.invoke({'input': question}, config={'callbacks': [StreamHandler(response_placeholder)]})
    answer = result["output"]

    # Store the bot's answer in a session object for redrawing next time
    historial.add_ai_msj(session_selected, answer)

    # Write the final answer without the cursor
    response_placeholder.markdown(answer)