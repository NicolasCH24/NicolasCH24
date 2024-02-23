from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os
import streamlit as st

class CrearRetriever:
    #Archivo temporal por su corto tiempo de ejecucion, pero puede existir la posibilidad de almacenarlo en Cassandra BBDD Vectorial.
    #Pulir la clase para almacenar mas tipos de documentos, no se descartan los videos.
    def __init__(self, documentos):
        self.documentos = documentos
    
    @staticmethod
    def vectorize_text(documentos, vector_store):
        if documentos is not None:
        
        # Write to temporary file
            temp_dir = tempfile.TemporaryDirectory()
            file = documentos
            temp_filepath = os.path.join(temp_dir.name, file.name)
            with open(temp_filepath, 'wb') as f:
                f.write(file.getvalue())

        # Load the PDF
            docs = []
            loader = PyPDFLoader(temp_filepath)
            docs.extend(loader.load())

        # Create the text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1500,
                chunk_overlap  = 100
                )

        # Vectorize the PDF and load it into the Astra DB Vector Store
            pages = text_splitter.split_documents(docs)
            vector_store.add_documents(pages)  
            return st.info(f"{len(pages)} pages loaded.")
        
    
    def load_retriever(vector_store):
        _retriever = vector_store.as_retriever(
        search_kwargs={"k": 5}
        )
        return _retriever
        
    