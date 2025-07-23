import azure.functions as func
import logging
from azure.kusto.data import KustoClient
from utils import Utils
import os
from openai import AzureOpenAI
from prompts.system_prompts import DEFAULT_SYSTEM_PROMPT

CONFIG_FILE_NAME = "config.json"

def generate_kusto_query_from_nl(prompt: str) -> str:
    """
    Placeholder function to generate Kusto query from natural language prompt.
    
    Args:
        prompt (str): Natural language description of the query
        
    Returns:
        str: Generated Kusto query
    """
    # TODO: Implement AI/LLM integration to convert natural language to Kusto
    # This could integrate with Azure OpenAI, OpenAI API, or other language models
    # For now, return a placeholder query with the prompt
    
    logging.info(f"Generating Kusto query for prompt: {prompt}")

    kql_query = execute_llm_call(
        user_prompt=prompt,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        return_query_only=True
    )

    return kql_query.strip()

def get_prompt_from_request(req: func.HttpRequest) -> str:
    """
    Extracts the 'prompt' parameter from the HTTP request.
    
    Args:
        req (func.HttpRequest): The HTTP request object
        
    Returns:
        str: The prompt string if found, otherwise None
    """
    prompt = req.params.get('prompt')
    if not prompt:
        try:
            req_body = req.get_json()
            if req_body:
                prompt = req_body.get('prompt')
        except ValueError as e:
            logging.error(f"Failed to parse JSON body: {e}")
            return None
    return prompt

def execute_llm_call(
    user_prompt: str, 
    system_prompt: str = None, 
    return_query_only: bool = True,
    return_full_response: bool = False
) -> str:
    """
    Execute LLM call to generate Kusto queries from natural language.
    
    Args:
        user_prompt (str): The natural language question or request
        system_prompt (str, optional): Custom system prompt. If None, uses default Kusto expert prompt
        return_query_only (bool, optional): If True, extracts only the KQL query from response. Default True
        return_full_response (bool, optional): If True, returns the full API response object. Default False
        
    Returns:
        str or dict: Generated Kusto query string, or full response object if return_full_response=True
    """
    if not user_prompt:
        raise ValueError("User prompt cannot be empty")

    messages = [{"role": "user", "content": user_prompt}]

    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    client = AzureOpenAI(
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_version="2025-01-01-preview",
        api_key=os.environ.get("AI_FOUNDRY_API_KEY")
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1,  # Lower temperature for more consistent query generation
        max_tokens=1000
    )

    logging.info(f"LLM response for query generation: {response.choices[0].message.content}")

    if return_full_response:
        return response

    response_content = response.choices[0].message.content

    if return_query_only:
        return extract_kql_query(response_content)
    
    return response_content

def extract_kql_query(response_content: str) -> str:
    """
    Extract KQL query from LLM response content.
    
    Args:
        response_content (str): The full LLM response
        
    Returns:
        str: Extracted KQL query
    """
    import re
    
    # Look for KQL code blocks
    kql_pattern = r'```kql\s*(.*?)\s*```'
    match = re.search(kql_pattern, response_content, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    # If no code block found, look for common KQL patterns
    # This is a fallback for cases where the response doesn't use code blocks
    lines = response_content.split('\n')
    kql_lines = []
    
    for line in lines:
        stripped_line = line.strip()
        # Skip empty lines and comments
        if not stripped_line or stripped_line.startswith('//'):
            continue
        # Look for typical KQL operators and table names
        if any(keyword in stripped_line for keyword in ['|', 'where', 'summarize', 'project', 'order', 'join', 'extend', 'distinct']):
            kql_lines.append(stripped_line)
        # Also include lines that look like table names (start with capital letter)
        elif stripped_line and stripped_line[0].isupper() and not any(char in stripped_line for char in ['.', ':', ';']):
            kql_lines.append(stripped_line)
    
    if kql_lines:
        return '\n'.join(kql_lines)
    
    # If nothing found, return the original content
    logging.warning("Could not extract KQL query from response, returning full content")
    return response_content.strip()

def execute_kusto_query(query: str) -> dict:
    """
    Placeholder function to execute Kusto query against Azure Data Explorer.
    
    Args:
        query (str): Kusto query to execute
        
    Returns:
        dict: Query results and metadata
    """
    # TODO: Implement actual Kusto query execution
    # This should connect to Azure Data Explorer using:
    # - Azure SDK for Python (azure-kusto-data)
    # - Managed Identity for authentication
    # - Proper error handling and retry logic

    config_dict = Utils.load_configs(CONFIG_FILE_NAME)
    kusto_uri = config_dict["kustoUri"]
    database_name = config_dict["databaseName"]
    authentication_mode = config_dict["authenticationMode"]

    kusto_connection_string = Utils.Authentication.generate_connection_string(kusto_uri, authentication_mode)
    
    #Handle Null here
    if not kusto_connection_string:
        Utils.error_handler("Connection String error. Please validate your configuration file.")
    else:
        with KustoClient(kusto_connection_string) as kusto_client:
            logging.info(f"Executing Kusto query: {query[:100]}...")
            response = kusto_client.execute(database_name, query)
            logging.info("Query executed successfully.")
            logging.debug(f"Query response: {response}")
            # Convert KustoResultTable to list of dicts for JSON serialization
            result_table = response.primary_results[0]
            columns = [col.column_name for col in result_table.columns]
            rows = [dict(zip(columns, row)) for row in result_table.rows]
            return rows
        