from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
#from langchain.embeddings import HuggingFaceEmbeddings
from groq import Groq
import os
from langchain.embeddings import OllamaEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# ✅ Initialize Groq Client
def get_groq_response(prompt):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    response = client.chat.completions.create(
       # model="llama3-8b-8192",  # Groq's fast free model
        model="llama-3.1-8b-instant",

        messages=[
            {"role": "system", "content": "You are a helpful AI assistant. Answer clearly and concisely based ONLY on the provided context."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


def quey_vectorstore(query):
    # ✅ Replace Ollama embeddings with HuggingFace (free & offline)
   # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    print("Loading vector store from 'faiss_index/'...")
    db = FAISS.load_local(
        r"F:\Program Files\projects\Bookkeeping\Backend\project\chatapp\chatbot\faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )
    print("Vector store loaded.")

    # ✅ Retrieve best matching context
    retriever = db.as_retriever(search_kwargs={"k": 1})
    docs = retriever.get_relevant_documents(query)
    context = docs[0].page_content if docs else "No relevant context found."

    # ✅ Build structured prompt for Groq model
    prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer clearly using ONLY the context."

    answer = get_groq_response(prompt)
    return answer
