# Universal Document RAG (Replaces GraphRAG)

I have successfully replaced the complex, API-heavy GraphRAG with a fast, efficient, and robust Universal Document RAG chatbot. 

## What changed?

1. **GraphRAG Removed:** The old section 6 which required expensive Gemini API calls just to parse a PDF has been completely removed.
2. **Universal RAG Added:** In its place is a new Section 6 that allows you to upload standard documents you might find on UNESCO's website. 
3. **Local Embedding:** The heavy lifting of chunking and mapping documents to a vector database now happens 100% locally using an open-source model (`all-MiniLM-L6-v2`) and ChromaDB.

## Supported File Formats

You can now upload any of the following documents downloaded from the UNESCO document tab (e.g., from [https://whc.unesco.org/en/list/252/documents/](https://whc.unesco.org/en/list/252/documents/)):
- `📄 .pdf` (Official Dossiers)
- `📝 .docx` (Word Documents)
- `📊 .xlsx` (Excel Spreadsheets)
- `📈 .csv` (Data Tables)
- `🧾 .txt` (Raw Text)

## How to use it

1. Scroll to the bottom of the Streamlit app to the new **📚 Custom Document Chatbot (RAG)** section.
2. Upload one or more documents from your computer.
3. Click **🏗️ Ingest Document into Database**. The app will automatically slice the document into readable chunks, extract the text, and save it to the local vector database.
4. Enter your query (e.g. *"What are the conservation materials mentioned in the word document?"*) and click **Ask Document AI**. 

> [!TIP]
> The app still uses your free Gemini API key to formulate the final English answer, but because it only sends the 5 most relevant paragraphs (instead of the whole document), it is incredibly fast and avoids rate limits entirely!
