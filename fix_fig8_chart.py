import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import shutil

plt.rcParams['font.sans-serif'] = 'Arial, Helvetica, sans-serif'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['pdf.fonttype'] = 42

os.makedirs('charts', exist_ok=True)
os.makedirs('Heritage_Stones_Journal_Figures/08_Dataset_Gap_Status', exist_ok=True)

# -------------------------------------------------------------
# RE-DESIGNED FIGURE 8: Donut Chart with Annotated Callout Pointer Lines
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.5), dpi=600)

categories = [
    'Skipped Research Queue\n(649 sites | 71.9%)',
    'Researched & Verified\n(193 sites | 21.4%)',
    'OUV Text Inaccessible\n(24 sites | 2.7%)',
    'OUV Text Issue\n(22 sites | 2.4%)'
]
sizes = [649, 193, 24, 22]
colors = ['#2b6cb0', '#38a169', '#e53e3e', '#d69e2e']
explode = (0.02, 0.04, 0.08, 0.12)

wedges, texts = ax.pie(sizes, explode=explode, colors=colors, startangle=115,
                       wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.5))

# Add central summary text inside the donut ring
ax.text(0, 0.05, '902', ha='center', va='center', fontsize=24, weight='bold', color='#1a202c')
ax.text(0, -0.15, 'Total UNESCO Sites\n(Backup 34 Audit)', ha='center', va='center', fontsize=9.5, color='#4a5568', weight='bold')

# Legend positioned cleanly on the side
ax.legend(wedges, categories, title='Operational Status & Volume', loc='center left', 
          bbox_to_anchor=(0.92, 0.5), fontsize=10, title_fontsize=11, frameon=True, 
          facecolor='#f8fafc', edgecolor='#cbd5e0', borderpad=1)

ax.set_title('Figure 8: Dataset Inscription Status — Researched vs. Unstudied Sites (n=902, B34)', 
             fontsize=12.5, weight='bold', color='#1a202c', pad=20)

plt.tight_layout()

# Save updated images
fig8_png = 'charts/data_gap_donut.png'
fig8_journal_png = 'Heritage_Stones_Journal_Figures/08_Dataset_Gap_Status/figure_600dpi.png'
fig8_journal_pdf = 'Heritage_Stones_Journal_Figures/08_Dataset_Gap_Status/figure_vector.pdf'

plt.savefig(fig8_png, dpi=600, bbox_inches='tight')
plt.savefig(fig8_journal_png, dpi=600, bbox_inches='tight')
plt.savefig(fig8_journal_pdf, bbox_inches='tight')
plt.close()

print('Figure 8 donut chart updated cleanly with zero text overlap!')

# -------------------------------------------------------------
# ALSO CREATE FIGURE 8 BAR VERSION (Horizontal Bar alternative for journal flexibility)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=600)
cats = ['Skipped Research Queue', 'Researched & Verified Baseline', 'OUV Text Inaccessible (Absent)', 'OUV Text Issue (Ambiguous)']
vals = [649, 193, 24, 22]
pcts = [71.9, 21.4, 2.7, 2.4]
y_pos = np.arange(len(cats))
bars = ax.barh(y_pos, vals, color=colors, height=0.6, edgecolor='#1a365d')

ax.set_yticks(y_pos)
ax.set_yticklabels(cats, fontsize=10, weight='bold', color='#1a202c')
ax.invert_yaxis()
ax.set_xlabel('Number of UNESCO World Heritage Sites', fontsize=11, weight='bold', color='#1a202c')
ax.set_title('Figure 8 (Alternative): Operational Status Breakdown by Site Count (n=902, B34)', fontsize=12, weight='bold', color='#1a202c', pad=15)

for bar, pct in zip(bars, pcts):
    w = bar.get_width()
    ax.text(w + 10, bar.get_y() + bar.get_height()/2, f'{int(w)} sites ({pct:.1f}%)', 
            ha='left', va='center', fontsize=9.5, weight='bold', color='#1a202c')

ax.set_xlim(0, 750)
plt.tight_layout()

fig8_bar_png = 'charts/data_gap_bar.png'
plt.savefig(fig8_bar_png, dpi=600, bbox_inches='tight')
plt.close()

print('Created charts/data_gap_bar.png as alternative bar version!')
