import azure.functions as func
import datetime
import logging
import configparser
from azure.storage.blob import BlobServiceClient
from VMReportApp.azure_helper import azure_report
from VMReportApp.aws_helper import aws_report
import os
import uuid

def get_configuration():
    """
    Reads configuration from test_config.ini to get credentials for AWS and AZURE.
    """
    config = configparser.ConfigParser()
    config.read('test_config.ini')

    azure_credentials = None
    aws_credentials = None

    try:
        if 'AZURE' in config.sections():
            azure_credentials = {
                "subscription_id": config['AZURE']['SUBSCRIPTION_ID'],
                "client_secret": config['AZURE']['CLIENT_SECRET'],
                "client_id": config['AZURE']['CLIENT_ID'],
                "tenant_id": config['AZURE']['TENANT_ID'],
            }
        elif 'AWS' in config.sections():
            aws_credentials = {
                "access_key": config['AWS']['ACCESS_KEY'],    
                "secret_key": config['AWS']['SECRET_KEY'],
                "region": config['AWS']['REGION'],
            }
        else :
            raise Exception("AWS and AZURE both are not present in config.ini file")
    except Exception as e:
        logging.error(f"Credentials error: {e}")
        return None, None, None

    report_days = config['REPORT']['DAYS']
    return report_days, azure_credentials, aws_credentials


local_path = "./data"
os.mkdir(local_path)

# Create a file in the local data directory to upload and download
local_file_name = str(uuid.uuid4()) + ".txt"
upload_file_path = os.path.join(local_path, local_file_name)

# Write text to the file
file = open(file=upload_file_path, mode='w')
file.write("Hello, World!")
file.close()

# Create a blob client using the local file name as the name for the blob
connection_string = ""
container_name = "azureacc02"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

# Upload the created file
with open(file=upload_file_path, mode="rb") as data:
    blob_client.upload_blob(data)

def store_report_in_blob(report_data, filename):
    """
    Stores the VM report JSON file in Azure Blob Storage.
    """
    try:
        connection_string = ""
        container_name = "azureacc02"

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

        blob_client.upload_blob(report_data, overwrite=True)

        logging.info(f"Report {filename} successfully stored in Azure Blob Storage.")

    except Exception as e:
        logging.error(f"Error storing report in Azure Blob Storage: {e}")

def main(myTimer: func.TimerRequest) -> None:
    """
    Runs the report generation function on a schedule.
    """
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info(f"Azure Function triggered at {utc_timestamp}")

    report_days, azure_creds, aws_creds = get_configuration()

    if azure_creds:
        azure_report_data = azure_report(report_days, azure_creds, logging)
        print(f"Azure Report Data: {azure_report_data}")
        store_report_in_blob(azure_report_data, f"azure_vm_report_{utc_timestamp}.json")

    if aws_creds:
        aws_report_data = aws_report(aws_creds, report_days, logging)
        store_report_in_blob(aws_report_data, f"aws_vm_report_{utc_timestamp}.json")

    logging.info("VM report generation completed successfully.")
