#!/usr/bin/env python3
"""
Complete Carbon Emissions Data Extraction and Upload Workflow
This script demonstrates the full process from data extraction to Azure Storage upload
"""

import os
import sys
import json
from datetime import datetime

def test_data_extraction():
    """Test the carbon emissions data extraction process"""
    print("🧪 TESTING: Carbon Emissions Data Extraction")
    print("=" * 50)
    
    # Import and run the demo data creation
    try:
        from demo_carbon_data import create_demo_carbon_data, save_to_storage_ready_format
        
        print("1️⃣ Creating demo carbon emissions data...")
        demo_data = create_demo_carbon_data()
        
        print("2️⃣ Saving data in storage-ready format...")
        filename = save_to_storage_ready_format(demo_data, "test_carbon_export.json")
        
        print("3️⃣ Validating data structure...")
        with open(filename, 'r') as f:
            loaded_data = json.load(f)
        
        # Validate required fields
        required_fields = ['reportType', 'reportPeriod', 'summary', 'emissionsByService']
        for field in required_fields:
            if field not in loaded_data:
                raise ValueError(f"Missing required field: {field}")
        
        print("✅ Data extraction test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Data extraction test FAILED: {str(e)}")
        return False

def test_file_formats():
    """Test that files are in correct format for Azure Storage"""
    print("\n🧪 TESTING: File Format Validation")
    print("=" * 50)
    
    try:
        files_to_check = [
            ("test_carbon_export.json", "JSON"),
            ("test_carbon_export.csv", "CSV")
        ]
        
        for filename, file_type in files_to_check:
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"✅ {filename} ({file_type}): {file_size} bytes")
                
                if file_type == "JSON":
                    # Validate JSON structure
                    with open(filename, 'r') as f:
                        json.load(f)  # This will raise an exception if invalid JSON
                    print(f"   └─ Valid JSON structure")
                
            else:
                print(f"❌ {filename} not found")
                return False
        
        print("✅ File format validation PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ File format validation FAILED: {str(e)}")
        return False

def test_azure_connection():
    """Test Azure connectivity and authentication"""
    print("\n🧪 TESTING: Azure Connectivity")
    print("=" * 50)
    
    try:
        from azure.identity import DefaultAzureCredential
        
        print("1️⃣ Testing Azure authentication...")
        credential = DefaultAzureCredential()
        
        # Try to get a token (this will fail in demo environment but shows the process)
        try:
            token = credential.get_token("https://management.azure.com/.default")
            print("✅ Azure authentication successful!")
            print(f"   └─ Token expires: {datetime.fromtimestamp(token.expires_on)}")
            return True
        except Exception as auth_error:
            print(f"⚠️  Azure authentication not configured: {str(auth_error)}")
            print("   └─ This is expected in demo environment")
            print("   └─ In production, ensure 'az login' or service principal is configured")
            return False
            
    except ImportError:
        print("❌ Azure identity library not available")
        return False

def show_deployment_instructions():
    """Show instructions for actual deployment"""
    print("\n📋 DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    
    instructions = """
🚀 To deploy this solution in your Azure environment:

1. AUTHENTICATION:
   - Run 'az login' to authenticate with Azure CLI
   - Or configure a Service Principal with environment variables:
     * AZURE_CLIENT_ID
     * AZURE_CLIENT_SECRET  
     * AZURE_TENANT_ID

2. PERMISSIONS REQUIRED:
   - Carbon Optimization API: Reader access to subscriptions
   - Storage Account: Storage Blob Data Contributor role

3. RUN THE EXTRACTION:
   python export_carbon_data.py

4. UPLOAD TO STORAGE:
   python upload_to_storage.py <storage_account_name> [container_name]

5. EXAMPLE COMPLETE WORKFLOW:
   python demo_carbon_data.py  # Create demo data
   python upload_to_storage.py mystorageaccount carbon-emissions

📁 Output files ready for Azure Storage:
   - carbon_emissions_export.json (structured data)
   - carbon_emissions_export.csv (for analysis)
"""
    print(instructions)

def main():
    """Run all tests and show results"""
    print("🧪 CARBON EMISSIONS DATA EXTRACTION - FULL TEST SUITE")
    print("=" * 80)
    
    tests = [
        ("Data Extraction", test_data_extraction),
        ("File Formats", test_file_formats),
        ("Azure Connectivity", test_azure_connection)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Show summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The solution is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Check authentication and dependencies.")
    
    show_deployment_instructions()

if __name__ == "__main__":
    main()
