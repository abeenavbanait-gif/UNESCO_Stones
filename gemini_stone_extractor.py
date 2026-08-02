"""
gemini_stone_extractor.py — Heritage Stones Extraction Pipeline (v2)
=====================================================================
Uses Google Gemini 3.5 Flash via the modern google.genai SDK to extract
structured geological, provenance, architectural use, and conservation
data from UNESCO cultural site OUV statements.

Features:
  - Processes sites where stone_count > 0 (951 sites)
  - Prompts for Gemini API key
  - Resume support: skips already-processed sites
  - Rate limiting with exponential backoff
  - Progress tracking with ETA
  - Robust JSON parsing with truncation recovery
"""

import os
import sys
import csv
import json
import time
import getpass
import logging
import re
from pathlib import Path
from datetime import datetime

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
INPUT_CSV = BASE_DIR / "972-sites_cultural_sites_classified.csv"
OUTPUT_CSV = BASE_DIR / "heritage_stones_extracted.csv"
OUTPUT_EXCEL = BASE_DIR / "heritage_stones_extracted.xlsx"
ERROR_LOG = BASE_DIR / "extraction_errors.log"

# ── Config ─────────────────────────────────────────────────────────────────
MODEL_NAME = "gemini-2.5-flash"

DELAY_BETWEEN_CALLS = 6   # seconds delay to comfortably handle API rate limits
MAX_RETRIES = 3
BATCH_SAVE_INTERVAL = 1   # save to CSV/Excel after every site



# ── Output CSV columns ────────────────────────────────────────────────────
OUTPUT_COLUMNS = [
    # Identifiers (from input)
    "unesco_id", "site_name", "country", "region", "year_inscribed",
    "latitude", "longitude", "unesco_url",
    # A. Monument Information
    "architecture_type", "architecture_type_ref",
    "construction_period", "construction_period_ref",
    "civilization", "civilization_ref",
    "unesco_criteria", "unesco_criteria_ref",
    # B. Geological Materials
    "major_stones", "major_stones_ref",
    "rock_class", "rock_class_ref",
    "secondary_stones", "secondary_stones_ref",
    "local_stone_name", "local_stone_name_ref",
    "lithology", "lithology_ref",
    "geological_age", "geological_age_ref",
    "formation", "formation_ref",
    "colour", "colour_ref",
    "texture", "texture_ref",
    "minerals", "minerals_ref",
    # C. Provenance
    "quarry", "quarry_ref",
    "quarry_country", "quarry_country_ref",
    "local_vs_imported", "local_vs_imported_ref",
    "transport_distance", "transport_distance_ref",
    # D. Architectural Use
    "structural_use", "structural_use_ref",
    "decorative_use", "decorative_use_ref",
    "masonry_technique", "masonry_technique_ref",
    # E. Conservation
    "weathering", "weathering_ref",
    "replacement_stone", "replacement_stone_ref",
    "restoration", "restoration_ref",
    "condition", "condition_ref",
    # F. Sources
    "unesco_mention",
]

# ── JSON field keys we expect from Gemini ─────────────────────────────────
EXTRACTED_FIELDS = [
    "architecture_type", "architecture_type_ref",
    "construction_period", "construction_period_ref",
    "civilization", "civilization_ref",
    "major_stones", "major_stones_ref",
    "rock_class", "rock_class_ref",
    "secondary_stones", "secondary_stones_ref",
    "local_stone_name", "local_stone_name_ref",
    "lithology", "lithology_ref",
    "geological_age", "geological_age_ref",
    "formation", "formation_ref",
    "colour", "colour_ref",
    "texture", "texture_ref",
    "minerals", "minerals_ref",
    "quarry", "quarry_ref",
    "quarry_country", "quarry_country_ref",
    "local_vs_imported", "local_vs_imported_ref",
    "transport_distance", "transport_distance_ref",
    "structural_use", "structural_use_ref",
    "decorative_use", "decorative_use_ref",
    "masonry_technique", "masonry_technique_ref",
    "weathering", "weathering_ref",
    "replacement_stone", "replacement_stone_ref",
    "restoration", "restoration_ref",
    "condition", "condition_ref",
    "unesco_mention",
]

# ── The Extraction Prompt (optimized for shorter output) ──────────────────

