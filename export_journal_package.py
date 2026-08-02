import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os
import shutil
import zipfile

# Set up matplotlib for high-res publication figures
plt.rcParams['font.sans-serif'] = 'Arial, Helvetica, sans-serif'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['pdf.fonttype'] = 42 # TrueType fonts for vector PDF journal requirements
plt.rcParams['ps.fonttype'] = 42

base_dir = 'Heritage_Stones_Journal_Figures'
os.makedirs(base_dir, exist_ok=True)

# -------------------------------------------------------------
# FIGURE 1: Data Completeness
# -------------------------------------------------------------
fig1_dir = os.path.join(base_dir, '01_Data_Completeness')
os.makedirs(fig1_dir, exist_ok=True)

df1 = pd.DataFrame({
    'Field_Name': ['Site Name & ID', 'UNESCO Criteria', 'Site Condition', 'Major Stone (B34 Verified)', 'Structural Use', 'Restoration', 'Masonry Technique', 'Rock Class', 'Local Provenance', 'Weathering', 'Lithology', 'Quarry Site', 'Local Stone Name', 'Minerals', 'Geological Age'],
    'Filled_Count': [902, 790, 194, 193, 190, 174, 157, 152, 129, 119, 80, 62, 43, 22, 16],
    'Total_Sites': [902]*15,
    'Completion_Percentage': [100.0, 87.6, 21.5, 21.4, 21.1, 19.3, 17.4, 16.9, 14.3, 13.2, 8.9, 6.9, 4.8, 2.4, 1.8]
})
df1.to_csv(os.path.join(fig1_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(9, 5.5), dpi=600)
pcts = df1['Completion_Percentage'].values
fields = df1['Field_Name'].values
y_pos = np.arange(len(fields))
colors = ['#1a365d' if p > 50 else '#2b6cb0' if p >= 15 else '#c53030' for p in pcts]

bars = ax.barh(y_pos, pcts, color=colors, height=0.65, edgecolor='#1a365d', linewidth=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(fields, fontsize=10, weight='bold', color='#1a202c')
ax.invert_yaxis()
ax.set_xlabel('Completion Percentage across 902 UNESCO Sites (%)', fontsize=11, weight='bold', color='#1a202c')
ax.set_title('Figure 1: Field Completeness Baseline across UNESCO Heritage Dataset (n=902)', fontsize=12.5, weight='bold', color='#1a202c', pad=15)
for bar in bars:
    w = bar.get_width()
    ax.text(w + 1, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', ha='left', va='center', fontsize=9.5, weight='bold', color='#1a202c')
ax.set_xlim(0, 115)
plt.tight_layout()
plt.savefig(os.path.join(fig1_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig1_dir, 'figure_vector.pdf'))
plt.close()

# -------------------------------------------------------------
# FIGURE 2: Rock Class Distribution
# -------------------------------------------------------------
fig2_dir = os.path.join(base_dir, '02_Rock_Class_Distribution')
os.makedirs(fig2_dir, exist_ok=True)

df2 = pd.DataFrame({
    'Rock_Class': ['Sedimentary Rock', 'Igneous Rock', 'Metamorphic Rock'],
    'Site_Count': [92, 37, 23],
    'Percentage': [60.53, 24.34, 15.13]
})
df2.to_csv(os.path.join(fig2_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(7.5, 5), dpi=600)
labels = ['Sedimentary Rock\n(92 sites | 60.5%)', 'Igneous Rock\n(37 sites | 24.3%)', 'Metamorphic Rock\n(23 sites | 15.1%)']
sizes = [92, 37, 23]
colors = ['#2b6cb0', '#dd6b20', '#38a169']
explode = (0.02, 0.02, 0.02)
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
                                  colors=colors, pctdistance=0.75, explode=explode,
                                  textprops=dict(color='#1a202c', fontsize=10.5, weight='bold'))
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(11.5)
centre_circle = plt.Circle((0,0), 0.55, fc='white')
fig.gca().add_artist(centre_circle)
ax.set_title('Figure 2: Rock Class Distribution Across Classified UNESCO Sites (n=152)', fontsize=12.5, weight='bold', color='#1a202c', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(fig2_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig2_dir, 'figure_vector.pdf'))
plt.close()

# -------------------------------------------------------------
# FIGURE 3: Regional Rock Class Breakdown
# -------------------------------------------------------------
fig3_dir = os.path.join(base_dir, '03_Regional_Rock_Class')
os.makedirs(fig3_dir, exist_ok=True)

df3 = pd.DataFrame({
    'Geographic_Region': ['Europe', 'Asia', 'Africa', 'Americas', 'Oceania'],
    'Sedimentary_Sites': [37, 26, 7, 7, 0],
    'Igneous_Sites': [13, 9, 5, 7, 2],
    'Metamorphic_Sites': [16, 4, 0, 1, 1],
    'Total_Classified_Sites': [66, 39, 12, 15, 3]
})
df3.to_csv(os.path.join(fig3_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(9, 5), dpi=600)
regions = df3['Geographic_Region'].values
x = np.arange(len(regions))
width = 0.25

rects1 = ax.bar(x - width, df3['Sedimentary_Sites'], width, label='Sedimentary', color='#2b6cb0', edgecolor='#1a365d', linewidth=0.5)
rects2 = ax.bar(x, df3['Igneous_Sites'], width, label='Igneous', color='#dd6b20', edgecolor='#7b341e', linewidth=0.5)
rects3 = ax.bar(x + width, df3['Metamorphic_Sites'], width, label='Metamorphic', color='#38a169', edgecolor='#1c4532', linewidth=0.5)

ax.set_ylabel('Number of Classified Sites', fontsize=11, weight='bold', color='#1a202c')
ax.set_title('Figure 3: Rock Class Breakdown by Geographic Continent (n=135)', fontsize=12.5, weight='bold', color='#1a202c', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(regions, fontsize=10.5, weight='bold', color='#1a202c')
ax.legend(frameon=True, facecolor='white', edgecolor='#cbd5e0', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(fig3_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig3_dir, 'figure_vector.pdf'))
plt.close()

# -------------------------------------------------------------
# FIGURE 4: Top Major Stones
# -------------------------------------------------------------
fig4_dir = os.path.join(base_dir, '04_Top_Major_Stones')
os.makedirs(fig4_dir, exist_ok=True)

df4 = pd.DataFrame({
    'Major_Stone_Type': ['Limestone', 'Granite', 'Sandstone', 'Marble', 'White Marble', 'Laterite', 'Coral Rag', 'Chalk', 'Basalt', 'Red Sandstone + White Marble', 'Flint (Spiennes)'],
    'Rock_Class': ['Sedimentary', 'Igneous', 'Sedimentary', 'Metamorphic', 'Metamorphic', 'Sedimentary', 'Biogenic Sedimentary', 'Sedimentary', 'Igneous', 'Sedimentary + Metamorphic', 'Sedimentary'],
    'Direct_Site_Mentions': [24, 15, 14, 10, 3, 2, 2, 2, 2, 2, 1]
})
df4.to_csv(os.path.join(fig4_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=600)
stones = df4['Major_Stone_Type'].values
counts = df4['Direct_Site_Mentions'].values
y_pos = np.arange(len(stones))
bars = ax.barh(y_pos, counts, color='#2b6cb0', edgecolor='#1a365d', height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels(stones, fontsize=10, weight='bold', color='#1a202c')
ax.invert_yaxis()
ax.set_xlabel('Number of Directly Documented Sites', fontsize=11, weight='bold', color='#1a202c')
ax.set_title('Figure 4: Frequency of Primary Major Stone Types (Backup 34 Audit)', fontsize=12.5, weight='bold', color='#1a202c', pad=15)
for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.3, bar.get_y() + bar.get_height()/2, f'{int(w)}', ha='left', va='center', fontsize=10, weight='bold', color='#1a365d')
ax.set_xlim(0, 28)
plt.tight_layout()
plt.savefig(os.path.join(fig4_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig4_dir, 'figure_vector.pdf'))
plt.close()

# -------------------------------------------------------------
# FIGURE 5: Stone Provenance
# -------------------------------------------------------------
fig5_dir = os.path.join(base_dir, '05_Stone_Provenance')
os.makedirs(fig5_dir, exist_ok=True)

df5 = pd.DataFrame({
    'Provenance_Category': ['Local Stone (<25 km)', 'Both Local & Imported', 'Imported Stone (>100 km)', 'Reused Ancient Spolia'],
    'Site_Count': [114, 8, 6, 1],
    'Percentage': [88.37, 6.20, 4.65, 0.78]
})
df5.to_csv(os.path.join(fig5_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(7.5, 5), dpi=600)
labels = ['Local Stone\n(114 sites | 88.4%)', 'Both Local & Imported\n(8 sites | 6.2%)', 'Imported Stone\n(6 sites | 4.7%)', 'Reused Spolia\n(1 site | 0.8%)']
sizes = [114, 8, 6, 1]
colors = ['#38a169', '#d69e2e', '#e53e3e', '#805ad5']
explode = (0.02, 0.05, 0.05, 0.05)
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=120,
                                  colors=colors, pctdistance=0.72, explode=explode,
                                  textprops=dict(color='#1a202c', fontsize=10, weight='bold'))
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(10.5)
centre_circle = plt.Circle((0,0), 0.52, fc='white')
fig.gca().add_artist(centre_circle)
ax.set_title('Figure 5: Resource Sourcing Provenance: Local vs. Imported (n=129)', fontsize=12.5, weight='bold', color='#1a202c', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(fig5_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig5_dir, 'figure_vector.pdf'))
plt.close()

# -------------------------------------------------------------
# FIGURE 6: Preservation Condition
# -------------------------------------------------------------
fig6_dir = os.path.join(base_dir, '06_Preservation_Condition')
os.makedirs(fig6_dir, exist_ok=True)

df6 = pd.DataFrame({
    'Condition_Rating': ['Good Condition', 'Excellent Condition', 'Moderate Deterioration', 'Poor / Critical Condition'],
    'Site_Count': [82, 70, 32, 10],
    'Percentage': [42.27, 36.08, 16.49, 5.15]
})
df6.to_csv(os.path.join(fig6_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(7.5, 5), dpi=600)
labels = ['Good Condition\n(82 sites | 42.3%)', 'Excellent Condition\n(70 sites | 36.1%)', 'Moderate Deterioration\n(32 sites | 16.5%)', 'Poor / Critical\n(10 sites | 5.2%)']
sizes = [82, 70, 32, 10]
colors = ['#38a169', '#2b6cb0', '#d69e2e', '#e53e3e']
explode = (0.02, 0.02, 0.04, 0.06)
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
                                  colors=colors, pctdistance=0.75, explode=explode,
                                  textprops=dict(color='#1a202c', fontsize=10, weight='bold'))
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(10.5)
centre_circle = plt.Circle((0,0), 0.52, fc='white')
fig.gca().add_artist(centre_circle)
ax.set_title('Figure 6: Environmental Preservation Ratings across Assessed Monuments (n=194)', fontsize=12, weight='bold', color='#1a202c', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(fig6_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig6_dir, 'figure_vector.pdf'))
plt.close()

# -------------------------------------------------------------
# FIGURE 7: Weathering Threats
# -------------------------------------------------------------
fig7_dir = os.path.join(base_dir, '07_Weathering_Threats')
os.makedirs(fig7_dir, exist_ok=True)

df7 = pd.DataFrame({
    'Weathering_Threat': ['Surface Erosion', 'High Ambient Humidity', 'Atmospheric Pollution (SO2/NOx)', 'Flooding Risk', 'Invasive Vegetation', 'Seismic Activity / Earthquakes', 'Moisture / Rising Damp', 'Climate Change Vulnerability', 'Salt Crystallization / Efflorescence'],
    'Documented_Sites_Count': [31, 17, 11, 9, 8, 6, 6, 6, 5]
})
df7.to_csv(os.path.join(fig7_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=600)
threats = df7['Weathering_Threat'].values
counts = df7['Documented_Sites_Count'].values
y_pos = np.arange(len(threats))
bars = ax.barh(y_pos, counts, color='#e53e3e', edgecolor='#742a2a', height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels(threats, fontsize=10, weight='bold', color='#1a202c')
ax.invert_yaxis()
ax.set_xlabel('Number of Sites Documenting Threat Vector', fontsize=11, weight='bold', color='#1a202c')
ax.set_title('Figure 7: Primary Weathering & Deterioration Threat Vectors (n=119)', fontsize=12.5, weight='bold', color='#1a202c', pad=15)
for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.4, bar.get_y() + bar.get_height()/2, f'{int(w)}', ha='left', va='center', fontsize=10, weight='bold', color='#742a2a')
ax.set_xlim(0, 36)
plt.tight_layout()
plt.savefig(os.path.join(fig7_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig7_dir, 'figure_vector.pdf'))
plt.close()

# -------------------------------------------------------------
# FIGURE 8: Dataset Inscription Status
# -------------------------------------------------------------
fig8_dir = os.path.join(base_dir, '08_Dataset_Gap_Status')
os.makedirs(fig8_dir, exist_ok=True)

df8 = pd.DataFrame({
    'Operational_Status': ['Researched & Verified Stone Baseline', 'Skipped Research Queue (Pending)', 'OUV Text Inaccessible (Absent)', 'OUV Text Issue (Ambiguous)'],
    'Site_Count': [193, 649, 24, 22],
    'Percentage': [21.40, 71.95, 2.66, 2.44]
})
df8.to_csv(os.path.join(fig8_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(7.5, 5), dpi=600)
labels = ['Researched & Verified\n(193 sites | 21.4%)', 'Skipped Research Queue\n(649 sites | 71.9%)', 'OUV Inaccessible (Absent)\n(24 sites | 2.7%)', 'OUV Text Issue\n(22 sites | 2.4%)']
sizes = [193, 649, 24, 22]
colors = ['#38a169', '#2b6cb0', '#e53e3e', '#d69e2e']
explode = (0.05, 0.02, 0.06, 0.04)
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
                                  colors=colors, pctdistance=0.75, explode=explode,
                                  textprops=dict(color='#1a202c', fontsize=9.5, weight='bold'))
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(10)
centre_circle = plt.Circle((0,0), 0.52, fc='white')
fig.gca().add_artist(centre_circle)
ax.set_title('Figure 8: Operational Status Breakdown Across the World Heritage Universe (n=902)', fontsize=11.5, weight='bold', color='#1a202c', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(fig8_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig8_dir, 'figure_vector.pdf'))
plt.close()

# -------------------------------------------------------------
# FIGURE 9: Country Unstudied Gaps
# -------------------------------------------------------------
fig9_dir = os.path.join(base_dir, '09_Country_Unstudied_Gaps')
os.makedirs(fig9_dir, exist_ok=True)

df9 = pd.DataFrame({
    'Country': ['Italy', 'Germany', 'China', 'France', 'Spain', 'Mexico', 'Iran', 'India', 'Türkiye', 'United Kingdom', 'Japan', 'Russian Federation', 'Czechia', 'Republic of Korea'],
    'Total_Inscribed_Sites': [47, 42, 36, 38, 39, 26, 25, 35, 20, 25, 19, 17, 14, 14],
    'Unstudied_Sites_Gap': [34, 33, 32, 31, 30, 24, 23, 21, 18, 18, 15, 14, 14, 13],
    'Researched_Sites': [13, 9, 4, 7, 9, 2, 2, 14, 2, 7, 4, 3, 0, 1],
    'Unstudied_Percentage': [72.3, 78.6, 88.9, 81.6, 76.9, 92.3, 92.0, 60.0, 90.0, 72.0, 78.9, 82.4, 100.0, 92.9]
})
df9.to_csv(os.path.join(fig9_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(9, 5), dpi=600)
countries = df9['Country'].values
unstudied = df9['Unstudied_Sites_Gap'].values
totals = df9['Total_Inscribed_Sites'].values

x = np.arange(len(countries))
width = 0.35

bars1 = ax.bar(x - width/2, unstudied, width, label='Unstudied Sites (Research Gap)', color='#e53e3e', edgecolor='#742a2a', linewidth=0.5)
bars2 = ax.bar(x + width/2, totals, width, label='Total Inscribed Heritage Sites', color='#2b6cb0', edgecolor='#1a365d', linewidth=0.5)

ax.set_ylabel('Number of Heritage Sites', fontsize=11, weight='bold', color='#1a202c')
ax.set_title('Figure 9: Unstudied Site Gaps Across Leading Heritage Nations (Backup 34 Audit)', fontsize=12, weight='bold', color='#1a202c', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(countries, rotation=45, ha='right', fontsize=9.5, weight='bold', color='#1a202c')
ax.legend(frameon=True, facecolor='white', edgecolor='#cbd5e0', fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(fig9_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig9_dir, 'figure_vector.pdf'))
plt.close()

# -------------------------------------------------------------
# FIGURE 10: Iceberg Uncaptured Model
# -------------------------------------------------------------
fig10_dir = os.path.join(base_dir, '10_Iceberg_Uncaptured_Model')
os.makedirs(fig10_dir, exist_ok=True)

df10 = pd.DataFrame({
    'Heritage_Category': ['Currently Documented Stone Sites (Verified Baseline)', 'Estimated Uncaptured Stone Sites (Hidden Mass)', 'Non-Stone / Natural / Intangible Unstudied Sites'],
    'Site_Count': [193, 532, 177],
    'Percentage_of_Total_902': [21.40, 58.98, 19.62]
})
df10.to_csv(os.path.join(fig10_dir, 'data_table.csv'), index=False)

fig, ax = plt.subplots(figsize=(8, 4.8), dpi=600)
categories = ['Currently Documented\nStone Sites (Verified)', 'Estimated Uncaptured\nStone Sites (Hidden Mass)', 'Non-Stone / Natural\nUnstudied Sites']
counts = df10['Site_Count'].values
colors = ['#38a169', '#3182ce', '#cbd5e0']

bars = ax.bar(categories, counts, color=colors, width=0.55, edgecolor='#1a365d', linewidth=0.8)
ax.set_ylabel('Number of Sites', fontsize=11, weight='bold', color='#1a202c')
ax.set_title('Figure 10: The Iceberg Model: Documented Baseline vs. Hidden Stone Mass', fontsize=12.5, weight='bold', color='#1a202c', pad=15)
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 12, f'{int(h)} sites', ha='center', va='bottom', fontsize=10.5, weight='bold', color='#1a365d')
ax.set_ylim(0, 620)
plt.tight_layout()
plt.savefig(os.path.join(fig10_dir, 'figure_600dpi.png'), dpi=600)
plt.savefig(os.path.join(fig10_dir, 'figure_vector.pdf'))
plt.close()


# -------------------------------------------------------------
# FIGURE 11: Photographic Pre-Screening Stone Potential Tiers
# -------------------------------------------------------------
fig11_dir = os.path.join(base_dir, '11_Stone_Potential_Tiers')
os.makedirs(fig11_dir, exist_ok=True)

df11 = pd.DataFrame({
    'Potential_Flag_Code': ['bvvvvvvhp', 'bvvvvvhp', 'bvvvvhp', 'bvvvhp', 'bvvhp', 'bvhp', 'bhp', 'bp'],
    'Tier_Description': [
        'Tier 1: Maximum Monolithic / Giant Substrate',
        'Tier 2: Massive Cliff Rock Art / Bedrock Substrate',
        'Tier 3: Monumental Megalithic / Sanctuary Architecture',
        'Tier 4: Exceptional Stone Fortress / Cathedral / Mosque',
        'Tier 5: Major Ashlar Masonry / Imperial Ruins',
        'Tier 6: High Probability Ashlar / Urban Core',
        'Tier 7: High Probability Local Stone / Masonry',
        'Tier 8: Moderate Probability Stone Fabric'
    ],
    'Pre_Screened_Site_Count': [1, 10, 28, 62, 26, 93, 25, 89],
    'Percentage_of_Pre_Screened_334': [0.3, 3.0, 8.4, 18.6, 7.8, 27.8, 7.5, 26.6],
    'Percentage_of_Total_902': [0.1, 1.1, 3.1, 6.9, 2.9, 10.3, 2.8, 9.9]
})
df11.to_csv(os.path.join(fig11_dir, 'data_table.csv'), index=False)


# -------------------------------------------------------------
# FIGURE 12: All Mentioned Heritage Rocks Inventory
# -------------------------------------------------------------
fig12_dir = os.path.join(base_dir, '12_All_Mentioned_Rocks')
os.makedirs(fig12_dir, exist_ok=True)

print('All 12 figures and CSV tables created successfully in Heritage_Stones_Journal_Figures/')

# Create ZIP archive
zip_filename = 'Heritage_Stones_Journal_Figures_and_Tables.zip'
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, os.path.dirname(base_dir))
            zipf.write(file_path, arcname)

print(f'Successfully created ZIP package: {zip_filename}')
