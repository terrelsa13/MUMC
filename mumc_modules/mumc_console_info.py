# -*- coding: utf-8 -*-
import yaml
from datetime import datetime
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType,convert2json
from mumc_modules.mumc_versions import get_script_version,get_python_version,get_server_version,get_operating_system_info
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_season_episode import get_season_episode
from mumc_modules.mumc_days_since import get_days_since_played,get_days_since_created
from mumc_modules.mumc_output import appendTo_DEBUG_log


#print informational header to console
def print_informational_header(the_dict):
    strings_list_to_print=''
    strings_list_to_print+=the_dict['_console_separator'] + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'
    strings_list_to_print+='Time Stamp Start: ' + the_dict['date_time_now'].strftime('%Y%m%d%H%M%S') + '\n'
    strings_list_to_print+=the_dict['app_name_short'] + ' Version: ' + the_dict['script_version'] + '\n'
    strings_list_to_print+=the_dict['app_name_short'] + ' Config Version: ' + the_dict['version'] + '\n'
    strings_list_to_print+=the_dict['admin_settings']['server']['brand'].capitalize() + ' Version: ' + get_server_version(the_dict) + '\n'
    strings_list_to_print+='Python Version: ' + get_python_version() + '\n'
    strings_list_to_print+='OS Info: ' + get_operating_system_info() + '\n'
    strings_list_to_print+=the_dict['console_separator_'] + '\n'

    print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['headers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['headers']['script']['formatting'])


#print starting header to console
def print_starting_header(the_dict):
    strings_list_to_print=''
    strings_list_to_print+=the_dict['console_separator'] + '\n'
    strings_list_to_print+='Start...' + '\n'
    strings_list_to_print+='Cleaning media for server at: ' + the_dict['admin_settings']['server']['url'] + '\n'
    strings_list_to_print+=the_dict['console_separator_'] + '\n'

    print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['headers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['headers']['script']['formatting'])


#print header for specific user
def print_user_header(user_info,the_dict):
    strings_list_to_print=''
    strings_list_to_print+=the_dict['_console_separator'] + '\n'
    strings_list_to_print+='Get List Of Media For:' + '\n'
    strings_list_to_print+=user_info['user_name'] + ' - ' + user_info['user_id'] + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'

    print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['headers']['user']['show'],the_dict,the_dict['advanced_settings']['console_controls']['headers']['user']['formatting'])


#print cache statistics for cache tuning
def print_cache_stats(the_dict):
        strings_list_to_print=''
        strings_list_to_print+=the_dict['_console_separator'] + '\n'
        strings_list_to_print+='Cached Data Summary:' + '\n'
        strings_list_to_print+=the_dict['console_separator'] + '\n'
        strings_list_to_print+='Number of cache hits: ' + str(the_dict['cached_data'].cached_data_hits) + '\n'
        strings_list_to_print+='Number of cache misses: ' + str(the_dict['cached_data'].cached_data_misses) + '\n'
        strings_list_to_print+='Configured max cache size: ' + str(the_dict['cached_data'].api_query_cache_size) + '\n'
        strings_list_to_print+='Size of remaining data in cache: ' + str(the_dict['cached_data'].total_cached_data_size) + '\n'
        strings_list_to_print+='Size of all data removed from cache: ' + str(the_dict['cached_data'].total_cached_data_size_removed) + '\n'
        strings_list_to_print+='Size of all data remaining and removed from cache: ' + str(the_dict['cached_data'].total_data_size_thru_cache) + '\n'
        strings_list_to_print+='Newest cached item number (starts at 0): ' + str(the_dict['cached_data'].newest_cached_data_entry_number) + '\n'
        strings_list_to_print+='Oldest remaining cached item number (starts at 0): ' + str(the_dict['cached_data'].oldest_cached_data_entry_number) + '\n'
        strings_list_to_print+='Total remaining number of items in cache: ' + str(len(the_dict['cached_data'].cached_entry_urls)) + '\n'
        strings_list_to_print+='Total number of items through cache: ' + str(the_dict['cached_data'].total_cumulative_cached_data_entry_number) + '\n'
        strings_list_to_print+=the_dict['console_separator'] + '\n'

        print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['footers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['footers']['script']['formatting'])


#print all cached data elevated DEBUG value required
def cache_data_to_debug(the_dict):
    strings_list_to_print=''
    strings_list_to_print+='\nAll Cached URLs:' + '\n'
    strings_list_to_print+=convert2json(the_dict['cached_data'].cached_entry_urls) + '\n'
    strings_list_to_print+='\nAll Cached URL and Data Byte Sizes:' + '\n'
    strings_list_to_print+=convert2json(the_dict['cached_data'].cached_entry_sizes) + '\n'
    strings_list_to_print+='\nAll Cached URL Data Last Accessed Times:' + '\n'
    strings_list_to_print+=convert2json(the_dict['cached_data'].cached_entry_times) + '\n'
    strings_list_to_print+='\nAll Cached URLs And Data:' + '\n'
    strings_list_to_print+=convert2json(the_dict['cached_data'].cached_data) + '\n'

    print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['footers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['footers']['script']['formatting'])


#print ending footer and time to console
def print_footer_information(the_dict):
    strings_list_to_print=''
    strings_list_to_print+='Done.' + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'
    strings_list_to_print+=the_dict['_console_separator'] + '\n'
    strings_list_to_print+='Time Stamp End: ' + datetime.now().strftime('%Y%m%d%H%M%S') + '\n'
    strings_list_to_print+=the_dict['console_separator_'] + '\n'

    print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['footers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['footers']['script']['formatting'])


#there are times when new config option can be gracefully removed from the config yaml
 #when this is possible, print a warning notification to the console for the user to view
def print_config_options_removed_warning(the_dict,*yaml_sections):
    missing_accordion=''
    for yaml_section in yaml_sections:
        if (missing_accordion == ''):
            missing_accordion=yaml_section
        else:
            missing_accordion+=(' > ' + yaml_section)

    strings_list_to_print=''
    strings_list_to_print+=the_dict['console_separator'] + '\n'
    strings_list_to_print+='During the configuration check, the following option(s) were removed from the yaml configuration file...' + '\n'
    strings_list_to_print+='   ' + missing_accordion + '\n'
    strings_list_to_print+=the_dict['console_separator_'] + '\n'

    print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['warnings']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])


#there are times when new config option can be gracefully added to the config yaml
 #when this is possible, print a warning notification to the console for the user to view
def print_config_options_added_warning(the_dict,*yaml_sections):
    missing_accordion=''
    for yaml_section in yaml_sections:
        if (missing_accordion == ''):
            missing_accordion=yaml_section
        else:
            missing_accordion+=(' > ' + yaml_section)

    strings_list_to_print=''
    strings_list_to_print+=the_dict['console_separator'] + '\n'
    strings_list_to_print+='During the configuration check, the following option(s) were added to mumc_config.yaml file...' + '\n'
    strings_list_to_print+='   ' + missing_accordion + '\n'
    strings_list_to_print+=the_dict['console_separator_'] + '\n'

    print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['warnings']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])


