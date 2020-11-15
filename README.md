# pc-toolbox-extended-edition
Prisma Cloud API tools for convenience and general utility.

There are multiple tools that can be used (listed below).  Everything here is written in Python (2.7, origionally, now updated and tested in Python 3.7, but both should still work).

If you need to install python, you can get more information at [Python's Page](https://www.python.org/).  I also highly recommend you install the [PIP package manager for Python](https://pypi.python.org/pypi/pip) if you do not already have it installed.

To set up your python environment, you will need the following packages:
- requests
- **pandas**

To install/check for this:
```
pip install requests --upgrade
pip install pandas
pip3 install pandas 
```

------------------------------------------------------------------
**What's new in this fork (extended edition) compared against the base project?**

[This fork requires installation of the Pandas library (data analysis and manipulation): https://pandas.pydata.org/]

**Export Scripts [Python 3]**:

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
**Import Scripts [Python 3]**:

- **Account Groups** (Geared towards GCP, can create 1 or thousands of account groups based on the names of GCP projects. Code uses list from CSV export of Cloud Accounts level 2. Will link up one level to the cloud account of the same name. Will check for duplicates and only create new entries.) - pc-account-group-import-bulk-gcp_mapping.py
- **User Roles** (Geared towards GCP, can create 1 or thousands of user roles based on the names of GCP projects. Code uses the list from CSV export of Account Groups filtered. This will also link up one level to the account group of the same name. Will check for duplicates and only create new entries.) - pc-user-role-import-bulk.py
- **Alerts Dismissals** (Can dismiss 1 or thousands of alerts. Requires the alert IDs to be stored in a column on a CSV called "id", one alert ID per row. Users can leverage the CSV output from the "lite" or "full" GET Alerts scripts above to build a list of IDs needed for this operation.) - pc-alert-bulk-dismiss-from-CSV.py
- **Alerts Reopen** (Can reopen 1 or thousands of alerts. Requires the alert IDs to be stored in a column on a CSV called "id", one alert ID per row. Users can leverage the CSV output from the "lite" or "full" GET Alerts scripts above to build a list of IDs needed for this operation.) -pc-alert-bulk-reopen-from-CSV.py

---------------------------------------------
**Other Notes**:
- **API library file (pc_lib_api.py)**, edited to add in a lot more API calls from: https://api.docs.prismacloud.io/reference#try-the-apis
- **Automation (imports)** currently works off CSV dumps because the CSVs serve as a guard rail. At my company our Prisma Cloud is treated as "PROD" since we don't have a test account. CSVs at least offer option for the user to double check content before it's imported in (easily a large import). I advocate starting with CSV imports before working strictly with normalized JSON responses stored in dataframes. One JSON mishap on a large import could make things messy (account groups, user roles).
- **Backups**, today Prisma doesn't offer any method for a user to backup all settings in the UI. Prisma claims they keep some snapshot information on their back-end. The backup scripts should provide some peace of mind to fill the gap, better to be safe than sorry (due to destruction via an automation issue or a nefarious party).
- **Cron jobs** for importing and creating user roles and account groups is more effective than a Lamda function/Cloud function. This is due to the sync interval controlled from Palo Alto which makes launching on-demand scripts based on an event pointless. Scripts listed under "exports" above which export CSVs, can easily be ran as a cron job/scheduled task (Windows or Linux) for backup and/or automation purposes. Creating second option for "import" scripts to work only with normalized JSONs stored dataframes (with no output to CSV) to create user roles or account groups.
- **Default API Epoch Unix time (displays as scientific notification on CSV)** was converted to time/date (central USA) for most scripts.
- **Mirroring GCP environment** when a project is deleted on the GCP, a user should do the same on the Prisma Cloud side (deleting the account group associated with the specific project). Prisma account groups can't be deleted if there's a Prisma role underneath it which has users associated with it. An admin would have to first disassociate Prisma users from the Prisma role. Once this is accomplished, the admin can easily delete the Prisma role or account group tied to the offboarded GCP project. 
- **Pandas**, allows this project to easily exported nested JSONs to CSV once they are normalized and placed into a data frame. Pandas also allows us to do many things like take in multiple JSON responses from the API and map them to each other. Alerts and policies JSON responses don't include RQL queries by default, with Pandas you can append an RQL column succesfully once you map the correct values. Appending an RQL column to an alerts export takes 3 to 4 JSON responses (get alerts, get policies, get saved searches, get recent searches). Since alerts can't map directly to an RQL response (saved or recent search), it requires pulling in the GET POLICIES to complete the association.

---------------------------------------------
**Baseline RBAC Strategy for GCP in Prisma Cloud that organizations should consider:**
Cloud Account (Level 1, GCP) <--> Cloud Account (Level 2, child, lists GCP Projects) <--> Account Groups (Level 3, uses GCP project names) <--> User Role (Level 4 , uses GCP project names) <--> User roles
-Example: GCP <--> GO-DEV-Patriots-12 [level 2] <--> GO-DEV-Patriots-12 [Level 3] <--> GO-DEV-Patriots-12 [Level 4] <--> tom.smith@organization.domain (SSO)
- User (Tom Smith) is given a read-only role (GO-DEV-Patriots-12) that links up to only 1 account group (GO-DEV-Patriots-12), this 1 account group links up to the cloud account of the same name (GO-DEV-Patriots-12). 
---------------------------------
**Coming Soon**:
- IaC scripts 
- Compliance report for resources (output in CSV). Stop gap until Prisma offers something natively. Right now only PDF and it doesn't list out resources if large.

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

**pc-policy-status.py**
- Use this to enable/disable policies globally for an account (filtered on policy type).
- It will enable or disable all policies of a given type (or all) for a customer account (global).  This is used primarity for setting up a new environment that wants to begin with everything enabled out of the gate or to update after a large number of new policies have been released.

Example:
```
python pc-policy-status.py config enable
```

**pc-user-import.py**
- Use this to import a list of users from a CSV file.
- It will import the list from CSV then try to check for duplicates before import.

Example:
```
python pc-user-import.py "some user list.csv" "Prisma Cloud user role name for my new users"
```

**pc-compliance-copy.py**
- NOTE: This has been replaced by built in functioanlity.  Use the built in clone function for this purpose.
- Use this to copy an existing Compliance Standard (and related requirements and sections) into a new Compliance Standard.
- It will copy the entire specified standard into the new standard name specified.  Please use the -policy switch to also attempt to add the newly copied standard to all of the existing standards attached policies.
- If you would like to also add a label to a policy object with the new compliance name, use the -label switch.  This will add a label to any policy attached (must be used witht he -policy switch, otherwise it will be ignored).
- Note: The policy attachment is currently having some issues with updating certain built-in policies.  It will simply skip any policies it has an issue updating and give a list on the command line of the ones it has issues with.  This list can then be manually attached to the new standard after the copy completes.

Example:
```
python pc-compliance-copy.py "SOC 2" "SOC 2 Copy" -policy
```

**pc-compliance-export.py**
- Use this to export an existing Compliance Standard (and related requirements and sections) into a file for import later or in another tenant.

Example:
```
python pc-compliance-export.py "SOC 2" "soc2.json"
```

**pc-compliance-import.py**
- Use this to import a saved Compliance Standard (and related requirements and sections) into a new Compliance Standard in Prisma Cloud.
- It will copy the entire specified standard into the new standard name specified.
- If you also wish to have the same policy mappings, please use the -policy switch.  THIS ONLY WORKS WITH DEFAULT BUILT IN POLICIES.  Custom policies are not yet supported (they get dropped from the import).

Example:
```
python pc-compliance-import.py "soc2.json" "SOC 2 Copy" -policy
```

**pc-cloud-account-import-azure.py (in progress)**
- This is the framework for importing a CSV (template in the templates folder) with a list of Azure accounts into Prisma Cloud.
- Note: This is still a work in progress.  Basic import framework is running, but validation of CSV and duplicate name checking has not been implemented yet.

Example:
```
python pc-cloud-account-import-azure.py prisma_cloud_account_import_azure_template.csv
```

**pc-alert-get.py**
- Grab alerts from Prisma Cloud, this is a full dump with 150+ columns.
- Pandas library is required.
- Specify your parameters in the command-line and run. Results will be saved to a CSV file with the cloud type and time appended to the file name.
- If your response is large sometimes you will receive a server side error. The only way to handle this issue at the moment is to pull less days or do more filtering. 

Example:
```
python pc-alert-get.py -y -fas open -tr 120 --detailed -fct aws
python pc-alert-get.py -y -fas open -tr 90 --detailed -fct gcp
python pc-alert-get.py -y -fas open -tr 60 --detailed -fpt anomaly -fct gcp
python pc-alert-get.py -y -fas open -tr 30 --detailed -fpt config -fct azure
```
**pc-alert-get-lite.py**
- This code is geared towards GCP and AWS.
- Pandas library is required.
- Grab alerts from Prisma Cloud, this is a lite dump with 15-18 columns (number differs based on whether GCP or AWS is selected).
- Columns found in CSV output can be easily customized with other JSON elements.

Example:
```
python pc-alert-get-lite.py -y -fas open -tr 120 --detailed -fct aws
python pc-alert-get-lite.py -y -fas open -tr 90 --detailed -fct gcp
python pc-alert-get-lite.py -y -fas open -tr 60 --detailed -fpt anomaly -fct gcp
python pc-alert-get-lite.py -y -fas open -tr 10 --detailed -fct aws -fpcs GDPR -y

**WILL COMPLETE DOCUMENTATION IN DEC 2020 FOR ALL THE NEW SCRIPTS***
