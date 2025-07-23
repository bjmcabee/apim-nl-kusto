import json
import system_prompts

def generate_jsonl(data, output_file):
    """
    Generates a JSONL file from a list of dictionaries.

    Args:
        data (list): List of dictionaries to write to the JSONL file.
        output_file (str): Path to the output JSONL file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def create_message(user_content, assistant_content):
    return {
        "messages": [
            {"role": "system", "content": system_prompts.DEFAULT_KUSTO_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ]
    }

# List to hold all data entries
data = []

# Add entries easily by calling create_message
data.append(create_message("What is the current tenant release status?", 
                            """GetTenantVersions
| extend Region = tolower(replace_string(regions, " ", ""))
| join kind = inner (GetRegionalAppsVersion | where component == "RegionalResourceProvider" | distinct Region, ClusterName, sdpStage | where ClusterName !contains "prv-01") on Region
| where sku !contains "V2"
| summarize count() by sdpStage1, version, tostring(releaseChannel)
| order by sdpStage1 asc"""))

data.append(create_message("", 
                            """

"""))

generate_jsonl(data, "output.jsonl")

