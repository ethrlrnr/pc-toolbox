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

parser.add_argument(
    'source_csv_alerts_list',
    type=str,
    help='CSV filename of the file with the list of alerts to dismiss via POST.')

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

#Put column values from CSV into a dataframe
data = pandas.read_csv(args.source_csv_alerts_list)

#Filter out all columns in dataframe and focus on one.
data1 = data.filter(['id'])

#Method to ensure any rows with NaN values are dropped before we build out list. 
# data1.dropna(subset=['id']) - Drops NaN value for a specific column. Below drops NaN everywhere, either will work here. 
data2 = data1.dropna()
# print(data2)

# # Sort out and build the filters JSON
# print('Local - Building the filter JSON package...', end='')
alert_info = {}


#take all values in ID column and make a list of strings. The numby array method would fail here, complain JSON wasn't serializable: alert_info["alerts"] = data["id"].values
alert_info["alerts"] = data2["id"].values.tolist()

#Using the API documentation,nesting filters requires knowledge whether the element is something like an object, string, array of strings.  Objects require "{}" before you can flow down to the next value. See code below as an example.
alert_info['filter'] = {}
alert_info['filter']['timeRange'] = {}
alert_info['filter']['timeRange']['type'] = "relative"
alert_info['filter']['timeRange']['value'] = {}
alert_info['filter']['timeRange']['value']['unit'] = "day"
alert_info['filter']['timeRange']['value']['amount'] = args.timerange
alert_info['filter']['detailed'] = "true"

alert_info["dismissalNote"] = 'Alert(s) dismissed from API. Action can be tracked in Prisma audit logs. Please reach out to Risk & Security for more information.'

# print(alert_info)

# {"alerts":["P-43","P-432"],"filter":{"timeRange":{"value":{"unit":"year","amount":1},"type":"relative"},"detailed":true},"dismissalNote":"Alert dismissed from API. Test'"}  <----JSON successful 200 post elements in Postman
# {'alerts': ['P-43', 'P-432'], 'filter': {'timeRange': {'type': 'relative', 'value': {'unit': 'day', 'amount': 9}}, 'detailed': 'true'}, 'dismissalNote': 'Alert dismissed from API. Test'} <----Python print elements matches successful JSON post from Postman cURL

pc_settings, response_package = pc_lib_api.api_dismiss_alert_post(pc_settings, data=alert_info)
print('Done.')


#https://docs.paloaltonetworks.com/prisma/prisma-cloud/prisma-cloud-admin/manage-prisma-cloud-alerts/view-respond-to-prisma-cloud-alerts.html
