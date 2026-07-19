import pandas as pd

# Load old and new DataFrames
old_df = pd.read_csv("Imp Data/UNESCO_Stones_Manual_Data.csv")
new_df = pd.read_csv("Imp Data/Live_Manual_Data.csv")

# Find Taj Mahal
old_df['safe_id'] = old_df['Site ID'].astype(str).str.replace('.0', '', regex=False)
taj = old_df[old_df['safe_id'] == '252']

if not taj.empty:
    taj_data = taj.iloc[0].to_dict()
    new_row = {
        "Site ID": "252",
        "Site Name": "Taj Mahal",
        "Country": "India"
    }
    
    # Copy all matching columns
    for col in new_df.columns:
        if col in taj_data and pd.notna(taj_data[col]) and taj_data[col] != "":
            new_row[col] = taj_data[col]
            
    # Append
    new_df = pd.concat([new_df, pd.DataFrame([new_row])], ignore_index=True)
    new_df.to_csv("Imp Data/Live_Manual_Data.csv", index=False)
    print("Transferred Taj Mahal to Live_Manual_Data.csv successfully!")
else:
    print("Taj Mahal not found in old data.")
