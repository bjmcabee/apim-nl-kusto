import json
import system_prompts
import prompts_dict

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

# Add entries from prompts_dict by calling create_message for each key-value pair
for user_content, assistant_content in prompts_dict.prompts_dict.items():
    data.append(create_message(user_content, assistant_content))

generate_jsonl(data, "output.jsonl")

