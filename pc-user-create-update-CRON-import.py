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

#########NOTE IF YOU ARE USING THIS CODE TO PIPE IN LARGE AMOUNTS OF GCP USERS INTO PRISMA. ENSURE SSO IS SETUP ON PRISMA AND HOOKED TO THE APPROPIATE AD GROUP####################

args = parser.parse_args()
# --End parse command line arguments-- #

# --Main-- #
# Get login details worked out.
print('Stage 1 - API Response 1 - [Call Function]  Login')
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl)
print('Done.')
#---------------------------------------------------------------------------------------------------------------#
# Sort out API Login.
print('Stage 2 - API Response 2 - [Call Function] Getting authentication token...', end='')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 3 - Sorting and building the filters (JSON package) to plug into the API on Stage 3.')
config_search = {}

#Using the API documentation,nesting filters requires knowledge whether the element is something like an object, string, array of strings.  Objects require "{}" before you can flow down to the next value. See code below as an example.
config_search['filter'] = {}
config_search['filter']['timeRange'] = {}
config_search['filter']['timeRange']['type'] = "relative"
config_search['filter']['timeRange']['value'] = {}
config_search['filter']['timeRange']['value']['unit'] = "day"
config_search['filter']['timeRange']['value']['amount'] = 31
config_search['id'] = 'YOUR_SAVED_SEARCH_ID_CREATED_IN_UI'  #example '434343434334434544'
config_search['withResourceJson'] = True

#The RQL for your saved search which is leveraged as an ID above should look something like this: config from cloud.resource where cloud.type = 'gcp' AND api.name = 'gcloud-projects-get-iam-user' AND json.rule = user contains @domain.com and user does not contain gcp and user does not contain test
print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 4 - API Response 3 - [Call Function] Post to Prisma, plugging in a "saved search" id (aka saved RQL search from investigation tab on UI), this will allow data to be returned showing GCP users and their respective GCP project(s). Prisma ingests the Google Resource Manager API to accomplish this.', end='')
pc_settings, response_package = pc_lib_api.api_search_config(pc_settings, data=config_search)
gcp_list = response_package['data']
print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 5 - API Response 4 - Getting current user list on Prisma Cloud to compare against (new users vs existing users).', end='')
pc_settings, response_package = pc_lib_api.api_user_list_get(pc_settings)

#"data" is the name of the main key in the JSON response package. Critical to know. 
user_list_get = response_package['data']

#put json inside a dataframe.
pu = pandas.json_normalize(user_list_get)

#---------------------------------------------------------------------------------------------------------------#
#lets quickly copy the "pu" dataframe before operations are carried out against it. We want to use this copy for a second list comparison of users that should not be created. We also have logic in the code below that will skip a user if they exist in the database and import list.
wu = pu.copy()
#turn into a string type dvalue.
wu['lastName'] = pu['lastName'].apply(str).str.replace('.', ',')

#within the "lastName" column, find a last name with a specific string and keep only those in the list. 
wu2 = wu[wu['lastName'].str.contains('GCP')]

#filter out the columns and only focus on the "email" column. With the other GCP user list, we can compare against emails. 
wu3 = wu2.filter(['email'])

#for the column "email" in the dataframe, make it into a list that we will compare against below.
existing_gcp_users_already_in_prisma = wu3['email'].to_list()
#---------------------------------------------------------------------------------------------------------------#

#turn into a string type dvalue.
pu['roles'] = pu['roles'].apply(str).str.replace('.', ',')

#within the "roles" column, find a role(s) with a specific string and keep only those in the list. I used this to filter for a role string name included for members of Security (role name: company-systemadmin)
pu2 = pu[pu['roles'].str.contains('company-')]

#filter out the columns and only focus on the "email" column. 
pu3 = pu2.filter(['email'])

#for the column "email" in the dataframe, make it into a list that we will compare against below.
security_cloud_team_list = pu3['email'].to_list()

#lets print how many Prisma Cloud user accounts exist. 
print(len(security_cloud_team_list), 'Total user account(s) on Prisma Cloud list')

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 6 - Begin prepping the GCP list of users.')