#build and then print the individual media item data
def build_print_media_item_details(item,var_dict,the_dict):

    mediaType=var_dict['media_type_lower']
    isFavorited_Display=var_dict['isFavorited_Display']
    isFavorited_Display=var_dict['isFavorited_Display']
    isWhitetagged_Display=var_dict['isWhitetagged_Display']
    isBlacktagged_Display=var_dict['isBlacktagged_Display']
    isWhitelisted_Display=var_dict['isWhitelisted_Display']
    isBlacklisted_Display=var_dict['isBlacklisted_Display']
    showItemAsDeleted=var_dict['showItemAsDeleted']
    print_media_delete_info=var_dict['print_media_delete_info']
    print_media_keep_info=var_dict['print_media_keep_info']
    media_delete_info_format=var_dict['media_delete_info_format']
    media_keep_info_format=var_dict['media_keep_info_format']
    days_since_played=get_days_since_played(item['UserData']['LastPlayedDate'],the_dict)
    days_since_created=get_days_since_created(item['DateCreated'],the_dict)
    if (mediaType == 'episode'):
        season_episode=get_season_episode(item['ParentIndexNumber'],item['IndexNumber'],the_dict)

    strings_list=''

    if ('Played' in item['UserData']):
        try:

            strings_list+=item['Type']

            if (mediaType == 'movie'):
                strings_list+=' - ' + item['Name'] + ' - ' + item['Studios'][0]['Name']
            elif (mediaType == 'episode'):
                strings_list+=' - ' + item['SeriesName'] + ' - ' + season_episode + ' - ' + item['Name'] + ' - ' + item['SeriesStudio']
            elif (mediaType == 'audio'):
                strings_list+=' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Album: ' + item['Album'] + ' - Artist: ' + item['Artists'][0] + ' - Record Label: ' + item['Studios'][0]['Name']
            elif (mediaType == 'audiobook'):
                strings_list+=' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Book: ' + item['Album'] + ' - Author: ' +item['Artists'][0]

            strings_list+=' - ' + days_since_played + ' - Play Count: ' + str(item['UserData']['PlayCount']) + ' - ' + days_since_created + ' - Favorite: ' + str(isFavorited_Display) + ' - Whitetag: ' + \
                str(isWhitetagged_Display) + ' - Blacktag: ' + str(isBlacktagged_Display) + ' - Whitelisted: ' + str(isWhitelisted_Display) + ' - Blacklisted: ' + str(isBlacklisted_Display) + ' - ' + item['Type'] + 'ID: ' + item['Id']

        except (KeyError, IndexError):
            strings_list=''
            strings_list+=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('\nError encountered - ' + mediaType + ': \nitem: ' + str(item) + '\nitem' + str(item),2,the_dict)

        if (showItemAsDeleted):
            strings_list=':*[DELETE] - ' + strings_list
            print_media_info=print_media_delete_info
            media_info_format=media_delete_info_format
        else:
            strings_list=':[KEEPING] - ' + strings_list
            print_media_info=print_media_keep_info
            media_info_format=media_keep_info_format

        strings_list+='\n'

        print_byType(strings_list,print_media_info,the_dict,media_info_format)


