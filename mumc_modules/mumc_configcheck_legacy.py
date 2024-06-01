import sys
import json
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json


#Check blacklist and whitelist config variables are as expected
def cfgCheck_forLibraries(check_list, userid_check_list, username_check_list, config_var_name):

    error_found_in_mumc_config_py=''

    for check_irt in check_list:
        #Check if userid exists
        if ('userid' in check_irt):
            #Set user tracker to zero
            user_found=0
            #Check user from user_keys is also a user in this blacklist/whitelist
            for user_check in userid_check_list:
                if (user_check in check_irt['userid']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' userid ' + check_irt['userid'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' userid ' + check_irt['userid'] + ' is seen more than once\n'
            #Check userid is string
            if not (isinstance(check_irt['userid'], str)):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' the userid is not a string for at least one user\n'
            else:
                #Check userid is 32 character long alphanumeric
                if not (
                    (check_irt['userid'].isalnum()) and
                    (len(check_irt['userid']) == 32)
                ):
                    error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' + at least one userid is not a 32-character alphanumeric string\n'
        else:
            error_found_in_mumc_config_py+='NameError: In ' + config_var_name + ' the userid key is missing for at least one user\n'


        #Check if username exists
        if ('username' in check_irt):
            #Set user tracker to zero
            user_found=0
            #Check user from user_name is also a user in this blacklist/whitelist
            for user_check in username_check_list:
                if (user_check in check_irt['username']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' username ' + check_irt['username'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' username ' + check_irt['username'] + ' is seen more than once\n'
            #Check username is string
            if not (isinstance(check_irt['username'], str)):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' the username is not a string for at least one user\n'
        else:
            error_found_in_mumc_config_py+='NameError: In ' + config_var_name + ' the username is missing for at least one user\n'


        #Check if length is >2; which means a userid, username, and at least one library are stored
        if (len(check_irt) > 2):
            #Get number of elements
            for num_elements in check_irt:
                #Ignore userid and username
                if (((not (num_elements == 'userid')) and (not (num_elements == 'username'))) and (int(num_elements) >= 0)):
                    #Set library key trackers to zero
                    libid_found=0
                    collectiontype_found=0
                    networkpath_found=0
                    path_found=0
                    #Check if this num_element exists before proceeding
                    if (num_elements in check_irt):
                        for libinfo in check_irt[num_elements]:
                            if (libinfo == 'libid'):
                                libid_found += 1
                                #Check libid is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the libid for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check libid is 32 character long alphanumeric
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].isalnum()) and
                                        (len(check_irt[str(num_elements)][libinfo]) >= 1)
                                    ):
                                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the libid for library with key' + num_elements + ' is not an alphanumeric string\n'
                            elif (libinfo == 'collectiontype'):
                                collectiontype_found += 1
                                #Check collectiontype is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the collectiontype for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check collectiontype is all alphabet characters
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].isalpha())
                                    ):
                                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the collectiontype for library with key' + num_elements + ' is not an alphabetic string\n'
                                    else:
                                        #TODO verify we only see specific collection types (i.e. tvshows, movies, music, books, etc...)
                                        pass
                            elif (libinfo == 'networkpath'):
                                networkpath_found += 1
                                #Check networkpath is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the networkpath for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check networkpath has no backslashes
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].find('\\') < 0)
                                    ):
                                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' user ' + check_irt['userid'] + ' the networkpath for library with key' + num_elements + ' cannot have any forward slashes \'\\\'\n'
                            elif (libinfo == 'path'):
                                path_found += 1
                                #Check path is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the path for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check path has no backslashes
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].find('\\') < 0)
                                    ):
                                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the path for library with key' + num_elements + ' cannot have any backslashes \'\\\'\n'
                        if (libid_found == 0):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key libid is missing\n'
                        if (libid_found > 1):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key libid is seen more than once\n'
                        if (collectiontype_found == 0):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key collectiontype is missing\n'
                        if (collectiontype_found > 1):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key collectiontype is seen more than once\n'
                        if (networkpath_found == 0):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key networkpath is missing\n'
                        if (networkpath_found > 1):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key networkpath is seen more than once\n'
                        if (path_found == 0):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key path is missing\n'
                        if (path_found > 1):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key path is seen more than once\n'
                    else:
                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' user ' + check_irt['userid'] + ' key'+ str(num_elements) +' does not exist\n'
    return(error_found_in_mumc_config_py)


#Check select config variables are as expected
def cfgCheckLegacy(cfg,the_dict):

    #Todo: find clean way to put cfg.variable_names in a dict/list/etc... and use the dict/list/etc... to call the varibles by name in a for loop

    config_dict={}
    error_found_in_mumc_config_py=''
    warning_found_in_mumc_config_py=''

#######################################################################################################

    if hasattr(cfg,'server_brand'):
        check=cfg.server_brand.casefold()
        server_brand=check
        if (the_dict['DEBUG']):
            #Double newline for debug log formatting
            appendTo_DEBUG_log("\n\nserver_brand='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,str)) and
            ((check == 'emby') or
            (check == 'jellyfin')))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'server_brand\' variable must be a string with a value of \'emby\' or \'jellyfin\'\n'
            server_brand='invalid'
        else:
            config_dict['server_brand']=check
            server_brand=check
    else:
        error_found_in_mumc_config_py+='LegacyConfigNameError: The \'server_brand\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'
        server_brand='invalid'

