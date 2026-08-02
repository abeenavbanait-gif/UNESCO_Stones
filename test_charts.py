import pandas as pd
manual_df = pd.read_csv("Imp Data/Live_Manual_Data.csv")
print("Rock Class:")
class_counts = {"Igneous": 0, "Metamorphic": 0, "Sedimentary": 0}
if not manual_df.empty and 'Rock Class' in manual_df.columns:
    for val in manual_df['Rock Class'].dropna():
        rc = str(val).strip().capitalize()
        if "Igneous" in rc: class_counts["Igneous"] += 1
        elif "Metamorphic" in rc: class_counts["Metamorphic"] += 1
        elif "Sedimentary" in rc: class_counts["Sedimentary"] += 1
print(class_counts)

print("Stones:")
stone_list = []
if not manual_df.empty:
    if 'Mentioned Major Stone(s)' in manual_df.columns:
        for s in manual_df['Mentioned Major Stone(s)'].dropna():
            stone_list.extend([stn.strip().title() for stn in str(s).split(',') if stn.strip() and stn.strip().lower() not in ['nan', 'none']])
    if 'Secondary Stone' in manual_df.columns:
        for s in manual_df['Secondary Stone'].dropna():
            stone_list.extend([stn.strip().title() for stn in str(s).split(',') if stn.strip() and stn.strip().lower() not in ['nan', 'none']])
print(pd.Series(stone_list).value_counts().head(15))
