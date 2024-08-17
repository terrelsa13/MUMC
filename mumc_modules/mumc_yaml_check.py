import sys
from mumc_modules.mumc_versions import get_semantic_version_parts
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_compare_items import keys_exist_return_value
from mumc_modules.mumc_tagged import get_isFilterStatementTag


def cfgCheckYAML_Version(cfg,init_dict):

    if (cfg['version'] == ''):
        return 'ConfigVersionError: Config version is blank: \'\''\
                '\n Please use a config with a version greater than or equal to: '\
                + init_dict['min_config_version'] + ' or create a new config \n'
    else:
        config_version=get_semantic_version_parts(cfg['version'])
        min_config_version=get_semantic_version_parts(init_dict['min_config_version'])

        config_version_ok=True

        if (config_version['major'] < min_config_version['major']):
            config_version_ok=False
        else:
            if (config_version['minor'] < min_config_version['minor']):
                config_version_ok=False
            else:
                if (config_version['patch'] < min_config_version['patch']):
                    config_version_ok=False

    if (not (config_version_ok)):
        return 'ConfigVersionError: Config version: ' + cfg['version'] + ' is not supported by script version: '\
                + init_dict['script_version'] + '\n Please use a config with a version greater than or equal to: '\
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
                if (user_check == check_irt['user_id']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user_id ' + check_irt['user_id'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user_id ' + check_irt['user_id'] + ' is seen more than once\n'
            #Check user_id is string
            if (not (isinstance(check_irt['user_id'], str))):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' the user_id is not a string or is not a list for at least one user\n'
            else:
                #Check user_id is 32 character long alphanumeric
                if (not (
                    (check_irt['user_id'].isalnum()) and
                    (len(check_irt['user_id']) == 32)
                )):
                    error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' + at least one user_id is not a 32-character alphanumeric string\n'
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The ' + config_var_name + ' > user_id key is missing for at least one user\n'


        #Check if user_name exists
        if ('user_name' in check_irt):
            #Set user tracker to zero
            user_found=0
            #Check user from user_name is also a user in this blacklist/whitelist
            for user_check in user_name_check_list:
                if (user_check == check_irt['user_name']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user_name ' + check_irt['user_name'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user_name ' + check_irt['user_name'] + ' is seen more than once\n'
            #Check user_name is string
            if (not (isinstance(check_irt['user_name'], str))):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' the user_name is not a string or is not a list for at least one user\n'
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The ' + config_var_name + ' > user_name is missing for at least one user\n'

        #Check if whitelist exists
        if ('whitelist' in check_irt):
            #Check whitelist is string
            if (not (isinstance(check_irt['whitelist'], list))):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' the whitelist is not a string or is not a list for at least one user\n'
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The ' + config_var_name + ' > whitelist is missing for at least one user\n'

        #Check if blacklist exists
        if ('blacklist' in check_irt):
            #Check blacklist is string
            if (not (isinstance(check_irt['blacklist'], list))):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' the blacklist is not a string or is not a list for at least one user\n'
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The ' + config_var_name + ' > blacklist is missing for at least one user\n'

        #Get number of elements
        for user_elements in check_irt:
            #Ignore user_id and user_name
            #Check whitelist and blacklist only if they are not empty lists
            if (((not (user_elements == 'user_id')) and (not (user_elements == 'user_name'))) and (((user_elements == 'whitelist') or (user_elements == 'blacklist')) and check_irt[user_elements])):
                #Set library key trackers to zero
                lib_id_found=0
                collection_type_found=0
                path_found=0
                network_path_found=0
                subfolder_id_found=0
                lib_enabled_found=0
                #Check if this num_element exists before proceeding
                if (user_elements in check_irt):
                    for libinfo in check_irt[user_elements]:
                        if ('lib_id' in libinfo):
                            lib_id_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['lib_id']
                            #Check lib_id is alphanumeric string
                            if (not (isinstance(check_item,str) and (check_item.isalpha() or check_item.isalnum() or check_item.isnumeric()))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > lib_id: ' + str(check_item) + ' is not an expected string value\n'

                        if ('collection_type' in libinfo):
                            collection_type_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['collection_type']
                            #Check collection_type is string
                            if (not (isinstance(check_item,str) or (check_item == ''))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > collection_type: ' + str(check_item) + ' is not an expected string value\n'

                        if ('path' in libinfo):
                            path_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['path']
                            #Check path is string
                            if (not ((isinstance(check_item,str) and check_item.find('\\') < 0) or (check_item == '') or (check_item == None))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > path: ' + str(check_item) + ' is not an expected string value\n'

                        if ('network_path' in libinfo):
                            network_path_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['network_path']
                            #Check network_path is string
                            if (not ((isinstance(check_item,str) and check_item.find('\\') < 0) or (check_item == '') or (check_item == None))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > network_path: ' + str(check_item) + ' is not an expected string value\n'

                        if ('subfolder_id' in libinfo):
                            subfolder_id_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['subfolder_id']
                            #Check subfolder_id is alphanumeric string
                            if (not ((check_item == None) or (isinstance(check_item,str) and (check_item.isalpha() or check_item.isalnum() or check_item.isnumeric())))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > subfolder_id: ' + str(check_item) + ' is not an expected string value. Try adding quotes: \'' + str(check_item) + '\' or null if Jellyfin\n'

                        if ('lib_enabled' in libinfo):
                            lib_enabled_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['lib_enabled']
                            #Check lib_enabled is boolean
                            if (not (isinstance(check_item,bool))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > enabled: ' + str(check_item) + ' is not an expected boolean value\n'

                    if (lib_id_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key lib_id is missing\n'

                    if (collection_type_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key collection_type is missing\n'

                    if (network_path_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key network_path is missing\n'

                    if (path_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key path is missing\n'

                    if (subfolder_id_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key subfolder_id is missing\n'

                    if (lib_enabled_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key lib_enabled is missing\n'

                else:
                    error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user ' + check_irt['user_id'] + ' key'+ str(user_elements) +' does not exist\n'
    return(error_found_in_mumc_config_yaml)


#Check filter_tags are formatted as expected
def cfgCheckYAML_isFilterTag(tag,tag_list):
    
    no_error_found=True
    
    if (
        not (isinstance(tag,str) and isinstance(tag_list,list) and
            (isinstance(tag_list[0],str) and ((tag_list[0] == 'played') or (tag_list[0] == 'created')) and
                isinstance(tag_list[1],int) and ((tag_list[1] >= -1) and (tag_list[1] <= 730500)) and
                isinstance(tag_list[2],str) and
                ((tag_list[2] == '>') or (tag_list[2] == '<') or
                (tag_list[2] == '>=') or (tag_list[2] == '<=') or
                (tag_list[2] == '==') or (tag_list[2] == 'not ==') or
                (tag_list[2] == 'not >') or (tag_list[2] == 'not <') or
                (tag_list[2] == 'not >=') or (tag_list[2] == 'not <=')) and
                isinstance(tag_list[3],int) and ((tag_list[3] >= -1) and (tag_list[3] <= 730500)) and
                ((tag_list[0] == 'played') or ((tag_list[0] == 'created') and isinstance(tag_list[4],bool) and ((tag_list[4] == True) or (tag_list[4] == False)))))
            )
        ):
        no_error_found=False

    return no_error_found


#Check behavioral_tags config variables are as expected
def cfgCheckYAML_isBehavioralTag(cfg,tag,media_type):
    
    error_found_in_mumc_config_yaml=''

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'action')) == None)):
        if (
            not (isinstance(check,str) and
                ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'user_conditional')) == None)):
                if (
                    not (isinstance(check,str) and
                        (check.casefold() == 'all'))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
                else:
                    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'played_conditional')) == None)):
                        if (
                            not (isinstance(check,str) and
                                ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                                (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                                (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                                (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                                (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                                (check.casefold() == 'ignore')))
                            ):
                            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
                        else:
                            if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'action_control')) == None)):
                                if (
                                    not (isinstance(check,int) and
                                        ((check >= 0) and (check <= 8)))
                                    ):
                                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > action_control must be an integer\n\tValid range 0 thru 8\n'
                                else:
                                    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'dynamic_behavior')) == None)):
                                        if (
                                            not (isinstance(check,bool) and
                                                ((check == True) or (check == False)))
                                            ):
                                            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > dynamic_behavior must be an boolean\n\tValid values True or False\n'
                                        else:
                                            if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'high_priority')) == None)):
                                                if (
                                                    not (isinstance(check,bool) and
                                                        ((check == True) or (check == False)))
                                                    ):
                                                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > high_priority must be an boolean\n\tValid values True or False\n'

    return error_found_in_mumc_config_yaml


