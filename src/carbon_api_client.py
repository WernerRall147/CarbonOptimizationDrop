#!/usr/bin/env python3
"""
Azure Carbon Optimization API Client
Based on: https://learn.microsoft.com/en-us/azure/carbon-optimization/api-export-data

This script uses the official Azure Carbon Optimization APIs to extract carbon emissions data.
"""

import os
import sys
import json
import time
import requests
from azure.identity import DefaultAzureCredential
from datetime import datetime, timedelta

class CarbonOptimizationClient:
    def __init__(self, subscription_id=None):
        self.subscription_id = subscription_id or self._get_subscription_id()
        self.base_url = "https://management.azure.com"
        self.api_version = "2023-10-01-preview"
        self.credential = None
        self.headers = None
        
    def _get_subscription_id(self):
        """Get subscription ID from Azure CLI"""
        try:
            import subprocess
            result = subprocess.run(['az', 'account', 'show', '--query', 'id', '-o', 'tsv'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception as e:
            print(f"❌ Could not get subscription ID: {e}")
            print("💡 Please run 'az login' or set subscription ID manually")
            return None
    
    def authenticate(self):
        """Authenticate with Azure"""
        try:
            self.credential = DefaultAzureCredential()
            token = self.credential.get_token("https://management.azure.com/.default").token
            self.headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            print(f"✅ Authenticated successfully")
            print(f"📋 Subscription ID: {self.subscription_id}")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def get_carbon_insights(self):
        """Get carbon insights for the subscription"""
        url = f"{self.base_url}/subscriptions/{self.subscription_id}/providers/Microsoft.Carbon/insights"
        params = {"api-version": self.api_version}
        
        print("🔍 Getting carbon insights...")
        try:
            response = requests.get(url, headers=self.headers, params=params)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"   Request failed: {e}")
            return None
    
    def query_carbon_usage(self, timeframe="MonthToDate"):
        """Query carbon usage data"""
        url = f"{self.base_url}/subscriptions/{self.subscription_id}/providers/Microsoft.Carbon/query"
        params = {"api-version": self.api_version}
        
        # Query body based on Microsoft documentation
        body = {
            "type": "Usage",
            "timeframe": timeframe,
            "dataset": {
                "granularity": "Daily",
                "aggregation": {
                    "totalCarbonEmissions": {
                        "name": "UsageQuantity",
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
                        "name": "ResourceLocation"
                    }
                ]
            }
        }
        
        print(f"🔍 Querying carbon usage data (timeframe: {timeframe})...")
        try:
            response = requests.post(url, headers=self.headers, params=params, json=body)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"   Request failed: {e}")
            return None
    
    def create_export(self, export_name="carbon-export"):
        """Create a carbon emissions export"""
        url = f"{self.base_url}/subscriptions/{self.subscription_id}/providers/Microsoft.Carbon/exports/{export_name}"
        params = {"api-version": self.api_version}
        
        # Export configuration
        body = {
            "properties": {
                "schedule": {
                    "status": "Active",
                    "recurrence": "Daily"
                },
                "format": "Csv",
                "deliveryInfo": {
                    "destination": {
                        "resourceId": f"/subscriptions/{self.subscription_id}",
                        "container": "carbonexports",
                        "rootFolderPath": "exports"
                    }
                },
                "definition": {
                    "type": "Usage",
                    "timeframe": "MonthToDate"
                }
            }
        }
        
        print(f"🔍 Creating carbon export: {export_name}...")
        try:
            response = requests.put(url, headers=self.headers, params=params, json=body)
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"   Request failed: {e}")
            return None
    
    def extract_all_carbon_data(self):
        """Extract all available carbon data"""
        all_data = {
            "metadata": {
                "extractedAt": datetime.now().isoformat(),
                "subscriptionId": self.subscription_id,
                "apiVersion": self.api_version
            },
            "insights": None,
            "usage": None,
            "export": None
        }
        
        print("🌱 EXTRACTING ALL CARBON DATA")
        print("=" * 50)
        
        # 1. Get carbon insights
        insights = self.get_carbon_insights()
        if insights:
            all_data["insights"] = insights
            print("✅ Carbon insights extracted")
        
        # 2. Query carbon usage
        usage = self.query_carbon_usage()
        if usage:
            all_data["usage"] = usage
            print("✅ Carbon usage data extracted")
        
        # 3. Create export (for future data)
        export = self.create_export()
        if export:
            all_data["export"] = export
            print("✅ Carbon export created")
        
        return all_data

def main():
    print("🌍 AZURE CARBON OPTIMIZATION API CLIENT")
    print("=" * 60)
    print("📚 Based on Microsoft Carbon Optimization API documentation")
    print("🔗 https://learn.microsoft.com/en-us/azure/carbon-optimization/api-export-data")
    print()
    
    # Initialize client
    subscription_id = None  # Auto-detect or set manually
    if len(sys.argv) > 1:
        subscription_id = sys.argv[1]
        print(f"🎯 Using provided subscription ID: {subscription_id}")
    
    client = CarbonOptimizationClient(subscription_id)
    
    if not client.subscription_id:
        print("❌ No subscription ID available. Exiting.")
        sys.exit(1)
    
    # Authenticate
    if not client.authenticate():
        sys.exit(1)
    
    # Extract all carbon data
    carbon_data = client.extract_all_carbon_data()
    
    # Save results
    output_file = "azure_carbon_data.json"
    with open(output_file, 'w') as f:
        json.dump(carbon_data, f, indent=2)
    
    print(f"\n🎉 Carbon data extraction complete!")
    print(f"📁 Saved to: {output_file}")
    print(f"📊 File size: {os.path.getsize(output_file)} bytes")
    
    # Show summary
    print(f"\n📋 EXTRACTION SUMMARY:")
    for key, value in carbon_data.items():
        if key != "metadata":
            status = "✅" if value else "❌"
            print(f"   {status} {key}: {'Success' if value else 'Failed'}")

if __name__ == "__main__":
    main()
