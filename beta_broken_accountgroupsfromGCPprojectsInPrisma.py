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
#import pickle

#class Cloudaccounts(dict):
	#def __init__(self, id, name):
		#dict.__init__(self, id=id, name=name)

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
    help='Filename of the file with the list of GCP cloud sub accounts with Prisma ID. Call the CSV dumped from pc-gcp-projects-string-filter-export.py')


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


# use CSV file from created by pc-gcp-projects-string-filter-export.py
print('File - Importing CSV from disk...', end='')
import_list_from_csv = pandas.read_csv(args.source_csv_cloud_accounts_list)
print(import_list_from_csv)
# use CSV file from created by pc-gcp-projects-string-filter-export.py
print('Done.')

# Convert groupId to an array for import
print('Data - Converting CSV data format for import...', end='')
accounts_groups_to_import = []
#creates a dictionary inside a blank list. Each row in the CSV is a dicitonairy
for row_dict in import_list_from_csv.to_dict(orient="records"):

	temp_accounts_group = {}
	temp_accounts_group['name'] = row_dict['name']
	temp_accounts_group['accountIds'] = row_dict['id']
	
	

  
	accounts_groups_to_import.append(temp_accounts_group)
print('DoneDoneDoneDoneDone.')
print(accounts_groups_to_import)
print('Done.')


# Check ingested list for all required fields and data in all fields
## To Do ##

# Check ingested list for any duplicates in the CSV (Names or account ID's)
## To Do ##

# Get existing cloud account list
print('API - Getting existing cloud account list...', end='')
pc_settings, response_package = pc_lib_api.api_accounts_groups_list_get(pc_settings)
#pc_settings, response_package = pc_lib_api.api_cloud_accounts_list_names_get(pc_settings)
#cloud_accounts_list = response_package['data']
#print(cloud_accounts_list)
print('Done Getting existing account list ----------------------.')

# Figure out which accounts are already in Prisma Cloud and remove them from the import list
## To Do ##

# Check the remaining list for any duplicate names
## To Do ##

# Import the account list into Prisma Cloud
print('API - Adding account groups...')
cloud_type = "gcp"
print()


 
for new_accounts_group in accounts_groups_to_import:
	# data2=json.dumps(new_accounts_group)
    print(new_accounts_group)
    #print('Adding account name: ' + new_accounts_group['name'])
    #print('Adding account id: ' + new_accounts_group['accountIds'])
    pc_settings, response_package = pc_lib_api.api_accounts_groups_add(pc_settings, new_accounts_group)
#cant get to second row due to formating of the dictionary

print('Import Complete.')
