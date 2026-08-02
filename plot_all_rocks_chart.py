import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import re
from collections import Counter
import os

os.makedirs('charts', exist_ok=True)
os.makedirs('Heritage_Stones_Journal_Figures/12_All_Mentioned_Rocks', exist_ok=True)

# Styling for 600 DPI publication quality
plt.rcParams['font.sans-serif'] = 'Arial, Helvetica, sans-serif'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['pdf.fonttype'] = 42

df = pd.read_csv('Live_Manual_Data_Backup37_Mapped_Flags.csv')

# Normalized rock categorization mapping
rock_category_map = {
    # Sedimentary
    'limestone': ('Limestone (Common)', 'Sedimentary', '#2b6cb0'),
    'local limestone': ('Limestone (Local)', 'Sedimentary', '#2b6cb0'),
    'white limestone': ('Limestone (White)', 'Sedimentary', '#2b6cb0'),
    'globigerina limestone': ('Globigerina Limestone', 'Sedimentary', '#2b6cb0'),
    'coralline limestone': ('Coralline Limestone', 'Sedimentary', '#2b6cb0'),
    'coral rag': ('Coral Ragstone', 'Sedimentary', '#2b6cb0'),
    'coralline ragstone': ('Coral Ragstone', 'Sedimentary', '#2b6cb0'),
    'coral stone': ('Coral Ragstone', 'Sedimentary', '#2b6cb0'),
    'coral': ('Coral Ragstone', 'Sedimentary', '#2b6cb0'),
    'sandstone': ('Sandstone (Common)', 'Sedimentary', '#3182ce'),
    'red sandstone': ('Red Ferruginous Sandstone', 'Sedimentary', '#3182ce'),
    'calcareous sandstone': ('Calcareous Sandstone', 'Sedimentary', '#3182ce'),
    'sarsen': ('Silicified Sandstone (Sarsen)', 'Sedimentary', '#3182ce'),
    'chalk': ('Chalk', 'Sedimentary', '#4299e1'),
    'flint': ('Flint (Chert)', 'Sedimentary', '#4299e1'),
    'loess': ('Loess Deposits', 'Sedimentary', '#63b3ed'),
    'fireclay': ('Fireclay', 'Sedimentary', '#63b3ed'),

    # Igneous
    'granite': ('Granite (Plutonic)', 'Igneous', '#dd6b20'),
    'polished granite': ('Polished Granite', 'Igneous', '#dd6b20'),
    'basalt': ('Basalt (Deccan / Volcanic)', 'Igneous', '#c05621'),
    'andesite': ('Andesite', 'Igneous', '#c05621'),
    'volcanic tuff': ('Volcanic Tuff / Vitric Tuff', 'Igneous', '#e2e8f0'),
    'tuff': ('Volcanic Tuff / Vitric Tuff', 'Igneous', '#dd6b20'),
    'volcanic rock': ('Volcanic Rock / Lava', 'Igneous', '#dd6b20'),
    'lava': ('Volcanic Rock / Lava', 'Igneous', '#dd6b20'),
    'yellow tufa': ('Yellow Volcanic Tufa', 'Igneous', '#ed8936'),
    'grey piperno': ('Piperno Volcanic Stone', 'Igneous', '#ed8936'),
    'sillar': ('Sillar (Dacitic Ignimbrite Tuff)', 'Igneous', '#ed8936'),

    # Metamorphic
    'marble': ('Marble (Common)', 'Metamorphic', '#38a169'),
    'white marble': ('White Calcitic Marble (Makrana)', 'Metamorphic', '#38a169'),
    'carrara marble': ('Carrara Marble', 'Metamorphic', '#38a169'),
    'proconnesian marble': ('Proconnesian Marble', 'Metamorphic', '#38a169'),
    'italian marble': ('Italian Decorative Marble', 'Metamorphic', '#38a169'),
    'cipollino marble': ('Cipollino Marble', 'Metamorphic', '#38a169'),
    'slate': ('Slate (Metamorphic)', 'Metamorphic', '#2f855a'),
    'soapstone': ('Soapstone / Talc-Schist', 'Metamorphic', '#48bb78'),
    'steatite': ('Steatite (Soapstone)', 'Metamorphic', '#48bb78'),
    'bluestone': ('Welsh Bluestone (Dolerite/Rhyolite)', 'Metamorphic', '#48bb78'),

    # Earthen & Processed / Gemstones
    'laterite': ('Laterite (Iron-rich Soil Stone)', 'Earthen & Processed', '#805ad5'),
    'brick': ('Fired Brick / Terracotta', 'Earthen & Processed', '#805ad5'),
    'adobe': ('Adobe / Mud-Brick', 'Earthen & Processed', '#805ad5'),
    'travertine': ('Travertine (Chemical Carbonate)', 'Earthen & Processed', '#9f7aea'),
    'gypsum': ('Gypsum / Stucco Plaster', 'Earthen & Processed', '#9f7aea'),
    'pietra forte': ('Pietra Forte (Florentine Sandstone)', 'Earthen & Processed', '#b794f4'),
    'pietra serena': ('Pietra Serena (Florentine Greywacke)', 'Earthen & Processed', '#b794f4'),
    'agate': ('Agate Gemstone Inlay', 'Earthen & Processed', '#d69e2e'),
    'carnelian': ('Carnelian Gemstone Inlay', 'Earthen & Processed', '#d69e2e'),
    'iron ore': ('Iron Ore / Mineral', 'Earthen & Processed', '#d69e2e')
}

