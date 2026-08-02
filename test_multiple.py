import streamlit as st
from data_manager import save_live_data_field, get_live_data_for_site
import pandas as pd

unesco_id = "252"
field_key = "Architecture Type"
ref_key = f"ref_{field_key}_{unesco_id}"

# clear db
df = pd.read_csv("Imp Data/Live_Manual_Data.csv")
df.to_csv("Imp Data/Live_Manual_Data_backup.csv", index=False)

# simulate saving Architecture Type
save_live_data_field(unesco_id, "Taj Mahal", "India", field_key, "Tomb")
# simulate saving Ref
save_live_data_field(unesco_id, "Taj Mahal", "India", f"{field_key}_Ref", "Internal (DS/OUV)")

df_new = pd.read_csv("Imp Data/Live_Manual_Data.csv")
print("After saving both:")
print("Type:", df_new[field_key].values)
print("Ref:", df_new[f"{field_key}_Ref"].values)

