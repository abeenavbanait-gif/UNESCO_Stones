import re

with open('classify_monuments_v2.py', 'r') as f:
    content = f.read()

# 1. Update target_indices to process all sites
content = re.sub(
    r"target_indices = df\[.*?\]\.index",
    "target_indices = df.index",
    content,
    flags=re.DOTALL
)

# 2. Update prompt_template
new_prompt = """    prompt_template = (
        "You are an expert geologist and architectural historian.\\n"
        "Analyze this UNESCO World Heritage Site information:\\n"
        "Site Name: {site_name}\\n"
        "Brief Description: {brief_desc}\\n"
        "OUV Statement: {ouv_stmt}\\n\\n"
        "Question: Does this site feature or consist of natural building stone, rock-cut architecture, "
        "or specific geological materials (e.g. granite, limestone, sandstone, marble, slate, tuff, travertine, basalt, ashlar masonry)?\\n"
        "Respond ONLY with a valid JSON object in this format:\\n"
        "{{\\n"
        '  "has_geological_material": true/false,\\n'
        '  "stone_types": ["type1", "type2"],\\n'
        '  "mention_context": "The exact full sentence or paragraph from the text where these stones/rocks are mentioned. If none, return empty string.",\\n'
        '  "confidence": "HIGH"/"MEDIUM"/"LOW"/"NONE",\\n'
        '  "explanation": "Short 1-sentence explanation"\\n'
        "}}"
    )"""
content = re.sub(r"    prompt_template = \(.*?\"\n        \"\}\}\"\n    \)", new_prompt, content, flags=re.DOTALL)

# 3. Update evaluate_single_site return dict
new_return = """            return {
                'index': idx,
                'has_geo': res_json.get("has_geological_material", False),
                'stone_types': "; ".join(res_json.get("stone_types", [])),
                'mention_context': res_json.get("mention_context", ""),
                'confidence': res_json.get("confidence", "NONE"),
                'summary': res_json.get("explanation", "")
            }"""
content = re.sub(r"            return \{\n                'index': idx,.*?'summary': res_json.get\(\"explanation\", \"\"\)\n            \}", new_return, content, flags=re.DOTALL)

# 4. Update the lists that build the final dataframe columns
new_lists = """    llm_has_geo = []
    llm_stones = []
    llm_context = []
    llm_conf = []
    llm_summary = []

    for idx in df.index:
        row = df.loc[idx]
        if idx in target_indices and idx in results_map:
            res = results_map[idx]
            llm_has_geo.append(res['has_geo'])
            llm_stones.append(res['stone_types'])
            llm_context.append(res['mention_context'])
            llm_conf.append(res['confidence'])
            llm_summary.append(res['summary'])
        elif row['stone_count_v2'] > 0 or row['confidence_v2'] == 'HIGH':
            llm_has_geo.append(True)
            llm_stones.append(row['stone_types_found_v2'])
            llm_context.append("")
            llm_conf.append(row['confidence_v2'])
            llm_summary.append("Automatically verified by dictionary match")
        else:
            llm_has_geo.append(False)
            llm_stones.append("")
            llm_context.append("")
            llm_conf.append(row['confidence_v2'])
            llm_summary.append("No material identified")

    df['llm_evaluated'] = True
    df['llm_has_geological_material'] = llm_has_geo
    df['llm_stone_types'] = llm_stones
    df['llm_mention_context'] = llm_context
    df['llm_confidence'] = llm_conf
    df['llm_summary'] = llm_summary"""

content = re.sub(r"    llm_has_geo = \[\]\n.*?df\['llm_summary'\] = llm_summary", new_lists, content, flags=re.DOTALL)

with open('classify_monuments_v2.py', 'w') as f:
    f.write(content)
print("classify_monuments_v2.py updated successfully.")
