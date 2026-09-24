[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$EnvironmentUrl = "https://orgb46f68a9.crm.dynamics.com",
    [string]$SchemaPath = (Join-Path $PSScriptRoot "..\dataverse\schema.json"),
    [string]$CliMappingPath = (Join-Path $PSScriptRoot "..\dataverse\dataverse-cli-mappings.json"),
    [string]$SolutionUniqueName,
    [ValidateSet("PacToken", "DataverseCli")][string]$Transport = "PacToken",
    [switch]$SkipPublish,
    [switch]$KeysOnly
)

$ErrorActionPreference = "Stop"
$schema = Get-Content -LiteralPath $SchemaPath -Raw | ConvertFrom-Json
$cliMappings = Get-Content -LiteralPath $CliMappingPath -Raw | ConvertFrom-Json
$prefix = $schema.publisherPrefix
$targetSolutionUniqueName = if ($SolutionUniqueName) { $SolutionUniqueName } else { $schema.solutionUniqueName }
$apiRoot = "$($EnvironmentUrl.TrimEnd('/'))/api/data/v9.2"

function New-Label([string]$Text) {
    return @{
        "@odata.type" = "Microsoft.Dynamics.CRM.Label"
        LocalizedLabels = @(@{
            "@odata.type" = "Microsoft.Dynamics.CRM.LocalizedLabel"
            Label = $Text
            LanguageCode = 1033
        })
    }
}

function Get-SchemaName([string]$Name) {
    return "${prefix}_$Name"
}

function Get-LogicalName([string]$Name) {
    return (Get-SchemaName $Name).ToLowerInvariant()
}

foreach ($table in $schema.tables) {
    $primaryIdLogicalName = Get-LogicalName "$($table.name)id"
    foreach ($column in $table.columns) {
        if ((Get-LogicalName $column.name) -eq $primaryIdLogicalName) {
            throw "Column '$($column.name)' on table '$($table.name)' conflicts with the Dataverse primary key '$primaryIdLogicalName'."
        }
    }
}

function Get-Token {
    $tokenOutput = @(& pac auth token 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "PAC authentication failed. Select the target environment with pac env select and retry."
    }

    $token = $tokenOutput | Where-Object { $_ -is [string] -and $_.Length -gt 500 } | Sort-Object Length -Descending | Select-Object -First 1
    if ([string]::IsNullOrWhiteSpace($token)) {
        throw "PAC didn't return an access token."
    }
    return $token.Trim()
}

$script:headers = @{
    Accept = "application/json"
    "Content-Type" = "application/json; charset=utf-8"
    "OData-MaxVersion" = "4.0"
    "OData-Version" = "4.0"
    "MSCRM.SolutionUniqueName" = $targetSolutionUniqueName
}
if ($Transport -eq "PacToken") {
    $script:headers.Authorization = "Bearer $(Get-Token)"
}
elseif (-not (Get-Command dataverse -ErrorAction SilentlyContinue)) {
    throw "Dataverse CLI isn't installed. Run: npm install -g @microsoft/dataverse"
}

