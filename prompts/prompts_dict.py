# /e:/apim-nl-kusto/prompts/prompts_dict.py

prompts_dict = {
    "What is the current Tenant Release Status?": """
GetTenantVersions
| extend Region = tolower(replace_string(regions, " ", ""))
| join kind = inner (GetRegionalAppsVersion | where component == "RegionalResourceProvider" | distinct Region, ClusterName, sdpStage | where ClusterName !contains "prv-01") on Region
| where sku !contains "V2"
| summarize count() by sdpStage1, version, releaseChannel
| order by sdpStage1 asc
    """,
    
    "How do I create a resource group in Azure?": "You can create a resource group using the Azure Portal, Azure CLI, or ARM templates.",
    # Add more question-answer pairs below
}