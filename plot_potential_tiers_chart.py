import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

os.makedirs('charts', exist_ok=True)
os.makedirs('Heritage_Stones_Journal_Figures/11_Stone_Potential_Tiers', exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Arial, Helvetica, sans-serif'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['pdf.fonttype'] = 42

df = pd.read_csv('Live_Manual_Data_Backup37_Mapped_Flags.csv')

# Filter for sites with flags
df_flags = df[df['Stone_Potential_Flag'].notna()].copy()

# Sort order by potential hierarchy
flag_order = ['bvvvvvvhp', 'bvvvvvhp', 'bvvvvhp', 'bvvvhp', 'bvvhp', 'bvhp', 'bhp', 'bp']
flag_names = [
    'bvvvvvvhp (Tier 1: Max Substrate | 1 site)',
    'bvvvvvhp (Tier 2: Cliff Rock Art | 10 sites)',
    'bvvvvhp (Tier 3: Megalithic / Monumental | 28 sites)',
    'bvvvhp (Tier 4: Exceptional Fortress / Cathedral | 62 sites)',
    'bvvhp (Tier 5: Major Imperial Ashlar | 26 sites)',
    'bvhp (Tier 6: High Probability Ashlar | 93 sites)',
    'bhp (Tier 7: High Probability Local Stone | 25 sites)',
    'bp (Tier 8: Moderate Stone Potential | 89 sites)'
]
counts = [df_flags['Stone_Potential_Flag'].value_counts().get(f, 0) for f in flag_order]

# Export CSV table
df_export = pd.DataFrame({
    'Potential_Flag_Code': flag_order,
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
    'Pre_Screened_Site_Count': counts,
    'Percentage_of_Pre_Screened_334': [round(100*c/sum(counts), 1) for c in counts],
    'Percentage_of_Total_902': [round(100*c/902, 1) for c in counts]
})
df_export.to_csv('Heritage_Stones_Journal_Figures/11_Stone_Potential_Tiers/data_table.csv', index=False)

# Plot high-res horizontal bar chart
fig, ax = plt.subplots(figsize=(9, 5.2), dpi=600)
y_pos = np.arange(len(flag_names))
colors = ['#742a2a', '#9b2c2c', '#c53030', '#e53e3e', '#dd6b20', '#d69e2e', '#3182ce', '#63b3ed']

bars = ax.barh(y_pos, counts, color=colors, height=0.65, edgecolor='#1a202c', linewidth=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels(flag_names, fontsize=9.5, weight='bold', color='#1a202c')
ax.invert_yaxis()
ax.set_xlabel('Number of Pre-Screened Unstudied Sites', fontsize=11, weight='bold', color='#1a202c')
ax.set_title('Figure 11: Photographic Pre-Screening Stone Potential Tiers (n=334 Pre-Screened Sites)', fontsize=12, weight='bold', color='#1a202c', pad=15)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 1.5, bar.get_y() + bar.get_height()/2, f'{int(w)} sites', ha='left', va='center', fontsize=9.5, weight='bold', color='#1a202c')

ax.set_xlim(0, 108)
plt.tight_layout()

plt.savefig('charts/figure_11_stone_potential_tiers.png', dpi=600, bbox_inches='tight')
plt.savefig('Heritage_Stones_Journal_Figures/11_Stone_Potential_Tiers/figure_600dpi.png', dpi=600, bbox_inches='tight')
plt.savefig('Heritage_Stones_Journal_Figures/11_Stone_Potential_Tiers/figure_vector.pdf', bbox_inches='tight')
plt.close()

print('Generated Figure 11 Stone Potential Tiers Chart cleanly!')

