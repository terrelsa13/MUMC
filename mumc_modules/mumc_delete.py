import traceback
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType
from mumc_modules.mumc_url import requestURL,build_request_message
from mumc_modules.mumc_console_info import build_config_setup_to_delete_media
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_season_episode import get_season_episode


#api call to delete items
def delete_media_item(itemID,the_dict):
    #Below are the x3 ways to delete media items

#########################################################################################################
    #Option #1
    #build API delete request for specified media item (only single itemIds)
    url=the_dict['admin_settings']['server']['url'] + '/Items/' + str(itemID) #DELETE
    req=build_request_message(url,the_dict,method='DELETE')
#########################################################################################################
    #Option #2
    #build API delete request for specified media item (multiple comma separated itemIds)
    #url=the_dict['admin_settings']['server']['url'] + '/Items?Ids=' + str(itemID) #DELETE
    #req=build_request_message(url,the_dict,method='DELETE')
#########################################################################################################
    #Option #3
    #build API delete request for specified media item (multiple comma separated itemIds)
    #url=the_dict['admin_settings']['server']['url'] + '/Items/Delete?Ids=' + str(itemID) #POST
    #req=build_request_message(url,the_dict,method='POST')
#########################################################################################################

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nSending Delete Request For: " + itemID,3,the_dict)
        appendTo_DEBUG_log("\nURL:\n" + url,3,the_dict)
        appendTo_DEBUG_log("\nRequest:\n" + str(req),4,the_dict)

    #Check if REMOVE_FILES='True'; send request to Emby/Jellyfin to delete specified media item
    if (the_dict['advanced_settings']['REMOVE_FILES']):
        try:
            requestURL(req, the_dict['DEBUG'], 'delete_media_item_request_for_' + itemID, 3, the_dict)
        except:
            print_byType('\nGeneric exception occured for media with Id: ' + str(itemID),True,the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])
            print_byType('\nGeneric exception occured: ' + str(traceback.format_exc()),True,the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])
        return
    #else in dry-run mode; REMOVE_FILES='False'; exit this function
    else:
        return


#list and delete items past played threshold
def print_and_delete_items(deleteItems,the_dict,delete_item_type='Media'):
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
    strings_list_to_print=''
    strings_list_to_print=build_config_setup_to_delete_media(strings_list_to_print,the_dict,delete_item_type)

    print_byType(strings_list_to_print,print_summary_header,the_dict,summary_header_format)

    if len(deleteItems) > 0:
        for item in deleteItems:

            strings_list_to_print=''

            if (not (item['Id'] in deleteItems_Tracker)):
                deleteItems_Tracker.append(item['Id'])

                if (item['Type'] == 'Movie'):
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    
                    #Delete media item
                    delete_media_item(item['Id'],the_dict)

                    #Print output for deleted media item
                    strings_list_to_print+=item_output_details + '\n'
                    print_byType(strings_list_to_print,print_movie_summary,the_dict,movie_summary_format)
                elif (item['Type'] == 'Episode'):
                    try:
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'],item['IndexNumber'],the_dict) + ' - ' + item['Name'] + ' - ' + item['Id']
                    except (KeyError, IndexError):
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log('Error encountered - Delete Episode: \n\n' + str(item),2,the_dict)

                    #Delete media item
                    delete_media_item(item['Id'],the_dict)

                    #Print output for deleted media item
                    strings_list_to_print+=item_output_details + '\n'
                    print_byType(strings_list_to_print,print_episode_summary,the_dict,episode_summary_format)
                elif (item['Type'] == 'Audio'):
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Artists'][0] + ' ' + item['Album'] + ' ' + str(item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']

                    #Delete media item
                    delete_media_item(item['Id'],the_dict)

                    #Print output for deleted media item
                    strings_list_to_print+=item_output_details + '\n'
                    print_byType(strings_list_to_print,print_audio_summary,the_dict,audio_summary_format)
                elif (item['Type'] == 'AudioBook'):
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Artists'][0] + ' ' + item['Album'] + ' ' + str(item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']

                    #Delete media item
                    delete_media_item(item['Id'],the_dict)

                    #Print output for deleted media item
                    strings_list_to_print+=item_output_details + '\n'
                    print_byType(strings_list_to_print,print_audiobook_summary,the_dict,audiobook_summary_format)
                elif (item['Type'] == 'Season'):
                    try:
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['SeriesName'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    except (KeyError, IndexError):
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log('Error encountered - Delete Season Folder: \n\n' + str(item),2,the_dict)

                    #Delete media item
                    delete_media_item(item['Id'],the_dict)

                    #Print output for deleted media item
                    strings_list_to_print+=item_output_details + '\n'
                    print_byType(strings_list_to_print,print_episode_summary,the_dict,episode_summary_format)
                elif (item['Type'] == 'Series'):
                    try:
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    except (KeyError, IndexError):
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log('Error encountered - Delete Series Folder: \n\n' + str(item),2,the_dict)

                    #Delete media item
                    delete_media_item(item['Id'],the_dict)

                    #Print output for deleted media item
                    strings_list_to_print+=item_output_details + '\n'
                    print_byType(strings_list_to_print,print_episode_summary,the_dict,episode_summary_format)
                else: #(item['Type'] == 'Unknown'):
                    strings_list_to_print+='Not Able To Delete Unknown Media Type' + '\n'

                    print_byType(strings_list_to_print,True,the_dict,the_dict['formatting'])
    else:
        strings_list_to_print=''
        strings_list_to_print+='[NO ITEMS TO DELETE]' + '\n'
        print_byType(strings_list_to_print,print_summary_header,the_dict,summary_header_format)

    strings_list_to_print=''

    strings_list_to_print+=the_dict['_console_separator'] + '\n'
    strings_list_to_print+=the_dict['console_separator'] + '\n'

    print_byType(strings_list_to_print,print_summary_header,the_dict,summary_header_format)