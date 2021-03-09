# pc-toolbox-GCP-extended-edition
Prisma Cloud API tools for convenience and general utility.

There are multiple tools that can be used (listed below).  Everything here is written in Python (2.7, origionally, now updated and tested in Python 3.7, but both should still work).

If you need to install python, you can get more information at [Python's Page](https://www.python.org/).  I also highly recommend you install the [PIP package manager for Python](https://pypi.python.org/pypi/pip) if you do not already have it installed.

To set up your python environment, you will need the following packages:
- requests
- **pandas**

To install/check for this:
```
Python 2.x:
pip install requests --upgrade
pip install pandas

Python 3.x:
pip3 install requests --upgrade
pip3 install pandas 
```

------------------------------------------------------------------
**What's new in this fork (extended edition) compared against the base project?**

This fork is focused more on GCP and requires installation of the popular Pandas open source library. Why Pandas instead of just using something native like CSVwriter to accomplish some of the tasks? If you are unfamiliar with the data analysis/manipulation flexibility provided the Pandas project which has over 27,000 stars, 11,000 forks, and 1,000 watchers (as of December 2020), here's a brief intro from the creators:
"Pandas is a Python package that provides fast, flexible, and expressive data structures designed to make working with "relational" or "labeled" data both easy and intuitive. It aims to be the fundamental high-level building block for doing practical, real world data analysis in Python. Additionally, it has the broader goal of becoming the most powerful and flexible open source data analysis / manipulation tool available in any language. It is already well on its way towards this goal."
- https://pandas.pydata.org/
- https://github.com/pandas-dev/pandas

**Export Scripts [Python 3] for backup and/or automation purposes**:

- **Cloud Accounts** (Main, Level 1, geared towards GCP/AWS. This will grab the 1 top level GCP account and AWS accounts) - pc-cloud-account-main-export.py
- **Cloud Accounts** (Main, Level 2, geared towards GCP. This will export all synced GCP projects found in Prisma) - pc-cloud-account-gcp-projects-CSV-export.py 
- **Cloud Accounts** (Filters items out based on a string within the data frame) - pc-cloud-account-gcp-projects-string-filter-CSV-export.py
- **Account Groups** (Main, export all account groups) - pc-account-groups-names-CSV-export.py 
- **Account Groups** (Filters items out based on string within the data frame) - pc-account-groups-names-string-filter-CSV-export.py
- **User Roles** (Main, export all user roles) - pc-user-role-CSV-export.py
- **User Roles** (Filters items out based on string within the data frame) - pc-user-role-filter-CSV-export.py
--------------------------
- **Access Key List (metadata)** (Export list of access key metadata) - pc-access-key-list-CSV.py
- **Alerts** (Full dump of JSON response, results in over 200+ columns) - pc-alert-get-full-CSV-export.py
- **Alerts** (Lite version, output limited to around 20 columns with RQLs. Geared towards AWS/GCP with ServiceNOW Integration) - pc-alert-get-lite-CSV-export(RQLmode).py
- **Alerts Names** (List of all the created alerts) - pc-alert-names-CSV.py
- **Anomalies Trusted list** (Export existing whitelist) - pc-anomalies-trusted-list-CSV.py
- **Anomalies Settings** (Export Anomaly settings for network and UEBA) - pc-anomalies-settings(UEBA and Network)-CSV.py 
- **Audit Logs** (Export list based on filtered days) - pc-audit-logs-CSV.py
- **Audit Logs, Filter for User** (Export list based on filtered days and user) - pc-audit-logs-filter-CSV.py
- **Notification Templates** (Export notification templates with configs) - pc-notification-templates-CSV.py
- **Policies** (Export all enabled default policies and append the RQL statements) - pc-policy-enabled-CSV-export(with-RQL).py 
- **Policies** (Export all enabled custom default policies and append the RQL statements) - pc-policy-enabled-custom-CSV-export(with-RQL).py
- **Search Recent** (Export all recent searches made on Prisma Cloud, useful for RQL mapping purposes) - pc-search-recent-CSV-export.py
- **Search Saved** (Export all saved searches made on Prisma Cloud, useful for RQL mapping purposes) - pc-search-saved-CSV-export.py
- **Third Party Integrations** (Export list of all integrations) - pc-third-party-integration-CSV.py
- **User List** (List of all users) - pc-user-list-CSV.py
-------------------------------
**Import Scripts [Python 3] for one time usage or continuous automation on Prisma Cloud**:

- **Account Groups Create (CSV, this is for testing before moving to working with just JSON responses on the CRON script.)** (Geared towards GCP, can create 1 or thousands of account groups based on the names of GCP projects. Code uses list from CSV export of Cloud Accounts level 2. Will link up one level to the cloud account of the same name. Next release coming before Thanksgiving 2020, will check for duplicates and only create new entries.) - pc-account-group-bulk-gcp-mapping-CSV-import.py
- **Account Groups Create and Clean up (CRON job using JSON responses)** (Geared towards GCP, can create 1 or thousands of account groups based on the names of GCP projects. Code works off JSON responses. The two API responses are compared (child cloud accounts and account groups), a new list is created with items that will be imported (duplicates are dropped). Will link up one level to the cloud account of the same name). pc-account-group-gcp-mapping-CRON-import.py

- **User Roles Create (CSV, this is for testing before moving to working with just JSON responses on the CRON script.)** (Geared towards GCP, can create 1 or thousands of user roles based on the names of GCP projects. Code uses the list from CSV export of Account Groups filtered. This will also link up one level to the account group of the same name. Next release coming before Thanksgiving 2020, will check for duplicates and only create new entries.) - pc-user-role-bulk-CSV-import.py
- **User Roles Create and Clean Up**  (CRON job using JSON responses)** (Geared towards GCP, can create 1 or thousands of account groups based on the names of GCP projects. Code works off JSON responses. The two API responses are compared (account groups and user roles), a new list is created with items that will be imported (duplicates are dropped). Will link up one level to the account group of the same name). pc-user-role-gcp-mapping-CRON-import.py

- **User Create or Update** (CRON job, pulls in list of GCP users via a custom saved search. Associates GCP users with their specific projects. These projects are represented as roles and account groups using the same name, which takes advantage of the script work done to create account groups and user roles (based on GCP projects, CRON job). If SSO is configured properly on Prisma and hooked to the correct AD group, soon as the users are created, they will have SSO on day 1. Ensure the correct SSO link is provided in welcome emails. This script is the last script in the automation job: 1. child cloud account (native sync to pulling in GCP projects), 2. account groups (created with our scripts, names on based on projects list in child cloud accouts), 3. user roles (created with our scripts, names are based on account groups which use GCP project names), 4. user create or update (created with our scripts, if existing user it updates if new projects are added or removed. Users a hooked to their respective GCP projects (response from SAVED SEARCH, leverages GCP resource manager API). Once created and SSO is enabled, they will be able to log via SSO. pc-user-create-update-CRON-import.py

- **Alerts Dismissals** (Can dismiss 1 or thousands of alerts. Requires the alert IDs to be stored in a column on a CSV called "id", one alert ID per row. Users can leverage the CSV output from the "lite" or "full" GET Alerts scripts above to build a list of IDs needed for this operation.) - pc-alert-bulk-dismiss-from-CSV.py
- **Alerts Reopen** (Can reopen 1 or thousands of alerts. Requires the alert IDs to be stored in a column on a CSV called "id", one alert ID per row. Users can leverage the CSV output from the "lite" or "full" GET Alerts scripts above to build a list of IDs needed for this operation.) -pc-alert-bulk-reopen-from-CSV.py

---------------------------------------------
**Other Notes**:
- **API library file (pc_lib_api.py)**, edited to add in a lot more API calls from: https://api.docs.prismacloud.io/reference#try-the-apis
- **Automation (imports, cron)** Please see 2 import scripts for account groups and user roles, all the work is done in memory instead of from a CSV. 
- **Backups**, today Prisma doesn't offer any method for a user to backup all settings in the UI. Prisma claims they keep some snapshot information on their back-end. The backup scripts should provide some peace of mind to fill the gap, better to be safe than sorry (due to destruction via an automation issue or a nefarious party).
- **Default API Epoch Unix time (displays as scientific notification on CSV)** was converted to time/date (central USA) for scripts.
- **Mirroring GCP environment** when a project is deleted on the GCP, a user should do the same on the Prisma Cloud side (deleting the account group associated with the specific project). Prisma account groups can't be deleted if there's a Prisma role underneath it which has users associated with it. An admin would have to first disassociate Prisma users from the Prisma role. Once this is accomplished, the admin can easily delete the Prisma role or account group tied to the offboarded GCP project. 
- **Pandas**, allows this project to easily exported nested JSONs to CSV once they are normalized and placed into a data frame. Pandas also allows us to do many things like take in multiple JSON responses from the API and map them to each other. Alerts and policies JSON responses don't include RQL queries by default, with Pandas you can append an RQL column succesfully once you map the correct values. Appending an RQL column to an alerts export takes 3 to 4 JSON responses (get alerts, get policies, get saved searches, get recent searches). Since alerts can't map directly to an RQL response (saved or recent search), it requires pulling in the GET POLICIES to complete the association.

---------------------------------------------
**Baseline RBAC Strategy for GCP in Prisma Cloud that organizations should consider:**
Cloud Account (Level 1, GCP) <--> Cloud Account (Level 2, child, lists GCP Projects) <--> Account Groups (Level 3, uses GCP project names) <--> User Role (Level 4 , uses GCP project names) <--> User roles
-Example: GCP <--> GO-DEV-Patriots-12 [level 2] <--> GO-DEV-Patriots-12 [Level 3] <--> GO-DEV-Patriots-12 [Level 4] <--> tom.smith@organization.domain (SSO)
- User (Tom Smith) is given a read-only role (GO-DEV-Patriots-12) that links up to only 1 account group (GO-DEV-Patriots-12), this 1 account group links up to the cloud account of the same name (GO-DEV-Patriots-12). 
---------------------------------
**Coming Soon to the Extended Edition**:
- IaC scripts 
- Compliance report for resources (output in CSV). Stop gap until Prisma offers something natively. Right now only PDFs are offered on Prisma Cloud, reports don't list out resources if it's large. The beta is out and on this repo, the last piece is plugging the associated RQLs to specific policies that are split out (injecting into the cell). 
------------------------------------------------------------------

On to the tools themselves (Everything requires the pc_api_lib.py and pc_lib_general.py library files - keep them in the same directory as the other tools):

**pc-configure.py**
- Use this to set up your Prisma Cloud username, password, and URL for use in the remaining tools.
- REQUIRED - -u switch for the Access Key ID generated from your Prisma Cloud user.
- REQUIRED - -p switch for the Secred Key generated from your Prisma Cloud user.
- REQUIRED - -url switch for the Prisma Cloud UI base URL found in the URL used to access the Prisma Cloud UI (app.prismacloud.io, app2.prismacloud.io, etc.).  This will try to translate from the older redlock.io addresses.  You can also put in the direct api.* link as well.
- Also you can run this without any args to see what Access Key ID and URL is being used.

NOTE: This is stored in clear JSON text in the same folder as the tools.  Keep the resulting conf file protected and do not give it out to anyone.

Example:
```
python pc-configure.py -u "accesskeyidhere" -p "secretkeyhere" -url "app3.prismacloud.io"
```
--------------------------------------------------------------
**pc-alert-get-full-CSV-export.py**
- Grab alerts from Prisma Cloud, this is a full dump with 150+ columns.
- Pandas library is required.
- Specify your parameters in the command-line and run. Results will be saved to a CSV file with the cloud type and time appended to the file name.
- **If your response is large sometimes you will receive a server side 504 error. The only way to handle this issue at the moment is to pull less days or do more filtering.**
- For specific commandline argument filters (outside of what's shown in the example below) just look inside the first block of the code. 

Example:
```
pc-alert-get-full-CSV-export.py -y -fas open -tr 5 --detailed -fct aws
pc-alert-get-full-CSV-export.py -y -fas open -tr 10 --detailed -fct gcp
pc-alert-get-full-CSV-export.py -y -fas open -tr 15 --detailed -fpt anomaly -fct gcp
pc-alert-get-full-CSV-export.py -y -fas open -tr 20 --detailed -fpt config -fct azure
```
**python pc-alert-get-lite-rql.py**
- This code is geared towards GCP and AWS.
- Pandas library is required.
- Grab alerts from Prisma Cloud, this is a lite dump with 15-18 columns (number differs based on whether GCP or AWS is selected).
- Columns found in CSV output can be easily customized with other JSON elements.
- Can handle 90% of the alert filters mentioned in the API: https://api.docs.prismacloud.io/reference#get-alerts-v2
- For specific commandline argument filters (outside of what's shown in the example below) just look inside the first block of the code. 
- Try matrix mode if you want to see all the json responses printed.
- **If your response is large sometimes you will receive a server side 504 error. The only way to handle this issue at the moment is to pull less days or do more filtering.**

Example:
```
python pc-alert-get-lite-CSV-export(RQLmode).py -y -fas open -tr 120 --detailed -fct aws
python pc-alert-get-lite-CSV-export(RQLmode).py -y -fas open -tr 90 --detailed -fct gcp
python pc-alert-get-lite-CSV-export(RQLmode).py -y -fas open -tr 10 --detailed -fpt anomaly -fct gcp
python pc-alert-get-lite-CSV-export(RQLmode).py -y -fas open -tr 10 --detailed -fct aws -fpcs GDPR -y
python pc-alert-get-lite-CSV-export(RQLmode).py -y -fas open -tr 5 --detailed -fct aws --matrixmode
```
**pc-cloud-account-main-export.py**
- Grab top level cloud accounts. 
- On the GCP side this will grab the main account and not the child cloud accounts (which represent projects in Prisma Cloud).

Example:
```
python pc-cloud-account-main-export.py -y
```

**pc-cloud-account-gcp-projects-CSV-export.py**
- Grab the list of GCP projects which are represented in Prisma Cloud as child cloud accounts.
- This will also grab the one GCP top level account. 

Example:
```
python pc-cloud-account-gcp-projects-CSV-export.py  -y
```

**pc-cloud-account-gcp-projects-string-filter-CSV-export.py**
- Grab the list of GCP projects which are represented in Prisma Cloud as child cloud accounts and one top level GCP account.
- This will then filter out the top level account (user must add this account number inside code) to focus on just the projects/child accounts.
- User has the option to add in additional row filters within code (example: remove all projects with sandbox in the string from CSV output).
- Can use the output CSV with the account group import creation script in this project GCP.

Example:
```
python pc-cloud-account-gcp-projects-string-filter-CSV-export.py -y
```

**pc-account-groups-names-CSV-export.py**
- Grab the account groups. 
- If the "accountIds" column shows "[]" that means the cloud account it was linked to above was offboarded. 

Example:
```
python pc-account-groups-names-CSV-export.py -y
```

**pc-account-groups-names-string-filter-CSV-export.py**
- Grab the account groups.
- Within code you can customize the script to filter out specific strings. Filtered items won't show up in the output CSV.
- Can use the output CSV with the user role import creation script from this project. 

Example:
```
python pc-account-groups-names-string-filter-CSV-export.py -y
```

**pc-user-role-CSV-export.py -y**
- Grab list of user roles.


Example:
```
python pc-user-role-CSV-export.py -y
```

**pc-user-role-filter-CSV-export.py**
- Grab list of user roles.
- Within code you can customize the script to filter out specific strings. Filtered items won't show up in the output CSV.

Example:
```
python pc-user-role-filter-CSV-export.py -y
```

**pc-access-key-list-CSV.py**
- Grab list of users issued an access key.

Example:
```
python pc-access-key-list-CSV.py -y
```

**pc-alert-names-CSV.py**
- Grab list of alert names.

Example:
```
python pc-alert-names-CSV.py -y
```

**pc-anomalies-trusted-list-CSV.py**
- Grab anomalies trust list.

Example:
```
python pc-anomalies-trusted-list-CSV.py -y
```

**pc-anomalies-settings(UEBA_and_Network)-CSV.py**
- Grab list of anomaly settings specific to UEBA and Network.

Example:
```
python pc-anomalies-settings(UEBA_and_Network)-CSV.py -y
```

**pc-audit-logs-CSV.py**
- Grab audit logs, specify a time range. 

Example:
```
python pc-audit-logs-CSV.py -tr 20 -y
```

**pc-audit-logs-filter-CSV.py**
- Grab audit logs, specify a time range.
- Filter by user.
- More options coming soon but this is easily customizable to focus on other columns in terms of filtering. 

Example:
```
python pc-audit-logs-filter-CSV.py -tr 20 -uf user@domain.com -y
```

**pc-notification-templates-CSV.py**
- Grab the list of notification templates.

Example:
```
python pc-notification-templates-CSV.py -y
```

**pc-policy-enabled-CSV-export(with-RQL).py**
- Grab the list of enabled polices 
- Use a second JSON response to "saved search" API to map RQLs to policies.
- Use a third JSON response to "recent search" API to map RQLs to policies. 
- Map all and output dataframe to a CSV. 

Example:
```
python pc-policy-enabled-CSV-export(with-RQL).py  -y
```

**pc-policy-enabled-custom-CSV-export(with-RQL).py**
- Grab the list of enabled custom polices 
- Use a second JSON response to "recent search" API to map RQLs to policies. 
- Map all and output dataframe to a CSV. 

Example:
```
python pc-policy-enabled-custom-CSV-export(with-RQL).py -y
```

**pc-search-recent-CSV-export.py**
- Grab recent searches list (RQLs).

Example:
```
python pc-search-recent-CSV-export.py -y
```

**pc-search-saved-CSV-export.py**
- Grab saved searches list (RQLs).

Example:
```
python pc-search-saved-CSV-export.py -y
```

**pc-third-party-integration-CSV.py**
- Grab list of third party integrations. 

Example:
```
python pc-third-party-integration-CSV.py -y
```

**pc-user-list-CSV.py**
- Grab list of users. 

Example:
```
python pc-user-list-CSV.py -y
```

**pc-alert-dismiss.py**
- Dismiss 1 or many alerts using this script alongside a CSV.
- CSV can be a custom one or one from one of our alert dump scripts. 
- CSV must have a column named "id" that has one alert per row. 

Example:
```
python pc-alert-dismiss.py -tr 9 -y sample_with_alert_ids.csv
```

**pc-alert-bulk-reopen-from-CSV.py**
- Reopen 1 or many alerts using this script alongside a CSV.
- CSV can be a custom one or one from one of our alert dump scripts. 
- CSV must have a column named "id" that has one alert per row. 

Example:
```
python pc-alert-bulk-reopen-from-CSV.py -tr 9 -y sample.csv
```

**pc-compliance-report-beta.py**
- Prisma Cloud as of November 2020 doesn't provide a compliance report in CSV format. 
- The PDF version provided by Prisma doesn't list out all the failed resources if it's a large list.
- I am attempting to provide a stop gap solution to the problems above, this is in beta and won't be available until December 2020 (not doing any Prisma coding over Thxgiving Break). 

Example:
```
python pc-compliance-report-beta.py -tr 15 -y
python pc-compliance-report-beta.py -tr 15 -y -fct GCP
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -ss failed
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -ss failed -fagt YOUR_ACCOUNT_GROUP
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -ss failed -fagt YOUR_ACCOUNT_GROUP -fca YOUR_CLOUD_ACCOUNT
python pc-compliance-report-beta.py -tr 15 -y -fct AWS -fpcs "CIS v1.3.0 (AWS)"
python pc-compliance-report-beta.py -tr 15 -y -fct AWS -ss passed
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -fcr "GCP Salt Lake City" -fpcs "GDPR"
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -fcr "GCP Salt Lake City" -fpcs "SOC 2"
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -fcr "GCP Salt Lake City" -fpcs "PCI DSS v3.2"
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -fcr "GCP Salt Lake City" -fpcs "HIPAA"
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -fcr "GCP Salt Lake City" -fpcs "CISv1.1.0 (GKE)"
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -fcr "GCP Salt Lake City" -fpcs "CISv1.1.0 (GCP)"
python pc-compliance-report-beta.py -tr 15 -y -fct GCP -fcr "GCP Salt Lake City" -fpcs "MITRE ATT%26CK [Beta]"
```

**pc-account-group-bulk-gcp-mapping-CSV-import.py**
- Bulk import/creation of account groups using GCP project names listed under cloud accounts child (level 2 in Prisma Cloud, level 1 is cloud accounts and top level GCP account). The cloud account (child) list is pulled from the CSV. Users can utilize the cloud account child backup script (filtered) above to create this CSV
- This is focused on a one time import. 

Example:
```
python pc-account-group-import-bulk-gcp_mapping.py -y sample_with_cloud_account_list_names.csv
```

**pc-account-group-gcp-mapping-CRON-import.py**
- Cron job capability since it uses JSON responses (no output to CSV).
- 2 API calls, child cloud accounts (shows GCP projects) and accounts groups. Does a compare for both, drops duplicates and makes a new dataframe with only new items.
- New account groups are imported (based on dataframe with new items) then created within Prisma Cloud.
- These account groups will hook up one level to a child cloud account (GCP project).
- Error handling is in place, if an item exists in the new dataframe and also already in Prisma Cloud, it will skip this and continue to next item. This sometimes occur because Prisma doesn't update account groups data (using API) if an attached child cloud account is deleted. The pre-work for dataframe creates a new item (ultimately a duplicate) due to a gap between child cloud accounts and account groups on the compare, this will remain the case until Palo provides and update.

Example:
```
python pc-account-group-gcp-mapping-CRON-import.py
```
**pc-user-role-bulk-CSV-import.py**
- Bulk import/creation of user roles using GCP project names listed under account groups. The account groups list is pulled from the CSV. Users can utilize the account groups backup script (filtered) above to create this CSV. 
- This is focused on a one time import. 

Example:
```
python pc-user-role-import-bulk.py -y sample_with_account_group_names.csv
```

**pc-user-role-gcp-mapping-CRON-import.py**
- Cron job capability since it uses JSON responses (no output to CSV).
- 2 API calls, account groups and user roles. Does a compare for both, drops duplicates and makes a new dataframe with only new items.
- New roles are imported (based on dataframe with new items) then created within Prisma Cloud.
- These roles will hook up one level to a account groups.
- Error handling is in place, if an item exists in the new dataframe and also already in Prisma Cloud, it will skip this and continue to next item. 

Example:
```
python pc-user-role-gcp-mapping-CRON-import.py
```
