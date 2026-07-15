import os
import networkx as nx
import pickle
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
import fitz # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GRAPH_PATH = "data/custom_graph.pkl"

def get_llm(api_key):
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=api_key,
        temperature=0.1
    )

def ingest_custom_pdf_graph(pdf_bytes, api_key):
    """
    Parses a PDF byte stream, chunks it, and uses Gemini to extract a Knowledge Graph.
    Saves the graph to a local pickle file.
    """
    logger.info("Extracting text from uploaded PDF...")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    
    if not text.strip():
        raise ValueError("Could not extract any text from the PDF.")

    logger.info("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len
    )
    
    # Create LangChain Document objects
    chunks = text_splitter.split_text(text)
    documents = [Document(page_content=chunk) for chunk in chunks]
    
    logger.info(f"Extracting graph nodes and edges from {len(documents)} chunks using Gemini...")
    llm = get_llm(api_key)
    llm_transformer = LLMGraphTransformer(llm=llm)
    
    # Process in batches or all at once (might hit rate limits if document is huge, but we'll try all at once for simplicity)
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    
    logger.info("Building NetworkX graph...")
    G = nx.Graph()
    for g_doc in graph_documents:
        for node in g_doc.nodes:
            G.add_node(node.id, type=node.type)
        for rel in g_doc.relationships:
            G.add_edge(rel.source.id, rel.target.id, type=rel.type)
            
    logger.info(f"Graph built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
    
    # Save graph
    os.makedirs(os.path.dirname(GRAPH_PATH), exist_ok=True)
    with open(GRAPH_PATH, "wb") as f:
        pickle.dump(G, f)
        
    return G.number_of_nodes(), G.number_of_edges()

def ask_graph_question(question, api_key):
    """
    Answers a question by querying the NetworkX graph for relevant relations.
    """
    if not os.path.exists(GRAPH_PATH):
        raise FileNotFoundError("Knowledge graph not found. Please upload and process a document first.")
        
    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)
        
    llm = get_llm(api_key)
    
    # Step 1: Ask LLM to extract key entities from the user's question
    logger.info("Extracting entities from question...")
    extraction_prompt = f"Extract the key entities (names, places, materials, concepts) from this question as a comma-separated list. Question: '{question}'"
    response = llm.invoke([HumanMessage(content=extraction_prompt)])
    entities_str = response.content
    extracted_entities = [e.strip() for e in entities_str.split(',')]
    
    # Step 2: Search for these entities in the Graph and pull their 1-hop neighborhoods
    logger.info(f"Searching graph for entities: {extracted_entities}")
    graph_context = "Knowledge Graph Relations:\n"
    found_any = False
    
    # We do a case-insensitive search through graph nodes
    node_names_lower = {str(n).lower(): n for n in G.nodes()}
    
    for entity in extracted_entities:
        entity_lower = entity.lower()
        # Find best matching node
        matched_node = None
        for n_lower, original_n in node_names_lower.items():
            if entity_lower in n_lower or n_lower in entity_lower:
                matched_node = original_n
                break
                
        if matched_node:
            found_any = True
            neighbors = list(G.neighbors(matched_node))
            for neighbor in neighbors:
                edge_data = G.get_edge_data(matched_node, neighbor)
                edge_type = edge_data.get("type", "related to")
                graph_context += f"- {matched_node} -> {edge_type} -> {neighbor}\n"
                
    if not found_any:
        graph_context += "No direct graph relations found for these entities.\n"
        
    # Step 3: Generate the final answer using the Graph Context
    logger.info("Generating final answer...")
    system_prompt = (
        "You are an expert architectural historian assistant.\n"
        "You have been provided with structured relationships extracted from a Knowledge Graph.\n"
        "Use ONLY this provided context to answer the user's question. If the context does not contain the answer, say you don't know.\n"
        "Context:\n"
        f"{graph_context}"
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    
    final_response = llm.invoke(messages)
    return final_response.content, graph_context
