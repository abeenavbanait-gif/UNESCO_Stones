import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

os.makedirs('charts', exist_ok=True)

# Styling defaults
plt.rcParams['font.sans-serif'] = 'Arial, Helvetica, sans-serif'
plt.rcParams['axes.edgecolor'] = '#d0d0d0'
plt.rcParams['axes.linewidth'] = 0.8

# Chart 1: Rock Class Donut
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
labels = ['Sedimentary\n(92 sites | 60.5%)', 'Igneous\n(37 sites | 24.3%)', 'Metamorphic\n(23 sites | 15.1%)']
sizes = [92, 37, 23]
colors = ['#2b6cb0', '#dd6b20', '#38a169']
explode = (0.02, 0.02, 0.02)
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
                                  colors=colors, pctdistance=0.75, explode=explode,
                                  textprops=dict(color='#2d3748', fontsize=10, weight='bold'))
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(11)
centre_circle = plt.Circle((0,0), 0.55, fc='white')
fig.gca().add_artist(centre_circle)
ax.set_title('Rock Class Distribution Across Classified Sites (n=152)', fontsize=12, weight='bold', color='#1a202c', pad=15)
plt.tight_layout()
plt.savefig('charts/rock_class_donut.png')
plt.close()

# Chart 2: Top Major Stones Horizontal Bar (Updated for B34 - Flint cleaned up to 1)
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
stones = ['Limestone', 'Granite', 'Sandstone', 'Marble', 'White Marble', 'Laterite', 'Coral Rag', 'Chalk', 'Basalt', 'Red Sandstone + White Marble', 'Flint (Spiennes)']
counts = [24, 15, 14, 10, 3, 2, 2, 2, 2, 2, 1]
y_pos = np.arange(len(stones))
bars = ax.barh(y_pos, counts, color='#2b6cb0', edgecolor='#1a365d', height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels(stones, fontsize=10, weight='bold', color='#2d3748')
ax.invert_yaxis()  # top-down
ax.set_xlabel('Number of Directly Documented Sites', fontsize=10, weight='bold', color='#2d3748')
ax.set_title('Top Major Stone Types Documented Across UNESCO Sites (Backup 34 Audit)', fontsize=11.5, weight='bold', color='#1a202c', pad=15)
for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.3, bar.get_y() + bar.get_height()/2, f'{int(w)}', ha='left', va='center', fontsize=10, weight='bold', color='#1a365d')
ax.set_xlim(0, 28)
plt.tight_layout()
plt.savefig('charts/top_stones_bar.png')
plt.close()

# Chart 3: Stone Provenance Donut Chart
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
labels = ['Local Stone\n(114 sites | 88.4%)', 'Both Local & Imported\n(8 sites | 6.2%)', 'Imported Stone\n(6 sites | 4.7%)', 'Reused Spolia\n(1 site | 0.8%)']
sizes = [114, 8, 6, 1]
colors = ['#38a169', '#d69e2e', '#e53e3e', '#805ad5']
explode = (0.02, 0.05, 0.05, 0.05)
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=120,
                                  colors=colors, pctdistance=0.72, explode=explode,
                                  textprops=dict(color='#2d3748', fontsize=9.5, weight='bold'))
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(10)
centre_circle = plt.Circle((0,0), 0.52, fc='white')
fig.gca().add_artist(centre_circle)
ax.set_title('Stone Provenance: Local vs. Imported Sourcing (n=129)', fontsize=12, weight='bold', color='#1a202c', pad=15)
plt.tight_layout()
plt.savefig('charts/provenance_pie.png')
plt.close()

# Chart 4: Rock Class by World Region (Grouped Bar)
fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
regions = ['Europe', 'Asia', 'Africa', 'Americas', 'Oceania']
sedimentary = [37, 26, 7, 7, 0]
igneous = [13, 9, 5, 7, 2]
metamorphic = [16, 4, 0, 1, 1]

x = np.arange(len(regions))
width = 0.25

rects1 = ax.bar(x - width, sedimentary, width, label='Sedimentary', color='#2b6cb0')
rects2 = ax.bar(x, igneous, width, label='Igneous', color='#dd6b20')
rects3 = ax.bar(x + width, metamorphic, width, label='Metamorphic', color='#38a169')

