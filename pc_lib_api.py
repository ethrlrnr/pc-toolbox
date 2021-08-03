import json
import requests
import time
import pc_lib_general


# --Helper Methods-- #
# Main API Call Function
def pc_call_api(action, api_url, pc_settings, data=None, params=None, try_count=5, max_retries=9, auth_count=0,
                auth_retries=5, headers_param={'Content-Type': 'application/json'}):
    retry_statuses = [429, 500, 502, 503, 504]
    auth_statuses = [401]
    retry_wait_timer = 30
    headers = headers_param
    headers['x-redlock-auth'] = pc_settings['jwt']

    # Make the API Call
    print(headers)
    response = requests.request(action, api_url, params=params, headers=headers, data=json.dumps(data))
    print(response)

    # Check for an error to retry, re-auth, or fail
    if response.status_code in retry_statuses:
        try_count = try_count + 1
        if try_count <= max_retries:
            time.sleep(retry_wait_timer)
            return pc_call_api(action=action, api_url=api_url, pc_settings=pc_settings, data=data, params=params,
                               try_count=try_count, max_retries=max_retries, auth_count=auth_count,
                               auth_retries=auth_retries, headers_param=headers)
        else:
            response.raise_for_status()
    elif response.status_code in auth_statuses and pc_settings['jwt'] is not None:
        auth_count = auth_count + 1
        if auth_count <= auth_retries:
            pc_settings = pc_jwt_get(pc_settings)
            return pc_call_api(action=action, api_url=api_url, pc_settings=pc_settings, data=data, params=params,
                               try_count=try_count, max_retries=max_retries, auth_count=auth_count,
                               auth_retries=auth_retries, headers_param=headers)
        else:
            response.raise_for_status()
    else:
        response.raise_for_status()

    # Check for valid response and catch if blank or unexpected
    api_response_package = {}
    api_response_package['statusCode'] = response.status_code
    try:
        # Check if response should be CSV or JSON
        if 'accept' in headers and headers['accept'] == 'text/csv':
            api_response_package['data'] = response.text
        else:
            api_response_package['data'] = response.json()
    except ValueError:
        if response.text == '':
            api_response_package['data'] = None
        else:
            pc_lib_general.pc_exit_error(501, 'The server returned an unexpected server response.')
    return pc_settings, api_response_package


# Get JWT for access
def pc_jwt_get(pc_settings):
    url = "https://" + pc_settings['apiBase'] + "/login"
    action = "POST"
    pc_settings['jwt'] = pc_call_api(action, url, pc_settings, data=pc_settings)[1]['data']['token']
    return pc_settings


# Get Compliance Standards list
def api_compliance_posture_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/compliance/posture"
    return pc_call_api(action, url, pc_settings)


# Get Compliance Standards list
def api_compliance_standard_list_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/compliance"
    return pc_call_api(action, url, pc_settings)


# Add a new Compliance Standard
def api_compliance_standard_add(pc_settings, compliance_standard_new):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/compliance"
    return pc_call_api(action, url, pc_settings, data=compliance_standard_new)


# Get Compliance Standards Requirements list
def api_compliance_standard_requirement_list_get(pc_settings, compliance_standard_id):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/compliance/" + compliance_standard_id + "/requirement"
    return pc_call_api(action, url, pc_settings)


# Add a new Compliance Standard Requirement
def api_compliance_standard_requirement_add(pc_settings, compliance_standard_id, compliance_requirement_new):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/compliance/" + compliance_standard_id + "/requirement"
    return pc_call_api(action, url, pc_settings, data=compliance_requirement_new)


# Get Compliance Standards Requirements Sections list
def api_compliance_standard_requirement_section_list_get(pc_settings, compliance_requirement_id):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/compliance/" + compliance_requirement_id + "/section"
    return pc_call_api(action, url, pc_settings)


# Add a new Compliance Standard Requirement Section
def api_compliance_standard_requirement_section_add(pc_settings, compliance_requirement_id, compliance_section_new):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/compliance/" + compliance_requirement_id + "/section"
    return pc_call_api(action, url, pc_settings, data=compliance_section_new)