#show the command line help text
def default_helper_menu(the_dict):
    strings_list_to_print=''
    strings_list_to_print+='\nFor help use -h or -help' + '\n'
    strings_list_to_print+='\n/path/to/python3.x /path/to/mumc.py -help' + '\n'
    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])


#show the full help menu
def print_full_help_menu(the_dict):
    strings_list_to_print=''
    strings_list_to_print+='\n' + the_dict['app_name_short'] + ' Version: ' + get_script_version() + '\n'
    strings_list_to_print+=the_dict['app_name_long'] + ' aka ' + the_dict['app_name_short'] + ' (pronounced Mew-Mick) will query movies, tv episodes, audio tracks, and audiobooks in your Emby/Jellyfin libraries and delete media_items you no longer want to keep.' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='Usage:' + '\n'
    strings_list_to_print+='/path/to/python3.x /path/to/mumc.py [-option] [arg]' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+'Options:' + '\n'
    strings_list_to_print+='-a, -attrs, -attributes       Show console attribute test output; will override all other options' + '\n'
    strings_list_to_print+='-c [path], -config [path]     Specify alternate *.py configuration file' + '\n'
    strings_list_to_print+='-d, -container                Script is running in a docker container' + '\n'
    strings_list_to_print+='-u, -config-updater           Modify configuration by adding users to the mumc_config.yaml' + '\n'
    #strings_list_to_print+='-rak, -remake-api-key         Delete the existing MUMC API key and make a new one.' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='-h, -help                     Show this help menu; will override all other options' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='Latest Release:' + '\n'
    strings_list_to_print+='https://github.com/terrelsa13/MUMC/releases' + '\n'
    strings_list_to_print+='\n'

    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])


def unknown_command_line_option_helper(cmdUnknown,the_dict):
    strings_list_to_print=''
    strings_list_to_print+='\nUnknownCMDOptionError: ' + str(cmdUnknown) + '\n'
    strings_list_to_print+='\n'

    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])


#print missing argument for alternate config helper
def missing_config_argument_helper(argv,the_dict):
    strings_list_to_print=''
    strings_list_to_print+='\n'
    strings_list_to_print+='CMDMissingPathError: Cannot find /path/to/alternate_config.yaml after -c' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='Verify the -c option looks like this: -c /path/to/alternate_config.yaml' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='or\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='Verify the -c option looks like this: -c c:\\path\\to\\alternate_config.yaml' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+=' '.join(argv) + '\n'
    strings_list_to_print+='\n'

    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])


#print missing config argument format error
def missing_config_argument_format_helper(argv,the_dict):
    strings_list_to_print=''
    strings_list_to_print+='\n'
    strings_list_to_print+='AlternateConfigArgumentError: Cannot find /path/to/alternate_config.yaml after -c' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='Verify the -c option looks like this: -c /path/to/alternate_config.yaml' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='or\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='Verify the -c option looks like this: -c c:\\path\\to\\alternate_config.yaml' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+=' '.join(argv) + '\n'
    strings_list_to_print+='\n'

    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])


#print alt config does not exist helper
def alt_config_file_does_not_exists_helper(argv,the_dict):
    strings_list_to_print=''
    strings_list_to_print+='\n'
    strings_list_to_print+='AlternateConfigNotFoundError: Alternate config path or file does not exist; check for typo, create config file, or move existing config to this location' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+=' '.join(argv) + '\n'
    strings_list_to_print+='\n'

    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])


