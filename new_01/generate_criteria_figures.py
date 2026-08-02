#!/usr/bin/env python3
"""
Generate 8 publication-quality figures showing the distribution of
UNESCO Selection Criteria per Cultural Site (n=991).
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap
import re

# Try importing extras
try:
    import seaborn as sns
except ImportError:
    os.system("pip3 install seaborn")
    import seaborn as sns

try:
    import squarify
except ImportError:
    os.system("pip3 install squarify")
    import squarify

# ──────────────────────────────────────────────────────────────────
# Style
# ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Colour palette — warm-to-cool gradient for 1–6 criteria
CRIT_COLORS = ["#3D405B", "#4F5D75", "#81B29A", "#F2CC8F", "#EF8354", "#E07A5F"]
SOURCE_NOTE = "Source: UNESCO WHS Database (2025) | n = 991 cultural sites"

# ──────────────────────────────────────────────────────────────────
# Load data
# ──────────────────────────────────────────────────────────────────
CSV = os.path.join(os.path.dirname(__file__), "991_Cultural_Sites_Manual_Data.csv")
df = pd.read_csv(CSV)

# Ensure Number of Criteria is computed
def count_criteria(text):
    if pd.isna(text):
        return 0
    return len(re.findall(r'\((?:i{1,3}|iv|v|vi)\)', str(text)))

df["Number of Criteria"] = df["UNESCO Criteria"].apply(count_criteria)

OUT = os.path.join(os.path.dirname(__file__), "figures_criteria")
os.makedirs(OUT, exist_ok=True)

# Distribution table
dist = df["Number of Criteria"].value_counts().sort_index()
dist = dist[dist.index > 0]  # exclude 0 if any
labels = [str(x) for x in dist.index]
values = dist.values


# ════════════════════════════════════════════════════════════════
# FIGURE 1 — Bar Chart
# ════════════════════════════════════════════════════════════════
def fig1_bar_chart():
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=CRIT_COLORS[: len(labels)],
                  edgecolor="white", linewidth=0.8, width=0.65)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
                f"{v}\n({v/values.sum()*100:.1f}%)", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color="#2D3142")
    ax.set_xlabel("Number of UNESCO Selection Criteria", fontweight="bold")
    ax.set_ylabel("Number of Sites", fontweight="bold")
    ax.set_title("Distribution of UNESCO Selection Criteria\nAcross Cultural Heritage Sites (n = 991)",
                 fontweight="bold", pad=14)
    ax.set_ylim(0, max(values) * 1.18)
    ax.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    fig.text(0.99, 0.01, SOURCE_NOTE, ha="right", va="bottom", fontsize=7, color="#777", style="italic")
    plt.tight_layout()
    path = os.path.join(OUT, "Fig1_Criteria_Bar_Chart.png")
    plt.savefig(path, dpi=300)
    plt.savefig(path.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Fig 1 saved → {path}")


# ════════════════════════════════════════════════════════════════
# FIGURE 2 — Pie / Donut Chart
# ════════════════════════════════════════════════════════════════
def fig2_donut_chart():
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        values, labels=[f"{l} criteria" for l in labels],
        autopct=lambda pct: f"{pct:.1f}%\n(n={int(pct/100*sum(values))})",
        colors=CRIT_COLORS[: len(labels)],
        startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=2),
        textprops=dict(fontsize=9),
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_fontweight("bold")
    centre = plt.Circle((0, 0), 0.35, fc="white")
    ax.add_artist(centre)
    ax.text(0, 0, f"991\nsites", ha="center", va="center",
            fontsize=16, fontweight="bold", color="#2D3142")
    ax.set_title("Proportional Share of Sites by\nNumber of Selection Criteria",
                 fontweight="bold", fontsize=14, pad=16)
    fig.text(0.99, 0.01, SOURCE_NOTE, ha="right", va="bottom", fontsize=7, color="#777", style="italic")
    plt.tight_layout()
    path = os.path.join(OUT, "Fig2_Criteria_Donut_Chart.png")
    plt.savefig(path, dpi=300)
    plt.savefig(path.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Fig 2 saved → {path}")


# ════════════════════════════════════════════════════════════════
# FIGURE 3 — Histogram
# ════════════════════════════════════════════════════════════════
def fig3_histogram():
    fig, ax = plt.subplots(figsize=(8, 5))
    n, bins, patches = ax.hist(
        df[df["Number of Criteria"] > 0]["Number of Criteria"],
        bins=np.arange(0.5, 7.5, 1), rwidth=0.8,
        color="#4F5D75", edgecolor="white", linewidth=0.8,
    )
    for i, (patch, count) in enumerate(zip(patches, n)):
        patch.set_facecolor(CRIT_COLORS[i % len(CRIT_COLORS)])
        ax.text(patch.get_x() + patch.get_width() / 2, patch.get_height() + 5,
                f"{int(count)}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    # Add KDE-like smooth line
    from scipy.ndimage import uniform_filter1d
    x_smooth = np.linspace(1, 6, 100)
    y_smooth = np.interp(x_smooth, range(1, 7), n)
    y_smooth = uniform_filter1d(y_smooth, size=15)
    ax.plot(x_smooth, y_smooth, color="#E07A5F", linewidth=2, linestyle="--", alpha=0.7, label="Trend")
    ax.set_xlabel("Number of UNESCO Selection Criteria", fontweight="bold")
    ax.set_ylabel("Frequency (Number of Sites)", fontweight="bold")
    ax.set_title("Frequency Distribution of Selection Criteria Count\nper UNESCO Cultural Heritage Site",
                 fontweight="bold", pad=14)
    ax.set_xticks(range(1, 7))
    ax.legend(loc="upper right", frameon=True, framealpha=0.9)
    ax.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    fig.text(0.99, 0.01, SOURCE_NOTE, ha="right", va="bottom", fontsize=7, color="#777", style="italic")
    plt.tight_layout()
    path = os.path.join(OUT, "Fig3_Criteria_Histogram.png")
    plt.savefig(path, dpi=300)
    plt.savefig(path.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Fig 3 saved → {path}")


# ════════════════════════════════════════════════════════════════
# FIGURE 4 — Stacked Bar by Region
# ════════════════════════════════════════════════════════════════
def fig4_stacked_bar_region():
    # Get region from master DB
    try:
        df_master = pd.read_csv("Imp Data/unesco_whs_master_database.csv")
        df_master["id"] = df_master["id"].astype(str).str.replace(".0", "", regex=False)
        region_lookup = dict(zip(df_master["id"], df_master["region"]))
    except Exception:
        region_lookup = {}

    df["Region"] = df["Site ID"].astype(str).str.replace(".0", "", regex=False).map(region_lookup)
    df["Region"] = df["Region"].fillna("Unknown")

    cross = pd.crosstab(df["Region"], df["Number of Criteria"])
    cross = cross[[c for c in sorted(cross.columns) if c > 0]]
    cross = cross.loc[cross.sum(axis=1).sort_values(ascending=True).index]

    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(cross))
    for i, col in enumerate(cross.columns):
        ax.barh(cross.index, cross[col], left=bottom,
                label=f"{col} criteria", color=CRIT_COLORS[i % len(CRIT_COLORS)],
                edgecolor="white", linewidth=0.5, height=0.65)
        bottom += cross[col].values

    ax.set_xlabel("Number of Sites", fontweight="bold")
    ax.set_ylabel("")
    ax.set_title("UNESCO Selection Criteria Distribution\nby Geographic Region",
                 fontweight="bold", pad=14)
    ax.legend(title="Criteria Count", loc="lower right", frameon=True,
              framealpha=0.9, edgecolor="#ccc")
    ax.xaxis.grid(True, linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    fig.text(0.99, 0.005, SOURCE_NOTE, ha="right", va="bottom", fontsize=7, color="#777", style="italic")
    plt.tight_layout()
    path = os.path.join(OUT, "Fig4_Criteria_Stacked_Bar_Region.png")
    plt.savefig(path, dpi=300)
    plt.savefig(path.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Fig 4 saved → {path}")


# ════════════════════════════════════════════════════════════════
# FIGURE 5 — Violin / Box Plot
# ════════════════════════════════════════════════════════════════
def fig5_violin_box():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), sharey=True)

    data = df[df["Number of Criteria"] > 0]["Number of Criteria"]

    # Violin
    parts = ax1.violinplot(data, positions=[1], showmeans=True, showmedians=True)
    for pc in parts["bodies"]:
        pc.set_facecolor("#81B29A")
        pc.set_alpha(0.7)
    parts["cmeans"].set_color("#E07A5F")
    parts["cmedians"].set_color("#2D3142")
    ax1.set_title("Violin Plot", fontweight="bold")
    ax1.set_xticks([1])
    ax1.set_xticklabels(["All Sites"])
    ax1.set_ylabel("Number of Criteria", fontweight="bold")
    ax1.yaxis.grid(True, linestyle="--", alpha=0.3)
    ax1.set_axisbelow(True)

    # Add stats annotation
    stats_text = (f"Mean: {data.mean():.2f}\nMedian: {data.median():.1f}\n"
                  f"Std: {data.std():.2f}\nMin: {data.min()}, Max: {data.max()}")
    ax1.text(1.35, data.max(), stats_text, fontsize=8, va="top",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f8f8", edgecolor="#ccc"))

    # Box plot by region
    if "Region" in df.columns:
        regions = df[df["Number of Criteria"] > 0].groupby("Region")["Number of Criteria"].apply(list)
        regions = regions[regions.apply(len) >= 5].sort_index()
        bp = ax2.boxplot(regions.values, tick_labels=[r[:20] for r in regions.index],
                         patch_artist=True, vert=True, widths=0.6)
        for i, patch in enumerate(bp["boxes"]):
            patch.set_facecolor(CRIT_COLORS[i % len(CRIT_COLORS)])
            patch.set_alpha(0.8)
        ax2.set_title("Box Plot by Region", fontweight="bold")
        ax2.tick_params(axis="x", rotation=25, labelsize=7)
        ax2.yaxis.grid(True, linestyle="--", alpha=0.3)
        ax2.set_axisbelow(True)

    fig.suptitle("Statistical Distribution of Selection Criteria per Site",
                 fontweight="bold", fontsize=14, y=1.02)
    fig.text(0.99, -0.02, SOURCE_NOTE, ha="right", va="bottom", fontsize=7, color="#777", style="italic")
    plt.tight_layout()
    path = os.path.join(OUT, "Fig5_Criteria_Violin_Box.png")
    plt.savefig(path, dpi=300)
    plt.savefig(path.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Fig 5 saved → {path}")


# ════════════════════════════════════════════════════════════════
# FIGURE 6 — Waffle Chart
# ════════════════════════════════════════════════════════════════
def fig6_waffle():
    # Each cell = ~1 site, grid of ~33×30 = 990 cells ≈ 991
    cols_grid = 33
    rows_grid = 30
    total_cells = cols_grid * rows_grid  # 990

    # Scale values proportionally to fill 990 cells
    proportions = values / values.sum() * total_cells
    cell_counts = np.round(proportions).astype(int)

    # Adjust rounding to sum exactly to total_cells
    diff = total_cells - cell_counts.sum()
    if diff > 0:
        idx = np.argmax(values)
        cell_counts[idx] += diff
    elif diff < 0:
        idx = np.argmax(cell_counts)
        cell_counts[idx] += diff

    # Build colour grid
    color_grid = []
    for i, count in enumerate(cell_counts):
        color_grid.extend([CRIT_COLORS[i]] * count)

    # Reshape into grid
    grid = np.arange(total_cells).reshape(rows_grid, cols_grid)

    fig, ax = plt.subplots(figsize=(11, 7))

    for row in range(rows_grid):
        for col in range(cols_grid):
            idx = row * cols_grid + col
            if idx < len(color_grid):
                rect = plt.Rectangle((col, rows_grid - 1 - row), 0.9, 0.9,
                                     facecolor=color_grid[idx], edgecolor="white",
                                     linewidth=0.3)
                ax.add_patch(rect)

    ax.set_xlim(-0.5, cols_grid + 0.5)
    ax.set_ylim(-0.5, rows_grid + 0.5)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.set_title("Waffle Chart: UNESCO Cultural Sites by Number of Selection Criteria\n"
                 "(each square ≈ 1 site; total = 991)",
                 fontweight="bold", fontsize=13, pad=16)

    # Legend
    handles = [mpatches.Patch(color=CRIT_COLORS[i], label=f"{labels[i]} criteria (n={values[i]})")
               for i in range(len(labels))]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.08),
              ncol=3, frameon=True, framealpha=0.9, edgecolor="#ccc", fontsize=9)

    fig.text(0.99, 0.01, SOURCE_NOTE, ha="right", va="bottom", fontsize=7, color="#777", style="italic")
    plt.tight_layout()
    path = os.path.join(OUT, "Fig6_Criteria_Waffle_Chart.png")
    plt.savefig(path, dpi=300)
    plt.savefig(path.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Fig 6 saved → {path}")


# ════════════════════════════════════════════════════════════════
# FIGURE 7 — Treemap
# ════════════════════════════════════════════════════════════════
def fig7_treemap():
    treemap_labels = [
        f"{l} Criteria\nn = {v} ({v/values.sum()*100:.1f}%)"
        for l, v in zip(labels, values)
    ]

    fig, ax = plt.subplots(figsize=(10, 7))
    squarify.plot(
        sizes=values.tolist(),
        label=treemap_labels,
        color=CRIT_COLORS[: len(values)],
        alpha=0.88,
        text_kwargs={"fontsize": 11, "fontweight": "bold", "color": "white"},
        ax=ax,
        pad=True,
        bar_kwargs={"edgecolor": "white", "linewidth": 2.5},
    )
    ax.set_title("Proportional Treemap: Sites by Number of Selection Criteria",
                 fontweight="bold", fontsize=14, pad=14)
    ax.axis("off")
    fig.text(0.99, 0.01, SOURCE_NOTE, ha="right", va="bottom", fontsize=7, color="#777", style="italic")
    plt.tight_layout()
    path = os.path.join(OUT, "Fig7_Criteria_Treemap.png")
    plt.savefig(path, dpi=300)
    plt.savefig(path.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Fig 7 saved → {path}")


# ════════════════════════════════════════════════════════════════
# FIGURE 8 — Heatmap (Criteria Count × Country, top 25 countries)
# ════════════════════════════════════════════════════════════════
def fig8_heatmap():
    # Top 25 countries by number of sites
    top_countries = df["Country"].value_counts().head(25).index.tolist()
    df_top = df[df["Country"].isin(top_countries) & (df["Number of Criteria"] > 0)]

    cross = pd.crosstab(df_top["Country"], df_top["Number of Criteria"])
    # Ensure all columns 1–6 exist
    for c in range(1, 7):
        if c not in cross.columns:
            cross[c] = 0
    cross = cross[[1, 2, 3, 4, 5, 6]]
    cross = cross.loc[cross.sum(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(9, 10))

    cmap = LinearSegmentedColormap.from_list("custom", ["#f7f7f7", "#81B29A", "#3D405B"])
    im = ax.imshow(cross.values, cmap=cmap, aspect="auto")

    # Labels
    ax.set_xticks(range(6))
    ax.set_xticklabels([f"{i}" for i in range(1, 7)], fontsize=10)
    ax.set_yticks(range(len(cross)))
    ax.set_yticklabels(cross.index, fontsize=8)
    ax.set_xlabel("Number of Selection Criteria", fontweight="bold", fontsize=11)
    ax.set_ylabel("")

    # Annotate cells
    for i in range(len(cross)):
        for j in range(6):
            val = cross.values[i, j]
            if val > 0:
                text_color = "white" if val > cross.values.max() * 0.6 else "#2D3142"
                ax.text(j, i, str(val), ha="center", va="center",
                        fontsize=8, fontweight="bold", color=text_color)

    ax.set_title("Heatmap: Selection Criteria Distribution\nAcross Top 25 Countries by Site Count",
                 fontweight="bold", fontsize=13, pad=14)

    cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label("Number of Sites", fontsize=9)

    fig.text(0.99, 0.005, SOURCE_NOTE, ha="right", va="bottom", fontsize=7, color="#777", style="italic")
    plt.tight_layout()
    path = os.path.join(OUT, "Fig8_Criteria_Heatmap_Country.png")
    plt.savefig(path, dpi=300)
    plt.savefig(path.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Fig 8 saved → {path}")


# ════════════════════════════════════════════════════════════════
# Run all
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("GENERATING 8 CRITERIA DISTRIBUTION FIGURES")
    print("=" * 60)
    fig1_bar_chart()
    fig2_donut_chart()
    fig3_histogram()
    fig4_stacked_bar_region()
    fig5_violin_box()
    fig6_waffle()
    fig7_treemap()
    fig8_heatmap()
    print("=" * 60)
    print(f"All figures saved to: {OUT}")
    print("Formats: PNG (300 dpi) + EPS (vector)")
    print("=" * 60)
