import json
import os.path
import sys
import csv


# --Description-- #
# Prisma Cloud General Helper library.  Used to contain the general useful shared functions.
# --End Description-- #


# --Configuration-- #
# Settings file name
DEFAULT_SETTINGS_FILE_NAME = "pc-settings.conf"
DEFAULT_SETTINGS_FILE_VERSION = 4


# --End Configuration-- #


# --Helper Methods-- #
# Exit handler (Error)
def pc_exit_error(error_code, error_message=None, system_message=None):
    print(error_code)
    if error_message is not None:
        print(error_message)
    if system_message is not None:
        print(system_message)
    sys.exit(1)


# Exit handler (Success)
def pc_exit_success():
    sys.exit(0)


# Find the correct API Base URL
def pc_find_api_base(ui_base):
    api_base = None
    ui_base_lower = ui_base.lower()
    if ui_base_lower in ['app.redlock.io', 'app.prismacloud.io', 'api.redlock.io']:
        api_base = 'api.prismacloud.io'
    elif ui_base_lower in ['app2.redlock.io', 'app2.prismacloud.io', 'api2.redlock.io']:
        api_base = 'api2.prismacloud.io'
    elif ui_base_lower in ['app3.redlock.io', 'app3.prismacloud.io', 'api3.redlock.io']:
        api_base = 'api3.prismacloud.io'
    elif ui_base_lower in ['app4.redlock.io', 'app4.prismacloud.io', 'api4.redlock.io']:
        api_base = 'api4.prismacloud.io'
    elif ui_base_lower in ['app.eu.redlock.io', 'app.eu.prismacloud.io', 'api.eu.redlock.io']:
        api_base = 'api.eu.prismacloud.io'
    elif ui_base_lower in ['app2.eu.redlock.io', 'app2.eu.prismacloud.io', 'api2.eu.redlock.io']:
        api_base = 'api2.eu.prismacloud.io'
    elif ui_base_lower in ['app.anz.redlock.io', 'app.anz.prismacloud.io', 'api.anz.redlock.io']:
        api_base = 'api.anz.prismacloud.io'
    elif ui_base_lower in ['app.gov.redlock.io', 'app.gov.prismacloud.io', 'api.gov.redlock.io']:
        api_base = 'api.gov.prismacloud.io'
    elif ui_base_lower in ['api.prismacloud.io', 'api2.prismacloud.io', 'api3.prismacloud.io', 'api4.prismacloud.io',
                           'api.eu.prismacloud.io', 'api2.eu.prismacloud.io', 'api.anz.prismacloud.io',
                           'api.gov.prismacloud.io']:
        api_base = ui_base_lower
    else:
        pc_exit_error(400,
                      "API URL Base not found.  Please verify the UI base is accurate.  If it is correct, and you are still getting this message, "
                      "then a new URL was added to the system that this tool does not understand.  Please check for a new version of this tool.")
    return api_base


# Update settings
def pc_settings_upgrade(old_settings):
    if old_settings['settings_file_version'] < DEFAULT_SETTINGS_FILE_VERSION:
        pc_exit_error(400,
                      "Saved settings file is out of date.  Please re-run the pc-settings.py and update your login settings.")
    else:
        pc_exit_error(500,
                      "Something went wrong.  Settings file appears to be outdated, but this tool cannot understand what version it is.  "
                      "Please recreate the settings file or download the latest version of this tool.")
    return old_settings


# Read in settings
def pc_settings_read(settings_file_name=DEFAULT_SETTINGS_FILE_NAME,
                     settings_file_version=DEFAULT_SETTINGS_FILE_VERSION):
    settings_file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), settings_file_name)
    if os.path.isfile(settings_file_name_and_path):
        pc_settings = pc_file_read_json(settings_file_name)
        if pc_settings is None or pc_settings == {}:
            pc_exit_error(500,
                          "The settings file appears to exist, but is empty?  Check the settings file or rerun the pc-configure.py utility.")
        elif pc_settings['settings_file_version'] == settings_file_version:
            return pc_settings
        elif pc_settings['settings_file_version'] < settings_file_version:
            return pc_settings_upgrade(pc_settings)
        else:
            pc_exit_error(500, "The settings file being used is newer than the utility understands.  "
                               "Please recreate the settings file using the pc-configure.py utility or "
                               "update the Prisma Cloud tools in use.")
    else:
        pc_exit_error(400, "Cannot find the pc-settings file.  Please create one using the pc-configure.py utility.")


