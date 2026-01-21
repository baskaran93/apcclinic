# Deploy to Azure Script (Reuse Existing Plan)
$resourceGroup = "apcapi_group"
$location = "canadacentral"
$planName = "ASP-apcapigroup-8999"
$appName = "apc-doublemanda-backend-" + (Get-Random -Minimum 1000 -Maximum 9999)

Write-Host "Reusing Resource Group: $resourceGroup in $location..."
# az group create --name $resourceGroup --location $location # Idempotent

Write-Host "Reusing App Service Plan: $planName..."
# No need to create if it exists, but we can't easily change SKU if it fails.
# We will just create the webapp directly.

Write-Host "Creating Web App: $appName..."
az webapp create --name $appName --resource-group $resourceGroup --plan $planName --runtime "PYTHON:3.10"

Write-Host "Configuring Environment Variables..."
$envContent = Get-Content .env
$settings = @()
foreach ($line in $envContent) {
    if ($line -match "^[^#]*=[^#]*") {
        $settings += $line
    }
}
az webapp config appsettings set --name $appName --resource-group $resourceGroup --settings $settings

Write-Host "Configuring Startup Command..."
az webapp config set --name $appName --resource-group $resourceGroup --startup-file "startup.sh"

Write-Host "Zipping Application..."
$zipPath = Join-Path $PSScriptRoot "app_deploy.zip"
Remove-Item $zipPath -ErrorAction SilentlyContinue
$files = Get-ChildItem -Path $PSScriptRoot -Exclude ".venv", ".git", ".idea", "__pycache__", "*.zip", "app.zip", "appnew.zip"
Compress-Archive -Path $files -DestinationPath $zipPath -Update

Write-Host "Deploying Application via 'az webapp deployment source config-zip'..."
az webapp deployment source config-zip --name $appName --resource-group $resourceGroup --src $zipPath

Write-Host "Deployment Complete!"
Write-Host "URL: https://$appName.azurewebsites.net"
