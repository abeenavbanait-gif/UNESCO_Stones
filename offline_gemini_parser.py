import os
import time
import base64
import fitz  # PyMuPDF
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("==========================================================")
    print("☁️ UNESCO Heritage Stones - Lightweight Gemini Parser ☁️")
    print("==========================================================")
    print("This script uses your Gemini API key to parse messy, scanned")
    print("UNESCO PDFs in the cloud. Your laptop does NO heavy lifting!\n")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable is not set.")
        print("Please export it before running, e.g.:")
        print("    export GEMINI_API_KEY='your_api_key'")
        return
        
    input_dir = "data/dossiers"
    output_dir = "data/markdown_dossiers"
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    pdfs = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not pdfs:
        print(f"⚠️ No PDFs found in '{input_dir}'.")
        return
        
    print(f"✅ Found {len(pdfs)} PDFs in '{input_dir}'.")
    
    # Initialize Gemini 1.5 Flash (extremely fast and cheap)
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.1
    )
    
    prompt_text = (
        "You are an expert OCR and document parsing AI. "
        "Extract all the text from this page and format it beautifully in Markdown. "
        "Preserve tables, headings, and lists exactly as they appear. "
        "If the page is blank or only contains an image with no text, output nothing."
    )
    
    for pdf_file in pdfs:
        pdf_path = os.path.join(input_dir, pdf_file)
        md_filename = os.path.splitext(pdf_file)[0] + ".md"
        output_path = os.path.join(output_dir, md_filename)
        
        # Skip if already processed
        if os.path.exists(output_path):
            logger.info(f"⏭️ Skipping {pdf_file}, already processed.")
            continue
            
        logger.info(f"📄 Processing: {pdf_file}")
        
        try:
            doc = fitz.open(pdf_path)
            full_markdown = []
            
            for page_num in range(len(doc)):
                logger.info(f"  -> Uploading page {page_num + 1}/{len(doc)}")
                
                # Render page to an image (72 dpi is fine for OCR, 150 is better for blurry scans)
                pix = doc[page_num].get_pixmap(dpi=150)
                img_bytes = pix.tobytes("jpeg")
                b64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                # Construct the multimodal message
                message = HumanMessage(
                    content=[
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                    ]
                )
                
                try:
                    response = llm.invoke([message])
                    if response.content and response.content.strip():
                        full_markdown.append(f"<!-- Page {page_num + 1} -->\n{response.content.strip()}\n")
                except Exception as api_err:
                    logger.error(f"  -> Error on page {page_num + 1}: {api_err}")
                    
                # The Gemini Free Tier allows 15 Requests Per Minute (1 every 4 seconds)
                # Sleep for 5 seconds to guarantee we stay under the limit
                time.sleep(5)
                
            # Save the accumulated Markdown to a file
            if full_markdown:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(full_markdown))
                logger.info(f"✅ Saved clean Markdown to {output_path}")
            else:
                logger.warning(f"⚠️ No text could be extracted from {pdf_file}")
                
        except Exception as e:
            logger.error(f"❌ Failed to process {pdf_file}: {e}")
            
    print("\n🎉 Batch processing complete!")
    print("You can now upload these .md files directly into the Custom Document Chatbot in the app!")

if __name__ == "__main__":
    main()
