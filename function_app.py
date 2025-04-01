import azure.functions as func
import logging
from main import running_vms  # Importing the core VM report function
from main import get_configuration
from datetime import datetime

# Create the Azure Function App
app = func.FunctionApp()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Schedule function to run every day at 6 PM UTC (or another schedule)
@app.schedule('0 18 * * *', name='running_vms_schedule')
def scheduled_task(timer: func.TimerRequest) -> None:
    '''This function will be triggered on a daily basis at 6 PM UTC.'''
    logger.info("Azure function triggered.")
    
    # Fetch the configuration and run the report generation logic
    report_days, azure_creds, aws_creds = get_configuration()
    
    if report_days is None:
        logger.error("Failed to retrieve configuration for report days.")
        return
    
    running_vms(report_days, azure_creds, aws_creds)
    logger.info(f"VM report generation executed at {datetime.now()}")

