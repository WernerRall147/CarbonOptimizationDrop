from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import os
import sys

def upload_to_azure_storage(local_file_path, storage_account_name, container_name, blob_name=None):
    """
    Upload a file to Azure Storage Account using Azure Identity for authentication
    
    Args:
        local_file_path: Path to the local file to upload
        storage_account_name: Name of the Azure Storage Account
        container_name: Name of the container in the storage account
        blob_name: Name for the blob (optional, defaults to filename)
    """
    
    if not blob_name:
        blob_name = os.path.basename(local_file_path)
    
    try:
        # Use DefaultAzureCredential for authentication
        credential = DefaultAzureCredential()
        
        # Create BlobServiceClient
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        
        # Get blob client
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Upload file
        print(f"📤 Uploading {local_file_path} to Azure Storage...")
        with open(local_file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        print(f"✅ Successfully uploaded to: {account_url}/{container_name}/{blob_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error uploading to Azure Storage: {str(e)}")
        return False

def upload_carbon_data(storage_account_name, container_name="carbon-emissions"):
    """Upload both JSON and CSV carbon emissions files to Azure Storage"""
    
    files_to_upload = [
        "carbon_emissions_export.json",
        "carbon_emissions_export.csv"
    ]
    
    print("🌱 Starting Azure Storage upload for carbon emissions data...")
    print("=" * 60)
    
    success_count = 0
    
    for file_path in files_to_upload:
        if os.path.exists(file_path):
            if upload_to_azure_storage(file_path, storage_account_name, container_name):
                success_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("\n" + "=" * 60)
    print(f"✨ Upload complete! {success_count}/{len(files_to_upload)} files uploaded successfully.")
    
    if success_count > 0:
        print(f"\n📁 Files are now available in Azure Storage:")
        print(f"   Storage Account: {storage_account_name}")
        print(f"   Container: {container_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_to_storage.py <storage_account_name> [container_name]")
        print("Example: python upload_to_storage.py mystorageaccount carbon-emissions")
        sys.exit(1)
    
    storage_account = sys.argv[1]
    container = sys.argv[2] if len(sys.argv) > 2 else "carbon-emissions"
    
    upload_carbon_data(storage_account, container)
