import os
import requests
from azure.identity import DefaultAzureCredential

# Constants (update as needed)
API_URL = "https://management.azure.com/providers/Microsoft.Carbon/exports?api-version=2023-10-01-preview"
OUTPUT_FILE = "carbon_emissions_export.json"

# Authenticate using Azure Default Credentials (works in Azure Cloud Shell, VS Code, or with AZ CLI login)
credential = DefaultAzureCredential()
token = credential.get_token("https://management.azure.com/.default").token

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Example request body for OverallSummaryReport (see Azure docs for more options)
body = {
    "reportType": "OverallSummaryReport",
    "format": "Json"
}

response = requests.post(API_URL, headers=headers, json=body)

if response.status_code == 200:
    with open(OUTPUT_FILE, "w") as f:
        f.write(response.text)
    print(f"Data exported to {OUTPUT_FILE}")
else:
    print(f"Failed to export data: {response.status_code} {response.text}")