#Check select config variables are as expected
def cfgCheckYAML(cfg,init_dict):

    #TODO: find clean way to put cfg.variable_names in a dict/list/etc... and use the dict/list/etc... to call the varibles by name in a for loop

    #Start as blank error string
    error_found_in_mumc_config_yaml=''
    filter_tag_formatting_value_url=''

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','server','brand')) == None)):
        server_brand=check
        if (
            not ((isinstance(check,str)) and
            ((check.casefold() == 'emby') or (check.casefold() == 'jellyfin')))
        ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > server > brand must be a string with a value of \'emby\' or \'jellyfin\'\n'
            server_brand='invalid'

#######################################################################################################

    #sets of tags for user later
    filter_movie_whitetag_set=set()
    filter_movie_blacktag_set=set()
    filter_episode_whitetag_set=set()
    filter_episode_blacktag_set=set()
    filter_audio_whitetag_set=set()
    filter_audio_blacktag_set=set()
    if (isJellyfinServer(server_brand)):
        filter_audiobook_whitetag_set=set()
        filter_audiobook_blacktag_set=set()
    movie_whitetag_set=set()
    movie_blacktag_set=set()
    episode_whitetag_set=set()
    episode_blacktag_set=set()
    audio_whitetag_set=set()
    audio_blacktag_set=set()
    if (isJellyfinServer(server_brand)):
        audiobook_whitetag_set=set()
        audiobook_blacktag_set=set()
    global_whitetag_set=set()
    global_blacktag_set=set()

#######################################################################################################

    error_found_in_mumc_config_yaml+=cfgCheckYAML_Version(cfg,init_dict)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'version')) == None)):
        check_parts=get_semantic_version_parts(check)
        if (
            not ((isinstance(check,str)) and
            (isinstance(check_parts['major'],int)) and
            (isinstance(check_parts['minor'],int)) and
            (isinstance(check_parts['patch'],int)) and
            (isinstance(check_parts['release'],str)))
        ):
            error_found_in_mumc_config_yaml+='ConfigValueError: version must be in the semantic versioning syntax\n\tFormatted as shown: MAJOR.MINOR.PATCH (e.g. 1.22.333)'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','server','url')) == None)):
        server_url=check
        if (
            not (isinstance(check,str))
        ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > server > url must be a string\n'

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','server','auth_key')) == None)):
        server_auth_key=check
        if (
            not ((isinstance(check,str)) and (check.isalnum()))
        ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > server > auth_key must be an alphanumeric string\n'

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','server','admin_id')) == None)):
        server_admin_id=check
        if (
            not ((isinstance(check,str)) and (check.isalnum()))
        ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > server > admin_id must be an alphanumeric string\n'

#######################################################################################################
    user_id_check_list=[]
    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','users',0,'user_id')) == None)):
        #user_id_check_list=[]
        check_dict_user_name={}
        check=cfg['admin_settings']['users']
        for entry in check:
            for user_data in entry:
                if (user_data == 'user_id'):
                    user_id_check_list.append(entry[user_data])
                    if (not ((temp_check:=keys_exist_return_value(cfg,'admin_settings','users',0,'user_name')) == None)):
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
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > users > user_id cannot be empty\n'

    user_name_check_list=[]
    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','users',0,'user_name')) == None)):
        check_list=[]
        check=cfg['admin_settings']['users']
        for entry in check:
            for user_data in entry:
                if (user_data == 'user_name'):
                    check_list.append(entry[user_data])
        check_user_names_length=len(check_list)

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
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > users > user_name cannot be empty\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','movie','played','condition_days')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > movie > played > condition_days must be an integer\n\tValid range -1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','movie','played','count_equality')) == None)):
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > movie > played > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','movie','played','count')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= 1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > movie > played > count must be an integer\n\tValid range 1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','movie','created','condition_days')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > movie > created > condition_days must be an integer\n\tValid range -1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','movie','created','count_equality')) == None)):
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > movie > created > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','movie','created','count')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= 0) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > movie > created > count must be an integer\n\tValid range 0 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','movie','created','behavioral_control')) == None)):
        if (
            not (isinstance(check,bool) and
                 (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > movie > created > behavioral_control must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','episode','played','condition_days')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > episode > played > condition_days must be an integer\n\tValid range -1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','episode','played','count_equality')) == None)):
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > episode > played > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','episode','played','count')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= 1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > episode > played > count must be an integer\n\tValid range 1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','episode','created','condition_days')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > episode > created > condition_days must be an integer\n\tValid range -1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','episode','created','count_equality')) == None)):
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > episode > created > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','episode','created','count')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= 0) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > episode > created > count must be an integer\n\tValid range 0 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','episode','created','behavioral_control')) == None)):
        if (
            not (isinstance(check,bool) and
                 (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > episode > created > behavioral_control must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audio','played','condition_days')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audio > played > condition_days must be an integer\n\tValid range -1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audio','played','count_equality')) == None)):
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audio > played > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audio','played','count')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= 1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audio > played > count must be an integer\n\tValid range 1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audio','created','condition_days')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= -1) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audio > created > condition_days must be an integer\n\tValid range -1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audio','created','count_equality')) == None)):
        if (
            not (isinstance(check,str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or (check == 'not ==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audio > created > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audio','created','count')) == None)):
        if (
            not (isinstance(check,int) and
                 (check >= 0) and (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audio > created > count must be an integer\n\tValid range 0 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audio','created','behavioral_control')) == None)):
        if (
            not (isinstance(check,bool) and
                 (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audio > created > behavioral_control must be a boolean\n\tValid values are true or false\n'

    if (isJellyfinServer(server_brand)):

        if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audiobook','played','condition_days')) == None)):
            if (
                not (isinstance(check,int) and
                    (check >= -1) and (check <= 730500))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audiobook > played > condition_days must be an integer\n\tValid range -1 thru 730500\n'

        if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audiobook','played','count_equality')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check == '>') or (check == '<') or
                    (check == '>=') or (check == '<=') or
                    (check == '==') or (check == 'not ==') or
                    (check == 'not >') or (check == 'not <') or
                    (check == 'not >=') or (check == 'not <=')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audiobook > played > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'

        if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audiobook','played','count')) == None)):
            if (
                not (isinstance(check,int) and
                    (check >= 1) and (check <= 730500))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audiobook > played > count must be an integer\n\tValid range 1 thru 730500\n'

        if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audiobook','created','condition_days')) == None)):
            if (
                not (isinstance(check,int) and
                    (check >= -1) and (check <= 730500))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audiobook > created > condition_days must be an integer\n\tValid range -1 thru 730500\n'

        if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audiobook','created','count_equality')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check == '>') or (check == '<') or
                    (check == '>=') or (check == '<=') or
                    (check == '==') or (check == 'not ==') or
                    (check == 'not >') or (check == 'not <') or
                    (check == 'not >=') or (check == 'not <=')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audiobook > created > count_equality must be a string\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n'

        if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audiobook','created','count')) == None)):
            if (
                not (isinstance(check,int) and
                    (check >= 0) and (check <= 730500))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audiobook > created > count must be an integer\n\tValid range 0 thru 730500\n'

        if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_statements','audiobook','created','behavioral_control')) == None)):
            if (
                not (isinstance(check,bool) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_statements > audiobook > created > behavioral_control must be a boolean\n\tValid values are true or false\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','movie','whitetags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (tag == None))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > movie > white_tags > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    if (not (tag == None)):
                        filter_movie_whitetag_set.add(tag)

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','movie','blacktags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (tag == None))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > movie > black_tags > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    if (not (tag == None)):
                        filter_movie_blacktag_set.add(tag)

    '''
    for thisFilterTag in cfg['basic_settings']['filter_tags']['movie']['whitetags']:
        if (tag_list:=get_isFilterStatementTag(thisFilterTag)):
            if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','movie','whitetags',thisFilterTag)) == None)):
                if (cfgCheckYAML_isFilterTag(tag,tag_list)):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > movie > white_tags > ' + thisFilterTag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    filter_movie_whitetag_set.add(thisFilterTag)

    for thisFilterTag in cfg['basic_settings']['filter_tags']['movie']['blacktags']:
        if (tag_list:=get_isFilterStatementTag(thisFilterTag)):
            if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','movie','blacktags',thisFilterTag)) == None)):
                if (cfgCheckYAML_isFilterTag(tag,tag_list)):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > movie > black_tags > ' + thisFilterTag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    filter_movie_blacktag_set.add(thisFilterTag)
    '''

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','episode','whitetags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (tag == None))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > episode > white_tags > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    if (not (tag == None)):
                        filter_episode_whitetag_set.add(tag)

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','episode','blacktags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (tag == None))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > episode > black_tags > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    if (not (tag == None)):
                        filter_episode_blacktag_set.add(tag)

    '''
    for thisFilterTag in cfg['basic_settings']['filter_tags']['episode']['whitetags']:
        if (tag_list:=get_isFilterStatementTag(thisFilterTag)):
            if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','episode','whitetags',thisFilterTag)) == None)):
                if (cfgCheckYAML_isFilterTag(tag,tag_list)):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > episode > white_tags > ' + thisFilterTag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    filter_episode_whitetag_set.add(thisFilterTag)

    for thisFilterTag in cfg['basic_settings']['filter_tags']['episode']['blacktags']:
        if (tag_list:=get_isFilterStatementTag(thisFilterTag)):
            if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','episode','blacktags',thisFilterTag)) == None)):
                if (cfgCheckYAML_isFilterTag(tag,tag_list)):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > episode > black_tags > ' + thisFilterTag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    filter_episode_blacktag_set.add(thisFilterTag)
    '''

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','audio','whitetags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (tag == None))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > audio > white_tags > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    if (not (tag == None)):
                        filter_audio_whitetag_set.add(tag)

    if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','audio','blacktags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (tag == None))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > audio > black_tags > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    if (not (tag == None)):
                        filter_audio_blacktag_set.add(tag)

    '''
    for thisFilterTag in cfg['basic_settings']['filter_tags']['audio']['whitetags']:
        if (tag_list:=get_isFilterStatementTag(thisFilterTag)):
            if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','audio','whitetags',thisFilterTag)) == None)):
                if (cfgCheckYAML_isFilterTag(tag,tag_list)):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > audio > white_tags > ' + thisFilterTag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    filter_audio_whitetag_set.add(thisFilterTag)

    for thisFilterTag in cfg['basic_settings']['filter_tags']['audio']['blacktags']:
        if (tag_list:=get_isFilterStatementTag(thisFilterTag)):
            if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','audio','blacktags',thisFilterTag)) == None)):
                if (cfgCheckYAML_isFilterTag(tag,tag_list)):
                    error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > audio > black_tags > ' + thisFilterTag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    filter_audio_blacktag_set.add(thisFilterTag)
    '''

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','audiobook','whitetags')) == None)):
            if (isinstance(check,list)):
                for tag in check:
                    if (
                        not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                            (tag == None))
                        ):
                        error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > audiobook > white_tags > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                    else:
                        if (not (tag == None)):
                            filter_audiobook_whitetag_set.add(tag)

        if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','audiobook','blacktags')) == None)):
            if (isinstance(check,list)):
                for tag in check:
                    if (
                        not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                            (tag == None))
                        ):
                        error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > audiobook > black_tags > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                    else:
                        if (not (tag == None)):
                            filter_audiobook_blacktag_set.add(tag)

        '''
        for thisFilterTag in cfg['basic_settings']['filter_tags']['audiobook']['whitetags']:
            if (tag_list:=get_isFilterStatementTag(thisFilterTag)):
                if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','audiobook','whitetags',thisFilterTag)) == None)):
                    if (cfgCheckYAML_isFilterTag(tag,tag_list)):
                        error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > audiobook > white_tags > ' + thisFilterTag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                    else:
                        filter_audiobook_whitetag_set.add(thisFilterTag)

        for thisFilterTag in cfg['basic_settings']['filter_tags']['audiobook']['blacktags']:
            if (tag_list:=get_isFilterStatementTag(thisFilterTag)):
                if (not ((check:=keys_exist_return_value(cfg,'basic_settings','filter_tags','audiobook','blacktags',thisFilterTag)) == None)):
                    if (cfgCheckYAML_isFilterTag(tag,tag_list)):
                        error_found_in_mumc_config_yaml+='ConfigValueError: basic_settings > filter_tags > audiobook > black_tags > ' + thisFilterTag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                    else:
                        filter_audiobook_blacktag_set.add(thisFilterTag)
        '''

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','whitelisted','favorited')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  whitelisted > favorited must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','whitelisted','whitetagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  whitelisted > whitetagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','whitelisted','blacktagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  whitelisted > blacktagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','whitelisted','played')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  whitelisted > played must be a boolean\n\tValid values are true or false\n'
    elif (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','whitelisted','whitelisted')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  whitelisted > played must be a boolean\n\tValid values are true or false\n'
        else:
            cfg['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']=cfg['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted'].pop('whitelisted')

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','blacklisted','favorited')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  blacklisted > favorited must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','blacklisted','blacktagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  blacklisted > blacktagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','blacklisted','blacktagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  blacklisted > blacktagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','blacklisted','played')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  blacklisted > played must be a boolean\n\tValid values are true or false\n'
    elif (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','movie','query_filter','blacklisted','blacklisted')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > movie > query_filter >  blacklisted > played must be a boolean\n\tValid values are true or false\n'
        else:
            cfg['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']=cfg['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted'].pop('blacklisted')

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','whitelisted','favorited')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  whitelisted > favorited must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','whitelisted','whitetagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  whitelisted > whitetagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','whitelisted','blacktagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  whitelisted > blacktagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','whitelisted','played')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  whitelisted > played must be a boolean\n\tValid values are true or false\n'
    elif (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','whitelisted','whitelisted')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  whitelisted > played must be a boolean\n\tValid values are true or false\n'
        else:
            cfg['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']=cfg['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted'].pop('whitelisted')

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','blacklisted','favorited')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  blacklisted > favorited must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','blacklisted','blacktagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  blacklisted > blacktagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','blacklisted','blacktagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  blacklisted > blacktagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','blacklisted','played')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  blacklisted > played must be a boolean\n\tValid values are true or false\n'
    elif (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','episode','query_filter','blacklisted','blacklisted')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > episode > query_filter >  blacklisted > played must be a boolean\n\tValid values are true or false\n'
        else:
            cfg['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']=cfg['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted'].pop('blacklisted')

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','whitelisted','favorited')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > whitelisted > favorited must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','whitelisted','whitetagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > whitelisted > whitetagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','whitelisted','blacktagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > whitelisted > blacktagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','whitelisted','played')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > whitelisted > played must be a boolean\n\tValid values are true or false\n'
    elif (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','whitelisted','whitelisted')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > whitelisted > played must be a boolean\n\tValid values are true or false\n'
        else:
            cfg['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']=cfg['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted'].pop('whitelisted')

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','blacklisted','favorited')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > blacklisted > favorited must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','blacklisted','blacktagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > blacklisted > blacktagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','blacklisted','blacktagged')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > blacklisted > blacktagged must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','blacklisted','played')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > blacklisted > played must be a boolean\n\tValid values are true or false\n'
    elif (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audio','query_filter','blacklisted','blacklisted')) == None)):
        if (
            not (isinstance(check,bool))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audio > query_filter > blacklisted > played must be a boolean\n\tValid values are true or false\n'
        else:
            cfg['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']=cfg['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted'].pop('blacklisted')

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','whitelisted','favorited')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > whitelisted > favorited must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','whitelisted','whitetagged')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > whitelisted > whitetagged must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','whitelisted','blacktagged')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > whitelisted > blacktagged must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','whitelisted','played')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > whitelisted > played must be a boolean\n\tValid values are true or false\n'
        elif (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','whitelisted','whitelisted')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > whitelisted > played must be a boolean\n\tValid values are true or false\n'
            else:
                cfg['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']=cfg['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted'].pop('whitelisted')

#######################################################################################################

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','blacklisted','favorited')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > blacklisted > favorited must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','blacklisted','blacktagged')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > blacklisted > blacktagged must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','blacklisted','blacktagged')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > blacklisted > blacktagged must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','blacklisted','played')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > blacklisted > played must be a boolean\n\tValid values are true or false\n'
        elif (not ((check:=keys_exist_return_value(cfg,'advanced_settings','filter_statements','audiobook','query_filter','blacklisted','played')) == None)):
            if (
                not (isinstance(check,bool))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > filter_statements > audiobook > query_filter > blacklisted > played must be a boolean\n\tValid values are true or false\n'
            else:
                cfg['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']=cfg['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted'].pop('blacklisted')

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','extra','genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > advanced > genre must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','favorited','extra','library_genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > favorited > extra > library_genre must be an integer\n\tValid range 0 thru 2\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > user_conditional must be a string\n\tValid value \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitetagged','tags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitetagged > tags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        movie_whitetag_set.add(tag)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > user_conditional must be a string\n\tValid value \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacktagged','tags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacktagged > tags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        movie_blacktag_set.add(tag)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitelisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitelisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitelisted > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','whitelisted','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > whitelisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacklisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacklisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacklisted > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','movie','blacklisted','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > movie > blacklisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > genre must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','season_genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > season_genre must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','series_genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > series_genre must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','library_genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > extra > library_genre must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','studio_network')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > studio_network must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','favorited','extra','studio_network_genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > favorited > advanced > studio_network_genre must be an integer\n\tValid range 0 thru 2\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > user_conditional must be a string\n\tValid value \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitetagged','tags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitetagged > tags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        episode_whitetag_set.add(tag)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > user_conditional must be a string\n\tValid value \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacktagged','tags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacktagged > tags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        episode_blacktag_set.add(tag)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitelisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitelisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitelisted > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','whitelisted','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > whitelisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacklisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacklisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacklisted > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','episode','blacklisted','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > episode > blacklisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > advanced > genre must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','album_genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > advanced > album_genre must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','library_genre')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > extra > library_genre must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','track_artist')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > advanced > track_artist must be an integer\n\tValid range 0 thru 2\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','favorited','extra','album_artist')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 2)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > favorited > advanced > album_artist must be an integer\n\tValid range 0 thru 2\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > user_conditional must be a string\n\tValid value \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitetagged','tags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitetagged > tags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        audio_whitetag_set.add(tag)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > user_conditional must be a string\n\tValid value \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacktagged','tags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacktagged > tags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        audio_blacktag_set.add(tag)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitelisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitelisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitelisted > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','whitelisted','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > whitelisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','action')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacklisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','user_conditional')) == None)):
        if (
            not (isinstance(check,str) and
                 ((check.casefold() == 'any') or (check.casefold() == 'all')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacklisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','played_conditional')) == None)):
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

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','action_control')) == None)):
        if (
            not (isinstance(check,int) and
                 ((check >= 0) and (check <= 8)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacklisted > action_control must be an integer\n\tValid range 0 thru 8\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audio','blacklisted','dynamic_behavior')) == None)):
        if (
            not (isinstance(check,bool) and
                 ((check == True) or (check == False)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audio > blacklisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'

    if (isJellyfinServer(server_brand)):

#######################################################################################################

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','action')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','user_conditional')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'any') or (check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','played_conditional')) == None)):
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

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','action_control')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > action_control must be an integer\n\tValid range 0 thru 8\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','dynamic_behavior')) == None)):
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > dynamic_behavior must be an boolean\n\tValid values True or False\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','genre')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > genre must be an integer\n\tValid range 0 thru 2\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','audiobook_genre')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > audiobook_genre must be an integer\n\tValid range 0 thru 2\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','library_genre')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > extra > library_genre must be an integer\n\tValid range 0 thru 2\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','track_author')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > track_author must be an integer\n\tValid range 0 thru 2\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','author')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > author must be an integer\n\tValid range 0 thru 2\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','favorited','extra','library_author')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 2)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > favorited > advanced > library_author must be an integer\n\tValid range 0 thru 2\n'

