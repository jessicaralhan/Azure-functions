"""
I need a script or automation of some sorts which runs on a daily basis which gets me a list of
running instances (VMs) on a cloud provider. 

It should show me a report of the instances that are running for a certain period of time. 
(That time can be configurable eventually )

"""

import schedule
import time
import configparser
from VMReportApp.azure_helper import azure_report
from VMReportApp.aws_helper import aws_report
import logging

logging.basicConfig(filename="application.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
                "subscription_id":subscription_id,
                "client_secret":client_secret,
                "client_id":client_id,
                "tenant_id":tenant_id,
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
        logger.error("Credentials error. Recheck the crendentials", e)
        return
    report_days = config['REPORT']['DAYS']

    return report_days, azure_credentials, aws_credentials

# help(get_configuration)

def running_vms():
    '''
    running the code to get the report
    '''
    report_days, azure_creds, aws_creds = get_configuration()
    if azure_creds:
        azure_report(report_days, azure_creds, logger)
    if aws_creds:
        aws_report(aws_creds, report_days, logger)


if __name__ == "__main__":
    # schedule.every().day.at("18:00").do(running_vms)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
# help(running_vms)
    running_vms()