ax.set_ylabel('Number of Sites', fontsize=10, weight='bold', color='#2d3748')
ax.set_title('Rock Class Distribution Across Geographic Regions', fontsize=12, weight='bold', color='#1a202c', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(regions, fontsize=10, weight='bold', color='#2d3748')
ax.legend(frameon=True, facecolor='white', edgecolor='#cbd5e0')
plt.tight_layout()
plt.savefig('charts/regional_rock_class.png')
plt.close()

# Chart 5: Data Completeness Bar Chart (Updated B34)
fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
fields = ['Site Name & ID', 'UNESCO Criteria', 'Site Condition', 'Major Stone (B34 Verified)', 'Structural Use', 'Restoration', 'Masonry Technique', 'Rock Class', 'Local Provenance', 'Weathering', 'Lithology', 'Quarry Site', 'Local Stone Name', 'Minerals', 'Geological Age']
pcts = [100, 88, 21.5, 21.4, 21.1, 19.3, 17.4, 16.9, 14.3, 13.2, 8.9, 6.9, 4.8, 2.4, 1.8]
y_pos = np.arange(len(fields))

colors = ['#2b6cb0' if p > 50 else '#d69e2e' if p >= 15 else '#e53e3e' for p in pcts]
bars = ax.barh(y_pos, pcts, color=colors, height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels(fields, fontsize=9.5, weight='bold', color='#2d3748')
ax.invert_yaxis()
ax.set_xlabel('Completion Percentage across 902 UNESCO Sites (%)', fontsize=10, weight='bold', color='#2d3748')
ax.set_title('Data Completeness by Field Across the UNESCO Dataset (n=902, B34)', fontsize=11.5, weight='bold', color='#1a202c', pad=15)
for bar in bars:
    w = bar.get_width()
    ax.text(w + 1, bar.get_y() + bar.get_height()/2, f'{w:.1f}%', ha='left', va='center', fontsize=9, weight='bold', color='#2d3748')
ax.set_xlim(0, 115)
plt.tight_layout()
plt.savefig('charts/data_completeness_bar.png')
plt.close()

# Chart 6: Condition Assessment Donut
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
labels = ['Good Condition\n(82 sites | 42.3%)', 'Excellent Condition\n(70 sites | 36.1%)', 'Moderate Deterioration\n(32 sites | 16.5%)', 'Poor / Critical\n(10 sites | 5.2%)']
sizes = [82, 70, 32, 10]
colors = ['#38a169', '#2b6cb0', '#d69e2e', '#e53e3e']
explode = (0.02, 0.02, 0.04, 0.06)
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
                                  colors=colors, pctdistance=0.75, explode=explode,
                                  textprops=dict(color='#2d3748', fontsize=9.5, weight='bold'))
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(10)
centre_circle = plt.Circle((0,0), 0.52, fc='white')
fig.gca().add_artist(centre_circle)
ax.set_title('Conservation Condition Ratings of Assessed Sites (n=194)', fontsize=12, weight='bold', color='#1a202c', pad=15)
plt.tight_layout()
plt.savefig('charts/condition_assessment_pie.png')
plt.close()

# Chart 7: Weathering Threat Frequency
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
threats = ['Surface Erosion', 'High Humidity', 'Atmospheric Pollution', 'Flooding Risk', 'Invasive Vegetation', 'Seismic / Earthquakes', 'Moisture / Dampness', 'Climate Change Impact', 'Salt Efflorescence']
counts = [31, 17, 11, 9, 8, 6, 6, 6, 5]
y_pos = np.arange(len(threats))
bars = ax.barh(y_pos, counts, color='#e53e3e', height=0.65)
ax.set_yticks(y_pos)
ax.set_yticklabels(threats, fontsize=9.5, weight='bold', color='#2d3748')
ax.invert_yaxis()
ax.set_xlabel('Number of Sites Documenting Threat', fontsize=10, weight='bold', color='#2d3748')
ax.set_title('Primary Weathering & Deterioration Threats to Heritage Stones', fontsize=12, weight='bold', color='#1a202c', pad=15)
for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.4, bar.get_y() + bar.get_height()/2, f'{int(w)}', ha='left', va='center', fontsize=9.5, weight='bold', color='#742a2a')
ax.set_xlim(0, 36)
plt.tight_layout()
plt.savefig('charts/weathering_threats_bar.png')
plt.close()

