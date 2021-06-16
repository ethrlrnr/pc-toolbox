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

print('API - Getting current account groups list...', end='')
pc_settings, response_package = pc_lib_api.api_accounts_groups_list_get(pc_settings)
account_groups_list_names = response_package['data']
print('Done.')

#current date and time
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

#put json inside a dataframe
mvp = pandas.json_normalize(account_groups_list_names) 

#filter for columns "id" and "name"
#another filter option -->mvp1 = mvp.drop(columns=['name','cloudType','parentAccountName'])
mvp1 = mvp.filter(['id', 'name'])

#Sort name column alphabetically
mvp1.sort_values(by=['name'], ascending = True)

#Sort name column alphabetically, remove index on left side and output to CSV (if you want to test output)
#mvp1.sort_values(by=['name'], ascending = True).to_csv('prisma_account_groups_list_names_{}.csv'.format(now), sep=',', encoding='utf-8', index=False) 

print('API - Getting user roles list...', end='')
pc_settings, response_package = pc_lib_api.api_user_role_list_get(pc_settings)
user_role_list = response_package['data']

#put json inside a dataframe
pmvp = pandas.json_normalize(user_role_list) 

#Filter for the "name" column.
pmvp1 = pmvp.filter(['name'])

#Sort name column alphabetically
pmvp1.sort_values(by=['name'], ascending = True)

#Sort name column alphabetically, remove index on left side and output to CSV (if you want to test output) 
#pmvp1.sort_values(by=['name'], ascending = True).to_csv('old_user_role_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False) 

#merge both dataframes and focus on the name column. Dataframes should have the same column names before joining. All dupes are dropped.
pmvp1_mvp1 = pandas.concat([pmvp1,mvp1]).drop_duplicates(subset=['name'], keep=False)

#drop rows with empty cells
pmvp1_mvp1 = pmvp1_mvp1.dropna()

#within "name" column, pull in only rows which contain a specfic string. I added company name to my roles list to distinguish security/audit members vs. developers, example "company-systemadmin".
pmvp1_mvp2 = pmvp1_mvp1[pmvp1_mvp1['name'].str.contains('company-')]

#within "name" exclude rows which feature a specific string
pmvp1_mvp3 = pmvp1_mvp2[~pmvp1_mvp2['name'].str.contains('sbx')]

#Sort name column alphabetically
pmvp1_mvp3.sort_values(by=['name'], ascending = True)

#Sort name column alphabetically, remove index on left side and output to CSV (if you want to test output) 
#pmvp1_mvp3.sort_values(by=['name'], ascending = True).to_csv('new_combined_role_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False) 

#to_dict uses the pandas dataframe and turns it into a dictionary. Orient Records=do it by row (and not columns) 
pmvp1_mvp4 = pmvp1_mvp3.to_dict(orient="records")

#Add counter
user_roles_added_count = 0
user_roles_skipped_count = 0
user_roles_duplicate_count = 0

#creates a dictionary inside a blank list. Each row in the dataframe needs to be a dicitonary. Loop through each row and turn it into dictionary. 
user_roles_to_import = []

#iterate through all rows in dictionary
for row_dict in pmvp1_mvp4:
    #Check for duplicates in the dataframe converted to a dictionary
    user_roles_exist = False
    for user_roles_duplicate_check in user_roles_to_import:
        if user_roles_duplicate_check['name'].lower() == row_dict['name'].lower():
            user_roles_duplicate_count = user_roles_duplicate_count + 1
            user_roles_exist = True
            break
    if not user_roles_exist:
        # Check for duplicates already in the Prisma Cloud Account
        for user_roles_old in user_role_list:
            if row_dict['name'].lower() == user_roles_old['name'].lower():
                user_roles_skipped_count = user_roles_skipped_count + 1
                user_roles_exist = True
                break
        if not user_roles_exist:
            temp_user_roles = {}
            temp_user_roles['accountGroupIds'] = [row_dict['id']]
            temp_user_roles['name'] = row_dict['name']
            temp_user_roles['description'] = 'Role Mapped to GCP Project'
            temp_user_roles['roleType'] = 'Account Group Read Only'
            #each temp user roles row will look like ---> {'accountGroupIds': ['364cade7-715b-4976-8eff-xxxxxxx'], 'name': 'tab-iac-xxxxx', 'description': 'Role Mapped to Something', 'roleType': 'Account Group Read Only'}
            user_roles_added_count = user_roles_added_count + 1
	#append each new dictionary to the master array (user_roles_to_import)
            user_roles_to_import.append(temp_user_roles)
	
