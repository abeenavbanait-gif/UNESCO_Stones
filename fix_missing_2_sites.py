import pandas as pd
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import urllib3
import datetime

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from classify_monuments_v2 import classify_site_row
import spacy
import spacy
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

def fetch_details(site_id):
    url = f'https://whc.unesco.org/en/list/{site_id}'
    resp = requests.get(url, verify=False)
    soup = BeautifulSoup(resp.content, 'html.parser')
    
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

def main():
    print("Fetching XML...")
    url = 'https://whc.unesco.org/en/list/xml/'
    response = requests.get(url, verify=False)
    tree = ET.fromstring(response.content)

    all_sites = []
    missing_ids = {'1715', '1774'}
    missing_rows = []

    # Get all 1273 sites for master database
    for row in tree.findall('row'):
        site_id = str(row.find('id_number').text)
        cat_node = row.find('category')
        cat = cat_node.text if cat_node is not None else ''
        
        site_data = {
            'id': site_id,
            'name': row.find('site').text if row.find('site') is not None else '',
            'category': cat,
            'region': row.find('region').text if row.find('region') is not None else '',
            'latitude': row.find('latitude').text if row.find('latitude') is not None else '',
            'longitude': row.find('longitude').text if row.find('longitude') is not None else '',
            'is_endangered': '1' if row.find('danger') is not None and row.find('danger').text else '0',
            'is_transnational': '1' if row.find('transnational') is not None and row.find('transnational').text == '1' else '0',
            'iso_code': row.find('iso_code').text if row.find('iso_code') is not None else '',
            'date_inscribed': row.find('date_inscribed').text if row.find('date_inscribed') is not None else ''
        }
        all_sites.append(site_data)
        
        if site_id in missing_ids:
            missing_rows.append(row)

    print(f"Total sites in XML: {len(all_sites)}")
    
    # 1. Update master database with TRUE 1273 sites
    master_df = pd.DataFrame(all_sites)
    master_df.to_csv('Imp Data/unesco_whs_master_database.csv', index=False)
    print("Updated unesco_whs_master_database.csv with 1273 accurate rows.")

    # 2. Process missing 2 sites
    new_cultural = []
    for row in missing_rows:
        site_id = str(row.find('id_number').text)
        print(f"Processing missing site {site_id}...")
        brief, ouv = fetch_details(site_id)
        
        site_data = {
            'unesco_id': site_id,
            'site_name': row.find('site').text if row.find('site') is not None else '',
            'country': row.find('states').text if row.find('states') is not None else '',
            'region': row.find('region').text if row.find('region') is not None else '',
            'year_inscribed': row.find('date_inscribed').text if row.find('date_inscribed') is not None else '',
            'category': row.find('category').text if row.find('category') is not None else '',
            'latitude': row.find('latitude').text if row.find('latitude') is not None else '',
            'longitude': row.find('longitude').text if row.find('longitude') is not None else '',
            'is_endangered': '1' if row.find('danger') is not None and row.find('danger').text else '0',
            'is_transnational': '1' if row.find('transnational') is not None and row.find('transnational').text == '1' else '0',
            'iso_code': row.find('iso_code').text if row.find('iso_code') is not None else '',
            'unesco_url': f'https://whc.unesco.org/en/list/{site_id}',
            'brief_description': brief,
            'ouv_statement': ouv,
            'date_fetched': datetime.date.today().isoformat(),
            'date_of_inscription': row.find('date_inscribed').text if row.find('date_inscribed') is not None else '',
            'criteria': row.find('criteria_txt').text if row.find('criteria_txt') is not None else '',
            'property_size': '',
            'buffer_zone_size': '',
            'dossier': ''
        }
        
        # Classify
        site_series = pd.Series(site_data)
        text_to_lemmatize = str(site_series.get('brief_description', '')) + " " + str(site_series.get('ouv_statement', ''))
        lemmatized_text = " ".join([token.lemma_ for token in nlp(text_to_lemmatize)])
        site_name_lemmatized = " ".join([token.lemma_ for token in nlp(str(site_series.get('site_name', '')))])
        classified_series = classify_site_row(site_series, lemmatized_text, site_name_lemmatized)
        
        # Merge
        combined = {**site_data, **classified_series}
        new_cultural.append(combined)

    new_cultural_df = pd.DataFrame(new_cultural)
    
    # 3. Append to Live_Manual_Data
    manual_df = pd.read_csv('Imp Data/Live_Manual_Data.csv')
    
    new_manual_rows = []
    for _, row in new_cultural_df.iterrows():
        new_row = {col: '' for col in manual_df.columns}
        new_row['Site ID'] = row['unesco_id']
        new_row['Site Name'] = row['site_name']
        new_row['Country'] = row['country']
        # safe_id format: e.g. 1715_GdyniaModernistCityCentre
        import re
        safe_name = re.sub(r'[^A-Za-z0-9]', '', str(row['site_name']))
        new_row['safe_id'] = f"{row['unesco_id']}_{safe_name}"
        new_row['Index'] = len(manual_df) + len(new_manual_rows)
        new_row['UNESCO Criteria'] = row['criteria']
        new_manual_rows.append(new_row)
        
    manual_df = pd.concat([manual_df, pd.DataFrame(new_manual_rows)], ignore_index=True)
    manual_df.to_csv('Imp Data/Live_Manual_Data.csv', index=False)
    print("Appended 2 missing sites to Live_Manual_Data.csv.")
    
    # 4. Append to rescanned_built_geological_monuments.csv
    rescanned_df = pd.read_csv('re-scan/rescanned_built_geological_monuments.csv')
    
    # Ensure column order
    for col in rescanned_df.columns:
        if col not in new_cultural_df.columns:
            new_cultural_df[col] = ''
    new_cultural_df = new_cultural_df[rescanned_df.columns]
    
    rescanned_df = pd.concat([rescanned_df, new_cultural_df], ignore_index=True)
    rescanned_df.to_csv('re-scan/rescanned_built_geological_monuments.csv', index=False)
    print("Appended 2 missing sites to rescanned_built_geological_monuments.csv.")
    print("Done!")

if __name__ == '__main__':
    main()
