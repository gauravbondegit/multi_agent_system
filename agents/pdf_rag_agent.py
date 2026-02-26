import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
VECTOR_STORE_PATH = "vector_store"

def _build_vector_store(pdf_path: str, store_path: str):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(pages)

    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(store_path)
    print(f"Vector store saved at: {store_path}")
    return vector_store

def get_vector_store(pdf_path):
    """Creates or loads a vector store for a given PDF."""
    store_name = os.path.basename(pdf_path).replace('.pdf', '')
    store_path = os.path.join(VECTOR_STORE_PATH, store_name)

    if os.path.exists(store_path):
        print(f"Loading existing vector store: {store_path}")
        try:
            return FAISS.load_local(store_path, embeddings)
        except Exception as load_error:
            print(f"Safe load failed for {store_path}. Rebuilding store. Error: {load_error}")
            shutil.rmtree(store_path, ignore_errors=True)
    
    print(f"Creating new vector store for: {pdf_path}")
    return _build_vector_store(pdf_path, store_path)

def query_rag_agent(pdf_path: str, query: str):
    """Queries the RAG agent for information from the PDF."""
    vector_store = get_vector_store(pdf_path)
    retriever = vector_store.as_retriever()
    docs = retriever.get_relevant_documents(query)
    
    # Format the retrieved documents into a string context
    context = "\n---\n".join([doc.page_content for doc in docs])
    return context, [doc.metadata for doc in docs]