import os
import subprocess
import sys

def main():
    print("=========================================================")
    print("🏛️ UNESCO Heritage Stones - Offline MinerU PDF Parser 🏛️")
    print("=========================================================")
    print("This script uses MinerU (magic-pdf) to parse messy, scanned")
    print("UNESCO PDFs into perfectly structured Markdown files using AI.")
    print("You can then upload these clean .md files to the Streamlit app.\n")
    
    # Check if mineru is installed
    try:
        subprocess.run(["mineru", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except FileNotFoundError:
        print("❌ MinerU is not installed on your system.")
        print("To install it, please run the following command in your terminal:")
        print("    pip install magic-pdf[full]")
        print("\nNote: This will download several gigabytes of AI models (PaddleOCR, LayoutLMv3, etc.).")
        print("Please ensure you have at least 16GB of RAM before running this.")
        sys.exit(1)
    
    input_dir = "data/dossiers"
    output_dir = "data/markdown_dossiers"
    
    # Ensure directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if there are PDFs to process
    pdfs = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not pdfs:
        print(f"⚠️ No PDFs found in '{input_dir}'.")
        print("Please place your UNESCO PDFs in this folder and run the script again.")
        sys.exit(0)
        
    print(f"✅ Found {len(pdfs)} PDFs in '{input_dir}'.")
    print(f"🚀 Starting MinerU batch processing. Output will be saved to '{output_dir}'.")
    print("⏳ This may take a while depending on your CPU/GPU and document length...\n")
    
    # Run the mineru CLI command on the directory
    # -m auto will automatically use OCR for scanned documents
    try:
        subprocess.run([
            "mineru", 
            "-p", input_dir, 
            "-o", output_dir, 
            "-m", "auto"
        ], check=True)
        print("\n🎉 Batch processing complete!")
        print(f"Check the '{output_dir}' folder for your clean Markdown files.")
        print("You can now upload these .md files directly into the Custom Document Chatbot in the app!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ An error occurred while running MinerU: {e}")

if __name__ == "__main__":
    main()
