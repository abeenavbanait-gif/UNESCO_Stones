import pandas as pd
import os
import json

# Attempt to load from JSON
with open("data/unesco_master_list.json", "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)

# Create new dataframe
template_df = pd.DataFrame()
template_df['Index'] = range(1, len(df) + 1)
template_df['Site ID'] = df['unesco_id']
template_df['Site Name'] = df['site_name']
template_df['Country'] = df['country']

# A. Monument Information
template_df['Architecture Type'] = ""
template_df['Construction Period'] = ""
template_df['Civilization'] = ""
template_df['UNESCO Criteria'] = df.get('criteria', '')

# B. Geological Materials
template_df['Mentioned Major Stone(s)'] = ""
template_df['Secondary Stone'] = ""
template_df['Local Stone Name'] = ""
template_df['Lithology'] = ""
template_df['Geological Age'] = ""
template_df['Formation'] = ""
template_df['Colour'] = ""
template_df['Texture'] = ""
template_df['Minerals'] = ""

# C. Provenance
template_df['Quarry'] = ""
template_df['Quarry Country'] = ""
template_df['Local vs Imported'] = ""
template_df['Transport Distance'] = ""

# D. Architectural Use
template_df['Structural Use'] = ""
template_df['Decorative Use'] = ""
template_df['Masonry Technique'] = ""

# E. Conservation
template_df['Weathering'] = ""
template_df['Replacement Stone'] = ""
template_df['Restoration'] = ""
template_df['Condition'] = ""

# F. Heritage Stone
template_df['GHSR'] = ""
template_df['Heritage Stone Candidate'] = ""
template_df['Geoheritage Value'] = ""

# G. Sources
template_df['UNESCO Mention'] = ""
template_df['Wikipedia Mention'] = ""
template_df['Research Papers'] = ""
template_df['Confidence Score'] = ""

template_df.to_csv("UNESCO_Stones_Blank_Template.csv", index=False)
print("Successfully generated UNESCO_Stones_Blank_Template.csv")
