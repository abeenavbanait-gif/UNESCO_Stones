import pandas as pd
import numpy as np

current_df = pd.DataFrame({'Site ID': [174], 'Architecture Type': ['Renaissance'], 'safe_id': ['174']})
template_df = pd.DataFrame({'Site ID': [174], 'Architecture Type': [''], 'safe_id': ['174']})

for idx, row in current_df.iterrows():
    match_idx = template_df[template_df['safe_id'] == row['safe_id']].index
    if len(match_idx) > 0:
        for col in current_df.columns:
            if col != 'Index' and col != 'safe_id':
                val = row[col]
                if pd.notna(val) and val != "":
                    template_df.loc[match_idx, col] = val

print(template_df)
