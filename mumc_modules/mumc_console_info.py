#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType,convert2json
from mumc_modules.mumc_versions import get_script_version,get_python_version,get_server_version,get_operating_system_info
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_season_episode import get_season_episode
from mumc_modules.mumc_delete import delete_media_item
from mumc_modules.mumc_days_since import get_days_since_played,get_days_since_created


#concatenate to the running list of strings
def concat_to_console_strings_list(strings_list,string_to_append):
    string_list_len=len(strings_list)

    for x in range(string_list_len):
        strings_list[x]+=string_to_append + '\n'

    return strings_list


#precatenate to the running list of strings
def precat_to_console_strings_list(string_to_prepend,strings_list):
    string_list_len=len(strings_list)

    for x in range(string_list_len):
        strings_list[x]=string_to_prepend + strings_list[x] + '\n'

    return strings_list


#print informational header to console
def print_informational_header(the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['_console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'MUMC Version: ' + the_dict['script_version'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'MUMC Config Version: ' + the_dict['version'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['admin_settings']['server']['brand'].capitalize() + ' Version: ' + get_server_version(the_dict))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Python Version: ' + get_python_version())
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'OS Info: ' + get_operating_system_info())
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Time Stamp Start: ' + the_dict['date_time_now'].strftime('%Y%m%d%H%M%S'))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator_'])

    print_byType(strings_list_to_print[0],the_dict['advanced_settings']['console_controls']['headers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['headers']['script']['formatting'])


#print starting header to console
def print_starting_header(the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Start...')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Cleaning media for server at: ' + the_dict['admin_settings']['server']['url'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator_'])

    print_byType(strings_list_to_print[0],the_dict['advanced_settings']['console_controls']['headers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['headers']['script']['formatting'])


#print header for specific user
def print_user_header(user_info,the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['_console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Get List Of Media For:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,user_info['user_name'] + ' - ' + user_info['user_id'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])

    print_byType(strings_list_to_print[0],the_dict['advanced_settings']['console_controls']['headers']['user']['show'],the_dict,the_dict['advanced_settings']['console_controls']['headers']['user']['formatting'])


#print cache statistics for cache tuning
def print_cache_stats(the_dict):
    if (the_dict['DEBUG']):
        strings_list_to_print=['']
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['_console_separator'])
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Cached Data Summary:')
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Number of cache hits: ' + str(the_dict['cached_data'].cached_data_hits))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Number of cache misses: ' + str(the_dict['cached_data'].cached_data_misses))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Configured max cache size: ' + str(the_dict['cached_data'].api_query_cache_size))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Size of remaining data in cache: ' + str(the_dict['cached_data'].total_cached_data_size))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Size of all data removed from cache: ' + str(the_dict['cached_data'].total_cached_data_size_removed))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Size of all data remaining and removed from cache: ' + str(the_dict['cached_data'].total_data_size_thru_cache))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Newest cached item number (starts at 0): ' + str(the_dict['cached_data'].newest_cached_data_entry_number))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Oldest remaining cached item number (starts at 0): ' + str(the_dict['cached_data'].oldest_cached_data_entry_number))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Total remaining number of items in cache: ' + str(len(the_dict['cached_data'].cached_entry_urls)))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Total number of items through cache: ' + str(the_dict['cached_data'].total_cumulative_cached_data_entry_number))
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])

        print_byType(strings_list_to_print[0],the_dict['advanced_settings']['console_controls']['footers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['footers']['script']['formatting'])


#print all cached data elevated DEBUG value required
def cache_data_to_debug(the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nAll Cached URLs:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,convert2json(the_dict['cached_data'].cached_entry_urls))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nAll Cached URL and Data Byte Sizes:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,convert2json(the_dict['cached_data'].cached_entry_sizes))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nAll Cached URL Data Last Accessed Times:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,convert2json(the_dict['cached_data'].cached_entry_times))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nAll Cached URLs And Data:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,convert2json(the_dict['cached_data'].cached_data))

    print_byType(strings_list_to_print[0],the_dict['advanced_settings']['console_controls']['footers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['footers']['script']['formatting'])


#print ending footer and time to console
def print_footer_information(the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['_console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Time Stamp End: ' + datetime.now().strftime('%Y%m%d%H%M%S'))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator_'])

    print_byType(strings_list_to_print[0],the_dict['advanced_settings']['console_controls']['footers']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['footers']['script']['formatting'])


#there are times when new config option can be gracefully removed from the config yaml
 #when this is possible, print a warning notification to the console for the user to view
def print_config_options_removed_warning(the_dict,*yaml_sections):
    missing_accordion=''
    for yaml_section in yaml_sections:
        if (missing_accordion == ''):
            missing_accordion=yaml_section
        else:
            missing_accordion+=(' > ' + yaml_section)

    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'During the configuration check, the following option(s) were removed from the yaml configuration file...')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'   ' + missing_accordion)
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator_'])

    print_byType(strings_list_to_print[0],the_dict['advanced_settings']['console_controls']['warnings']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])


