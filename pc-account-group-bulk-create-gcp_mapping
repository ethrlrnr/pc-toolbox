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
    'source_csv_cloud_accounts_list',
    type=str,
    help='Filename of the file with the list of cloud accounts to import (CSV). Please use output CSV file generated from "pc-cloud-account-gcp-projects-string-filter-CSV-export.py" or "pc-cloud-account-main-export.py". The only column we really need is "id" from the CSV')

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

print('File - Importing CSV from disk...', end='')
import_list_from_csv = pandas.read_csv(args.source_csv_cloud_accounts_list)
print(import_list_from_csv)
print('Done.')

# Get existing cloud account list
print('API - Getting existing cloud account list...', end='')
#below gets level2
pc_settings, response_package = pc_lib_api.api_cloud_accounts_list_names_get(pc_settings)
cloud_accounts_list = response_package['data']
#print(cloud_accounts_list)

# Convert groupId to an array for import
print('Data - Converting CSV data format for import...', end='')
# below creates an empty list (this is master array)
accounts_groups_to_import = []
#creates a dictionary inside a blank list. Each row in the CSV needs to be a dicitonary. Loop through each row and turn it into dictionary. 
#to_dict uses the pandas dataframe and turns it into a dictionary. Orient Records=do it by row (and not columns) 
for row_dict in import_list_from_csv.to_dict(orient="records"):
	#Important--to match the api requirements:
	#accountIds = 'id' is required to be an array of strings. This means the accountIds must be inside of a list []. Added extra brackets around.
	#name = 'id' also. is just a string. 
	#first create an empty dictionary, then add each item to it (accountIds, name)
	temp_accounts_group = {}
	temp_accounts_group['accountIds'] = [row_dict['id']]
	temp_accounts_group['description'] = 'GCP Project Mapped to Account Group'
	temp_accounts_group['name'] = row_dict['id']
	#each temp account group row will look like ---> {'accountIds': ['automation-tooling-4857'], 'name': 'automation-tooling-4857'}
	
	#append each new dictionary to the master array (accounts_groups_to_import)
	accounts_groups_to_import.append(temp_accounts_group)
	
print(accounts_groups_to_import)
#the master array should look like this---->[{'accountIds': ['autop-tooling-4857'], 'name': 'autop-tooling-4857'}, {'accountIds': ['crew-ma-gen-6006'], 'name': 'crew-ma-gen-6006'}, {'accountIds': ['egressgateway-5876'], 'name': 'gateway-5876'}]
print('Done.')

# Figure out which accounts are already in Prisma Cloud and remove them from the import list
## To Do ##

# Check the remaining list for any duplicate names
## To Do ##


#for each dictionary in the master array, send one row at a time to pc_lib_api. 
#for example, send first---->{'accountIds': ['automation-tooling-47'], 'name': 'automation-tooling-47'}
#this imports each group one at a time. 
for new_accounts_group in accounts_groups_to_import:
    print('Adding account name: ' + new_accounts_group['name'])
    print(new_accounts_group['accountIds'])
    pc_settings, response_package = pc_lib_api.api_accounts_groups_add(pc_settings, new_accounts_group)
print('Import Complete.')

#if receive status code 200, group imported correctly. 

#if receive Status Error 400: three reasons you might get this error:
# (1) this exact cloud account group already exists. Most likely this is why getting Error 400. 
# (2) the formatting of accoutIds is incorrect. This was initial error, had to make accountIds an array of strings to meet api requirements. 
# (3) the formatting of account group name is inocrrect. must be a string. 