# Write settings to a file
def pc_settings_write(username, password, uiBase, apiCompute="",
                      settings_file_name=DEFAULT_SETTINGS_FILE_NAME,
                      settings_file_version=DEFAULT_SETTINGS_FILE_VERSION):
    # Verify API Base is understood
    apiBase = pc_find_api_base(uiBase)

    # Write settings file
    new_settings = {}
    new_settings['settings_file_version'] = settings_file_version
    new_settings['username'] = username
    new_settings['password'] = password
    new_settings['apiBase'] = apiBase
    new_settings['apiCompute'] = apiCompute
    new_settings['uiBase'] = uiBase
    pc_file_write_json(settings_file_name, new_settings)


# Work out login information
def pc_login_get(username, password, uibase, apicompute=""):
    pc_settings = {}
    if username is None and password is None and uibase is None:
        pc_settings = pc_settings_read()
    elif username is None or password is None or uibase is None:
        pc_exit_error(400,
                      'Access Key ID (--username), Secret Key (--password), and UI URL Base (--uiurl) are all '
                      'required if using overrides.')
    else:
        pc_settings['username'] = username
        pc_settings['password'] = password
        pc_settings['apiBase'] = pc_find_api_base(uibase)
        pc_settings['apiCompute'] = apicompute
        pc_settings['uiBase'] = uibase
    # Add a placeholder for jwt
    pc_settings['jwt'] = None
    return pc_settings


# Load the CSV file into Dict
def pc_file_load_csv(file_name):
    csv_list = []
    with open(file_name, 'rb') as csv_file:
        file_reader = csv.DictReader(csv_file)
        for row in file_reader:
            csv_list.append(row)
    return csv_list


# Write JSON file
def pc_file_write_json(file_name, data_to_write, file_path=os.path.dirname(os.path.realpath(__file__))):
    file_name_and_path = os.path.join(file_path, file_name)
    try:
        with open(file_name_and_path, 'w') as f:
            json.dump(data_to_write, f)
    except Exception as ex:
        pc_exit_error(500, "Failed to write JSON file.", ex)


# Read JSON file into Dict
def pc_file_read_json(file_name, file_path=os.path.dirname(os.path.realpath(__file__))):
    json_data = None
    file_name_and_path = os.path.join(file_path, file_name)
    try:
        with open(file_name_and_path, 'r') as f:
            json_data = json.load(f)
    except Exception as ex:
        pc_exit_error(500, "Failed to read JSON file.  Check the file name?", ex)
    return json_data


# Write CSV file
def pc_file_write_csv(file_name, data_to_write, file_path=os.path.dirname(os.path.realpath(__file__))):
    file_name_and_path = os.path.join(file_path, file_name)
    try:
        if not os.path.exists(file_path):
            os.mkdir(file_path,750)
        with open(file_name_and_path, 'a') as f:
            f.write(data_to_write + "\n")
        f.close()
    except Exception as ex:
        pc_exit_error(500, "Failed to write CSV file.", ex)

# Load the txt file into List
def pc_file_load_txt(file_name):
    txt_list = []
    with open(file_name) as txt_file:
        txt_list = txt_file.read().splitlines()
    return txt_list

# Check if pc-settings exist

# Read in settings
def pc_settings_exist(settings_file_name=DEFAULT_SETTINGS_FILE_NAME,
                     settings_file_version=DEFAULT_SETTINGS_FILE_VERSION):
    settings_file_name_and_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), settings_file_name)
    return os.path.isfile(settings_file_name_and_path)
