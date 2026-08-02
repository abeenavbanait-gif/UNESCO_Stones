from data_manager import save_live_data_field
import pandas as pd

save_live_data_field("252", "Taj Mahal", "India", "Architecture Type_Ref", "External")

df = pd.read_csv("Imp Data/Live_Manual_Data.csv")
print("Saved values for Architecture Type_Ref:", df["Architecture Type_Ref"].values)