#print alt config syntax helper
def alt_config_syntax_helper(argv,cmdOption,the_dict):
    strings_list_to_print=''
    strings_list_to_print+='\n'
    strings_list_to_print+='Alternate configuration file must have a .yml, .yaml, or .py extension and follow the Python module naming convention' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='These are NOT valid config file names:' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='\t' + argv[argv.index(cmdOption)+1] + '\n'
    strings_list_to_print+='\t/path/to/alternate.config.yml' + '\n'
    strings_list_to_print+='\t/path/to/alternate config.yml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternate.config.yml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternate config.yml' + '\n'
    strings_list_to_print+='\t/path/to/alternate.config.yaml' + '\n'
    strings_list_to_print+='\t/path/to/alternate config.yaml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternate.config.yaml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternate config.yaml' + '\n'
    strings_list_to_print+='\t/path/to/alternate.config.yaml' + '\n'
    strings_list_to_print+='\t/path/to/alternate config.yaml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternate.config.yaml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternate config.yaml' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='These are valid config file names:' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='\t/path/to/alternateconfig.yml' + '\n'
    strings_list_to_print+='\t/path/to/alternate_config.yml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternateconfig.yml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternate_config.yml' + '\n'
    strings_list_to_print+='\t/path/to/alternateconfig.yaml' + '\n'
    strings_list_to_print+='\t/path/to/alternate_config.yaml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternateconfig.yaml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternate_config.yaml' + '\n'
    strings_list_to_print+='\t/path/to/alternateconfig.yaml' + '\n'
    strings_list_to_print+='\t/path/to/alternate_config.yaml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternateconfig.yaml' + '\n'
    strings_list_to_print+='\tc:\\path\\to\\alternate_config.yaml' + '\n'
    strings_list_to_print+='\n'

    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])


#print unable to sucessfully load the Configuration file
def print_failed_to_load_config(the_dict):
    strings_list_to_print=''
    strings_list_to_print+=the_dict['_console_separator'] + '\n'
    strings_list_to_print+='Config file missing or cannot find alternate Config file.' + '\n'
    strings_list_to_print+='Or Config file missing \'DEBUG\' and/or \'version\' variables.' + '\n'
    strings_list_to_print+='Either point to the correct alternate Config file, add missing Config variables, or rebuild the Config by running: /path/to/python /path/to/mumc.py' + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'

    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])


#print unable to sucessfully load the Configuration file
def print_containerized_config_missing(the_dict):
    strings_list_to_print=''
    strings_list_to_print+=the_dict['_console_separator'] + '\n'
    strings_list_to_print+='Config file missing.' + '\n'
    strings_list_to_print+='Config file should be located at /usr/src/app/config/mumc_config.yaml inside of the container.' + '\n'
    strings_list_to_print+='\n'
    strings_list_to_print+='To build config run: docker exec -it mumc bash' + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'

    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])


#print all media disabled helper
def print_all_media_disabled(the_dict):
    strings_list_to_print=""

    strings_list_to_print+=the_dict['console_separator'] + '\n'
    strings_list_to_print+="* ATTENTION!!!                                                                         *" + '\n'
    strings_list_to_print+="* No media types are being monitored.                                                  *" + '\n'
    strings_list_to_print+="* Open the mumc_config.yaml file in a text editor.                                     *" + '\n'
    strings_list_to_print+="* Set at least one media type's condition_days >= 0.                                   *" + '\n'
    strings_list_to_print+="*                                                                                      *" + '\n'
    strings_list_to_print+="* basic_settings > filter_statements > movie > played > condition_days: -1             *" + '\n'
    strings_list_to_print+="* basic_settings > filter_statements > episode > played > condition_days: -1           *" + '\n'
    strings_list_to_print+="* basic_settings > filter_statements > audio > played > condition_days: -1             *" + '\n'
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        strings_list_to_print+="* basic_settings > filter_statements > audiobook > played > condition_days: -1         *" + '\n'
    strings_list_to_print+="*                                                                                      *" + '\n'
    strings_list_to_print+="* basic_settings > filter_statements > movie > created > condition_days: -1            *" + '\n'
    strings_list_to_print+="* basic_settings > filter_statements > episode > created > condition_days: -1          *" + '\n'
    strings_list_to_print+="* basic_settings > filter_statements > audio > created > condition_days: -1            *" + '\n'
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        strings_list_to_print+="* basic_settings > filter_statements > audiobook > created > condition_days: -1        *" + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'

    try:
        print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['warnings']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])
    except:
        print_byType(strings_list_to_print,True,the_dict,{'font':{'color':'','style':''},'background':{'color':''}})


