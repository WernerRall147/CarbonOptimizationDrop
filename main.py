#!/usr/bin/env python3
"""
Azure Carbon Emissions Data Extraction - Main Application

This is the primary script for extracting carbon emissions data from Azure
and uploading it to Azure Storage Account.

Features:
- Real Azure Carbon Optimization API integration
- Multiple authentication methods (Azure CLI, Service Principal, Managed Identity)
- Automatic container creation in Azure Storage
- Both JSON and CSV output formats
- Comprehensive error handling and logging

Usage:
    python main.py --help
    python main.py --extract --storage-account mystorageaccount
    python main.py --extract --upload --storage-account mystorageaccount
"""

import argparse
import sys
import os
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def extract_carbon_data():
    """Extract carbon emissions data using the Azure Carbon API"""
    try:
        from azure_carbon_extractor import extract_carbon_emissions
        
        print("🌱 EXTRACTING CARBON EMISSIONS DATA FROM AZURE")
        print("=" * 60)
        
        # Extract data
        success, output_files = extract_carbon_emissions()
        
        if success:
            print(f"\n✅ Carbon data extraction successful!")
            print(f"📁 Output files created in './output/':")
            for file_path in output_files:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   • {os.path.basename(file_path)} ({size:,} bytes)")
            return output_files
        else:
            print("❌ Carbon data extraction failed")
            return None
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        return None
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return None

def upload_to_azure_storage(storage_account_name, container_name="carbon-emissions"):
    """Upload extracted files to Azure Storage"""
    try:
        from direct_upload import main as upload_main
        import sys
        
        print(f"\n🚀 UPLOADING TO AZURE STORAGE: {storage_account_name}")
        print("=" * 60)
        
        # Temporarily modify sys.argv for the upload script
        original_argv = sys.argv
        sys.argv = ['direct_upload.py', storage_account_name, container_name]
        
        # Change to output directory where files are located
        original_cwd = os.getcwd()
        os.chdir('output')
        
        try:
            upload_main()
            success = True
        except SystemExit:
            success = True  # upload script calls sys.exit() on success
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            success = False
        finally:
            # Restore original state
            os.chdir(original_cwd)
            sys.argv = original_argv
        
        return success
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def show_status():
    """Show current status of extracted files"""
    print("📊 CURRENT STATUS")
    print("=" * 60)
    
    output_dir = "output"
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if f.endswith(('.json', '.csv'))]
        if files:
            print("📁 Available files:")
            for filename in sorted(files):
                filepath = os.path.join(output_dir, filename)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"   • {filename} ({size:,} bytes) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("📁 No output files found")
    else:
        print("📁 Output directory doesn't exist")

def main():
    parser = argparse.ArgumentParser(
        description="Azure Carbon Emissions Data Extraction and Upload Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --status
  python main.py --extract
  python main.py --extract --upload --storage-account mystorageaccount
  python main.py --upload --storage-account mystorageaccount --container mycontainer
        """
    )
    
    parser.add_argument("--extract", action="store_true",
                       help="Extract carbon emissions data from Azure")
    parser.add_argument("--upload", action="store_true",
                       help="Upload extracted files to Azure Storage")
    parser.add_argument("--storage-account", type=str,
                       help="Azure Storage Account name for upload")
    parser.add_argument("--container", type=str, default="carbon-emissions",
                       help="Container name (default: carbon-emissions)")
    parser.add_argument("--status", action="store_true",
                       help="Show status of current files")
    
    args = parser.parse_args()
    
    # Show header
    print("🌍 AZURE CARBON EMISSIONS DATA EXTRACTION TOOL")
    print("=" * 80)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Handle status request
    if args.status:
        show_status()
        return
    
    # Validate arguments
    if args.upload and not args.storage_account:
        print("❌ --storage-account is required when using --upload")
        parser.print_help()
        sys.exit(1)
    
    if not args.extract and not args.upload and not args.status:
        print("❌ Please specify --extract, --upload, or --status")
        parser.print_help()
        sys.exit(1)
    
    success = True
    
    # Extract data if requested
    if args.extract:
        output_files = extract_carbon_data()
        if not output_files:
            success = False
    
    # Upload data if requested
    if args.upload and success:
        upload_success = upload_to_azure_storage(args.storage_account, args.container)
        if not upload_success:
            success = False
    
    # Final summary
    print("\n" + "=" * 80)
    print("📋 FINAL SUMMARY")
    print("=" * 80)
    
    if success:
        print("🎉 All operations completed successfully!")
        if args.upload:
            print(f"\n🌐 Your carbon emissions data is now available in:")
            print(f"   Azure Storage Account: {args.storage_account}")
            print(f"   Container: {args.container}")
    else:
        print("⚠️  Some operations failed. Check the logs above for details.")
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