#######################################################################################################

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','action')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','user_conditional')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > user_conditional must be a string\n\tValid value \'all\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','played_conditional')) == None)):
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

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','action_control')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > action_control must be an integer\n\tValid range 0 thru 8\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','dynamic_behavior')) == None)):
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','tags')) == None)):
            if (isinstance(check,list)):
                for tag in check:
                    if (
                        not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                            (((isinstance(tag,str)) and
                            (tag.find('\\') < 0)) or
                            (tag == None)))
                        ):
                        error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitetagged > tags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                    else:
                        if (not (tag == None)):
                            audiobook_whitetag_set.add(tag)

#######################################################################################################

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','action')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','user_conditional')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > user_conditional must be a string\n\tValid value \'all\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','played_conditional')) == None)):
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

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','action_control')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > action_control must be an integer\n\tValid range 0 thru 8\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','dynamic_behavior')) == None)):
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitetagged','dynamic_behavior')) == None)):
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > dynamic_behavior must be an boolean\n\tValid values True or False\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacktagged','tags')) == None)):
            if (isinstance(check,list)):
                for tag in check:
                    if (
                        not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                            (((isinstance(tag,str)) and
                            (tag.find('\\') < 0)) or
                            (tag == None)))
                        ):
                        error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacktagged > tags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                    else:
                        if (not (tag == None)):
                            audiobook_blacktag_set.add(tag)

