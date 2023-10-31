#!/usr/bin/env python3
import yaml
import copy
from mumc_modules.mumc_versions import get_semantic_version_parts,get_script_version
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_compare_items import keys_exist,return_key_value
from mumc_modules.mumc_config_updater import yaml_configurationUpdater
from mumc_modules.mumc_console_info import print_config_options_added_warning,print_config_options_removed_warning
from mumc_modules.mumc_yaml_edits import add_minium_age_to_yaml,add_query_filter_to_yaml,add_dynamic_behavior_to_yaml


def cfgCheckYAML_Version(cfg,init_dict):
    config_version=get_semantic_version_parts(cfg['version'])
    min_config_version=get_semantic_version_parts(init_dict['min_config_version'])

    config_version_ok=True
    if ((not (config_version['major'] >= min_config_version['major'])) or
        (not (config_version['minor'] >= min_config_version['minor'])) or
        (not (config_version['patch'] >= min_config_version['patch']))):
        config_version_ok=False

    if (not (config_version_ok)):
        return 'ConfigVersionError: Config version: ' + cfg['version'] + ' is not supported by script version: '\
                + init_dict['script_version'] + '\n Please use a config with a version greater than: '\
                + init_dict['min_config_version'] + ' or create a new config \n'
    else:
        return ''

#Check blacklist and whitelist config variables are as expected
def cfgCheckYAML_forLibraries(check_list, user_id_check_list, user_name_check_list, config_var_name):

    error_found_in_mumc_config_yaml=''

    for check_irt in check_list:
        #Check if user_id exists
        if ('user_id' in check_irt):
            #Set user tracker to zero
            user_found=0
            #Check user from user_keys is also a user in this blacklist/whitelist
            for user_check in user_id_check_list:
                if (user_check in check_irt['user_id']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' user_id ' + check_irt['user_id'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' user_id ' + check_irt['user_id'] + ' is seen more than once\n'
            #Check user_id is string
            if not (isinstance(check_irt['user_id'], str)):
                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' the user_id is not a string for at least one user\n'
            else:
                #Check user_id is 32 character long alphanumeric
                if not (
                    (check_irt['user_id'].isalnum()) and
                    (len(check_irt['user_id']) == 32)
                ):
                    error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' + at least one user_id is not a 32-character alphanumeric string\n'
        else:
            error_found_in_mumc_config_yaml+='NameError: In ' + config_var_name + ' the user_id key is missing for at least one user\n'


        #Check if user_name exists
        if ('user_name' in check_irt):
            #Set user tracker to zero
            user_found=0
            #Check user from user_name is also a user in this blacklist/whitelist
            for user_check in user_name_check_list:
                if (user_check in check_irt['user_name']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' user_name ' + check_irt['user_name'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' user_name ' + check_irt['user_name'] + ' is seen more than once\n'
            #Check user_name is string
            if not (isinstance(check_irt['user_name'], str)):
                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' the user_name is not a string for at least one user\n'
        else:
            error_found_in_mumc_config_yaml+='NameError: In ' + config_var_name + ' the user_name is missing for at least one user\n'

        #Check if whitelist exists
        if ('whitelist' in check_irt):
            #Check whitelist is string
            if not (isinstance(check_irt['whitelist'], list)):
                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' the whitelist is not a string for at least one user\n'
        else:
            error_found_in_mumc_config_yaml+='NameError: In ' + config_var_name + ' the whitelist is missing for at least one user\n'

        #Check if blacklist exists
        if ('blacklist' in check_irt):
            #Check blacklist is string
            if not (isinstance(check_irt['blacklist'], list)):
                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' the blacklist is not a string for at least one user\n'
        else:
            error_found_in_mumc_config_yaml+='NameError: In ' + config_var_name + ' the blacklist is missing for at least one user\n'

        #Get number of elements
        for num_elements in check_irt:
            #Ignore user_id and user_name
            #Check whitelist and blacklist only if they are not empty lists
            if (((not (num_elements == 'user_id')) and (not (num_elements == 'user_name'))) and (((num_elements == 'whitelist') or (num_elements == 'blacklist')) and check_irt[num_elements])):
                #Set library key trackers to zero
                lib_id_found=0
                collection_type_found=0
                path_found=0
                network_path_found=0
                lib_enabled_found=0
                #Check if this num_element exists before proceeding
                if (num_elements in check_irt):
                    for libinfo in check_irt[num_elements]:
                        if ('lib_id' in libinfo):
                            lib_id_found += 1
                            check_item=check_irt[num_elements][int(check_irt[num_elements].index(libinfo))]['lib_id']
                            #Check lib_id is alphanumeric string
                            if (not (check_item.isalnum() or check_item.isnumeric() or (check_item == ''))):
                                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + num_elements + ' > lib_id: ' + str(check_item) + ' is not an expected string value\n'

                        if ('collection_type' in libinfo):
                            collection_type_found += 1
                            check_item=check_irt[num_elements][int(check_irt[num_elements].index(libinfo))]['collection_type']
                            #Check collection_type is string
                            if (not (isinstance(check_item,str) or (check_item == ''))):
                                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + num_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > collection_type: ' + str(check_item) + ' is not an expected string value\n'

                        if ('path' in libinfo):
                            path_found += 1
                            check_item=check_irt[num_elements][int(check_irt[num_elements].index(libinfo))]['path']
                            #Check path is string
                            if (not ((isinstance(check_item,str) and check_item.find('\\') < 0) or (check_item == ''))):
                                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + num_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > path: ' + str(check_item) + ' is not an expected string value\n'

                        if ('network_path' in libinfo):
                            network_path_found += 1
                            check_item=check_irt[num_elements][int(check_irt[num_elements].index(libinfo))]['network_path']
                            #Check network_path is string
                            if (not ((isinstance(check_item,str) and check_item.find('\\') < 0) or (check_item == '') or (check_item == None))):
                                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + num_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > network_path: ' + str(check_item) + ' is not an expected string value\n'

                        if ('lib_enabled' in libinfo):
                            lib_enabled_found += 1
                            check_item=check_irt[num_elements][int(check_irt[num_elements].index(libinfo))]['lib_enabled']
                            #Check lib_enabled is boolean
                            if (not (isinstance(check_item,bool))):
                                error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + num_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > enabled: ' + str(check_item) + ' is not an expected boolean value\n'

                    if (lib_id_found == 0):
                        error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key lib_id is missing\n'

                    if (collection_type_found == 0):
                        error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key collection_type is missing\n'

                    if (network_path_found == 0):
                        error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key network_path is missing\n'

                    if (path_found == 0):
                        error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key path is missing\n'

                    if (lib_enabled_found == 0):
                        error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key lib_enabled is missing\n'

                else:
                    error_found_in_mumc_config_yaml+='ValueError: ' + config_var_name + ' user ' + check_irt['user_id'] + ' key'+ str(num_elements) +' does not exist\n'
    return(error_found_in_mumc_config_yaml)


#Check select config variables are as expected
def cfgCheckYAML(cfg,init_dict):

    #Todo: find clean way to put cfg.variable_names in a dict/list/etc... and use the dict/list/etc... to call the varibles by name in a for loop

    #DELETE config_dict{} not used for anything
    config_dict={}

    #Start as blank error string
    error_found_in_mumc_config_yaml=''

#######################################################################################################

    if (keys_exist(cfg,'admin_settings','server','brand')):
        check=return_key_value(cfg,'admin_settings','server','brand')
        server_brand=check
        if (
            not ((isinstance(check,str)) and
            ((check.casefold() == 'emby') or (check.casefold() == 'jellyfin')))
        ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > server > brand must be a string with a value of \'emby\' or \'jellyfin\'\n'
            server_brand='invalid'
        else:
            config_dict['server_brand']=check.casefold()
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > server > brand key is missing from mumc_config.yaml\n'
        server_brand='invalid'

#######################################################################################################

    #Setup for known variables that could be missing from config
    minimum_age_missing_bool=False
    missing_minimum_age_dict={}
    missing_minimum_age_dict['admin_settings']={}
    missing_minimum_age_dict['admin_settings']['cache']={}
    missing_minimum_age_dict['admin_settings']['cache']['minimum_age']=None

    query_filter_missing_bool=False
    missing_query_filter_dict={}
    missing_query_filter_dict['advanced_settings']={}
    missing_query_filter_dict['advanced_settings']['filter_statements']={}
    missing_query_filter_dict['advanced_settings']['filter_statements']['movie']={}
    missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']={}
    missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['favorited']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['whitetagged']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['blacktagged']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['episode']={}
    missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']={}
    missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['favorited']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['whitetagged']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['blacktagged']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['audio']={}
    missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']={}
    missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['favorited']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['whitetagged']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['blacktagged']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']=None
    missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']=None
    if (isJellyfinServer(server_brand)):
        missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']={}
        missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']={}
        missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['favorited']=None
        missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitetagged']=None
        missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacktagged']=None
        missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']=None
        missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']=None

    dynamic_behavior_missing_bool=False
    missing_dynamic_behavior_dict={}
    missing_dynamic_behavior_dict['advanced_settings']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['favorited']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['favorited']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['favorited']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']=None
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']={}
    missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']=None
    if (isJellyfinServer(server_brand)):
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']={}
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']={}
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']=None
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']={}
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=None
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']={}
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']=None
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']={}
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']=None
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']={}
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']=None

#######################################################################################################

    error_found_in_mumc_config_yaml+=cfgCheckYAML_Version(cfg,init_dict)

#######################################################################################################

    if (keys_exist(cfg,'version')):
        check=return_key_value(cfg,'version')
        check_parts=get_semantic_version_parts(check)
        if (
            not ((isinstance(check,str)) and
            (isinstance(check_parts['major'],int)) and
            (isinstance(check_parts['minor'],int)) and
            (isinstance(check_parts['patch'],int)) and
            (isinstance(check_parts['release'],str)))
        ):
            error_found_in_mumc_config_yaml+='ConfigValueError: version must be in the semantic versioning syntax\n\tFormatted as shown: MAJOR.MINOR.PATCH (e.g. 111.22.3)'
        else:
            config_dict['config_version']=check
            config_dict['config_version_parts']=check_parts
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The version key is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'admin_settings','server','url')):
        check=return_key_value(cfg,'admin_settings','server','url')
        server_url=check
        if (
            not (isinstance(check,str))
        ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > server > url must be a string\n'
        else:
            config_dict['server_url']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > server > url key is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'admin_settings','server','auth_key')):
        check=return_key_value(cfg,'admin_settings','server','auth_key')
        server_auth_key=check
        if (
            not ((isinstance(check,str)) and (check.isalnum()))
        ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > server > auth_key must be a string\n'
        else:
            config_dict['auth_key']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > server > auth_key key is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'admin_settings','users')):
        check=return_key_value(cfg,'admin_settings','users')
        user_id_check_list=[]
        check_dict_user_name={}
        for entry in check:
            for user_data in entry:
                if (user_data == 'user_id'):
                    user_id_check_list.append(entry[user_data])
                    check_dict_user_name[entry[user_data]]=entry['user_name']
        check_user_keys_length=len(user_id_check_list)
        user_id_user_id_check_list=[]
        if (check_user_keys_length > 0):
            for user_info in user_id_check_list:
                user_id_user_id_check_list.append(user_info)
                for check_irt in user_id_user_id_check_list:
                    if (
                        not ((isinstance(user_id_check_list,list)) and
                            (isinstance(check_irt,str)) and
                            (len(check_irt) == 32) and
                            (str(check_irt).isalnum()))
                    ):
                        error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > users > user_id there must be an entry for each monitored user\n\tEach user key must be a 32-character alphanumeric string\n'
            else:
                config_dict['user_keys']=user_id_check_list
        else:
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > users > user_id cannot be empty\n'
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: admin_settings > users > user_id is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'admin_settings','users')):
        check=return_key_value(cfg,'admin_settings','users')
        check_list=[]
        for entry in check:
            for user_data in entry:
                if (user_data == 'user_name'):
                    check_list.append(entry[user_data])
        check_user_names_length=len(check_list)
        user_name_check_list=[]
        if (check_user_names_length > 0):
            for user_info in check_list:
                user_name_check_list.append(user_info)
                for check_irt in user_name_check_list:
                    if (
                        not ((isinstance(check_list,list)) and
                            (isinstance(check_irt,str)))
                    ):
                        error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > users > user_name there must be an entry for each monitored user\n\tEach user\'s name must be a string\n'
            else:
                config_dict['user_names']=check_dict_user_name
        else:
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > users > user_name cannot be empty\n'
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: admin_settings > users > user_name is missing from mumc_config.yaml\n'