print(user_roles_to_import)
#the master array should look like this---->[{'accountGroupIds': ['364cade7-715b-4976-8eff-xxxxxxx'], 'name': 'tab-iac-xxxxx', 'description': 'Role Mapped to Something', 'roleType': 'Account Group Read Only'}, {'accountGroupIds': ['364cade7-715b-4976-8eff-xxxxxxx'], 'name': 'tab-iac-xxxxx', 'description': 'Role Mapped to Something', 'roleType': 'Account Group Read Only'}]

print('Done.')

#for each dictionary in the master array, send one row at a time to pc_lib_api. 
#for example, send first---->{'accountGroupIds': ['364cade7-715b-4976-8eff-xxxxxxx'], 'name': 'tab-iac-xxxxx', 'description': 'Role Mapped to Something', 'roleType': 'Account Group Read Only'}
#this imports each role one at a time. 
for user_role_to_add in user_roles_to_import:
    print('Adding user role: ' + user_role_to_add['name'])
    print(user_role_to_add['accountGroupIds'])
    print(user_role_to_add['description'])
    print(user_role_to_add['roleType'])
	#comment out the line below if you don't want this script to post changes to Prisma Cloud.
    pc_settings, response_package = pc_lib_api.api_user_role_add(pc_settings, user_role_to_add)

#print final counts 
print('User roles to add: ' + str(user_roles_added_count))
print('User roles skipped (Duplicates): ' + str(user_roles_skipped_count))
print('User roles removed as duplicates from CSV: ' + str(user_roles_duplicate_count))
print('Import Complete.')

#if receive status code 200, group imported correctly. 

#if receive Status Error 400: three reasons you might get this error:
# (1) This exact cloud account group/role already exists. Most likely this is why getting Error 400. 
# (2) The formatting of is incorrect. This was initial error, had to make accountIds an array of strings to meet api requirements. 
# (3) Use the API try out tool on the Prisma API website to get an example of syntax it expects (brackets, no brackets etc.)


print('Final Stage. The following code will go back into user roles and delete user roles. Specifically, user roles that are no longer attached to a account group (recently off-boarded GCP project etc.')

pc_settings, response_package = pc_lib_api.api_user_role_list_get(pc_settings)
user_role_list1 = response_package['data']
print('Done.')


# Get the current date/time
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

# Put json inside a dataframe
ppu = pandas.json_normalize(user_role_list1)

# Query a specific column (description in this case) and match on a string
mmvp = ppu.query('description == "Role Mapped to GCP Project"')

# Once all items are matched above, filter out all remaining columns except ID and Name. 
mmvp1 = mmvp.filter(['id', 'name', 'accountGroupIds'])

# Filter for rows that show an empty account group ID associated with the role. This will pull rows with account groups that were deleted (now showing as empty).
mmvp2 = mmvp1[mmvp1['accountGroupIds'].str.len() == 0]

# Drop the column accountGroupIds since it's no longer needed after our filter operation. 
mmvp2.drop(columns=['accountGroupIds'], inplace=True)



# print('Saving JSON contents as a CSV...', end='')
#mvp2.sort_values(by=['id'], ascending = True).to_csv('prisma_user_role_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False)
# print('Done.')

mmvp3 = mmvp2.to_dict('records')

#print(mvp4)

user_role_remove = []
for row_dict1 in mmvp3:
    temp_UR = {}
	#row_dict values pull from the dictionary
    temp_UR['id']= row_dict1['id']
    user_role_remove.append(temp_UR)
				
print(user_role_remove)

for user_role_to_delete in user_role_remove:
    print('user role ID: ',user_role_to_delete['id'])
    pc_settings, response_package = pc_lib_api.api_delete_user_role(pc_settings, user_role_to_delete)
print('Done.')