#######################################################################################################

    if hasattr(cfg, 'user_keys'):
        check=cfg.user_keys
        try:
            check_list=json.loads(check)
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nuser_keys=" + convert2json(check_list),2,the_dict)
            check_user_keys_length=len(check_list)
            username_check_list=[]
            userid_check_list=[]
            if (check_user_keys_length > 0):
                for user_info in check_list:
                    username_check_list.append(user_info.split(':',1)[0])
                    userid_check_list.append(user_info.split(':',1)[1])
                    for check_irt in userid_check_list:
                        if (
                            not ((isinstance(check_list,list)) and
                                (isinstance(check_irt,str)) and
                                (len(check_irt) == 32) and
                                (str(check_irt).isalnum()))
                        ):
                            error_found_in_mumc_config_py+='LegacyConfigValueError: \'user_keys\' must be a single list with a key:value pair for each monitored \'UserName:UserId\' each user key must be a 32-character alphanumeric string\n'
                else:
                    config_dict['user_keys']=check_list
            else:
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'user_keys cannot be empty\n'
        except:
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'user_keys\' has an unknown formatting error\n'
    else:
        error_found_in_mumc_config_py+='LegacyConfigNameError: The \'user_keys\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'played_filter_movie'):
        check=cfg.played_filter_movie
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nplayed_filter_movie=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],int)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],int)) and
                (len(check) == 3) and
                ((check[1] == '>') or (check[1] == '<') or
                (check[1] == '>=') or (check[1] == '<=') or
                (check[1] == '==') or (check[1] == 'not ==') or
                (check[1] == 'not >') or (check[1] == 'not <') or
                (check[1] == 'not >=') or (check[1] == 'not <=')) and
                ((check[0] >= -1) and (check[0] <= 730500)) and
                ((check[2] >= 1) and (check[2] <= 730500)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'played_filter_movie\' must be a list with three entries\n\tValid range for first entry -1 thru 730500\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n\tValid range for third entry -1 and 1 thru 730500 (0 is invalid)\n'
        else:
            config_dict['played_filter_movie']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'played_filter_movie\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'played_filter_episode'):
        check=cfg.played_filter_episode
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nplayed_filter_episode=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],int)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],int)) and
                (len(check) == 3) and
                ((check[0] >= -1) and (check[0] <= 730500)) and
                ((check[1] == '>') or (check[1] == '<') or
                (check[1] == '>=') or (check[1] == '<=') or
                (check[1] == '==') or (check[1] == 'not ==') or
                (check[1] == 'not >') or (check[1] == 'not <') or
                (check[1] == 'not >=') or (check[1] == 'not <=')) and
                ((check[2] >= 1) and (check[2] <= 730500)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'played_filter_episode\' must be a list with three entries\n\tValid range for first entry -1 thru 730500\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n\tValid range for third entry -1 and 1 thru 730500 (0 is invalid)\n'
        else:
            config_dict['played_filter_episode']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'played_filter_episode\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'played_filter_audio'):
        check=cfg.played_filter_audio
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nplayed_filter_audio=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],int)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],int)) and
                (len(check) == 3) and
                ((check[0] >= -1) and (check[0] <= 730500)) and
                ((check[1] == '>') or (check[1] == '<') or
                (check[1] == '>=') or (check[1] == '<=') or
                (check[1] == '==') or (check[1] == 'not ==') or
                (check[1] == 'not >') or (check[1] == 'not <') or
                (check[1] == 'not >=') or (check[1] == 'not <=')) and
                ((check[2] >= 1) and (check[2] <= 730500)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'played_filter_audio\' must be a list with three entries\n\tValid range for first entry -1 thru 730500\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n\tValid range for third entry -1 and 1 thru 730500 (0 is invalid)\n'
        else:
            config_dict['played_filter_audio']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'played_filter_audio\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'played_filter_audiobook'):
            check=cfg.played_filter_audiobook
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nplayed_filter_audiobook=" + str(check),2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    (isinstance(check[0],int)) and
                    (isinstance(check[1],str)) and
                    (isinstance(check[2],int)) and
                    (len(check) == 3) and
                    ((check[0] >= -1) and (check[0] <= 730500)) and
                    ((check[1] == '>') or (check[1] == '<') or
                    (check[1] == '>=') or (check[1] == '<=') or
                    (check[1] == '==') or (check[1] == 'not ==') or
                    (check[1] == 'not >') or (check[1] == 'not <') or
                    (check[1] == 'not >=') or (check[1] == 'not <=')) and
                    ((check[2] >= 1) and (check[2] <= 730500)))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'played_filter_audiobook\' must be a list with three entries\n\tValid range for first entry -1 thru 730500\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n\tValid range for third entry -1 and 1 thru 730500 (0 is invalid)\n'
            else:
                config_dict['played_filter_audiobook']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'played_filter_audiobook\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'created_filter_movie'):
        check=cfg.created_filter_movie
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\ncreated_filter_movie=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],int)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],int)) and
                (isinstance(check[3],bool)) and
                (len(check) == 4) and
                ((check[0] >= -1) and (check[0] <= 730500)) and
                ((check[1] == '>') or (check[1] == '<') or
                (check[1] == '>=') or (check[1] == '<=') or
                (check[1] == '==') or (check[1] == 'not ==') or
                (check[1] == 'not >') or (check[1] == 'not <') or
                (check[1] == 'not >=') or (check[1] == 'not <=')) and
                ((check[2] >= 0) and (check[2] <= 730500)) and
                ((check[3] == True) or (check[3] == False)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'created_filter_movie\' must be a list with four entries\n\tValid range for first entry -1 thru 730500\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n\tValid range for third entry -1 thru 730500\n\tValid values for fourth entry boolean \'True\' or \'False\'\n'
        else:
            config_dict['created_filter_movie']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'created_filter_movie\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'created_filter_episode'):
        check=cfg.created_filter_episode
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\ncreated_filter_episode=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],int)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],int)) and
                (isinstance(check[3],bool)) and
                (len(check) == 4) and
                ((check[0] >= -1) and (check[0] <= 730500)) and
                ((check[1] == '>') or (check[1] == '<') or
                (check[1] == '>=') or (check[1] == '<=') or
                (check[1] == '==') or (check[1] == 'not ==') or
                (check[1] == 'not >') or (check[1] == 'not <') or
                (check[1] == 'not >=') or (check[1] == 'not <=')) and
                ((check[2] >= 0) and (check[2] <= 730500)) and
                ((check[3] == True) or (check[3] == False)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'created_filter_episode\' must be a list with four entries\n\tValid range for first entry -1 thru 730500\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n\tValid range for third entry -1 thru 730500\n\tValid values for fourth entry boolean \'True\' or \'False\'\n'
        else:
            config_dict['created_filter_episode']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'created_filter_episode\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'created_filter_audio'):
        check=cfg.created_filter_audio
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\ncreated_filter_audio=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],int)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],int)) and
                (isinstance(check[3],bool)) and
                (len(check) == 4) and
                ((check[0] >= -1) and (check[0] <= 730500)) and
                ((check[1] == '>') or (check[1] == '<') or
                (check[1] == '>=') or (check[1] == '<=') or
                (check[1] == '==') or (check[1] == 'not ==') or
                (check[1] == 'not >') or (check[1] == 'not <') or
                (check[1] == 'not >=') or (check[1] == 'not <=')) and
                ((check[2] >= 0) and (check[2] <= 730500)) and
                ((check[3] == True) or (check[3] == False)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'created_filter_audio\' must be a list with four entries\n\tValid range for first entry -1 thru 730500\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n\tValid range for third entry -1 thru 730500\n\tValid values for fourth entry boolean \'True\' or \'False\'\n'
        else:
            config_dict['created_filter_audio']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'created_filter_audio\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'created_filter_audiobook'):
            check=cfg.created_filter_audiobook
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\ncreated_filter_audiobook=" + str(check),2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    (isinstance(check[0],int)) and
                    (isinstance(check[1],str)) and
                    (isinstance(check[2],int)) and
                    (isinstance(check[3],bool)) and
                    (len(check) == 4) and
                    ((check[0] >= -1) and (check[0] <= 730500)) and
                    ((check[1] == '>') or (check[1] == '<') or
                    (check[1] == '>=') or (check[1] == '<=') or
                    (check[1] == '==') or (check[1] == 'not ==') or
                    (check[1] == 'not >') or (check[1] == 'not <') or
                    (check[1] == 'not >=') or (check[1] == 'not <=')) and
                    ((check[2] >= 0) and (check[2] <= 730500)) and
                    ((check[3] == True) or (check[3] == False)))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'created_filter_audiobook\' must be a list with four entries\n\tValid range for first entry -1 thru 730500\n\tValid values for second entry are inequalities \'>\', \'<\', \'>=\', etc...\n\tValid range for third entry -1 thru 730500\n\tValid values for fourth entry boolean \'True\' or \'False\'\n'
            else:
                config_dict['created_filter_audiobook']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'created_filter_audiobook\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'favorited_behavior_movie'):
        check=cfg.favorited_behavior_movie
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_behavior_movie=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_behavior_movie\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['favorited_behavior_movie']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_behavior_movie\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_behavior_episode'):
        check=cfg.favorited_behavior_episode
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_behavior_episode=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_behavior_episode\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['favorited_behavior_episode']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_behavior_episode\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_behavior_audio'):
        check=cfg.favorited_behavior_audio
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_behavior_audio=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_behavior_audio\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['favorited_behavior_audio']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_behavior_audio\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'favorited_behavior_audiobook'):
            check=cfg.favorited_behavior_audiobook
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nfavorited_behavior_audiobook=" + str(check),2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    (isinstance(check[0],str)) and
                    (isinstance(check[1],str)) and
                    (isinstance(check[2],str)) and
                    (isinstance(check[3],int)) and
                    (len(check) == 4) and
                    ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                    ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                    ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                     (check[2].casefold() == 'any_all') or(check[2].casefold() == 'all_any') or
                     (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                     (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                     (check[2].casefold() == 'ignore')) and
                    ((check[3] >= 0) and (check[3] <= 8)))
            ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_behavior_audiobook\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
            else:
                config_dict['favorited_behavior_audiobook']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_behavior_audiobook\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'favorited_advanced_movie_genre'):
        check=cfg.favorited_advanced_movie_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_movie_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_movie_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_movie_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_movie_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_movie_library_genre'):
        check=cfg.favorited_advanced_movie_library_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_movie_library_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_movie_library_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_movie_library_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_movie_library_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'favorited_advanced_episode_genre'):
        check=cfg.favorited_advanced_episode_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_episode_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_episode_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_episode_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_episode_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_season_genre'):
        check=cfg.favorited_advanced_season_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_season_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_season_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_season_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_season_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_series_genre'):
        check=cfg.favorited_advanced_series_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_series_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_series_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_series_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_series_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_tv_library_gnre'):
        check=cfg.favorited_advanced_tv_library_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_tv_library_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_tv_library_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_tv_library_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_tv_library_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_tv_studio_network'):
        check=cfg.favorited_advanced_tv_studio_network
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_tv_studio_network=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_tv_studio_network\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_tv_studio_network']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_tv_studio_network\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_tv_studio_network_genre'):
        check=cfg.favorited_advanced_tv_studio_network_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_tv_studio_network_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_tv_studio_network_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_tv_studio_network_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_tv_studio_network_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'favorited_advanced_track_genre'):
        check=cfg.favorited_advanced_track_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_track_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_track_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_track_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_track_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_album_genre'):
        check=cfg.favorited_advanced_album_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_album_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_album_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_album_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_album_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_music_library_genre'):
        check=cfg.favorited_advanced_music_library_genre
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_music_library_genre=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_music_library_genre\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_music_library_genre']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_music_library_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_track_artist'):
        check=cfg.favorited_advanced_track_artist
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_track_artist=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_track_artist\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_track_artist']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_track_artist\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'favorited_advanced_album_artist'):
        check=cfg.favorited_advanced_album_artist
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nfavorited_advanced_album_artist=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 2))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_album_artist\' must be an integer; valid range 0 thru 2\n'
        else:
            config_dict['favorited_advanced_album_artist']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_album_artist\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if (isJellyfinServer(server_brand)):
            if hasattr(cfg, 'favorited_advanced_audiobook_track_genre'):
                check=cfg.favorited_advanced_audiobook_track_genre
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nfavorited_advanced_audiobook_track_genre=" + str(check),2,the_dict)
                if (
                    not ((isinstance(check,int)) and
                        (check >= 0) and
                        (check <= 2))
                ):
                    error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_audiobook_track_genre\' must be an integer; valid range 0 thru 2\n'
                else:
                    config_dict['favorited_advanced_audiobook_track_genre']=check
            else:
                warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_audiobook_track_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

            if hasattr(cfg, 'favorited_advanced_audiobook_genre'):
                check=cfg.favorited_advanced_audiobook_genre
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nfavorited_advanced_audiobook_genre=" + str(check),2,the_dict)
                if (
                    not ((isinstance(check,int)) and
                        (check >= 0) and
                        (check <= 2))
                ):
                    error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_audiobook_genre\' must be an integer; valid range 0 thru 2\n'
                else:
                    config_dict['favorited_advanced_audiobook_genre']=check
            else:
                warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_audiobook_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

            if hasattr(cfg, 'favorited_advanced_audiobook_library_genre'):
                check=cfg.favorited_advanced_audiobook_library_genre
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nfavorited_advanced_audiobook_library_genre=" + str(check),2,the_dict)
                if (
                    not ((isinstance(check,int)) and
                        (check >= 0) and
                        (check <= 2))
                ):
                    error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_audiobook_library_genre\' must be an integer; valid range 0 thru 2\n'
                else:
                    config_dict['favorited_advanced_audiobook_library_genre']=check
            else:
                warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_audiobook_library_genre\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

            if hasattr(cfg, 'favorited_advanced_audiobook_track_author'):
                check=cfg.favorited_advanced_audiobook_track_author
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nfavorited_advanced_audiobook_track_author=" + str(check),2,the_dict)
                if (
                    not ((isinstance(check,int)) and
                        (check >= 0) and
                        (check <= 2))
                ):
                    error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_audiobook_track_author\' must be an integer; valid range 0 thru 2\n'
                else:
                    config_dict['favorited_advanced_audiobook_track_author']=check
            else:
                warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_audiobook_track_author\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

            if hasattr(cfg, 'favorited_advanced_audiobook_author'):
                check=cfg.favorited_advanced_audiobook_author
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nfavorited_advanced_audiobook_author=" + str(check),2,the_dict)
                if (
                    not ((isinstance(check,int)) and
                        (check >= 0) and
                        (check <= 2))
                ):
                    error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_audiobook_author\' must be an integer; valid range 0 thru 2\n'
                else:
                    config_dict['favorited_advanced_audiobook_author']=check
            else:
                warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_audiobook_author\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

            if hasattr(cfg, 'favorited_advanced_audiobook_library_author'):
                check=cfg.favorited_advanced_audiobook_library_author
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nfavorited_advanced_audiobook_library_author=" + str(check),2,the_dict)
                if (
                    not ((isinstance(check,int)) and
                        (check >= 0) and
                        (check <= 2))
                ):
                    error_found_in_mumc_config_py+='LegacyConfigValueError: \'favorited_advanced_audiobook_library_author\' must be an integer; valid range 0 thru 2\n'
                else:
                    config_dict['favorited_advanced_audiobook_library_author']=check
            else:
                warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'favorited_advanced_audiobook_library_author\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'whitetag'):
        check=cfg.whitetag
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nwhitetag='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,str)) and
                (check.find('\\') < 0))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'Whitetag(s)\' must be a single string with a comma separating multiple tag names; backlash \'\\\' not allowed\n'
        else:
            config_dict['whitetag']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'whitetag\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'whitetagged_behavior_movie'):
        check=cfg.whitetagged_behavior_movie
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nwhitetagged_behavior_movie=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'whitetagged_behavior_movie\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid value for second entry: \'all\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['whitetagged_behavior_movie']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'whitetagged_behavior_movie\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'whitetagged_behavior_episode'):
        check=cfg.whitetagged_behavior_episode
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nwhitetagged_behavior_episode=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'whitetagged_behavior_episode\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid value for second entry: \'all\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['whitetagged_behavior_episode']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'whitetagged_behavior_episode\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'whitetagged_behavior_audio'):
        check=cfg.whitetagged_behavior_audio
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nwhitetagged_behavior_audio=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'whitetagged_behavior_audio\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid value for second entry: \'all\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['whitetagged_behavior_audio']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'whitetagged_behavior_audio\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'whitetagged_behavior_audiobook'):
            check=cfg.whitetagged_behavior_audiobook
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nwhitetagged_behavior_audiobook=" + str(check),2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    (isinstance(check[0],str)) and
                    (isinstance(check[1],str)) and
                    (isinstance(check[2],str)) and
                    (isinstance(check[3],int)) and
                    (len(check) == 4) and
                    ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                    ((check[1].casefold() == 'all')) and
                    ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                     (check[2].casefold() == 'any_all') or(check[2].casefold() == 'all_any') or
                     (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                     (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                     (check[2].casefold() == 'ignore')) and
                    ((check[3] >= 0) and (check[3] <= 8)))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'whitetagged_behavior_audiobook\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid value for second entry: \'all\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
            else:
                config_dict['whitetagged_behavior_audiobook']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'whitetagged_behavior_audiobook\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'blacktag'):
        check=cfg.blacktag
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nblacktag='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,str)) and
                (check.find('\\') < 0))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'Blacktag(s)\' must be a single string with a comma separating multiple tag names; backlash \'\\\' not allowed\n'
        else:
            config_dict['blacktag']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'blacktag\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'blacktagged_behavior_movie'):
        check=cfg.blacktagged_behavior_movie
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nblacktagged_behavior_movie=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'blacktagged_behavior_movie\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid value for second entry: \'all\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['blacktagged_behavior_movie']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'blacktagged_behavior_movie\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'blacktagged_behavior_episode'):
        check=cfg.blacktagged_behavior_episode
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nblacktagged_behavior_episode=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'blacktagged_behavior_episode\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid value for second entry: \'all\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['blacktagged_behavior_episode']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'blacktagged_behavior_episode\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'blacktagged_behavior_audio'):
        check=cfg.blacktagged_behavior_audio
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nblacktagged_behavior_audio=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'blacktagged_behavior_audio\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid value for second entry: \'all\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['blacktagged_behavior_audio']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'blacktagged_behavior_audio\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'blacktagged_behavior_audiobook'):
            check=cfg.blacktagged_behavior_audiobook
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nblacktagged_behavior_audiobook=" + str(check),2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    (isinstance(check[0],str)) and
                    (isinstance(check[1],str)) and
                    (isinstance(check[2],str)) and
                    (isinstance(check[3],int)) and
                    (len(check) == 4) and
                    ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                    ((check[1].casefold() == 'all')) and
                    ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                     (check[2].casefold() == 'any_all') or(check[2].casefold() == 'all_any') or
                     (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                     (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                     (check[2].casefold() == 'ignore')) and
                    ((check[3] >= 0) and (check[3] <= 8)))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'blacktagged_behavior_audiobook\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid value for second entry: \'all\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
            else:
                config_dict['blacktagged_behavior_audiobook']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'blacktagged_behavior_audiobook\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'whitelisted_behavior_movie'):
        check=cfg.whitelisted_behavior_movie
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nwhitelisted_behavior_movie=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'whitelisted_behavior_movie\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['whitelisted_behavior_movie']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'whitelisted_behavior_movie\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'whitelisted_behavior_episode'):
        check=cfg.whitelisted_behavior_episode
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nwhitelisted_behavior_episode=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'whitelisted_behavior_episode\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['whitelisted_behavior_episode']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'whitelisted_behavior_episode\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'whitelisted_behavior_audio'):
        check=cfg.whitelisted_behavior_audio
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nwhitelisted_behavior_audio=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'whitelisted_behavior_audio\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['whitelisted_behavior_audio']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'whitelisted_behavior_audio\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'whitelisted_behavior_audiobook'):
            check=cfg.whitelisted_behavior_audiobook
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nwhitelisted_behavior_audiobook=" + str(check),2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    (isinstance(check[0],str)) and
                    (isinstance(check[1],str)) and
                    (isinstance(check[2],str)) and
                    (isinstance(check[3],int)) and
                    (len(check) == 4) and
                    ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                    ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                    ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                     (check[2].casefold() == 'any_all') or(check[2].casefold() == 'all_any') or
                     (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                     (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                     (check[2].casefold() == 'ignore')) and
                    ((check[3] >= 0) and (check[3] <= 8)))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'whitelisted_behavior_audiobook\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
            else:
                config_dict['whitelisted_behavior_audiobook']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'whitelisted_behavior_audiobook\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'blacklisted_behavior_movie'):
        check=cfg.blacklisted_behavior_movie
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nblacklisted_behavior_movie=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'blacklisted_behavior_movie\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['blacklisted_behavior_movie']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'blacklisted_behavior_movie\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'blacklisted_behavior_episode'):
        check=cfg.blacklisted_behavior_episode
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nblacklisted_behavior_episode=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'blacklisted_behavior_episode\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['blacklisted_behavior_episode']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'blacklisted_behavior_episode\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'blacklisted_behavior_audio'):
        check=cfg.blacklisted_behavior_audio
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nblacklisted_behavior_audio=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,list)) and
                (isinstance(check[0],str)) and
                (isinstance(check[1],str)) and
                (isinstance(check[2],str)) and
                (isinstance(check[3],int)) and
                (len(check) == 4) and
                ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                 (check[2].casefold() == 'any_all') or (check[2].casefold() == 'all_any') or
                 (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                 (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                 (check[2].casefold() == 'ignore')) and
                ((check[3] >= 0) and (check[3] <= 8)))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'blacklisted_behavior_audio\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
        else:
            config_dict['blacklisted_behavior_audio']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'blacklisted_behavior_audio\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'blacklisted_behavior_audiobook'):
            check=cfg.blacklisted_behavior_audiobook
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nblacklisted_behavior_audiobook=" + str(check),2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    (isinstance(check[0],str)) and
                    (isinstance(check[1],str)) and
                    (isinstance(check[2],str)) and
                    (isinstance(check[3],int)) and
                    (len(check) == 4) and
                    ((check[0].casefold() == 'delete') or (check[0].casefold() == 'keep')) and
                    ((check[1].casefold() == 'all') or (check[1].casefold() == 'any')) and
                    ((check[2].casefold() == 'all') or (check[2].casefold() == 'any') or
                     (check[2].casefold() == 'any_all') or(check[2].casefold() == 'all_any') or
                     (check[2].casefold() == 'any_played') or (check[2].casefold() == 'all_played') or
                     (check[2].casefold() == 'any_created') or (check[2].casefold() == 'all_created') or
                     (check[2].casefold() == 'ignore')) and
                    ((check[3] >= 0) and (check[3] <= 8)))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'blacklisted_behavior_audiobook\' must be a list with four entries\n\tValid values for first entry: \'delete\' and \'keep\'\n\tValid values for second entry: \'all\' and/or \'any\'\n\tValid values for third entry: \'all\', \'any\', and/or \'ignore\'\n\tValid range for fourth entry: 0 thru 8\n'
            else:
                config_dict['blacklisted_behavior_audiobook']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'blacklisted_behavior_audiobook\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'minimum_number_episodes'):
        check=cfg.minimum_number_episodes
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nminimum_number_episodes=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 730500))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'minimum_number_episodes\' must be an integer; valid range 0 thru 730500\n'
        else:
            config_dict['minimum_number_episodes']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'minimum_number_episodes\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'minimum_number_played_episodes'):
        check=cfg.minimum_number_played_episodes
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nminimum_number_played_episodes=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 730500))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'minimum_number_played_episodes\' must be an integer; valid range 0 thru 730500\n'
        else:
            config_dict['minimum_number_played_episodes']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'minimum_number_played_episodes\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'minimum_number_episodes_behavior'):
        check=cfg.minimum_number_episodes_behavior
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nminimum_number_episodes_behavior='" + str(check) + "'",2,the_dict)
        check=check.casefold()
        usersname_usersid_match=False
        for usersname in username_check_list:
            if (check == usersname.casefold()):
                usersname_usersid_match=True
        for usersid in userid_check_list:
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
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'minimum_number_episodes_behavior\' must be a string; valid values \'User Name\', \'User Id\', and \'Min/Max Played/Unplayed\'\n'
        else:
            config_dict['minimum_number_episodes_behavior']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'minimum_number_episodes_behavior\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'movie_set_missing_last_played_date'):
        check=cfg.movie_set_missing_last_played_date
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nmovie_set_missing_last_played_date=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'movie_set_missing_last_played_date\' must be a boolean; valid values True and False\n'
        else:
            config_dict['movie_set_missing_last_played_date']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'movie_set_missing_last_played_date\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'episode_set_missing_last_played_date'):
        check=cfg.episode_set_missing_last_played_date
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nepisode_set_missing_last_played_date=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'episode_set_missing_last_played_date\' must be a boolean; valid values True and False\n'
        else:
            config_dict['episode_set_missing_last_played_date']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'episode_set_missing_last_played_date\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'audio_set_missing_last_played_date'):
        check=cfg.audio_set_missing_last_played_date
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\naudio_set_missing_last_played_date=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'audio_set_missing_last_played_date\' must be a boolean; valid values True and False\n'
        else:
            config_dict['audio_set_missing_last_played_date']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audio_set_missing_last_played_date\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'audiobook_set_missing_last_played_date'):
            check=cfg.audiobook_set_missing_last_played_date
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\naudiobook_set_missing_last_played_date=" + str(check),2,the_dict)
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or
                    (check == False))
            ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'audiobook_set_missing_last_played_date\' must be a boolean; valid values True and False\n'
            else:
                config_dict['audiobook_set_missing_last_played_date']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audiobook_set_missing_last_played_date\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'print_script_header'):
        check=cfg.print_script_header
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_script_header='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_script_header\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_script_header']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_script_header\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_warnings'):
        check=cfg.print_warnings
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_warnings='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_warnings\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_warnings']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_warnings\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_user_header'):
        check=cfg.print_user_header
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_user_header='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_user_header\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_user_header']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_user_header\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_movie_delete_info'):
        check=cfg.print_movie_delete_info
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_movie_delete_info='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_movie_delete_info\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_movie_delete_info']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_movie_delete_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_movie_keep_info'):
        check=cfg.print_movie_keep_info
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_movie_keep_info='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_movie_keep_info\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_movie_keep_info']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_movie_keep_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_episode_delete_info'):
        check=cfg.print_episode_delete_info
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_episode_delete_info='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_episode_delete_info\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_episode_delete_info']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_episode_delete_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_episode_keep_info'):
        check=cfg.print_episode_keep_info
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_episode_keep_info='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_episode_keep_info\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_episode_keep_info']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_episode_keep_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_audio_delete_info'):
        check=cfg.print_audio_delete_info
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_audio_delete_info='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_audio_delete_info\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_audio_delete_info']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_audio_delete_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_audio_keep_info'):
        check=cfg.print_audio_keep_info
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_audio_keep_info='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_audio_keep_info\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_audio_keep_info']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_audio_keep_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'print_audiobook_delete_info'):
            check=cfg.print_audiobook_delete_info
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nprint_audiobook_delete_info='" + str(check) + "'",2,the_dict)
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or
                    (check == False))
            ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_audiobook_delete_info\' must be a boolean; valid values True and False\n'
            else:
                config_dict['print_audiobook_delete_info']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_audiobook_delete_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

        if hasattr(cfg, 'print_audiobook_keep_info'):
            check=cfg.print_audiobook_keep_info
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nprint_audiobook_keep_info='" + str(check) + "'",2,the_dict)
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or
                    (check == False))
            ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_audiobook_keep_info\' must be a boolean; valid values True and False\n'
            else:
                config_dict['print_audiobook_keep_info']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_audiobook_keep_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_movie_post_processing_info'):
        check=cfg.print_movie_post_processing_info
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_movie_post_processing_info='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_movie_post_processing_info\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_movie_post_processing_info']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_movie_post_processing_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_episode_post_processing_info'):
        check=cfg.print_episode_post_processing_info
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_episode_post_processing='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_episode_post_processing_info\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_episode_post_processing_info']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_episode_post_processing_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_audio_post_processing_info'):
        check=cfg.print_audio_post_processing_info
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_audio_post_processing='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_audio_post_processing_info\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_audio_post_processing_info']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_audio_post_processing_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'print_audiobook_post_processing_info'):
            check=cfg.print_audiobook_post_processing_info
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nprint_audiobook_post_processing='" + str(check) + "'",2,the_dict)
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or
                    (check == False))
            ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_audiobook_post_processing_info\' must be a boolean; valid values True and False\n'
            else:
                config_dict['print_audiobook_post_processing_info']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_audiobook_post_processing_info\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_summary_header'):
        check=cfg.print_summary_header
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_summary_header='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_summary_header\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_summary_header']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_summary_header\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_movie_summary'):
        check=cfg.print_movie_summary
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_movie_summary='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_movie_summary\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_movie_summary']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_movie_summary\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_episode_summary'):
        check=cfg.print_episode_summary
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_episode_summary='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_episode_summary\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_episode_summary']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_episode_summary\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_audio_summary'):
        check=cfg.print_audio_summary
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_audio_summary='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_audio_summary\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_audio_summary']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_audio_summary\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'print_audiobook_summary'):
            check=cfg.print_audiobook_summary
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nprint_audiobook_summary='" + str(check) + "'",2,the_dict)
            if (
                not ((isinstance(check,bool)) and
                    (check == True) or
                    (check == False))
            ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_audiobook_summary\' must be a boolean; valid values True and False\n'
            else:
                config_dict['print_audiobook_summary']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_audiobook_summary\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'print_script_footer'):
        check=cfg.print_script_footer
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nprint_script_footer='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'print_script_footer\' must be a boolean; valid values True and False\n'
        else:
            config_dict['print_script_footer']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'print_script_footer\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'script_header_format'):
        check=cfg.script_header_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nscript_header_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'script_header_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
            
        else:
            config_dict['script_header_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'script_header_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'script_warnings_format'):
        check=cfg.script_warnings_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nscript_warnings_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'nscript_warnings_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['script_warnings_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'script_warnings_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'user_header_format'):
        check=cfg.user_header_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nuser_header_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'user_header_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['user_header_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'user_header_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'movie_delete_info_format'):
        check=cfg.movie_delete_info_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nmovie_delete_info_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'movie_delete_info_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['movie_delete_info_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'movie_delete_info_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'movie_keep_info_format'):
        check=cfg.movie_keep_info_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nmovie_keep_info_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'movie_keep_info_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['movie_keep_info_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'movie_keep_info_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'episode_delete_info_format'):
        check=cfg.episode_delete_info_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nepisode_delete_info_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'episode_delete_info_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['episode_delete_info_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'episode_delete_info_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'episode_keep_info_format'):
        check=cfg.episode_keep_info_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nepisode_keep_info_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'episode_keep_info_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['episode_keep_info_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'episode_keep_info_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'audio_delete_info_format'):
        check=cfg.audio_delete_info_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\naudio_delete_info_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'audio_delete_info_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['audio_delete_info_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audio_delete_info_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'audio_keep_info_format'):
        check=cfg.audio_keep_info_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\naudio_keep_info_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'audio_keep_info_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['audio_keep_info_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audio_keep_info_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'audiobook_delete_info_format'):
            check=cfg.audiobook_delete_info_format
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\naudiobook_delete_info_format='" + str(check) + "'",2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                    ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                    ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                    (len(check) == 3) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'audiobook_delete_info_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
            else:
                config_dict['audiobook_delete_info_format']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audiobook_delete_info_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

        if hasattr(cfg, 'audiobook_keep_info_format'):
            check=cfg.audiobook_keep_info_format
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\naudiobook_keep_info_format='" + str(check) + "'",2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                    ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                    ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                    (len(check) == 3) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'audiobook_keep_info_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
            else:
                config_dict['audiobook_keep_info_format']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audiobook_keep_info_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'movie_post_processing_format'):
        check=cfg.movie_post_processing_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nmovie_post_processing_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'movie_post_processing_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['movie_post_processing_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'movie_post_processing_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'episode_post_processing_format'):
        check=cfg.episode_post_processing_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nepisode_post_processing_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'episode_post_processing_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['episode_post_processing_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'episode_post_processing_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'audio_post_processing_format'):
        check=cfg.audio_post_processing_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\naudio_post_processing_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'audio_post_processing_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['audio_post_processing_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audio_post_processing_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'audiobook_post_processing_format'):
            check=cfg.audiobook_post_processing_format
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\naudiobook_post_processing_format='" + str(check) + "'",2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                    ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                    ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                    (len(check) == 3) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'audiobook_post_processing_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
            else:
                config_dict['audiobook_post_processing_format']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audiobook_post_processing_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'summary_header_format'):
        check=cfg.summary_header_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nsummary_header_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'summary_header_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['summary_header_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'summary_header_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'movie_summary_format'):
        check=cfg.movie_summary_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nmovie_summary_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'movie_summary_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['movie_summary_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'movie_summary_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'episode_summary_format'):
        check=cfg.episode_summary_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nepisode_summary_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'episode_summary_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['episode_summary_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'episode_summary_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'audio_summary_format'):
        check=cfg.audio_summary_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\naudio_summary_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'audio_summary_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['audio_summary_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audio_summary_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if (isJellyfinServer(server_brand)):
        if hasattr(cfg, 'audiobook_summary_format'):
            check=cfg.audiobook_summary_format
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\naudiobook_summary_format='" + str(check) + "'",2,the_dict)
            if (
                not ((isinstance(check,list)) and
                    ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                    ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                    ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                    (len(check) == 3) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                    ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
                ):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'audiobook_summary_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
            else:
                config_dict['audiobook_summary_format']=check
        else:
            warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'audiobook_summary_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'script_footer_format'):
        check=cfg.script_footer_format
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nscript_footer_format='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,list)) and
                ((isinstance(check[0],str)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(check[1],str)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(check[2],str)) or (check[2] == None) or (check[2] == '')) and
                (len(check) == 3) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',check[0]),int)) or (check[0] == None) or (check[0] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',check[1]),int)) or (check[1] == None) or (check[1] == '')) and
                ((isinstance(the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',check[2]),int)) or (check[2] == None) or (check[2] == '')))
            ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'script_footer_format\' must be a list with three entries\n\tValid values for each entry are \'\', \'None\' or the attributes values defined here: https://github.com/terrelsa13/MUMC/tree/MUMC-Latest#control-console-text-formatting\n'
        else:
            config_dict['script_footer_format']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'script_footer_format\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'UPDATE_CONFIG'):
        check=cfg.UPDATE_CONFIG
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nUPDATE_CONFIG='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'UPDATE_CONFIG\' must be a boolean; valid values True and False\n'
        else:
            config_dict['UPDATE_CONFIG']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'UPDATE_CONFIG\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'REMOVE_FILES'):
        check=cfg.REMOVE_FILES
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nREMOVE_FILES='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,bool)) and
                (check == True) or
                (check == False))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'REMOVE_FILES\' must be a boolean; valid values True and False\n'
        else:
            config_dict['REMOVE_FILES']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'REMOVE_FILES\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'server_url'):
        check=cfg.server_url
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nserver_url='" + str(check) + "'",2,the_dict)
        if (
            not (isinstance(check,str))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'server_url\' must be a string\n'
        else:
            config_dict['server_url']=check
    else:
        error_found_in_mumc_config_py+='LegacyConfigNameError: The \'server_url\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'auth_key'):
        check=cfg.auth_key
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nauth_key='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,str)) and
            (len(check) == 32) and
            (str(check).isalnum()))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'auth_key\' must be a 32-character alphanumeric string\n'
        else:
            config_dict['auth_key']=check
    else:
        error_found_in_mumc_config_py+='LegacyConfigNameError: The \'auth_key\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'library_setup_behavior'):
        check=cfg.library_setup_behavior
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nlibrary_setup_behavior='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,str)) and
            ((check == 'blacklist') or (check == 'whitelist')))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'library_setup_behavior\' must be a string; valid values \'blacklist\' or \'whitelist\'\n'
        else:
            config_dict['library_setup_behavior']=check
    else:
        error_found_in_mumc_config_py+='LegacyConfigNameError: The \'library_setup_behavior\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'library_matching_behavior'):
        check=cfg.library_matching_behavior.casefold()
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nlibrary_matching_behavior='" + str(check) + "'",2,the_dict)
        if (
            not ((isinstance(check,str)) and
            ((check == 'byid') or (check == 'bypath') or (check == 'bynetworkpath')))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'library_matching_behavior\' must be a string; valid values \'byId\' or \'byPath\' or \'byNetworkPath\'\n'
        else:
            config_dict['library_matching_behavior']=check
    else:
        error_found_in_mumc_config_py+='LegacyConfigNameError: The \'library_matching_behavior\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'user_bl_libs'):
        check=cfg.user_bl_libs
        check_list=json.loads(check)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nuser_bl_libs=" + convert2json(check_list),2,the_dict)
        check_user_bllibs_length=len(check_list)
        if (check_user_bllibs_length > 0):
            #Check number of users matches the number of blacklist entries
            if not (check_user_bllibs_length == check_user_keys_length):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'user_bl_libs\' Number of configured users does not match the number of configured blacklists\n'
            else:
                error_found_in_mumc_config_py+=cfgCheck_forLibraries(check_list, userid_check_list, username_check_list, 'user_bl_libs')
        else:
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'user_bl_libs\' cannot be empty\n'

        config_dict['user_bl_libs']=check_list
    else:
        error_found_in_mumc_config_py+='LegacyConfigNameError: The \'user_bl_libs\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'user_wl_libs'):
        check=cfg.user_wl_libs
        check_list=json.loads(check)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nuser_wl_libs=" + convert2json(check_list),2,the_dict)
        check_user_wllibs_length=len(check_list)
        if (check_user_wllibs_length > 0):
            #Check number of users matches the number of whitelist entries
            if not (check_user_wllibs_length == check_user_keys_length):
                error_found_in_mumc_config_py+='LegacyConfigValueError: \'user_wl_libs\' Number of configured users does not match the number of configured whitelists\n'
            else:
                error_found_in_mumc_config_py+=cfgCheck_forLibraries(check_list, userid_check_list, username_check_list, 'user_wl_libs')
        else:
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'user_wl_libs\' cannot be empty\n'

        config_dict['user_wl_libs']=check_list
    else:
        error_found_in_mumc_config_py+='LegacyConfigNameError: The \'user_wl_libs\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'api_query_attempts'):
        check=cfg.api_query_attempts
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\napi_query_attempts=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 0) and
                (check <= 16))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'api_query_attempts\' must be an integer; valid range 0 thru 16\n'
        else:
            config_dict['api_query_attempts']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'api_query_attempts\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'api_query_item_limit'):
        check=cfg.api_query_item_limit
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\napi_query_item_limit=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
                (check >= 1) and
                (check <= 10000))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'api_query_item_limit\' must be an integer; valid range 0 thru 10000\n'
        else:
            config_dict['api_query_item_limit']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'api_query_item_limit\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'api_query_cache_size'):
        check=cfg.api_query_cache_size
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\napi_query_cache_size=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) or (isinstance(check,float)) and
                (check >= 0) and
                (check <= 10000))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'api_query_cache_size\' must be a number; valid range 0 thru 10000\n'
        else:
            config_dict['api_query_cache_size']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'api_query_cache_size\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'api_query_cache_fallback_behavior'):
        check=cfg.api_query_cache_fallback_behavior.upper()
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\napi_query_cache_fallback_behavior='" + str(check) + "'",2,the_dict)
        if (
            not (isinstance(check,str)) and
                ((check == 'FIFO') or (check == 'LFU') or (check == 'LRU'))
       ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'api_query_cache_fallback_behavior\' must be a string; valid values \'FIFO\', \'LFU\', or \'LRU\'\n'
        else:
            config_dict['api_query_cache_fallback_behavior']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'api_query_cache_fallback_behavior\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

    if hasattr(cfg, 'api_query_cache_last_accessed_time'):
        check=cfg.api_query_cache_last_accessed_time
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\napi_query_cache_last_accessed_time=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) or (isinstance(check,float)) and
                (check >= 0) and
                (check <= 60000))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'api_query_cache_last_accessed_time\' must be a number; valid range 0 thru 60000\n'
        else:
            config_dict['api_query_cache_last_accessed_time']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'api_query_cache_last_accessed_time\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    if hasattr(cfg, 'DEBUG'):
        check=cfg.DEBUG
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nDEBUG=" + str(check),2,the_dict)
        if (
            not ((isinstance(check,int)) and
            (((check >= 0) and (check <= 4)) or
             check == 255))
        ):
            error_found_in_mumc_config_py+='LegacyConfigValueError: \'DEBUG\' must be a integer or bool; valid range 0 thru 4\n'
        else:
            config_dict['DEBUG']=check
    else:
        warning_found_in_mumc_config_py+='LegacyConfigNameWarning: The \'DEBUG\' variable is missing from ' + str(the_dict['mumc_path'] / the_dict['config_file_name']) + '\n'

