import asyncio
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import logging
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import urllib3
import datetime
import os

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from unesco_fetcher import create_stealth_browser
from classify_monuments import classify_site  # Re-use v1 logic

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def fetch_site_details(page, site_id):
    url = f'https://whc.unesco.org/en/list/{site_id}'
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        ouv_content = []
        ouv_div = soup.find('div', id='ouv')
        if ouv_div:
            for p in ouv_div.find_all('p'):
                text = p.get_text(strip=True)
                if text:
                    ouv_content.append(text)
        
        if not ouv_content:
            headers = soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
            for header in headers:
                if 'Outstanding Universal Value' in header.get_text() or 'Justification for Inscription' in header.get_text():
                    curr = header.find_next_sibling()
                    while curr and curr.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
                        text = curr.get_text(separator='\n\n', strip=True)
                        if text:
                            ouv_content.append(text)
                        curr = curr.find_next_sibling()
                    break
        
        brief_desc = ""
        brief_div = soup.find('div', id='contentdes_en')
        if brief_div:
            brief_desc = brief_div.get_text(separator='\n', strip=True)
            
        ouv_statement = "\n\n".join(ouv_content)
        if not ouv_statement or len(ouv_statement.strip()) < 10:
            if brief_desc:
                ouv_statement = brief_desc
            else:
                ouv_statement = "MISSING_ON_WEBSITE"
            
        return brief_desc, ouv_statement
    except Exception as e:
        logger.warning(f"Failed to fetch details for {site_id}: {e}")
        return "", ""

async def main():
    logger.info("Fetching live XML feed...")
    url = 'https://whc.unesco.org/en/list/xml/'
    response = requests.get(url, verify=False)
    tree = ET.fromstring(response.content)

    new_sites = []
    old_df = pd.read_csv('Imp Data/972-sites_cultural_sites_classified.csv')
    old_ids = set(old_df['unesco_id'].astype(str))

    for row in tree.findall('row'):
        cat_node = row.find('category')
        cat = cat_node.text if cat_node is not None else ''
        if cat == 'Cultural':
            id_node = row.find('id_number')
            site_id = id_node.text if id_node is not None else ''
            
            if site_id and str(site_id) not in old_ids:
                site_data = {
                    'unesco_id': site_id,
                    'site_name': row.find('site').text if row.find('site') is not None else '',
                    'country': row.find('states').text if row.find('states') is not None else '',
                    'region': row.find('region').text if row.find('region') is not None else '',
                    'year_inscribed': row.find('date_inscribed').text if row.find('date_inscribed') is not None else '',
                    'category': cat,
                    'latitude': row.find('latitude').text if row.find('latitude') is not None else '',
                    'longitude': row.find('longitude').text if row.find('longitude') is not None else '',
                    'is_endangered': '1' if row.find('danger') is not None and row.find('danger').text else '0',
                    'is_transnational': '1' if row.find('transnational') is not None and row.find('transnational').text == '1' else '0',
                    'iso_code': row.find('iso_code').text if row.find('iso_code') is not None else '',
                    'unesco_url': f'https://whc.unesco.org/en/list/{site_id}',
                    'brief_description': '',
                    'ouv_statement': '',
                    'date_fetched': datetime.date.today().isoformat(),
                    'date_of_inscription': row.find('date_inscribed').text if row.find('date_inscribed') is not None else '',
                    'criteria': row.find('criteria_txt').text if row.find('criteria_txt') is not None else '',
                    'property_size': '',
                    'buffer_zone_size': '',
                    'dossier': ''
                }
                new_sites.append(site_data)

    logger.info(f"Found {len(new_sites)} new cultural sites.")
    
    if not new_sites:
        logger.info("No new sites to process.")
        return

    logger.info("Starting browser to scrape OUV and Brief Descriptions...")
    async with async_playwright() as p:
        browser, context, page = await create_stealth_browser(p)
        
        for idx, site in enumerate(new_sites):
            logger.info(f"[{idx+1}/{len(new_sites)}] Scraping site {site['unesco_id']} - {site['site_name']}")
            brief_desc, ouv = await fetch_site_details(page, site['unesco_id'])
            site['brief_description'] = brief_desc
            site['ouv_statement'] = ouv
            await asyncio.sleep(2)  # Polite delay
            
        await browser.close()
        
    logger.info("Classifying new sites...")
    df_new = pd.DataFrame(new_sites)
    
    # Classify each row
    classified_results = []
    for idx, row in df_new.iterrows():
        classified_row = classify_site(row)
        # combine dictionaries
        combined = {**row.to_dict(), **classified_row.to_dict()}
        classified_results.append(combined)
        
    df_final = pd.DataFrame(classified_results)
    
    # Ensure column order matches exactly
    output_cols = [
        'unesco_id', 'site_name', 'country', 'region', 'year_inscribed',
        'category', 'latitude', 'longitude', 'is_endangered',
        'is_transnational', 'iso_code', 'unesco_url', 'brief_description',
        'ouv_statement', 'date_fetched', 'date_of_inscription', 'criteria',
        'property_size', 'buffer_zone_size', 'dossier', 'confidence', 'score',
        'stone_count', 'stone_types_found', 'stone_geological_class',
        'named_trade_stones', 'decorative_minerals_found',
        'building_materials_found', 'construction_terms_found',
        'architectural_elements_found', 'architecture_style_found',
        'construction_verbs_found', 'matched_categories', 'matched_name_keywords'
    ]
    
    # Add any missing columns from output_cols with empty strings
    for col in output_cols:
        if col not in df_final.columns:
            df_final[col] = ''
            
    df_final = df_final[output_cols]
    
    output_file = '17-new-sites_cultural_sites_classified.csv'
    df_final.to_csv(output_file, index=False)
    logger.info(f"Saved to {output_file}")
    
    combined_file = 'Imp Data/989-sites_cultural_sites_classified.csv'
    df_combined = pd.concat([old_df, df_final], ignore_index=True)
    df_combined.to_csv(combined_file, index=False)
    logger.info(f"Saved combined master file to {combined_file}")

if __name__ == '__main__':
    asyncio.run(main())