#there are times when new config option can be gracefully added to the config yaml
 #when this is possible, print a warning notification to the console for the user to view
def print_config_options_added_warning(the_dict,*yaml_sections):
    missing_accordion=''
    for yaml_section in yaml_sections:
        if (missing_accordion == ''):
            missing_accordion=yaml_section
        else:
            missing_accordion+=(' > ' + yaml_section)

    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'During the configuration check, the following option(s) were added to the yaml configuration file...')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'   ' + missing_accordion)
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator_'])

    print_byType(strings_list_to_print[0],the_dict['advanced_settings']['console_controls']['warnings']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])


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

    strings_list=['']

    if ('Played' in item['UserData']):
        try:

            strings_list[0]=strings_list[0] + item['Type']

            if (mediaType == 'movie'):
                strings_list[0]=strings_list[0] + ' - ' + item['Name'] + ' - ' + item['Studios'][0]['Name']
            elif (mediaType == 'episode'):
                strings_list[0]=strings_list[0] + ' - ' + item['SeriesName'] + ' - ' + season_episode + ' - ' + item['Name'] + ' - ' + item['SeriesStudio']
            elif (mediaType == 'audio'):
                strings_list[0]=strings_list[0] + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Album: ' + item['Album'] + ' - Artist: ' + item['Artists'][0] + ' - Record Label: ' + item['Studios'][0]['Name']
            elif (mediaType == 'audiobook'):
                strings_list[0]=strings_list[0] + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Book: ' + item['Album'] + ' - Author: ' +item['Artists'][0]

            strings_list[0]=strings_list[0] + ' - ' + days_since_played + ' - Play Count: ' + str(item['UserData']['PlayCount']) + ' - ' + days_since_created + ' - Favorite: ' + str(isFavorited_Display) + ' - Whitetag: ' + \
                str(isWhitetagged_Display) + ' - Blacktag: ' + str(isBlacktagged_Display) + ' - Whitelisted: ' + str(isWhitelisted_Display) + ' - Blacklisted: ' + str(isBlacklisted_Display) + ' - ' + item['Type'] + 'ID: ' + item['Id']

        except (KeyError, IndexError):
            strings_list[0]=['']
            strings_list[0]=strings_list[0] + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('\nError encountered - ' + mediaType + ': \nitem: ' + str(item) + '\nitem' + str(item),2,the_dict)

        if (showItemAsDeleted):
            strings_list[0]=':*[DELETE] - ' + strings_list[0]
            print_media_info=print_media_delete_info
            media_info_format=media_delete_info_format
        else:
            strings_list[0]=':[KEEPING] - ' + strings_list[0]
            print_media_info=print_media_keep_info
            media_info_format=media_keep_info_format

        strings_list=concat_to_console_strings_list(strings_list,'')

        print_byType(strings_list[0],print_media_info,the_dict,media_info_format)


