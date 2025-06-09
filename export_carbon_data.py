import os
import requests
import json
from azure.identity import DefaultAzureCredential

# Constants (update as needed)
# Try multiple API versions and endpoints
API_ENDPOINTS = [
    "https://management.azure.com/providers/Microsoft.Carbon/exports?api-version=2023-10-01-preview",
    "https://management.azure.com/providers/Microsoft.CostManagement/exports?api-version=2023-03-01",
    "https://management.azure.com/providers/Microsoft.Consumption/usageDetails?api-version=2023-05-01"
]
OUTPUT_FILE = "carbon_emissions_export.json"

def try_carbon_api_extraction():
    """Try to extract data from Carbon API with fallback options"""
    
    # Authenticate using Azure Default Credentials
    try:
        credential = DefaultAzureCredential()
        token = credential.get_token("https://management.azure.com/.default").token
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Try different API endpoints
    for api_url in API_ENDPOINTS:
        print(f"🔍 Trying API endpoint: {api_url.split('/')[-2]}")
        
        try:
            # For Carbon API
            if "Carbon" in api_url:
                body = {
                    "reportType": "OverallSummaryReport",
                    "format": "Json"
                }
                response = requests.post(api_url, headers=headers, json=body)
            else:
                # For other APIs, try GET request
                response = requests.get(api_url, headers=headers)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                with open(OUTPUT_FILE, "w") as f:
                    f.write(response.text)
                print(f"✅ Data exported to {OUTPUT_FILE}")
                return True
            elif response.status_code == 404:
                print(f"   ⚠️ API not available: {response.json().get('error', {}).get('message', 'Not found')}")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text[:200]}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")
    
    print("\n⚠️ All Carbon APIs failed. This might be because:")
    print("   • Carbon Optimization API is not available in your subscription/region")
    print("   • Your account doesn't have the required permissions")
    print("   • The service is in preview and not widely available yet")
    print("\n💡 Falling back to demo data generation...")
    
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
    print("🌱 Attempting to extract carbon emissions data from Azure...")
    
    success = try_carbon_api_extraction()
    
    if not success:
        print("\n🔄 Carbon API extraction failed, using fallback demo data...")
        success = generate_fallback_data()
    
    if success:
        print(f"\n🎉 Data extraction completed! File: {OUTPUT_FILE}")
    else:
        print(f"\n❌ All extraction methods failed!")
