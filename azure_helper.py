from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime
import pytz
import json 

def azure_report(report_days, azure_creds, logger):
        '''
        Getting the AZURE credentials and generating a report for all the instances that have been running since {report_days}.

        args:
            report_days : number of days since an instance in running
            azure_creds : getting the azure credentials
            logger : logger object to get generate logs 

        and appending it in .json file which is generated daily based on the date
        '''
        credentials = ClientSecretCredential(
            client_secret=azure_creds['client_secret'],
            client_id=azure_creds['client_id'],
            tenant_id=azure_creds['tenant_id'],
            )
        compute_client = ComputeManagementClient(credentials, azure_creds['subscription_id'])
        day = datetime.today().strftime('%Y-%m-%d')
        dt = datetime.strptime(day, "%Y-%m-%d")
        timezone = pytz.UTC
        dt_with_timezone = timezone.localize(dt)
        info = []     
        try:
            for vm in compute_client.virtual_machines.list_all():
                if abs((vm.time_created - dt_with_timezone).days) >= int(report_days):
                    logger.info(f"VM name which is running from last {report_days} or more than {report_days} days - {vm.name}") 
                    id = vm.id
                    splitIDbyslash = id.split('/')
                    time_created = vm.time_created.strftime("%Y/%m/%d %H:%M")
                    if vm.os_profile.linux_configuration is not None:
                        osName = "linux"
                    elif vm.os_profile.windows_configuration is not None:
                        osName = "Window"
                    
                    vm_info = {
                        "VM Name": vm.name,
                        "VM ID": vm.id,
                        "VM Resource Group": splitIDbyslash[4],
                        "VM operating system": osName,
                        "VM Subscription ID": splitIDbyslash[2],
                        "Region": vm.location,
                        "VM type": vm.type,
                        "VM id" : vm.vm_id,
                        "Provisioning state": vm.provisioning_state,
                        "VM Launch Time": time_created
                        }
                    info.append(vm_info)
            file = open(f"azure_{day}.json","a")
                    
            file.write(json.dumps(info))
            file.close()
            logger.info("VM report is generated")
        except Exception as e:
            logger.error("Recheck the credentials", e)
# help(azure_report)