#list and delete items past played threshold
def print_and_delete_items(deleteItems,the_dict):
    deleteItems_Tracker=[]
    print_summary_header=the_dict['advanced_settings']['console_controls']['headers']['summary']['show']
    print_movie_summary=the_dict['advanced_settings']['console_controls']['movie']['summary']['show']
    print_episode_summary=the_dict['advanced_settings']['console_controls']['episode']['summary']['show']
    print_audio_summary=the_dict['advanced_settings']['console_controls']['audio']['summary']['show']
    summary_header_format=the_dict['advanced_settings']['console_controls']['headers']['summary']['formatting']
    movie_summary_format=the_dict['advanced_settings']['console_controls']['movie']['summary']['formatting']
    episode_summary_format=the_dict['advanced_settings']['console_controls']['episode']['summary']['formatting']
    audio_summary_format=the_dict['advanced_settings']['console_controls']['audio']['summary']['formatting']
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        print_audiobook_summary=the_dict['advanced_settings']['console_controls']['audiobook']['summary']['show']
        audiobook_summary_format=the_dict['advanced_settings']['console_controls']['audiobook']['summary']['formatting']
    else:
        print_audiobook_summary=False
        audiobook_summary_format={'font':{'color':'','style':''},'background':{'color':''}}

    #get number of items to be deleted
     #have to loop thru and look for item_ids because some media has almost
      #the same data and would not be filtered out by turning this into a set
    for item in deleteItems:
        if (not(item['Id'] in deleteItems_Tracker)):
            deleteItems_Tracker.append(item['Id'])
    the_dict['deleteItemsLength']=len(deleteItems_Tracker)
    #clear tracker so it can be used again below
    deleteItems_Tracker.clear()

    #List items to be deleted
    strings_list_to_print=['']
    strings_list_to_print=build_config_setup_to_delete_media(strings_list_to_print,deleteItems,the_dict)

    print_byType(strings_list_to_print[0],print_summary_header,the_dict,summary_header_format)

    if len(deleteItems) > 0:
        for item in deleteItems:

            strings_list_to_print=['']

            if (not(item['Id'] in deleteItems_Tracker)):
                deleteItems_Tracker.append(item['Id'])
                if item['Type'] == 'Movie':
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    #Delete media item
                    delete_media_item(item['Id'],the_dict)
                    #Print output for deleted media item
                    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,item_output_details)
                    print_byType(strings_list_to_print[0],print_movie_summary,the_dict,movie_summary_format)
                elif item['Type'] == 'Episode':
                    try:
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'],item['IndexNumber'],the_dict) + ' - ' + item['Name'] + ' - ' + item['Id']
                    except (KeyError, IndexError):
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log('Error encountered - Delete Episode: \n\n' + str(item),2,the_dict)
                    #Delete media item
                    delete_media_item(item['Id'],the_dict)
                    #Print output for deleted media item
                    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,item_output_details)
                    print_byType(strings_list_to_print[0],print_episode_summary,the_dict,episode_summary_format)
                elif item['Type'] == 'Audio':
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Artists'][0] + ' ' + item['Album'] + ' ' + str(item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']
                    #Delete media item
                    delete_media_item(item['Id'],the_dict)
                    #Print output for deleted media item
                    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,item_output_details)
                    print_byType(strings_list_to_print[0],print_audio_summary,the_dict,audio_summary_format)
                elif item['Type'] == 'AudioBook':
                    #if (the_dict['DEBUG']):
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Artists'][0] + ' ' + item['Album'] + ' ' + str(item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']
                    #Delete media item
                    delete_media_item(item['Id'],the_dict)
                    #Print output for deleted media item
                    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,item_output_details)
                    print_byType(strings_list_to_print[0],print_audiobook_summary,the_dict,audiobook_summary_format)
                else: # item['Type'] == 'Unknown':
                    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Not Able To Delete Unknown Media Type')
                    print_byType(strings_list_to_print[0],True,the_dict,the_dict['formatting'])
    else:
        strings_list_to_print=['']
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'[NO ITEMS TO DELETE]')
        print_byType(strings_list_to_print[0],print_summary_header,the_dict,summary_header_format)

    strings_list_to_print=['']

    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['_console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Done.')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])

    print_byType(strings_list_to_print[0],print_summary_header,the_dict,summary_header_format)


