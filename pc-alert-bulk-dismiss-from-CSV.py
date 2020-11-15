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
    '-tr',
    '--timerange',
    type=int,
    default=30,
    help='(Optional) - Time Range in days.  Defaults to 30.')



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

# Sort out API Login
print('API - Getting authentication token...', end='')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')

# # Sort out and built the filters JSON
# print('Local - Building the filter JSON package...', end='')
resource_info_scan = {}

data = pandas.read_csv("sample.csv")

#take all values in ID column and make a list. The numby array method would fail here. 
resource_info_scan["alerts"] = data["id"].values.tolist()



resource_info_scan['filter'] = {}
resource_info_scan['filter']['timeRange'] = {}
resource_info_scan['filter']['timeRange']['type'] = "relative"
resource_info_scan['filter']['timeRange']['value'] = {}
resource_info_scan['filter']['timeRange']['value']['unit'] = "day"
resource_info_scan['filter']['timeRange']['value']['amount'] = args.timerange
resource_info_scan['filter']['detailed'] = "true"

resource_info_scan["dismissalNote"] = 'Alert dismissed from API. Action can be tracked in Prisma audit logs. Please reach out to Risk & Security for more information.'

# {"alerts":["P-4316284","P-4316285"],"filter":{"timeRange":{"value":{"unit":"year","amount":1},"type":"relative"},"detailed":true},"dismissalNote":"Alert dismissed from API. Test'"}  <----JSON successful 200 post elements
# {'alerts': ['P-4316284', 'P-4316285'], 'filter': {'timeRange': {'type': 'relative', 'value': {'unit': 'day', 'amount': 9}}, 'detailed': 'true'}, 'dismissalNote': 'Alert dismissed from API. Test'} <----Python elements matches successful JSON post 


print(resource_info_scan)


# print('Done.')
# # Get alerts list
# print('API - Getting alerts list...', end='')
pc_settings, response_package = pc_lib_api.api_dismiss_alert_post(pc_settings, data=resource_info_scan)
print('Done.')


#https://docs.paloaltonetworks.com/prisma/prisma-cloud/prisma-cloud-admin/manage-prisma-cloud-alerts/view-respond-to-prisma-cloud-alerts.html