# # Put json inside a dataframe. Go 1 level down on the JSON (data --> items). If not the dataframe gets ruined. 
gcp = pandas.json_normalize(gcp_list['data']['items'])

#focus on columns "id" aka email and "accountID" aka project names.
gcp1 = gcp.filter(['id', 'accountId'])

#sort "id" by email addresses.
gcp1.sort_values(by=['id'], ascending = True, inplace=True)

#dump rows which contain a specific string.
gcp2 = gcp1[~gcp1['accountId'].str.contains('sbx|sandbox|test|YOUR_GCP_ACCOUNT_ID|playground')]

#within "accountID" column, pull in only rows which contain a specfic string. Add a company name to existing role names for just members for team to filter easier (example of role name, company-systemadmin).
gcp3 = gcp2[gcp2['accountId'].str.contains('company-')]

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 7 - API Response 5 - [Call Function] Getting current user role on Prisma Cloud. Add roleIDs to existing GCP dataframe after mapping exercise (match on project name then pull in RoleID).', end='')
pc_settings, response_package = pc_lib_api.api_user_role_list_get(pc_settings)
user_role_list = response_package['data']

#put json inside a dataframe. 
normalize_user = pandas.json_normalize(user_role_list)
print('Done.')

#To append roleIds (from our user roles API response) to a dataframe, two dataframes must match on column values. If match is found during compare, the role ID gets added to that row.  
gcp3['roleIds'] = gcp3['accountId'].map(normalize_user.set_index('name')['id'])

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 8 - Compare GCP user list against existing Prisma Users that are members of Security or Cloud Engineering with elevated roles. Remove members from GCP list if found. Finish GCP dataframe prep work.')
#check prepared GCP dataframe against the existing list of emails for Security & Cloud team assisting with Prisma. If email match is found remove user from GCP list since it will impact existing permissions (will lessen permissions and tie users to a specific project, impacting their audit ability). Just to note but if you wanted to keep matches and drop everything that wasn't a match (aka duplicate) then just remove the "~" from the "isin" code below. 
gcp4 = gcp3[~gcp3.id.isin(security_cloud_team_list)]

#check prepared GCP dataframe against the existing list of emails for GCP users already created in Prisma Cloud. If email match is found remove user from GCP list since they don't need to be created. 
gcp5 = gcp4[~gcp4.id.isin(existing_gcp_users_already_in_prisma)]

#Lets drop the  "accountId" column since it's no longer needed for creating a user profile or updating one. We used accountID above for our mapping existing above which pulled in the RoleID from the User Role API response.
gcp5.drop(columns=['accountId'], inplace=True)

#RoleIDs must be sorted on this dataframe (GCP users) and it's comparison dataframe (existing users). If the same Ids exist on both sides but not in order then an update is made. This helps prevent that.
gcp5.sort_values(by=['id', 'roleIds'], ascending = True, inplace=True)

#The dataframe will most likely list users multiple times in different rows. This code will group all data by a common value into a single row. Resetting the index will re-add any columns initially lost in the operation (applying the list). More columns can be specified after "roleIds" by just adding a comma. Once this work is complete, going to add 2 new columns to this dataframe (firstName and defaultRoleId). Less messy this way. 
gcp6 = gcp5.groupby('id')['roleIds'].apply(list).reset_index()

#Parsing a name from an email, this drops all text at @ and after it.
gcp6['firstName']= gcp6.id.str.extract("(.*)@")

#strip a specific part of a string
gcp6['firstName'] = gcp6['firstName'].str.replace('.ctr', '')

#replace dots with a space, first.last = first last
gcp6['firstName'] = gcp6['firstName'].str.replace('.', ' ')

#posting of a new user profile requires a default role ID which must be part of the Role IDs array list. To begin work on extract an ID from the list, lets first make a copy of the column and push these values new column "defaultRoleId" in our existing dataframe. 
gcp6['defaultRoleId'] = gcp6['roleIds'].copy()