#show the command line help text
def default_helper_menu(the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nFor help use -h or -help')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\n/path/to/python3.x /path/to/mumc.py -help')
    print_byType(strings_list_to_print[0],True,the_dict,the_dict['formatting'])


#show the full help menu
def print_full_help_menu(the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nMUMC Version: ' + get_script_version())
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Multi-User Media Cleaner aka MUMC (pronounced Mew-Mick) will query movies, tv episodes, audio tracks, and audiobooks in your Emby/Jellyfin libraries and delete media_items you no longer want to keep.')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Usage:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'/path/to/python3.x /path/to/mumc.py [-option] [arg]')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Options:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'-a -attrs, -attributes      Show console attribute test output')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'-c [path], -config [path]   Specify alternate *.py configuration file')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'-d, -container              Script is running in a docker container')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'-h, -help                   Show this help menu; will override all other options')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Latest Release:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'https://github.com/terrelsa13/MUMC/releases')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')

    print_byType(strings_list_to_print[0],True,the_dict,the_dict['formatting'])


def unknown_command_line_option_helper(cmdUnknown,the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nUnknownCMDOptionError: ' + str(cmdUnknown))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')

    print_byType(strings_list_to_print[0],True,the_dict,the_dict['formatting'])


#print missing argument for alternate config helper
def missing_config_argument_helper(argv,the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'CMDOptionIndexError: Cannot find /path/to/alternate_config.yaml after -c')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Verify the \'-c\' option looks like this: -c /path/to/alternate_config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,' '.join(argv))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')

    print_byType(strings_list_to_print[0],True,the_dict,the_dict['formatting'])


#print missing config argument format error
def missing_config_argument_format_helper(argv,the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'AlternateConfigArgumentError: Cannot find /path/to/alternate_config.yaml after -c')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Verify the \'-c\' option looks like this: -c /path/to/alternate_config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,' '.join(argv))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')

    print_byType(strings_list_to_print[0],True,the_dict,the_dict['formatting'])


#print alt config does not exist helper
def alt_config_file_does_not_exists_helper(argv,the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'AlternateConfigNotFoundError: Alternate config path or file does not exist; check for typo or create file')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,' '.join(argv))
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')

    print_byType(strings_list_to_print[0],True,the_dict,the_dict['formatting'])


#print alt config syntax helper
def alt_config_syntax_helper(argv,cmdOption,the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Alternate configuration file must have a .yml, .yaml, or .py extension and follow the Python module naming convention')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'These are NOT valid config file names:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t' + argv[argv.index(cmdOption)+1])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternate.config.yml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternate config.yml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternate.config.yml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternate config.yml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternate.config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternate config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternate.config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternate config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternate.config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternate config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternate.config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternate config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'These are valid config file names:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternateconfig.yml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternate_config.yml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternateconfig.yml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternate_config.yml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternateconfig.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternate_config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternateconfig.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternate_config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternateconfig.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\t/path/to/alternate_config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternateconfig.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\tc:\\path\\to\\alternate_config.yaml')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'')

    print_byType(strings_list_to_print[0],True,the_dict,the_dict['formatting'])


#print unable to sucessfully load the Configuration file
def print_failed_to_load_config(the_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'_console_separator')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Config file missing or cannot find alternate Config file.')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Or Config file missing \'DEBUG\' and/or \'server_brand\' variables.')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Either point to the correct alternate Config file, add missing Config variables, or rebuild the Config by running: /path/to/python /path/to/mumc.py')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'console_separator')

    print_byType(strings_list_to_print[0],True,the_dict,the_dict['formatting'])


