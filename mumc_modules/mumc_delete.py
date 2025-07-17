import traceback
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType
from mumc_modules.mumc_url import requestURL,build_emby_jellyfin_request_message
from mumc_modules.mumc_console_info import build_config_setup_to_delete_media
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_season_episode import get_season_episode
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo,lookup_MOVIE_radarrInfo_IMdBId,get_MOVIE_radarrInfo_TMdBId,put_MOVIE_radarrInfo_radarrId,remove_MOVIE_radarr_radarrId,put_EPISODE_sonarrInfo_sonarrId,lookup_SERIES_sonarrInfo_IMdbId,get_SERIES_sonarrInfo_TVdbId,put_SERIES_sonarrInfo_sonarrId,remove_SERIES_sonarr
from mumc_modules.mumc_string_case import all_uppercase_lowercase_permutations
#from memory_profiler import profile


#@profile
#api call to delete items
def delete_media_item(itemID,the_dict):
    #Below are the x3 ways to delete media items

#########################################################################################################
    #Option #1
    #build API delete request for specified media item (only single itemIds)
    url=the_dict['admin_settings']['server']['url'] + '/Items/' + str(itemID) #DELETE emby and jellyfin
    req=build_emby_jellyfin_request_message(url,the_dict,method='DELETE')
#########################################################################################################
    #Option #2
    #build API delete request for specified media item (multiple comma separated itemIds)
    #url=the_dict['admin_settings']['server']['url'] + '/Items?Id=' + str(itemID) #DELETE emby
    #url=the_dict['admin_settings']['server']['url'] + '/Items?itemId=' + str(itemID) #DELETE jellyfin
    #req=build_emby_jellyfin_request_message(url,the_dict,method='DELETE')
#########################################################################################################
    #Option #3
    #build API delete request for specified media item (multiple comma separated itemIds)
    #url=the_dict['admin_settings']['server']['url'] + '/Items/Delete?Ids=' + str(itemID) #POST emby only
    #req=build_emby_jellyfin_request_message(url,the_dict,method='POST')
#########################################################################################################

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nSending Delete Request For: " + itemID,3,the_dict)
        appendTo_DEBUG_log("\nURL:\n" + url,3,the_dict)
        appendTo_DEBUG_log("\nRequest:\n" + str(req),4,the_dict)

    #Check if REMOVE_FILES='True'; send request to Emby/Jellyfin to delete specified media item
    if (the_dict['advanced_settings']['REMOVE_FILES']):
        try:
            rtn=requestURL(the_dict, req, the_dict['DEBUG'], 'delete_media_item_request_for_' + itemID, 3)
        except:
            print_byType('\nGeneric exception occured for media with Id: ' + str(itemID),True,the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])
            print_byType('\nGeneric exception occured: ' + str(traceback.format_exc()),True,the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])
            return False
        if ((rtn >= 200) and (rtn < 300)):
            return True
        else:
            return False
    #else in dry-run mode; REMOVE_FILES='False'; exit this function
    else:
        return True


