# 🏛️ UNESCO Heritage Stones: Data Collection Guide

Welcome to the team! Your goal is to systematically build out our master database by analyzing the official UNESCO documents for various World Heritage Sites and extracting specific architectural and geological data. 

Because we are on a strict 24-hour deadline, you will be leveraging an AI-powered Document Assistant built directly into the app to rapidly scan hundreds of pages in seconds.

Please follow this exact procedure from start to finish.

---

## Step 1: App Setup & Navigation

1. **Open the App:** Launch the Streamlit application in your web browser.
2. **Add API Key:** Look at the left sidebar under **🤖 Gemini API Configuration**. You *must* enter a Google Gemini API Key to use the AI features. If you don't have one, click the link provided in the app to get a free key instantly.
3. **Navigate to the Explorer:** In the left sidebar under **🧭 Navigation**, select the **"🏛️ Site Explorer"** page.

## Step 2: Select a Site

1. Use the **🔍 Site Filters** in the sidebar to find the site you are assigned to. 
2. You can filter by Region, Country, or just use the **"Search Site Name"** box.
3. Select the site from the dropdown. The main page will now load all the details for this specific location.

## Step 3: Uploading Documents & Using AI (The Fast Way)

Reading a 300-page official UNESCO dossier manually will take hours. We will use the **Universal Document RAG** system to do this in seconds.

1. **Get the Document:** Go to the official UNESCO website for the site (e.g., `whc.unesco.org/en/list/[SiteID]/documents/`) and download the official dossier (usually a `.pdf` or `.docx`).
2. **Upload to App:** Scroll down in the app to the **📚 Custom Document Chatbot (RAG)** section.
3. **Ingest:** Upload the document you just downloaded and click **"🏗️ Ingest Document into Database"**. The app will quickly slice and read the document locally.
4. **Interrogate the AI:** Once ingested, use the **Ask Document AI** chat box. 
   * **Pro-Tip (Copy & Paste these prompts for speed):**
     * *"What specific building stones or rocks were used to construct this monument?"*
     * *"Are any quarries or geographical sources for the building materials mentioned?"*
     * *"What are the conservation or restoration materials mentioned?"*

## Step 4: ✍️ The Manual Data Entry Form

Now that you have the answers from the AI (and have verified them against the text), it's time to log the data.

1. Scroll to the **"✍️ Manual Data Entry Form"** section.
2. You will see several expandable categories (🏛️ A. Monument Information, 🪨 B. Geological Materials, 🗺️ C. Provenance, etc.).
3. Expand each section and fill in the fields based on your findings.
4. **🚨 CRITICAL RULE (Truthfulness):** You must be **100% truthful to the official UNESCO text**. If the AI or the document does *not* explicitly name the rock (e.g., it just says "white stone", not "Makrana marble"), you must write what the text says. **Do not guess or use outside knowledge.**
5. **Save:** Once you have filled out the form for the site, click the primary **"💾 Save Data to CSV"** button. 
6. *Verify:* You can click the **"👀 View Site Data"** button to double-check that your entry was saved correctly.

## ⚡ Speed Run Tips (Beating the 24-Hour Deadline)

* **Don't Read, Interrogate:** Trust the AI to find the mentions of "stone", "rock", "marble", "quarry", etc. Only read the specific paragraphs the AI quotes.
* **Batch Downloads:** Spend your first hour downloading the PDFs for all your assigned sites into a single folder on your desktop so you aren't constantly switching between the app and the UNESCO website.
* **Keep Prompts Handy:** Keep a Notepad open with your 3-4 best AI questions and just copy/paste them into the chat box for every new site.
* **Skip if Empty:** If the AI definitively tells you "There is no mention of building materials in this document," do a quick manual search (Ctrl+F for "stone"). If it's truly empty, leave the material fields blank, save the form, and move on immediately. Don't waste time looking for data that doesn't exist.

Good luck!
