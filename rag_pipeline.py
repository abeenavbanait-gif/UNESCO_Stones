import os
from pathlib import Path
import logging
import asyncio

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Langchain / RAG imports
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from download_dossiers import download_dossier

# Paths
CHROMA_DIR = Path("data/chromadb")
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
COLLECTION_NAME = "unesco_dossiers"

# Global embeddings and vectorstore initialization
_embeddings = None
_vectorstore = None

def get_vectorstore():
    global _embeddings, _vectorstore
    if _vectorstore is None:
        logger.info("Initializing HuggingFace Embeddings (all-MiniLM-L6-v2)...")
        # Load small local model for fast on-device embeddings
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        logger.info("Initializing ChromaDB...")
        _vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=_embeddings,
            persist_directory=str(CHROMA_DIR)
        )
    return _vectorstore

async def ingest_dossier(unesco_id: str):
    """
    Ensures the PDF is downloaded and ingested into the vector database.
    """
    pdf_path = Path(f"data/dossiers/{unesco_id}.pdf")
    
    # 1. Download if not exists
    if not pdf_path.exists():
        logger.info(f"Dossier {unesco_id}.pdf not found locally. Triggering on-demand download...")
        downloaded_path = await download_dossier(str(unesco_id))
        if not downloaded_path:
            return False, "Failed to download the dossier from UNESCO."
    
    vectorstore = get_vectorstore()
    
    # 2. Check if already ingested (we store source metadata)
    # Chroma allows fetching metadata, but it's simpler to just try loading.
    # To prevent re-ingesting, we can check if any documents match this source.
    existing_docs = vectorstore.get(where={"source": str(pdf_path)})
    if existing_docs and existing_docs['ids']:
        logger.info(f"Dossier {unesco_id} is already in the Vector Database.")
        return True, "Already ingested."
        
    # 3. Load PDF
    logger.info(f"Extracting text from {pdf_path}...")
    loader = PyMuPDFLoader(str(pdf_path))
    docs = loader.load()
    
    # 4. Chunk text
    logger.info("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # Add unesco_id to metadata so we can filter during retrieval
    for split in splits:
        split.metadata['unesco_id'] = str(unesco_id)
        
    # 5. Embed and store
    logger.info(f"Embedding {len(splits)} chunks into ChromaDB...")
    vectorstore.add_documents(documents=splits)
    logger.info(f"Successfully ingested dossier {unesco_id}.")
    
    return True, "Ingestion successful."

def ask_question(unesco_id: str, question: str, api_key: str):
    """
    Runs a RAG query over the vector database for a specific site without relying on langchain.chains.
    """
    if not api_key:
        return "Error: Google Gemini API Key is required."
        
    os.environ["GOOGLE_API_KEY"] = api_key
    
    vectorstore = get_vectorstore()
    
    # 1. Retrieve context
    logger.info("Retrieving documents from ChromaDB...")
    docs = vectorstore.similarity_search(
        question, 
        k=5, 
        filter={"unesco_id": str(unesco_id)}
    )
    context_text = "\\n\\n".join([doc.page_content for doc in docs])
    
    # 2. Call LLM directly
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    system_prompt = (
        "You are an expert geologist and UNESCO researcher.\\n"
        "Use the following pieces of retrieved context from the site's official nomination dossier to answer the question.\\n"
        "If you don't know the answer based on the context, say that you don't know.\\n"
        "Use detailed, professional language. Focus heavily on building stones, materials, and architectural details if asked.\\n"
        "\\nContext:\\n"
        f"{context_text}"
    )
    
    logger.info(f"Querying Gemini for site {unesco_id}...")
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ])
    
    return response.content

if __name__ == "__main__":
    import asyncio
    asyncio.run(ingest_dossier("252"))
