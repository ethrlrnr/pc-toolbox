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
print('Local - Building the filter JSON package and checking for cloud provider specificed...')
print (args.cloudtype)
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

#In order to get an RQL query column populated and mapped to specific alerts, first we need to combine response from a policy list response and a saved search list response. Alerts response has a policyID field which we can map to this combo response to extract the associated RQL (if applicable)
print('API - Data Call 1 - Getting current policy list, this will help tie alerts to an RQL query...')
pc_settings, response_package = pc_lib_api.api_policy_v2_list_get_enabled(pc_settings)
policy_v2_list = response_package['data']
print('Done')

pu = pandas.json_normalize(policy_v2_list) #put json inside a dataframe
print('Putting JSON reponse inside dataframe #1  - policy_v2_list')
print('Done')

print('API - Data Call 2 - Getting saved search history list, this will help tie alerts to an RQL query...')
pc_settings, response_package = pc_lib_api.api_search_get_all(pc_settings)
saved_searches = response_package['data']

pu2 = pandas.json_normalize(saved_searches)
print('Putting JSON response inside dataframe #2 - saved_searches')
print('Done')


print('API - Mapping "policy" and "saved search" dataframes before appending RQL "query" column')
pu['query'] = pu['rule.criteria'].map(pu2.set_index('id')['query'])
print('Done')

# Get alerts list
print('API - Data Call 3 - Getting alerts list. The more days pulled, the longer this step will take. Please wait, if this times out with a 504 server side error, apply more filters or lower the days pulled.')
pc_settings, response_package = pc_lib_api.api_alert_v2_list_get(pc_settings, data=alerts_filter)
alerts_list = response_package['data']
print('Done.')

#Save as CSV from JSON (requires pandas library to be installed) <-------------------

rr = pandas.json_normalize(alerts_list['items']) #put json inside a dataframe
print('Putting JSON response inside dataframe #3 - alerts_list')
print('Done')

type = args.cloudtype
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

#Now that the query column from the Saved Search response has been merged into the policy dataframe. Next step is to map the policy dataframe to the alerts dataframe (policy ID is the index). Once mapped one can associate the "query" from the saved search with a specific alert. 
print('API - Mapping "policy" dataframe with appended RQL column to "alerts" data frame. This will allow the script to add the query column to the alerts dump.')
rr['query'] = rr['policy.policyId'].map(pu.set_index('policyId')['query'])
print('Done')


