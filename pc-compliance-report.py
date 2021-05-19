from __future__ import print_function
try:
    input = raw_input
except NameError:
    pass
import argparse
import pc_lib_api
import pc_lib_general
import json
import sys
import pandas
from datetime import datetime, date, time
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

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
    '-fpcs',
    '--policycomplianceStandard',
    type=str,
    help='(Optional) - Filter - Policy Compliance Standard.')
	

		
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
    '-ss',
    '--scanstatus',
    type=str,
    help='(Optional) - Filter - "all", "passed" or "failed". Default is "all" which includes unscanned items.')

args = parser.parse_args()
# --End parse command line arguments-- #

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


#---------------------------------------------------------------------------------------------------------------#
# Sort out API Login
print('API Call #1 - Getting authentication token...')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')

#---------------------------------------------------------------------------------------------------------------#
# Sort out and build the filters JSON for resource info
print('Building the filter JSON package...', end='')
resource_info_scan = {}

resource_info_scan['timeRange'] = {}
resource_info_scan['timeRange']['type'] = "relative"
resource_info_scan['timeRange']['value'] = {}
resource_info_scan['timeRange']['value']['unit'] = "day"
resource_info_scan['timeRange']['value']['amount'] = args.timerange

# resource_info_scan['scan.status'] = args.scanstatus

resource_info_scan['filters'] = []

if args.cloudaccount is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "cloud.account"
    temp_filter['value'] = args.cloudaccount
    resource_info_scan['filters'].append(temp_filter)
if args.cloudregion is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "cloud.region"
    temp_filter['value'] = args.cloudregion
    resource_info_scan['filters'].append(temp_filter)
if args.accountgroup is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "account.group"
    temp_filter['value'] = args.accountgroup
    resource_info_scan['filters'].append(temp_filter)
if args.cloudtype is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "cloud.type"
    temp_filter['value'] = args.cloudtype
    resource_info_scan['filters'].append(temp_filter)

if args.policycomplianceStandard is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "policy.complianceStandard"
    temp_filter['value'] = args.policycomplianceStandard
    resource_info_scan['filters'].append(temp_filter)

if args.scanstatus is not None:
    temp_filter = {}
    temp_filter['operator'] = "="
    temp_filter['name'] = "scan.status"
    temp_filter['value'] = args.scanstatus
    resource_info_scan['filters'].append(temp_filter)

print('Done.')

#Used for CSV filename output 	
type = args.cloudtype
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

#---------------------------------------------------------------------------------------------------------------#
print('API Call #2 - Getting resource scan information')
pc_settings, response_package = pc_lib_api.api_resource_scan_info(pc_settings, data=resource_info_scan)

#Data is the top most key on JSON response to begin with.
resource_list = response_package['data']

#put json inside a dataframe
rr = pandas.json_normalize(resource_list['resources'])

#---------------------------------------------------------------------------------------------------------------#
print("Prepping the dataframes created from API Call #2.")

#don't need these 2 columns, duplicates of others.
rr.drop(['id', 'accountName'], axis=1, inplace=True)  

#This will take the "overallPassed" column and turn it into a string dtype value from a int64 or float64 value. If not the value_counts code below will not work which gives us the total number of pass/fails. 
rr['overallPassed'] = rr['overallPassed'].apply(str).str.replace('.', ',')

#Replace string values in column, true to passed, false to failed, nan to untested
rr["overallPassed"] = rr["overallPassed"].replace(['True','False','nan'],['Passed','Failed','Untested'])

#Counts the frequence of true or false which will be appended to the column title. NaN means item wasn't scanned. 
passed = rr.overallPassed.str.split(expand=True).stack().value_counts()

#This will take the "passed" returned multi-line values and turn it into a string dtype value.
str1 = passed.apply(str).str.replace('.', ',')

#Removes text "dtype" from output
str2 = str1.to_string()

#Takes the multi-line string and makes it one line. "|" is used as the seperator. 
str3 = "| ".join(str2.splitlines())

#Take lists of policies contained within each column "scannedPolicies and break them out into their own respective columns. Drop the column once complete. The concat piece ensures we stick the results back to the orginal dataframe. 
rr2 = pandas.concat([rr, rr['scannedPolicies'].apply(pandas.Series)], axis = 1).drop('scannedPolicies', axis = 1).add_prefix('PolicyScanned_')


