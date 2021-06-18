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
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

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
config_search['id'] = '2aaa539a-e028-400c-ba87-2152a06d79c7'
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

#turn into a string type dvalue.
pu['roles'] = pu['roles'].apply(str).str.replace('.', ',')

#within the "roles" column, find a role(s) with a specific string and keep only those in the list. 
pu2 = pu[pu['roles'].str.contains('Sabre-')]

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
gcp2 = gcp1[~gcp1['accountId'].str.contains('sab-ssvcs-gold-images-c3d9|66278518872|retrieveseatmap01')]

#within "accountID" column, pull in only rows which contain a specfic string
gcp3 = gcp2[gcp2['accountId'].str.contains('sab-')]

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

# now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")
# gcp4.to_csv('gcp_sample_user_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 

#Sorting Values
gcp4.sort_values(by=['id', 'roleIds', 'accountId'], ascending = True, inplace=True)

#Group by accountID aka GCP project name. Tie in the associated IDs (name of users) and RoleIds (tied to role)
gcp5 = gcp4.groupby('accountId')[['id', 'roleIds']].agg(list).reset_index()
# gcp5.drop_duplicates('roleIDs',keep=False)

#copy the roleIDs column
gcp5['RoleId_'] = gcp5['roleIds'].copy()

#after the copy the column will be classified as a "dtype: float64". We will need to convert the column to am object (string) before we have do any additional procedures (in our case we want to delete duplicate roleIDs listed on each row).
gcp5['RoleId_'] = gcp5['RoleId_'].astype(str)

#since account IDs are lets say 36 characters, using a "2" will allow the program to skip a bracket and apostrophe. This will then grab the ID and end on the 38th position, right before the closing apostrophe.
gcp5['RoleId_'] = gcp5['RoleId_'].str[2:38]

#RoleIds column is no longer needed and has been replaced with a column which started out as a copy, removing all the duplicate RoleIDs
gcp5.drop(columns=['roleIds'], inplace=True)

#grab time now
now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")

#Save Dataframe to CSV
gcp5.to_csv('prisma_roles_and_associated_users_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 






