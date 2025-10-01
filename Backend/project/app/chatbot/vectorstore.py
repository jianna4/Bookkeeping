from langchain.vectorstores import FAISS
import json
import os
from langchain.embeddings import OllamaEmbeddings


from langchain.schema import Document



with open(r"F:\projects\wastewise\backend\project\app\chatbot\chunks.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert back to Document objects
documents = [Document(page_content=d["content"], metadata=d["metadata"]) for d in data]

embeddings = OllamaEmbeddings(model="nomic-embed-text")


#now the vector db
vectorstore = FAISS.from_documents(documents, embeddings)
print("Vector store created with FAISS.")
vectorstore.save_local("faiss_index")
print("Vector store saved to 'faiss_index/'")