rr2.rename(columns={'PolicyScanned_name':'name', 'PolicyScanned_accountId':'accountId', 'PolicyScanned_regionId':'regionId', 'PolicyScanned_regionName':'regionName', 'PolicyScanned_cloudType':'cloudType', 'PolicyScanned_rrn':'rrn'}, inplace=True)

# # # specifies the column we want to focus on, index starts at 0 and 6 represents "overallPassed". We are always replacing the column title with the total count for passed, failed, and untested.
rr2.columns.values[6] = "Total: " + str3

#---------------------------------------------------------------------------------------------------------------#

print('Building the filter JSON package to plug into the API on the next step for grabbing Sabre users and associated GCP projects. Utilizes a custom saved search ID that must be done in the UI.')
config_search = {}

#Using the API documentation,nesting filters requires knowledge whether the element is something like an object, string, array of strings.  Objects require "{}" before you can flow down to the next value. See code below as an example.
config_search['filter'] = {}
config_search['filter']['timeRange'] = {}
config_search['filter']['timeRange']['type'] = "relative"
config_search['filter']['timeRange']['value'] = {}
config_search['filter']['timeRange']['value']['unit'] = "day"
config_search['filter']['timeRange']['value']['amount'] = 31
#If this code fails, it's due to the saved search ID not being possibly sharable? To create your own ID simply follow the directions below for the RQL needed, once this is saved, click on it and theID should be in the URL bar. Replace the ID with your saved search ID in the next line.
config_search['id'] = 'YOUR_SAVED_SEARCH_ID'
config_search['withResourceJson'] = True

#Instructions: The RQL for your saved search which is leveraged as an "id" above should look something like this: config from cloud.resource where cloud.type = 'gcp' AND api.name = 'gcloud-projects-get-iam-user' AND json.rule = user contains @domain.com and user does not contain gcp and user does not contain test
print('Done.')

#---------------------------------------------------------------------------------------------------------------#
print('API Call #3 - Plugging in a "saved search" id (aka saved RQL search from investigation tab on UI), this will allow data to be returned showing GCP users and their respective GCP project(s). Prisma ingests the Google Resource Manager API to accomplish this.', end='')
pc_settings, response_package = pc_lib_api.api_search_config(pc_settings, data=config_search)
gcp_list = response_package['data']
print('Done.')

#---------------------------------------------------------------------------------------------------------------#
print("Prepping the dataframes created from API Call #3.")

# # Put json inside a dataframe. Go 1 level down on the JSON (data --> items). If not the dataframe gets ruined. 
gcp = pandas.json_normalize(gcp_list['data']['items'])

#focus on columns "id" aka email and "accountID" aka project names.
gcp1 = gcp.filter(['id', 'accountId'])

#sort "id" by email addresses.
gcp1.sort_values(by=['accountId'], ascending = True, inplace=True)

#dump rows which contain a specific string.
gcp2 = gcp1[~gcp1['accountId'].str.contains('some_value|some_value')]


#The dataframe will most likely list users multiple times in different rows. This code will group all data by a common value into a single row. Resetting the index will re-add any columns initially lost in the operation (applying the list). More columns can be specified after "roleIds" by just adding a comma. Less messy this way. 
gcp3 = gcp2.groupby('accountId')['id'].apply(list).reset_index()

#print(sys.argv[1:])
# gcp3.to_csv('%s_outputt_{}.csv'.format(now) % type, sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 


#To append roleIds (from our user roles API response) to a dataframe, two dataframes must match on column values. If match is found during compare, the role ID gets added to that row.  
rr2['GCP_Contact_Information(if_available)'] = rr2['accountId'].map(gcp3.set_index('accountId')['id'])

#drop 2 columns if AWS is selected. AccountID shows the same scientific notation for all rows. GCP contact info column is not useful here.
if (args.cloudtype == 'aws' or args.cloudtype == 'AWS'):
	rr2.drop(columns=['accountId', 'GCP_Contact_Information(if_available)'], inplace=True)
	
else:
    print('Done')
	
#Looking at a CSV output is easier to check for issues than a standard print of "rr2" in this scenario.
rr2.to_csv('%s_output_{}.csv'.format(now) % type, sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 

print('CSV saved.')


