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
print('API - Getting Alert Rules...', end='')
try:
    # Preparing the destination file
    export_file_name = "alert_rules_get_full_" + str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".csv"
    export_file_path = os.path.join(Path.home(), "prisma-cloud-exports")
    if not os.path.exists(export_file_path):
        os.makedirs(export_file_path)
    pc_settings, response_package = pc_lib_api.api_alert_names_get(pc_settings)
    alert_rules_df = pandas.json_normalize(response_package['data'])  # put json inside a dataframe
    alert_rules_df = alert_rules_df[sorted(alert_rules_df.columns)]
    alert_rules_df.to_csv(export_file_path + "/" + export_file_name, sep=',', encoding='utf-8', index=False,
                    date_format='%m-%d-%y || %I:%M:%S %p CDT%z', mode='a', header=True)
except Exception as ex:
    print("Error: " + str(ex))

print("All Done; Started at: " + str(start_time) + " and ended at: " + str(datetime.now()))
