#!/usr/bin/env python3
"""
Azure Carbon Emissions Data Extractor
Uses live Azure APIs to extract carbon footprint and sustainability data.
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
import subprocess

class AzureCarbonExtractor:
    def __init__(self, subscription_id=None):
        self.subscription_id = subscription_id or self._get_subscription_id()
        self.credential = None
        self.token = None
        self.output_file = "azure_carbon_data.json"
        self.csv_file = "azure_carbon_data.csv"
        
    def _get_subscription_id(self):
        """Auto-detect subscription ID from Azure CLI"""
        try:
            result = subprocess.run(['az', 'account', 'show', '--query', 'id', '-o', 'tsv'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            print(f"⚠️ Could not auto-detect subscription ID: {e}")
            return None
            
    def authenticate(self):
        """Authenticate with Azure and get access token"""
        try:
            self.credential = DefaultAzureCredential()
            self.token = self.credential.get_token("https://management.azure.com/.default").token
            print("✅ Azure authentication successful")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
            
    def get_headers(self):
        """Get HTTP headers with authentication"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_cost_management_data(self):
        """Get data from Azure Cost Management API (includes some carbon metrics)"""
        print("🔍 Querying Azure Cost Management API...")
        
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
        
        # Query for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        body = {
            "type": "ActualCost",
            "timeframe": "Custom",
            "timePeriod": {
                "from": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
            },
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
                        "name": "ServiceName"
                    },
                    {
                        "type": "Dimension", 
                        "name": "ResourceLocation"
                    },
                    {
                        "type": "Dimension",
                        "name": "ResourceGroupName"
                    }
                ]
            }
        }
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=body)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Cost Management data retrieved: {len(data.get('properties', {}).get('rows', []))} rows")
                return data
            else:
                print(f"❌ Cost Management API failed: {response.status_code} - {response.text[:200]}")
                return None
        except Exception as e:
            print(f"❌ Cost Management API error: {e}")
            return None
    
    def get_resource_data(self):
        """Get Azure resource data to calculate carbon footprint"""
        print("🔍 Querying Azure Resource Graph for carbon-relevant resources...")
        
        # Use Azure Resource Graph API (correct endpoint)
        url = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01"
        
        # Resource Graph query to get carbon-relevant resources
        query = """
        Resources
        | where type in~ (
            'microsoft.compute/virtualmachines',
            'microsoft.storage/storageaccounts',
            'microsoft.containerservice/managedclusters',
            'microsoft.sql/servers',
            'microsoft.dbforpostgresql/servers',
            'microsoft.web/serverfarms',
            'microsoft.network/loadbalancers'
        )
        | project name, type, location, resourceGroup, subscriptionId, tags
        | limit 1000
        """
        
        request_body = {
            "subscriptions": [self.subscription_id],
            "query": query
        }
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=request_body)
            if response.status_code == 200:
                data = response.json()
                resources = data.get('data', [])
                print(f"✅ Resource data retrieved: {len(resources)} carbon-relevant resources")
                return resources
            else:
                print(f"⚠️ Resource Graph API failed: {response.status_code} - {response.text[:200]}")
                # Fallback to simpler approach
                return self.get_resource_data_fallback()
        except Exception as e:
            print(f"⚠️ Resource Graph API error: {e}")
            # Fallback to simpler approach
            return self.get_resource_data_fallback()
    
    def get_resource_data_fallback(self):
        """Fallback method to get resource data using simpler API"""
        print("🔄 Trying fallback resource API...")
        
        # Use simple Resource Manager API
        url = f"https://management.azure.com/subscriptions/{self.subscription_id}/resources?api-version=2021-04-01"
        
        try:
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                data = response.json()
                all_resources = data.get('value', [])
                
                # Filter for carbon-relevant resources
                carbon_resource_types = [
                    'Microsoft.Compute/virtualMachines',
                    'Microsoft.Storage/storageAccounts',
                    'Microsoft.ContainerService/managedClusters',
                    'Microsoft.Sql/servers',
                    'Microsoft.DBforPostgreSQL/servers',
                    'Microsoft.Web/serverFarms',
                    'Microsoft.Network/loadBalancers'
                ]
                
                resources = [r for r in all_resources if r.get('type') in carbon_resource_types]
                print(f"✅ Resource data retrieved (fallback): {len(resources)} carbon-relevant resources")
                return resources
            else:
                print(f"❌ Fallback Resource API failed: {response.status_code} - {response.text[:200]}")
                return []
        except Exception as e:
            print(f"❌ Fallback Resource API error: {e}")
            return []
    
    def get_sustainability_data(self):
        """Try to get sustainability/carbon data from various Azure endpoints"""
        print("🔍 Querying for sustainability data...")
        
        sustainability_endpoints = [
            {
                "name": "Sustainability Workbook",
                "url": f"https://management.azure.com/subscriptions/{self.subscription_id}/providers/Microsoft.Insights/workbooks?api-version=2022-04-01",
                "params": {"category": "workbook"}
            },
            {
                "name": "Resource Health",
                "url": f"https://management.azure.com/subscriptions/{self.subscription_id}/providers/Microsoft.ResourceHealth/availabilityStatuses?api-version=2022-10-01",
                "params": {}
            },
            {
                "name": "Advisor Recommendations",
                "url": f"https://management.azure.com/subscriptions/{self.subscription_id}/providers/Microsoft.Advisor/recommendations?api-version=2020-01-01",
                "params": {}
            }
        ]
        
        results = {}
        for endpoint in sustainability_endpoints:
            try:
                url = endpoint["url"]
                if endpoint["params"]:
                    # Add query parameters
                    params = "&".join([f"{k}={v}" for k, v in endpoint["params"].items()])
                    url += f"&{params}" if "?" in url else f"?{params}"
                
                response = requests.get(url, headers=self.get_headers())
                if response.status_code == 200:
                    data = response.json()
                    results[endpoint["name"]] = data
                    count = len(data.get('value', [])) if isinstance(data, dict) and 'value' in data else 'unknown'
                    print(f"✅ {endpoint['name']}: {response.status_code} ({count} items)")
                else:
                    print(f"⚠️ {endpoint['name']}: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                print(f"⚠️ {endpoint['name']} error: {str(e)[:100]}")
        
        return results if results else None
    
    def calculate_carbon_estimates(self, cost_data, resource_data):
        """Calculate estimated carbon footprint based on cost and resource data"""
        print("🧮 Calculating carbon footprint estimates...")
        
        # Carbon intensity factors (kg CO2 per USD) - approximate values
        carbon_factors = {
            "Microsoft.Compute/virtualMachines": 0.45,  # High compute resources
            "Microsoft.Storage/storageAccounts": 0.15,   # Storage
            "Microsoft.ContainerService/managedClusters": 0.55,  # Container orchestration
            "Microsoft.Sql/servers": 0.25,              # Database services
            "Microsoft.Web/serverFarms": 0.35,          # App services
            "default": 0.30                             # Default factor
        }
        
        # Regional carbon intensity (kg CO2 per kWh) - approximate values
        regional_factors = {
            "eastus": 0.45,
            "westus": 0.35,
            "northeurope": 0.25,
            "westeurope": 0.30,
            "southeastasia": 0.55,
            "default": 0.40
        }
        
        carbon_estimates = []
        
        if cost_data and 'properties' in cost_data:
            rows = cost_data['properties'].get('rows', [])
            columns = [col['name'] for col in cost_data['properties'].get('columns', [])]
            
            for row in rows:
                row_data = dict(zip(columns, row))
                
                service_name = row_data.get('ServiceName', 'Unknown')
                location = row_data.get('ResourceLocation', 'unknown').lower()
                cost_usd = float(row_data.get('CostUSD', 0))
                
                # Estimate carbon based on service type and cost
                service_factor = carbon_factors.get(service_name, carbon_factors['default'])
                regional_factor = regional_factors.get(location, regional_factors['default'])
                
                estimated_carbon_kg = cost_usd * service_factor * regional_factor
                
                carbon_estimates.append({
                    "date": row_data.get('Date', ''),
                    "serviceName": service_name,
                    "location": location,
                    "costUSD": cost_usd,
                    "estimatedCarbonKg": round(estimated_carbon_kg, 4),
                    "carbonIntensityFactor": service_factor,
                    "regionalFactor": regional_factor
                })
        
        print(f"✅ Calculated carbon estimates for {len(carbon_estimates)} data points")
        return carbon_estimates
    
    def export_data(self, cost_data, resource_data, sustainability_data, carbon_estimates):
        """Export all collected data to JSON and CSV files"""
        print("📄 Exporting data...")
        
        # Prepare comprehensive export
        export_data = {
            "metadata": {
                "extractionTime": datetime.now().isoformat(),
                "subscriptionId": self.subscription_id,
                "dataSource": "Azure Management APIs",
                "carbonEstimationMethod": "Cost-based with regional and service factors",
                "note": "Carbon estimates are calculated based on cost data and industry factors"
            },
            "costManagementData": cost_data,
            "resourceData": resource_data,
            "sustainabilityData": sustainability_data,
            "carbonEstimates": carbon_estimates,
            "summary": {
                "totalEstimatedCarbonKg": sum(item['estimatedCarbonKg'] for item in carbon_estimates),
                "totalCostUSD": sum(item['costUSD'] for item in carbon_estimates),
                "resourceCount": len(resource_data) if resource_data else 0,
                "dataPointCount": len(carbon_estimates)
            }
        }
        
        # Export to JSON
        with open(self.output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"✅ Data exported to {self.output_file}")
        
        # Export carbon estimates to CSV
        if carbon_estimates:
            import csv
            with open(self.csv_file, 'w', newline='') as csvfile:
                fieldnames = ['date', 'serviceName', 'location', 'costUSD', 'estimatedCarbonKg', 'carbonIntensityFactor', 'regionalFactor']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(carbon_estimates)
            print(f"✅ Carbon estimates exported to {self.csv_file}")
        
        return True
    
    def run_extraction(self):
        """Run the complete carbon data extraction workflow"""
        print("🌱 Starting Azure Carbon Data Extraction")
        print("=" * 60)
        
        if not self.subscription_id:
            print("❌ No subscription ID available. Please run 'az login' and 'az account set --subscription <id>'")
            return False
        
        print(f"🔍 Using subscription: {self.subscription_id}")
        
        if not self.authenticate():
            return False
        
        # Collect data from multiple sources
        cost_data = self.get_cost_management_data()
        resource_data = self.get_resource_data()
        sustainability_data = self.get_sustainability_data()
        
        # Calculate carbon estimates
        carbon_estimates = self.calculate_carbon_estimates(cost_data, resource_data)
        
        # Export all data
        success = self.export_data(cost_data, resource_data, sustainability_data, carbon_estimates)
        
        if success:
            print("\n🎉 Carbon data extraction completed successfully!")
            print(f"📁 JSON output: {self.output_file}")
            print(f"📊 CSV output: {self.csv_file}")
            
            # Show summary
            if carbon_estimates:
                total_carbon = sum(item['estimatedCarbonKg'] for item in carbon_estimates)
                total_cost = sum(item['costUSD'] for item in carbon_estimates)
                print(f"📈 Total estimated carbon footprint: {total_carbon:.2f} kg CO2")
                print(f"💰 Total cost analyzed: ${total_cost:.2f} USD")
            
        return success

def extract_carbon_emissions():
    """Extract carbon emissions data from Azure APIs and save to output directory"""
    print("🌱 Starting Azure Carbon Emissions extraction...")
    
    # Ensure output directory exists
    output_dir = "../output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Initialize the extractor
        extractor = AzureCarbonExtractor()
        
        # Override output paths to use output directory
        extractor.output_file = os.path.join(output_dir, "azure_carbon_data.json")
        extractor.csv_file = os.path.join(output_dir, "azure_carbon_data.csv")
        
        # Run the extraction
        success = extractor.run_extraction()
        
        if success:
            output_files = [extractor.output_file, extractor.csv_file]
            return True, output_files
        else:
            return False, []
        
    except Exception as e:
        print(f"❌ Extraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, []

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract carbon emissions data from Azure')
    parser.add_argument('--subscription-id', help='Azure subscription ID (auto-detected if not provided)')
    args = parser.parse_args()
    
    extractor = AzureCarbonExtractor(subscription_id=args.subscription_id)
    success = extractor.run_extraction()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