EXTRACTION_PROMPT = """You are an expert geologist and architectural historian specializing in heritage building stones.

Analyze the UNESCO World Heritage Site info below and extract geological, provenance, architectural use, and conservation details about stones/geological materials.

**SITE**: {site_name} | **COUNTRY**: {country} | **YEAR**: {year_inscribed}
**Known stones**: {stone_types_found}
**Geological class**: {stone_geological_class}
**Trade stones**: {named_trade_stones}
**Minerals**: {decorative_minerals_found}
**Materials**: {building_materials_found}
**Construction**: {construction_terms_found}
**Elements**: {architectural_elements_found}

**TEXT**:
{ouv_text}

---
RULES:
1. Extract ONLY from the text above. Do NOT invent data.
2. For "ref" fields: give a SHORT phrase (max 15 words) from the text as evidence. NOT the full sentence.
3. CRITICAL: If NO specific stone or geological material is mentioned in the site description and OUV statement, set "unesco_mention" to "Not mentioned in UNESCO Site", set "major_stones" to "Not mentioned in UNESCO Site", and set other unmentioned fields to "Not mentioned in UNESCO Site".
4. If a specific field (like quarry or texture) is not mentioned for a stone site, set its value and ref to "Not mentioned in UNESCO Site".
5. "condition": must be one of Good, Fair, Poor, Critical, or Not mentioned in UNESCO Site.
6. "unesco_mention": "Yes" if stone/geological material is mentioned, otherwise "Not mentioned in UNESCO Site".
7. Return ONLY valid JSON, no markdown, no code fences.

Return this exact JSON structure:
{{"architecture_type":"","architecture_type_ref":"","construction_period":"","construction_period_ref":"","civilization":"","civilization_ref":"","major_stones":"","major_stones_ref":"","rock_class":"","rock_class_ref":"","secondary_stones":"","secondary_stones_ref":"","local_stone_name":"","local_stone_name_ref":"","lithology":"","lithology_ref":"","geological_age":"","geological_age_ref":"","formation":"","formation_ref":"","colour":"","colour_ref":"","texture":"","texture_ref":"","minerals":"","minerals_ref":"","quarry":"","quarry_ref":"","quarry_country":"","quarry_country_ref":"","local_vs_imported":"","local_vs_imported_ref":"","transport_distance":"","transport_distance_ref":"","structural_use":"","structural_use_ref":"","decorative_use":"","decorative_use_ref":"","masonry_technique":"","masonry_technique_ref":"","weathering":"","weathering_ref":"","replacement_stone":"","replacement_stone_ref":"","restoration":"","restoration_ref":"","condition":"","condition_ref":"","unesco_mention":""}}"""


