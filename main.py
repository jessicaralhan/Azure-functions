import logging
import configparser
from azure_helper import azure_report
from aws_helper import aws_report
from datetime import datetime

# Logger setup for Azure Function
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_configuration():
    '''
        Configuration function which is reading from config.ini sections to get the credentials for AWS and AZURE 
    '''
    config = configparser.ConfigParser()
    config.read('test_config.ini')
    try:
        if 'AZURE' in config.sections():
            subscription_id = config['AZURE']['SUBSCRIPTION_ID']
            client_secret = config['AZURE']['CLIENT_SECRET']
            client_id = config['AZURE']['CLIENT_ID']
            tenant_id = config['AZURE']['TENANT_ID']
            azure_credentials = {
                "subscription_id": subscription_id,
                "client_secret": client_secret,
                "client_id": client_id,
                "tenant_id": tenant_id,
            }
            aws_credentials = None
        elif 'AWS' in config.sections():
            access_key = config['AWS']['ACCESS_KEY']    
            secret_key = config['AWS']['SECRET_KEY']
            region = config['AWS']['REGION']
            aws_credentials = {
                "access_key": access_key,
                "secret_key": secret_key,
                "region": region,
            }     
            azure_credentials = None
        else:
            raise Exception("AWS and AZURE both are not present in config.ini file")

    except Exception as e:
        logger.error("Credentials error. Recheck the credentials", exc_info=True)
        return None, None, None

    report_days = config['REPORT']['DAYS']
    return report_days, azure_credentials, aws_credentials

def running_vms(report_days, azure_creds=None, aws_creds=None):
    '''
    Running the code to get the report for running VMs
    '''
    if azure_creds:
        azure_report(report_days, azure_creds, logger)
    if aws_creds:
        aws_report(aws_creds, report_days, logger)