# Chart 8: The 78% Data Gap Donut Chart (Updated B34 - 193 Verified, 649 Skipped, 22 Issue, 24 Absent)
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
labels = ['Researched & Verified\n(193 sites | 21.4%)', 'Skipped Research Queue\n(649 sites | 71.9%)', 'OUV Text Issue\n(22 sites | 2.4%)', 'OUV Text Inaccessible\n(24 sites | 2.7%)']
sizes = [193, 649, 22, 24]
colors = ['#38a169', '#2b6cb0', '#d69e2e', '#e53e3e']
explode = (0.05, 0.02, 0.04, 0.06)
wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
                                  colors=colors, pctdistance=0.75, explode=explode,
                                  textprops=dict(color='#2d3748', fontsize=9.5, weight='bold'))
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(9.5)
centre_circle = plt.Circle((0,0), 0.52, fc='white')
fig.gca().add_artist(centre_circle)
ax.set_title('Dataset Status: Researched vs. Unstudied Sites (n=902, B34)', fontsize=11.5, weight='bold', color='#1a202c', pad=15)
plt.tight_layout()
plt.savefig('charts/data_gap_donut.png')
plt.close()

# Chart 9: Unstudied Sites by Country (Top 14)
fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=300)
countries = ['Italy', 'Germany', 'China', 'France', 'Spain', 'Mexico', 'Iran', 'India', 'Türkiye', 'United Kingdom', 'Japan', 'Russian Fed.', 'Czechia', 'Rep. of Korea']
unstudied = [34, 33, 32, 31, 30, 24, 23, 21, 18, 18, 15, 14, 14, 13]
totals = [47, 42, 36, 38, 39, 26, 25, 35, 20, 25, 19, 17, 14, 14]

x = np.arange(len(countries))
width = 0.35

bars1 = ax.bar(x - width/2, unstudied, width, label='Unstudied Sites (Gap)', color='#e53e3e')
bars2 = ax.bar(x + width/2, totals, width, label='Total Inscribed Sites', color='#2b6cb0')

ax.set_ylabel('Number of Sites', fontsize=10, weight='bold', color='#2d3748')
ax.set_title('Unstudied Site Gaps Across Top Heritage Nations', fontsize=12, weight='bold', color='#1a202c', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(countries, rotation=45, ha='right', fontsize=9.5, weight='bold', color='#2d3748')
ax.legend(frameon=True, facecolor='white', edgecolor='#cbd5e0')
plt.tight_layout()
plt.savefig('charts/country_unstudied_gaps.png')
plt.close()

# Chart 10: Iceberg Model Comparison Bar (Updated B34: 193 Verified, 532 Estimated Hidden Mass, 177 Non-Stone)
fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
categories = ['Currently Documented\nStone Sites (Verified)', 'Estimated Uncaptured\nStone Sites (Hidden Mass)', 'Non-Stone / Natural\nUnstudied Sites']
counts = [193, 532, 177]
colors = ['#38a169', '#3182ce', '#cbd5e0']

bars = ax.bar(categories, counts, color=colors, width=0.55, edgecolor='#1a365d')
ax.set_ylabel('Number of Sites', fontsize=10, weight='bold', color='#2d3748')
ax.set_title('The Iceberg Model: Documented vs. Estimated Stone Heritage (B34)', fontsize=11.5, weight='bold', color='#1a202c', pad=15)
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 10, f'{int(h)} sites', ha='center', va='bottom', fontsize=10, weight='bold', color='#1a365d')
ax.set_ylim(0, 600)
plt.tight_layout()
plt.savefig('charts/iceberg_uncaptured_model.png')
plt.close()

print('All 10 charts updated for Backup 34!')
