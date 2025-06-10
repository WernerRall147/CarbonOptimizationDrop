#!/usr/bin/env python3
"""
CARBON EMISSIONS DATA EXTRACTION - COMPLETE SOLUTION

This is the most efficient way to extract carbon emissions data from Azure
and prepare it for upload to Azure Storage Account.

Usage:
    python run_complete_extraction.py [--demo] [--storage-account ACCOUNT_NAME]

Examples:
    python run_complete_extraction.py --demo
    python run_complete_extraction.py --storage-account mystorageaccount
"""

import argparse
import sys
import os
from datetime import datetime

def run_demo_extraction():
    """Run demo extraction with sample data"""
    print("🌱 RUNNING DEMO CARBON EMISSIONS EXTRACTION")
    print("=" * 60)
    
    try:
        from demo_carbon_data import create_demo_carbon_data, save_to_storage_ready_format
        
        print("📊 Creating demo carbon emissions data...")
        demo_data = create_demo_carbon_data()
        
        print("💾 Saving data in storage-ready formats...")
        json_file = save_to_storage_ready_format(demo_data)
        
        print(f"\n✅ Demo extraction complete!")
        print(f"📁 Files created:")
        print(f"   - {json_file} (JSON format)")
        print(f"   - {json_file.replace('.json', '.csv')} (CSV format)")
        
        return json_file
        
    except Exception as e:
        print(f"❌ Demo extraction failed: {str(e)}")
        return None

def run_production_extraction():
    """Run production extraction from actual Azure API"""
    print("🏭 RUNNING PRODUCTION CARBON EMISSIONS EXTRACTION")
    print("=" * 60)
    
    try:
        # Import the production extraction script
        import subprocess
        result = subprocess.run([sys.executable, "export_carbon_data.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Production extraction successful!")
            print(result.stdout)
            return "carbon_emissions_export.json"
        else:
            print("❌ Production extraction failed:")
            print(result.stderr)
            return None
            
    except Exception as e:
        print(f"❌ Production extraction failed: {str(e)}")
        return None

def upload_to_storage(storage_account_name, files_to_upload):
    """Upload files to Azure Storage"""
    print(f"\n🚀 UPLOADING TO AZURE STORAGE: {storage_account_name}")
    print("=" * 60)
    
    try:
        from upload_to_storage import upload_carbon_data
        upload_carbon_data(storage_account_name)
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        print("💡 Ensure you are authenticated with Azure (run 'az login')")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Extract carbon emissions data from Azure and prepare for storage upload",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_complete_extraction.py --demo
  python run_complete_extraction.py --storage-account mystorageaccount
  python run_complete_extraction.py --demo --storage-account mystorageaccount
        """
    )
    
    parser.add_argument("--demo", action="store_true", 
                       help="Use demo data instead of real Azure API")
    parser.add_argument("--storage-account", type=str,
                       help="Azure Storage Account name for upload")
    parser.add_argument("--container", type=str, default="carbon-emissions",
                       help="Container name (default: carbon-emissions)")
    
    args = parser.parse_args()
    
    print("🌍 AZURE CARBON EMISSIONS DATA EXTRACTION TOOL")
    print("=" * 80)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Mode: {'Demo' if args.demo else 'Production'}")
    if args.storage_account:
        print(f"📦 Storage: {args.storage_account}/{args.container}")
    print("=" * 80)
    
    # Step 1: Extract data
    if args.demo:
        extracted_file = run_demo_extraction()
    else:
        extracted_file = run_production_extraction()
    
    if not extracted_file:
        print("❌ Data extraction failed. Exiting.")
        sys.exit(1)
    
    # Step 2: Upload to storage (if requested)
    if args.storage_account:
        success = upload_to_storage(args.storage_account, [extracted_file])
        if not success:
            print("⚠️  Upload failed, but extracted files are available locally.")
    else:
        print("\n💡 To upload to Azure Storage, run:")
        print(f"   python upload_to_storage.py <storage_account_name> {args.container}")
    
    # Step 3: Show summary
    print("\n" + "=" * 80)
    print("📋 EXTRACTION SUMMARY")
    print("=" * 80)
    
    # Show created files
    files_created = []
    for ext in ['.json', '.csv']:
        filename = extracted_file.replace('.json', ext) if extracted_file else f"carbon_emissions_export{ext}"
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            files_created.append((filename, size))
    
    if files_created:
        print("📁 Files created:")
        for filename, size in files_created:
            print(f"   ✅ {filename} ({size:,} bytes)")
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 Carbon emissions data extraction complete!")
    
    if not args.storage_account:
        print("\n💡 Next steps:")
        print("   1. Review the generated files")
        print("   2. Upload to Azure Storage using upload_to_storage.py")
        print("   3. Use the data for carbon footprint analysis")

if __name__ == "__main__":
    main()
