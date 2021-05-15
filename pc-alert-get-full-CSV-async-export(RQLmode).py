from __future__ import print_function
try:
    input = raw_input
except NameError:
    pass
import argparse
import pc_lib_api
import pc_lib_general
import json
import pandas
import time
import sys
from datetime import datetime, date

# --Execution Block-- #
# --Parse command line arguments-- #
parser = argparse.ArgumentParser(prog='rltoolbox')

parser.add_argument(
    '-u',
    '--username',
    type=str,
    help='*Required* - Prisma Cloud API Access Key ID that you want to set to access your Prisma Cloud account.')

parser.add_argument(
    '-p',
    '--password',
    type=str,
    help='*Required* - Prisma Cloud API Secret Key that you want to set to access your Prisma Cloud account.')

parser.add_argument(
    '-url',
    '--uiurl',
    type=str,
    help='*Required* - Base URL used in the UI for connecting to Prisma Cloud.  '
         'Formatted as app.prismacloud.io or app2.prismacloud.io or app.eu.prismacloud.io, etc.  '
         'You can also input the api version of the URL if you know it and it will be passed through.')

parser.add_argument(
    '-y',
    '--yes',
    action='store_true',
    help='(Optional) - Override user input for verification (auto answer for yes).')

parser.add_argument(
    '--detailed',
    action='store_true',
    help='(Optional) - Detailed alerts response.')
	
parser.add_argument(
    '--matrixmode',
    action='store_true',
    help='(Optional) - Print out JSON responses.')

parser.add_argument(
    '-fas',
    '--alertstatus',
    type=str,
    help='(Optional) - Filter - Alert Status.')
	
parser.add_argument(
    '-aid',
    '--alertid',
    type=str,
    help='(Optional) - Filter - Alert ID.')

parser.add_argument(
    '-fpt',
    '--policytype',
    type=str,
    help='(Optional) - Filter - Policy Type.')
	
parser.add_argument(
    '-fpcs',
    '--policycomplianceStandard',
    type=str,
    help='(Optional) - Filter - Policy Compliance Standard.')
	
parser.add_argument(
    '-fps',
    '--policyseverity',
    type=str,
    help='(Optional) - Filter - Policy Severity.')
		
parser.add_argument(
    '-fct',
    '--cloudtype',
    type=str,
    help='(Optional) - Filter - Cloud Type.')
parser.add_argument(
    '-fca',
    '--cloudaccount',
    type=str,
    help='(Optional) - Filter - Cloud Account.')
parser.add_argument(
    '-fcaid',
    '--cloudaccountid',
    type=str,
    help='(Optional) - Filter - Cloud Account ID.')
parser.add_argument(
    '-fcr',
    '--cloudregion',
    type=str,
    help='(Optional) - Filter - Cloud Region.')

parser.add_argument(
    '-tr',
    '--timerange',
    type=int,
    default=30,
    help='(Optional) - Time Range in days.  Defaults to 30.')

parser.add_argument(
    '-l',
    '--limit',
    type=int,
    default=500,
    help='(Optional) - Return values limit (Default to 500).')
parser.add_argument(
    '-fagt',
    '--accountgroup',
    type=str,
    help='(Optional) - Filter - Account Group.')
parser.add_argument(
    '-fpid',
    '--policyid',
    type=str,
    help='(Optional) - Filter - Policy ID.')	
parser.add_argument(
    '-frid',
    '--resourceid',
    type=str,
    help='(Optional) - Filter - Resource ID.')	

args = parser.parse_args()
# --End parse command line arguments-- #

print('User login')
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl)
print('Done')
# Verification (override with -y)
if not args.yes:
    print()
    print('Ready to excute commands aginst your Prisma Cloud tenant.')
    verification_response = str(input('Would you like to continue (y or yes to continue)?'))
    continue_response = {'yes', 'y'}
    print()
    if verification_response not in continue_response:
        pc_lib_general.pc_exit_error(400, 'Verification failed due to user response.  Exiting...')

#----------------------------------------------------------------------
print('API - Data Call 1 - Getting authentication token..')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')

print ('Cloud Type Specified in CLI =', args.cloudtype)
print('Building the filters for JSON package.')

alerts_filter = {}

if args.detailed:
    alerts_filter['detailed'] = True
else:
    alerts_filter['detailed'] = False

alerts_filter['timeRange'] = {}
alerts_filter['timeRange']['type'] = "relative"
alerts_filter['timeRange']['value'] = {}
alerts_filter['timeRange']['value']['unit'] = "day"
alerts_filter['timeRange']['value']['amount'] = args.timerange

alerts_filter['sortBy'] = ["id:asc"]

alerts_filter['offset'] = 0

alerts_filter['limit'] = args.limit

alerts_filter['filters'] = []
if args.alertstatus is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "alert.status"
    temp_filter['value'] = args.alertstatus
    alerts_filter['filters'].append(temp_filter)
if args.alertid is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "alert.id"
    temp_filter['value'] = args.alertid
    alerts_filter['filters'].append(temp_filter)
if args.cloudaccount is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "cloud.account"
    temp_filter['value'] = args.cloudaccount
    alerts_filter['filters'].append(temp_filter)
