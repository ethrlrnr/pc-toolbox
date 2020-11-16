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


# Get alerts list
print('API - Getting alerts list...', end='')
pc_settings, response_package = pc_lib_api.api_resource_scan_info(pc_settings, data=resource_info_scan)
resource_list = response_package['data']
print('Done.')

#NEW - Save as CSV from JSON (requires pandas library to be installed) <-------------------
print('Saving JSON contents as a CSV...', end='')

type = args.cloudtype
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")
rr = pandas.json_normalize(resource_list['resources']) #put json inside a dataframe
rr.drop(['id', 'accountName'], axis=1, inplace=True)  #don't need these 2 columns, duplicates of others.

# rr2 = pandas.concat([rr[['name', 'accountId', 'regionId', 'regionName', 'cloudType', 'rrn', 'overallPassed']], rr['scannedPolicies'].str.split('id', axis=1)

#print(rr.overallPassed)

#This will take the overPassed column and turn it into a string dtype value from a int64 or float64 value. If not the value_counts code below will not work which gives us the total number of pass/fails. 
rr['overallPassed'] = rr['overallPassed'].apply(str).str.replace('.', ',')

#Counts the frequence of true or false which will be appended to the column title. NaN means item wasn't scanned. 
passed = rr.overallPassed.str.split(expand=True).stack().value_counts()

#print(passed)

#This will take the "passed" returned multi-line values and turn it into a string dtype value.
str1 = passed.apply(str).str.replace('.', ',')
#print(str1)

str2 = str1.replace(r"\n", "\t")
print(str2)

#Take lists of policies contained within each column "scannedPolicies and break them out into their own respective columns. Drop the column once complete. The concat piece ensures we stick the results back to the orginal dataframe. 
rr2 = pandas.concat([rr, rr['scannedPolicies'].apply(pandas.Series)], axis = 1).drop('scannedPolicies', axis = 1)




rr2.columns.values[6] = ['overallPassed'] + str2
# print(test)
# pc_settings, response_package = pc_lib_api.api_search_get_all(pc_settings)
# saved_searches = response_package['data']

# pc_settings, response_package = pc_lib_api.api_search_get_all_recent(pc_settings)
# saved_searches_recent = response_package['data']

# pu2 = pandas.json_normalize(saved_searches) #put json inside a dataframe
# pu3 = pandas.json_normalize(saved_searches_recent)

# pu['query'] = pu['rule.criteria'].map(pu2.set_index('id')['query'])
# pu['custom_query'] = pu['rule.criteria'].map(pu3.set_index('id')['query'])



rr2.to_csv('%s_output_{}.csv'.format(now) % type, sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z')  
# print('Done.')