def get_api_key():
    """Get API key from environment variable or prompt user."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        logger.info("🔑 Using GEMINI_API_KEY from environment.")
        return api_key
    print("\n" + "=" * 60)
    print("🔑  Google Gemini API Key Required")
    print("=" * 60)
    api_key = input("Paste your Gemini API key and press Enter: ").strip()
    if not api_key:
        print("❌ No API key provided. Exiting.")
        sys.exit(1)
    return api_key



def init_gemini(api_key):
    """Initialize the Gemini client using the modern google.genai SDK."""
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        # Quick test
        logger.info(f"Testing connection to {MODEL_NAME}...")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="Say OK",
        )
        if response and response.text:
            logger.info(f"✅ Gemini {MODEL_NAME} connected successfully.")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini: {e}")
        sys.exit(1)


def load_input_csv():
    """Load all sites from the input CSV."""
    if not INPUT_CSV.exists():
        logger.error(f"❌ Input CSV not found: {INPUT_CSV}")
        sys.exit(1)

    sites = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sites.append(row)

    logger.info(f"📋 Loaded all {len(sites)} cultural sites from {INPUT_CSV.name}")
    return sites



def load_processed_ids():
    """Load already-processed UNESCO IDs for resume support."""
    processed = set()
    if OUTPUT_CSV.exists():
        try:
            with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    uid = row.get("unesco_id", "").strip()
                    if uid:
                        processed.add(uid)
            logger.info(f"🔄 Resume: {len(processed)} sites already done, skipping them.")
        except Exception:
            pass
    return processed


def build_ouv_text(row):
    """Combine brief_description and ouv_statement, truncate if very long."""
    parts = []
    bd = row.get("brief_description", "").strip()
    ouv = row.get("ouv_statement", "").strip()
    if bd:
        parts.append(bd)
    if ouv:
        parts.append(ouv)
    text = "\n\n".join(parts) if parts else "No description available."
    # Truncate extremely long texts to ~8000 chars to stay within token limits
    if len(text) > 8000:
        text = text[:8000] + "\n[...truncated...]"
    return text


def call_gemini(client, prompt, retries=MAX_RETRIES):
    """Call Gemini API with retries and exponential backoff."""
    from google.genai import types

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=8192,
                    response_mime_type="application/json",
                ),
            )
            if response and response.text:
                return response.text
            else:
                logger.warning(f"  ⚠️ Empty response (attempt {attempt + 1})")
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                wait = (2 ** attempt) * 15  # 15, 30, 60 seconds
                logger.warning(f"  ⏳ Rate limited. Waiting {wait}s (retry {attempt + 1}/{retries})...")
                time.sleep(wait)
            elif "500" in error_str or "503" in error_str:
                wait = (2 ** attempt) * 5
                logger.warning(f"  🔄 Server error. Waiting {wait}s (retry {attempt + 1}/{retries})...")
                time.sleep(wait)
            else:
                logger.error(f"  ❌ API error: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                else:
                    return None
    return None


def parse_json_response(raw_text):
    """Parse JSON from Gemini response with robust error handling."""
    if not raw_text:
        return None

    text = raw_text.strip()

    # Remove markdown code fences if present
    if text.startswith("```"):
        first_newline = text.index("\n") if "\n" in text else len(text)
        text = text[first_newline + 1:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object boundaries
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    # Try to fix truncated JSON by closing it
    if start != -1:
        fragment = text[start:]
        # Count unclosed braces/quotes and try to close them
        # Remove trailing incomplete key-value pair
        last_complete = fragment.rfind('",')
        if last_complete > 0:
            fragment = fragment[:last_complete + 1]
            # Close any unclosed strings/objects
            open_braces = fragment.count("{") - fragment.count("}")
            open_quotes = fragment.count('"') % 2
            if open_quotes:
                fragment += '"'
            fragment += "}" * open_braces
            try:
                return json.loads(fragment)
            except json.JSONDecodeError:
                pass

    logger.error(f"  ❌ Failed to parse JSON response")
    return None


def extract_site_data(client, row):
    """Extract structured data for a single site using Gemini."""
    site_name = row.get("site_name", "Unknown")
    ouv_text = build_ouv_text(row)

    prompt = EXTRACTION_PROMPT.format(
        site_name=site_name,
        country=row.get("country", ""),
        year_inscribed=row.get("year_inscribed", ""),
        stone_types_found=row.get("stone_types_found", ""),
        stone_geological_class=row.get("stone_geological_class", ""),
        named_trade_stones=row.get("named_trade_stones", ""),
        decorative_minerals_found=row.get("decorative_minerals_found", ""),
        building_materials_found=row.get("building_materials_found", ""),
        construction_terms_found=row.get("construction_terms_found", ""),
        architectural_elements_found=row.get("architectural_elements_found", ""),
        ouv_text=ouv_text
    )

    raw_response = call_gemini(client, prompt)
    parsed = parse_json_response(raw_response)

    if parsed is None:
        return None

    # Build output row
    result = {
        "unesco_id": row.get("unesco_id", ""),
        "site_name": site_name,
        "country": row.get("country", ""),
        "region": row.get("region", ""),
        "year_inscribed": row.get("year_inscribed", ""),
        "latitude": row.get("latitude", ""),
        "longitude": row.get("longitude", ""),
        "unesco_url": row.get("unesco_url", ""),
        "unesco_criteria": row.get("criteria", ""),
        "unesco_criteria_ref": "UNESCO OUV Statement",
    }

    for field in EXTRACTED_FIELDS:
        val = parsed.get(field, "Not mentioned in UNESCO Site")
        if val in ["Not mentioned", "None", "", None]:
            val = "Not mentioned in UNESCO Site"
        result[field] = val

    # Enforce clear unesco_mention status
    um = str(result.get("unesco_mention", "")).strip().lower()
    ms = str(result.get("major_stones", "")).strip()

    if um in ["no", "not mentioned", "not mentioned in unesco site"] or ms in ["Not mentioned in UNESCO Site", "Not mentioned", "None", ""]:
        if ms in ["Not mentioned in UNESCO Site", "Not mentioned", "None", ""]:
            result["unesco_mention"] = "Not mentioned in UNESCO Site"
        else:
            result["unesco_mention"] = "Yes" if um == "yes" else "Not mentioned in UNESCO Site"

    return result



def save_results(results, mode="a"):
    """Save results to CSV (UTF-8-SIG for Excel) and auto-generate XLSX."""
    file_exists = OUTPUT_CSV.exists() and mode == "a"

    with open(OUTPUT_CSV, mode, newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, extrasaction='ignore')
        if not file_exists or mode == "w":
            writer.writeheader()
        for row in results:
            writer.writerow(row)
        f.flush()

    # Also update Excel file (.xlsx) for easy double-click opening
    try:
        import pandas as pd
        df = pd.read_csv(OUTPUT_CSV, encoding="utf-8-sig")
        df.to_excel(OUTPUT_EXCEL, index=False)
    except Exception as ex:
        pass



def log_error(unesco_id, site_name, error_msg):
    """Log extraction errors."""
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] ID={unesco_id} | {site_name} | {error_msg}\n")


def format_eta(seconds):
    """Format seconds into human-readable time."""
    if seconds < 0:
        return "calculating..."
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def main():
    print("\n" + "=" * 60)
    print("🏛️  Heritage Stones — Gemini Extraction Pipeline v2")
    print("=" * 60)
    print(f"  Model:  {MODEL_NAME}")
    print(f"  Input:  {INPUT_CSV.name}")
    print(f"  Output: {OUTPUT_CSV.name}")
    print("=" * 60)

    # 1. Get API key
    api_key = get_api_key()

    # 2. Initialize Gemini
    client = init_gemini(api_key)

    # 3. Load input data
    sites = load_input_csv()
    if not sites:
        logger.error("No sites to process!")
        return

    # 4. Resume support
    processed_ids = load_processed_ids()
    remaining = [s for s in sites if s.get("unesco_id", "").strip() not in processed_ids]

    if not remaining:
        print("\n🎉 All sites have already been processed!")
        print(f"   Output: {OUTPUT_CSV}")
        return

    total = len(remaining)
    already_done = len(processed_ids)
    print(f"\n📊 Sites to process: {total} (already done: {already_done})")

    estimated_time = total * (DELAY_BETWEEN_CALLS + 3)
    print(f"⏱️  Estimated time: {format_eta(estimated_time)}")
    print()

    # 5. Process sites
    batch_buffer = []
    success_count = 0
    fail_count = 0
    start_time = time.time()

    for i, site in enumerate(remaining, 1):
        uid = site.get("unesco_id", "?")
        name = site.get("site_name", "Unknown")
        short_name = name[:55] + "..." if len(name) > 55 else name

        # Progress
        elapsed = time.time() - start_time
        if i > 1:
            rate = (i - 1) / elapsed
            eta = (total - i) / rate if rate > 0 else 0
        else:
            eta = estimated_time
        progress_pct = (i / total) * 100

        print(f"[{i}/{total}] ({progress_pct:.0f}%) ETA: {format_eta(eta)} | "
              f"ID={uid} | {short_name}")

        # Extract
        try:
            result = extract_site_data(client, site)
            if result:
                batch_buffer.append(result)
                success_count += 1
                stones = result.get('major_stones', 'N/A')
                mention = result.get('unesco_mention', '?')
                logger.info(f"  ✅ stones={stones[:50]} | mention={mention}")
            else:
                fail_count += 1
                log_error(uid, name, "Null response / parse failure")
                logger.warning(f"  ⚠️ Failed")
        except Exception as e:
            fail_count += 1
            log_error(uid, name, str(e))
            logger.error(f"  ❌ Error: {e}")

        # Batch save every N sites
        if len(batch_buffer) >= BATCH_SAVE_INTERVAL:
            save_results(batch_buffer, mode="a" if OUTPUT_CSV.exists() else "w")
            logger.info(f"  💾 Batch saved ({len(batch_buffer)} sites)")
            batch_buffer = []

        # Rate limiting
        if i < total:
            time.sleep(DELAY_BETWEEN_CALLS)

    # Save final batch
    if batch_buffer:
        save_results(batch_buffer, mode="a" if OUTPUT_CSV.exists() else "w")
        logger.info(f"💾 Final batch saved ({len(batch_buffer)} sites)")

    # Summary
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("🎉  EXTRACTION COMPLETE!")
    print("=" * 60)
    print(f"  ✅ Success:  {success_count}")
    print(f"  ❌ Failed:   {fail_count}")
    print(f"  ⏱️  Time:     {format_eta(total_time)}")
    print(f"  📄 Output:   {OUTPUT_CSV}")
    if fail_count > 0:
        print(f"  📋 Errors:   {ERROR_LOG}")
    print("=" * 60)


if __name__ == "__main__":
    main()
