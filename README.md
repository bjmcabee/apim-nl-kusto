# apim-nl-kusto

Quickstart Ref: https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python

[NL Kusto Doc](https://loop.cloud.microsoft/p/eyJ1IjoiaHR0cHM6Ly9taWNyb3NvZnQuc2hhcmVwb2ludC5jb20vc2l0ZXMvMjViYWJmYzQtN2JiNC00NGEyLTgyNTctMjYzMjhhNTgyZTY0P25hdj1jejBsTWtaemFYUmxjeVV5UmpJMVltRmlabU0wTFRkaVlqUXRORFJoTWkwNE1qVTNMVEkyTXpJNFlUVTRNbVUyTkNaa1BXSWhPWFozYVhSRFdEQnhSWEZ6UVZaQlNXZDVjRW8xTVZOd2VUTlZkRUU1YUU1eVdEVlZYMVZsVVUxVVpsZFBPR3BpYTB4SVlsUmhUMHAyTVV4aWJuVnFUaVptUFRBeFdUZEpNbEUwVFZSR1YxTkNNMHRVVkV4T1ExbE9ORWcyVmtSUlRFdEVVMHNtWXowbE1rWW1abXgxYVdROU1TWmhQVXh2YjNCQmNIQW1jRDBsTkRCbWJIVnBaSGdsTWtac2IyOXdMWEJoWjJVdFkyOXVkR0ZwYm1WeUpuZzlKVGRDSlRJeWR5VXlNaVV6UVNVeU1sUXdVbFJWU0hoMFlWZE9lV0l6VG5aYWJsRjFZekpvYUdOdFZuZGlNbXgxWkVNMWFtSXlNVGhaYVVVMVpHNWtjR1JGVGxsTlNFWkdZMWhPUWxaclJrcGFNMngzVTJwVmVGVXpRalZOTVZZd1VWUnNiMVJ1U2xsT1ZsWm1WbGRXVWxSV1VtMVdNRGcwWVcxS2NsUkZhR2xXUjBaUVUyNVplRlJIU25Wa1YzQlBaa1JCZUZkVVpFcE5iRVV3VTJ0S1VWSnNhR0ZTTUdoSFZtdFdTMUpWYkV0WFJURlRWV3RrU2swd2JFTlJlazBsTTBRbE1qSWxNa01sTWpKcEpUSXlKVE5CSlRJeU5qWmxObVkyTWpBdE5EZzBaUzAwWkdGbExUbGpObU10TXpFNU16WTNOV1l3TTJWbUpUSXlKVGRFIn0%3D)

## LOCAL SETTINGS VALUES
Get Foundry key from [Foundry Resource](https://ai.azure.com/foundryProject/overview?wsid=/subscriptions/a200340d-6b82-494d-9dbf-687ba6e33f9e/resourceGroups/apimnlkustofunction/providers/Microsoft.CognitiveServices/accounts/apimnlkusto-foundry/projects/apim-nl-kusto&tid=72f988bf-86f1-41af-91ab-2d7cd011db47)

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python", 
    "AI_FOUNDRY_API_KEY": "<>",
    "AZURE_OPENAI_ENDPOINT": "https://apimnlkusto-foundry.openai.azure.com/",
    "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4o-mini",
    "AZURE_OPENAI_API_VERSION": "2025-01-01-preview"
  }
}
```