#print how to delete files info
def remove_files_helper(strings_list_to_print,the_dict):
    strings_list_to_print+=the_dict['console_separator'] + '\n'
    strings_list_to_print+='To delete media, open mumc_config.yaml in a text editor:' + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'
    strings_list_to_print+='* Set advanced_settings > REMOVE_FILES: true' + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'

    return strings_list_to_print


#print new config info
def build_new_config_setup_to_delete_media(strings_list_to_print,the_dict):
    if (not (the_dict['advanced_settings']['REMOVE_FILES'])):
        strings_list_to_print+=the_dict['_console_separator'] + '\n'
        strings_list_to_print+='* Config file is not setup to delete media.' + '\n'
        strings_list_to_print+='* Config file is in dry run mode to prevent deleting media.' + '\n'

        strings_list_to_print=remove_files_helper(strings_list_to_print,the_dict)

        return strings_list_to_print


#print build config how to delete files info
def build_config_setup_to_delete_media(strings_list_to_print,the_dict,delete_item_type):
    strings_list_to_print+=the_dict['_console_separator'] + '\n'
    strings_list_to_print+='Summary Of Deleted ' + delete_item_type + ':' + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'

    if not bool(the_dict['advanced_settings']['REMOVE_FILES']):
        strings_list_to_print+='* Dry Run Mode' + '\n'
        strings_list_to_print+='* advanced_settings > REMOVE_FILES: false' + '\n'
        strings_list_to_print+='* No Media Deleted' + '\n'
        strings_list_to_print+='* Items = ' + str(the_dict['deleteItemsLength']) + '\n'

        strings_list_to_print=remove_files_helper(strings_list_to_print,the_dict)

    else:
        strings_list_to_print+='* Items Deleted = ' + str(the_dict['deleteItemsLength']) + '    *' + '\n'
        strings_list_to_print+=the_dict['console_separator'] + '\n'

    return strings_list_to_print


#print post processing started
def print_post_processing_started(the_dict,postproc_dict):
    strings_list_to_print=''
    strings_list_to_print+='\n' + postproc_dict['media_type_upper'] + ' POST PROCESSING STARTED...' + '\n'

    print_byType(strings_list_to_print,postproc_dict['print_media_post_processing'],the_dict,postproc_dict['media_post_processing_format'])


#print post processing verbal progress info
def print_post_processing_verbal_progress(the_dict,postproc_dict,prost_processing_step):
    strings_list_to_print=''

    if (not(postproc_dict['media_type_lower'] == 'audio')):
        strings_list_to_print+='\nPROCESSING ' + prost_processing_step.upper() + ' ' + postproc_dict['media_type_upper'] + 'S...' + '\n'
    else:
        strings_list_to_print+='\nPROCESSING ' + prost_processing_step.upper() + ' ' + postproc_dict['media_type_upper'] + '...' + '\n'

    print_byType(strings_list_to_print,postproc_dict['print_media_post_processing'],the_dict,postproc_dict['media_post_processing_format'])


#print post processing verbal progress info for minimum episodes
def print_post_processing_verbal_progress_min_episode(the_dict,postproc_dict):
    strings_list_to_print=''
    strings_list_to_print+='\nPROCESSING MINIMUM NUMBER ' + postproc_dict['media_type_upper'] + 'S...' + '\n'

    print_byType(strings_list_to_print,postproc_dict['print_media_post_processing'],the_dict,postproc_dict['media_post_processing_format'])


#print post processing completed
def print_post_processing_completed(the_dict,postproc_dict):
    strings_list_to_print=''
    strings_list_to_print+='\n' + postproc_dict['media_type_upper'] + ' POST PROCESSING COMPLETE.' + '\n'

    print_byType(strings_list_to_print,postproc_dict['print_media_post_processing'],the_dict,postproc_dict['media_post_processing_format'])
    
    
def print_configuration_yaml(the_dict,init_dict):
    cfg_out={}
    cfg_out['version']=the_dict['version']
    cfg_out['basic_settings']=the_dict['basic_settings']
    cfg_out['advanced_settings']=the_dict['advanced_settings']
    cfg_out['admin_settings']=the_dict['admin_settings']
    cfg_out['DEBUG']=the_dict['DEBUG']
    the_dict['text_attrs']=init_dict['text_attrs']

    print_byType('---\n',True,the_dict,the_dict['advanced_settings']['console_controls']['headers']['script']['formatting'])
    print_byType(yaml.safe_dump(cfg_out,sort_keys=False),True,the_dict,the_dict['advanced_settings']['console_controls']['headers']['script']['formatting'])
    print_byType('...\n',True,the_dict,the_dict['advanced_settings']['console_controls']['headers']['script']['formatting'])
    
    the_dict.pop('text_attrs')