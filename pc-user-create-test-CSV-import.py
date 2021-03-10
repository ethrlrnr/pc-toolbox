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
import ast 

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
    'source_csv_cloud_accounts_list',
    type=str,
    help='Filename of the file with the list of cloud accounts to import (CSV). Please use output CSV file generated from "pc-cloud-account-gcp-projects-string-filter-CSV-export.py" or "pc-cloud-account-main-export.py". The only column we really need is "id" from the CSV')

args = parser.parse_args()
# --End parse command line arguments-- #

# --Main-- #
# Get login details worked out.
print('Stage 1 - API - Response 1 - Login')
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl)
print('Done.')
#---------------------------------------------------------------------------------------------------------------#
# Sort out API Login.
print('Stage 2 - API - Response 2 - Getting authentication token...', end='')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')
#---------------------------------------------------------------------------------------------------------------#

print('Stage 5 - API Response 4 - Getting current user list on Prisma Cloud to compare against (new users vs existing users).', end='')
pc_settings, response_package = pc_lib_api.api_user_list_get(pc_settings)

#"data" is the name of the main key in the JSON response package. Critical to know. 
user_list_get = response_package['data']





#---------------------------------------------------------------------------------------------------------------#
print('Stage 9 - Turn prepped GCP user list csv into a dictionary and iterate through it.')
#turn prepared dataframe to a dictionary. If you try to iterate against a pure dataframe such as gcp5, errors will pop up around integer use etc. 
print('File - Importing CSV from disk...', end='')
import_list_from_csv = pandas.read_csv(args.source_csv_cloud_accounts_list)
print(import_list_from_csv)
print('Done.')


gcp7 = import_list_from_csv.to_dict('records')
gcp8 = str(gcp7).replace('"','')

#Convert string dictionary to dictionary
gcp88 = ast.literal_eval(gcp8) 

print(gcp88)

#---------------------------------------------------------------------------------------------------------------#
print('Stage 10 - Add counter for new users added, users skipped and duplicate users.')
#Add counter
user_added_count = 0
user_skipped_count = 0
user_duplicate_count = 0

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 11 - Sorting and building the filters (JSON package) to plug into the API upon completion (building user profiles).')
#creates a dictionary inside a blank list. Each row in the dataframe needs to be a dicitonary. Loop through each row and turn it into dictionary. 
user_to_import = []

for row_dict in gcp88:
    #Check for duplicates in the dataframe converted to a dictionary
    user_exist = False
    for user_duplicate_check in user_to_import:
        if user_duplicate_check['email'] == row_dict['id']:
            user_duplicate_count = user_duplicate_count + 1
            user_exist = True
            break
    if not user_exist:
        # Check for duplicates already in the Prisma Cloud Account
        for user_old in user_list_get:
            if row_dict['id'] == user_old['email']:
                user_skipped_count = user_skipped_count + 1
                user_exist = True
                break
        if not user_exist:
            temp_user = {}
	#row_dict values pull from the dictionary
            temp_user['roleIds']= row_dict['roleIds']
            temp_user['email'] = row_dict['id']
            temp_user['firstName'] = row_dict['firstName']
            temp_user['lastName'] = '[GCP]'
            temp_user['timeZone'] = 'America/Chicago'
            temp_user['accessKeysAllowed'] = 'true'
            temp_user['defaultRoleId'] = row_dict['defaultRoleId']
            user_added_count = user_added_count + 1
	#append each new dictionary to the master array (user_to_import)
            user_to_import.append(temp_user)

#lets print all the users that will be imported, syntax should align with what's specific on the API documentation for creating a new user profile. They give samples of expected response on website (this is pasted two lines down). Use Postman tool to test at least 1 user creation using cURL then post command.  	
print(user_to_import)
#Expected syntax for filters:
#'{"roleIds":["8989898989-90989889-9898989898","8989898989-90989889-9898989898","8989898989-90989889-9898989898"],"email":"first.last@domain.com","firstName":"bob","lastName":"smith","timeZone":"America/Chicago","defaultRoleId":"8989898989-90989889-9898989898"}'
print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 12 - Plugging in filter criteria into the API via a post. Importing users one at a time. Will print for each user.')

for user_to_add_v2 in user_to_import:
    print('User Email: ',user_to_add_v2['email'])
    print('First Name: ',user_to_add_v2['firstName'])
    print('Last Name: ',user_to_add_v2['lastName'])
    print('Time Zone: ',user_to_add_v2['timeZone'])
    print('Access Key: ',user_to_add_v2['accessKeysAllowed'])
    print('Role IDs: ',user_to_add_v2['roleIds'])
    print('Default Role ID: ',user_to_add_v2['defaultRoleId'])
    
	# #comment out the line below if you don't want this script to post changes to Prisma Cloud.
    pc_settings, response_package = pc_lib_api.api_user_add_v2(pc_settings, user_to_add_v2)
#---------------------------------------------------------------------------------------------------------------#
print('Stage 13 - Final user counts.')
print('Users to add: ' + str(user_added_count))
print('Users skipped (Duplicates): ' + str(user_skipped_count))
print('Users removed as duplicates from dataframe: ' + str(user_duplicate_count))
print('Import Complete.')
#---------------------------------------------------------------------------------------------------------------#

#DF[['new_column_1','new_column_2']] = DF.original_column_to_split_into_new_columns.str.split('/', expand=True)
