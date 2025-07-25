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
""",

    "Get the VersionMappings": """
```kql
All('Orchestration')
| where PreciseTimeStamp > ago(6h)
| where eventType == "GotSortedVersionMappings"
| extend msg = parse_json(message)
| mv-expand msg
| extend 
    channel = tostring(msg["ReleaseChannel"]),
    targetVersion = tostring(msg["TargetVersion"])
| summarize arg_max(PreciseTimeStamp, targetVersion) by Region, channel
| evaluate pivot(channel, any(targetVersion))
| join kind=leftouter GetSDPRegions on Region
| extend SdpStage = coalesce(SdpStage, 6)
| project Region, SdpStage, GenAI, Preview, Default, Stable, Stable2, Stable3
| order by SdpStage asc, Region asc 
```
""",

    "Get the VersionMappings in EastUS": """
```kql
All('Orchestration')
| where PreciseTimeStamp > ago(6h)
| where eventType == "GotSortedVersionMappings"
| extend msg = parse_json(message)
| mv-expand msg
| extend 
    channel = tostring(msg["ReleaseChannel"]),
    targetVersion = tostring(msg["TargetVersion"])
| summarize arg_max(PreciseTimeStamp, targetVersion) by Region, channel
| evaluate pivot(channel, any(targetVersion))
| join kind=leftouter GetSDPRegions on Region
| extend SdpStage = coalesce(SdpStage, 6)
| project Region, SdpStage, GenAI, Preview, Default, Stable, Stable2, Stable3
| order by SdpStage asc, Region asc 
| where Region == "East US"
```
""",

    "Get the ResourceProvider Versions": """
```kql
All('Orchestration')
| where TIMESTAMP >= ago(6h)
| where eventType in ("HealthMonitorRegionalResourceProviderReachable")
| where eventType !contains "Healthy"
| extend msg=replace("\\"{", "{", replace("}\\"", "}", replace(@"\\\\", "", message)))
| extend msg=parse_json(msg), eventType = replace("HealthMonitorRegional", "", eventType)
| project PreciseTimeStamp, ClusterName=tostring(msg.ClusterName), Region=msg.Region, RuntimeVersion= iff(eventType contains "Smapi", msg.ResponseBody.version, replace("'", "", tostring(msg.ResponseBody.RuntimeVersion))), eventType, Endpoint=tostring(msg.Endpoint) // , msg.StatusCode
| extend t=PreciseTimeStamp
| where ClusterName !endswith "-prv-01"
| summarize argmax(t, ClusterName, tostring(RuntimeVersion), tostring(Endpoint)) by eventType, tostring(Region)
| join kind=inner (GetRegionalAppsVersion()
| where component == "RegionalResourceProvider"
| summarize by sdpStage, Region
| extend Region = replace(" ", "", tolower(Region))
| order by sdpStage asc)
on Region
| project sdpStage, Region, ClusterName= max_t_ClusterName, RuntimeVersion= max_t_RuntimeVersion, eventType, Time=max_t, Endpoint= max_t_Endpoint
| summarize dcount(Region) by RuntimeVersion, sdpStage
| order by sdpStage asc
```
""",

    "Get the ResourceProvider Versions in Stage 1": """
```kql
All('Orchestration')
| where TIMESTAMP >= ago(6h)
| where eventType in ("HealthMonitorRegionalResourceProviderReachable")
| where eventType !contains "Healthy"
| extend msg=replace("\\"{", "{", replace("}\\"", "}", replace(@"\\\\", "", message)))
| extend msg=parse_json(msg), eventType = replace("HealthMonitorRegional", "", eventType)
| project PreciseTimeStamp, ClusterName=tostring(msg.ClusterName), Region=msg.Region, RuntimeVersion= iff(eventType contains "Smapi", msg.ResponseBody.version, replace("'", "", tostring(msg.ResponseBody.RuntimeVersion))), eventType, Endpoint=tostring(msg.Endpoint) // , msg.StatusCode
| extend t=PreciseTimeStamp
| where ClusterName !endswith "-prv-01"
| summarize argmax(t, ClusterName, tostring(RuntimeVersion), tostring(Endpoint)) by eventType, tostring(Region)
| join kind=inner (GetRegionalAppsVersion()
| where component == "RegionalResourceProvider"
| summarize by sdpStage, Region
| extend Region = replace(" ", "", tolower(Region))
| order by sdpStage asc)
on Region
| project sdpStage, Region, ClusterName= max_t_ClusterName, RuntimeVersion= max_t_RuntimeVersion, eventType, Time=max_t, Endpoint= max_t_Endpoint
| summarize dcount(Region) by RuntimeVersion, sdpStage
| order by sdpStage asc
| where sdpStage == "Stage_1"
```
""",

    "Get the ResourceProvider Versions in East US": """
```kql
All('Orchestration')
| where TIMESTAMP >= ago(6h)
| where eventType in ("HealthMonitorRegionalResourceProviderReachable")
| where eventType !contains "Healthy"
| extend msg=replace("\\"{", "{", replace("}\\"", "}", replace(@"\\\\", "", message)))
| extend msg=parse_json(msg), eventType = replace("HealthMonitorRegional", "", eventType)
| project PreciseTimeStamp, ClusterName=tostring(msg.ClusterName), Region=msg.Region, RuntimeVersion= iff(eventType contains "Smapi", msg.ResponseBody.version, replace("'", "", tostring(msg.ResponseBody.RuntimeVersion))), eventType, Endpoint=tostring(msg.Endpoint) // , msg.StatusCode
| extend t=PreciseTimeStamp
| where ClusterName !endswith "-prv-01"
| summarize argmax(t, ClusterName, tostring(RuntimeVersion), tostring(Endpoint)) by eventType, tostring(Region)
| join kind=inner (GetRegionalAppsVersion()
| where component == "RegionalResourceProvider"
| summarize by sdpStage, Region
| extend Region = replace(" ", "", tolower(Region))
| order by sdpStage asc)
on Region
| project sdpStage, Region, ClusterName= max_t_ClusterName, RuntimeVersion= max_t_RuntimeVersion, eventType, Time=max_t, Endpoint= max_t_Endpoint
| summarize dcount(Region) by RuntimeVersion, Region
| where Region == "eastus"
```
""",

    "where is the 0.48.23550.0 Tenant Release": """
```kql
GetTenantVersions
| extend Region = tolower(replace_string(regions, " ", ""))
| join kind = inner (GetRegionalAppsVersion | where component == "RegionalResourceProvider" | distinct Region, ClusterName, sdpStage | where ClusterName !contains "prv-01") on Region
| where sku !contains "V2"
| summarize count() by sdpStage1, version, releaseChannel
| order by sdpStage1 asc
| where version == "0.48.23550.0"
```
""",
}