#after the copy the column will be classified as a "dtype: float64". We will need to convert the column to am object (string) before we have do any additional procedures (avoid NaN results).
gcp6['defaultRoleId'] = gcp6['defaultRoleId'].astype(str)

#since account IDs are lets say 36 characters, using a "2" will allow the program to skip a bracket and apostrophe. This will then grab the ID and end on the 38th position, right before the closing apostrophe.
gcp6['defaultRoleId'] = gcp6['defaultRoleId'].str[2:38]

#test prepped GCP list for new users to be created.
#print(gcp5)

#Grab the current date/time.
# now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")
# gcp6.to_csv('gcp_sample_user_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 9 - Turn prepped GCP user list dataframe into a dictionary and iterate through it.')
#turn prepared dataframe to a dictionary. If you try to iterate against a pure dataframe such as gcp5, errors will pop up around integer use etc. 
gcp7 = gcp6.to_dict('records')
#print(gcp6)

#To test a REAL small sample size of users before doing live with the JSON/dataframe CRON approach, uncomment the line above for "gcp_sample_user_list_{}.csv", once it downloads locally, mod the amount of users you wish to test against. Save it, then run this CSV against the User_Role_CRON_test.py. CLI will look something like: python User_Role_CRON_test.py name_of_your_csv_file.csv

#Remember commenting out the code below will prevent users from actually being created in Prisma Cloud: "pc_settings, response_package = pc_lib_api.api_user_add_v2(pc_settings, user_to_add_v2)"

print('Done.')
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

for row_dict in gcp7:
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
            if row_dict['id'].lower() == user_old['email'].lower():
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
print('User create operation complete. We will now check whether existing Prisma Cloud users need their roles/gcp projects updated. This is for GCP users only, this skips users with audit permission abilities across the GCP cloud.')

#---------------------------------------------------------------------------------------------------------------#

#df.dtypes

#---------------------------------------------------------------------------------------------------------------#
print('Stage 14 - Sorting and building the filters (JSON package) to plug into the API on Stage 3.')
cconfig_search = {}

#Using the API documentation,nesting filters requires knowledge whether the element is something like an object, string, array of strings.  Objects require "{}" before you can flow down to the next value. See code below as an example.
cconfig_search['filter'] = {}
cconfig_search['filter']['timeRange'] = {}
cconfig_search['filter']['timeRange']['type'] = "relative"
cconfig_search['filter']['timeRange']['value'] = {}
cconfig_search['filter']['timeRange']['value']['unit'] = "day"
cconfig_search['filter']['timeRange']['value']['amount'] = 31
cconfig_search['id'] = 'YOUR_SAVED_SEARCH_ID_CREATED_IN_UI'  #example: '434343434334434544', use the same search ID as above.
cconfig_search['withResourceJson'] = True

#The RQL for your saved search which is leveraged as an ID above should look something like this: config from cloud.resource where cloud.type = 'gcp' AND api.name = 'gcloud-projects-get-iam-user' AND json.rule = user contains @domain.com and user does not contain gcp and user does not contain test
print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 15 - API Response 3 - [Call Function] Post to Prisma, plugging in a "saved search" id (aka saved RQL search from investigation tab on UI), this will allow data to be returned showing GCP users and their respective GCP project(s). Prisma ingests the Google Resource Manager API to accomplish this.', end='')
pc_settings, response_package = pc_lib_api.api_search_config(pc_settings, data=cconfig_search)
ggcp_list = response_package['data']
print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 16 - API Response 4 - Getting current user list on Prisma Cloud to compare against (new users vs existing users).', end='')
pc_settings, response_package = pc_lib_api.api_user_list_get(pc_settings)

#"data" is the name of the main key in the JSON response package. Critical to know. 
uuser_list_get = response_package['data']

#put json inside a dataframe.
ppu = pandas.json_normalize(uuser_list_get)

