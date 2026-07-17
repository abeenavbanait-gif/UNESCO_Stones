import os
import tempfile
import pandas as pd
from pathlib import Path
import logging

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHROMA_DIR = Path("data/chromadb")
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
CUSTOM_COLLECTION = "custom_uploaded_docs"

_embeddings = None
_vectorstore = None

def get_custom_vectorstore():
    global _embeddings, _vectorstore
    if _vectorstore is None:
        logger.info("Initializing HuggingFace Embeddings for custom docs...")
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        _vectorstore = Chroma(
            collection_name=CUSTOM_COLLECTION,
            embedding_function=_embeddings,
            persist_directory=str(CHROMA_DIR)
        )
    return _vectorstore

def ingest_custom_document(file_bytes: bytes, file_name: str) -> int:
    """
    Saves bytes to a temp file, extracts text, chunks it, and saves to Chroma.
    Returns the number of chunks added.
    """
    ext = os.path.splitext(file_name)[1].lower()
    
    # Write bytes to a temporary file because many loaders require a file path
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
        
    try:
        docs = []
        if ext == ".pdf":
            loader = PyMuPDFLoader(tmp_path)
            docs = loader.load()
        elif ext in [".txt", ".md"]:
            loader = TextLoader(tmp_path, encoding='utf-8')
            docs = loader.load()
        elif ext == ".docx":
            loader = Docx2txtLoader(tmp_path)
            docs = loader.load()
        elif ext == ".csv":
            loader = CSVLoader(tmp_path)
            docs = loader.load()
        elif ext == ".xlsx":
            # Pandas is usually easiest for arbitrary xlsx
            df = pd.read_excel(tmp_path)
            text = df.to_string(index=False)
            docs = [Document(page_content=text, metadata={"source": file_name})]
        else:
            raise ValueError(f"Unsupported file type: {ext}")
            
        # Re-map metadata source to the actual filename instead of the tmp path
        for doc in docs:
            doc.metadata["source"] = file_name
            
        logger.info(f"Loaded {len(docs)} documents from {file_name}. Splitting...")
        
        # Chunk text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        vectorstore = get_custom_vectorstore()
        
        # Add to ChromaDB
        if splits:
            vectorstore.add_documents(documents=splits)
            logger.info(f"Added {len(splits)} chunks to ChromaDB.")
            
        return len(splits)
    finally:
        os.remove(tmp_path)

def ask_custom_question(question: str, api_key: str):
    """
    Searches the custom documents collection and asks Gemini for the answer.
    """
    if not api_key:
        raise ValueError("Google Gemini API Key is required.")
        
    os.environ["GOOGLE_API_KEY"] = api_key
    
    vectorstore = get_custom_vectorstore()
    
    # 1. Retrieve context
    logger.info("Retrieving documents from custom ChromaDB...")
    docs = vectorstore.similarity_search(question, k=5)
    
    if not docs:
        return "No documents have been uploaded yet, or no relevant information was found."
        
    context_text = "\n\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}" for doc in docs])
    
    # 2. Call LLM
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0)
    
    system_prompt = (
        "You are an expert analytical assistant. "
        "Use the following pieces of retrieved context from user-uploaded documents to answer the question. "
        "If you don't know the answer based on the context, say that you don't know. "
        "Provide detailed, accurate answers and cite the Source document if applicable.\n\n"
        "Context:\n"
        f"{context_text}"
    )
    
    logger.info("Querying Gemini...")
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ])
    
    content = response.content
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                return item.get("text", str(content))
            elif isinstance(item, dict) and "text" in item:
                return item["text"]
    elif isinstance(content, dict):
        if "text" in content: return content["text"]
        
    return str(content)
