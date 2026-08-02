import pandas as pd
from data_manager import save_live_data_field, get_live_data_for_site

# 1. Simulate the DB is empty
print(get_live_data_for_site("252"))

# 2. User selects "Internal (DS/OUV)"
save_live_data_field("252", "Taj Mahal", "India", "Architecture Type_Ref", "Internal (DS/OUV)")

# 3. Read DB again
print(get_live_data_for_site("252"))