#---------------------------------------------------------------------------------------------------------------#
#lets quickly copy the "pu" dataframe before operations are carried out against it. We want to use this copy for a second list comparison of users that should be updated. We also have logic in the code below that will remove a GCP user if they don't exist in the Prisma Cloud database (GCP user list dataframe prepping phase). We also have a 2nd check in place, that will skip the user if not found in the Prisma database (during creation time, useful if check 1 fails which it should never do).
wwu = ppu.copy()

#turn into a string type dvalue. Remember to follow this method when using "apply", using the column name on both sides. If a column names is only specified on the right, we lose all the other columns.  
wwu['lastName'] = ppu['lastName'].apply(str).str.replace('.', ',')

#within the "lastName" column, find a last name with a specific string and keep only those in the list. 
wwu2 = wwu[wwu['lastName'].str.contains('GCP')]

#filter out the columns and only focus on the "email" column. With the other GCP user list, we can compare against emails. 
wwu3 = wwu2.filter(['email', 'roleIds'])

#we must sort the roleIds array/list in order on both the existing users in Prisma check (this line of code) and also the GCP users list(further down in the code). If both dataframes contain the same Ids but not in the same order, it will be identified as "different" and an update will be made. 
wwu3['roleIds'] = wwu3['roleIds'].apply(sorted)

#for the column "email" in the dataframe, make it into a list that we will compare against below.
eexisting_gcp_users_already_in_prisma = wwu3['email'].to_list()

#---------------------------------------------------------------------------------------------------------------#

#turn into a string type dvalue.
ppu['roles'] = ppu['roles'].apply(str).str.replace('.', ',')

#within the "roles" column, find a role(s) with a specific string and keep only those in the list. 
ppu2 = ppu[ppu['roles'].str.contains('Sabre-')]

#filter out the columns and only focus on the "email" column. 
ppu3 = ppu2.filter(['email'])

#for the column "email" in the dataframe, make it into a list that we will compare against below.
ssecurity_cloud_team_list = ppu3['email'].to_list()

#lets print how many Prisma Cloud user accounts exist. 
print(len(ssecurity_cloud_team_list), 'Total user account(s) on Prisma Cloud list')

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 17 - Begin prepping the GCP list of users.')

# # Put json inside a dataframe. Go 1 level down on the JSON (data --> items). If not the dataframe gets ruined. 
ggcp = pandas.json_normalize(ggcp_list['data']['items'])

#focus on columns "id" aka email and "accountID" aka project names.
ggcp1 = ggcp.filter(['id', 'accountId'])

#sort "id" by email addresses.
ggcp1.sort_values(by=['id'], ascending = True, inplace=True)

#dump rows which contain a specific string.
ggcp2 = ggcp1[~ggcp1['accountId'].str.contains('sbx|sandbox|test|YOUR_GCP_ACCOUNT_ID|playground')]

#within "accountID" column, pull in only rows which contain a specfic string. Something that can easily identify your existing team for roles (example role name, "company-systemadmin").
ggcp3 = ggcp2[ggcp2['accountId'].str.contains('company-')]

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 18 - API Response 5 - [Call Function] Getting current user role on Prisma Cloud. Add roleIDs to existing GCP dataframe after mapping exercise (match on project name then pull in RoleID).', end='')
pc_settings, response_package = pc_lib_api.api_user_role_list_get(pc_settings)
uuser_role_list = response_package['data']

#put json inside a dataframe. 
nnormalize_user = pandas.json_normalize(user_role_list)
print('Done.')

#To append roleIds (from our user roles API response) to a dataframe, two dataframes must match values in a column. If match is found during compare, the role ID gets added to that row.  
ggcp3['roleIds'] = ggcp3['accountId'].map(nnormalize_user.set_index('name')['id'])

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 19 - Compare GCP user list against existing Prisma Users that are members of Security or Cloud Engineering with elevated roles. Remove members from GCP list if found. Finish GCP dataframe prep work.')
#check prepared GCP dataframe against the existing list of emails for Security & Cloud team assisting with Prisma. If email match is found remove user from GCP list since it will impact existing permissions (will lessen permissions and tie users to a specific project, impacting their audit ability). Just to note but if you wanted to keep matches and drop everything that wasn't a match (aka duplicate) then just remove the "~" from the "isin" code below. 
ggcp4 = ggcp3[~ggcp3.id.isin(ssecurity_cloud_team_list)]

