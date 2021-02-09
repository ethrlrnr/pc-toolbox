#level 4 user role from prisma cloud website

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
    'source_csv_user_roles_list',
    type=str,
    help='Filename of the file with the list of account groups to import (CSV). "Use output file from "pc-account-groups-names-string-filter-CSV-export.py" to generate this')


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
print('API - Getting current user list...', end='')
pc_settings, response_package = pc_lib_api.api_user_role_list_get(pc_settings)
user_role_list_old = response_package['data']
print('Done.')

#level 4 User Role CVS
print('File - Loading CSV user data...', end='')
user_role_list_new = pandas.read_csv(args.source_csv_user_roles_list)
print('Done.')

#level 3 account groups
print('API - Getting user roles...', end='')
pc_settings, response_package = pc_lib_api.api_accounts_groups_list_get(pc_settings)
account_group_list = response_package['data']
#print(account_group_list)
print('Done.')

# print('Searching for account group to get account group ID...', end='')
# account_group_id = None
# #for each level 3 account list-- 
# for account_group in account_group_list:
    # if account_group['name'].lower() == args.userrolename.lower():
        # account_group_id = account_group['id']
        # break
# if account_group_id is None:
    # pc_lib_general.pc_exit_error(400, 'No account group by that name found.  Please check the account group and try again.')
# print('Done.')

print('Formatting imported user list and checking for duplicates by e-mail...', end='')
user_roles_added_count = 0
user_roles_skipped_count = 0
user_roles_duplicate_count = 0
# Convert groupId to an array for import
print('Data - Converting CSV data format for import...', end='')
# below creates an empty list (this is master array)
user_roles_to_import = []

#for user_new in import_list_from_csv:
#looping through level 4 CSV first
for row_dict in user_role_list_new.to_dict(orient="records"):
    # row_dict_id = row_dict['id']
    print(row_dict['id'])
    #Check for duplicates in the imported CSV
    user_role_exists = False

	#loop through level 3
    for user_duplicate_check in account_group_list:
        
		#if the ID in level 3 matches the ID in level 4, do NOTHING BREAK.
        if user_duplicate_check['id'] == row_dict['id']:
            print("Found one!")
            #print(user_duplicate_check['id']) 
            user_role_exists = True
            user_roles_duplicate_count = user_roles_duplicate_count + 1
            break
    
	#after going through all the level 3s, now have a list of CSV items that are not in level 3 account groups. 
    if not user_role_exists:
        print("this one does not exist")		
        print(row_dict['id'])
        # # Check for duplicates already in the Prisma Cloud Account via NAME. this should check NAME in level 2. currently does level 3. 
        for user_role_old in account_group_list:
            if row_dict['name'].lower() == user_role_old['name'].lower():
                user_roles_skipped_count = user_roles_skipped_count + 1
                user_role_exists = True
                print("duplicate already in prisma cloud.")
                break
		#if still false, this means these need to  be added to level 3 account groups. 
        if not user_role_exists:
            temp_accounts_group = {}
            temp_accounts_group['accountGroupIds'] = [row_dict['id']]
            temp_accounts_group['name'] = row_dict['name']
            #print_accounts_group['name'] = row_dict['name']
            temp_accounts_group['description'] = 'Role Mapped to GCP Project'
            temp_accounts_group['roleType'] = 'Account Group Read Only'
            user_roles_added_count = user_roles_added_count + 1
            user_roles_to_import.append(temp_accounts_group)
            #user_roles_to_import_print.append(print_accounts_group)


# #each temp account group row will look like ---> {'accountIds': ['automation-tooling-4857'], 'name': 'automation-tooling-4857'}
        
# #append each new dictionary to the master array (user_roles_to_import)

print(user_roles_to_import)

# print(user_roles_to_import)
# #the master array should look like this---->[{'accountIds': ['automation-tooling-4857'], 'name': 'automation-tooling-4857'}, {'accountIds': ['crew-manager-nextgen-6006'], 'name': 'crew-manager-nextgen-6006'}, {'accountIds': ['istioegressgateway-5876'], 'name': 'istioegressgateway-5876'}]
# print('Done.')
           
# #for each dictionary in the master array, send one row at a time to pc_lib_api.
# #for example, send first---->{'accountIds': ['automation-tooling-4857'], 'name': 'automation-tooling-4857'}
# #this imports each group one at a time.
# for user_role_to_add in user_roles_to_import:
    # print('Adding account name: ' + user_role_to_add['name'])
    # print(user_role_to_add['accountGroupIds'])
 
    # pc_settings, response_package = pc_lib_api.api_user_role_add(pc_settings, user_role_to_add)

# print('Users to add: ' + str(user_roles_added_count))
# print('Users skipped (Duplicates): ' + str(user_roles_skipped_count))
# print('Users removed as duplicates from CSV: ' + str(user_roles_duplicate_count))
# print('Import Complete.')

#if receive status code 200, group imported correctly.

#if receive Status Error 400: three reasons you might get this error:
# (1) this exact cloud account group already exists. Most likely this is why getting Error 400.
# (2) the formatting of accoutIds is incorrect. This was initial error, had to make accountIds an array of strings to meet api requirements.
# (3) the formatting of account group name is inocrrect. must be a string.