#######################################################################################################

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','action')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitelisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','user_conditional')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'any') or (check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitelisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','played_conditional')) == None)):
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

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','action_control')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitelisted > action_control must be an integer\n\tValid range 0 thru 8\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','whitelisted','dynamic_behavior')) == None)):
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > whitelisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'

#######################################################################################################

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','action')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacklisted > action must be a string\n\tValid values \'delete\' and \'keep\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','user_conditional')) == None)):
            if (
                not (isinstance(check,str) and
                    ((check.casefold() == 'any') or (check.casefold() == 'all')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacklisted > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','played_conditional')) == None)):
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

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','action_control')) == None)):
            if (
                not (isinstance(check,int) and
                    ((check >= 0) and (check <= 8)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacklisted > action_control must be an integer\n\tValid range 0 thru 8\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_statements','audiobook','blacklisted','dynamic_behavior')) == None)):
            if (
                not (isinstance(check,bool) and
                    ((check == True) or (check == False)))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_statements > audiobook > blacklisted > dynamic_behavior must be an boolean\n\tValid values True or False\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags','movie')) == None)):
        if (isinstance(check,dict)):
            for tag in check:
                if (
                    not (cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > movie > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    error_found_in_mumc_config_yaml+=cfgCheckYAML_isBehavioralTag(cfg,tag,'movie')

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags','episode')) == None)):
        if (isinstance(check,dict)):
            for tag in check:
                if (
                    not (cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > episode > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    error_found_in_mumc_config_yaml+=cfgCheckYAML_isBehavioralTag(cfg,tag,'episode')

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags','audio')) == None)):
        if (isinstance(check,dict)):
            for tag in check:
                if (
                    not (cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > audio > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                else:
                    error_found_in_mumc_config_yaml+=cfgCheckYAML_isBehavioralTag(cfg,tag,'audio')

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags','audiobook')) == None)):
            if (isinstance(check,dict)):
                for tag in check:
                    if (
                        not (cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag)))
                        ):
                        error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > audiobook > ' + tag + ' is either formatted incorrectly or has invalid value(s)\n\tValid formatting and values can be found here: ' + filter_tag_formatting_value_url + '\n'
                    else:
                        error_found_in_mumc_config_yaml+=cfgCheckYAML_isBehavioralTag(cfg,tag,'audiobook')

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','whitetags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > whitetags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        global_whitetag_set.add(tag)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','blacktags')) == None)):
        if (isinstance(check,list)):
            for tag in check:
                if (
                    not ((cfgCheckYAML_isFilterTag(tag,get_isFilterStatementTag(tag))) or
                        (((isinstance(tag,str)) and
                        (tag.find('\\') < 0)) or
                        (tag == None)))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > blacktags must be a list of strings or an empty list\n\tBacklashes \'\\\' are not an allowed character\n'
                else:
                    if (not (tag == None)):
                        global_blacktag_set.add(tag)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','delete_empty_folders','episode','season')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > delete_empty_folders > episode > season must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','delete_empty_folders','episode','series')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > delete_empty_folders > episode > series must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','episode_control','minimum_episodes')) == None)):
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > episode_control > minimum_episodes must be an integer\n\tValid range 0 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','episode_control','minimum_played_episodes')) == None)):
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 730500))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > episode_control > minimum_played_episodes must be an integer\n\tValid range 0 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','episode_control','minimum_episodes_behavior')) == None)):
        
        check=check.casefold()
        users_name_users_id_match=False
        for users_name in user_name_check_list:
            if (check == users_name.casefold()):
                users_name_users_id_match=True
        for users_id in user_id_check_list:
            if (check == users_id.casefold()):
                users_name_users_id_match=True
        if (users_name_users_id_match == False):
            check = check.replace(' ','')
        if (
            not ((isinstance(check,str)) and
                ((users_name_users_id_match == True) or
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
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > episode_control > minimum_episodes_behavior must be a string\n\tValid values \'User Name\', \'User Id\', and combinations of \'Min/Max Played/Unplayed\'\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','movie')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > trakt_fix > set_missing_last_played_date > movie must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','episode')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > trakt_fix > set_missing_last_played_date > episode must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','audio')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > trakt_fix > set_missing_last_played_date > audio must be a boolean\n\tValid values are true or false\n'

    if (isJellyfinServer(server_brand)):
        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','trakt_fix','set_missing_last_played_date','audiobook')) == None)):
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > trakt_fix > set_missing_last_played_date > audiobook must be a boolean\n\tValid values are true or false\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','script','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > script > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','script','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > script > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','script','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > script > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','script','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > script > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','user','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > user > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','user','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > user > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','user','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > user > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superuser, and subuser\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','user','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > user > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','summary','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > summary > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','summary','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','summary','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, supersummary, and subsummary\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','headers','summary','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > headers > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','footers','script','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > footers > script > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','footers','script','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > footers > script > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','footers','script','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > footers > script > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','footers','script','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > footers > script > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','warnings','script','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > warnings > script > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','warnings','script','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > warnings > script > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','warnings','script','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > warnings > script > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','warnings','script','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > warnings > script > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','delete','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > delete > movie > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','delete','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > delete > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','delete','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > delete > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','delete','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > delete > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','keep','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > keep > movie > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','keep','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > keep > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','keep','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > keep > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','keep','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > keep > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','post_processing','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > post_processing > movie > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','post_processing','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > post_processing > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','post_processing','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > post_processing > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','post_processing','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > post_processing > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','summary','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > summary > movie > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','summary','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','summary','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','movie','summary','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > movie > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','delete','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > delete > episode > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','delete','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > delete > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','delete','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > delete > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','delete','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > delete > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','keep','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > keep > episode > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','keep','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > keep > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','keep','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > keep > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','keep','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > keep > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','post_processing','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > post_processing > episode > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','post_processing','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > post_processing > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','post_processing','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > post_processing > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','post_processing','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > post_processing > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','summary','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > summary > episode > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','summary','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','summary','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','episode','summary','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > episode > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','delete','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > delete > audio > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','delete','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > delete > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','delete','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > delete > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','delete','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > delete > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','keep','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > keep > audio > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','keep','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > keep > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','keep','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > keep > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','keep','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > keep > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','post_processing','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > post_processing > audio > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','post_processing','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > post_processing > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','post_processing','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > post_processing > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','post_processing','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > post_processing > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','summary','show')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > summary > audio > show must be a boolean\n\tValid values are true or false\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','summary','formatting','font','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','summary','formatting','font','style')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audio','summary','formatting','background','color')) == None)):
        if (
            not (((isinstance(check,str)) or (check == None) or (check == '')) and
                ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audio > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

    if (isJellyfinServer(server_brand)):
        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','delete','show')) == None)):
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > delete > audiobook > show must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','delete','formatting','font','color')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > delete > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','delete','formatting','font','style')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > delete > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','delete','formatting','background','color')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > delete > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','keep','show')) == None)):
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > keep > audiobook > show must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','keep','formatting','font','color')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > keep > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','keep','formatting','font','style')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > keep > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','keep','formatting','background','color')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > keep > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','post_processing','show')) == None)):
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > post_processing > audiobook > show must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','post_processing','formatting','font','color')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > post_processing > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','post_processing','formatting','font','style')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > post_processing > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','post_processing','formatting','background','color')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > post_processing > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','summary','show')) == None)):
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or (check == False))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > summary > audiobook > show must be a boolean\n\tValid values are true or false\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','summary','formatting','font','color')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > summary > formatting > font > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','summary','formatting','font','style')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > summary > formatting > font > style must be a string\n\tValid values are bold, faint, italic, underline, slow blink, fast blink, swap, conceal, strikethrough, default, fraktur, double underline, reveal, frame, encircle, overline, ideogram underline, ideogram double underline, ideogram overline, ideogram double overline, ideogram stress mark, superscript, and subscript\n'

        if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','console_controls','audiobook','summary','formatting','background','color')) == None)):
            if (
                not (((isinstance(check,str)) or (check == None) or (check == '')) and
                    ((isinstance(init_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check),int)) or (check == None) or (check == '')))
                ):
                error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > console_controls > audiobook > summary > formatting > background > color must be a string\n\tValid values are black, red, green, yellow, blue, magenta, cyan, white, default, bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, and bright white\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','UPDATE_CONFIG')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > UPDATE_CONFIG must be a boolean\n\tValid values are true or false\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','REMOVE_FILES')) == None)):
        if (
            not ((isinstance(check,bool)) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > REMOVE_FILES must be a boolean\n\tValid values are true or false\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','behavior','list')) == None)):
        if (
            not ((isinstance(check,str)) and
                (check.casefold() == 'whitelist') or (check.casefold() == 'blacklist'))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > behavior > list must be a string\n\tValid values are whitelist or blacklist\n'

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','behavior','matching')) == None)):
        if (
            not ((isinstance(check,str)) and
                (check.casefold() == 'byid') or (check.casefold() == 'bypath') or (check.casefold() == 'bynetworkpath'))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > behavior > matching must be a string\n\tValid values are whitelist or blacklist\n'

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','behavior','users','monitor_disabled')) == None)):
        if (
            not (isinstance(check,bool) and
                 (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > behavior > user > monitor_disabled must be a boolean\n\tValid values are true or false\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','users')) == None)):
        
        error_found_in_mumc_config_yaml+=cfgCheckYAML_forLibraries(check, user_id_check_list, user_name_check_list, 'admin_settings > users')
        if (not (len(check) == check_user_keys_length)):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > users Number of configured users does not match the expected value\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','api_controls','attempts')) == None)):
        if (
            not ((isinstance(check,int)) and
                ((check >= 0) and
                (check <= 16)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > api_controls > attempts must be an integer\n\tValid range 0 thru 16\n'

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','api_controls','item_limit')) == None)):
        if (
            not ((isinstance(check,int)) and
                ((check >= 0) and
                (check <= 10000)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > api_controls > item_limit must be an integer\n\tValid range 0 thru 10000\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','cache','size')) == None)):
        if (
            not ((isinstance(check,int)) and
                ((check >= 0) and
                (check <= 10000)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > cache > size must be an integer\n\tValid range 0 thru 10000\n'

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','cache','fallback_behavior')) == None)):
        if (
            not ((isinstance(check,str)) and
                (check.upper() == 'FIFO') or (check.upper() == 'LFU') or (check.upper() == 'LRU'))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > cache > fallback_behavior must be a string\n\tValid values are FIFO, LFU, or LRU\n'

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','cache','minimum_age')) == None)):
        if (
            not ((isinstance(check,int)) and
                ((check >= 0) and
                (check <= 60000)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > cache > minimum_age must be an integer\n\tValid range 0 thru 60000\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','output_controls','character_limit','print')) == None)):
        if (
            not ((isinstance(check,int)) and
                ((check >= -1) and
                (check <= 730500)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > output_controls > character_limit > print must be an integer\n\tValid range -1 thru 730500\n'

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','output_controls','character_limit','write')) == None)):
        if (
            not ((isinstance(check,int)) and
                ((check >= -1) and
                (check <= 730500)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > output_controls > character_limit > write must be an integer\n\tValid range -1 thru 730500\n'

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'DEBUG')) == None)):
        if (
            not ((isinstance(check,int)) and (((check >= 0) and (check <= 4)) or (check == 255)))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: DEBUG must be a string\n\tValid range 0 thru 4\n'

#######################################################################################################

#Check for overlapping tags between blacklists and whitelists

    #check global blacktags and global whitetags do not have a common string
    if (overlapping_tags_set:=global_blacktag_set.intersection(global_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check media specific blacktags and media specific whitetags do not have a common string
    if (overlapping_tags_set:=movie_blacktag_set.intersection(movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > movie > blacktagged > tags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=episode_blacktag_set.intersection(episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > episode > blacktagged > tags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=audio_blacktag_set.intersection(audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audio > blacktagged > tags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=audiobook_blacktag_set.intersection(audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audiobook > blacktagged > tags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check media specific filter blacktags and media specific filter whitetags do not have a common string
    if (overlapping_tags_set:=filter_movie_blacktag_set.intersection(filter_movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > movie > blacktagged > tags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=filter_episode_blacktag_set.intersection(filter_episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > episode > blacktagged > tags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=filter_audio_blacktag_set.intersection(filter_audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audio > blacktagged > tags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=filter_audiobook_blacktag_set.intersection(filter_audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audiobook > blacktagged > tags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check global blacktags and media specific whitetags do not have a common string
    if (overlapping_tags_set:=global_blacktag_set.intersection(movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_blacktag_set.intersection(episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_blacktag_set.intersection(audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=global_blacktag_set.intersection(audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

    #check global whitetags and media specific blacktags do not have a common string
    if (overlapping_tags_set:=global_whitetag_set.intersection(movie_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > movie > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_whitetag_set.intersection(episode_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > episode > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_whitetag_set.intersection(audio_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audio > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=global_whitetag_set.intersection(audiobook_blacktag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audiobook > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check global blacktags and media specific filter whitetags do not have a common string
    if (overlapping_tags_set:=global_blacktag_set.intersection(filter_movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_blacktag_set.intersection(filter_episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_blacktag_set.intersection(filter_audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=global_blacktag_set.intersection(filter_audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

    #check global whitetags and media specific filter blacktags do not have a common string
    if (overlapping_tags_set:=global_whitetag_set.intersection(filter_movie_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > movie > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_whitetag_set.intersection(filter_episode_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > episode > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_whitetag_set.intersection(filter_audio_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audio > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=global_whitetag_set.intersection(filter_audiobook_blacktag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audiobook > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check media specific blacktags and media specific filter whitetags do not have a common string
    if (overlapping_tags_set:=movie_blacktag_set.intersection(filter_movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > movie > blacktagged > tags and basic_settings > filter_tags > movie > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=episode_blacktag_set.intersection(filter_episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > episode > blacktagged > tags and basic_settings > filter_tags > episode > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=audio_blacktag_set.intersection(filter_audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audio > blacktagged > tags and basic_settings > filter_tags > audio > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=audiobook_blacktag_set.intersection(filter_audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audiobook > blacktagged > tags and basic_settings > filter_tags > audiobook > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

    #check media specific filter blacktags and media specific whitetags do not have a common string
    if (overlapping_tags_set:=filter_movie_blacktag_set.intersection(movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both basic_settings > filter_tags > movie > blacktags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=filter_episode_blacktag_set.intersection(episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both basic_settings > filter_tags > episode > blacktags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=filter_audio_blacktag_set.intersection(audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both basic_settings > filter_tags > audio > blacktags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=filter_audiobook_blacktag_set.intersection(audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both basic_settings > filter_tags > audiobook > blacktags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #Bring all errors found to users attention
    if (not (error_found_in_mumc_config_yaml == '')):
        if (init_dict['DEBUG']):
            appendTo_DEBUG_log("\n" + error_found_in_mumc_config_yaml,2,init_dict)
        print('\n' + error_found_in_mumc_config_yaml)
        sys.exit(0)

#######################################################################################################
    return cfg,init_dict


#admin_settings and server have to be checked early
def pre_cfgCheckYAML(cfg):
    error_found_in_mumc_config_yaml=''
    try:
        cfg['admin_settings']=cfg['admin_settings']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']=cfg['admin_settings']['server']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']['brand']=cfg['admin_settings']['server']['brand']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > brand is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']['url']=cfg['admin_settings']['server']['url']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > url is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']['auth_key']=cfg['admin_settings']['server']['auth_key']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > auth_key is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']['admin_id']=cfg['admin_settings']['server']['admin_id']
    except:
        pass
        #error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > admin_id is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['users']=cfg['admin_settings']['users']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > users is missing from the mumc_config.yaml\n'

    #Bring all errors found to users attention
    if (not (error_found_in_mumc_config_yaml == '')):
        print('\n' + error_found_in_mumc_config_yaml)
        sys.exit(0)