#######################################################################################################

    
    #Other config options can be assumed before converting to yaml; notify user of these; then convert to yaml
    if not (warning_found_in_mumc_config_py == ''):
        warning_text="\nWARNING: One or more config variable(s) were missing from " + str(the_dict['mumc_path'] / the_dict['config_file_name']) + ".\n MUMC has assumed defaults values for the missing variable(s).\n Please be sure to review these variable(s) in " + str(the_dict['mumc_path']) + "/" + the_dict['config_file_name_yaml']
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log(warning_text,2,the_dict)
            appendTo_DEBUG_log("\n" + warning_found_in_mumc_config_py,2,the_dict)
        print(warning_text)
        print('\n' + warning_found_in_mumc_config_py)

    #Some config options have to be fixed before converting to yaml; notify user of these; then stop script
    if not (error_found_in_mumc_config_py == ''):
        error_text="\nERROR: MUMC unable to convert the legacy config to the new yaml format.\n Please add/fix the following variable(s) in: " + str(the_dict['mumc_path'] / the_dict['config_file_name'])
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log(error_text,2,the_dict)
            appendTo_DEBUG_log("\n" + error_found_in_mumc_config_py,2,the_dict)
        print(error_text)
        print('\n' + error_found_in_mumc_config_py)
        sys.exit(0)

#######################################################################################################
    return config_dict