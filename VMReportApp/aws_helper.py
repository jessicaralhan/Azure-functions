from datetime import datetime
import boto3
import json
import pytz




def aws_report(aws_creds, report_days, logger):
        '''
        Getting the AWS credentials and generating a report for all the instances that have been running since {report_days}

        args:
            report_days : number of days since an instance in running
            aws_creds : getting the AWS credentials
            logger : logger object to get generate logs 

        and appending it in .json file which is generated daily based on the date

        '''
        ec2_client = boto3.client('ec2', aws_access_key_id=aws_creds['access_key'], aws_secret_access_key=aws_creds['secret_key'], region_name=aws_creds['region'])
        response = ec2_client.describe_instances()
        ec2_info = []
        day = datetime.today().strftime('%Y-%m-%d')
        dt = datetime.strptime(day, "%Y-%m-%d")
        timezone = pytz.UTC
        dt_with_timezone = timezone.localize(dt)
        try: 
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    if abs((instance['LaunchTime'] - dt_with_timezone).days) >= int(report_days):
                        instance_name = instance['Tags'][0]['Value']
                        logger.info(f"VM name which is running from last {report_days} or more than {report_days} days - {instance_name}")
                        logger.info(f"Running EC2 - {instance_name}")
                        instance_id = instance['InstanceId']
                        instance_type = instance['InstanceType']
                        state = instance['State']['Name']
                        time = instance['LaunchTime']
                        launch_time = time.strftime("%Y/%m/%d %H:%M")
                        Region = instance['Placement']['AvailabilityZone']
                        instance_info = {
                            "VM Name": instance_name,
                            "VM ID": instance_id,
                            "VM Type": instance_type,
                            "Region": Region,
                            "VM State": state,
                            "VM Launch Time": launch_time
                        }
                        ec2_info.append(instance_info)
            file = open(f"aws_{day}.json","a")
            file.write(json.dumps(ec2_info))
            file.close()
            logger.info("EC2 report is generated")
            
    
        except Exception as e:
            logger.error("An error has occured. Check the credentials", e)

# help(aws_report)