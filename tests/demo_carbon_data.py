import json
import os
from datetime import datetime, timedelta

# Demo script to simulate carbon emissions data extraction
# This creates sample data similar to what would come from Azure

def create_demo_carbon_data():
    """Create demo carbon emissions data that simulates Azure API response"""
    
    # Simulate data for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    demo_data = {
        "reportType": "OverallSummaryReport",
        "reportPeriod": {
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat()
        },
        "metadata": {
            "generatedOn": datetime.now().isoformat(),
            "subscriptionId": "demo-subscription-id",
            "dataSource": "Azure Carbon Optimization API (Demo)"
        },
        "summary": {
            "totalEmissions": {
                "value": 42.5,
                "unit": "kg CO2e"
            },
            "totalCost": {
                "value": 1250.75,
                "unit": "USD"
            },
            "averageDailyEmissions": {
                "value": 1.42,
                "unit": "kg CO2e/day"
            }
        },
        "emissionsByService": [
            {
                "serviceName": "Virtual Machines",
                "emissions": 18.2,
                "unit": "kg CO2e",
                "percentage": 42.8
            },
            {
                "serviceName": "Storage Account",
                "emissions": 8.5,
                "unit": "kg CO2e",
                "percentage": 20.0
            },
            {
                "serviceName": "App Service",
                "emissions": 7.3,
                "unit": "kg CO2e",
                "percentage": 17.2
            },
            {
                "serviceName": "SQL Database",
                "emissions": 5.1,
                "unit": "kg CO2e",
                "percentage": 12.0
            },
            {
                "serviceName": "Azure Functions",
                "emissions": 3.4,
                "unit": "kg CO2e",
                "percentage": 8.0
            }
        ],
        "emissionsByRegion": [
            {
                "region": "East US",
                "emissions": 15.6,
                "unit": "kg CO2e",
                "percentage": 36.7
            },
            {
                "region": "West Europe",
                "emissions": 12.3,
                "unit": "kg CO2e", 
                "percentage": 28.9
            },
            {
                "region": "Southeast Asia",
                "emissions": 9.8,
                "unit": "kg CO2e",
                "percentage": 23.1
            },
            {
                "region": "Central US",
                "emissions": 4.8,
                "unit": "kg CO2e",
                "percentage": 11.3
            }
        ],
        "dailyEmissions": []
    }
    
    # Generate daily emissions data
    current_date = start_date
    while current_date <= end_date:
        daily_emission = {
            "date": current_date.strftime("%Y-%m-%d"),
            "emissions": round(1.0 + (hash(current_date.strftime("%Y-%m-%d")) % 100) / 100, 2),
            "unit": "kg CO2e"
        }
        demo_data["dailyEmissions"].append(daily_emission)
        current_date += timedelta(days=1)
    
    return demo_data

def save_to_storage_ready_format(data, filename="carbon_emissions_export.json"):
    """Save data in a format ready for Azure Storage upload"""
    
    # Save as JSON (most common format for Azure Storage)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Demo carbon emissions data saved to {filename}")
    print(f"📊 Total emissions: {data['summary']['totalEmissions']['value']} {data['summary']['totalEmissions']['unit']}")
    print(f"💰 Total cost: ${data['summary']['totalCost']['value']}")
    print(f"📅 Report period: {data['reportPeriod']['startDate'][:10]} to {data['reportPeriod']['endDate'][:10]}")
    print(f"📁 File size: {os.path.getsize(filename)} bytes")
    print(f"\n🚀 This file is ready to be uploaded to Azure Storage Account!")
    
    # Also create a CSV version for easy analysis
    csv_filename = filename.replace('.json', '.csv')
    create_csv_summary(data, csv_filename)
    
    return filename

def create_csv_summary(data, csv_filename):
    """Create a CSV summary of the emissions data"""
    
    import csv
    
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write summary information
        writer.writerow(['Summary'])
        writer.writerow(['Total Emissions (kg CO2e)', data['summary']['totalEmissions']['value']])
        writer.writerow(['Total Cost (USD)', data['summary']['totalCost']['value']])
        writer.writerow(['Average Daily Emissions (kg CO2e/day)', data['summary']['averageDailyEmissions']['value']])
        writer.writerow([])
        
        # Write emissions by service
        writer.writerow(['Emissions by Service'])
        writer.writerow(['Service', 'Emissions (kg CO2e)', 'Percentage'])
        for service in data['emissionsByService']:
            writer.writerow([service['serviceName'], service['emissions'], f"{service['percentage']}%"])
        writer.writerow([])
        
        # Write emissions by region
        writer.writerow(['Emissions by Region'])
        writer.writerow(['Region', 'Emissions (kg CO2e)', 'Percentage'])
        for region in data['emissionsByRegion']:
            writer.writerow([region['region'], region['emissions'], f"{region['percentage']}%"])
        writer.writerow([])
        
        # Write daily emissions
        writer.writerow(['Daily Emissions'])
        writer.writerow(['Date', 'Emissions (kg CO2e)'])
        for daily in data['dailyEmissions']:
            writer.writerow([daily['date'], daily['emissions']])
    
    print(f"📄 CSV summary saved to {csv_filename}")

if __name__ == "__main__":
    print("🌱 Generating demo Azure carbon emissions data...")
    print("=" * 50)
    
    # Create demo data
    demo_data = create_demo_carbon_data()
    
    # Save in storage-ready format
    filename = save_to_storage_ready_format(demo_data)
    
    print("\n" + "=" * 50)
    print("✨ Demo complete! Files are ready for Azure Storage upload.")
