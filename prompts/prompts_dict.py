# /e:/apim-nl-kusto/prompts/prompts_dict.py

prompts_dict = {
    "What is the current Tenant Release Status?": """
```kql
GetTenantVersions
| extend Region = tolower(replace_string(regions, " ", ""))
| join kind = inner (GetRegionalAppsVersion | where component == "RegionalResourceProvider" | distinct Region, ClusterName, sdpStage | where ClusterName !contains "prv-01") on Region
| where sku !contains "V2"
| summarize count() by sdpStage1, version, releaseChannel
| order by sdpStage1 asc
```
""",
    
    "What is the current SKU distribution in West Europe?": """
```kql
GetTenantVersions
| where regions contains "west europe"
| summarize count() by sku
| order by count_ desc
```
""",

    "How many services are quarantined in each stage?": """
```kql
GetQuarantinedServicesList
| extend jsonObject = parse_json(datetimeRanges)
| mv-expand jsonObject
| extend endDate = todatetime(jsonObject.endDateTime)
| where endDate > now() 
| distinct serviceName, sdpStage, quarantineType = "DateRange"
| union (GetQuarantinedServicesList
| where minorVersionNumbers != "[]"
| distinct serviceName, sdpStage,quarantineType = "MinorVersion")
| summarize quarantineType = min(quarantineType)  by serviceName, sdpStage
| summarize count() by sdpStage, quarantineType
| order by sdpStage asc
```
""",

    "How many services are quarantined?": """
```kql
GetQuarantinedServicesList
| extend jsonObject = parse_json(datetimeRanges)
| mv-expand jsonObject
| extend endDate = todatetime(jsonObject.endDateTime)
| where endDate > now() 
| distinct serviceName, sdpStage, quarantineType = "DateRange"
| union (GetQuarantinedServicesList
| where minorVersionNumbers != "[]"
| distinct serviceName, sdpStage,quarantineType = "MinorVersion")
| summarize quarantineType = min(quarantineType) by serviceName
| summarize count() by quarantineType
```
""",

    "What is the Current Windows Version By Stage?": """```kql
GetTenantVersions
| extend windowsVer = extract(@"(?i)(2019|2022)-Datacenter(?:-azure-edition)?", 0, windowsVersion)
| where sku !contains "v2"
| summarize count() by sdpStage, windowsVer
| where windowsVer != ""
| sort by sdpStage asc
```
"""

}