#check prepared GCP dataframe against the existing list of emails for GCP users already created in Prisma Cloud. If email match is found on both lists, KEEP those GCP users and drop any users from the GCP list not already in Prisma. This is a profile UPDATE operation. 
ggcp5 = ggcp4[ggcp4.id.isin(eexisting_gcp_users_already_in_prisma)]

#Lets drop the  "accountId" column since it's no longer needed for creating a user profile or updating one. We used accountID above for our mapping existing above which pulled in the RoleID from the User Role API response.
ggcp5.drop(columns=['accountId'], inplace=True)

#RoleIDs must be sorted on this dataframe (GCP users) and it's comparison dataframe (existing users). If the same Ids exist on both sides but not in order then an update is made. This helps prevent that.
ggcp5.sort_values(by=['id', 'roleIds'], ascending = True, inplace=True)

#The dataframe will most likely list users multiple times in different rows. This code will group all data by a common value into a single row. Resetting the index will re-add any columns initially lost in the operation (applying the list). More columns can be specified after "roleIds" by just adding a comma. Once this work is complete, going to add 2 new columns to this dataframe (firstName and defaultRoleId). Less messy this way. 
ggcp6 = ggcp5.groupby('id')['roleIds'].apply(list).reset_index()

#Parsing a name from an email, this drops all text at @ and after it.
ggcp6['firstName']= ggcp6.id.str.extract("(.*)@")

#strip a specific part of a string
ggcp6['firstName'] = ggcp6['firstName'].str.replace('.ctr', '')

#replace dots with a space, first.last = first last
ggcp6['firstName'] = ggcp6['firstName'].str.replace('.', ' ')

#updating of a new user profile requires a default role ID which must be part of the Role IDs array list. To begin work on extract an ID from the list, lets first make a copy of the column and push these values new column "defaultRoleId" in our existing dataframe. 
ggcp6['defaultRoleId'] = ggcp6['roleIds'].copy()

#after the copy the column will be classified as a "dtype: float64". We will need to convert the column to an object (string) before we have do any additional procedures (avoid NaN results).
ggcp6['defaultRoleId'] = ggcp6['defaultRoleId'].astype(str)

#since account IDs are lets say 36 characters, using a "2" will allow the program to skip the first 2 characters (in our case, a bracket and apostrophe). This will then grab the ID and end on the 38th position, right before the closing apostrophe.
ggcp6['defaultRoleId'] = ggcp6['defaultRoleId'].str[2:38]

#Lets append the RoleIds column from the "existing users" dataframe into this "GCP users" dataframe which also has a RoleIds column. We will do a compare next.
ggcp6['roleIdsExistingInPrismaCompare'] = ggcp6['id'].map(wwu3.set_index('email')['roleIds'])

#Lets compare the sorted RoleIds from the two dataframes (existing users and GCP users). If a match is found, drop the user from the update list (prepped dataframe).
ggcp7 = ggcp6.query("roleIds != roleIdsExistingInPrismaCompare")

#Lets drop the roleIdsExistingInPrismaCompare column, now that the comparison is done between role IDs. We want the GCP roleIDs (which map to projects) to be the source of truth and not what's already in Prisma.
ggcp7.drop(columns=['roleIdsExistingInPrismaCompare'], inplace=True)


#Grab the current date/time.
# now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")
# ggcp7.to_csv('gcp_sample_user_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 20 - Turn prepped GCP user list dataframe into a dictionary and iterate through it.')
#turn prepared dataframe to a dictionary. If you try to iterate against a pure dataframe such as gcp5, errors will pop up around integer use etc. 
ggcp8 = ggcp7.to_dict('records')
print(ggcp8)

#To test a REAL small sample size of users before doing live with the JSON/dataframe CRON approach, uncomment the line above for "gcp_sample_user_list_{}.csv", once it downloads locally, mod the amount of users you wish to test against. Save it, then run this CSV against the User_Role_CRON_test.py. CLI will look something like: python User_Role_CRON_test.py name_of_your_csv_file.csv

