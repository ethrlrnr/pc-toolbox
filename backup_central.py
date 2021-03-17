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
print('Logging into account')
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl)

# Sort out API Login
print('Getting authentication token...')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')

#------------------------------------>
print('Backing up access key list')

pc_settings, response_package = pc_lib_api.api_access_key_list_get(pc_settings)
access_key_list_get = response_package['data']

now = datetime.now().strftime("%m_%d_%Y-%I_%M_%p")
access_key_list = pandas.json_normalize(access_key_list_get) #access_key_listt json inside a dataframe
access_key_list['lastUsedTime']=(pandas.to_datetime(access_key_list['lastUsedTime'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
access_key_list['createdTs']=(pandas.to_datetime(access_key_list['createdTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
access_key_list['expiresOn']=(pandas.to_datetime(access_key_list['expiresOn'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

access_key_list.to_csv('access_key_list_get_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')

#------------------------------------>

print('Backing up account groups')
pc_settings, response_package = pc_lib_api.api_accounts_groups_list_get(pc_settings)
accounts_groups_list = response_package['data']

accounts_groups = pandas.json_normalize(accounts_groups_list) 

#Change specific column from Unix time to central. Can be changed to any time zone.
accounts_groups['lastModifiedTs']=(pandas.to_datetime(accounts_groups['lastModifiedTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

accounts_groups.to_csv('prisma_accounts_groups_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')

#------------------------------------>
print('Backing up anomaly settings')
pc_settings, response_package = pc_lib_api.api_anomalies_settings_get_UEBA(pc_settings)
anomalies_settings_UEBA = response_package['data']

pc_settings, response_package = pc_lib_api.api_anomalies_settings_get_Network(pc_settings)
anomalies_settings_Network = response_package['data']

# Put JSON(s) inside a data frame
UEBA = pandas.json_normalize(anomalies_settings_UEBA) #put json inside a dataframe
NETWORK = pandas.json_normalize(anomalies_settings_Network)

UEBA.to_csv('anomalies_settings_UEBA_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z')
NETWORK.to_csv('anomalies_settings_Network_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')

#-------------------------------------->
print('Backing up anomalies trusted list')
pc_settings, response_package = pc_lib_api.api_anomalies_trusted_list(pc_settings)
anomalies_trusted_list = response_package['data']

anomalies_trusted_list = pandas.json_normalize(anomalies_trusted_list) #put json inside a dataframe
anomalies_trusted_list.to_csv('anomalies_trusted_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False) 
print('Done.')

#------------------------------------------>

print('Backing up audit logs')
audit_info = {}
audit_info['timeType'] = "relative"
audit_info['timeUnit'] = "day"
audit_info['timeAmount'] = "90"

pc_settings, response_package = pc_lib_api.api_audit_logs_get(pc_settings, data=audit_info)
audit_logs_get = response_package['data']

audit_logs = pandas.json_normalize(audit_logs_get) #put json inside a dataframe
audit_logs['timestamp']=(pandas.to_datetime(audit_logs['timestamp'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
audit_logs.to_csv('audit_logs_get_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')

#------------------------------------------>

print('Backing up GCP child cloud accounts, aka GCP projects')
pc_settings, response_package = pc_lib_api.api_cloud_accounts_list_names_get(pc_settings)
cloud_accounts_list_names = response_package['data']

# Put json inside a dataframe
prisma_cloud_accounts = pandas.json_normalize(cloud_accounts_list_names)

# For the items returned, in the cloud type column, will focus on GCP only. 
mvp = prisma_cloud_accounts.query('cloudType == "gcp"')

# Filters out the remaining GCP items to just the "id" column.
mvp1 = mvp.filter(['id'])

mvp1.to_csv('prisma_cloud_accounts_list_names_{}.csv'.format(now), sep=',', encoding='utf-8', index=False)
print('Done')

#----------------------------------------------->

print('Backing up cloud accounts')
pc_settings, response_package = pc_lib_api.api_cloud_accounts_list_get(pc_settings)
cloud_accounts_list = response_package['data']

#put json inside a dataframe
prisma_cloud_accounts = pandas.json_normalize(cloud_accounts_list)

#Change Epoch Unix Time on specific columns to Chicago/Central. Users can change to any timezone.
prisma_cloud_accounts['lastModifiedTs']=(pandas.to_datetime(prisma_cloud_accounts['lastModifiedTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
prisma_cloud_accounts['addedOn']=(pandas.to_datetime(prisma_cloud_accounts['addedOn'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

prisma_cloud_accounts.to_csv('prisma_cloud_accounts_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 

print('Done.')

#---------------------------------------------->

print('Backing up notification templates')
pc_settings, response_package = pc_lib_api.api_notification_template_get(pc_settings)
notification_template = response_package['data']

#Put JSON inside a dataframe
notification_template = pandas.json_normalize(notification_template) 

# Change the timestamp from Unix time to a specific time zone on a column:
notification_template['createdTs']=(pandas.to_datetime(notification_template['createdTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
notification_template['lastModifiedTs']=(pandas.to_datetime(notification_template['lastModifiedTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
notification_template['reason.lastUpdated']=(pandas.to_datetime(notification_template['reason.lastUpdated'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

notification_template.to_csv('notification_template_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')

#---------------------------------------------->

print('Backing up user roles')
pc_settings, response_package = pc_lib_api.api_user_role_list_get(pc_settings)
user_role_list = response_package['data']

# Put json inside a dataframe
prisma_user_role_list = pandas.json_normalize(user_role_list)

# Change a column timestamp from Unix Time to any time zone
prisma_user_role_list['lastModifiedTs']=(pandas.to_datetime(prisma_user_role_list['lastModifiedTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

prisma_user_role_list.to_csv('prisma_user_role_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')

#---------------------------------------------->

print('Backing up user list')
pc_settings, response_package = pc_lib_api.api_user_list_get(pc_settings)
user_list_get = response_package['data']

user_list = pandas.json_normalize(user_list_get) #put json inside a dataframe
user_list['lastModifiedTs']=(pandas.to_datetime(user_list['lastModifiedTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
user_list['lastLoginTs']=(pandas.to_datetime(user_list['lastLoginTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

user_list.to_csv('user_list_get_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')

#---------------------------------------------->

print('Backing up third party integration')
pc_settings, response_package = pc_lib_api.api_third_party_get(pc_settings)
third_party_get = response_package['data']

third_party = pandas.json_normalize(third_party_get) #put json inside a dataframe
third_party['lastModifiedTs']=(pandas.to_datetime(third_party['lastModifiedTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
third_party['createdTs']=(pandas.to_datetime(third_party['createdTs'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
third_party['reason.lastUpdated']=(pandas.to_datetime(third_party['reason.lastUpdated'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

third_party.to_csv('third_party_get_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')

#---------------------------------------------->

print('Backing up policies')

# Grab enabled policies
pc_settings, response_package = pc_lib_api.api_policy_v2_list_get_enabled(pc_settings)
policy_v2_list = response_package['data']

# Grab the RQLs which are "Saved"
pc_settings, response_package = pc_lib_api.api_search_get_all(pc_settings)
saved_searches = response_package['data']

# Grab the RQLs which are "Recent"
pc_settings, response_package = pc_lib_api.api_search_get_all_recent(pc_settings)
saved_searches_recent = response_package['data']

# Put json inside a dataframe
pu = pandas.json_normalize(policy_v2_list) 

# Change timestamp for specific column from UNIX time to any time zone. 
pu['ruleLastModifiedOn']=(pandas.to_datetime(pu['ruleLastModifiedOn'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))
pu['lastModifiedOn']=(pandas.to_datetime(pu['lastModifiedOn'],unit='ms')).apply(lambda x: x.tz_localize('UTC').tz_convert('America/Chicago'))

# List of columns that we want to specify, query and custom_query are additional items we are adding into the default set. Each of these 2 columns will take in mapped RQL data either from RECENT or SAVED json responses. 
POLICY_FIELDS = ["name", "policyType", "policyClass", "policySubTypes", "policyUpi", "remediable", "systemDefault", "rule.type", "ruleLastModifiedOn", "cloudType", "severity", "owner", "policyMode", "complianceMetadata", "labels", "description", "recommendation", "enabled", "lastModifiedBy", "lastModifiedOn", "policyId", "rule.name", "rule.criteria", "rule.parameters.withIac", "rule.children", "rule.parameters.savedSearch", "query", "custom_query"]

# Put json(s) inside a dataframe
pu2 = pandas.json_normalize(saved_searches) #put json inside a dataframe
pu3 = pandas.json_normalize(saved_searches_recent)

#For custom column name "query" on our PU dataframe, map on "rule.criteria" column (policy v2 json response) to "id" column (saved search json response). Pull in the associated query column (not our custom one) from the saved search response. Once done, populate the data into our own "query" column that we specified. 
pu['query'] = pu['rule.criteria'].map(pu2.set_index('id')['query'])
#For custom column name "query" on our PU dataframe, map on "rule.criteria" column (policy v2 json response) to "id" column (recent search json response). Pull in the associated query column (not our custom one) from the saved search response. Once done, populate the data into our own "query" column that we specified. 
pu['custom_query'] = pu['rule.criteria'].map(pu3.set_index('id')['query'])

pu[POLICY_FIELDS].to_csv('policy_v2_list_{}.csv'.format(now), sep=',', encoding='utf-8', index=False, date_format='%m-%d-%y || %I:%M:%S %p CDT%z') 
print('Done.')