# Extract and map all mentioned rocks
raw_list = []
for col in ['Mentioned Major Stone(s)', 'Local Stone Name', 'Secondary Stone']:
    for val in df[col].dropna():
        text = str(val).strip()
        parts = re.split(r'\s*[,|;/]\s*', text)
        for p in parts:
            p_clean = re.sub(r'\b(b[v]*hp|bp|skipped|ouv absent)\b', '', p, flags=re.IGNORECASE).strip(' ;,()')
            p_clean_lower = p_clean.lower()
            if len(p_clean) > 2 and not p_clean_lower.startswith('to be') and not p_clean_lower.startswith('no'):
                # Match against category map
                matched = False
                for k, info in rock_category_map.items():
                    if k in p_clean_lower:
                        raw_list.append(info)
                        matched = True
                        break
                if not matched:
                    raw_list.append((p_clean.title(), 'Other / Vernacular', '#718096'))

# Build aggregated DataFrame
df_rocks = pd.DataFrame(raw_list, columns=['Rock_Name', 'Geological_Class', 'Color_Code'])
counts = df_rocks['Rock_Name'].value_counts()

df_summary = pd.DataFrame({
    'Rock_Name': counts.index,
    'Mentions_Count': counts.values
})

# Merge class info back
class_lookup = dict(zip(df_rocks['Rock_Name'], df_rocks['Geological_Class']))
color_lookup = dict(zip(df_rocks['Rock_Name'], df_rocks['Color_Code']))

df_summary['Geological_Class'] = df_summary['Rock_Name'].map(class_lookup)
df_summary['Color_Code'] = df_summary['Rock_Name'].map(color_lookup)

# Save CSV
df_summary.to_csv('Heritage_Stones_Journal_Figures/12_All_Mentioned_Rocks/data_table.csv', index=False)

print('Top 25 Mentioned Rocks:')
print(df_summary.head(25))

# Plot High-Res Chart: Top 22 Most Mentioned Heritage Rocks
fig, ax = plt.subplots(figsize=(10, 7), dpi=600)

top_df = df_summary.head(22).iloc[::-1] # Top 22 reverse for top-down bar
y_pos = np.arange(len(top_df))

bars = ax.barh(y_pos, top_df['Mentions_Count'], color=top_df['Color_Code'], height=0.68, edgecolor='#1a202c', linewidth=0.6)

ax.set_yticks(y_pos)
ax.set_yticklabels(top_df['Rock_Name'], fontsize=10, weight='bold', color='#1a202c')
ax.set_xlabel('Number of Direct Inscription & Field Mentions', fontsize=11, weight='bold', color='#1a202c')
ax.set_title('Figure 12: Comprehensive Geological Inventory — All Mentioned Heritage Rocks (Backup 37)', fontsize=12.5, weight='bold', color='#1a202c', pad=15)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.4, bar.get_y() + bar.get_height()/2, f'{int(w)}', ha='left', va='center', fontsize=9.5, weight='bold', color='#1a202c')

# Custom Legend for Geological Classes
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2b6cb0', edgecolor='#1a202c', label='Sedimentary Rocks (Limestones & Sandstones)'),
    Patch(facecolor='#dd6b20', edgecolor='#1a202c', label='Igneous Rocks (Granites, Basalts, Tuffs)'),
    Patch(facecolor='#38a169', edgecolor='#1a202c', label='Metamorphic Rocks (Marbles, Slates, Soapstones)'),
    Patch(facecolor='#805ad5', edgecolor='#1a202c', label='Earthen / Processed / Semi-Precious')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=9.5, frameon=True, facecolor='#f8fafc', edgecolor='#cbd5e0')

ax.set_xlim(0, 50)
plt.tight_layout()

plt.savefig('charts/all_rocks_mentioned_chart.png', dpi=600, bbox_inches='tight')
plt.savefig('Heritage_Stones_Journal_Figures/12_All_Mentioned_Rocks/figure_600dpi.png', dpi=600, bbox_inches='tight')
plt.savefig('Heritage_Stones_Journal_Figures/12_All_Mentioned_Rocks/figure_vector.pdf', bbox_inches='tight')
plt.close()

print('Successfully generated charts/all_rocks_mentioned_chart.png!')