#print all media disabled helper
def print_all_media_disabled(the_dict):
    strings_list_to_print=[""]

    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* ATTENTION!!!                                                                         *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* No media types are being monitored.                                                  *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* Open the mumc_config.yaml file in a text editor.                                     *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* Set at least one media type's condition_days >= 0.                                   *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"*                                                                                      *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* basic_settings > filter_statements > movie > played > condition_days: -1             *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* basic_settings > filter_statements > episode > played > condition_days: -1           *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* basic_settings > filter_statements > audio > played > condition_days: -1             *")
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* basic_settings > filter_statements > audiobook > played > condition_days: -1         *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"*                                                                                      *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* basic_settings > filter_statements > movie > created > condition_days: -1            *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* basic_settings > filter_statements > episode > created > condition_days: -1          *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* basic_settings > filter_statements > audio > created > condition_days: -1            *")
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,"* basic_settings > filter_statements > audiobook > created > condition_days: -1        *")
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])

    print_byType(strings_list_to_print[0],the_dict['advanced_settings']['console_controls']['warnings']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])


#print how to delete files info
def remove_files_helper(strings_list_to_print,the_dict):
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'To delete media, open mumc_config.yaml in a text editor:')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'* Set advanced_settings > REMOVE_FILES: true')
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])

    return strings_list_to_print


#print new config info
def build_new_config_setup_to_delete_media(strings_list_to_print,the_dict):
    if not (the_dict['advanced_settings']['REMOVE_FILES']):
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['_console_separator'])
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'* Config file is not setup to delete media.')
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'* Config file is in dry run mode to prevent deleting media.')

        strings_list_to_print=remove_files_helper(strings_list_to_print,the_dict)

        return strings_list_to_print


#print build config how to delete files info
def build_config_setup_to_delete_media(strings_list_to_print,deleteItems,the_dict):
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['_console_separator'])
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'Summary Of Deleted Media:')

    if not bool(the_dict['advanced_settings']['REMOVE_FILES']):
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'* Dry Run Mode')
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'* advanced_settings > REMOVE_FILES: false')
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'* No Media Deleted')
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'* Items = ' + str(the_dict['deleteItemsLength']))

        strings_list_to_print=remove_files_helper(strings_list_to_print,the_dict)

    else:
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'* Items Deleted = ' + str(the_dict['deleteItemsLength']) + '    *')
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,the_dict['console_separator'])

    return strings_list_to_print


#print post processing started
def print_post_processing_started(the_dict,postproc_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\n' + postproc_dict['media_type_upper'] + ' POST PROCESSING STARTED...')

    print_byType(strings_list_to_print[0],postproc_dict['print_media_post_processing'],the_dict,postproc_dict['media_post_processing_format'])


#print post processing verbal progress info
def print_post_processing_verbal_progress(the_dict,postproc_dict,prost_processing_step):
    strings_list_to_print=['']

    if (not(postproc_dict['media_type_lower'] == 'audio')):
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nPROCESSING ' + prost_processing_step.upper() + ' ' + postproc_dict['media_type_upper'] + 'S...')
    else:
        strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nPROCESSING ' + prost_processing_step.upper() + ' ' + postproc_dict['media_type_upper'] + '...')

    print_byType(strings_list_to_print[0],postproc_dict['print_media_post_processing'],the_dict,postproc_dict['media_post_processing_format'])


#print post processing verbal progress info for minimum episodes
def print_post_processing_verbal_progress_min_episode(the_dict,postproc_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\nPROCESSING MINIMUM NUMBER ' + postproc_dict['media_type_upper'] + 'S...')

    print_byType(strings_list_to_print[0],postproc_dict['print_media_post_processing'],the_dict,postproc_dict['media_post_processing_format'])


#print post processing completed
def print_post_processing_completed(the_dict,postproc_dict):
    strings_list_to_print=['']
    strings_list_to_print=concat_to_console_strings_list(strings_list_to_print,'\n' + postproc_dict['media_type_upper'] + ' POST PROCESSING COMPLETE.')

    print_byType(strings_list_to_print[0],postproc_dict['print_media_post_processing'],the_dict,postproc_dict['media_post_processing_format'])