#!/usr/bin/env python3
"""
Generate four publication-quality figures for Igneous Rocks in UNESCO World Heritage Sites.
Figures:
    1. Horizontal bar chart — frequency of each Standardized Stone Name
    2. Stacked bar chart   — stone-type composition per site
    3. Treemap              — proportional area view of stone frequencies
    4. Bubble plot          — site-level stone diversity (distinct igneous types per site)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager

# ---------------------------------------------------------------------------
# Try to load squarify; install if missing
# ---------------------------------------------------------------------------
try:
    import squarify
except ImportError:
    os.system("pip3 install squarify")
    import squarify

# ---------------------------------------------------------------------------
# Global style settings for journal-quality figures
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.titlesize": 13,
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

# ---------------------------------------------------------------------------
# Colour palette — curated, colour-blind-safe, high contrast
# ---------------------------------------------------------------------------
PALETTE = [
    "#2D3142",  # Dark gunmetal
    "#4F5D75",  # Payne's grey
    "#BFC0C0",  # Silver
    "#EF8354",  # Mandarin orange
    "#E07A5F",  # Terra cotta
    "#3D405B",  # Dark liver
    "#81B29A",  # Cambridge blue
    "#F2CC8F",  # Deep champagne
    "#718355",  # Russian green
    "#C9B1FF",  # Lavender
    "#6C5B7B",  # Purple taupe
]

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
CSV_PATH = os.path.join(os.path.dirname(__file__), "Igneous_Rocks_Sites.csv")
df = pd.read_csv(CSV_PATH)

# Output directory
OUT_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Horizontal Bar Chart: Frequency of Standardized Stone Names
# ═══════════════════════════════════════════════════════════════════════════
def figure_1_bar_chart():
    stone_counts = (
        df["Standardized Stone Name"]
        .value_counts()
        .sort_values(ascending=True)
    )

    fig, ax = plt.subplots(figsize=(8, 5.5))

    bars = ax.barh(
        stone_counts.index,
        stone_counts.values,
        color=PALETTE[3],
        edgecolor="white",
        linewidth=0.6,
        height=0.65,
    )

    # Data labels on bars
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{int(width)}",
            va="center",
            ha="left",
            fontsize=9,
            fontweight="bold",
            color="#2D3142",
        )

    ax.set_xlabel("Number of Mentions (n)", fontweight="bold")
    ax.set_ylabel("")
    ax.set_title(
        "Frequency of Igneous Stone Types in UNESCO\nWorld Heritage Built-Monument Sites",
        fontweight="bold",
        pad=12,
    )
    ax.set_xlim(0, stone_counts.max() + 3)
    ax.tick_params(axis="y", length=0)

    # Subtle grid
    ax.xaxis.grid(True, linestyle="--", alpha=0.3, color="#999")
    ax.set_axisbelow(True)

    # Source note
    fig.text(
        0.99, 0.01,
        "Source: UNESCO WHS Database (2025) | n = 60 mentions across 44 sites",
        ha="right", va="bottom", fontsize=7, color="#777", style="italic",
    )

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "Fig1_Igneous_Stone_Frequency_BarChart.png")
    plt.savefig(out, dpi=300)
    plt.savefig(out.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Figure 1 saved → {out}")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Stacked Bar Chart: Stone Composition per Site
# ═══════════════════════════════════════════════════════════════════════════
def figure_2_stacked_bar():
    # Build a site × stone cross-tab (count of each stone per site)
    cross = pd.crosstab(df["Site Name"], df["Standardized Stone Name"])

    # Sort sites by total stone mentions (descending)
    cross["_total"] = cross.sum(axis=1)
    cross = cross.sort_values("_total", ascending=True)
    cross = cross.drop(columns=["_total"])

    # Assign colours to stones
    stones_ordered = cross.sum().sort_values(ascending=False).index.tolist()
    colour_map = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(stones_ordered)}

    fig, ax = plt.subplots(figsize=(10, 12))

    left = np.zeros(len(cross))
    for stone in stones_ordered:
        if stone in cross.columns:
            vals = cross[stone].values
            ax.barh(
                cross.index,
                vals,
                left=left,
                label=stone,
                color=colour_map[stone],
                edgecolor="white",
                linewidth=0.4,
                height=0.7,
            )
            left += vals

    ax.set_xlabel("Number of Igneous Stone Mentions", fontweight="bold")
    ax.set_ylabel("")
    ax.set_title(
        "Igneous Stone Composition per UNESCO World Heritage Site",
        fontweight="bold",
        pad=12,
    )
    ax.tick_params(axis="y", length=0, labelsize=7.5)
    ax.xaxis.grid(True, linestyle="--", alpha=0.3, color="#999")
    ax.set_axisbelow(True)

    # Truncate long site names for readability
    labels = [
        (l[:55] + "…") if len(l) > 55 else l for l in cross.index
    ]
    ax.set_yticklabels(labels)

    ax.legend(
        title="Stone Type",
        loc="lower right",
        frameon=True,
        framealpha=0.9,
        edgecolor="#ccc",
        fontsize=7,
        title_fontsize=8,
    )

    fig.text(
        0.99, 0.005,
        "Source: UNESCO WHS Database (2025) | 44 sites with igneous stone mentions",
        ha="right", va="bottom", fontsize=6.5, color="#777", style="italic",
    )

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "Fig2_Igneous_Stone_Stacked_Bar.png")
    plt.savefig(out, dpi=300)
    plt.savefig(out.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Figure 2 saved → {out}")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Treemap: Proportional Area View of Stone Frequencies
# ═══════════════════════════════════════════════════════════════════════════
def figure_3_treemap():
    stone_counts = df["Standardized Stone Name"].value_counts()

    labels = [
        f"{name}\n(n={count}, {count/stone_counts.sum()*100:.1f}%)"
        for name, count in zip(stone_counts.index, stone_counts.values)
    ]
    sizes = stone_counts.values.tolist()
    colours = [PALETTE[i % len(PALETTE)] for i in range(len(sizes))]

    fig, ax = plt.subplots(figsize=(10, 7))

    squarify.plot(
        sizes=sizes,
        label=labels,
        color=colours,
        alpha=0.88,
        text_kwargs={
            "fontsize": 9,
            "fontweight": "bold",
            "color": "white",
            "wrap": True,
        },
        ax=ax,
        pad=True,
        bar_kwargs={"edgecolor": "white", "linewidth": 2},
    )

    ax.set_title(
        "Proportional Distribution of Igneous Stone Types\nin UNESCO World Heritage Built-Monument Sites",
        fontweight="bold",
        fontsize=13,
        pad=14,
    )
    ax.axis("off")

    fig.text(
        0.99, 0.01,
        "Source: UNESCO WHS Database (2025) | n = 60 mentions across 44 sites",
        ha="right", va="bottom", fontsize=7, color="#777", style="italic",
    )

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "Fig3_Igneous_Stone_Treemap.png")
    plt.savefig(out, dpi=300)
    plt.savefig(out.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Figure 3 saved → {out}")


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Bubble Plot: Site-level Igneous Stone Diversity
# ═══════════════════════════════════════════════════════════════════════════
def figure_4_bubble_plot():
    # For each site, count distinct stone types and total mentions
    site_stats = (
        df.groupby(["Site Name", "Country"])
        .agg(
            distinct_stones=("Standardized Stone Name", "nunique"),
            total_mentions=("Standardized Stone Name", "count"),
            stones_list=("Standardized Stone Name", lambda x: ", ".join(sorted(set(x)))),
        )
        .reset_index()
        .sort_values("distinct_stones", ascending=False)
    )

    # Colour by country (top 8 countries get unique colours, rest are grey)
    top_countries = site_stats["Country"].value_counts().head(8).index.tolist()
    country_colour = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(top_countries)}
    site_stats["colour"] = site_stats["Country"].map(
        lambda c: country_colour.get(c, "#BFC0C0")
    )

    fig, ax = plt.subplots(figsize=(11, 8))

    # Size scale: total mentions × 120 for visibility
    sizes = site_stats["total_mentions"].values * 120

    scatter = ax.scatter(
        site_stats["distinct_stones"],
        range(len(site_stats)),
        s=sizes,
        c=site_stats["colour"],
        alpha=0.75,
        edgecolors="white",
        linewidths=0.8,
        zorder=3,
    )

    # Y-axis site labels
    labels = [
        (n[:50] + "…") if len(n) > 50 else n for n in site_stats["Site Name"]
    ]
    ax.set_yticks(range(len(site_stats)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.tick_params(axis="y", length=0)

    ax.set_xlabel("Number of Distinct Igneous Stone Types", fontweight="bold")
    ax.set_ylabel("")
    ax.set_title(
        "Igneous Stone Diversity per UNESCO World Heritage Site\n(bubble size = total stone mentions)",
        fontweight="bold",
        pad=12,
    )
    ax.set_xlim(0.5, site_stats["distinct_stones"].max() + 0.8)
    ax.xaxis.grid(True, linestyle="--", alpha=0.3, color="#999")
    ax.set_axisbelow(True)

    # Set x-axis to integers only
    ax.set_xticks(range(1, site_stats["distinct_stones"].max() + 1))

    # Legend for country colours
    legend_handles = [
        mpatches.Patch(color=colour_colour, label=country)
        for country, colour_colour in country_colour.items()
    ]
    legend_handles.append(mpatches.Patch(color="#BFC0C0", label="Other"))
    ax.legend(
        handles=legend_handles,
        title="Country",
        loc="lower right",
        frameon=True,
        framealpha=0.9,
        edgecolor="#ccc",
        fontsize=7,
        title_fontsize=8,
    )

    # Size legend (manual)
    for mention_val in [1, 2, 4]:
        ax.scatter(
            [], [],
            s=mention_val * 120,
            c="#999",
            alpha=0.5,
            edgecolors="white",
            label=f"{mention_val} mention{'s' if mention_val > 1 else ''}",
        )

    fig.text(
        0.99, 0.005,
        "Source: UNESCO WHS Database (2025) | 44 sites with igneous stone mentions",
        ha="right", va="bottom", fontsize=6.5, color="#777", style="italic",
    )

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "Fig4_Igneous_Stone_Bubble_Plot.png")
    plt.savefig(out, dpi=300)
    plt.savefig(out.replace(".png", ".eps"), format="eps")
    plt.close()
    print(f"✓ Figure 4 saved → {out}")


# ═══════════════════════════════════════════════════════════════════════════
# Run all
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("GENERATING IGNEOUS ROCK FIGURES FOR JOURNAL PUBLICATION")
    print("=" * 60)
    figure_1_bar_chart()
    figure_2_stacked_bar()
    figure_3_treemap()
    figure_4_bubble_plot()
    print("=" * 60)
    print(f"All figures saved to: {OUT_DIR}")
    print("Formats: PNG (300 dpi) + EPS (vector)")
    print("=" * 60)
