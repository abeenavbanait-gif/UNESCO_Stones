# Removing Manual Overrides & Adding a "Suggestions" Feature

Yes, I completely understand! You want the NLP extraction to be **100% truthful to the official UNESCO text**. If UNESCO did not explicitly write "Makrana marble" or "Carrara marble" in the text, we should not secretly inject it into the dataset and pretend it was there. 

Instead, you want a new "Suggestions" feature where the app acknowledges that a famous stone is missing from the official text and suggests that UNESCO should add it.

## User Review Required

Please review the proposed approach below. If this looks good to you, click **Proceed** and I will implement it!

## Proposed Changes

### 1. Update `classify_monuments.py`

I will rewrite the `MANUAL_OVERRIDES` logic. 
- **Currently:** If a site like the Taj Mahal is found, the script sneaks "Makrana marble" into the `named_stone_matches` list, artificially boosting its NLP score and adding it to the charts.
- **Proposed Fix:** The script will no longer touch the `named_stone_matches` list. Instead, it will create a brand new column in the CSV database called `suggested_stones`. If a site matches our dictionary (e.g., Pisa = Carrara marble), it will save "Carrara marble" into the `suggested_stones` column *without* affecting the NLP score or the primary extraction data.

### 2. Update `app.py` (Site Explorer UI)

When you are exploring a site in the Site Explorer (e.g., Taj Mahal):
- The app will check if there is anything written in the new `suggested_stones` column.
- If there is, it will display a distinct **Suggestions box** right below the main stone mentions, with a message like: 
  > 💡 **Suggestion for UNESCO:** The specific rock *Makrana marble* is historically significant to this monument but is completely missing from the official OUV statement and site description. It should be explicitly mentioned.

## Verification Plan

1. I will run `classify_monuments.py` to strip out all the fake manual overrides and regenerate the clean dataset.
2. I will verify that the pie charts and map statistics on the Home Page no longer include these forced stones.
3. I will open the app and verify that the Taj Mahal and Pisa display the new "Suggestions" UI box instead of listing the stones as officially found.
