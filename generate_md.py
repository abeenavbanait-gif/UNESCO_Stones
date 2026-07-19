import pandas as pd

df = pd.read_csv("Imp Data/972-sites_cultural_sites_classified.csv")
sites = df['site_name'].tolist()

with open("UNESCO_Sites_Index.md", "w") as f:
    f.write("# UNESCO Cultural Built Heritage Sites (Index 1 - 972)\n\n")
    for i, site in enumerate(sites):
        f.write(f"{i+1}. {site}\n")

print("Successfully generated UNESCO_Sites_Index.md")
