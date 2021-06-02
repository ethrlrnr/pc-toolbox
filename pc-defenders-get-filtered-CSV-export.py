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
         'Formatted as region.cloud.twistlock.com/identifier. Example: us-west1.cloud.twistlock.com/us-3-159182384  '
         'Retrieved from Compute->Manage->System->Downloads->Path to Console')

args = parser.parse_args()
# --End parse command line arguments-- #

# --Main-- #
# Get login details worked out
pc_settings = pc_lib_general.pc_login_get(args.username, args.password, args.uiurl, args.uiurl_compute)

# Verification (override with -y)
# if not args.yes:
#     print()
#     print('Ready to excute commands aginst your Prisma Cloud tenant.')
#     verification_response = str(input('Would you like to continue (y or yes to continue)?'))
#     continue_response = {'yes', 'y'}
#     print()
#     if verification_response not in continue_response:
#         pc_lib_general.pc_exit_error(400, 'Verification failed due to user response.  Exiting...')

# Sort out API Login
print('API - Getting authentication token...', end='')
pc_settings = pc_lib_api.pc_jwt_get(pc_settings)
print('Done.')

# Get containers list
print('API - Getting defenders list...', end='')
pc_settings, response_package = pc_lib_api.api_defenders_get(pc_settings)
file_name = "defenders_list_filtered_" + str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".csv"
file_path = os.path.join(Path.home(), "prisma-compute-exports")
defenders = response_package['data']
data_header = "Hostname,Cluster,FQDN,Project,Connected,Type,Registry Scanner,Cluster Monitoring"
print("Exporting data to: " + os.path.join(file_path, file_name))
pc_lib_general.pc_file_write_csv(file_name, data_header, file_path)
for defender in defenders:
    data_info_hostname = defender['hostname']
    data_info_fqdn = defender['fqdn']
    data_info_cluster = defender['cluster']
    data_info_connected = defender['connected']
    data_info_type = defender['type']
    data_info_regscanner = defender['features']['registryScanner']
    data_info_clustmonitoring = defender['features']['clusterMonitoring']
    data_info_project = defender['cloudMetadata']['accountID']
    data_line = data_info_hostname + "," + data_info_fqdn + "," + data_info_cluster + "," + data_info_project + "," + str(data_info_connected) + "," + data_info_type + "," + str(data_info_regscanner) + "," + str(data_info_clustmonitoring)
    pc_lib_general.pc_file_write_csv(file_name, data_line, file_path)
print('Done.')
