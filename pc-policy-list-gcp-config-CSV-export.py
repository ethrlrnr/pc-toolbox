from __future__ import print_function

from pprint import pprint

try:
    input = raw_input
except NameError:
    pass
import argparse
import pc_lib_api
import pc_lib_general
import os
import pandas
from datetime import datetime, date, time
from pathlib import Path

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

# Preparing the destination file
export_file_name = "policy_list_filtered_" + str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".csv"
export_file_path = os.path.join(Path.home(), "prisma-cloud-exports")
if not os.path.exists(export_file_path):
    os.makedirs(export_file_path)

export_file_header = "cloudType,createdBy,createdOn,deleted,description,enabled,labels,lastModifiedBy,lastModifiedOn," \
                     "name,owner,policyCategory,policyClass,policyId,policyMode,policySubTypes,policyType,policyUpi," \
                     "recommendation,remediable,remediation.cliScriptTemplate,remediation.description," \
                     "remediation.impact,rql_query,rule.children,rule.criteria,rule.criteria_cft,rule.criteria_k8s," \
                     "rule.criteria_tf,rule.name,rule.name_cft,rule.name_k8s,rule.name_tf," \
                     "rule.parameters.savedSearch,rule.parameters.withIac,rule.type,rule.type_cft,rule.type_k8s," \
                     "rule.type_tf,ruleLastModifiedOn,severity,systemDefault "
print("Printing header to: {0}".format(os.path.join(export_file_path, export_file_name)))
pc_lib_general.pc_file_write_csv(export_file_name, export_file_header, export_file_path)

# Grab the policies
print('API - Getting current policy list...', end='')

# Retrieves policies high, medium, low; that are only for gcp or all; run, build, and run_and_build
query_params = "policy.severity=high&policy.severity=medium&policy.severity=low&cloud.type=gcp&cloud.type=all&policy" \
               ".subtype=run" \
               "&policy.subtype=build&policy.subtype=run_and_build"
pc_settings, response_package = pc_lib_api.api_policy_v2_list_filtered_get(pc_settings, query_params=query_params)
policy_v2_list = response_package['data']
# Removing complianceMetadata from list and retrieving the RQL if exist
for policy_item in policy_v2_list:
    # Fix for missing columns
    if 'policyUpi' not in policy_item:
        policy_item['policyUpi'] = ''
    if 'recommendation' not in policy_item:
        policy_item['recommendation'] = ''
    if 'withIac' not in policy_item['rule']['parameters']:
        policy_item['rule']['parameters']['withIac'] = ''
    if 'remediation' not in policy_item:
        policy_item['remediation'] = {}
    if 'cliScriptTemplate' not in policy_item['remediation']:
        policy_item['remediation']['cliScriptTemplate'] = ''
    if 'description' not in policy_item['remediation']:
        policy_item['remediation']['description'] = ''
    if 'impact' not in policy_item['remediation']:
        policy_item['remediation']['impact'] = ''

    # If no children defined, create the headers for consistency
    if 'children' not in policy_item['rule']:
        policy_item['rule']['children'] = []
        policy_item['rule']['name_tf'] = ''
        policy_item['rule']['type_tf'] = ''
        policy_item['rule']['criteria_tf'] = ''
        policy_item['rule']['name_cft'] = ''
        policy_item['rule']['type_cft'] = ''
        policy_item['rule']['criteria_cft'] = ''
        policy_item['rule']['name_k8s'] = ''
        policy_item['rule']['type_k8s'] = ''
        policy_item['rule']['criteria_k8s'] = ''
    else:
        # If at least one child, create the headers and dictionary element for the type of rule, and create the
        # headers for the types that are not present
        for child in policy_item['rule']['children']:
            if child['type'] == 'tf':
                policy_item['rule']['name_tf'] = child['name']
                policy_item['rule']['type_tf'] = child['type']
                policy_item['rule']['criteria_tf'] = child['criteria']
            if child['type'] == 'cft':
                policy_item['rule']['name_cft'] = child['name']
                policy_item['rule']['type_cft'] = child['type']
                policy_item['rule']['criteria_cft'] = child['criteria']
            if child['type'] == 'k8s':
                policy_item['rule']['name_k8s'] = child['name']
                policy_item['rule']['type_k8s'] = child['type']
                policy_item['rule']['criteria_k8s'] = child['criteria']
            # Check if there are missing types and create the headers for consistency
            if 'type_tf' not in policy_item['rule']:
                policy_item['rule']['name_tf'] = ''
                policy_item['rule']['type_tf'] = ''
                policy_item['rule']['criteria_tf'] = ''
            if 'type_cft' not in policy_item['rule']:
                policy_item['rule']['name_cft'] = ''
                policy_item['rule']['type_cft'] = ''
                policy_item['rule']['criteria_cft'] = ''
            if 'type_k8s' not in policy_item['rule']:
                policy_item['rule']['name_k8s'] = ''
                policy_item['rule']['type_k8s'] = ''
                policy_item['rule']['criteria_k8s'] = ''
    if 'criteria' not in policy_item['rule']:
        policy_item['rule']['criteria'] = ''
    policy_item['rql_query'] = ''

    if "complianceMetadata" in policy_item:
        del policy_item['complianceMetadata']
    if 'savedSearch' in policy_item['rule']['parameters'] and policy_item['rule']['parameters'][
        'savedSearch'] == 'true':
        pc_settings, policy_rql = pc_lib_api.api_search_get(pc_settings, policy_item['rule']['criteria'])
        # pprint(policy_rql['data']['query'])
        policy_item['rql_query'] = policy_rql['data']['query']

    # Converting to CSV and appending to file

    policies_df = pandas.json_normalize(policy_item)  # put json inside a dataframe
    policies_df = policies_df[sorted(policies_df.columns)]  # sorting columns alphabetically to match the header of the file
    policies_df.to_csv(export_file_path + "/" + export_file_name, sep=',', encoding='utf-8', index=False,
                       date_format='%m-%d-%y || %I:%M:%S %p CDT%z', mode='a', header=False)
print('Done.')