#Remember commenting out the code below will prevent users from actually being created in Prisma Cloud: "pc_settings, response_package = pc_lib_api.api_user_add_v2(pc_settings, user_to_update_v2)"

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 21 - Add counter for new users added, users skipped and duplicate users.')
#Add counter
uuser_added_count = 0
uuser_skipped_count = 0
uuser_duplicate_count = 0

print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 22 - Sorting and building the filters (JSON package) to plug into the API upon completion (building user profiles).')
#creates a dictionary inside a blank list. Each row in the dataframe needs to be a dicitonary. Loop through each row and turn it into dictionary. 
uuser_to_import = []
uuser_match_count = 0
for rrow_dict in ggcp8:
    print('id: users to update: ',rrow_dict['id'])	
    #Check for duplicates in the dataframe converted to a dictionary
    uuser_exist = False
    for uuser_match_check in uuser_to_import:
        if uuser_match_check['email'] == rrow_dict['id']:
            uuser_match_count = uuser_match_count + 1
            uuser_exist = True
            break
    if not uuser_exist:
        # Check for duplicates already in the Prisma Cloud Account
        for uuser_old in uuser_list_get:
            if rrow_dict['id'].lower() != uuser_old['email'].lower():
                uuser_skipped_count = uuser_skipped_count + 1
                uuser_exist = False
            else:
                uuser_exist = True
                #print(we found one!', user_old['email'].lower())
            if uuser_exist:
                ttemp_user = {}
	#row_dict values pull from the dictionary
                ttemp_user['roleIds']= rrow_dict['roleIds']
                ttemp_user['email'] = rrow_dict['id']
                ttemp_user['firstName'] = rrow_dict['firstName']
                ttemp_user['lastName'] = '[GCP]'
                ttemp_user['timeZone'] = 'America/Chicago'
                ttemp_user['accessKeysAllowed'] = 'true'
                ttemp_user['defaultRoleId'] = rrow_dict['defaultRoleId']
                uuser_added_count = uuser_added_count + 1
	#append each new dictionary to the master array (user_to_import)
                uuser_to_import.append(ttemp_user)

#lets print all the users that will be updated, syntax should align with what's specific on the API documentation for creating a new user profile. They give samples of expected response on website (this is pasted two lines down). Use Postman tool to test at least 1 user creation using cURL then post command.  	
print(uuser_to_import)
#Expected syntax for filters:
#'{"roleIds":["8989898989-90989889-9898989898","8989898989-90989889-9898989898","8989898989-90989889-9898989898"],"email":"first.last@domain.com","firstName":"bob","lastName":"smith","timeZone":"America/Chicago","defaultRoleId":"8989898989-90989889-9898989898"}'
print('Done.')
#---------------------------------------------------------------------------------------------------------------#
print('Stage 23 - Plugging in filter criteria into the API via a post. Importing users one at a time. Will print for each user.')

for user_to_update_v2 in uuser_to_import:
    print('User Email: ',user_to_update_v2['email'])
    print('First Name: ',user_to_update_v2['firstName'])
    print('Last Name: ',user_to_update_v2['lastName'])
    print('Time Zone: ',user_to_update_v2['timeZone'])
    print('Access Key: ',user_to_update_v2['accessKeysAllowed'])
    print('Role IDs: ',user_to_update_v2['roleIds'])
    print('Default Role ID: ',user_to_update_v2['defaultRoleId'])
    
	# #comment out the line below if you don't want this script to post changes to Prisma Cloud.
    pc_settings, response_package = pc_lib_api.api_user_update_v2(pc_settings, user_to_update_v2)
#---------------------------------------------------------------------------------------------------------------#
print('Stage 24 - Final user counts.')
print('Users to update: ' + str(uuser_added_count))
print('Users removed as duplicates from dataframe: ' + str(uuser_match_count))
print('Operation Complete.')
#---------------------------------------------------------------------------------------------------------------#
#df.dtypes





