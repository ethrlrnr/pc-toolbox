from __future__ import print_function

import os
from pprint import pprint

try:
    input = raw_input
except NameError:
    pass
import argparse
import pc_lib_api
import pc_lib_general
import json
import csv
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
    '-url_compute',
    '--uiurl_compute',
    type=str,
    help='*Required* - Base URL used in the UI for connecting to Prisma Cloud Compute.  '
         'Formatted as region.cloud.twistlock.com/identifier.'
         'Retrieved from Compute->Manage->System->Downloads->Path to Console')

parser.add_argument(
    '-y',
    '--yes',
    action='store_true',
    help='(Optional) - Override user input for verification (auto answer for yes).')

args = parser.parse_args()
# --End parse command line arguments-- #

# --Main-- #
# Get login details worked out
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl, args.uiurl_compute)

# Verification (override with -y)
if not args.yes:
    print()
    print('Ready to execute commands against your Prisma Cloud tenant.')
    verification_response = str(input('Would you like to continue (y or yes to continue)?'))
    continue_response = {'yes', 'y'}
    print()
    if verification_response not in continue_response:
        pc_lib_general.pc_exit_error(400, 'Verification failed due to user response.  Exiting...')

# Sort out API Login
print('API - Getting authentication token...', end='')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
token_time_stamp = datetime.now()
print('Done.')

start_time = datetime.now()
print('API - Getting IaC Scans...', end='')
try:
    # Preparing the destination file
    export_file_name = "iac_scan_get_full_" + str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".csv"
    export_file_path = os.path.join(Path.home(), "prisma-cloud-exports")
    if not os.path.exists(export_file_path):
        os.makedirs(export_file_path)
    # Create the filter, excluding scans "processing", retrieving last 1 week of scans
    api_call_filter_status = "filter%5Bstatus%5D=passed&filter%5Bstatus%5D=failed&filter%5Bstatus%5D=failed_n_merged&filter%5Bstatus%5D=failed_n_deployed&filter%5Bstatus%5D=error"
    api_call_filter_time_type = "filter%5BtimeType%5D=absolute"
    time_now = datetime.now().timestamp()
    days_back = 45
    api_call_filter_time_start = int((time_now * 1000) - (days_back*24*60*60*1000))
    api_call_filter_time_end = int((time_now * 1000))
    api_call_filter_time_window = "filter%5BstartTime%5D=" + str(api_call_filter_time_start) + "&filter%5BendTime%5D=" + str(api_call_filter_time_end)

    # Create the pagination parameters, starting on page 1, with a maximum of 25 scans per page
    api_call_page_size = "page%5Bsize%5D=25"
    api_call_page_number = "page%5Bnumber%5D=1"

    # Headers as per API version - July 2021
    export_file_header = "attributes.deployed,attributes.fail,attributes.failureCriteria," \
                         "attributes.matchedPoliciesSummary.high,attributes.matchedPoliciesSummary.low," \
                         "attributes.matchedPoliciesSummary.medium,attributes.merged,attributes.name,attributes.pass," \
                         "attributes.resourceList,attributes.scanAttributes.appliedAlertRules," \
                         "attributes.scanAttributes.resourcesScanned," \
                         "attributes.scanAttributes.templateType,attributes.scanTime,attributes.status," \
                         "attributes.tags,attributes.type,attributes.user,details_data,details_meta.errorDetails," \
                         "details_meta.matchedPoliciesSummary.high,details_meta.matchedPoliciesSummary.low," \
                         "details_meta.matchedPoliciesSummary.medium,id,links.self," \
                         "relationships.scanResult.links.related,z_attributes_scanAttributes"
    print("Printing header to: {0}".format(os.path.join(export_file_path, export_file_name)))
    pc_lib_general.pc_file_write_csv(export_file_name, export_file_header, export_file_path)

    # Calling the API until no further pages

    while True:

        # Calling the API to retrieve list of scans as per the filters

        api_call_str_params = api_call_filter_status + "&" + api_call_filter_time_type + "&" + api_call_filter_time_window + "&" + api_call_page_size + "&" + api_call_page_number
        pc_settings, response_package = pc_lib_api.api_iac_scans_get(pc_settings,api_call_str_params)
        response_data = response_package['data']
        response_data_data = response_data['data']
        response_data_meta = response_data['meta']
        response_data_links = response_data['links']

        current_page = (response_data_links['self'].split('page[number]='))[1]
        next_page = (response_data_links['next'].split('page[number]='))[1]
        last_page = (response_data_links['last'].split('page[number]='))[1]

        # Calling the detailed scans result list for each item in the page

        for scan_item in response_data_data:
            scan_id = (scan_item['links']['self'].split('/'))[3]
            pc_settings, response_package_2 = pc_lib_api.api_iac_scan_result_get(pc_settings,scan_id)
            scan_item_2_data = response_package_2['data']['data']
            scan_item_2_meta = response_package_2['data']['meta']

            # Workaround for a strange key showing up in some scans
            if 'newKey' in scan_item['attributes']['scanAttributes']:
                del scan_item['attributes']['scanAttributes']['newKey']

            # In case of scan status error, add attributes for json completeness
            if scan_item['attributes']['status'] == 'error':
                scan_item['attributes']['scanAttributes']['templateType'] = ''
                scan_item['attributes']['scanAttributes']['resourcesScanned'] = 0
                scan_item['attributes']['scanAttributes']['appliedAlertRules'] = ''

            # Keep fixed scanAttributes and relocate/remove custom scanAttributes
            z_otherAttributes_list = []
            for scanAttr in scan_item["attributes"]["scanAttributes"]:
                if scanAttr not in ['templateType' ,'resourcesScanned','appliedAlertRules']:
                    # Relocate
                    attr_key = scanAttr
                    attr_value = scan_item["attributes"]["scanAttributes"][scanAttr]
                    # will be shown at the end of the columns list
                    z_otherAttributes_list.append({attr_key: attr_value})
            # Delete
            for attr_keys_to_delete in z_otherAttributes_list:
                for attr_key_to_delete in attr_keys_to_delete:
                    del scan_item["attributes"]["scanAttributes"][attr_key_to_delete]
            scan_item["z_otherAttributes_list"] = z_otherAttributes_list

            # Consolidate data from both API calls into one json
            consolidated_json = scan_item
            consolidated_json['details_meta'] = scan_item_2_meta
            consolidated_json['details_data'] = scan_item_2_data

            scans_df = pandas.json_normalize(consolidated_json)  # put json inside a dataframe
            scans_df = scans_df[sorted(scans_df.columns)]
            scans_df.to_csv(export_file_path + "/" + export_file_name, sep=',', encoding='utf-8', index=False,
                        date_format='%m-%d-%y || %I:%M:%S %p CDT%z', mode='a', header=False)

        # Check if there are more pages

        if current_page == last_page:
            break
        else:
            api_call_page_number = "page%5Bnumber%5D=" + str(next_page)

    print('Done.')

except Exception as ex:

    print("Error: " + str(ex))

print("All Done; Started at: " + str(start_time) + " and ended at: " + str(datetime.now()))
