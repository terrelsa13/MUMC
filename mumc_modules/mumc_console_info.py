#!/usr/bin/env python3
from datetime import datetime
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType,convert2json
from mumc_modules.mumc_versions import get_script_version,get_python_version,get_server_version,get_operating_system_info
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_season_episode import get_season_episode
from mumc_modules.mumc_delete import delete_media_item
from mumc_modules.mumc_url import requestURL


def print_informational_header(the_dict):
    if (the_dict['DEBUG']):
        the_dict['print_script_header']=True
    else:
        the_dict['print_script_header']=the_dict['print_script_header']

    print_byType('\n-----------------------------------------------------------',the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('',the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('-----------------------------------------------------------',the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('MUMC Version: ' + get_script_version(),the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType(the_dict['server_brand'].capitalize() + ' Version: ' + get_server_version(the_dict),the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('Python Version: ' + get_python_version(),the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    appendTo_DEBUG_log('OS Info: ' + get_operating_system_info(),1,the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('Time Stamp: ' + the_dict['date_time_now'].strftime('%Y%m%d%H%M%S'),the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('-----------------------------------------------------------\n',the_dict['print_script_header'],the_dict)


def print_starting_header(the_dict):
    if (the_dict['DEBUG']):
        #Double newline for debug log formatting
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('-----------------------------------------------------------',the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('Start...',the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('Cleaning media for server at: ' + the_dict['server_url'],the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('-----------------------------------------------------------',the_dict['print_script_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('',the_dict['print_script_header'],the_dict)


#print header for specific user
def print_user_header(user_key,the_dict):
    #for user_key in user_keys_json:
    url=the_dict['server_url'] + '/Users/' + user_key  + '/?api_key=' + the_dict['auth_key']

    user_data=requestURL(url, the_dict['DEBUG'], 'current_user', the_dict['api_query_attempts'],the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('',the_dict['print_user_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('-----------------------------------------------------------',the_dict['print_user_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('Get List Of Media For:',the_dict['print_user_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType(user_data['Name'] + ' - ' + user_data['Id'],the_dict['print_user_header'],the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)
    print_byType('-----------------------------------------------------------',the_dict['print_user_header'],the_dict)


def print_cache_stats(the_dict):
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('-----------------------------------------------------------',the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Cached Data Summary:',the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('-----------------------------------------------------------',the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Number of cache hits: ' + str(the_dict['cached_data'].cached_data_hits),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Number of cache misses: ' + str(the_dict['cached_data'].cached_data_misses),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('',the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Configured max cache size: ' + str(the_dict['cached_data'].api_query_cache_size),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Size of remaining data in cache: ' + str(the_dict['cached_data'].total_cached_data_size),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Size of all data removed from cache: ' + str(the_dict['cached_data'].total_cached_data_size_removed),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Size of all data remaining and removed from cache: ' + str(the_dict['cached_data'].total_data_size_thru_cache),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('',the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Newest cached item number (starts at 0): ' + str(the_dict['cached_data'].newest_cached_data_entry_number),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Oldest remaining cached item number (starts at 0): ' + str(the_dict['cached_data'].oldest_cached_data_entry_number),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Total remaining number of items in cache: ' + str(len(the_dict['cached_data'].cached_entry_urls)),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('Total number of items through cache: ' + str(the_dict['cached_data'].total_cumulative_cached_data_entry_number),the_dict['print_script_footer'],the_dict)
        appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
        print_byType('',the_dict['print_script_footer'],the_dict)


def print_cache_data(the_dict):
    appendTo_DEBUG_log('\n',5,the_dict)
    appendTo_DEBUG_log('\nAll Cached URLs:',5,the_dict)
    appendTo_DEBUG_log('\n',5,the_dict)
    appendTo_DEBUG_log(convert2json(the_dict['cached_data'].cached_entry_urls),5,the_dict)
    appendTo_DEBUG_log('\n',5,the_dict)
    appendTo_DEBUG_log('\nAll Cached URL and Data Byte Sizes:',5,the_dict)
    appendTo_DEBUG_log('\n',5,the_dict)
    appendTo_DEBUG_log(convert2json(the_dict['cached_data'].cached_entry_sizes),5,the_dict)
    appendTo_DEBUG_log('\n',5,the_dict)
    appendTo_DEBUG_log('\nAll Cached URL Data Last Accessed Times:',5,the_dict)
    appendTo_DEBUG_log('\n',5,the_dict)
    appendTo_DEBUG_log(convert2json(the_dict['cached_data'].cached_entry_times),5,the_dict)
    appendTo_DEBUG_log('\n',5,the_dict)
    appendTo_DEBUG_log('\nAll Cached URLs And Data:',5,the_dict)
    appendTo_DEBUG_log('\n',5,the_dict)
    appendTo_DEBUG_log(convert2json(the_dict['cached_data'].cached_data),5,the_dict)
    appendTo_DEBUG_log('\n',5,the_dict)


def print_footer_information(the_dict):
    appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
    print_byType('-----------------------------------------------------------',the_dict['print_script_footer'],the_dict)
    appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
    print_byType('Time Stamp: ' + datetime.now().strftime('%Y%m%d%H%M%S'),the_dict['print_script_footer'],the_dict)
    appendTo_DEBUG_log('\n',the_dict['print_script_footer'],the_dict)
    print_byType('-----------------------------------------------------------',the_dict['print_script_footer'],the_dict)


#build and then print the individual media item data
def build_print_media_item_details(the_dict,item,mediaType,output_state_dict,days_since_played,days_since_created,season_episode=None):

    if ('Played' in item['UserData']):
        try:

            item_output_details=item['Type']

            if (mediaType.lower() == 'movie'):
                item_output_details=(item_output_details + ' - ' + item['Name'] + ' - ' + item['Studios'][0]['Name'])
            elif (mediaType.lower() == 'episode'):
                item_output_details=(item_output_details + ' - ' + item['SeriesName'] + ' - ' + season_episode +
                                     ' - ' + item['Name'] + ' - ' + item['SeriesStudio'])
            elif (mediaType.lower() == 'audio'):
                item_output_details=(item_output_details + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Album: ' + item['Album'] + ' - Artist: ' +
                                     item['Artists'][0] + ' - Record Label: ' + item['Studios'][0]['Name'])
            elif (mediaType.lower() == 'audiobook'):
                item_output_details=(item_output_details + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Book: ' + item['Album'] +
                                     ' - Author: ' +item['Artists'][0])

            item_output_details=(item_output_details + ' - ' + days_since_played + ' - Play Count: ' + str(item['UserData']['PlayCount']) + ' - ' + days_since_created + ' - Favorite: ' +
                                 str(output_state_dict['isFavorited_Display']) + ' - WhiteTag: ' + str(output_state_dict['isWhiteTagged_Display']) + ' - BlackTag: ' +
                                 str(output_state_dict['isBlackTagged_Display']) + ' - Whitelisted: ' + str(output_state_dict['isWhiteListed_Display']) + ' - Blacklisted: ' +
                                 str(output_state_dict['isBlackListed_Display']) + ' - ' + item['Type'] + 'ID: ' + item['Id'])

        except (KeyError, IndexError):
            item_output_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('\nError encountered - ' + mediaType.upper() + ': \nitem: ' + str(item) + '\nitem' + str(item),2,the_dict)

        if (the_dict['DEBUG']):
            print_media_delete_info=True
            print_media_keep_info=True
            appendTo_DEBUG_log("\n\n",1,the_dict)
        else:
            print_media_delete_info=output_state_dict['print_media_delete_info']
            print_media_keep_info=output_state_dict['print_media_keep_info']

        if (output_state_dict['showItemAsDeleted']):
            print_byType(':*[DELETE] - ' + item_output_details,print_media_delete_info,the_dict)
        else:
            print_byType(':[KEEPING] - ' + item_output_details,print_media_keep_info,the_dict)

        if (the_dict['DEBUG']):
            #Spacing for debug file
            appendTo_DEBUG_log("\n",1,the_dict)


#list and delete items past played threshold
def print_and_delete_items(deleteItems,the_dict):
    deleteItems_Tracker=[]
    print_summary_header=the_dict['print_summary_header']
    print_movie_summary=the_dict['print_movie_summary']
    print_episode_summary=the_dict['print_episode_summary']
    print_audio_summary=the_dict['print_audio_summary']
    if (isJellyfinServer(the_dict['server_brand'])):
        print_audiobook_summary=the_dict['print_audiobook_summary']
    else:
        print_audiobook_summary=False

    if (the_dict['DEBUG']):
        print_summary_header=True
        print_movie_summary=True
        print_episode_summary=True
        print_audio_summary=True
        if (isJellyfinServer(the_dict['server_brand'])):
            print_audiobook_summary=True
        else:
            print_audiobook_summary=False

    print_common_summary = (print_movie_summary or print_episode_summary or print_audio_summary or print_audiobook_summary)

    #List items to be deleted
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('-----------------------------------------------------------',print_summary_header,the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('Summary Of Deleted Media:',print_summary_header,the_dict)
    if not bool(the_dict['REMOVE_FILES']):
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('* Trial Run Mode',print_summary_header,the_dict)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('* REMOVE_FILES=\'False\'',print_summary_header,the_dict)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('* No Media Deleted',print_summary_header,the_dict)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('* Items = ' + str(len(deleteItems)),print_summary_header,the_dict)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('-----------------------------------------------------------',print_summary_header,the_dict)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('To delete media open mumc_config.py in a text editor:',print_summary_header,the_dict)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('* Set REMOVE_FILES=\'True\'',print_summary_header,the_dict)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('-----------------------------------------------------------',(print_summary_header or print_common_summary),the_dict)
    else:
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('* Items Deleted = ' + str(len(deleteItems)) + '    *',print_summary_header,the_dict)
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('-----------------------------------------------------------',(print_summary_header or print_common_summary),the_dict)

    if len(deleteItems) > 0:
        for item in deleteItems:
            if (not(item['Id'] in deleteItems_Tracker)):
                deleteItems_Tracker.append(item['Id'])
                if item['Type'] == 'Movie':
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n",1,the_dict)
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    #Delete media item
                    delete_media_item(item['Id'],the_dict)
                    #Print output for deleted media item
                    print_byType(item_output_details,print_movie_summary,the_dict)
                elif item['Type'] == 'Episode':
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n",1,the_dict)
                    try:
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'],item['IndexNumber'],the_dict) + ' - ' + item['Name'] + ' - ' + item['Id']
                    except (KeyError, IndexError):
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log('Error encountered - Delete Episode: \n\n' + str(item),2,the_dict)
                    #Delete media item
                    delete_media_item(item['Id'],the_dict)
                    #Print output for deleted media item
                    print_byType(item_output_details,print_episode_summary,the_dict)
                elif item['Type'] == 'Audio':
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n",1,the_dict)
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Artists'][0] + ' ' + item['Album'] + ' ' + str(item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']
                    #Delete media item
                    delete_media_item(item['Id'],the_dict)
                    #Print output for deleted media item
                    print_byType(item_output_details,print_audio_summary,the_dict)
                elif item['Type'] == 'AudioBook':
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n",1,the_dict)
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Artists'][0] + ' ' + item['Album'] + ' ' + str(item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']
                    #Delete media item
                    delete_media_item(item['Id'],the_dict)
                    #Print output for deleted media item
                    print_byType(item_output_details,print_audiobook_summary,the_dict)
                else: # item['Type'] == 'Unknown':
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\nNot Able To Delete Unknown Media Type",2,the_dict)
                    pass
    else:
        appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('[NO ITEMS TO DELETE]',print_common_summary,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('-----------------------------------------------------------',print_common_summary,the_dict)
    print_byType('\n',print_common_summary,the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('-----------------------------------------------------------',print_common_summary,the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('Done.',print_common_summary,the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('-----------------------------------------------------------',print_common_summary,the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('',print_common_summary,the_dict)


#show the command line help text
def defaultHelper(the_dict):
    #print_byType('\nUse -h or -help for command line option(s)',True)
    print_byType('\nFor help use -h or -help',True,the_dict)
    print_byType('\n/path/to/python3.x /path/to/mumc.py -help',True,the_dict)
    print_byType('',True,the_dict)


def print_all_media_disabled(the_dict):
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* ATTENTION!!!                                            *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* No media types are being monitored.                     *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* Open the mumc_config.py file in a text editor.          *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* Set at least one media type\'s condition days to >=0.    *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('*                                                         *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* played_filter_movie[0]=-1                               *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* played_filter_episode[0]=-1                             *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* played_filter_audio[0]=-1                               *',the_dict['print_warnings'],the_dict)
    if (isJellyfinServer(the_dict['server_brand'])):
        appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('* played_filter_audiobook[0]=-1                           *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('*                                                         *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* created_filter_movie[0]=-1                              *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* created_filter_episode[0]=-1                            *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('* created_filter_audio[0]=-1                              *',the_dict['print_warnings'],the_dict)
    if (isJellyfinServer(the_dict['server_brand'])):
        appendTo_DEBUG_log("\n",1,the_dict)
        print_byType('* created_filter_audiobook[0]=-1                          *',the_dict['print_warnings'],the_dict)
    appendTo_DEBUG_log("\n",1,the_dict)
    print_byType('-----------------------------------------------------------',the_dict['print_warnings'],the_dict)