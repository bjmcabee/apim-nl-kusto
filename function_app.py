import azure.functions as func
import logging
import json
from helper_functions import *

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="HttpTrigger1")
@app.route(route="req", methods=["POST"])
def HttpTrigger1(req: func.HttpRequest) -> func.HttpResponse :
    logging.info('Python HTTP trigger function processed a request.')

    command = "GetTenantVersions |distinct serviceName"
    result = execute_kusto_query(command)

    # Return trigger
    logging.info(f"Query executed successfully: {result}")
    # for i, row in enumerate(result["primary_result"]):
    #     logging.info(f"Row {i + 1}: {row}")

    return func.HttpResponse("Executed Correctly.")

@app.function_name(name="BasicLLMCall")
@app.route(route="basic_llm_call", methods=["POST"])
def basic_llm_call(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to handle basic LLM calls.
    Accepts POST requests with a JSON body containing the prompt.
    """
    logging.info('Basic LLM call function processed a request.')

    try:
        # Extract the natural language prompt from the request
        prompt = get_prompt_from_request(req)
        response_message = execute_llm_call(prompt)

        logging.info(f"LLM response: {response_message}")

        return func.HttpResponse(
            json.dumps({"response": response_message}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.function_name(name="kustoNlQuery")
@app.route(route="kusto_nl_query", methods=["POST"])
def kusto_nl_query(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to convert natural language prompts to Kusto queries and execute them.
    Accepts POST requests with a natural language prompt and returns query results.
    """
    logging.info('Kusto NL query function processed a request.')

    try:
        # Extract the natural language prompt from the request
        prompt = get_prompt_from_request(req)

        logging.info(f"Processing natural language prompt: {prompt}")

        # TODO: Implement Kusto query generation from natural language
        kusto_query = generate_kusto_query_from_nl(prompt)
        
        # TODO: Implement Kusto query execution
        results = execute_kusto_query(kusto_query)
        
        # Return the results
        response_data = {
            "prompt": prompt,
            "generated_query": kusto_query,
            "results": results,
            "status": "success"
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": f"Internal server error: {str(e)}",
                "status": "error"
            }),
            status_code=500,
            mimetype="application/json"
        )
