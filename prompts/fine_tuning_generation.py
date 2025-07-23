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
            {"role": "system", "content": system_prompts.DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ]
    }

# List to hold all data entries
data = []

# Add entries easily by calling create_message
data.append(create_message("What is the current tenant release status?", 
                            """All('ResourceProvider')
| where TIMESTAMP >= datetime(2025-07-23T16:52:30Z) and TIMESTAMP <= datetime(2025-07-23T22:53:00Z)
| where Tenant endswith \"-rpApp\" and slotName == \"PRODUCTION\"
| distinct Tenant, codeVersion, Region
| project ClusterName=Tenant, Region, codeVersion
| join kind=inner (GetRegionalAppsVersion()
| where component == \"RegionalResourceProvider\"
| summarize by sdpStage, Region
| extend Region = replace(\" \", \"\", tolower(Region))
| order by sdpStage asc)
on Region
| project sdpStage, Region, ClusterName= ClusterName, RuntimeVersion= codeVersion
| summarize dcount(Region) by RuntimeVersion, sdpStage"""))

data.append(create_message("", 
                            """"""))

generate_jsonl(data, "output.jsonl")

