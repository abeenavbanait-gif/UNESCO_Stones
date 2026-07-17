import time
import logging
import wikipedia
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from data_manager import load_monument_data
from custom_rag_pipeline import get_custom_vectorstore

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def ingest_all_wikipedia_sites():
    # Set a custom user agent to prevent Wikipedia API from rejecting our requests
    wikipedia.set_user_agent('UNESCOHeritageStonesBot/1.0 (contact@example.com)')
    
    print("==========================================================")
    print("🌍 UNESCO Heritage Stones - Wikipedia Batch Ingestion 🌍")
    print("==========================================================")
    print("This script will search Wikipedia for all 900+ sites, download")
    print("their full text content, and embed them into the local ChromaDB.\n")
    
    # 1. Load the database of sites
    logger.info("Loading monument data...")
    df = load_monument_data()
    if df.empty:
        logger.error("Failed to load monument data. Make sure the dataset is available.")
        return
        
    site_names = df['site_name'].dropna().unique().tolist()
    total_sites = len(site_names)
    logger.info(f"Found {total_sites} unique sites to process.")
    
    # 2. Setup Vector Store and Text Splitter
    vectorstore = get_custom_vectorstore()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    success_count = 0
    fail_count = 0
    
    # 3. Iterate through all sites
    for idx, site in enumerate(site_names):
        progress = f"[{idx + 1}/{total_sites}]"
        logger.info(f"{progress} Processing: {site}")
        
        try:
            # First try exact match, no auto suggest
            page = wikipedia.page(site, auto_suggest=False)
            content = page.content
        except wikipedia.exceptions.DisambiguationError as e:
            # If disambiguation, just take the first option
            try:
                page = wikipedia.page(e.options[0], auto_suggest=False)
                content = page.content
            except Exception:
                logger.warning(f"{progress} Disambiguation failed for {site}. Skipping.")
                fail_count += 1
                continue
        except wikipedia.exceptions.PageError:
            # If not found, try with auto_suggest enabled
            try:
                page = wikipedia.page(site, auto_suggest=True)
                content = page.content
            except Exception:
                logger.warning(f"{progress} Page not found for {site}. Skipping.")
                fail_count += 1
                continue
        except Exception as e:
            logger.error(f"{progress} Unexpected error searching for {site}: {e}")
            fail_count += 1
            # Sleep extra on API errors
            time.sleep(5)
            continue
            
        if not content.strip():
            logger.warning(f"{progress} Page content is empty for {site}.")
            fail_count += 1
            continue
            
        # Create a document out of the Wikipedia content
        # Add metadata so the RAG knows where it came from
        doc = Document(
            page_content=content,
            metadata={"source": f"Wikipedia - {page.title} (UNESCO Site: {site})"}
        )
        
        # Split into chunks
        splits = text_splitter.split_documents([doc])
        
        # Add to ChromaDB
        if splits:
            vectorstore.add_documents(documents=splits)
            logger.info(f"{progress} ✅ Successfully ingested {len(splits)} chunks for {page.title}.")
            success_count += 1
        else:
            logger.warning(f"{progress} No valid chunks created for {site}.")
            fail_count += 1
            
        # Sleep for 1.5 seconds to prevent rate limiting from Wikipedia
        time.sleep(1.5)
        
    print("\n==========================================================")
    print("✅ BATCH INGESTION COMPLETE")
    print("==========================================================")
    print(f"Total Sites Attempted: {total_sites}")
    print(f"Successfully Ingested: {success_count}")
    print(f"Failed / Not Found: {fail_count}")
    print("You can now query these sites in the Custom Document Chatbot!")

if __name__ == "__main__":
    ingest_all_wikipedia_sites()
