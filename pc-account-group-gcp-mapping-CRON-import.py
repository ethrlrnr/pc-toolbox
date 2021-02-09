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
		 

args = parser.parse_args()
# --End parse command line arguments-- #

# --Main-- #
# Get login details worked out
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl)

# Sort out API Login
print('API - Getting authentication token...', end='')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')

#Get list of child cloud accounts
print('API - Getting current child cloud accounts list...', end='')
pc_settings, response_package = pc_lib_api.api_cloud_accounts_list_names_get(pc_settings)
cloud_accounts_list_names = response_package['data']

#put json inside a dataframe
pu = pandas.json_normalize(cloud_accounts_list_names) 

#current date/time
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

#Filter down to only rows with "GCP" string
mvp = pu.query('cloudType == "gcp"')

#columns returned are name, cloudtype, parantaccountname and ID. Filter out everything except ID (GCP project name)
#another filter option -->mvp1 = mvp.drop(columns=['name','cloudType','parentAccountName'])
mvp1 = mvp.filter(['id'])

#filter for lines that contain a specific string
mvp2 = mvp1[mvp1['id'].str.contains('sab-')]

#Filter out rows which contain certain strings, add your own items below, this is useful for bulk upload purposes and/or cron jobs. "~" symbol filters out.
mvp3 = mvp2[~mvp2['id'].str.contains('sbx | sandbox | test | retrieveseatmap01 | playground | your_GCP_main_account_ID')]

#Sort ID column alphabetically
mvp3.sort_values(by=['id'], ascending = True)

#Sort ID column alphabetically, remove index on left side. Create a CSV for backup. 
#mvp3.sort_values(by=['id'], ascending = True).to_csv('prisma_child_cloud_accounts_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False) 

#get list of account groups
pc_settings, response_package = pc_lib_api.api_accounts_groups_list_get(pc_settings)
account_group_list = response_package['data']

#put json inside a dataframe
pmvp = pandas.json_normalize(account_group_list) 

#filter for column called "name" in dataframe
#another filter option -->mvp1 = mvp.drop(columns=['name','cloudType','parentAccountName'])
pmvp1 = pmvp.filter(['name'])

#filter for lines that contain a specific string
pmvp2 = pmvp1[pmvp1['name'].str.contains('sab-')]

#Filter out rows which contain certain strings, add your own items below, this is useful for bulk upload purposes and/or cron jobs. "~" symbol filters out.
pmvp3 = pmvp2[~pmvp2['name'].str.contains('sbx | sandbox | test | retrieveseatmap01 | playground | your_GCP_main_account_ID')]

#Rename "name" column to "id"
pmvp3.rename(columns={'name': 'id'}, inplace=True)

#Sort "ID" column alphabetically
pmvp3.sort_values(by=['id'], ascending = True)

#Sort "ID" column alphabetically, remove index on left side. Create a CSV for backup. 
#pmvp3.sort_values(by=['id'], ascending = True).to_csv('old_account_group_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False) 

#Make a newly prepared dataframe by combining both dataframes and drop all duplicates
pmvp3_mvp3 = pandas.concat([pmvp3,mvp3]).drop_duplicates(keep=False)

#Sort "ID" column alphabetically, remove index on left side. Create a CSV for backup. 
pmvp3_mvp3.sort_values(by=['id'], ascending = True)

#Sort "ID" column alphabetically, remove index on left side. Create a CSV for backup. 
#pmvp3_mvp3.sort_values(by=['id'], ascending = True).to_csv('new_combined_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False) 

#add counter
account_groups_added_count = 0
account_groups_skipped_count = 0
account_groups_duplicate_count = 0

#to_dict uses the pandas dataframe and turns it into a dictionary. Orient Records=do it by row (and not columns) 
pmvp4_mvp4 = pmvp3_mvp3.to_dict(orient="records")

#creates a dictionary inside a blank list. Each row in the dataframe needs to be a dicitonary. Loop through each row and turn it into dictionary. 
accounts_groups_to_import = []

#iterate through all rows in dictionary
for row_dict in pmvp4_mvp4:
    #Check for duplicates in the imported CSV
    account_group_exists = False
    for account_group_duplicate_check in accounts_groups_to_import:
        if account_group_duplicate_check['id'].lower() == row_dict['id'].lower():
            account_groups_duplicate_count = account_groups_duplicate_count + 1
            account_group_exists = True
            break
    if not account_group_exists:
        # Check for duplicates already in the Prisma Cloud Account
        for account_group_old in account_group_list:
            if row_dict['id'].lower() == account_group_old['name'].lower():
                account_groups_skipped_count = account_groups_skipped_count + 1
                account_group_exists = True
                break
        if not account_group_exists:
            temp_accounts_group = {}
            temp_accounts_group['accountIds'] = [row_dict['id']]
            temp_accounts_group['description'] = 'GCP Project Mapped to Account Group'
            temp_accounts_group['name'] = row_dict['id']
            account_groups_added_count = account_groups_added_count + 1
			#each temp account group row will look like ---> {'accountIds': ['automationxx-tooling-xxxx'], 'name': 'automationxx-tooling-xxx'}
	
	#append each new dictionary to the master array (user_roles_to_import)
            accounts_groups_to_import.append(temp_accounts_group)
	
print(accounts_groups_to_import)
#the master array should look like this---->[{'accountIds': ['autx-tooling-xxxx'], 'name': 'autx-tooling-xxxx'}, {'accountIds': ['crewx-max-gen-xxxx'], 'name': 'crewx-max-gen-xxxx'}, {'accountIds': ['egressgatexxx-xxxx'], 'name': 'gateway-xxxx'}]
print('Done.')

#for each dictionary in the master array, send one row at a time to pc_lib_api. 
#for example, send first---->{'accountIds': ['automationxx-tooling-xx'], 'name': 'automationxx-tooling-xx'}
#this imports each group one at a time. 
for new_accounts_group in accounts_groups_to_import:
    print('Adding account name: ' + new_accounts_group['name'])
    print(new_accounts_group['accountIds'])
	#comment out the line below if you don't want this script to post changes to Prisma Cloud.
    pc_settings, response_package = pc_lib_api.api_accounts_groups_add(pc_settings, new_accounts_group)

#print final counts
print('Account groups to add: ' + str(account_groups_added_count))
print('Account groups (Duplicates): ' + str(account_groups_skipped_count))
print('Account groups removed as duplicates from datafame: ' + str(account_groups_duplicate_count))
print('Import Complete.')

#if receive status code 200, group imported correctly. 

#if receive Status Error 400: three reasons you might get this error:
# (1) This exact cloud account group/role already exists. Most likely this is why getting Error 400. 
# (2) The formatting of is incorrect. This was initial error, had to make accountIds an array of strings to meet api requirements. 
# (3) Use the API try out tool on the Prisma API website to get an example of syntax it expects (brackets, no brackets etc.)
