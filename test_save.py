import pandas as pd
from data_manager import save_manual_data, load_manual_data

print("Before:", load_manual_data()[load_manual_data()['Site ID'] == 252]['Architecture Type'].values)
save_manual_data("252", {"Architecture Type": "Test Architecture"})
print("After:", load_manual_data()[load_manual_data()['Site ID'] == 252]['Architecture Type'].values)