print ('Converting the main time stamp column in dataframe to time/date. By default, Prisma Cloud stores the time stamp in Unix epoch time. This code will also convert the default time zone from Coordinated Universal Time (UTC) to Chicago/Central Time (CDT).')
rr['alertTime']=(pandas.to_datetime(rr['alertTime'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
column_exist_check = "investigateOptions.searchId" in rr


print ('Check on whether any investigation links were provided in the JSON response: ' + str(column_exist_check))
print('Done')
print ('Assembling columns specific to AWS or GCP, this includes all tag/label information pulled in from ServiceNow(SNOW). If tags/labels from SNOW exists for a specific alert in Prisma Cloud, they will show up in the CSV.')

#Specifies which which columns to grab on this lite version. AWS uses "tags" and GCP uses "labels" so we must be sure the correct column names are called. The columns below can be swapped out for anything found in the JSON response ("rr" in this case). Condition check above is for the investigate column which isn't always populated with data.
if args.cloudtype == "gcp": 
    if column_exist_check == True:
        gcp_LITE_FIELDS = ["id", "status", "alertTime", "policy.severity", "policy.name", "policy.policyId",  "policy.policyType", "policy.recommendation","resource.cloudType", "resource.cloudAccountGroups", "resource.resourceType", "resource.resourceApiName", "resource.account", "resource.rrn", "resource.name", "resource.region", "resource.regionId", "resource.data.labels.owner", "resource.data.labels.owner_email","resource.data.labels.contact_email", "resource.data.payload.authenticationInfo.principalEmail", "resource.data.labels.business_service", "resource.data.labels.environment","resource.data.labels.business_unit", "resource.data.labels.name", "resource.data.status", "investigateOptions.searchId", "query"]
#Reindex, if one of our columns is empty the code will proceed and not error out. 	
        rr2 = rr.reindex(columns=gcp_LITE_FIELDS)
    
        rr2.loc[rr2['investigateOptions.searchId'].notnull(), 'investigateOptions.searchId'] = rr2['investigateOptions.searchId'].apply(lambda x: "{}{}".format('https://app3.prismacloud.io/investigate?searchId=', x))
    #rr2.loc[rr2['investigateOptions.searchId'].isnull(), 'investigateOptions.searchId'] = 
#We can specify additional parameters in the post processing. Data_Format, provides the time format for the AlertTime column. Index=false, removes the 1st column of numbers (index).
        rr2.to_csv('%s_output_{}.csv'.format(now) % type, sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 

    else:
        gcp_LITE_FIELDS = ["id", "status", "alertTime", "policy.severity", "policy.name", "policy.policyId", "policy.policyType", "policy.recommendation","resource.cloudType", "resource.cloudAccountGroups", "resource.resourceType", "resource.resourceApiName", "resource.account", "resource.rrn", "resource.name", "resource.region", "resource.regionId", "resource.data.labels.owner", "resource.data.labels.owner_email","resource.data.labels.contact_email", "resource.data.payload.authenticationInfo.principalEmail", "resource.data.labels.business_service", "resource.data.labels.environment","resource.data.labels.business_unit", "resource.data.labels.name", "resource.data.status", "query"]
#Reindex, if one of our columns is empty the code will proceed and not error out. 	
        rr2 = rr.reindex(columns=gcp_LITE_FIELDS)
    
#We can specify additional parameters in the post processing. Data_Format, provides the time format for the AlertTime column. Index=false, removes the 1st column of numbers (index).
        rr2.to_csv('%s_output_{}.csv'.format(now) % type, sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z')
	
if args.cloudtype == "aws": 
    if column_exist_check == True:
        aws_LITE_FIELDS = ["id", "status", "alertTime", "policy.severity", "policy.name", "policy.policyId", "policy.policyType", "policy.recommendation","resource.cloudType", "resource.cloudAccountGroups", "resource.resourceType", "resource.resourceApiName", "resource.account", "resource.rrn", "resource.name", "resource.region", "resource.regionId", "resource.data.tagSets.Owner", "resource.data.tagSets.OwnerEmail", "resource.data.tagSets.ContactEmail","resource.data.tagSets.TechnicalService", "resource.data.tagSets.BusinessService","resource.data.tagSets.Environment","resource.data.tagSets.BusinessUnit", "investigateOptions.searchId", "query"]
#Reindex, if one of our columns is empty the code will proceed and not error out. 	
        rr2 = rr.reindex(columns=aws_LITE_FIELDS)
    
        rr2.loc[rr2['investigateOptions.searchId'].notnull(), 'investigateOptions.searchId'] = rr2['investigateOptions.searchId'].apply(lambda x: "{}{}".format('https://app3.prismacloud.io/investigate?searchId=', x))
    #rr2.loc[rr2['investigateOptions.searchId'].isnull(), 'investigateOptions.searchId'] = 
#We can specify additional parameters in the post processing. Data_Format, provides the time format for the AlertTime column. Index=false, removes the 1st column of numbers (index).
        rr2.to_csv('%s_output_{}.csv'.format(now) % type, sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 

    else:
        aws_LITE_FIELDS = ["id", "status", "alertTime", "policy.severity", "policy.name", "policy.policyId", "policy.policyType", "policy.recommendation","resource.cloudType", "resource.cloudAccountGroups", "resource.resourceType", "resource.resourceApiName", "resource.account", "resource.rrn", "resource.name", "resource.region", "resource.regionId", "resource.data.tagSets.Owner", "resource.data.tagSets.OwnerEmail", "resource.data.tagSets.ContactEmail","resource.data.tagSets.TechnicalService", "resource.data.tagSets.BusinessService","resource.data.tagSets.Environment","resource.data.tagSets.BusinessUnit", "query"]
#Reindex, if one of our columns is empty the code will proceed and not error out. 	
        rr2 = rr.reindex(columns=aws_LITE_FIELDS)
    
#We can specify additional parameters in the post processing. Data_Format, provides the time format for the AlertTime column. Index=false, removes the 1st column of numbers (index).
        rr2.to_csv('%s_output_{}.csv'.format(now) % type, sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 		

print('Done')
print('Saving JSON contents as a CSV...')
print('Done.')
 
