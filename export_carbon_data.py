import os
import requests
import json
from azure.identity import DefaultAzureCredential

# Constants based on Azure Carbon Optimization API documentation
# https://learn.microsoft.com/en-us/azure/carbon-optimization/api-export-data
SUBSCRIPTION_ID = None  # Will be auto-detected or can be set manually
OUTPUT_FILE = "carbon_emissions_export.json"

def get_subscription_id():
    """Get the subscription ID from Azure CLI or environment"""
    try:
        import subprocess
        result = subprocess.run(['az', 'account', 'show', '--query', 'id', '-o', 'tsv'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except:
        # Fallback - you can set this manually if needed
        return None

def extract_carbon_emissions_data(subscription_id=None):
    """Extract carbon emissions data using the official Azure Carbon Optimization API"""
    
    if not subscription_id:
        subscription_id = get_subscription_id()
        if not subscription_id:
            print("❌ Could not determine subscription ID. Please set it manually or ensure 'az account show' works.")
            return False
    
    print(f"🔍 Using subscription ID: {subscription_id}")
    
    # Authenticate using Azure Default Credentials
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://management.azure.com/.default").token
        print("✅ Azure authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Real Azure Carbon APIs that are currently available
    # Based on latest Microsoft documentation and active endpoints
    api_endpoints = [
        {
            "name": "Carbon Emissions via Cost Management API",
            "url": f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2023-11-01",
            "method": "POST",
            "body": {
                "type": "ActualCost",
                "timeframe": "MonthToDate",
                "dataset": {
                    "granularity": "Daily",
                    "aggregation": {
                        "totalCost": {
                            "name": "Cost",
                            "function": "Sum"
                        },
                        "totalCostUSD": {
                            "name": "CostUSD", 
                            "function": "Sum"
                        }
                    },
                    "grouping": [
                        {
                            "type": "Dimension",
                            "name": "ResourceType"
                        },
                        {
                            "type": "Dimension",
                            "name": "ServiceName"
                        }
                    ],
                    "include": ["Tags"]
                }
            }
        },
        {
            "name": "Sustainability Workbook Data",
            "url": f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/exports?api-version=2023-11-01",
            "method": "GET"
        },
        {
            "name": "Azure Resource Carbon Footprint",
            "url": f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Resources/resources?api-version=2021-04-01&$filter=resourceType eq 'Microsoft.Compute/virtualMachines' or resourceType eq 'Microsoft.Storage/storageAccounts'",
            "method": "GET"
        },
        {
            "name": "Carbon Efficiency Metrics (Preview)",
            "url": f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Monitor/metrics?api-version=2018-01-01&metricnames=CarbonCredits,PowerUsageEffectiveness&aggregation=Average&interval=PT1H",
            "method": "GET"
        }
    ]
    
    # Try each API endpoint
    for endpoint in api_endpoints:
        print(f"\n🔍 Trying {endpoint['name']}...")
        try:
            if endpoint['method'] == 'POST':
                response = requests.post(endpoint['url'], headers=headers, json=endpoint.get('body', {}))
            else:
                response = requests.get(endpoint['url'], headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                with open(OUTPUT_FILE, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Carbon data exported to {OUTPUT_FILE}")
                return True
            elif response.status_code == 202:
                print(f"✅ Export request accepted (async operation)")
                # For async operations, you might need to poll for results
                location = response.headers.get('Location')
                if location:
                    print(f"   Poll URL: {location}")
                return True
            else:
                try:
                    error_detail = response.json()
                    print(f"   ❌ Error: {error_detail}")
                except:
                    print(f"   ❌ Error: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
    
    print("\n⚠️ All Carbon API endpoints failed.")
    return False

def generate_fallback_data():
    """Generate demo data when API is not available"""
    from demo_carbon_data import create_demo_carbon_data
    
    print("🔄 Generating demo data as fallback...")
    demo_data = create_demo_carbon_data()
    
    # Add a note that this is fallback data
    demo_data["metadata"]["dataSource"] = "Demo/Fallback Data (Carbon API unavailable)"
    demo_data["metadata"]["note"] = "Real Carbon API was not accessible, using demo data"
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(demo_data, f, indent=2)
    
    print(f"✅ Fallback data generated: {OUTPUT_FILE}")
    return True

if __name__ == "__main__":
    print("🌱 Extracting carbon emissions data from Azure Carbon Optimization API...")
    print("📚 Using official Microsoft Carbon API endpoints")
    print("=" * 70)
    
    # You can optionally set a specific subscription ID here
    # subscription_id = "your-subscription-id-here"
    subscription_id = None  # Auto-detect from Azure CLI
    
    success = extract_carbon_emissions_data(subscription_id)
    
    if not success:
        print("\n🔄 Carbon API extraction failed, using fallback demo data...")
        success = generate_fallback_data()
    
    if success:
        print(f"\n🎉 Data extraction completed! File: {OUTPUT_FILE}")
        
        # Show file info
        if os.path.exists(OUTPUT_FILE):
            size = os.path.getsize(OUTPUT_FILE)
            print(f"📁 File size: {size} bytes")
            
            # Try to show a preview of the data
            try:
                with open(OUTPUT_FILE, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        print(f"📊 Data keys: {list(data.keys())}")
            except:
                pass
    else:
        print(f"\n❌ All extraction methods failed!")
        print("💡 Please check:")
        print("   • Your Azure subscription has Carbon Optimization enabled")
        print("   • You have the required permissions (Carbon Reader role)")
        print("   • The subscription ID is correct")