function Invoke-DataverseRequest {
    param(
        [ValidateSet("GET", "POST")][string]$Method,
        [string]$Path,
        [object]$Body
    )

    if ($Transport -eq "DataverseCli") {
        $arguments = @(
            "api", "request",
            "--target", $cliMappings.target,
            "--environment", $EnvironmentUrl,
            "--path", "$($cliMappings.apiRoot)/$Path",
            "--method", $Method
        )
        foreach ($header in $cliMappings.headers.PSObject.Properties) {
            if ($header.Name -in @("OData-MaxVersion", "OData-Version")) {
                continue
            }
            $value = ([string]$header.Value).Replace("{solutionUniqueName}", $targetSolutionUniqueName)
            $arguments += @("--header", "$($header.Name):$value")
        }

        $bodyFile = $null
        try {
            if ($null -ne $Body) {
                $bodyFile = Join-Path ([System.IO.Path]::GetTempPath()) "dataverse-$([guid]::NewGuid().ToString('N')).json"
                $Body | ConvertTo-Json -Depth 30 -Compress | Set-Content -LiteralPath $bodyFile -Encoding utf8NoBOM
                $arguments += @("--body-file", $bodyFile)
            }

            $output = @(& dataverse @arguments 2>&1)
            if ($LASTEXITCODE -ne 0) {
                $message = $output -join [Environment]::NewLine
                $exception = [System.InvalidOperationException]::new("Dataverse CLI request failed: $message")
                if ($message -match "(^|\D)404(\D|$)|Not Found|0x80060888|does not exist on type") {
                    $exception.Data["StatusCode"] = 404
                }
                throw $exception
            }

            $response = ($output -join [Environment]::NewLine).Trim()
            if ([string]::IsNullOrWhiteSpace($response)) {
                return $null
            }
            return $response | ConvertFrom-Json
        }
        finally {
            if ($bodyFile -and (Test-Path -LiteralPath $bodyFile)) {
                Remove-Item -LiteralPath $bodyFile -Force
            }
        }
    }

    $parameters = @{
        Uri = "$apiRoot/$Path"
        Method = $Method
        Headers = $script:headers
        UseBasicParsing = $true
    }
    if ($null -ne $Body) {
        $parameters.Body = $Body | ConvertTo-Json -Depth 30 -Compress
    }
    return Invoke-RestMethod @parameters
}

function Test-MetadataExists([string]$Path) {
    try {
        $null = Invoke-DataverseRequest -Method GET -Path $Path
        return $true
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($_.Exception.Data.Contains("StatusCode")) {
            $statusCode = $_.Exception.Data["StatusCode"]
        }
        if ($statusCode -eq 404) {
            return $false
        }
        throw
    }
}

function New-RequiredLevel([bool]$Required) {
    return @{
        Value = $(if ($Required) { "ApplicationRequired" } else { "None" })
        CanBeChanged = $true
        ManagedPropertyLogicalName = "canmodifyrequirementlevelsettings"
    }
}

