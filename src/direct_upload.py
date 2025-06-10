#!/usr/bin/env python3
"""
Direct Azure Storage Upload Script
This script uploads the carbon emissions files directly to Azure Storage
with better error handling and authentication feedback.
"""

import sys
import os
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceExistsError, ClientAuthenticationError

def check_authentication():
    """Check if Azure authentication is working"""
    try:
        credential = DefaultAzureCredential()
        # Try to get a token to test authentication
        token = credential.get_token("https://storage.azure.com/.default")
        print("✅ Azure authentication successful")
        return credential
    except ClientAuthenticationError as e:
        print("❌ Azure authentication failed:")
        print(f"   {str(e)}")
        print("\n💡 To fix this, try one of:")
        print("   1. Run 'az login' to authenticate with Azure CLI")
        print("   2. Set up a Service Principal with environment variables:")
        print("      - AZURE_CLIENT_ID")
        print("      - AZURE_CLIENT_SECRET") 
        print("      - AZURE_TENANT_ID")
        print("   3. Use Azure Cloud Shell which has built-in authentication")
        return None

def create_container_if_needed(blob_service_client, container_name):
    """Create container if it doesn't exist"""
    try:
        container_client = blob_service_client.get_container_client(container_name)
        container_client.get_container_properties()
        print(f"📁 Container '{container_name}' exists")
        return True
    except Exception:
        print(f"📁 Container '{container_name}' doesn't exist, creating...")
        try:
            blob_service_client.create_container(container_name, public_access="blob")
            print(f"✅ Created container '{container_name}' with public blob access")
            return True
        except Exception as e:
            print(f"❌ Failed to create container: {str(e)}")
            return False

def upload_file(blob_service_client, container_name, local_file, blob_name=None):
    """Upload a single file to Azure Storage"""
    if not blob_name:
        blob_name = os.path.basename(local_file)
    
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        print(f"📤 Uploading {local_file} as {blob_name}...")
        with open(local_file, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        # Get the URL for the uploaded blob
        blob_url = blob_client.url
        print(f"✅ Upload successful: {blob_url}")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python direct_upload.py <storage_account_name> [container_name]")
        print("Example: python direct_upload.py mystorageaccount carbon-emissions")
        sys.exit(1)
    
    storage_account_name = sys.argv[1]
    container_name = sys.argv[2] if len(sys.argv) > 2 else "carbon-emissions"
    
    print("🚀 DIRECT AZURE STORAGE UPLOAD")
    print("=" * 50)
    print(f"📦 Storage Account: {storage_account_name}")
    print(f"📁 Container: {container_name}")
    print()
    
    # Step 1: Check authentication
    print("1️⃣ Checking Azure authentication...")
    credential = check_authentication()
    if not credential:
        sys.exit(1)
    
    # Step 2: Connect to storage account
    print("\n2️⃣ Connecting to Azure Storage...")
    try:
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        print(f"✅ Connected to {account_url}")
    except Exception as e:
        print(f"❌ Failed to connect: {str(e)}")
        sys.exit(1)
    
    # Step 3: Create container if needed
    print("\n3️⃣ Ensuring container exists...")
    if not create_container_if_needed(blob_service_client, container_name):
        sys.exit(1)
    
    # Step 4: Upload files
    print("\n4️⃣ Uploading carbon emissions files...")
    files_to_upload = [
        "carbon_emissions_export.json",
        "carbon_emissions_export.csv"
    ]
    
    uploaded_count = 0
    for filename in files_to_upload:
        if os.path.exists(filename):
            if upload_file(blob_service_client, container_name, filename):
                uploaded_count += 1
        else:
            print(f"⚠️  File not found: {filename}")
    
    # Step 5: Summary
    print("\n" + "=" * 50)
    print("📊 UPLOAD SUMMARY")
    print("=" * 50)
    print(f"✅ {uploaded_count}/{len(files_to_upload)} files uploaded successfully")
    
    if uploaded_count > 0:
        print(f"\n📁 Files are now available at:")
        print(f"   {account_url}/{container_name}/")
        print(f"\n🌐 You can access them via:")
        for filename in files_to_upload:
            if os.path.exists(filename):
                print(f"   • {account_url}/{container_name}/{filename}")

if __name__ == "__main__":
    main()