#@profile
#list and delete items past played threshold
def print_and_delete_items(deleteItems,the_dict,delete_item_type='Media'):
    deleteItems_Tracker=[]

    print_summary_header=the_dict['advanced_settings']['console_controls']['headers']['summary']['show']
    summary_header_format=the_dict['advanced_settings']['console_controls']['headers']['summary']['formatting']

    print_movie_summary=the_dict['advanced_settings']['console_controls']['movie']['summary']['show']
    movie_summary_format=the_dict['advanced_settings']['console_controls']['movie']['summary']['formatting']

    print_episode_summary=the_dict['advanced_settings']['console_controls']['episode']['summary']['show']
    episode_summary_format=the_dict['advanced_settings']['console_controls']['episode']['summary']['formatting']

    print_audio_summary=the_dict['advanced_settings']['console_controls']['audio']['summary']['show']
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

    #List number of items to be deleted
    strings_list_to_print=''
    strings_list_to_print=build_config_setup_to_delete_media(strings_list_to_print,the_dict,delete_item_type)

    print_byType(strings_list_to_print,print_summary_header,the_dict,summary_header_format)

    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        serverBrand='Jellyfin'
    else:
        serverBrand='Emby'

    if len(deleteItems) > 0:
        for item in deleteItems:

            strings_list_to_print=''

            if (not (item['Id'] in deleteItems_Tracker)):
                deleteItems_Tracker.append(item['Id'])

                if (item['Type'] == 'Movie'):
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    
                    ##Delete media item
                    #if (delete_media_item(item['Id'],the_dict)):
                    #loop thru each radarr instance
                    for arrInfo,arrMovie in zip(the_dict['admin_settings']['media_managers']['radarr'],the_dict['advanced_settings']['radarr']['movie']):
                        try:
                            #Imdb not consistent from Emby/Jellyfin with uppercase and lowercase
                            for imdb in all_uppercase_lowercase_permutations('Imdb'):
                                #check if  imdb in providerIds
                                if (imdb in item['mumc']['providerIds']):
                                #try:
                                    #unmonitor media item in radarr
                                    if ((arrInfo['enabled'] and arrMovie['unmonitor'] and (not (item['mumc']['providerIds'][imdb] == None))) or
                                        (arrInfo['enabled'] and arrMovie['remove'] and (not (item['mumc']['providerIds']['Imdb'] == None)))):
                                        ######################################################################
                                        #For movies; because TMDB sometimes changes the movie Ids and then re-adds them with completely new Ids this has to be done in a certain order
                                        #  1. Lookup movie in Radarr using the IMDB Id (the IMDB Id should NEVER change)
                                        #  2. Grab the TMDB Id from the lookup in step #1
                                        #  3. Get the movie info using the TMDB Id in step #2
                                        #  4. Grab the Radarr Id returned in step #3
                                        #  5. Unmonitor/Remove movie in Radarr using Radarr Id in step #4
                                        ######################################################################
                                        #lookup movie info from Radarr using IMdBId
                                        lookup_media_item_data=lookup_MOVIE_radarrInfo_IMdBId(item['mumc']['providerIds']['Imdb'],arrInfo,the_dict)
                                        #get movie info from radarr using TMdBId
                                        media_item_data=get_MOVIE_radarrInfo_TMdBId(lookup_media_item_data['tmdbId'],arrInfo,the_dict)
                                        #save movie's radarr id
                                        item['mumc']['providerIds']['radarr']=media_item_data[0]['id']
                                        try:
                                            if (arrInfo['enabled'] and arrMovie['unmonitor'] and (not (item['mumc']['providerIds'][imdb] == None))):
                                                #set monitored state to False
                                                media_item_data[0]['monitored']=False
                                                if (the_dict['advanced_settings']['REMOVE_FILES']):
                                                    #unmonitor movie in Radarr using Radarr Id
                                                    media_item_data=put_MOVIE_radarrInfo_radarrId(media_item_data[0]['id'],media_item_data[0],arrInfo,the_dict)
                                                appendTo_DEBUG_log(str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" monitor status is now unmonitored in Radarr-' + str(the_dict['admin_settings']['media_managers']['radarr'].index(arrInfo)) + '.\n',2,the_dict)
                                        except:
                                            print('RadarrMovieWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be unmonitored in Radarr-' + str(the_dict['admin_settings']['media_managers']['radarr'].index(arrInfo)) + '.\n')
                                            appendTo_DEBUG_log('RadarrMovieWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be unmonitored in Radarr-' + str(the_dict['admin_settings']['media_managers']['radarr'].index(arrInfo)) + '.\n',2,the_dict)
                                        try:
                                            if (arrInfo['enabled'] and arrMovie['remove'] and (not (item['mumc']['providerIds']['Imdb'] == None))):
                                                if (the_dict['advanced_settings']['REMOVE_FILES']):
                                                    #remove movie from Radarr using Radarr Id
                                                    media_item_data=remove_MOVIE_radarr_radarrId(media_item_data[0]['id'],the_dict)
                                                appendTo_DEBUG_log(str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" is now removed from Radarr-' + str(the_dict['admin_settings']['media_managers']['radarr'].index(arrInfo)) + '.\n',2,the_dict)
                                        except:
                                            print('RadarrMovieWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be removed from Radarr-' + str(the_dict['admin_settings']['media_managers']['radarr'].index(arrInfo)) + '.\n')
                                            appendTo_DEBUG_log('RadarrMovieWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be removed from Radarr-' + str(the_dict['admin_settings']['media_managers']['radarr'].index(arrInfo)) + '.\n',2,the_dict)

                                    #permutation of imdb found
                                    break

                        except:
                            print('RadarrMovieWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" issue getting data from Radarr-' + str(the_dict['admin_settings']['media_managers']['radarr'].index(arrInfo)) + '.\n')
                            appendTo_DEBUG_log('RadarrMovieWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" issue getting data from Radarr-' + str(the_dict['admin_settings']['media_managers']['radarr'].index(arrInfo)) + '.\n',2,the_dict)

                    ##Delete media item
                    if (delete_media_item(item['Id'],the_dict)):
                        #Print output for deleted media item
                        strings_list_to_print+=item_output_details + '\n'
                        print_byType(strings_list_to_print,print_movie_summary,the_dict,movie_summary_format)
                elif (item['Type'] == 'Episode'):
                    try:
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'],item['IndexNumber'],the_dict) + ' - ' + item['Name'] + ' - ' + item['Id']
                    except (KeyError, IndexError):
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log('Missing' + item['Type'] + 'DataError encountered - Delete Episode: \n\n' + str(item),2,the_dict)

                    #Delete media item
                    if (delete_media_item(item['Id'],the_dict)):
                        #loop thru each sonarr instance
                        for arrInfo,arrEpisode in zip(the_dict['admin_settings']['media_managers']['sonarr'],the_dict['advanced_settings']['sonarr']['episode']):
                            try:
                                #unmonitor media item
                                if ((arrInfo['enabled']) and (arrEpisode['unmonitor'])):
                                    if (the_dict['advanced_settings']['REMOVE_FILES']):
                                        #unmonitor episode item in Sonarr
                                        media_item_data=put_EPISODE_sonarrInfo_sonarrId(item['mumc']['providerIds']['sonarr'],arrInfo,the_dict)
                                    appendTo_DEBUG_log(str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - SeriesName: ' + str(item['SeriesName']) + ' ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" monitor status is now unmonitored in Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n',2,the_dict)
                            except:
                                print('SonarrEpisodeWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - SeriesName: ' + str(item['SeriesName']) + ' ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be unmonitored in Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n')
                                appendTo_DEBUG_log('SonarrEpisodeWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - SeriesName: ' + str(item['SeriesName']) + ' ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be unmonitored in Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n',2,the_dict)

                    #Print output for deleted media item
                    strings_list_to_print+=item_output_details + '\n'
                    print_byType(strings_list_to_print,print_episode_summary,the_dict,episode_summary_format)
                elif (item['Type'] == 'Audio'):
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Artists'][0] + ' ' + item['Album'] + ' ' + str(item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']

                    #Delete media item
                    if (delete_media_item(item['Id'],the_dict)):
                        #unmonitor audio in Lidarr
                        pass

                    #Print output for deleted media item
                    strings_list_to_print+=item_output_details + '\n'
                    print_byType(strings_list_to_print,print_audio_summary,the_dict,audio_summary_format)
                elif (item['Type'] == 'AudioBook'):
                    item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Artists'][0] + ' ' + item['Album'] + ' ' + str(item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']

                    #Delete media item
                    if (delete_media_item(item['Id'],the_dict)):
                        #unmonitor audiobook in Readarr
                        pass

                    #Print output for deleted media item
                    strings_list_to_print+=item_output_details + '\n'
                    print_byType(strings_list_to_print,print_audiobook_summary,the_dict,audiobook_summary_format)
                elif (item['Type'] == 'Season'):
                    try:
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['SeriesName'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    except (KeyError, IndexError):
                        item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log('Missing' + item['Type'] + 'DataError encountered - Delete Season Folder: \n\n' + str(item),2,the_dict)

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
                            appendTo_DEBUG_log('Missing' + item['Type'] + 'DataError encountered - Delete Series Folder: \n\n' + str(item),2,the_dict)

                    ##Delete media item
                    #if (delete_media_item(item['Id'],the_dict)):
                    #loop thru each sonarr instance
                    for arrInfo,arrSeries in zip(the_dict['admin_settings']['media_managers']['sonarr'],the_dict['advanced_settings']['sonarr']['series']):
                        try:
                            #unmonitor media item
                            if ((arrInfo['enabled'] and arrSeries['unmonitor']) or
                                (arrInfo['enabled'] and arrSeries['remove'])):
                                user_info={}
                                user_info['user_id']=the_dict['admin_settings']['server']['admin_id']
                                #get series info
                                series_info=get_ADDITIONAL_itemInfo(user_info,item['Id'],'get_series_info_to_unmonitor_and_or_remove',the_dict)
                                item['mumc']={}
                                item['mumc']['providerIds']=series_info['ProviderIds']
                                ######################################################################
                                #For series; because TVDB sometimes changes the series Ids and then re-adds them with completely new Ids this has to be done in a certain order
                                #  1. Lookup series in Sonarr using the IMDB Id (the IMDB Id should NEVER change)
                                #  2. Grab the TMDB Id from the lookup in step #1
                                #  3. Get the series info using the TMDB Id in step #2
                                #  4. Grab the Sonarr Id returned in step #3
                                #  5. Unmonitor/Remove series in Sonarr using Sonarr Id in step #4
                                ######################################################################
                                #Imdb not consistent from Emby/Jellyfin with uppercase and lowercase
                                for imdb in all_uppercase_lowercase_permutations('Imdb'):
                                    #check if  imdb in providerIds
                                    if (imdb in item['mumc']['providerIds']):
                                        #lookup series info from sonarrr using IMdBId
                                        lookup_media_item_data=lookup_SERIES_sonarrInfo_IMdbId(item['mumc']['providerIds']['Imdb'],arrInfo,the_dict)
                                        #get series info from sonarr using TVdBId
                                        media_item_data=get_SERIES_sonarrInfo_TVdbId(lookup_media_item_data[0]['tvdbId'],arrInfo,the_dict)
                                        #save series' sonarr id
                                        item['mumc']['providerIds']['sonarr']=media_item_data[0]['id']
                                        try:
                                            if (arrInfo['enabled'] and arrSeries['unmonitor']):
                                                #set monitored state to False
                                                media_item_data[0]['monitored']=False
                                                if (the_dict['advanced_settings']['REMOVE_FILES']):
                                                    #unmonitor series in Sonarr
                                                    media_item_data=put_SERIES_sonarrInfo_sonarrId(media_item_data[0]['id'],arrInfo,media_item_data[0],the_dict)
                                                appendTo_DEBUG_log(str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" monitor status is now unmonitored in Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n',2,the_dict)
                                        except:
                                            print('SonarrSeriesWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be unmonitored in Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n')
                                            appendTo_DEBUG_log('SonarrSeriesWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be unmonitored in Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n',2,the_dict)
                                        try:
                                            if (arrInfo['enabled'] and arrSeries['remove']):
                                                #force an exception if series is not in Sonarr
                                                media_item_data[0]['id']=media_item_data[0]['id']
                                                if (the_dict['advanced_settings']['REMOVE_FILES']):
                                                    #remove series from Sonarr
                                                    media_item_data=remove_SERIES_sonarr(media_item_data['id'],the_dict)
                                            appendTo_DEBUG_log(str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" is now removed from Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n',2,the_dict)

                                        except:
                                            print('SonarrSeriesWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be removed from Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n')
                                            appendTo_DEBUG_log('SonarrSeriesWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" cannot be removed from Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n',2,the_dict)

                                        #permutation of imdb found
                                        break

                        except:
                            print('SonarrSeriesWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" issue getting data from Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n')
                            appendTo_DEBUG_log('SonarrSeriesWarning: ' + str(serverBrand) + str(item['Type']) + 'Id: ' + str(item['Id']) + ' - ' + str(item['Type']) + 'Name: "' + str(item['Name']) + '" issue getting data from Sonarr-' + str(the_dict['admin_settings']['media_managers']['sonarr'].index(arrInfo)) + '.\n',2,the_dict)

                    #Delete media item
                    if (delete_media_item(item['Id'],the_dict)):
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

    return