function New-ColumnMetadata($Column) {
    $typeMapping = $cliMappings.columnTypes.PSObject.Properties[$Column.type].Value
    if ($null -eq $typeMapping) {
        throw "Unsupported column type '$($Column.type)'."
    }

    $metadata = @{
        SchemaName = Get-SchemaName $Column.name
        DisplayName = New-Label $Column.displayName
        Description = New-Label "$($Column.displayName) for TD CAT contents valuation."
        RequiredLevel = New-RequiredLevel ([bool]$Column.required)
        IsAuditEnabled = @{ Value = $true }
    }

    switch ($Column.type) {
        "String" {
            $metadata["@odata.type"] = $typeMapping.odataType
            $metadata.AttributeType = $typeMapping.attributeType
            $metadata.AttributeTypeName = @{ Value = $typeMapping.attributeTypeName }
            $metadata.FormatName = @{ Value = "Text" }
            $metadata.MaxLength = $(if ($Column.maxLength) { [int]$Column.maxLength } else { 200 })
        }
        "Memo" {
            $metadata["@odata.type"] = $typeMapping.odataType
            $metadata.AttributeType = $typeMapping.attributeType
            $metadata.AttributeTypeName = @{ Value = $typeMapping.attributeTypeName }
            $metadata.Format = "TextArea"
            $metadata.MaxLength = 1048576
        }
        "Integer" {
            $metadata["@odata.type"] = $typeMapping.odataType
            $metadata.AttributeType = $typeMapping.attributeType
            $metadata.AttributeTypeName = @{ Value = $typeMapping.attributeTypeName }
            $metadata.Format = "None"
            $metadata.MinValue = $(if ($null -ne $Column.min) { [int]$Column.min } else { -2147483648 })
            $metadata.MaxValue = $(if ($null -ne $Column.max) { [int]$Column.max } else { 2147483647 })
        }
        "Decimal" {
            $metadata["@odata.type"] = $typeMapping.odataType
            $metadata.AttributeType = $typeMapping.attributeType
            $metadata.AttributeTypeName = @{ Value = $typeMapping.attributeTypeName }
            $metadata.Precision = $(if ($Column.precision) { [int]$Column.precision } else { 2 })
            $metadata.MinValue = -100000000000
            $metadata.MaxValue = 100000000000
        }
        "DateTime" {
            $metadata["@odata.type"] = $typeMapping.odataType
            $metadata.AttributeType = $typeMapping.attributeType
            $metadata.AttributeTypeName = @{ Value = $typeMapping.attributeTypeName }
            $metadata.Format = "DateAndTime"
            $metadata.DateTimeBehavior = @{ Value = "UserLocal" }
        }
        "Boolean" {
            $metadata["@odata.type"] = $typeMapping.odataType
            $metadata.AttributeType = $typeMapping.attributeType
            $metadata.AttributeTypeName = @{ Value = $typeMapping.attributeTypeName }
            $metadata.DefaultValue = $false
            $metadata.OptionSet = @{
                TrueOption = @{ Value = 1; Label = New-Label "Yes" }
                FalseOption = @{ Value = 0; Label = New-Label "No" }
                OptionSetType = "Boolean"
            }
        }
        "Choice" {
            $metadata["@odata.type"] = $typeMapping.odataType
            $metadata.AttributeType = $typeMapping.attributeType
            $metadata.AttributeTypeName = @{ Value = $typeMapping.attributeTypeName }
            $optionValue = 100000000
            $options = @()
            foreach ($option in $Column.options) {
                $options += @{ Value = $optionValue; Label = New-Label ([string]$option) }
                $optionValue++
            }
            $metadata.OptionSet = @{
                "@odata.type" = "Microsoft.Dynamics.CRM.OptionSetMetadata"
                IsGlobal = $false
                OptionSetType = "Picklist"
                Options = $options
            }
        }
        "File" {
            $metadata["@odata.type"] = $typeMapping.odataType
            $metadata.AttributeTypeName = @{ Value = $typeMapping.attributeTypeName }
            $metadata.MaxSizeInKB = [int]$Column.maxSizeInKB
        }
        default { throw "Unsupported column type '$($Column.type)'." }
    }
    return $metadata
}

