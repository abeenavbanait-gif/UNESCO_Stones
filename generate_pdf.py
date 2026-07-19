import pandas as pd
from fpdf import FPDF
import math

# Load the dataset
df = pd.read_csv("Imp Data/972-sites_cultural_sites_classified.csv")
sites = df['site_name'].tolist()

# Ensure we have exactly 972 or whatever the number is
total_sites = len(sites)
print(f"Total sites: {total_sites}")

# PDF Settings
pdf = FPDF(orientation='P', unit='mm', format='A4')
pdf.set_auto_page_break(auto=True, margin=10)

# Layout constants
MARGIN_LEFT = 10
MARGIN_TOP = 15
COLUMNS = 3
PAGE_WIDTH = 210
PAGE_HEIGHT = 297
usable_width = PAGE_WIDTH - 2 * MARGIN_LEFT
col_width = usable_width / COLUMNS
line_height = 3.3  # Forces ~81 items per column * 3 = 243 items per page. 972/243 = 4 pages
max_lines_per_col = int((PAGE_HEIGHT - MARGIN_TOP - 15) / line_height)

pdf.add_page()
pdf.set_font("Arial", size=7.5)

col_idx = 0
y_offset = MARGIN_TOP

# Header
pdf.set_font("Arial", 'B', 12)
pdf.set_xy(MARGIN_LEFT, 5)
pdf.cell(0, 10, "UNESCO Cultural Built Heritage Sites (Index 1 - 972)", ln=1, align="C")
pdf.set_font("Arial", size=7.5)

for i, site in enumerate(sites):
    # If the column is full, move to next column
    if y_offset > (PAGE_HEIGHT - 15):
        col_idx += 1
        y_offset = MARGIN_TOP
        
        # If the page is full (all columns used), add a new page
        if col_idx >= COLUMNS:
            pdf.add_page()
            col_idx = 0
            y_offset = MARGIN_TOP
            
            # Header for new page
            pdf.set_font("Arial", 'B', 12)
            pdf.set_xy(MARGIN_LEFT, 5)
            pdf.cell(0, 10, "UNESCO Cultural Built Heritage Sites (Continued)", ln=1, align="C")
            pdf.set_font("Arial", size=7.5)

    x_offset = MARGIN_LEFT + (col_idx * col_width)
    pdf.set_xy(x_offset, y_offset)
    
    # Truncate site name if it's too long to fit in the column
    display_name = site
    if len(display_name) > 65:
        display_name = display_name[:62] + "..."
        
    # Fix unicode errors for fpdf
    display_name = display_name.encode('latin-1', 'replace').decode('latin-1')
        
    pdf.cell(col_width - 2, line_height, f"{i+1}. {display_name}", border=0, ln=0)
    
    y_offset += line_height

pdf.output("UNESCO_Sites_Index.pdf")
print("Successfully generated UNESCO_Sites_Index.pdf")