if args.cloudregion is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "cloud.region"
    temp_filter['value'] = args.cloudregion
    alerts_filter['filters'].append(temp_filter)
if args.accountgroup is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "account.group"
    temp_filter['value'] = args.accountgroup
    alerts_filter['filters'].append(temp_filter)
if args.cloudaccountid is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "cloud.accountId"
    temp_filter['value'] = args.cloudaccountid
    alerts_filter['filters'].append(temp_filter)
if args.cloudtype is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "cloud.type"
    temp_filter['value'] = args.cloudtype
    alerts_filter['filters'].append(temp_filter)
if args.policytype is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "policy.type"
    temp_filter['value'] = args.policytype
    alerts_filter['filters'].append(temp_filter)
if args.policycomplianceStandard is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "policy.complianceStandard"
    temp_filter['value'] = args.policycomplianceStandard
    alerts_filter['filters'].append(temp_filter)
if args.policyseverity is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "policy.severity"
    temp_filter['value'] = args.policyseverity
    alerts_filter['filters'].append(temp_filter)
if args.policyid is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "policy.id"
    temp_filter['value'] = args.policyid
    alerts_filter['filters'].append(temp_filter)
if args.resourceid is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "resource.id"
    temp_filter['value'] = args.policyid
    alerts_filter['filters'].append(temp_filter)

print('Done building filters specified in CLI.')

#----------------------------------------------------------------------
print('API - Data Call 2 - Plugging in filters, a granular JSON response is now being prepared by Prisma. A job ID will be provided.')
pc_settings, response_package = pc_lib_api.api_async_alerts_job(pc_settings, data=alerts_filter)
alerts_job_number = response_package

print('Putting JSON response inside a dataframe - job_id')
job_id_json = pandas.json_normalize(alerts_job_number) #put json inside a dataframe

#Grab the job ID which we will plug into a URL, this will allow a user to check status and download. We first must convert it to a string (schema purposes for URL) and then deal with unneccesary characters.
job_id_string = job_id_json['data.id'].to_string()

#For the job ID, will remove the first 5 characters since JSON pulls characters not relevant to the job ID.
job_id = job_id_string[5:]

print('Our job number is', job_id)

#----------------------------------------------------------------------
print('API - Data Call 3 - Using the job ID, we can now plug this into a URL to track status updates for alerts job.') 
pc_settings, response_package = pc_lib_api.api_async_alerts_job_status(pc_settings, job_id)
alerts_job_status = response_package

if args.matrixmode == True:
    print(alerts_job_status)
	
else:
    print('Done')

print('Putting JSON response inside a dataframe - alert_status')
jobs_status_json = pandas.json_normalize(alerts_job_status)
print('Done')

#Before using this status check in the "IF" "ELSE" section below, we first have to convert the data to a string in order to help strip unneccesary characters.
jobs_status_string = jobs_status_json['data.status'].to_string()

#For the status, will remove the first 5 characters since it pulls characters not relevant to the status.
status_check = jobs_status_string[5:]
test = status_check.split()

print('Now lets create a loop to continously check on job status. Once the status changes from "IN_PROGRESS" to "READY_TO_DOWNLOAD", we will break the loop.')

for boston in test:
    
    while status_check == "IN_PROGRESS":
        print('Please wait, alert data job still in progress. Once status changes from "IN_PROGRESS" to "READY_TO_DOWNLOAD", this message will disappear and the code will proceed to the next step. Retries occur every 60 seconds:')
        for i in range(60,0,-1):
            sys.stdout.write(str(i)+' ')
            sys.stdout.flush()
            time.sleep(1)
        pc_settings, response_package = pc_lib_api.api_async_alerts_job_status(pc_settings, job_id)
        alerts_job_status1 = response_package
        jobs_status_json1 = pandas.json_normalize(alerts_job_status1)	
        jobs_status_string1 = jobs_status_json1['data.status'].to_string()
        status_check1 = jobs_status_string1[5:]
        if status_check1 == "READY_TO_DOWNLOAD":
        
	        break
        
print('Job is now ready for download.')        
#----------------------------------------------------------------------!=
print('Done grabbing the JSON')

print('API - Data Call 4 - Downloading the list of alerts as a JSON response.')
pc_settings, response_package = pc_lib_api.api_async_alerts_job_download(pc_settings, job_id)
alerts_job_download = response_package

print('Putting JSON response inside a dataframe - async_alerts_list')
#data simply refers to the top most JSON key you want to begin sorting by in JSON reponse. 
rr = pandas.json_normalize(alerts_job_download['data']) 

# Change timestamp for specific column from UNIX time to any time zone. 
rr['alertTime']=(pandas.to_datetime(rr['alertTime'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
rr['lastSeen']=(pandas.to_datetime(rr['lastSeen'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
rr['firstSeen']=(pandas.to_datetime(rr['firstSeen'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
rr['policy.lastModifiedOn']=(pandas.to_datetime(rr['policy.lastModifiedOn'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

type = args.cloudtype

#current time/date utilized in CSV output filesnames
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

print('Saving JSON contents as a CSV...', end='')
rr.to_csv('%s_alerts_output_{}.csv'.format(now) % type, sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z')  
print('Done.')