if (-not $KeysOnly) {
foreach ($table in $schema.tables) {
    $logicalName = Get-LogicalName $table.name
    if (Test-MetadataExists "EntityDefinitions(LogicalName='$logicalName')?`$select=MetadataId") {
        Write-Host "Table exists: $logicalName"
    }
    elseif ($PSCmdlet.ShouldProcess($logicalName, "Create Dataverse table")) {
        $primaryName = Get-SchemaName $table.primaryName
        $body = @{
            "@odata.type" = $cliMappings.metadataTypes.table
            SchemaName = Get-SchemaName $table.name
            DisplayName = New-Label $table.displayName
            DisplayCollectionName = New-Label $table.displayCollectionName
            Description = New-Label $table.description
            OwnershipType = "UserOwned"
            IsActivity = $false
            HasActivities = $false
            HasNotes = $true
            IsAuditEnabled = @{ Value = $true }
            Attributes = @(@{
                "@odata.type" = $cliMappings.metadataTypes.primaryName
                AttributeType = "String"
                AttributeTypeName = @{ Value = "StringType" }
                SchemaName = $primaryName
                DisplayName = New-Label $table.displayName
                Description = New-Label "Primary name for $($table.displayName)."
                RequiredLevel = New-RequiredLevel $true
                MaxLength = 200
                FormatName = @{ Value = "Text" }
                IsPrimaryName = $true
                IsAuditEnabled = @{ Value = $true }
            })
        }
        $null = Invoke-DataverseRequest -Method POST -Path "EntityDefinitions" -Body $body
        Write-Host "Created table: $logicalName"
    }
}

foreach ($table in $schema.tables) {
    $logicalName = Get-LogicalName $table.name
    foreach ($column in $table.columns) {
        $columnLogicalName = Get-LogicalName $column.name
        $path = "EntityDefinitions(LogicalName='$logicalName')/Attributes(LogicalName='$columnLogicalName')?`$select=MetadataId"
        if (Test-MetadataExists $path) {
            Write-Host "Column exists: $logicalName.$columnLogicalName"
        }
        elseif ($PSCmdlet.ShouldProcess("$logicalName.$columnLogicalName", "Create Dataverse column")) {
            $null = Invoke-DataverseRequest -Method POST -Path "EntityDefinitions(LogicalName='$logicalName')/Attributes" -Body (New-ColumnMetadata $column)
            Write-Host "Created column: $logicalName.$columnLogicalName"
        }
    }
}

foreach ($relationship in $schema.relationships) {
    $schemaName = Get-SchemaName $relationship.name
    $encodedFilter = [uri]::EscapeDataString("SchemaName eq '$schemaName'")
    $existing = Invoke-DataverseRequest -Method GET -Path "RelationshipDefinitions?`$select=MetadataId&`$filter=$encodedFilter"
    if ($existing.value.Count -gt 0) {
        Write-Host "Relationship exists: $schemaName"
        continue
    }
    if ($PSCmdlet.ShouldProcess($schemaName, "Create Dataverse relationship")) {
        $parentLogicalName = Get-LogicalName $relationship.parent
        $childLogicalName = Get-LogicalName $relationship.child
        $body = @{
            "@odata.type" = $cliMappings.metadataTypes.relationship
            SchemaName = $schemaName
            ReferencedEntity = $parentLogicalName
            ReferencedAttribute = "${parentLogicalName}id"
            ReferencingEntity = $childLogicalName
            CascadeConfiguration = @{
                Assign = "NoCascade"; Delete = "Restrict"; Merge = "NoCascade"; Reparent = "NoCascade"; Share = "NoCascade"; Unshare = "NoCascade"
            }
            Lookup = @{
                "@odata.type" = $cliMappings.metadataTypes.lookup
                AttributeType = "Lookup"
                AttributeTypeName = @{ Value = "LookupType" }
                SchemaName = Get-SchemaName $relationship.lookup
                DisplayName = New-Label $relationship.displayName
                Description = New-Label "$($relationship.displayName) relationship."
                RequiredLevel = New-RequiredLevel ([bool]$relationship.required)
                IsAuditEnabled = @{ Value = $true }
            }
        }
        $null = Invoke-DataverseRequest -Method POST -Path "RelationshipDefinitions" -Body $body
        Write-Host "Created relationship: $schemaName"
    }
}
}

foreach ($table in $schema.tables) {
    $logicalName = Get-LogicalName $table.name
    foreach ($key in $table.keys) {
        $keySchemaName = Get-SchemaName $key.name
        $encodedFilter = [uri]::EscapeDataString("SchemaName eq '$keySchemaName'")
        $existing = Invoke-DataverseRequest -Method GET -Path "EntityDefinitions(LogicalName='$logicalName')/Keys?`$select=MetadataId&`$filter=$encodedFilter"
        if ($existing.value.Count -gt 0) {
            Write-Host "Key exists: $keySchemaName"
            continue
        }
        if ($PSCmdlet.ShouldProcess($keySchemaName, "Create Dataverse alternate key")) {
            $body = @{
                "@odata.type" = $cliMappings.metadataTypes.key
                SchemaName = $keySchemaName
                DisplayName = New-Label $key.displayName
                KeyAttributes = @($key.columns | ForEach-Object { Get-LogicalName $_ })
            }
            $null = Invoke-DataverseRequest -Method POST -Path "EntityDefinitions(LogicalName='$logicalName')/Keys" -Body $body
            Write-Host "Created key: $keySchemaName"
        }
    }
}

if (-not $SkipPublish -and $PSCmdlet.ShouldProcess($targetSolutionUniqueName, "Publish Dataverse metadata")) {
    $null = Invoke-DataverseRequest -Method POST -Path "PublishAllXml" -Body @{}
    Write-Host "Published Dataverse metadata."
}