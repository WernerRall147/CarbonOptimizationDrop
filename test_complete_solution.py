#!/usr/bin/env python3
"""
Complete Solution Test - Azure Carbon Emissions Data Extraction

This script tests the entire solution end-to-end:
1. Extract real carbon emissions data from Azure
2. Upload to Azure Storage
3. Verify all components work correctly

Usage:
    python test_complete_solution.py
    python test_complete_solution.py --storage-account mystorageaccount
"""

import os
import sys
import argparse
from datetime import datetime

def test_extraction():
    """Test the carbon emissions data extraction"""
    print("🧪 TESTING: Carbon Emissions Data Extraction")
    print("=" * 60)
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from azure_carbon_extractor import extract_carbon_emissions
        
        print("1️⃣ Running carbon emissions extraction...")
        success, output_files = extract_carbon_emissions()
        
        if success and output_files:
            print("✅ Extraction test PASSED!")
            print(f"📁 Files created: {len(output_files)}")
            for file_path in output_files:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   • {os.path.basename(file_path)}: {size:,} bytes")
            return True, output_files
        else:
            print("❌ Extraction test FAILED!")
            return False, []
            
    except Exception as e:
        print(f"❌ Extraction test ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, []

def test_upload(storage_account_name, container_name="carbon-emissions"):
    """Test the Azure Storage upload functionality"""
    print(f"\n🧪 TESTING: Azure Storage Upload to {storage_account_name}")
    print("=" * 60)
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Import and run upload
        from direct_upload import check_authentication, create_container_if_needed, upload_file
        from azure.storage.blob import BlobServiceClient
        
        print("1️⃣ Testing authentication...")
        credential = check_authentication()
        if not credential:
            print("❌ Upload test FAILED - Authentication issue")
            return False
        
        print("2️⃣ Testing storage connection...")
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        
        print("3️⃣ Testing container creation...")
        if not create_container_if_needed(blob_service_client, container_name):
            print("❌ Upload test FAILED - Container creation issue")
            return False
        
        print("4️⃣ Testing file upload...")
        # Check for files in output directory
        output_dir = "output"
        if not os.path.exists(output_dir):
            print("❌ Upload test FAILED - No output directory found")
            return False
        
        files_to_upload = [
            f for f in os.listdir(output_dir) 
            if f.endswith(('.json', '.csv'))
        ]
        
        if not files_to_upload:
            print("❌ Upload test FAILED - No files to upload found")
            return False
        
        upload_count = 0
        for filename in files_to_upload:
            filepath = os.path.join(output_dir, filename)
            if upload_file(blob_service_client, container_name, filepath):
                upload_count += 1
        
        if upload_count > 0:
            print(f"✅ Upload test PASSED! ({upload_count}/{len(files_to_upload)} files uploaded)")
            return True
        else:
            print("❌ Upload test FAILED - No files uploaded successfully")
            return False
            
    except Exception as e:
        print(f"❌ Upload test ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that the file structure is properly organized"""
    print("🧪 TESTING: File Structure Organization")
    print("=" * 60)
    
    expected_structure = {
        "src": ["azure_carbon_extractor.py", "carbon_api_client.py", "direct_upload.py", "upload_to_storage.py"],
        "tests": ["test_full_workflow.py", "demo_carbon_data.py"],
        "output": [],  # May be empty initially
        "legacy": []   # May contain old files
    }
    
    all_good = True
    
    for directory, expected_files in expected_structure.items():
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}/")
            actual_files = os.listdir(directory)
            for expected_file in expected_files:
                if expected_file in actual_files:
                    print(f"   ✅ {expected_file}")
                else:
                    print(f"   ❌ Missing: {expected_file}")
                    all_good = False
        else:
            print(f"❌ Directory missing: {directory}/")
            all_good = False
    
    if all_good:
        print("✅ File structure test PASSED!")
    else:
        print("❌ File structure test FAILED!")
    
    return all_good

def show_solution_status():
    """Show the current status of the complete solution"""
    print("📊 COMPLETE SOLUTION STATUS")
    print("=" * 60)
    
    # Check main components
    components = [
        ("main.py", "Main application script"),
        ("src/azure_carbon_extractor.py", "Carbon data extraction"),
        ("src/direct_upload.py", "Azure Storage upload"),
        ("requirements.txt", "Dependencies")
    ]
    
    print("🔧 Core Components:")
    for filepath, description in components:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"   ✅ {filepath} ({size:,} bytes) - {description}")
        else:
            print(f"   ❌ {filepath} - {description}")
    
    # Check output files
    print("\n📁 Output Files:")
    output_dir = "output"
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            for filename in sorted(files):
                filepath = os.path.join(output_dir, filename)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"   📄 {filename} ({size:,} bytes) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("   📁 No output files yet")
    else:
        print("   📁 Output directory not created yet")

def main():
    parser = argparse.ArgumentParser(description="Test the complete Azure Carbon Emissions solution")
    parser.add_argument("--storage-account", help="Azure Storage Account name for upload testing")
    parser.add_argument("--skip-extraction", action="store_true", help="Skip extraction test")
    parser.add_argument("--skip-upload", action="store_true", help="Skip upload test")
    
    args = parser.parse_args()
    
    print("🧪 COMPLETE SOLUTION TEST SUITE")
    print("=" * 80)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Show current status
    show_solution_status()
    
    test_results = []
    
    # Test file structure
    structure_ok = test_file_structure()
    test_results.append(("File Structure", structure_ok))
    
    # Test extraction
    if not args.skip_extraction:
        extraction_ok, output_files = test_extraction()
        test_results.append(("Data Extraction", extraction_ok))
    else:
        print("\n⏭️  Skipping extraction test")
        test_results.append(("Data Extraction", None))
    
    # Test upload
    if not args.skip_upload and args.storage_account:
        upload_ok = test_upload(args.storage_account)
        test_results.append(("Azure Storage Upload", upload_ok))
    elif args.skip_upload:
        print("\n⏭️  Skipping upload test")
        test_results.append(("Azure Storage Upload", None))
    else:
        print("\n⏭️  Skipping upload test (no storage account provided)")
        test_results.append(("Azure Storage Upload", None))
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = 0
    
    for test_name, result in test_results:
        if result is True:
            status = "✅ PASS"
            passed += 1
            total += 1
        elif result is False:
            status = "❌ FAIL"
            total += 1
        else:
            status = "⏭️  SKIP"
        
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total and total > 0:
        print("🎉 All tests passed! The complete solution is ready for production.")
    elif total == 0:
        print("⚠️  No tests were run. Use --storage-account to enable upload testing.")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
