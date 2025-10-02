from langchain.chains import RetrievalQA

from langchain.vectorstores import FAISS


from langchain.llms import Ollama

from langchain.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
import os

import json


def quey_vectorstore(query):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    print("Loading vector store from 'faiss_index/'...")
    db = FAISS.load_local(r"F:\projects\wastewise\backend\project\app\chatbot\faiss_index", embeddings , allow_dangerous_deserialization=True)
    print("Vector store loaded.")
    LLM=Ollama(model="llama3.1:8b")
    retriever = db.as_retriever(search_kwargs={"k": 1})

    QA = RetrievalQA.from_chain_type(
        llm=LLM,retriever=retriever, chain_type="stuff")
    result = QA.invoke(query)
    return result
#print(quey_vectorstore("what is your company mission?"))