#######################################################################################################

    config_dict['played_filter_movie']=[]

    if (keys_exist(cfg,'basic_settings','filter_statements','movie','played','condition_days')):
        check=return_key_value(cfg,'basic_settings','filter_statements','movie','played','condition_days')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > movie > played > condition_days must be an integer\n\tValid range -1 thru 730500\n'
        else:
            config_dict['played_filter_movie'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > movie > played > condition_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','movie','played','count_equality')):
        check=return_key_value(cfg,'basic_settings','filter_statements','movie','played','count_equality')
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > movie > played > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'
        else:
            config_dict['played_filter_movie'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > movie > played > count_equality is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','movie','played','count')):
        check=return_key_value(cfg,'basic_settings','filter_statements','movie','played','count')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (not (check == 0)) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > movie > played > count must be an integer\n\tValid range -1 and 1 thru 730500\n'
        else:
            config_dict['played_filter_movie'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > movie > played > count is missing from mumc_config.yaml\n'

    config_dict['created_filter_movie']=[]

    if (keys_exist(cfg,'basic_settings','filter_statements','movie','created','condition_days')):
        check=return_key_value(cfg,'basic_settings','filter_statements','movie','created','condition_days')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > movie > created > condition_days must be an integer\n\tValid range -1 thru 730500\n'
        else:
            config_dict['created_filter_movie'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > movie > created > condition_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','movie','created','count_equality')):
        check=return_key_value(cfg,'basic_settings','filter_statements','movie','created','count_equality')
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > movie > created > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'
        else:
            config_dict['created_filter_movie'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > movie > created > count_equality is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','movie','created','count')):
        check=return_key_value(cfg,'basic_settings','filter_statements','movie','created','count')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > movie > created > count must be an integer\n\tValid range -1 thru 730500\n'
        else:
            config_dict['created_filter_movie'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > movie > created > count is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','movie','created','behavioral_control')):
        check=return_key_value(cfg,'basic_settings','filter_statements','movie','created','behavioral_control')
        if (
            not (isinstance(check,bool) and
                 (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > movie > created > behavioral_control must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['created_filter_movie'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > movie > created > behavioral_control is missing from mumc_config.yaml\n'

    config_dict['played_filter_episode']=[]

    if (keys_exist(cfg,'basic_settings','filter_statements','episode','played','condition_days')):
        check=return_key_value(cfg,'basic_settings','filter_statements','episode','played','condition_days')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > episode > played > condition_days must be an integer\n\tValid range -1 thru 730500\n'
        else:
            config_dict['played_filter_episode'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > episode > played > condition_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','episode','played','count_equality')):
        check=return_key_value(cfg,'basic_settings','filter_statements','episode','played','count_equality')
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > episode > played > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'
        else:
            config_dict['played_filter_episode'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > episode > played > count_equality is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','episode','played','count')):
        check=return_key_value(cfg,'basic_settings','filter_statements','episode','played','count')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (not (check == 0)) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > episode > played > count must be an integer\n\tValid range -1 and 1 thru 730500\n'
        else:
            config_dict['played_filter_episode'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > episode > played > count is missing from mumc_config.yaml\n'

    config_dict['created_filter_episode']=[]

    if (keys_exist(cfg,'basic_settings','filter_statements','episode','created','condition_days')):
        check=return_key_value(cfg,'basic_settings','filter_statements','episode','created','condition_days')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > episode > created > condition_days must be an integer\n\tValid range -1 thru 730500\n'
        else:
            config_dict['created_filter_episode'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > episode > created > condition_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','episode','created','count_equality')):
        check=return_key_value(cfg,'basic_settings','filter_statements','episode','created','count_equality')
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > episode > created > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'
        else:
            config_dict['created_filter_episode'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > episode > created > count_equality is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','episode','created','count')):
        check=return_key_value(cfg,'basic_settings','filter_statements','episode','created','count')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > episode > created > count must be an integer\n\tValid range -1 thru 730500\n'
        else:
            config_dict['created_filter_episode'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > episode > created > count is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','episode','created','behavioral_control')):
        check=return_key_value(cfg,'basic_settings','filter_statements','episode','created','behavioral_control')
        if (
            not (isinstance(check,bool) and
                 (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > episode > created > behavioral_control must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['created_filter_episode'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > episode > created > behavioral_control is missing from mumc_config.yaml\n'

    config_dict['played_filter_audio']=[]

    if (keys_exist(cfg,'basic_settings','filter_statements','audio','played','condition_days')):
        check=return_key_value(cfg,'basic_settings','filter_statements','audio','played','condition_days')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audio > played > condition_days must be an integer\n\tValid range -1 thru 730500\n'
        else:
            config_dict['played_filter_audio']=[]
            config_dict['played_filter_audio'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audio > played > condition_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','audio','played','count_equality')):
        check=return_key_value(cfg,'basic_settings','filter_statements','audio','played','count_equality')
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audio > played > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'
        else:
            config_dict['played_filter_audio'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audio > played > count_equality is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','audio','played','count')):
        check=return_key_value(cfg,'basic_settings','filter_statements','audio','played','count')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (not (check == 0)) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audio > played > count must be an integer\n\tValid range -1 and 1 thru 730500\n'
        else:
            config_dict['played_filter_audio'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audio > played > count is missing from mumc_config.yaml\n'

    config_dict['created_filter_audio']=[]

    if (keys_exist(cfg,'basic_settings','filter_statements','audio','created','condition_days')):
        check=return_key_value(cfg,'basic_settings','filter_statements','audio','created','condition_days')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audio > created > condition_days must be an integer\n\tValid range -1 thru 730500\n'
        else:
            config_dict['created_filter_audio'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audio > created > condition_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','audio','created','count_equality')):
        check=return_key_value(cfg,'basic_settings','filter_statements','audio','created','count_equality')
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audio > created > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'
        else:
            config_dict['created_filter_audio'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audio > created > count_equality is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','audio','created','count')):
        check=return_key_value(cfg,'basic_settings','filter_statements','audio','created','count')
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audio > created > count must be an integer\n\tValid range -1 thru 730500\n'
        else:
            config_dict['created_filter_audio'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audio > created > count is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'basic_settings','filter_statements','audio','created','behavioral_control')):
        check=return_key_value(cfg,'basic_settings','filter_statements','audio','created','behavioral_control')
        if (
            not (isinstance(check,bool) and
                 (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audio > created > behavioral_control must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['created_filter_audio'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audio > created > behavioral_control is missing from mumc_config.yaml\n'

    if (isJellyfinServer(server_brand)):
        config_dict['played_filter_audiobook']=[]

        if (keys_exist(cfg,'basic_settings','filter_statements','audiobook','played','condition_days')):
            check=return_key_value(cfg,'basic_settings','filter_statements','audiobook','played','condition_days')
            if (
                not (isinstance(check,int) and
                    (check >= -1) and (check <= 730500))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audiobook > played > condition_days must be an integer\n\tValid range -1 thru 730500\n'
            else:
                config_dict['played_filter_audiobook']=[]
                config_dict['played_filter_audiobook'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audiobook > played > condition_days is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'basic_settings','filter_statements','audiobook','played','count_equality')):
            check=return_key_value(cfg,'basic_settings','filter_statements','audiobook','played','count_equality')
            if (
                not (isinstance(check,str) and
                    ((check == '>') or (check == '<') or
                    (check == '>=') or (check == '<=') or
                    (check == '==') or (check == 'not ==') or
                    (check == 'not >') or (check == 'not <') or
                    (check == 'not >=') or (check == 'not <=')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audiobook > played > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'
            else:
                config_dict['played_filter_audiobook'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audiobook > played > count_equality is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'basic_settings','filter_statements','audiobook','played','count')):
            check=return_key_value(cfg,'basic_settings','filter_statements','audiobook','played','count')
            if (
                not (isinstance(check,int) and
                    (check >= -1) and (not (check == 0)) and (check <= 730500))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audiobook > played > count must be an integer\n\tValid range -1 and 1 thru 730500\n'
            else:
                config_dict['played_filter_audiobook'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audiobook > played > count is missing from mumc_config.yaml\n'

        config_dict['created_filter_audiobook']=[]

        if (keys_exist(cfg,'basic_settings','filter_statements','audiobook','created','condition_days')):
            check=return_key_value(cfg,'basic_settings','filter_statements','audiobook','created','condition_days')
            if (
                not (isinstance(check,int) and
                    (check >= -1) and (check <= 730500))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audiobook > created > condition_days must be an integer\n\tValid range -1 thru 730500\n'
            else:
                config_dict['created_filter_audiobook'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audiobook > created > condition_days is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'basic_settings','filter_statements','audiobook','created','count_equality')):
            check=return_key_value(cfg,'basic_settings','filter_statements','audiobook','created','count_equality')
            if (
                not (isinstance(check,str) and
                    ((check == '>') or (check == '<') or
                    (check == '>=') or (check == '<=') or
                    (check == '==') or (check == 'not ==') or
                    (check == 'not >') or (check == 'not <') or
                    (check == 'not >=') or (check == 'not <=')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audiobook > created > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'
            else:
                config_dict['created_filter_audiobook'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audiobook > created > count_equality is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'basic_settings','filter_statements','audiobook','created','count')):
            check=return_key_value(cfg,'basic_settings','filter_statements','audiobook','created','count')
            if (
                not (isinstance(check,int) and
                    (check >= -1) and (check <= 730500))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audiobook > created > count must be an integer\n\tValid range -1 thru 730500\n'
            else:
                config_dict['created_filter_audiobook'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audiobook > created > count is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'basic_settings','filter_statements','audiobook','created','behavioral_control')):
            check=return_key_value(cfg,'basic_settings','filter_statements','audiobook','created','behavioral_control')
            if (
                not (isinstance(check,bool) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > behavioral_statements > audiobook > created > behavioral_control must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['created_filter_audiobook'].insert(3,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: basic_settings > behavioral_statements > audiobook > created > behavioral_control is missing from mumc_config.yaml\n'

#######################################################################################################

    config_dict['query_filter_movie']=[]

    if (keys_exist(cfg,'advanced_settings','filter_statements','movie','query_filter','favorited')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','movie','query_filter','favorited')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter > favorited must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_movie'].insert(0,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['favorited']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > movie > query_filter > favorited is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['favorited']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','movie','query_filter','whitetagged')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','movie','query_filter','whitetagged')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter > whitetagged must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_movie'].insert(1,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['whitetagged']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > movie > query_filter > whitetagged is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['whitetagged']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','movie','query_filter','blacktagged')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','movie','query_filter','blacktagged')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter > blacktagged must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_movie'].insert(2,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['blacktagged']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > movie > query_filter > blacktagged is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['blacktagged']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','movie','query_filter','whitelisted')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','movie','query_filter','whitelisted')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter > whitelisted must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_movie'].insert(3,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > movie > query_filter > whitelisted is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','movie','query_filter','blacklisted')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','movie','query_filter','blacklisted')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter > blacklisted must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_movie'].insert(4,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > movie > query_filter > blacklisted is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']=True

    config_dict['query_filter_episode']=[]

    if (keys_exist(cfg,'advanced_settings','filter_statements','episode','query_filter','favorited')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','episode','query_filter','favorited')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter > favorited must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_episode'].insert(0,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['favorited']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > episode > query_filter > favorited is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['favorited']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','episode','query_filter','whitetagged')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','episode','query_filter','whitetagged')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter > whitetagged must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_episode'].insert(1,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['whitetagged']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > episode > query_filter > whitetagged is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['whitetagged']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','episode','query_filter','blacktagged')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','episode','query_filter','blacktagged')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter > blacktagged must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_episode'].insert(2,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['blacktagged']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > episode > query_filter > blacktagged is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['blacktagged']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','episode','query_filter','whitelisted')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','episode','query_filter','whitelisted')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter > whitelisted must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_episode'].insert(3,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > episode > query_filter > whitelisted is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','episode','query_filter','blacklisted')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','episode','query_filter','blacklisted')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter > blacklisted must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_episode'].insert(4,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > episode > query_filter > blacklisted is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']=True

    config_dict['query_filter_audio']=[]

    if (keys_exist(cfg,'advanced_settings','filter_statements','audio','query_filter','favorited')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','audio','query_filter','favorited')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > favorited must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_audio'].insert(0,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['favorited']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audio > query_filter > favorited is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['favorited']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','audio','query_filter','whitetagged')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','audio','query_filter','whitetagged')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > whitetagged must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_audio'].insert(1,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['whitetagged']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audio > query_filter > whitetagged is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['whitetagged']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','audio','query_filter','blacktagged')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','audio','query_filter','blacktagged')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > blacktagged must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_audio'].insert(2,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['blacktagged']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audio > query_filter > blacktagged is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['blacktagged']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','audio','query_filter','whitelisted')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','audio','query_filter','whitelisted')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > whitelisted must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_audio'].insert(3,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audio > query_filter > whitelisted is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']=True

    if (keys_exist(cfg,'advanced_settings','filter_statements','audio','query_filter','blacklisted')):
        check=return_key_value(cfg,'advanced_settings','filter_statements','audio','query_filter','blacklisted')
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > blacklisted must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['query_filter_audio'].insert(4,check)
            missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audio > query_filter > blacklisted is missing from mumc_config.yaml\n'
        query_filter_missing_bool=True
        missing_query_filter_dict['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']=True

    if (isJellyfinServer(server_brand)):
        config_dict['query_filter_audiobook']=[]

        if (keys_exist(cfg,'advanced_settings','filter_statements','audiobook','query_filter','favorited')):
            check=return_key_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','favorited')
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > favorited must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['query_filter_audiobook'].insert(0,check)
                missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['favorited']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audiobook > query_filter > favorited is missing from mumc_config.yaml\n'
            query_filter_missing_bool=True
            missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['favorited']=True

        if (keys_exist(cfg,'advanced_settings','filter_statements','audiobook','query_filter','whitetagged')):
            check=return_key_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','whitetagged')
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > whitetagged must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['query_filter_audiobook'].insert(1,check)
                missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitetagged']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audiobook > query_filter > whitetagged is missing from mumc_config.yaml\n'
            query_filter_missing_bool=True
            missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitetagged']=True

        if (keys_exist(cfg,'advanced_settings','filter_statements','audiobook','query_filter','blacktagged')):
            check=return_key_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','blacktagged')
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > blacktagged must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['query_filter_audiobook'].insert(2,check)
                missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacktagged']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audiobook > query_filter > blacktagged is missing from mumc_config.yaml\n'
            query_filter_missing_bool=True
            missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacktagged']=True

        if (keys_exist(cfg,'advanced_settings','filter_statements','audiobook','query_filter','whitelisted')):
            check=return_key_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','whitelisted')
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > whitelisted must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['query_filter_audiobook'].insert(3,check)
                missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audiobook > query_filter > whitelisted is missing from mumc_config.yaml\n'
            query_filter_missing_bool=True
            missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']=True

        if (keys_exist(cfg,'advanced_settings','filter_statements','audiobook','query_filter','blacklisted')):
            check=return_key_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','blacklisted')
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > blacklisted must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['query_filter_audiobook'].insert(4,check)
                missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > filter_statements > audiobook > query_filter > blacklisted is missing from mumc_config.yaml\n'
            query_filter_missing_bool=True
            missing_query_filter_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']=True

    config_dict['favorited_behavior_movie']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','favorited','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['favorited_behavior_movie'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > favorited > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','favorited','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
        else:
            config_dict['favorited_behavior_movie'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > favorited > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','favorited','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['favorited_behavior_movie'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > favorited > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','favorited','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['favorited_behavior_movie'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > favorited > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','favorited','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['favorited_behavior_movie'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > favorited > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']=False

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','favorited','extra','genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','extra','genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > advanced > genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_movie_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > favorited > advanced > genre is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','favorited','extra','library_genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','extra','library_genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > extra > library_genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_movie_library_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > favorited > extra > library_genre is missing from mumc_config.yaml\n'

    config_dict['whitetagged_behavior_movie']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['whitetagged_behavior_movie'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitetagged > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > user_conditional must be a string\n\tValid value \'all\'\n'
        else:
            config_dict['whitetagged_behavior_movie'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitetagged > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['whitetagged_behavior_movie'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitetagged > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['whitetagged_behavior_movie'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitetagged > action_control is missing from mumc_config.yaml\n'

    config_dict['movie_whitetag']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['whitetagged_behavior_movie'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitetagged > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']=False

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','tags')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','tags')
        for tag in check:
            if (
                not (((isinstance(tag,str)) and
                    (tag.find('\\') < 0)) or
                    (tag == None))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > tags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
            else:
                if (not (tag == None)):
                    config_dict['movie_whitetag'].append(tag)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitetagged > tags is missing from mumc_config.yaml\n'

    config_dict['blacktagged_behavior_movie']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['blacktagged_behavior_movie'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacktagged > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > user_conditional must be a string\n\tValid value \'all\'\n'
        else:
            config_dict['blacktagged_behavior_movie'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacktagged > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['blacktagged_behavior_movie'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacktagged > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['blacktagged_behavior_movie'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacktagged > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['blacktagged_behavior_movie'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacktagged > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']=False

    config_dict['movie_blacktag']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','tags')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','tags')
        for tag in check:
            if (
                not (((isinstance(tag,str)) and
                    (tag.find('\\') < 0)) or
                    (tag == None))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > tags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
            else:
                if (not (tag == None)):
                    config_dict['movie_blacktag'].append(tag)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacktagged > tags is missing from mumc_config.yaml\n'

    config_dict['whitelisted_behavior_movie']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitelisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['whitelisted_behavior_movie'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitelisted > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitelisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
        else:
            config_dict['whitelisted_behavior_movie'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitelisted > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitelisted > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['whitelisted_behavior_movie'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitelisted > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitelisted > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['whitelisted_behavior_movie'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitelisted > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitelisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['whitelisted_behavior_movie'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > whitelisted > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']=False

    config_dict['blacklisted_behavior_movie']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacklisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['blacklisted_behavior_movie'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacklisted > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacklisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
        else:
            config_dict['blacklisted_behavior_movie'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacklisted > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacklisted > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['blacklisted_behavior_movie'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacklisted > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacklisted > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['blacklisted_behavior_movie'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacklisted > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacklisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['blacklisted_behavior_movie'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > movie > blacklisted > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']=False

    config_dict['favorited_behavior_episode']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['favorited_behavior_episode'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
        else:
            config_dict['favorited_behavior_episode'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['favorited_behavior_episode'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['favorited_behavior_episode'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['favorited_behavior_episode'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']=False

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_episode_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > advanced > genre is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','season_genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','season_genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > season_genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_season_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > advanced > season_genre is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','series_genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','series_genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > series_genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_series_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > advanced > series_genre is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','library_genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','library_genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > extra > library_genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_tv_library_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > extra > library_genre is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','studio_network')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','studio_network')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > studio_network must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_tv_studio_network']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > advanced > studio_network is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','studio_network_genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','studio_network_genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > studio_network_genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_tv_studio_network_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > favorited > advanced > studio_network_genre is missing from mumc_config.yaml\n'

    config_dict['whitetagged_behavior_episode']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['whitetagged_behavior_episode'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitetagged > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > user_conditional must be a string\n\tValid value \'all\'\n'
        else:
            config_dict['whitetagged_behavior_episode'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitetagged > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['whitetagged_behavior_episode'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitetagged > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['whitetagged_behavior_episode'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitetagged > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['whitetagged_behavior_episode'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitetagged > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']=False

    config_dict['episode_whitetag']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','tags')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','tags')
        for tag in check:
            if (
                not (((isinstance(tag,str)) and
                    (tag.find('\\') < 0)) or
                    (tag == None))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > tags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
            else:
                if (not (tag == None)):
                    config_dict['episode_whitetag'].append(tag)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitetagged > tags is missing from mumc_config.yaml\n'

    config_dict['blacktagged_behavior_episode']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['blacktagged_behavior_episode'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacktagged > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > user_conditional must be a string\n\tValid value \'all\'\n'
        else:
            config_dict['blacktagged_behavior_episode'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacktagged > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['blacktagged_behavior_episode'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacktagged > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['blacktagged_behavior_episode'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacktagged > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['blacktagged_behavior_episode'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacktagged > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']=False

    config_dict['episode_blacktag']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','tags')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','tags')
        for tag in check:
            if (
                not (((isinstance(tag,str)) and
                    (tag.find('\\') < 0)) or
                    (tag == None))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > tags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
            else:
                if (not (tag == None)):
                    config_dict['episode_blacktag'].append(tag)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacktagged > tags is missing from mumc_config.yaml\n'

    config_dict['whitelisted_behavior_episode']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitelisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['whitelisted_behavior_episode'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitelisted > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitelisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
        else:
            config_dict['whitelisted_behavior_episode'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitelisted > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitelisted > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['whitelisted_behavior_episode'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitelisted > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitelisted > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['whitelisted_behavior_episode'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitelisted > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitelisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['whitelisted_behavior_episode'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > whitelisted > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']=False

    config_dict['blacklisted_behavior_episode']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacklisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['blacklisted_behavior_episode'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacklisted > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacklisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
        else:
            config_dict['blacklisted_behavior_episode'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacklisted > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacklisted > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['blacklisted_behavior_episode'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacklisted > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacklisted > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['blacklisted_behavior_episode'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacklisted > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacklisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['blacklisted_behavior_episode'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > episode > blacklisted > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']=False

    config_dict['favorited_behavior_audio']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['favorited_behavior_audio'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
        else:
            config_dict['favorited_behavior_audio'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['favorited_behavior_audio'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['favorited_behavior_audio'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['favorited_behavior_audio'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']=False

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > advanced > genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_track_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > advanced > genre is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','album_genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','album_genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > advanced > album_genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_album_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > advanced > album_genre is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','library_genre')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','library_genre')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > extra > library_genre must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_music_library_genre']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > extra > library_genre is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','track_artist')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','track_artist')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > advanced > track_artist must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_track_artist']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > advanced > track_artist is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','album_artist')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','album_artist')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > advanced > album_artist must be an integer\n\tValid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_album_artist']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > favorited > advanced > album_artist is missing from mumc_config.yaml\n'

    config_dict['whitetagged_behavior_audio']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['whitetagged_behavior_audio'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitetagged > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > user_conditional must be a string\n\tValid value \'all\'\n'
        else:
            config_dict['whitetagged_behavior_audio'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitetagged > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['whitetagged_behavior_audio'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitetagged > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['whitetagged_behavior_audio'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitetagged > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['whitetagged_behavior_audio'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitetagged > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']=False

    config_dict['audio_whitetag']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','tags')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','tags')
        for tag in check:
            if (
                not (((isinstance(tag,str)) and
                    (tag.find('\\') < 0)) or
                    (tag == None))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > tags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
            else:
                if (not (tag == None)):
                    config_dict['audio_whitetag'].append(tag)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitetagged > tags is missing from mumc_config.yaml\n'

    config_dict['blacktagged_behavior_audio']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['blacktagged_behavior_audio'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacktagged > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > user_conditional must be a string\n\tValid value \'all\'\n'
        else:
            config_dict['blacktagged_behavior_audio'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacktagged > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['blacktagged_behavior_audio'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacktagged > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['blacktagged_behavior_audio'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacktagged > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['blacktagged_behavior_audio'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacktagged > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']=False

    config_dict['audio_blacktag']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','tags')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','tags')
        for tag in check:
            if (
                not (((isinstance(tag,str)) and
                    (tag.find('\\') < 0)) or
                    (tag == None))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > tags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
            else:
                if (not (tag == None)):
                    config_dict['audio_blacktag'].append(tag)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacktagged > tags is missing from mumc_config.yaml\n'

    config_dict['whitelisted_behavior_audio']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitelisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['whitelisted_behavior_audio'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitelisted > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitelisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
        else:
            config_dict['whitelisted_behavior_audio'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitelisted > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitelisted > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['whitelisted_behavior_audio'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitelisted > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitelisted > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['whitelisted_behavior_audio'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitelisted > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitelisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['whitelisted_behavior_audio'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > whitelisted > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']=False

    config_dict['blacklisted_behavior_audio']=[]

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','action')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','action')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacklisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            config_dict['blacklisted_behavior_audio'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacklisted > action_days is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','user_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','user_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacklisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
        else:
            config_dict['blacklisted_behavior_audio'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacklisted > user_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','played_conditional')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','played_conditional')
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                 (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                 (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                 (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                 (check.casefold() == 'ignore')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacklisted > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
        else:
            config_dict['blacklisted_behavior_audio'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacklisted > played_conditional is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','action_control')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','action_control')
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacklisted > action_control must be an integer\n\tValid range 0 thru 8\n'
        else:
            config_dict['blacklisted_behavior_audio'].insert(3,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacklisted > action_control is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','dynamic_behavior')):
        check=return_key_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','dynamic_behavior')
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacklisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'
        else:
            config_dict['blacklisted_behavior_audio'].insert(4,check)
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']=check
    else:
        #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audio > blacklisted > dynamic_behavior is missing from mumc_config.yaml\n'
        dynamic_behavior_missing_bool=True
        missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']=False

    if (isJellyfinServer(server_brand)):
        config_dict['favorited_behavior_audiobook']=[]

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','action')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','action')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
            else:
                config_dict['favorited_behavior_audiobook'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > action_days is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','user_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','user_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'any') or (check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
            else:
                config_dict['favorited_behavior_audiobook'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > user_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','played_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','played_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                    (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                    (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                    (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                    (check.casefold() == 'ignore')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
            else:
                config_dict['favorited_behavior_audiobook'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > played_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','action_control')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','action_control')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > action_control must be an integer\n\tValid range 0 thru 8\n'
            else:
                config_dict['favorited_behavior_audiobook'].insert(3,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > action_control is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','dynamic_behavior')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','dynamic_behavior')
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > dynamic_behavior must be an boolean\n\tValid values True or False\n'
            else:
                config_dict['favorited_behavior_audiobook'].insert(4,check)
                missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > dynamic_behavior is missing from mumc_config.yaml\n'
            dynamic_behavior_missing_bool=True
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']=False

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','genre')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','genre')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > genre must be an integer\n\tValid range 0 thru 2\n'
            else:
                config_dict['favorited_advanced_audiobook_track_genre']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > genre is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','audiobook_genre')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','audiobook_genre')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > audiobook_genre must be an integer\n\tValid range 0 thru 2\n'
            else:
                config_dict['favorited_advanced_audiobook_genre']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > audiobook_genre is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','library_genre')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','library_genre')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > extra > library_genre must be an integer\n\tValid range 0 thru 2\n'
            else:
                config_dict['favorited_advanced_audiobook_library_genre']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > extra > library_genre is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','track_author')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','track_author')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > track_author must be an integer\n\tValid range 0 thru 2\n'
            else:
                config_dict['favorited_advanced_audiobook_track_author']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > track_author is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','author')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','author')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > author must be an integer\n\tValid range 0 thru 2\n'
            else:
                config_dict['favorited_advanced_audiobook_author']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > author is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','library_author')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','library_author')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > library_author must be an integer\n\tValid range 0 thru 2\n'
            else:
                config_dict['favorited_advanced_audiobook_library_author']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > library_author is missing from mumc_config.yaml\n'

        config_dict['whitetagged_behavior_audiobook']=[]

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','action')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','action')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
            else:
                config_dict['whitetagged_behavior_audiobook'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitetagged > action_days is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','user_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','user_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > user_conditional must be a string\n\tValid value \'all\'\n'
            else:
                config_dict['whitetagged_behavior_audiobook'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitetagged > user_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','played_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','played_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                    (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                    (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                    (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                    (check.casefold() == 'ignore')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
            else:
                config_dict['whitetagged_behavior_audiobook'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitetagged > played_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','action_control')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','action_control')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > action_control must be an integer\n\tValid range 0 thru 8\n'
            else:
                config_dict['whitetagged_behavior_audiobook'].insert(3,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitetagged > action_control is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','dynamic_behavior')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','dynamic_behavior')
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'
            else:
                config_dict['whitetagged_behavior_audiobook'].insert(4,check)
                missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitetagged > dynamic_behavior is missing from mumc_config.yaml\n'
            dynamic_behavior_missing_bool=True
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=False

        config_dict['audiobook_whitetag']=[]

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','tags')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','tags')
            for tag in check:
                if (
                    not (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > tags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        config_dict['audiobook_whitetag'].append(tag)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitetagged > tags is missing from mumc_config.yaml\n'

        config_dict['blacktagged_behavior_audiobook']=[]

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','action')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','action')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
            else:
                config_dict['blacktagged_behavior_audiobook'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacktagged > action_days is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','user_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','user_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > user_conditional must be a string\n\tValid value \'all\'\n'
            else:
                config_dict['blacktagged_behavior_audiobook'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacktagged > user_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','played_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','played_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                    (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                    (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                    (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                    (check.casefold() == 'ignore')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
            else:
                config_dict['blacktagged_behavior_audiobook'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacktagged > played_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','action_control')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','action_control')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > action_control must be an integer\n\tValid range 0 thru 8\n'
            else:
                config_dict['blacktagged_behavior_audiobook'].insert(3,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacktagged > action_control is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','dynamic_behavior')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','dynamic_behavior')
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'
            else:
                config_dict['blacktagged_behavior_audiobook'].insert(4,check)
                missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacktagged > dynamic_behavior is missing from mumc_config.yaml\n'
            dynamic_behavior_missing_bool=True
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']=False

        config_dict['audiobook_blacktag']=[]

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','dynamic_behavior')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','dynamic_behavior')
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'
            else:
                config_dict['whitetagged_behavior_audiobook'].insert(4,check)
                missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitetagged > dynamic_behavior is missing from mumc_config.yaml\n'
            dynamic_behavior_missing_bool=True
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=False

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','tags')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','tags')
            for tag in check:
                if (
                    not (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > tags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        config_dict['audiobook_blacktag'].append(tag)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacktagged > tags is missing from mumc_config.yaml\n'

        config_dict['whitelisted_behavior_audiobook']=[]

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','action')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','action')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitelisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
            else:
                config_dict['whitelisted_behavior_audiobook'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitelisted > action_days is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','user_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','user_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'any') or (check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitelisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
            else:
                config_dict['whitelisted_behavior_audiobook'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitelisted > user_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','played_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','played_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                    (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                    (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                    (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                    (check.casefold() == 'ignore')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitelisted > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
            else:
                config_dict['whitelisted_behavior_audiobook'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitelisted > played_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','action_control')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','action_control')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitelisted > action_control must be an integer\n\tValid range 0 thru 8\n'
            else:
                config_dict['whitelisted_behavior_audiobook'].insert(3,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitelisted > action_control is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','dynamic_behavior')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','dynamic_behavior')
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitelisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'
            else:
                config_dict['whitelisted_behavior_audiobook'].insert(4,check)
                missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > whitelisted > dynamic_behavior is missing from mumc_config.yaml\n'
            dynamic_behavior_missing_bool=True
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']=False

        config_dict['blacklisted_behavior_audiobook']=[]

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','action')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','action')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacklisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
            else:
                config_dict['blacklisted_behavior_audiobook'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacklisted > action_days is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','user_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','user_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'any') or (check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacklisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
            else:
                config_dict['blacklisted_behavior_audiobook'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacklisted > user_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','played_conditional')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','played_conditional')
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                 (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                    (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                    (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                    (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                    (check.casefold() == 'ignore')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacklisted > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
            else:
                config_dict['blacklisted_behavior_audiobook'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacklisted > played_conditional is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','action_control')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','action_control')
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacklisted > action_control must be an integer\n\tValid range 0 thru 8\n'
            else:
                config_dict['blacklisted_behavior_audiobook'].insert(3,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacklisted > action_control is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','dynamic_behavior')):
            check=return_key_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','dynamic_behavior')
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacklisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'
            else:
                config_dict['blacklisted_behavior_audiobook'].insert(4,check)
                missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']=check
        else:
            #error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > behavioral_statements > audiobook > blacklisted > dynamic_behavior is missing from mumc_config.yaml\n'
            dynamic_behavior_missing_bool=True
            missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']=False

#######################################################################################################

    config_dict['whitetag']=[]

    if (keys_exist(cfg,'advanced_settings','whitetags')):
        check=return_key_value(cfg,'advanced_settings','whitetags')
        for tag in check:
            if (
                not (((isinstance(tag,str)) and
                    isinstance(check,list) and
                    (tag.find('\\') < 0)) or
                    (tag == None))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > whitetags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
            else:
                if (not (tag == None)):
                    config_dict['whitetag'].append(tag)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > whitetags is missing from mumc_config.yaml\n'

    config_dict['blacktag']=[]

    if (keys_exist(cfg,'advanced_settings','blacktags')):
        check=return_key_value(cfg,'advanced_settings','blacktags')
        for tag in check:
            if (
                not (((isinstance(tag,str)) and
                    isinstance(check,list) and
                    (tag.find('\\') < 0)) or
                    (tag == None))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > blacktags must be a list of strings\n\tBacklashes \'\\\' are not an allowed character\n'
            else:
                if (not (tag == None)):
                    config_dict['blacktag'].append(tag)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > blacktags is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'advanced_settings','episode_control','minimum_episodes')):
        check=return_key_value(cfg,'advanced_settings','episode_control','minimum_episodes')
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > episode_control > minimum_episodes must be an integer\n\tValid range 0 thru 730500\n'
        else:
            config_dict['minimum_number_episodes']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > episode_control > minimum_episodes variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','episode_control','minimum_played_episodes')):
        check=return_key_value(cfg,'advanced_settings','episode_control','minimum_played_episodes')
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > episode_control > minimum_played_episodes must be an integer\n\tValid range 0 thru 730500\n'
        else:
            config_dict['minimum_number_played_episodes']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > episode_control > minimum_played_episodes variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','episode_control','minimum_episodes_behavior')):
        check=return_key_value(cfg,'advanced_settings','episode_control','minimum_episodes_behavior')
        check=check.casefold()
        usersname_usersid_match=False
        for usersname in user_name_check_list:
            if (check == usersname.casefold()):
                usersname_usersid_match=True
        for usersid in user_id_check_list:
            if (check == usersid.casefold()):
                usersname_usersid_match=True
        if (usersname_usersid_match == False):
            check = check.replace(' ','')
        if (
            not ((isinstance(check,str)) and
                ((usersname_usersid_match == True) or
                (check == 'maxplayed') or
                (check == 'maxplayedmaxplayed') or
                (check == 'minplayed') or
                (check == 'minplayedminplayed') or
                (check == 'maxunplayed') or
                (check == 'maxunplayedmaxunplayed') or
                (check == 'minunplayed') or
                (check == 'minunplayedminunplayed') or
                (check == 'maxplayedmaxunplayed') or
                (check == 'minplayedminunplayed') or
                (check == 'maxplayedminunplayed') or
                (check == 'minplayedmaxunplayed') or
                (check == 'minunplayedminplayed') or
                (check == 'minunplayedmaxunplayed') or
                (check == 'minunplayedmaxplayed') or
                (check == 'minplayedmaxplayed') or
                (check == 'maxunplayedminunplayed') or
                (check == 'maxunplayedminplayed') or
                (check == 'maxunplayedmaxplayed') or
                (check == 'maxplayedminplayed')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > episode_control > minimum_episodes_behavior must be a string\n\tValid values \'User Name\', \'User Id\', and \'Min/Max Played/Unplayed\'\n'
        else:
            config_dict['minimum_number_episodes_behavior']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > episode_control > minimum_episodes_behavior variable is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','movie')):
        check=return_key_value(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','movie')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > trakt_fix > set_missing_last_played_date > movie must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['movie_set_missing_last_played_date']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > trakt_fix > set_missing_last_played_date > movie variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','episode')):
        check=return_key_value(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','episode')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > trakt_fix > set_missing_last_played_date > episode must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['episode_set_missing_last_played_date']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > trakt_fix > set_missing_last_played_date > episode variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','audio')):
        check=return_key_value(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','audio')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > trakt_fix > set_missing_last_played_date > audio must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['audio_set_missing_last_played_date']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > trakt_fix > set_missing_last_played_date > audio variable is missing from mumc_config.yaml\n'

    if (isJellyfinServer(server_brand)):
        if (keys_exist(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','audiobook')):
            check=return_key_value(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','audiobook')
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > trakt_fix > set_missing_last_played_date > audiobook must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['audiobook_set_missing_last_played_date']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > trakt_fix > set_missing_last_played_date > audiobook variable is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','script','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','script','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > script > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_script_header']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > script > show variable is missing from mumc_config.yaml\n'

    config_dict['script_header_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','script','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','script','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > script > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['script_header_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > script > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','script','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','script','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > script > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['script_header_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > script > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','script','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','script','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > script > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['script_header_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > script > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','user','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','user','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > user > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_user_header']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > user > show variable is missing from mumc_config.yaml\n'

    config_dict['user_header_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','user','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','user','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > user > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['user_header_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > user > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','user','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','user','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > user > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superuser, and subuser\n'
        else:
            config_dict['user_header_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > user > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','user','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','user','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > user > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['user_header_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > user > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','summary','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','summary','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > summary > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_summary_header']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > summary > show variable is missing from mumc_config.yaml\n'

    config_dict['summary_header_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','summary','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','summary','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['summary_header_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > summary > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','summary','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','summary','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, supersummary, and subsummary\n'
        else:
            config_dict['summary_header_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > summary > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','headers','summary','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','headers','summary','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['summary_header_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > headers > summary > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','footers','script','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','footers','script','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > footers > script > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_script_footer']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > footers > script > show variable is missing from mumc_config.yaml\n'

    config_dict['script_footer_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','footers','script','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','footers','script','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > footers > script > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['script_footer_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > footers > script > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','footers','script','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','footers','script','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > footers > script > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['script_footer_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > footers > script > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','footers','script','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','footers','script','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > footers > script > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['script_footer_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > footers > script > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','warnings','script','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','warnings','script','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > warnings > script > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_script_warning']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > warnings > script > show variable is missing from mumc_config.yaml\n'

    config_dict['script_warnings_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','warnings','script','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','warnings','script','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > warnings > script > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['script_warnings_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > warnings > script > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','warnings','script','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','warnings','script','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > warnings > script > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['script_warnings_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > warnings > script > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','warnings','script','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','warnings','script','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > warnings > script > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['script_warnings_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > warnings > script > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','delete','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','delete','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > delete > movie > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_movie_delete_info']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > delete > movie > show variable is missing from mumc_config.yaml\n'

    config_dict['movie_delete_info_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','delete','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','delete','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > delete > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['movie_delete_info_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > delete > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','delete','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','delete','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > delete > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['movie_delete_info_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > delete > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','delete','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','delete','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > delete > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['movie_delete_info_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > delete > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','keep','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','keep','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > keep > movie > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_movie_keep_info']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > keep > movie > show variable is missing from mumc_config.yaml\n'

    config_dict['movie_keep_info_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','keep','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','keep','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > keep > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['movie_keep_info_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > keep > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','keep','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','keep','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > keep > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['movie_keep_info_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > keep > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','keep','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','keep','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > keep > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['movie_keep_info_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > keep > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','post_processing','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','post_processing','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > post_processing > movie > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_movie_post_processing_info']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > post_processing > movie > show variable is missing from mumc_config.yaml\n'

    config_dict['movie_post_processing_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','post_processing','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','post_processing','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > post_processing > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['movie_post_processing_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > post_processing > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','post_processing','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','post_processing','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > post_processing > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['movie_post_processing_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > post_processing > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','post_processing','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','post_processing','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > post_processing > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['movie_post_processing_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > post_processing > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','summary','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','summary','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > summary > movie > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_movie_summary']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > summary > movie > show variable is missing from mumc_config.yaml\n'

    config_dict['movie_summary_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','summary','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','summary','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['movie_summary_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > summary > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','summary','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','summary','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['movie_summary_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > summary > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','movie','summary','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','movie','summary','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['movie_summary_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > movie > summary > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','delete','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','delete','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > delete > episode > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_episode_delete_info']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > delete > episode > show variable is missing from mumc_config.yaml\n'

    config_dict['episode_delete_info_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','delete','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','delete','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > delete > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['episode_delete_info_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > delete > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','delete','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','delete','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > delete > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['episode_delete_info_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > delete > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','delete','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','delete','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > delete > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['episode_delete_info_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > delete > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','keep','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','keep','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > keep > episode > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_episode_keep_info']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > keep > episode > show variable is missing from mumc_config.yaml\n'

    config_dict['episode_keep_info_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','keep','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','keep','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > keep > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['episode_keep_info_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > keep > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','keep','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','keep','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > keep > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['episode_keep_info_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > keep > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','keep','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','keep','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > keep > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['episode_keep_info_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > keep > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','post_processing','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','post_processing','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > post_processing > episode > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_episode_post_processing_info']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > post_processing > episode > show variable is missing from mumc_config.yaml\n'

    config_dict['episode_post_processing_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','post_processing','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','post_processing','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > post_processing > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['episode_post_processing_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > post_processing > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','post_processing','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','post_processing','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > post_processing > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['episode_post_processing_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > post_processing > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','post_processing','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','post_processing','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > post_processing > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['episode_post_processing_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > post_processing > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','summary','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','summary','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > summary > episode > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_episode_summary']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > summary > episode > show variable is missing from mumc_config.yaml\n'

    config_dict['episode_summary_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','summary','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','summary','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['episode_summary_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > summary > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','summary','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','summary','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['episode_summary_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > summary > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','episode','summary','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','episode','summary','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['episode_summary_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > episode > summary > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','delete','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','delete','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > delete > audio > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_audio_delete_info']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > delete > audio > show variable is missing from mumc_config.yaml\n'

    config_dict['audio_delete_info_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','delete','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','delete','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > delete > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['audio_delete_info_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > delete > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','delete','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','delete','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > delete > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['audio_delete_info_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > delete > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','delete','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','delete','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > delete > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['audio_delete_info_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > delete > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','keep','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','keep','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > keep > audio > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_audio_keep_info']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > keep > audio > show variable is missing from mumc_config.yaml\n'

    config_dict['audio_keep_info_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','keep','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','keep','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > keep > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['audio_keep_info_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > keep > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','keep','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','keep','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > keep > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['audio_keep_info_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > keep > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','keep','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','keep','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > keep > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['audio_keep_info_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > keep > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','post_processing','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','post_processing','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > post_processing > audio > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_audio_post_processing_info']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > post_processing > audio > show variable is missing from mumc_config.yaml\n'

    config_dict['audio_post_processing_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','post_processing','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','post_processing','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > post_processing > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['audio_post_processing_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > post_processing > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','post_processing','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','post_processing','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > post_processing > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['audio_post_processing_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > post_processing > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','post_processing','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','post_processing','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > post_processing > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['audio_post_processing_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > post_processing > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','summary','show')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','summary','show')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > summary > audio > show must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['print_audio_summary']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > summary > audio > show variable is missing from mumc_config.yaml\n'

    config_dict['audio_summary_format']=[]

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','summary','formatting','font','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','summary','formatting','font','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['audio_summary_format'].insert(0,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > summary > formatting > font > color variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','summary','formatting','font','style')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','summary','formatting','font','style')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
        else:
            config_dict['audio_summary_format'].insert(2,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > summary > formatting > font > style variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'advanced_settings','console_controls','audio','summary','formatting','background','color')):
        check=return_key_value(cfg,'advanced_settings','console_controls','audio','summary','formatting','background','color')
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
        else:
            config_dict['audio_summary_format'].insert(1,check)
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audio > summary > formatting > background > color variable is missing from mumc_config.yaml\n'

    if (isJellyfinServer(server_brand)):
        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','delete','show')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','delete','show')
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > delete > audiobook > show must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['print_audiobook_delete_info']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > delete > audiobook > show variable is missing from mumc_config.yaml\n'

        config_dict['audiobook_delete_info_format']=[]

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','delete','formatting','font','color')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','delete','formatting','font','color')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > delete > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
            else:
                config_dict['audiobook_delete_info_format'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > delete > formatting > font > color variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','delete','formatting','font','style')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','delete','formatting','font','style')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > delete > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
            else:
                config_dict['audiobook_delete_info_format'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > delete > formatting > font > style variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','delete','formatting','background','color')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','delete','formatting','background','color')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > delete > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
            else:
                config_dict['audiobook_delete_info_format'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > delete > formatting > background > color variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','keep','show')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','keep','show')
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > keep > audiobook > show must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['print_audiobook_keep_info']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > keep > audiobook > show variable is missing from mumc_config.yaml\n'

        config_dict['audiobook_keep_info_format']=[]

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','keep','formatting','font','color')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','keep','formatting','font','color')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > keep > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
            else:
                config_dict['audiobook_keep_info_format'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > keep > formatting > font > color variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','keep','formatting','font','style')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','keep','formatting','font','style')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > keep > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
            else:
                config_dict['audiobook_keep_info_format'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > keep > formatting > font > style variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','keep','formatting','background','color')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','keep','formatting','background','color')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > keep > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
            else:
                config_dict['audiobook_keep_info_format'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > keep > formatting > background > color variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','post_processing','show')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','post_processing','show')
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > post_processing > audiobook > show must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['print_audiobook_post_processing_info']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > post_processing > audiobook > show variable is missing from mumc_config.yaml\n'

        config_dict['audiobook_post_processing_format']=[]

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','post_processing','formatting','font','color')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','post_processing','formatting','font','color')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > post_processing > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
            else:
                config_dict['audiobook_post_processing_format'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > post_processing > formatting > font > color variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','post_processing','formatting','font','style')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','post_processing','formatting','font','style')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > post_processing > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
            else:
                config_dict['audiobook_post_processing_format'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > post_processing > formatting > font > style variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','post_processing','formatting','background','color')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','post_processing','formatting','background','color')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > post_processing > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
            else:
                config_dict['audiobook_post_processing_format'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > post_processing > formatting > background > color variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','summary','show')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','summary','show')
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > summary > audiobook > show must be a boolean\n\tValid values are true or false\n'
            else:
                config_dict['print_audiobook_summary']=check
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > summary > audiobook > show variable is missing from mumc_config.yaml\n'

        config_dict['audiobook_summary_format']=[]

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','summary','formatting','font','color')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','summary','formatting','font','color')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
            else:
                config_dict['audiobook_summary_format'].insert(0,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > summary > formatting > font > color variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','summary','formatting','font','style')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','summary','formatting','font','style')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'
            else:
                config_dict['audiobook_summary_format'].insert(2,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > summary > formatting > font > style variable is missing from mumc_config.yaml\n'

        if (keys_exist(cfg,'advanced_settings','console_controls','audiobook','summary','formatting','background','color')):
            check=return_key_value(cfg,'advanced_settings','console_controls','audiobook','summary','formatting','background','color')
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'
            else:
                config_dict['audiobook_summary_format'].insert(1,check)
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > console_controls > audiobook > summary > formatting > background > color variable is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'advanced_settings','UPDATE_CONFIG')):
        check=return_key_value(cfg,'advanced_settings','UPDATE_CONFIG')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > UPDATE_CONFIG must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['UPDATE_CONFIG']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > UPDATE_CONFIG variable is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'advanced_settings','REMOVE_FILES')):
        check=return_key_value(cfg,'advanced_settings','REMOVE_FILES')
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > REMOVE_FILES must be a boolean\n\tValid values are true or false\n'
        else:
            config_dict['REMOVE_FILES']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The advanced_settings > REMOVE_FILES variable is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'admin_settings','behavior','list')):
        check=return_key_value(cfg,'admin_settings','behavior','list')
        if (
            not ((isinstance(check,str)) and
                (check.casefold() == 'whitelist') or (check.casefold() == 'blacklist'))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > behavior > list must be a string\n\tValid values are whitelist or blacklist\n'
        else:
            config_dict['library_setup_behavior']=check.casefold()
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > behavior > list variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'admin_settings','behavior','matching')):
        check=return_key_value(cfg,'admin_settings','behavior','matching')
        if (
            not ((isinstance(check,str)) and
                (check.casefold() == 'byid') or (check.casefold() == 'bypath') or (check.casefold() == 'bynetworkpath'))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > behavior > matching must be a string\n\tValid values are whitelist or blacklist\n'
        else:
            config_dict['library_matching_behavior']=check.casefold()
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > behavior > matching variable is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'admin_settings','users')):
        check=return_key_value(cfg,'admin_settings','users')
        error_found_in_mumc_config_yaml+=cfgCheckYAML_forLibraries(check, user_id_check_list, user_name_check_list, 'admin_settings > users')
        if not (len(check) == check_user_keys_length):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > users Number of configured users does not match the expected value\n'
        else:
            config_dict['user_wl_libs']=check
            config_dict['user_bl_libs']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > behavior > matching variable is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'admin_settings','api_controls','attempts')):
        check=return_key_value(cfg,'admin_settings','api_controls','attempts')
        if (
            not ((isinstance(check,int)) and
                ((check >= 0) and
                (check <= 16)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > api_controls > attempts must be an integer\n\tValid range 0 thru 16\n'
        else:
            config_dict['api_query_attempts']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > api_controls > attempts variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'admin_settings','api_controls','item_limit')):
        check=return_key_value(cfg,'admin_settings','api_controls','item_limit')
        if (
            not ((isinstance(check,int)) and
                ((check >= 0) and
                (check <= 10000)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > api_controls > item_limit must be an integer\n\tValid range 0 thru 10000\n'
        else:
            config_dict['api_query_item_limit']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > api_controls > item_limit variable is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'admin_settings','cache','size')):
        check=return_key_value(cfg,'admin_settings','cache','size')
        if (
            not ((isinstance(check,int)) and
                ((check >= 0) and
                (check <= 10000)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > cache > size must be an integer\n\tValid range 0 thru 10000\n'
        else:
            config_dict['api_query_cache_size']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > cache > size variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'admin_settings','cache','fallback_behavior')):
        check=return_key_value(cfg,'admin_settings','cache','fallback_behavior')
        if (
            not ((isinstance(check,str)) and
                (check.upper() == 'FIFO') or (check.upper() == 'LFU') or (check.upper() == 'LRU'))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > cache > fallback_behavior must be a string\n\tValid values are FIFO, LFU, or LRU\n'
        else:
            config_dict['api_query_cache_fallback_behavior']=check.upper()
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > cache > fallback_behavior variable is missing from mumc_config.yaml\n'

    if (keys_exist(cfg,'admin_settings','cache','minimum_age')):
        check=return_key_value(cfg,'admin_settings','cache','minimum_age')
        if (
            not ((isinstance(check,int)) and
                ((check >= 0) and
                (check <= 60000)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > cache > minimum_age must be an integer\n\tValid range 0 thru 60000\n'
        else:
            config_dict['api_query_cache_minimum_age']=check
    elif (keys_exist(cfg,'admin_settings','cache','last_accessed_time')):
        check=return_key_value(cfg,'admin_settings','cache','last_accessed_time')
        if (
            not ((isinstance(check,int)) and
                ((check >= 0) and
                (check <= 60000)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > cache > last_accessed_time must be an integer\n\tValid range 0 thru 60000\n'
        else:
            config_dict['api_query_cache_minimum_age']=check
            minimum_age_missing_bool=True
            missing_minimum_age_dict['admin_settings']['cache']['minimum_age']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The admin_settings > cache > minimum_age variable is missing from mumc_config.yaml\n'

#######################################################################################################

    if (keys_exist(cfg,'DEBUG')):
        check=return_key_value(cfg,'DEBUG')
        if (
            not ((isinstance(check,int)) and (((check >= 0) and (check <= 4)) or (check == 255)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: DEBUG must be a string\n\tValid range 0 thru 4\n'
        else:
            config_dict['DEBUG']=check
    else:
        error_found_in_mumc_config_yaml+='ConfigNameError: The DEBUG variable is missing from mumc_config.yaml\n'

#######################################################################################################

    #Check for overlapping tags between blacklists and whitelists
    #convert tag lists to new sets
    generic_blacktag_set=set(config_dict['blacktag'])
    generic_whitetag_set=set(config_dict['whitetag'])
    movie_blacktag_set=set(config_dict['movie_blacktag'])
    movie_whitetag_set=set(config_dict['movie_whitetag'])
    episode_blacktag_set=set(config_dict['episode_blacktag'])
    episode_whitetag_set=set(config_dict['episode_whitetag'])
    audio_blacktag_set=set(config_dict['audio_blacktag'])
    audio_whitetag_set=set(config_dict['audio_whitetag'])
    if (isJellyfinServer(server_brand)):
        audiobook_blacktag_set=set(config_dict['audiobook_blacktag'])
        audiobook_whitetag_set=set(config_dict['audiobook_whitetag'])

    #check global blacktags and whitetags do not have a common string
    generic_blacktag_generic_whitetag_common_set=generic_blacktag_set & generic_whitetag_set

    #check global blacktags and media specific whitetags do not have a common string
    generic_blacktag_movie_whitetag_common_set=generic_blacktag_set & movie_whitetag_set
    generic_blacktag_episode_whitetag_common_set=generic_blacktag_set & episode_whitetag_set
    generic_blacktag_audio_whitetag_common_set=generic_blacktag_set & audio_whitetag_set
    if (isJellyfinServer(server_brand)):
        generic_blacktag_audiobook_whitetag_common_set=generic_blacktag_set & audiobook_whitetag_set

    #check global whitetags and media specific blacktags do not have a common string
    generic_whitetag_movie_blacktag_common_set=generic_whitetag_set & movie_blacktag_set
    generic_whitetag_episode_blacktag_common_set=generic_whitetag_set & episode_blacktag_set
    generic_whitetag_audio_blacktag_common_set=generic_whitetag_set & audio_blacktag_set
    if (isJellyfinServer(server_brand)):
        generic_whitetag_audiobook_blacktag_common_set=generic_whitetag_set & audiobook_blacktag_set

    #check media specific blacktags and media specific whitetags do not have a common string
    movie_blacktag_movie_whitetag_common_set=movie_blacktag_set & movie_whitetag_set
    episode_blacktag_set_blacktag_episode_whitetag_common_set=episode_blacktag_set & episode_whitetag_set
    audio_blacktag_audio_whitetag_common_set=audio_blacktag_set & audio_whitetag_set
    if (isJellyfinServer(server_brand)):
        audiobook_blacktag_audiobook_whitetag_common_set=audiobook_blacktag_set & audiobook_whitetag_set

    if (generic_blacktag_generic_whitetag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > whitetags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(generic_blacktag_generic_whitetag_common_set))  + '\n'

    if (generic_blacktag_movie_whitetag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(generic_blacktag_movie_whitetag_common_set))  + '\n'
    if (generic_blacktag_episode_whitetag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(generic_blacktag_episode_whitetag_common_set))  + '\n'
    if (generic_blacktag_audio_whitetag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(generic_blacktag_audio_whitetag_common_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (generic_blacktag_audiobook_whitetag_common_set):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(generic_blacktag_audiobook_whitetag_common_set))  + '\n'

    if (generic_whitetag_movie_blacktag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > movie > blacktagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(generic_whitetag_movie_blacktag_common_set))  + '\n'
    if (generic_whitetag_episode_blacktag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > episode > blacktagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(generic_whitetag_episode_blacktag_common_set))  + '\n'
    if (generic_whitetag_audio_blacktag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audio > blacktagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(generic_whitetag_audio_blacktag_common_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (generic_whitetag_audiobook_blacktag_common_set):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audiobook > blacktagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(generic_whitetag_audiobook_blacktag_common_set))  + '\n'

    if (movie_blacktag_movie_whitetag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > movie > blacktagged > tags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(movie_blacktag_movie_whitetag_common_set))  + '\n'
    if (episode_blacktag_set_blacktag_episode_whitetag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > episode > blacktagged > tags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(episode_blacktag_set_blacktag_episode_whitetag_common_set))  + '\n'
    if (audio_blacktag_audio_whitetag_common_set):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audio > blacktagged > tags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(audio_blacktag_audio_whitetag_common_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (audiobook_blacktag_audiobook_whitetag_common_set):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audiobook > blacktagged > tags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the folowing tags need to be fixed:: ' +  str(list(audiobook_blacktag_audiobook_whitetag_common_set))  + '\n'

#######################################################################################################

#######################################################################################################

    #Bring all errors found to users attention
    if not (error_found_in_mumc_config_yaml == ''):
        if (init_dict['DEBUG']):
            appendTo_DEBUG_log("\n" + error_found_in_mumc_config_yaml,2,init_dict)
        print('\n' + error_found_in_mumc_config_yaml)
        exit(0)

#######################################################################################################

    #Check if known possibly missing config values were found and silently ignored
    if (minimum_age_missing_bool):
        cfg=add_minium_age_to_yaml(missing_minimum_age_dict,init_dict,cfg)

    if (query_filter_missing_bool):
        cfg=add_query_filter_to_yaml(missing_query_filter_dict,init_dict,cfg)

    if (dynamic_behavior_missing_bool):
        cfg=add_dynamic_behavior_to_yaml(missing_dynamic_behavior_dict,server_brand,init_dict,cfg)

    if (minimum_age_missing_bool or query_filter_missing_bool or dynamic_behavior_missing_bool):
        #Update config version
        cfg['version']=get_script_version()
        #Make sure config path is used for the yaml_configurationUpdater()
        cfg['mumc_path']=init_dict['mumc_path']
        cfg['config_file_name_yaml']=init_dict['config_file_name_yaml']
        #Update config yaml with known possible missing config values
        yaml_configurationUpdater(cfg)
        #Update init_dict for later use
        init_dict.update(cfg)

#######################################################################################################
    return cfg