# Get Compliance Standards Policy list
def api_compliance_standard_policy_list_get(pc_settings, source_compliance_standard_name):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/policy"
    filters = [('policy.complianceStandard', source_compliance_standard_name)]
    return pc_call_api(action, url, pc_settings, params=filters)


# Get Compliance Standards Policy list (v2)
def api_compliance_standard_policy_v2_list_get(pc_settings, source_compliance_standard_name):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/v2/policy"
    filters = [('policy.complianceStandard', source_compliance_standard_name)]
    return pc_call_api(action, url, pc_settings, params=filters)


# Get policy list
def api_policy_list_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/policy"
    return pc_call_api(action, url, pc_settings)


# Get policy list (v2)
def api_policy_v2_list_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/v2/policy"
    return pc_call_api(action, url, pc_settings)


# Get policy list (v2)
def api_policy_v2_list_get_enabled(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/v2/policy?policy.enabled=true"
    return pc_call_api(action, url, pc_settings)


# Get Custom Policy list (v2)
def api_policy_custom_v2_list_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/v2/policy?policy.enabled=true"
    filters = [('policy.policyMode', 'custom')]
    return pc_call_api(action, url, pc_settings, params=filters)


# Get a policy
def api_policy_get(pc_settings, policy_id):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/policy/" + policy_id
    return pc_call_api(action, url, pc_settings)


# Add a policy
def api_policy_add(pc_settings, policy_to_add):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/policy"
    return pc_call_api(action, url, pc_settings, data=policy_to_add)


# Update a policy
def api_policy_update(pc_settings, policy_id, policy_update):
    action = "PUT"
    url = "https://" + pc_settings['apiBase'] + "/policy/" + policy_id
    return pc_call_api(action, url, pc_settings, data=policy_update)


# Update policy status
def api_policy_status_update(pc_settings, policy_id, status):
    action = "PATCH"
    url = "https://" + pc_settings['apiBase'] + "/policy/" + policy_id + "/status/" + status
    return pc_call_api(action, url, pc_settings)


# Get a Saved Search
def api_search_get(pc_settings, search_id):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/search/history/" + search_id
    return pc_call_api(action, url, pc_settings)


def api_search_get_all(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/search/history/?filter=saved&limit=10000"
    return pc_call_api(action, url, pc_settings)


def api_search_get_all_recent(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/search/history/?filter=recent&limit=10000"
    return pc_call_api(action, url, pc_settings)


# Join UEBA and Network together, easier this way.
def api_anomalies_settings_get_UEBA(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/anomalies/settings?type=UEBA"
    return pc_call_api(action, url, pc_settings)


def api_anomalies_settings_get_Network(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/anomalies/settings?type=Network"
    return pc_call_api(action, url, pc_settings)


def api_anomalies_trusted_list(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/anomalies/trusted_list"
    return pc_call_api(action, url, pc_settings)


# Get audit logs
def api_audit_logs_get(pc_settings, params=None, data=None):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/audit/redlock"
    return pc_call_api(action, url, pc_settings, params=data)


# Add a Saved Search
def api_search_add(pc_settings, type_of_search, search_to_add):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/search/" + type_of_search
    return pc_call_api(action, url, pc_settings, data=search_to_add)


# Get User Role list
def api_user_role_list_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/user/role"
    return pc_call_api(action, url, pc_settings)


# Add new User Role
def api_user_role_add(pc_settings, user_role_to_add):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/user/role"
    return pc_call_api(action, url, pc_settings, data=user_role_to_add)


# Get User list
def api_user_list_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/v2/user"
    return pc_call_api(action, url, pc_settings)


# Get a User
def api_user_get(pc_settings, useremail):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/user/" + useremail
    return pc_call_api(action, url, pc_settings)


# Add new User
def api_user_add(pc_settings, user_to_add):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/user"
    return pc_call_api(action, url, pc_settings, data=user_to_add)


# Add new User v2
def api_user_add_v2(pc_settings, user_to_add_v2):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/v2/user"
    return pc_call_api(action, url, pc_settings, data=user_to_add_v2)


# Update a User
def api_user_update(pc_settings, user_to_update):
    action = "PUT"
    url = "https://" + pc_settings['apiBase'] + "/user/" + user_to_update['email']
    return pc_call_api(action, url, pc_settings, data=user_to_update)


# Update a User v2
def api_user_update_v2(pc_settings, user_to_update_v2):
    action = "PUT"
    url = "https://" + pc_settings['apiBase'] + "/v2/user/" + user_to_update_v2['email']
    return pc_call_api(action, url, pc_settings, data=user_to_update_v2)


# Delete Account Group
def api_delete_account_group(pc_settings, account_group_to_delete):
    action = "DELETE"
    url = "https://" + pc_settings['apiBase'] + "/cloud/group/" + account_group_to_delete['id']
    return pc_call_api(action, url, pc_settings, data=account_group_to_delete)


# Delete User Role
def api_delete_user_role(pc_settings, user_role_to_delete):
    action = "DELETE"
    url = "https://" + pc_settings['apiBase'] + "/user/role/" + user_role_to_delete['id']
    return pc_call_api(action, url, pc_settings, data=user_role_to_delete)


# Get alert list with filters
def api_alert_list_get(pc_settings, params=None, data=None):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/alert"
    return pc_call_api(action, url, pc_settings, params=params, data=data)


# Async Alerts Status
def api_async_alerts_job_status(pc_settings, job_id, params=None, data=None):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/alert/jobs/" + job_id + "/status"
    return pc_call_api(action, url, pc_settings)


# Async Alerts JSON Response
def api_async_alerts_job_download(pc_settings, job_id, params=None, data=None):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/alert/jobs/" + job_id + "/download"
    return pc_call_api(action, url, pc_settings)


# Async Alerts Job
# https://prisma.pan.dev/api/cloud/cspm/alerts#operation/submit-job-for-listing-alerts
def api_async_alerts_job(pc_settings, params=None, data=None):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/alert/jobs"
    return pc_call_api(action, url, pc_settings, params=params, data=data)


# Get alert list with filters (V2)
def api_alert_v2_list_get(pc_settings, params=None, data=None):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/v2/alert"
    return pc_call_api(action, url, pc_settings, params=params, data=data)


def api_search_config(pc_settings, params=None, data=None, headers_param={'Content-Type': 'application/json'}):
    action = "POST"
    headers = headers_param
    url = "https://" + pc_settings['apiBase'] + "/search/config"
    return pc_call_api(action, url, pc_settings, params=params, data=data, headers_param=headers)


# Dismiss alerts
def api_dismiss_alert_post(pc_settings, params=None, data=None):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/alert/dismiss"
    return pc_call_api(action, url, pc_settings, params=params, data=data)


# Get alert names
def api_alert_names_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/v2/alert/rule?enabled=true"
    return pc_call_api(action, url, pc_settings)


# Get resource list with filters (V2)
def api_resource_scan_info(pc_settings, params=None, data=None):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/resource/scan_info"
    return pc_call_api(action, url, pc_settings, params=params, data=data)


# Get resource list with filters (V2)
def api_asset_inventory(pc_settings, params=None, data=None):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/v2/inventory"
    return pc_call_api(action, url, pc_settings, params=params, data=data)


# Get Compliance Reports list
def api_compliance_report_list_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/report"
    return pc_call_api(action, url, pc_settings)


# Add Compliance Report
def api_compliance_report_add(pc_settings, report_to_add):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/report"
    return pc_call_api(action, url, pc_settings, data=report_to_add)


# Delete Compliance Reports
def api_compliance_report_delete(pc_settings, report_id):
    action = "DELETE"
    url = "https://" + pc_settings['apiBase'] + "/report/" + report_id
    return pc_call_api(action, url, pc_settings)


# Download Compliance Report
def api_compliance_report_download(pc_settings, report_id):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/report/" + report_id + "/download"
    jwt, response_status, response_json = pc_call_api(action, url, pc_settings)
    if response_status == 204:
        # download pending
        pass
    elif response_status == 200:
        # download ready
        pass


# Get Access Key list
def api_access_key_list_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/access_keys"
    return pc_call_api(action, url, pc_settings)


# Get Third Party Integrations
def api_third_party_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/integration"
    return pc_call_api(action, url, pc_settings)


# Get Third Party Integrations
def api_asset_inventory_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/filter/inventory"
    return pc_call_api(action, url, pc_settings)


# Get Notification Templates
def api_notification_template_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/notification/template?type=service_now"
    return pc_call_api(action, url, pc_settings)


# Get Cloud Accounts list - level 1 get
def api_cloud_accounts_list_get(pc_settings, params=None):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/cloud"
    return pc_call_api(action, url, pc_settings, params=params)


# Get Cloud Accounts Names list - level 2 cloud sub accounts
def api_cloud_accounts_list_names_get(pc_settings, params=None):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/cloud/name"
    return pc_call_api(action, url, pc_settings, params=params)


# Add Cloud Account *** level 1 post
def api_cloud_accounts_add(pc_settings, cloud_type, cloud_account_to_add):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/cloud/" + cloud_type
    return pc_call_api(action, url, pc_settings, data=cloud_account_to_add)


# Get Account Groups Names list
def api_accounts_groups_list_get(pc_settings, params=None):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/cloud/group"
    # url = "https://" + pc_settings['apiBase'] + "/cloud/name"
    return pc_call_api(action, url, pc_settings, params=params)


# encoding='utf8
# Add Account Group - level 3 needed
def api_accounts_groups_add(pc_settings, new_accounts_group):
    action = "POST"
    url = "https://" + pc_settings['apiBase'] + "/cloud/group"
    return pc_call_api(action, url, pc_settings, data=new_accounts_group)


# Get Containers scan reports from Prisma Cloud Compute API
# https://prisma.pan.dev/api/cloud/cwpp/containers#operation/get-containers

def api_containers_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiCompute'] + "/api/v1/containers"
    return pc_call_api(action, url, pc_settings, data="")


# DiscoveredVMs returns discovered cloud VM instances from Prisma Cloud Compute API
# https://prisma.pan.dev/api/cloud/cwpp/cloud#operation/get-cloud-discovery-vms

def api_cloud_discovery_vms_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiCompute'] + "/api/v1/cloud/discovery/vms"
    return pc_call_api(action, url, pc_settings, data="")


# Defenders returns all deployed Defenders from Prisma Cloud Compute API
# https://prisma.pan.dev/api/cloud/cwpp/defenders#operation/get-defenders

def api_defenders_get(pc_settings):
    action = "GET"
    url = "https://" + pc_settings['apiCompute'] + "/api/v1/defenders"
    return pc_call_api(action, url, pc_settings, data="")


# Returns a list of IaC scans that meet the given conditions.
# https://prisma.pan.dev/api/cloud/cspm/iac-scan#operation/getScans
# Example: https://api.prismacloud.io/iac/v2/scans?
#   filter%5Bstatus%5D=passed&
#   filter%5Bstatus%5D=failed&
#   filter%5Bstatus%5D=failed_n_merged&
#   filter%5Bstatus%5D=failed_n_deployed&
#   filter%5Bstatus%5D=error&
#   filter%5BtimeAmount%5D=1&
#   filter%5BtimeType%5D=relative&
#   filter%5BtimeUnit%5D=week&
#   groupBy=scanId&
#   page%5Bnumber%5D=1&
#   page%5Bsize%5D=25&

def api_iac_scans_get(pc_settings, str_params):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/iac/v2/scans?" + str_params
    return pc_call_api(action, url, pc_settings, headers_param={})


# Returns scan result details for the completed scan that has the specified scan ID
# https://prisma.pan.dev/api/cloud/cspm/iac-scan#operation/getScanResult

def api_iac_scan_result_get(pc_settings, scan_id):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/iac/v2/scans/" + scan_id + "/results"
    return pc_call_api(action, url, pc_settings)


# Returns the status of the asynchronous IaC scan job that has the specified scan ID.
# https://prisma.pan.dev/api/cloud/cspm/iac-scan#operation/getAsyncScanStatus

def api_iac_scan_status_get(pc_settings, scan_id):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/iac/v2/scans/" + scan_id + "/status"
    return pc_call_api(action, url, pc_settings)


# Get all policies filtered by query parameters
#  default policy.severity=high
# https://prisma.pan.dev/api/cloud/cspm/policy#operation/get-policies-v2

def api_policy_v2_list_filtered_get(pc_settings, query_params="policy.severity=high"):
    action = "GET"
    url = "https://" + pc_settings['apiBase'] + "/v2/policy?" + query_params
    return pc_call_api(action, url, pc_settings)
