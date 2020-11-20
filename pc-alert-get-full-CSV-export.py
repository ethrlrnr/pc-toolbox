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
from datetime import datetime, date, time

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

#### Example of using the v2 alerts API call with a filter ####

# --Main-- #
# Get login details worked out
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl)

# Verification (override with -y)
if not args.yes:
    print()
    print('Ready to excute commands aginst your Prisma Cloud tenant.')
    verification_response = str(input('Would you like to continue (y or yes to continue)?'))
    continue_response = {'yes', 'y'}
    print()
    if verification_response not in continue_response:
        pc_lib_general.pc_exit_error(400, 'Verification failed due to user response.  Exiting...')

# Sort out API Login
print('API - Getting authentication token...', end='')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')

# Sort out and built the filters JSON
print('Local - Building the filter JSON package...', end='')
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
print('Done.')


# Get alerts list
print('API - Getting alerts list...', end='')
pc_settings, response_package = pc_lib_api.api_alert_v2_list_get(pc_settings, data=alerts_filter)
alerts_list = response_package['data']
print('Done.')

#Save as CSV from JSON (requires pandas library to be installed) <-------------------


# Get the cloud type specified in the argument (CLI)
type = args.cloudtype

# Get the current time/date 
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

# Put the json inside a dataframe
rr = pandas.json_normalize(alerts_list['items']) 


# Change timestamp for specific column from UNIX time to any time zone. 
rr['alertTime']=(pandas.to_datetime(rr['alertTime'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
rr['lastSeen']=(pandas.to_datetime(rr['lastSeen'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
rr['firstSeen']=(pandas.to_datetime(rr['firstSeen'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
rr['policy.lastModifiedOn']=(pandas.to_datetime(rr['policy.lastModifiedOn'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))


print('Saving JSON contents as a CSV...', end='')
rr.to_csv('%s_alerts_output_{}.csv'.format(now) % type, sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z')  
print('Done.')
