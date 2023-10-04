#!/usr/bin/env python3
import multiprocessing
import urllib.parse as urlparse
from datetime import timedelta,datetime
from collections import defaultdict
from mumc_modules.mumc_url import api_query_handler
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType
from mumc_modules.mumc_favorited import getChildren_favoritedMediaItems,get_isMOVIE_Fav,get_isMOVIE_AdvancedFav,get_isEPISODE_Fav,get_isEPISODE_AdvancedFav,get_isAUDIO_Fav,get_isAUDIO_AdvancedFav,get_isAUDIOBOOK_Fav,get_isAUDIOBOOK_AdvancedFav
from mumc_modules.mumc_tagged import getChildren_taggedMediaItems,get_isMOVIE_Tagged,get_isEPISODE_Tagged,get_isAUDIO_Tagged,get_isAUDIOBOOK_Tagged,list_to_urlparsed_string
from mumc_modules.mumc_blacklist_whitelist import get_isItemWhitelisted_Blacklisted
from mumc_modules.mumc_prepare_item import prepare_MOVIEoutput,prepare_EPISODEoutput,prepare_AUDIOoutput,prepare_AUDIOBOOKoutput
from mumc_modules.mumc_days_since import get_days_since_played,get_days_since_created
from mumc_modules.mumc_console_info import build_print_media_item_details,print_user_header
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_played_created import get_isPlayedCreated_FilterValue,get_playedCreatedDays_playedCreatedCounts
from mumc_modules.mumc_item_info import get_SERIES_itemInfo
from mumc_modules.mumc_season_episode import get_season_episode
from mumc_modules.mumc_compare_items import keys_exist


#Determine if item can be monitored
def get_isItemMonitored(mediasource,the_dict):
    #When script is run before a media item is physically available ignore that media item
    if ('Type' in mediasource) and ('Size' in mediasource):
        if ((mediasource['Type'] == 'Placeholder') and (mediasource['Size'] == 0)):
            #ignore this media item
            itemIsMonitored=False
        else:
            #ok to monitor this media item
            itemIsMonitored=True
    elif ('Type' in mediasource):
        if (mediasource['Type'] == 'Placeholder'):
            #ignore this media item
            itemIsMonitored=False
        else:
            #ok to monitor this media item
            itemIsMonitored=True
    elif ('Size' in mediasource):
        if (mediasource['Size'] == 0):
            #ignore this media item
            itemIsMonitored=False
        else:
            #ok to monitor this media item
            itemIsMonitored=True
    else:
        #ignore this media item
        itemIsMonitored=False

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\nMedia Item Is Monitored: ' + str(itemIsMonitored),2,the_dict)

    return(itemIsMonitored)


#Parse behavior for favorites, whitetags, blacktags, and whitelists
def parse_actionedConfigurationBehavior(theActionType,item,user_info,var_dict,the_dict):

    if (theActionType == 'favorited'):
        isactioned_extra_byUserId=var_dict['isfavorited_extraInfo_byUserId_Media']
        user_key=user_info['user_id']
        isActioned_and_played_byUserId=var_dict['isfavorited_and_played_byUserId_Media']
        action_behavior=var_dict['favorited_behavior_media']
        item_isActioned=(var_dict['item_isFavorited'] or var_dict['item_isFavorited_Advanced'])
    elif (theActionType == 'whitetagged'):
        isactioned_extra_byUserId=var_dict['iswhitetagged_extraInfo_byUserId_Media']
        user_key=user_info['user_id']
        isActioned_and_played_byUserId=var_dict['iswhitetagged_and_played_byUserId_Media']
        action_behavior=var_dict['whitetagged_behavior_media']
        item_isActioned=var_dict['item_isWhitetagged']
    elif (theActionType == 'blacktagged'):
        isactioned_extra_byUserId=var_dict['isblacktagged_extraInfo_byUserId_Media']
        user_key=user_info['user_id']
        isActioned_and_played_byUserId=var_dict['isblacktagged_and_played_byUserId_Media']
        action_behavior=var_dict['blacktagged_behavior_media']
        item_isActioned=var_dict['item_isBlacktagged']
    elif (theActionType == 'whitelisted'):
        isactioned_extra_byUserId=var_dict['iswhitelisted_extraInfo_byUserId_Media']
        user_key=user_info['user_id']
        isActioned_and_played_byUserId=var_dict['iswhitelisted_and_played_byUserId_Media']
        action_behavior=var_dict['whitelisted_behavior_media']
        item_isActioned=var_dict['item_isWhitelisted']
    elif (theActionType == 'blacklisted'):
        isactioned_extra_byUserId=var_dict['isblacklisted_extraInfo_byUserId_Media']
        user_key=user_info['user_id']
        isActioned_and_played_byUserId=var_dict['isblacklisted_and_played_byUserId_Media']
        action_behavior=var_dict['blacklisted_behavior_media']
        item_isActioned=var_dict['item_isBlacklisted']
    else: #(theActionType == 'unknown'):
        #generate error
        pass

    item_matches_played_days_filter=var_dict['item_matches_played_days_filter']
    item_matches_played_count_filter=var_dict['item_matches_played_count_filter']
    item_matches_created_days_filter=var_dict['item_matches_created_days_filter']
    item_matches_created_played_count_filter=var_dict['item_matches_created_played_count_filter']
    itemIsPlayed=var_dict['itemIsPlayed']
    itemPlayedCount=var_dict['itemPlayedCount']

    return_dict={}

    isactioned_extra_byUserId['ActionBehavior']=action_behavior['action_control']
    isactioned_extra_byUserId['ActionType']=theActionType
    isactioned_extra_byUserId['MonitoredUsersAction']=action_behavior['user_conditional'].casefold()
    isactioned_extra_byUserId['MonitoredUsersMeetPlayedFilter']=action_behavior['played_conditional'].casefold()
    isactioned_extra_byUserId['ConfiguredBehavior']=action_behavior['action'].casefold()

    #isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingAction']=item_isActioned
    #isactioned_extra_byUserId[user_key][item['Id']]['IsItemPlayed']=itemIsPlayed
    #isactioned_extra_byUserId[user_key][item['Id']]['IsItemPlayedCount']=itemPlayedCount
    #isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingPlayedDays']=item_matches_played_days_filter
    #isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingPlayedCount']=item_matches_played_count_filter
    #isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingCreatedPlayedDays']=item_matches_created_days_filter
    #isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingCreatedPlayedCount']=item_matches_created_played_count_filter

    isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingAction']=item_isActioned
    isactioned_extra_byUserId[user_key][item['Id']]['itemIsPlayed']=itemIsPlayed
    isactioned_extra_byUserId[user_key][item['Id']]['itemPlayedCount']=itemPlayedCount
    isactioned_extra_byUserId[user_key][item['Id']]['item_matches_played_days_filter']=item_matches_played_days_filter
    isactioned_extra_byUserId[user_key][item['Id']]['item_matches_played_count_filter']=item_matches_played_count_filter
    isactioned_extra_byUserId[user_key][item['Id']]['item_matches_created_days_filter']=item_matches_created_days_filter
    isactioned_extra_byUserId[user_key][item['Id']]['item_matches_created_played_count_filter']=item_matches_created_played_count_filter

    #if ((not item_matches_played_days_filter) and (not item_matches_played_count_filter)):
        #isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingPlayedFilter']=None
    #else:
        #isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingPlayedFilter']=(item_matches_played_days_filter and item_matches_played_count_filter)
    isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingPlayedFilter']=(item_matches_played_days_filter and item_matches_played_count_filter)

    #if ((not item_matches_created_days_filter) and (not item_matches_created_played_count_filter)):
        #isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingCreatedPlayedFilter']=None
    #else:
        #isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingCreatedPlayedFilter']=(item_matches_created_days_filter and item_matches_created_played_count_filter)
    isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingCreatedPlayedFilter']=(item_matches_created_days_filter and item_matches_created_played_count_filter)

    isActioned_and_played_byUserId[user_key][item['Id']]=item

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nActionBehavior=" + str(isactioned_extra_byUserId['ActionBehavior']),3,the_dict)
        appendTo_DEBUG_log("\nActionType=" + str(isactioned_extra_byUserId['ActionType']),3,the_dict)
        appendTo_DEBUG_log("\nMonitoredUsersAction=" + str(isactioned_extra_byUserId['MonitoredUsersAction']),3,the_dict)
        appendTo_DEBUG_log("\nIsMeetingAction=" + str(isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingAction']),3,the_dict)
        appendTo_DEBUG_log("\nMonitoredUsersMeetPlayedFilter=" + str(isactioned_extra_byUserId['MonitoredUsersMeetPlayedFilter']),3,the_dict)
        appendTo_DEBUG_log("\nIsMeetingPlayedFilter=" + str(isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingPlayedFilter']),3,the_dict)
        appendTo_DEBUG_log("\nConfiguredBehavior=" + str(isactioned_extra_byUserId['ConfiguredBehavior']),3,the_dict)
        appendTo_DEBUG_log("\nItemId=" + str(item['Id']),3,the_dict)

    if (theActionType == 'favorited'):
        return_dict['isfavorited_and_played_byUserId_Media']=isActioned_and_played_byUserId
        return_dict['isfavorited_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    elif (theActionType == 'whitetagged'):
        return_dict['iswhitetagged_and_played_byUserId_Media']=isActioned_and_played_byUserId
        return_dict['iswhitetagged_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    elif (theActionType == 'blacktagged'):
        return_dict['isblacktagged_and_played_byUserId_Media']=isActioned_and_played_byUserId
        return_dict['isblacktagged_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    elif (theActionType == 'whitelisted'):
        return_dict['iswhitelisted_and_played_byUserId_Media']=isActioned_and_played_byUserId
        return_dict['iswhitelisted_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    elif (theActionType == 'blacklisted'):
        return_dict['isblacklisted_and_played_byUserId_Media']=isActioned_and_played_byUserId
        return_dict['isblacklisted_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    else: #(theActionType == 'unknown'):
        #generate error
        pass

    #return isActioned_and_played_byUserId,isactioned_extra_byUserId
    return return_dict


#decide if this item is ok to be deleted; still has to meet other criteria
def get_singleUserDeleteStatus(var_dict,the_dict):

    item_matches_played_count_filter=var_dict['item_matches_played_count_filter']
    item_matches_played_days_filter=var_dict['item_matches_played_days_filter']
    item_matches_created_played_count_filter=var_dict['item_matches_created_played_count_filter']
    item_matches_created_days_filter=var_dict['item_matches_created_days_filter']
    item_isFavorited=var_dict['item_isFavorited']
    item_isFavorited_Advanced=var_dict['item_isFavorited_Advanced']
    item_isWhitetagged=var_dict['item_isWhitetagged']
    item_isBlacktagged=var_dict['item_isBlacktagged']
    item_isWhitelisted=var_dict['item_isWhitelisted']
    item_isBlacklisted=var_dict['item_isBlacklisted']

    #when item is favorited do not allow it to be deleted
    if (var_dict['item_isFavorited'] or var_dict['item_isFavorited_Advanced']):
        okToDelete=False
    #when item is whitetagged do not allow it to be deleted
    elif (item_isWhitetagged):
        okToDelete=False
    #when item is blacktagged allow it to be deleted
    elif (item_isBlacktagged and ((item_matches_played_count_filter and item_matches_played_days_filter) or (item_matches_created_played_count_filter and item_matches_created_days_filter))):
        okToDelete=True
    #when item is whitelisted do not allow it to be deleted
    elif (item_isWhitelisted):
        okToDelete=False
    #when item is blacklisted allow it to be deleted
    elif (item_isBlacklisted and ((item_matches_played_count_filter and item_matches_played_days_filter) or (item_matches_created_played_count_filter and item_matches_created_days_filter))):
        okToDelete=True
    else: #do not allow item to be deleted
        okToDelete=False

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nIs Media Item OK To Delete: " + str(okToDelete),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item Favorited For This User: " + str(item_isFavorited),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item An Advanced Favorite: " + str(item_isFavorited_Advanced),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item Whitetagged: " + str(item_isWhitetagged),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item Blacktagged: " + str(item_isBlacktagged),2,the_dict)
        appendTo_DEBUG_log("\nDoes Media Item Match The Play Count Filter: " + str(item_matches_played_count_filter),2,the_dict)
        appendTo_DEBUG_log("\nDoes Media Item Meet Number Of Days Since Played: " + str(item_matches_played_days_filter),2,the_dict)
        appendTo_DEBUG_log("\nDoes Media Item Match The Created Played Count Filter: " + str(item_matches_created_played_count_filter),2,the_dict)
        appendTo_DEBUG_log("\nDoes Media Item Meet Number Of Days Since Created-Played: " + str(item_matches_created_days_filter),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item Whitelisted For This User: " + str(item_isWhitelisted),2,the_dict)

    return okToDelete


# get played, favorited, and tagged media items
# save media items ready to be deleted
# remove media items with exceptions (i.e. favorited, whitelisted, whitetagged, etc...)
def get_mediaItems(the_dict,media_type,user_info,media_returns):

    var_dict={}

    var_dict['media_type_lower']=media_type.casefold()
    var_dict['media_type_upper']=media_type.upper()
    var_dict['media_type_title']=media_type.title()

    var_dict['media_dict_str']=the_dict[var_dict['media_type_lower'] + '_dict']['media_type'] + '_dict'

    var_dict['server_url']=the_dict['admin_settings']['server']['url']
    var_dict['auth_key']=the_dict['admin_settings']['server']['auth_key']

    var_dict['server_brand']=the_dict['admin_settings']['server']['brand']

    #remove whitespace(s) from the beginning and end of each tag
    whitetags_global = [tagstr for tagstr in the_dict['advanced_settings']['whitetags'] if tagstr.strip()]
    blacktags_global = [tagstr for tagstr in the_dict['advanced_settings']['blacktags'] if tagstr.strip()]
    whitetags_media_specific = [tagstr for tagstr in the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['tags'] if tagstr.strip()]
    blacktags_media_specific = [tagstr for tagstr in the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['tags'] if tagstr.strip()]
    #combine tags and remove any duplicates
    var_dict['whitetags']=list(set(whitetags_global + whitetags_media_specific))
    var_dict['blacktags']=list(set(blacktags_global + blacktags_media_specific))

    var_dict['library_matching_behavior']=the_dict['admin_settings']['behavior']['matching'].casefold()

    #user_bllib_keys_json=the_dict['user_bllib_keys_json']
    #user_bllib_netpath_json=the_dict['user_bllib_netpath_json']
    #user_bllib_path_json=the_dict['user_bllib_path_json']
    #user_wllib_keys_json=the_dict['user_wllib_keys_json']
    #user_wllib_netpath_json=the_dict['user_wllib_netpath_json']
    #user_wllib_path_json=the_dict['user_wllib_path_json']

    var_dict['media_played_days']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['played']['condition_days']
    var_dict['media_created_days']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['created']['condition_days']
    var_dict['media_played_count_comparison']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['played']['count_equality']
    var_dict['media_created_played_count_comparison']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['created']['count_equality']
    var_dict['media_played_count']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['played']['count']
    var_dict['media_created_played_count']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['created']['count']
    if (the_dict['DEBUG']):
        var_dict['print_media_delete_info']=True
        var_dict['print_media_keep_info']=True
    else:
        var_dict['print_media_delete_info']=the_dict['advanced_settings']['console_controls'][var_dict['media_type_lower']]['delete']['show']
        var_dict['print_media_keep_info']=the_dict['advanced_settings']['console_controls'][var_dict['media_type_lower']]['keep']['show']
    var_dict['media_delete_info_format']=the_dict['advanced_settings']['console_controls'][var_dict['media_type_lower']]['delete']['formatting']
    var_dict['media_keep_info_format']=the_dict['advanced_settings']['console_controls'][var_dict['media_type_lower']]['keep']['formatting']
    var_dict['favorited_behavior_media']={}
    var_dict['favorited_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['favorited']['action']
    var_dict['favorited_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['favorited']['user_conditional']
    var_dict['favorited_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['favorited']['played_conditional']
    var_dict['favorited_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['favorited']['action_control']
    var_dict['whitetagged_behavior_media']={}
    var_dict['whitetagged_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['action']
    var_dict['whitetagged_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['user_conditional']
    var_dict['whitetagged_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['played_conditional']
    var_dict['whitetagged_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['action_control']
    var_dict['blacktagged_behavior_media']={}
    var_dict['blacktagged_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['action']
    var_dict['blacktagged_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['user_conditional']
    var_dict['blacktagged_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['played_conditional']
    var_dict['blacktagged_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['action_control']
    var_dict['whitelisted_behavior_media']={}
    var_dict['whitelisted_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitelisted']['action']
    var_dict['whitelisted_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitelisted']['user_conditional']
    var_dict['whitelisted_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitelisted']['played_conditional']
    var_dict['whitelisted_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitelisted']['action_control']
    var_dict['blacklisted_behavior_media']={}
    var_dict['blacklisted_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacklisted']['action']
    var_dict['blacklisted_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacklisted']['user_conditional']
    var_dict['blacklisted_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacklisted']['played_conditional']
    var_dict['blacklisted_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacklisted']['action_control']
    var_dict['media_set_missing_last_played_date']=the_dict['advanced_settings']['trakt_fix']['set_missing_last_played_date'][var_dict['media_type_lower']]

    var_dict['print_common_delete_keep_info']=(var_dict['print_media_delete_info'] or var_dict['print_media_keep_info'])
    #the_dict['print_common_delete_keep_info']=print_common_delete_keep_info

    var_dict['advFav_media']={}
    var_dict['advFav_media']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['favorited']['extra']
    '''
    if (var_dict['media_type_lower'] == 'movie'):
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['genre'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['library_genre'])
        #advFav2_media=0
        #advFav3_media=0
        #advFav4_media=0
        #advFav5_media=0
    elif (var_dict['media_type_lower'] == 'episode'):
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['genre'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['season_genre'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['series_genre'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['library_genre'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network_genre'])
    elif (var_dict['media_type_lower'] == 'audio'):
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['genre'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_genre'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['library_genre'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['track_artist'])
        var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_artist'])
    elif (var_dict['media_type_lower'] == 'audiobook'):
        if (isJellyfinServer(var_dict['server_brand'])):
            var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['genre'])
            var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['audiobook_genre'])
            var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_genre'])
            var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['track_author'])
            var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['author'])
            var_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_author'])
        else: #(isEmbyServer(the_dict)):
            pass
    '''

    if (var_dict['media_type_lower'] == 'episode'):
        var_dict['minimum_number_episodes']=the_dict['advanced_settings']['episode_control']['minimum_episodes']
        var_dict['minimum_number_played_episodes']=the_dict['advanced_settings']['episode_control']['minimum_played_episodes']
    else:
        var_dict['minimum_number_episodes']=0
        var_dict['minimum_number_played_episodes']=0

    #Determine played or created time; UTC time used for media items; determine played and created date for each media type
    var_dict['cut_off_date_played_media']=the_dict['cut_off_date_played_media'][var_dict['media_type_lower']]
    var_dict['cut_off_date_created_media']=the_dict['cut_off_date_created_media'][var_dict['media_type_lower']]

    #var_dict['cut_off_date_played_media']=get=_timeDelta(the_dict['date_time_now_tz_utc'],timedelta(var_dict['media_played_days']))
    #var_dict['cut_off_date_created_media']=get_timeDelta(the_dict['date_time_now_tz_utc'] - timedelta(var_dict['media_created_days']))

    '''
    #Update media_returns with the cut_off_date_played_media if it does not already exist
    if (not (keys_exist(media_returns,'cut_off_date_played_media'))):
        media_returns['cut_off_date_played_media']={}
    #Update media_returns with the cut_off_date_created_media if it does not already exist
    if (not (keys_exist(media_returns,'cut_off_date_created_media'))):
        media_returns['cut_off_date_created_media']={}

    #Update media_returns with the played time for this media type if it does not already exist
    if (not (keys_exist(media_returns['cut_off_date_played_media'],var_dict['media_type_lower']))):
        media_returns['cut_off_date_played_media'][var_dict['media_type_lower']]=var_dict['cut_off_date_played_media']
    #Update media_returns with the created time for this media type if it does not already exist
    if (not (keys_exist(media_returns['cut_off_date_created_media'],var_dict['media_type_lower']))):
        media_returns['cut_off_date_created_media'][var_dict['media_type_lower']]=var_dict['cut_off_date_created_media']
    '''
        #moved to init_getMedia() to prevent race condition
        #the_dict['cut_off_date_played_media']={}
        #the_dict['cut_off_date_played_media']={}

        #save cutoff dates-times back to the_dict for use during post processing
        #if (not (keys_exist(the_dict['cut_off_date_played_media'],var_dict['media_type_lower']))):
            #the_dict['calculated_cut_off_date_played_media'][var_dict['media_type_lower']]=var_dict.copy()['cut_off_date_played_media']
        #if (not (keys_exist(the_dict['cut_off_date_created_media'],var_dict['media_type_lower']))):
            #the_dict['calculated_cut_off_date_created_media'][var_dict['media_type_lower']]=var_dict.copy()['cut_off_date_created_media']

    #dictionary of favortied and played items by userId
    var_dict['isfavorited_and_played_byUserId_Media']={}
    var_dict['isfavorited_extraInfo_byUserId_Media']={}
    #dictionary of whitetagged items by userId
    var_dict['iswhitetagged_and_played_byUserId_Media']={}
    var_dict['iswhitetagged_extraInfo_byUserId_Media']={}
    #dictionary of blacktagged items by userId
    var_dict['isblacktagged_and_played_byUserId_Media']={}
    var_dict['isblacktagged_extraInfo_byUserId_Media']={}
    #dictionary of whitelisted items by userId
    var_dict['iswhitelisted_and_played_byUserId_Media']={}
    var_dict['iswhitelisted_extraInfo_byUserId_Media']={}
    #dictionary of blacklisted items by userId
    var_dict['isblacklisted_and_played_byUserId_Media']={}
    var_dict['isblacklisted_extraInfo_byUserId_Media']={}
    #dictionary of media item counts by userId
    var_dict['mediaCounts_byUserId']={}

    #lists of items to be deleted
    var_dict['deleteItems_Media']=[]
    var_dict['deleteItemsIdTracker_Media']=[]
    var_dict['deleteItems_createdMedia']=[]
    var_dict['deleteItemsIdTracker_createdMedia']=[]

    #dictionary of favortied and played items by userId
    var_dict['isfavorited_and_played_byUserId_Media'][user_info['user_id']]={}
    var_dict['isfavorited_extraInfo_byUserId_Media'][user_info['user_id']]={}
    #dictionary of whitetagged items by userId
    var_dict['iswhitetagged_and_played_byUserId_Media'][user_info['user_id']]={}
    var_dict['iswhitetagged_extraInfo_byUserId_Media'][user_info['user_id']]={}
    #dictionary of blacktagged items by userId
    var_dict['isblacktagged_and_played_byUserId_Media'][user_info['user_id']]={}
    var_dict['isblacktagged_extraInfo_byUserId_Media'][user_info['user_id']]={}
    #dictionary of whitelisted items by userId
    var_dict['iswhitelisted_and_played_byUserId_Media'][user_info['user_id']]={}
    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']]={}
    #dictionary of blacklisted items by userId
    var_dict['isblacklisted_and_played_byUserId_Media'][user_info['user_id']]={}
    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']]={}
    #dictionary of media item counts by userId
    var_dict['mediaCounts_byUserId'][user_info['user_id']]=defaultdict(dict)

    var_dict['currentUserPosition']=the_dict['currentUserPosition']

    #get library attributes for user in this position
    #user_bllib_keys_json_lensplit=user_bllib_keys_json[currentUserPosition].split(',')
    #user_wllib_keys_json_lensplit=user_wllib_keys_json[currentUserPosition].split(',')
    #user_bllib_netpath_json_lensplit=user_bllib_netpath_json[currentUserPosition].split(',')
    #user_wllib_netpath_json_lensplit=user_wllib_netpath_json[currentUserPosition].split(',')
    #user_bllib_path_json_lensplit=user_bllib_path_json[currentUserPosition].split(',')
    #user_wllib_path_json_lensplit=user_wllib_path_json[currentUserPosition].split(',')

    #get length of library attributes
    #len_user_bllib_keys_json_lensplit=len(user_bllib_keys_json_lensplit)
    #len_user_wllib_keys_json_lensplit=len(user_wllib_keys_json_lensplit)
    #len_user_bllib_netpath_json_lensplit=len(user_bllib_netpath_json_lensplit)
    #len_user_wllib_netpath_json_lensplit=len(user_wllib_netpath_json_lensplit)
    #len_user_bllib_path_json_lensplit=len(user_bllib_path_json_lensplit)
    #len_user_wllib_path_json_lensplit=len(user_wllib_path_json_lensplit)

    #find min length of library attributes
    #min_attribute_length=min(len_user_bllib_keys_json_lensplit,len_user_wllib_keys_json_lensplit,
                                #len_user_bllib_netpath_json_lensplit,len_user_wllib_netpath_json_lensplit,
                                #len_user_bllib_path_json_lensplit,len_user_wllib_path_json_lensplit)

    #find max length of library attributes
    #max_attribute_length=max(len_user_bllib_keys_json_lensplit,len_user_wllib_keys_json_lensplit,
                                #len_user_bllib_netpath_json_lensplit,len_user_wllib_netpath_json_lensplit,
                                #len_user_bllib_path_json_lensplit,len_user_wllib_path_json_lensplit)

    #make all list attributes the same length
    #while not (min_attribute_length == max_attribute_length):
        #if (len_user_bllib_keys_json_lensplit < max_attribute_length):
            #user_bllib_keys_json_lensplit.append('')
            #len_user_bllib_keys_json_lensplit += 1
        #if (len_user_wllib_keys_json_lensplit < max_attribute_length):
            #user_wllib_keys_json_lensplit.append('')
            #len_user_wllib_keys_json_lensplit += 1

        #if (len_user_bllib_netpath_json_lensplit < max_attribute_length):
            #user_bllib_netpath_json_lensplit.append('')
            #len_user_bllib_netpath_json_lensplit += 1
        #if (len_user_wllib_netpath_json_lensplit < max_attribute_length):
            #user_wllib_netpath_json_lensplit.append('')
            #len_user_wllib_netpath_json_lensplit += 1

        #if (len_user_bllib_path_json_lensplit < max_attribute_length):
            #user_bllib_path_json_lensplit.append('')
            #len_user_bllib_path_json_lensplit += 1
        #if (len_user_wllib_path_json_lensplit < max_attribute_length):
            #user_wllib_path_json_lensplit.append('')
            #len_user_wllib_path_json_lensplit += 1
        #min_attribute_length += 1

    var_dict['whitelist_length'] = sum(1 for _ in user_info['whitelist'])
    var_dict['blacklist_length'] = sum(1 for _ in user_info['blacklist'])
    if (var_dict['whitelist_length'] > var_dict['blacklist_length']):
        #var_dict['longest_list_length']=var_dict['whitelist_length']
        var_dict['shortest_list_length']=var_dict['blacklist_length']
        var_dict['list_diff']=var_dict['whitelist_length'] - var_dict['blacklist_length']
        #longest_list='whitelist'
        var_dict['shortest_list']='blacklist'
    elif (var_dict['blacklist_length'] > var_dict['whitelist_length']):
        #var_dict['longest_list_length']=var_dict['blacklist_length']
        var_dict['shortest_list_length']=var_dict['whitelist_length']
        var_dict['list_diff']=var_dict['blacklist_length'] - var_dict['whitelist_length']
        #longest_list='blacklist'
        var_dict['shortest_list']='whitelist'
    else:
        #var_dict['longest_list_length']=blacklist_length
        var_dict['shortest_list_length']=0
        var_dict['list_diff']=0
        #longest_list=''
        var_dict['shortest_list']='whitelist'

    for listlen in range(var_dict['list_diff']):
        #user_info[shortest_list].insert((shortest_list_length+listlen),{'lib_id':None,'lib_enabled':False,'collection_type':None,'path':None,'network_path':None})
        user_info[var_dict['shortest_list']].insert((var_dict['shortest_list_length']+listlen),{'lib_id':None,'lib_enabled':False,'collection_type':None,'path':None,'network_path':None})

    var_dict['media_found']=False

############# Media #############

    if ((var_dict['media_played_days'] >= 0) or (var_dict['media_created_days'] >= 0)):

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nProcessing " + var_dict['media_type_upper'] + " Items For UserId: " + str(user_info['user_id']),2,the_dict)

        var_dict['user_processed_item_Ids']=set()

        #currentSubPosition=0

        #for var_dict['this_blacklist_lib']['lib_id'],var_dict['this_whitelist_lib']['lib_id'],var_dict['this_blacklist_lib']['network_path'],var_dict['this_whitelist_lib']['network_path'],var_dict['this_blacklist_lib']['path'],var_dict['this_whitelist_lib']['path'] in zip(user_bllib_keys_json_lensplit,user_wllib_keys_json_lensplit,user_bllib_netpath_json_lensplit,user_wllib_netpath_json_lensplit,user_bllib_path_json_lensplit,user_wllib_path_json_lensplit):
        for var_dict['this_whitelist_lib'],var_dict['this_blacklist_lib'] in zip (user_info['whitelist'],user_info['blacklist']):

            #Initialize api_query_handler() variables for watched media items in blacklists
            var_dict['StartIndex_Blacklist']=0
            var_dict['TotalItems_Blacklist']=1
            var_dict['QueryLimit_Blacklist']=1
            var_dict['QueriesRemaining_Blacklist']=True
            var_dict['APIDebugMsg_Blacklist']=var_dict['media_type_lower'] + '_blacklist_media_items'

            #if not (var_dict['this_blacklist_lib']['lib_id'] == ''):
            if (var_dict['this_blacklist_lib']['lib_enabled']):
                #Build query for watched media items in blacklists
                var_dict['IncludeItemTypes_Blacklist']=var_dict['media_type_title']
                var_dict['FieldsState_Blacklist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
                var_dict['SortBy_Blacklist']='ParentIndexNumber,IndexNumber,Name'
                var_dict['SortOrder_Blacklist']='Ascending'
                var_dict['EnableUserData_Blacklist']='True'
                var_dict['Recursive_Blacklist']='True'
                var_dict['EnableImages_Blacklist']='False'
                var_dict['CollapseBoxSetItems_Blacklist']='False'
                var_dict['IsPlayedState_Blacklist']=get_isPlayedCreated_FilterValue(the_dict,var_dict)

                if (var_dict['media_type_lower'] == 'episode'):
                    var_dict['FieldsState_Blacklist']=var_dict['FieldsState_Blacklist'] + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(var_dict['server_brand'])):
                        var_dict['SortBy_Blacklist']='SeriesSortName,' + var_dict['SortBy_Blacklist']
                    else:
                        var_dict['SortBy_Blacklist']='SeriesName,' + var_dict['SortBy_Blacklist']

                if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
                    var_dict['FieldsState_Blacklist']=var_dict['FieldsState_Blacklist'] + ',ArtistItems,AlbumId,AlbumArtist' 
                    var_dict['SortBy_Blacklist']='Artists,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Blacklist']
                    if (isEmbyServer(var_dict['server_brand'])):
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Blacklist']+=',audiobook,book'
                    else:
                        if (var_dict['media_type_lower'] == 'audiobook'):
                            var_dict['IncludeItemTypes_Blacklist']=',book'

            #Initialize api_query_handler() variables for watched media items in whitelists
            var_dict['StartIndex_Whitelist']=0
            var_dict['TotalItems_Whitelist']=1
            var_dict['QueryLimit_Whitelist']=1
            var_dict['QueriesRemaining_Whitelist']=True
            var_dict['APIDebugMsg_Whitelist']=var_dict['media_type_lower'] + '_whitelist_media_items'

            #if not (var_dict['this_whitelist_lib']['lib_id'] == ''):
            if (var_dict['this_whitelist_lib']['lib_enabled']):
                #Build query for watched media items in whitelists
                var_dict['IncludeItemTypes_Whitelist']=var_dict['media_type_title']
                var_dict['FieldsState_Whitelist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
                var_dict['SortBy_Whitelist']='ParentIndexNumber,IndexNumber,Name'
                var_dict['SortOrder_Whitelist']='Ascending'
                var_dict['EnableUserData_Whitelist']='True'
                var_dict['Recursive_Whitelist']='True'
                var_dict['EnableImages_Whitelist']='False'
                var_dict['CollapseBoxSetItems_Whitelist']='False'
                var_dict['IsPlayedState_Whitelist']=get_isPlayedCreated_FilterValue(the_dict,var_dict)

                if (var_dict['media_type_lower'] == 'episode'):
                    var_dict['FieldsState_Whitelist']=var_dict['FieldsState_Whitelist'] + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(var_dict['server_brand'])):
                        var_dict['SortBy_Whitelist']='SeriesSortName,' + var_dict['SortBy_Whitelist']
                    else:
                        var_dict['SortBy_Whitelist']='SeriesName,' + var_dict['SortBy_Whitelist']

                if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
                    var_dict['FieldsState_Whitelist']=var_dict['FieldsState_Whitelist'] + ',ArtistItems,AlbumId,AlbumArtist'
                    var_dict['SortBy_Whitelist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Whitelist']
                    if (isEmbyServer(var_dict['server_brand'])):
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Whitelist']+=',AudioBook,Book'
                    else:
                        if (var_dict['media_type_lower'] == 'audiobook'):
                            var_dict['IncludeItemTypes_Whitelist']=',Book'

            #Initialize api_query_handler() variables for Favorited from Blacklist media items
            var_dict['StartIndex_Favorited_From_Blacklist']=0
            var_dict['TotalItems_Favorited_From_Blacklist']=1
            var_dict['QueryLimit_Favorited_From_Blacklist']=1
            var_dict['QueriesRemaining_Favorited_From_Blacklist']=True
            var_dict['APIDebugMsg_Favorited_From_Blacklist']=var_dict['media_type_lower'] + '_Favorited_From_Blacklisted_media_items'

            #if not (var_dict['this_blacklist_lib']['lib_id'] == ''):
            if (var_dict['this_blacklist_lib']['lib_enabled']):
                    #Build query for Favorited_From_Blacklist media items
                var_dict['IncludeItemTypes_Favorited_From_Blacklist']=var_dict['media_type_title']
                var_dict['FieldsState_Favorited_From_Blacklist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
                var_dict['SortBy_Favorited_From_Blacklist']='ParentIndexNumber,IndexNumber,Name'
                var_dict['SortOrder_Favorited_From_Blacklist']='Ascending'
                var_dict['EnableUserData_Favorited_From_Blacklist']='True'
                var_dict['Recursive_Favorited_From_Blacklist']='True'
                var_dict['EnableImages_Favorited_From_Blacklist']='False'
                var_dict['CollapseBoxSetItems_Favorited_From_Blacklist']='False'
                var_dict['IsFavorite_From_Blacklist']='True'

                if (var_dict['media_type_lower'] == 'movie'):
                    var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',BoxSet,CollectionFolder'

                if (var_dict['media_type_lower'] == 'episode'):
                    var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',Season,Series,CollectionFolder'
                    var_dict['FieldsState_Favorited_From_Blacklist']=var_dict['FieldsState_Favorited_From_Blacklist'] + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(var_dict['server_brand'])):
                        var_dict['SortBy_Favorited_From_Blacklist']='SeriesSortName,' + var_dict['SortBy_Favorited_From_Blacklist']
                    else:
                        var_dict['SortBy_Favorited_From_Blacklist']='SeriesName,' + var_dict['SortBy_Favorited_From_Blacklist']

                if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
                    var_dict['FieldsState_Favorited_From_Blacklist']=var_dict['FieldsState_Favorited_From_Blacklist'] + ',ArtistItems,AlbumId,AlbumArtist'
                    var_dict['SortBy_Favorited_From_Blacklist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Favorited_From_Blacklist']
                    if (isEmbyServer(var_dict['server_brand'])):
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',MusicAlbum,Playlist,CollectionFolder'
                        elif (var_dict['media_type_lower'] == 'audiobook'):
                            var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for Favorited from Whitelist media items
            var_dict['StartIndex_Favorited_From_Whitelist']=0
            var_dict['TotalItems_Favorited_From_Whitelist']=1
            var_dict['QueryLimit_Favorited_From_Whitelist']=1
            var_dict['QueriesRemaining_Favorited_From_Whitelist']=True
            var_dict['APIDebugMsg_Favorited_From_Whitelist']=var_dict['media_type_lower'] + '_Favorited_From_Whitelisted_media_items'

            #if not (var_dict['this_whitelist_lib']['lib_id'] == ''):
            if (var_dict['this_whitelist_lib']['lib_enabled']):
                #Build query for Favorited_From_Whitelist media items
                var_dict['IncludeItemTypes_Favorited_From_Whitelist']=var_dict['media_type_title']
                var_dict['FieldsState_Favorited_From_Whitelist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
                var_dict['SortBy_Favorited_From_Whitelist']='ParentIndexNumber,IndexNumber,Name'
                var_dict['SortOrder_Favorited_From_Whitelist']='Ascending'
                var_dict['EnableUserData_Favorited_From_Whitelist']='True'
                var_dict['Recursive_Favorited_From_Whitelist']='True'
                var_dict['EnableImages_Favorited_From_Whitelist']='False'
                var_dict['CollapseBoxSetItems_Favorited_From_Whitelist']='False'
                var_dict['IsFavorite_From_Whitelist']='True'

                if (var_dict['media_type_lower'] == 'movie'):
                    var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',BoxSet,CollectionFolder'

                if (var_dict['media_type_lower'] == 'episode'):
                    var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',Season,Series,CollectionFolder'
                    var_dict['FieldsState_Favorited_From_Whitelist']=var_dict['FieldsState_Favorited_From_Whitelist'] + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(var_dict['server_brand'])):
                        var_dict['SortBy_Favorited_From_Whitelist']='SeriesSortName,' + var_dict['SortBy_Favorited_From_Whitelist']
                    else:
                        var_dict['SortBy_Favorited_From_Whitelist']='SeriesName,' + var_dict['SortBy_Favorited_From_Whitelist']

                if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
                    var_dict['FieldsState_Favorited_From_Whitelist']=var_dict['FieldsState_Favorited_From_Whitelist'] + ',ArtistItems,AlbumId,AlbumArtist'
                    var_dict['SortBy_Favorited_From_Whitelist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Favorited_From_Whitelist']
                    if (isEmbyServer(var_dict['server_brand'])):
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                        elif (var_dict['media_type_lower'] == 'audiobook'):
                            var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for tagged media items
            var_dict['StartIndex_Blacktagged_From_Blacklist']=0
            var_dict['TotalItems_Blacktagged_From_Blacklist']=1
            var_dict['QueryLimit_Blacktagged_From_Blacklist']=1
            var_dict['QueriesRemaining_Blacktagged_From_Blacklist']=True
            var_dict['APIDebugMsg_Blacktagged_From_Blacklist']=var_dict['media_type_lower'] + '_blacktagged_from_blacklist_media_items'

            #if not (var_dict['this_blacklist_lib']['lib_id'] == ''):
            if (var_dict['this_blacklist_lib']['lib_enabled']):
                #Build query for blacktagged media items from blacklist
                var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']=var_dict['media_type_title']
                var_dict['FieldsState_Blacktagged_From_Blacklist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
                var_dict['SortBy_Blacktagged_From_Blacklist']='ParentIndexNumber,IndexNumber,Name'
                var_dict['SortOrder_Blacktagged_From_Blacklist']='Ascending'
                var_dict['EnableUserData_Blacktagged_From_Blacklist']='True'
                var_dict['Recursive_Blacktagged_From_Blacklist']='True'
                var_dict['EnableImages_Blacktagged_From_Blacklist']='False'
                var_dict['CollapseBoxSetItems_Blacktagged_From_Blacklist']='False'
                #Encode blacktags so they are url acceptable
                var_dict['Blacktags_Parsed']=list_to_urlparsed_string(var_dict['blacktags'])

                if (var_dict['media_type_lower'] == 'movie'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',BoxSet,CollectionFolder'

                if (var_dict['media_type_lower'] == 'episode'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',Season,Series,CollectionFolder'
                    var_dict['FieldsState_Blacktagged_From_Blacklist']=var_dict['FieldsState_Blacktagged_From_Blacklist'] + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(var_dict['server_brand'])):
                        var_dict['SortBy_Blacktagged_From_Blacklist']='SeriesSortName,' + var_dict['SortBy_Blacktagged_From_Blacklist']
                    else:
                        var_dict['SortBy_Blacktagged_From_Blacklist']='SeriesName,' + var_dict['SortBy_Blacktagged_From_Blacklist']

                if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
                    var_dict['FieldsState_Blacktagged_From_Blacklist']=var_dict['FieldsState_Blacktagged_From_Blacklist'] + ',ArtistItems,AlbumId,AlbumArtist'
                    var_dict['SortBy_Blacktagged_From_Blacklist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Blacktagged_From_Blacklist']
                    if (isEmbyServer(var_dict['server_brand'])):
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                        elif (var_dict['media_type_lower'] == 'audiobook'):
                            var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for tagged media items
            var_dict['StartIndex_Blacktagged_From_Whitelist']=0
            var_dict['TotalItems_Blacktagged_From_Whitelist']=1
            var_dict['QueryLimit_Blacktagged_From_Whitelist']=1
            var_dict['QueriesRemaining_Blacktagged_From_Whitelist']=True
            var_dict['APIDebugMsg_Blacktagged_From_Whitelist']=var_dict['media_type_lower'] + '_blacktagged_from whitelisted_media_items'

            #if not (var_dict['this_whitelist_lib']['lib_id'] == ''):
            if (var_dict['this_whitelist_lib']['lib_enabled']):
                #Build query for blacktagged media items from whitelist
                var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']=var_dict['media_type_title']
                var_dict['FieldsState_Blacktagged_From_Whitelist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
                var_dict['SortBy_Blacktagged_From_Whitelist']='ParentIndexNumber,IndexNumber,Name'
                var_dict['SortOrder_Blacktagged_From_Whitelist']='Ascending'
                var_dict['EnableUserData_Blacktagged_From_Whitelist']='True'
                var_dict['Recursive_Blacktagged_From_Whitelist']='True'
                var_dict['EnableImages_Blacktagged_From_Whitelist']='False'
                var_dict['CollapseBoxSetItems_Blacktagged_From_Whitelist']='False'
                #Encode blacktags so they are url acceptable
                var_dict['Blacktags_Parsed']=list_to_urlparsed_string(var_dict['blacktags'])

                if (var_dict['media_type_lower'] == 'movie'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',BoxSet,CollectionFolder'

                if (var_dict['media_type_lower'] == 'episode'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',Season,Series,CollectionFolder'
                    var_dict['FieldsState_Blacktagged_From_Whitelist']=var_dict['FieldsState_Blacktagged_From_Whitelist'] + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(var_dict['server_brand'])):
                        var_dict['SortBy_Blacktagged_From_Whitelist']='SeriesSortName,' + var_dict['SortBy_Blacktagged_From_Whitelist']
                    else:
                        var_dict['SortBy_Blacktagged_From_Whitelist']='SeriesName,' + var_dict['SortBy_Blacktagged_From_Whitelist']

                if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
                    var_dict['FieldsState_Blacktagged_From_Whitelist']=var_dict['FieldsState_Blacktagged_From_Whitelist'] + ',ArtistItems,AlbumId,AlbumArtist'
                    var_dict['SortBy_Blacktagged_From_Whitelist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Blacktagged_From_Whitelist']
                    if (isEmbyServer(var_dict['server_brand'])):
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                        elif (var_dict['media_type_lower'] == 'audiobook'):
                            var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for tagged media items
            var_dict['StartIndex_Whitetagged_From_Blacklist']=0
            var_dict['TotalItems_Whitetagged_From_Blacklist']=1
            var_dict['QueryLimit_Whitetagged_From_Blacklist']=1
            var_dict['QueriesRemaining_Whitetagged_From_Blacklist']=True
            var_dict['APIDebugMsg_Whitetagged_From_Blacklist']=var_dict['media_type_lower'] + '_whitetagged_from_blacklisted_media_items'

            #if not (var_dict['this_blacklist_lib']['lib_id'] == ''):
            if (var_dict['this_blacklist_lib']['lib_enabled']):
                #Build query for whitetagged media items from blacklist
                var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']=var_dict['media_type_title']
                var_dict['FieldsState_Whitetagged_From_Blacklist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
                var_dict['SortBy_Whitetagged_From_Blacklist']='ParentIndexNumber,IndexNumber,Name'
                var_dict['SortOrder_Whitetagged_From_Blacklist']='Ascending'
                var_dict['EnableUserData_Whitetagged_From_Blacklist']='True'
                var_dict['Recursive_Whitetagged_From_Blacklist']='True'
                var_dict['EnableImages_Whitetagged_From_Blacklist']='False'
                var_dict['CollapseBoxSetItems_Whitetagged_From_Blacklist']='False'
                #Encode whitetags so they are url acceptable
                var_dict['Whitetags_Parsed']=list_to_urlparsed_string(var_dict['whitetags'])

                if (var_dict['media_type_lower'] == 'movie'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',BoxSet,CollectionFolder'

                if (var_dict['media_type_lower'] == 'episode'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',Season,Series,CollectionFolder'
                    var_dict['FieldsState_Whitetagged_From_Blacklist']=var_dict['FieldsState_Whitetagged_From_Blacklist'] + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(var_dict['server_brand'])):
                        var_dict['SortBy_Whitetagged_From_Blacklist']='SeriesSortName,' + var_dict['SortBy_Whitetagged_From_Blacklist']
                    else:
                        var_dict['SortBy_Whitetagged_From_Blacklist']='SeriesName,' + var_dict['SortBy_Whitetagged_From_Blacklist']

                if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
                    var_dict['FieldsState_Whitetagged_From_Blacklist']=var_dict['FieldsState_Whitetagged_From_Blacklist'] + ',ArtistItems,AlbumId,AlbumArtist'
                    var_dict['SortBy_Whitetagged_From_Blacklist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Whitetagged_From_Blacklist']
                    if (isEmbyServer(var_dict['server_brand'])):
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',Audio,AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                        elif (var_dict['media_type_lower'] == 'audiobook'):
                            var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for tagged media items
            var_dict['StartIndex_Whitetagged_From_Whitelist']=0
            var_dict['TotalItems_Whitetagged_From_Whitelist']=1
            var_dict['QueryLimit_Whitetagged_From_Whitelist']=1
            var_dict['QueriesRemaining_Whitetagged_From_Whitelist']=True
            var_dict['APIDebugMsg_Whitetagged_From_Whitelist']=var_dict['media_type_lower'] + '_whitetagged_from_whitelisted_media_items'

            #if not (var_dict['this_whitelist_lib']['lib_id'] == ''):
            if (var_dict['this_whitelist_lib']['lib_enabled']):
                #Build query for whitetagged media items from whitelist
                var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']=var_dict['media_type_title']
                var_dict['FieldsState_Whitetagged_From_Whitelist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
                var_dict['SortBy_Whitetagged_From_Whitelist']='ParentIndexNumber,IndexNumber,Name'
                var_dict['SortOrder_Whitetagged_From_Whitelist']='Ascending'
                var_dict['EnableUserData_Whitetagged_From_Whitelist']='True'
                var_dict['Recursive_Whitetagged_From_Whitelist']='True'
                var_dict['EnableImages_Whitetagged_From_Whitelist']='False'
                var_dict['CollapseBoxSetItems_Whitetagged_From_Whitelist']='False'
                #Encode whitetags so they are url acceptable
                var_dict['Whitetags_Parsed']=list_to_urlparsed_string(var_dict['whitetags'])

                if (var_dict['media_type_lower'] == 'movie'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',BoxSet,CollectionFolder'

                if (var_dict['media_type_lower'] == 'episode'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',Season,Series,CollectionFolder'
                    var_dict['FieldsState_Whitetagged_From_Whitelist']=var_dict['FieldsState_Whitetagged_From_Whitelist'] + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(var_dict['server_brand'])):
                        var_dict['SortBy_Whitetagged_From_Whitelist']='SeriesSortName,' + var_dict['SortBy_Whitetagged_From_Whitelist']
                    else:
                        var_dict['SortBy_Whitetagged_From_Whitelist']='SeriesName,' + var_dict['SortBy_Whitetagged_From_Whitelist']

                if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
                    var_dict['FieldsState_Whitetagged_From_Whitelist']=var_dict['FieldsState_Whitetagged_From_Whitelist'] + ',ArtistItems,AlbumId,AlbumArtist'
                    var_dict['SortBy_Whitetagged_From_Whitelist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Whitetagged_From_Whitelist']
                    if (isEmbyServer(var_dict['server_brand'])):
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (var_dict['media_type_lower'] == 'audio'):
                            var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',MusicAlbum,Playlist,CollectionFolder'
                        elif (var_dict['media_type_lower'] == 'audiobook'):
                            var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

            var_dict['QueryItemsRemaining_All']=True

            while (var_dict['QueryItemsRemaining_All']):

                #if not (var_dict['this_blacklist_lib']['lib_id'] == ''):
                if (var_dict['this_blacklist_lib']['lib_enabled']):
                    #Built query for watched items in blacklists
                    var_dict['apiQuery_Blacklist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_blacklist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Blacklist'] +
                    '&StartIndex=' + str(var_dict['StartIndex_Blacklist']) + '&Limit=' + str(var_dict['QueryLimit_Blacklist']) + '&IsPlayed=' + var_dict['IsPlayedState_Blacklist'] +
                    '&Fields=' + var_dict['FieldsState_Blacklist'] + '&Recursive=' + var_dict['Recursive_Blacklist'] + '&SortBy=' + var_dict['SortBy_Blacklist'] + '&SortOrder=' + var_dict['SortOrder_Blacklist'] +
                    '&EnableImages=' + var_dict['EnableImages_Blacklist'] + '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Blacklist'] + '&EnableUserData=' + var_dict['EnableUserData_Blacklist'] + '&api_key=' + var_dict['auth_key'])

                    #Send the API query for for watched media items in blacklists
                    #var_dict['data_Blacklist'],var_dict['StartIndex_Blacklist'],var_dict['TotalItems_Blacklist'],var_dict['QueryLimit_Blacklist'],var_dict['QueriesRemaining_Blacklist']=api_query_handler(var_dict['apiQuery_Blacklist'],var_dict['StartIndex_Blacklist'],var_dict['TotalItems_Blacklist'],var_dict['QueryLimit_Blacklist'],var_dict['APIDebugMsg_Blacklist'],the_dict)
                    var_dict=api_query_handler('Blacklist',var_dict,the_dict)
                else:
                    #When no media items are blacklisted; simulate an empty query being returned
                    #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                    var_dict['data_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    var_dict['QueryLimit_Blacklist']=0
                    var_dict['QueriesRemaining_Blacklist']=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo watched media items are blacklisted",2,the_dict)

                #if not (var_dict['this_whitelist_lib']['lib_id'] == ''):
                if (var_dict['this_whitelist_lib']['lib_enabled']):
                    #Built query for watched items in whitelists
                    var_dict['apiQuery_Whitelist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_whitelist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Whitelist'] +
                    '&StartIndex=' + str(var_dict['StartIndex_Whitelist']) + '&Limit=' + str(var_dict['QueryLimit_Whitelist']) + '&IsPlayed=' + var_dict['IsPlayedState_Whitelist'] +
                    '&Fields=' + var_dict['FieldsState_Whitelist'] + '&Recursive=' + var_dict['Recursive_Whitelist'] + '&SortBy=' + var_dict['SortBy_Whitelist'] + '&SortOrder=' + var_dict['SortOrder_Whitelist'] +
                    '&EnableImages=' + var_dict['EnableImages_Whitelist'] + '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Whitelist'] + '&EnableUserData=' + var_dict['EnableUserData_Whitelist'] + '&api_key=' + var_dict['auth_key'])

                    #Send the API query for for watched media items in whitelists
                    #var_dict['data_Whitelist'],var_dict['StartIndex_Whitelist'],var_dict['TotalItems_Whitelist'],var_dict['QueryLimit_Whitelist'],var_dict['QueriesRemaining_Whitelist']=api_query_handler(var_dict['apiQuery_Whitelist'],var_dict['StartIndex_Whitelist'],var_dict['TotalItems_Whitelist'],var_dict['QueryLimit_Whitelist'],var_dict['APIDebugMsg_Whitelist'],the_dict)
                    var_dict=api_query_handler('Whitelist',var_dict,the_dict)
                else:
                    #When no media items are whitelisted; simulate an empty query being returned
                    #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
                    var_dict['data_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    var_dict['QueryLimit_Whitelist']=0
                    var_dict['QueriesRemaining_Whitelist']=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo watched media items are whitelisted",2,the_dict)

                #if not (var_dict['this_blacklist_lib']['lib_id'] == ''):
                if (var_dict['this_blacklist_lib']['lib_enabled']):
                    #Built query for Favorited from Blacklist media items
                    var_dict['apiQuery_Favorited_From_Blacklist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_blacklist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Favorited_From_Blacklist'] +
                    '&StartIndex=' + str(var_dict['StartIndex_Favorited_From_Blacklist']) + '&Limit=' + str(var_dict['QueryLimit_Favorited_From_Blacklist']) + '&Fields=' + var_dict['FieldsState_Favorited_From_Blacklist'] +
                    '&Recursive=' + var_dict['Recursive_Favorited_From_Blacklist'] + '&SortBy=' + var_dict['SortBy_Favorited_From_Blacklist'] + '&SortOrder=' + var_dict['SortOrder_Favorited_From_Blacklist'] + '&EnableImages=' + var_dict['EnableImages_Favorited_From_Blacklist'] +
                    '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Favorited_From_Blacklist'] + '&IsFavorite=' + var_dict['IsFavorite_From_Blacklist'] + '&EnableUserData=' + var_dict['EnableUserData_Favorited_From_Blacklist'] + '&api_key=' + var_dict['auth_key'])

                    #Send the API query for for Favorited from Blacklist media items
                    #var_dict['data_Favorited_From_Blacklist'],var_dict['StartIndex_Favorited_From_Blacklist'],var_dict['TotalItems_Favorited_From_Blacklist'],var_dict['QueryLimit_Favorited_From_Blacklist'],var_dict['QueriesRemaining_Favorited_From_Blacklist']=api_query_handler(var_dict['apiQuery_Favorited_From_Blacklist'],var_dict['StartIndex_Favorited_From_Blacklist'],var_dict['TotalItems_Favorited_From_Blacklist'],var_dict['QueryLimit_Favorited_From_Blacklist'],var_dict['APIDebugMsg_Favorited_From_Blacklist'],the_dict)
                    var_dict=api_query_handler('Favorited_From_Blacklist',var_dict,the_dict)
                else:
                    #When no media items are blacklisted; simulate an empty query being returned
                    #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                    var_dict['data_Favorited_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    var_dict['QueryLimit_Favorited_From_Blacklist']=0
                    var_dict['QueriesRemaining_Favorited_From_Blacklist']=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo favorited media items are blacklisted",2,the_dict)

                #if not (var_dict['this_whitelist_lib']['lib_id'] == ''):
                if (var_dict['this_whitelist_lib']['lib_enabled']):
                    #Built query for Favorited From Whitelist media items
                    var_dict['apiQuery_Favorited_From_Whitelist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_whitelist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Favorited_From_Whitelist'] +
                    '&StartIndex=' + str(var_dict['StartIndex_Favorited_From_Whitelist']) + '&Limit=' + str(var_dict['QueryLimit_Favorited_From_Whitelist']) + '&Fields=' + var_dict['FieldsState_Favorited_From_Whitelist'] +
                    '&Recursive=' + var_dict['Recursive_Favorited_From_Whitelist'] + '&SortBy=' + var_dict['SortBy_Favorited_From_Whitelist'] + '&SortOrder=' + var_dict['SortOrder_Favorited_From_Whitelist'] + '&EnableImages=' + var_dict['EnableImages_Favorited_From_Whitelist'] +
                    '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Favorited_From_Whitelist'] + '&IsFavorite=' + var_dict['IsFavorite_From_Whitelist'] + '&EnableUserData=' + var_dict['EnableUserData_Favorited_From_Whitelist'] + '&api_key=' + var_dict['auth_key'])

                    #Send the API query for for Favorited from Whitelist media items
                    #var_dict['data_Favorited_From_Whitelist'],var_dict['StartIndex_Favorited_From_Whitelist'],var_dict['TotalItems_Favorited_From_Whitelist'],var_dict['QueryLimit_Favorited_From_Whitelist'],var_dict['QueriesRemaining_Favorited_From_Whitelist']=api_query_handler(var_dict['apiQuery_Favorited_From_Whitelist'],var_dict['StartIndex_Favorited_From_Whitelist'],var_dict['TotalItems_Favorited_From_Whitelist'],var_dict['QueryLimit_Favorited_From_Whitelist'],var_dict['APIDebugMsg_Favorited_From_Whitelist'],the_dict)
                    var_dict=api_query_handler('Favorited_From_Whitelist',var_dict,the_dict)
                else:
                    #When no media items are whitelisted; simulate an empty query being returned
                    #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
                    var_dict['data_Favorited_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    var_dict['QueryLimit_Favorited_From_Whitelist']=0
                    var_dict['QueriesRemaining_Favorited_From_Whitelist']=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo favorited media items are whitelisted",2,the_dict)

                #Check if blacktag or blacklist are not an empty strings
                #if (( not (var_dict['Blacktags_Parsed'] == '')) and ( not (var_dict['this_blacklist_lib']['lib_id'] == ''))):
                if ((not var_dict['Blacktags_Parsed']) and (var_dict['this_blacklist_lib']['lib_enabled'])):
                    #Built query for blacktagged from blacklist media items
                    var_dict['apiQuery_Blacktagged_From_Blacklist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_blacklist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Blacktagged_From_Blacklist'] +
                    '&StartIndex=' + str(var_dict['StartIndex_Blacktagged_From_Blacklist']) + '&Limit=' + str(var_dict['QueryLimit_Blacktagged_From_Blacklist']) + '&Fields=' + var_dict['FieldsState_Blacktagged_From_Blacklist'] +
                    '&Recursive=' + var_dict['Recursive_Blacktagged_From_Blacklist'] + '&SortBy=' + var_dict['SortBy_Blacktagged_From_Blacklist'] + '&SortOrder=' + var_dict['SortOrder_Blacktagged_From_Blacklist'] + '&EnableImages=' + var_dict['EnableImages_Blacktagged_From_Blacklist'] +
                    '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Blacktagged_From_Blacklist'] + '&Tags=' + var_dict['Blacktags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Blacktagged_From_Blacklist'] + '&api_key=' + var_dict['auth_key'])

                    #Send the API query for for blacktagged from blacklist media items
                    #var_dict['data_Blacktagged_From_Blacklist'],var_dict['StartIndex_Blacktagged_From_Blacklist'],var_dict['TotalItems_Blacktagged_From_Blacklist'],var_dict['QueryLimit_Blacktagged_From_Blacklist'],var_dict['QueriesRemaining_Blacktagged_From_Blacklist']=api_query_handler(var_dict['apiQuery_Blacktagged_From_Blacklist'],var_dict['StartIndex_Blacktagged_From_Blacklist'],var_dict['TotalItems_Blacktagged_From_Blacklist'],var_dict['QueryLimit_Blacktagged_From_Blacklist'],var_dict['APIDebugMsg_Blacktagged_From_Blacklist'],the_dict)
                    var_dict=api_query_handler('Blacktagged_From_Blacklist',var_dict,the_dict)
                else: #((var_dict['Blacktags_Parsed'] == '') or (var_dict['this_blacklist_lib']['lib_id'] == ''))
                    var_dict['data_Blacktagged_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    var_dict['QueryLimit_Blacktagged_From_Blacklist']=0
                    var_dict['QueriesRemaining_Blacktagged_From_Blacklist']=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo blacktagged media items are blacklisted",2,the_dict)

                #Check if blacktag or whitelist are not an empty strings
                #if (( not (var_dict['Blacktags_Parsed'] == '')) and ( not (var_dict['this_whitelist_lib']['lib_id'] == ''))):
                if ((not var_dict['Blacktags_Parsed']) and (var_dict['this_whitelist_lib']['lib_enabled'])):
                    #Built query for blacktagged from whitelist media items
                    var_dict['apiQuery_Blacktagged_From_Whitelist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_whitelist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Blacktagged_From_Whitelist'] +
                    '&StartIndex=' + str(var_dict['StartIndex_Blacktagged_From_Whitelist']) + '&Limit=' + str(var_dict['QueryLimit_Blacktagged_From_Whitelist']) + '&Fields=' + var_dict['FieldsState_Blacktagged_From_Whitelist'] +
                    '&Recursive=' + var_dict['Recursive_Blacktagged_From_Whitelist'] + '&SortBy=' + var_dict['SortBy_Blacktagged_From_Whitelist'] + '&SortOrder=' + var_dict['SortOrder_Blacktagged_From_Whitelist'] + '&EnableImages=' + var_dict['EnableImages_Blacktagged_From_Whitelist'] +
                    '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Blacktagged_From_Whitelist'] + '&Tags=' + var_dict['Blacktags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Blacktagged_From_Whitelist'] + '&api_key=' + var_dict['auth_key'])

                    #Send the API query for for blacktagged from whitelist media items
                    #var_dict['data_Blacktagged_From_Whitelist'],var_dict['StartIndex_Blacktagged_From_Whitelist'],var_dict['TotalItems_Blacktagged_From_Whitelist'],var_dict['QueryLimit_Blacktagged_From_Whitelist'],var_dict['QueriesRemaining_Blacktagged_From_Whitelist']=api_query_handler(var_dict['apiQuery_Blacktagged_From_Whitelist'],var_dict['StartIndex_Blacktagged_From_Whitelist'],var_dict['TotalItems_Blacktagged_From_Whitelist'],var_dict['QueryLimit_Blacktagged_From_Whitelist'],var_dict['APIDebugMsg_Blacktagged_From_Whitelist'],the_dict)
                    var_dict=api_query_handler('Blacktagged_From_Whitelist',var_dict,the_dict)
                else: #((var_dict['Blacktags_Parsed'] == '') or (var_dict['this_whitelist_lib']['lib_id'] == ''))
                    var_dict['data_Blacktagged_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    var_dict['QueryLimit_Blacktagged_From_Whitelist']=0
                    var_dict['QueriesRemaining_Blacktagged_From_Whitelist']=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo blacktagged media items are whitelisted",2,the_dict)

                #Check if whitetag or blacklist are not an empty strings
                #if (( not (var_dict['Whitetags_Parsed'] == '')) and ( not (var_dict['this_blacklist_lib']['lib_id'] == ''))):
                if ((not var_dict['Whitetags_Parsed']) and (var_dict['this_blacklist_lib']['lib_enabled'])):
                    #Built query for whitetagged from Blacklist media items
                    var_dict['apiQuery_Whitetagged_From_Blacklist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_blacklist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Whitetagged_From_Blacklist'] +
                    '&StartIndex=' + str(var_dict['StartIndex_Whitetagged_From_Blacklist']) + '&Limit=' + str(var_dict['QueryLimit_Whitetagged_From_Blacklist']) + '&Fields=' + var_dict['FieldsState_Whitetagged_From_Blacklist'] +
                    '&Recursive=' + var_dict['Recursive_Whitetagged_From_Blacklist'] + '&SortBy=' + var_dict['SortBy_Whitetagged_From_Blacklist'] + '&SortOrder=' + var_dict['SortOrder_Whitetagged_From_Blacklist'] + '&EnableImages=' + var_dict['EnableImages_Whitetagged_From_Blacklist'] +
                    '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Whitetagged_From_Blacklist'] + '&Tags=' + var_dict['Whitetags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Whitetagged_From_Blacklist'] + '&api_key=' + var_dict['auth_key'])

                    #Send the API query for for whitetagged from Blacklist= media items
                    #var_dict['data_Whitetagged_From_Blacklist'],var_dict['StartIndex_Whitetagged_From_Blacklist'],var_dict['TotalItems_Whitetagged_From_Blacklist'],var_dict['QueryLimit_Whitetagged_From_Blacklist'],var_dict['QueriesRemaining_Whitetagged_From_Blacklist']=api_query_handler(var_dict['apiQuery_Whitetagged_From_Blacklist'],var_dict['StartIndex_Whitetagged_From_Blacklist'],var_dict['TotalItems_Whitetagged_From_Blacklist'],var_dict['QueryLimit_Whitetagged_From_Blacklist'],var_dict['APIDebugMsg_Whitetagged_From_Blacklist'],the_dict)
                    var_dict=api_query_handler('Whitetagged_From_Blacklist',var_dict,the_dict)
                else: #(Whitetags_Tagged_From_Blacklist == '')
                    var_dict['data_Whitetagged_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    var_dict['QueryLimit_Whitetagged_From_Blacklist']=0
                    var_dict['QueriesRemaining_Whitetagged_From_Blacklist']=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo whitetagged media items are blacklisted",2,the_dict)

                #Check if whitetag or whitelist are not an empty strings
                #if (( not (var_dict['Whitetags_Parsed'] == '')) and ( not (var_dict['this_whitelist_lib']['lib_id'] == ''))):
                if ((not var_dict['Whitetags_Parsed']) and (var_dict['this_whitelist_lib']['lib_enabled'])):
                    #Built query for whitetagged_From_Whitelist= media items
                    var_dict['apiQuery_Whitetagged_From_Whitelist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_whitelist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Whitetagged_From_Whitelist'] +
                    '&StartIndex=' + str(var_dict['StartIndex_Whitetagged_From_Whitelist']) + '&Limit=' + str(var_dict['QueryLimit_Whitetagged_From_Whitelist']) + '&Fields=' + var_dict['FieldsState_Whitetagged_From_Whitelist'] +
                    '&Recursive=' + var_dict['Recursive_Whitetagged_From_Whitelist'] + '&SortBy=' + var_dict['SortBy_Whitetagged_From_Whitelist'] + '&SortOrder=' + var_dict['SortOrder_Whitetagged_From_Whitelist'] + '&EnableImages=' + var_dict['EnableImages_Whitetagged_From_Whitelist'] +
                    '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Whitetagged_From_Whitelist'] + '&Tags=' + var_dict['Whitetags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Whitetagged_From_Whitelist'] + '&api_key=' + var_dict['auth_key'])

                    #Send the API query for for whitetagged_From_Whitelist= media items
                    #var_dict['data_Whitetagged_From_Whitelist'],var_dict['StartIndex_Whitetagged_From_Whitelist'],var_dict['TotalItems_Whitetagged_From_Whitelist'],var_dict['QueryLimit_Whitetagged_From_Whitelist'],var_dict['QueriesRemaining_Whitetagged_From_Whitelist']=api_query_handler(var_dict['apiQuery_Whitetagged_From_Whitelist'],var_dict['StartIndex_Whitetagged_From_Whitelist'],var_dict['TotalItems_Whitetagged_From_Whitelist'],var_dict['QueryLimit_Whitetagged_From_Whitelist'],var_dict['APIDebugMsg_Whitetagged_From_Whitelist'],the_dict)
                    var_dict=api_query_handler('Whitetagged_From_Whitelist',var_dict,the_dict)
                else: #(var_dict['Whitetags_Parsed'] == '')
                    var_dict['data_Whitetagged_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    var_dict['QueryLimit_Whitetagged_From_Whitelist']=0
                    var_dict['QueriesRemaining_Whitetagged_From_Whitelist']=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo whitetagged media items are whitelisted",2,the_dict)

                #Define reasoning for lookup
                var_dict['APIDebugMsg_Child_Of_Favorited_Item_From_Blacklist']='Child_Of_Favorited_Item_From_Blacklist'
                #data_Favorited_From_Blacklist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Blacklist,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Favorited_From_Blacklist_Child,media_played_days,media_created_days)
                var_dict['data_Child_Of_Favorited_Item_From_Blacklist']=getChildren_favoritedMediaItems('From_Blacklist',user_info,var_dict,the_dict)
                #Define reasoning for lookup
                var_dict['APIDebugMsg_Child_Of_Favorited_Item_From_Whitelist']='Child_Of_Favorited_Item_From_Whitelist'
                #data_Favorited_From_Whitelist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Whitelist,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Favorited_From_Whitelist_Child,media_played_days,media_created_days)
                var_dict['data_Child_Of_Favorited_Item_From_Whitelist']=getChildren_favoritedMediaItems('From_Whitelist',user_info,var_dict,the_dict)

                #Define reasoning for lookup
                var_dict['APIDebugMsg_Child_Of_Blacktagged_From_Blacklist']='Child_Of_Blacktagged_Item_From_Blacklist'
                #data_Blacktagged_From_Blacklist_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_Blacklist,blacktags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Blacktag_From_Blacklist_Child,media_played_days,media_created_days)
                var_dict['data_Child_Of_Blacktagged_From_Blacklist']=getChildren_taggedMediaItems('Blacktagged_From_Blacklist',user_info,var_dict,the_dict)
                #Define reasoning for lookup
                var_dict['APIDebugMsg_Child_Of_Blacktagged_From_Whitelist']='Child_Of_Blacktagged_Item_From_Whitelist'
                #data_Blacktagged_From_Whitelist_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_Whitelist,blacktags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Blacktag_From_Whitelist_Child,media_played_days,media_created_days)
                var_dict['data_Child_Of_Blacktagged_From_Whitelist_Children']=getChildren_taggedMediaItems('Blacktagged_From_Whitelist',user_info,var_dict,the_dict)
                #Define reasoning for lookup
                var_dict['APIDebugMsg_Child_Of_Whitetagged_From_Blacklist']='Child_Of_Whitetagged_Item_From_Blacklist'
                #data_Whitetagged_From_Blacklist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Blacklist,whitetags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Whitetag_From_Blacklist_Child,media_played_days,media_created_days)
                var_dict['data_Child_Of_Whitetagged_From_Blacklist_Children']=getChildren_taggedMediaItems('Whitetagged_From_Blacklist',user_info,var_dict,the_dict)
                #Define reasoning for lookup
                var_dict['APIDebugMsg_Child_Of_Whitetagged_From_Whitelist']='Child_Of_Whitetagged_Item_From_Whitelist'
                #data_Whitetagged_From_Whitelist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Whitelist,whitetags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Whitetag_From_Whitelist_Child,media_played_days,media_created_days)
                var_dict['data_Child_Of_Whitetagged_From_Whitelist_Children']=getChildren_taggedMediaItems('Whitetagged_From_Whitelist',user_info,var_dict,the_dict)

                #Combine dictionaries into list of dictionaries
                #Order here is important
                var_dict['data_lists']=[var_dict['data_Favorited_From_Whitelist'], #0
                                        var_dict['data_Child_Of_Favorited_Item_From_Whitelist'], #1
                                        var_dict['data_Whitetagged_From_Whitelist'], #2
                                        var_dict['data_Child_Of_Whitetagged_From_Whitelist_Children'], #3
                                        var_dict['data_Blacktagged_From_Whitelist'], #4
                                        var_dict['data_Child_Of_Blacktagged_From_Whitelist_Children'], #5
                                        var_dict['data_Favorited_From_Blacklist'], #6APIDebugMsg_Whitetag_From_Blacklist_Child
                                        var_dict['data_Child_Of_Favorited_Item_From_Blacklist'], #7
                                        var_dict['data_Whitetagged_From_Blacklist'], #8
                                        var_dict['data_Child_Of_Whitetagged_From_Blacklist_Children'], #9
                                        var_dict['data_Blacktagged_From_Blacklist'], #10
                                        var_dict['data_Child_Of_Blacktagged_From_Blacklist'], #11
                                        var_dict['data_Blacklist'], #12
                                        var_dict['data_Whitelist']] #13

                #Order here is important (must match above)
                var_dict['data_from_favorited_queries']=[0,1,6,7]
                var_dict['data_from_whitetagged_queries']=[2,3,8,9]
                var_dict['data_from_blacktagged_queries']=[4,5,10,11]
                var_dict['data_from_whitelisted_queries']=[0,1,2,3,4,5,13]
                var_dict['data_from_blacklisted_queries']=[6,7,8,9,10,11,12]

                #Determine if we are done processing queries or if there are still queries to be sent
                var_dict['QueryItemsRemaining_All']=(var_dict['QueriesRemaining_Favorited_From_Blacklist'] |
                                                     var_dict['QueriesRemaining_Favorited_From_Whitelist'] |
                                                     var_dict['QueriesRemaining_Whitetagged_From_Blacklist'] |
                                                     var_dict['QueriesRemaining_Whitetagged_From_Whitelist'] |
                                                     var_dict['QueriesRemaining_Blacktagged_From_Blacklist'] |
                                                     var_dict['QueriesRemaining_Blacktagged_From_Whitelist'] |
                                                     var_dict['QueriesRemaining_Blacklist'] |
                                                     var_dict['QueriesRemaining_Whitelist'])

                #track where we are in the var_dict['data_lists']
                var_dict['data_list_pos']=0

                #Determine if media item is shown as DELETE or KEEP
                #Loop thru each dictionary in var_dict['data_lists'][#]
                for var_dict['data_dict'] in var_dict['data_lists']:

                    #Loop thru each data_dict['Items'] item
                    for item in var_dict['data_dict']['Items']:

                        #Check if item was already processed for this user
                        if (not (item['Id'] in var_dict['user_processed_item_Ids'])):

                            if (the_dict['DEBUG']):
                                #Double newline for DEBUG log formatting
                                appendTo_DEBUG_log("\n\nInspecting Media Item: " + str(item['Id']),2,the_dict)

                            var_dict['media_found']=True

                            var_dict['itemIsMonitored']=False
                            if (item['Type'] == var_dict['media_type_title']):
                                for var_dict['mediasource'] in item['MediaSources']:
                                    var_dict['itemIsMonitored']=get_isItemMonitored(var_dict['mediasource'],the_dict)

                            #determine how to show media item
                            if (var_dict['itemIsMonitored']):

                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nProcessing " + var_dict['media_type_title'] + " Item: " + str(item['Id']),2,the_dict)

                                #Fill in the blanks
                                if (var_dict['media_type_lower'] == 'movie'):
                                    item=prepare_MOVIEoutput(the_dict,item,user_info['user_id'],var_dict['media_set_missing_last_played_date'])
                                elif (var_dict['media_type_lower'] == 'episode'):
                                    item=prepare_EPISODEoutput(the_dict,item,user_info['user_id'],var_dict['media_set_missing_last_played_date'])
                                elif (var_dict['media_type_lower'] == 'audio'):
                                    item=prepare_AUDIOoutput(the_dict,item,user_info['user_id'],var_dict['media_set_missing_last_played_date'],var_dict['media_type_lower'])
                                elif (var_dict['media_type_lower'] == 'audiobook'):
                                    item=prepare_AUDIOBOOKoutput(the_dict,item,user_info['user_id'],var_dict['media_set_missing_last_played_date'],var_dict['media_type_lower'])

                                var_dict['isfavorited_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
                                var_dict['iswhitetagged_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
                                var_dict['isblacktagged_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
                                var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
                                var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}

##########################################################################################################################################

                                #Determine if item meets played days, created days, played counts, and played-created counts
                                var_dict.update(get_playedCreatedDays_playedCreatedCounts(the_dict,item,var_dict['media_played_days'],var_dict['media_created_days'],var_dict['cut_off_date_played_media'],var_dict['cut_off_date_created_media'],
                                                                            var_dict['media_played_count_comparison'],var_dict['media_played_count'],var_dict['media_created_played_count_comparison'],var_dict['media_created_played_count']))

##########################################################################################################################################

                                if (var_dict['item_matches_created_days_filter'] and var_dict['item_matches_created_played_count_filter']):
                                    if (not (item['Id'] in var_dict['deleteItemsIdTracker_createdMedia'])):
                                        var_dict['deleteItemsIdTracker_createdMedia'].append(item['Id'])
                                        var_dict['deleteItems_createdMedia'].append(item)

##########################################################################################################################################

                                var_dict['item_isFavorited']=False
                                #Get if media item is set as favorite
                                if (var_dict['data_list_pos'] in var_dict['data_from_favorited_queries']):
                                    var_dict['item_isFavorited']=True
                                else:
                                    if (var_dict['media_type_lower'] == 'movie'):
                                        var_dict['item_isFavorited']=get_isMOVIE_Fav(the_dict,item,user_info)
                                    elif (var_dict['media_type_lower'] == 'episode'):
                                        var_dict['item_isFavorited']=get_isEPISODE_Fav(the_dict,item,user_info)
                                    elif (var_dict['media_type_lower'] == 'audio'):
                                        var_dict['item_isFavorited']=get_isAUDIO_Fav(the_dict,item,user_info,'Audio')
                                    elif (var_dict['media_type_lower'] == 'audiobook'):
                                        var_dict['item_isFavorited']=get_isAUDIOBOOK_Fav(the_dict,item,user_info,'AudioBook')

                                #Get if media item is set as an advanced favorite
                                var_dict['item_isFavorited_Advanced']=False
                                #if (var_dict['favorited_behavior_media']['action_control'] and (advFav0_media or advFav1_media or advFav2_media or advFav3_media or advFav4_media or advFav5_media)):
                                if (var_dict['favorited_behavior_media']['action_control'] and (any(var_dict['advFav_media']) > 0)):
                                    if (var_dict['media_type_lower'] == 'movie'):
                                        var_dict['item_isFavorited_Advanced']=get_isMOVIE_AdvancedFav(the_dict,item,user_info,var_dict['advFav_media'])
                                    elif (var_dict['media_type_lower'] == 'episode'):
                                        var_dict['item_isFavorited_Advanced']=get_isEPISODE_AdvancedFav(the_dict,item,user_info,var_dict['advFav_media'])
                                    elif (var_dict['media_type_lower'] == 'audio'):
                                        var_dict['item_isFavorited_Advanced']=get_isAUDIO_AdvancedFav(the_dict,item,user_info,'Audio',var_dict['advFav_media'])
                                    elif (var_dict['media_type_lower'] == 'audiobook'):
                                        var_dict['item_isFavorited_Advanced']=get_isAUDIOBOOK_AdvancedFav(the_dict,item,user_info,'AudioBook',var_dict['advFav_media'])

                                #Determine what will show as the favorite status for this user and media item
                                var_dict['isFavorited_Display']=(var_dict['item_isFavorited'] or var_dict['item_isFavorited_Advanced'])

                                #favorite behavior enabled
                                var_dict.update(parse_actionedConfigurationBehavior('favorited',item,user_info,var_dict,the_dict))
##########################################################################################################################################

                                var_dict['item_isWhitetagged']=False
                                if (var_dict['data_list_pos'] in var_dict['data_from_whitetagged_queries']):
                                    var_dict['item_isWhitetagged']=True
                                elif (not (var_dict['whitetags'] == '')):
                                    if (var_dict['media_type_lower'] == 'movie'):
                                        var_dict['item_isWhitetagged']=get_isMOVIE_Tagged(the_dict,item,user_info,var_dict['whitetags'])
                                    elif (var_dict['media_type_lower'] == 'episode'):
                                        var_dict['item_isWhitetagged']=get_isEPISODE_Tagged(the_dict,item,user_info,var_dict['whitetags'])
                                    elif (var_dict['media_type_lower'] == 'audio'):
                                        var_dict['item_isWhitetagged']=get_isAUDIO_Tagged(the_dict,item,user_info,var_dict['whitetags'])
                                    elif (var_dict['media_type_lower'] == 'audiobook'):
                                        var_dict['item_isWhitetagged']=get_isAUDIOBOOK_Tagged(the_dict,item,user_info,var_dict['whitetags'])

                                var_dict['isWhitetagged_Display']=var_dict['item_isWhitetagged']

                                #whitetag behavior enabled
                                var_dict.update(parse_actionedConfigurationBehavior('whitetagged',item,user_info,var_dict,the_dict))

##########################################################################################################################################

                                var_dict['item_isBlacktagged']=False
                                if (var_dict['data_list_pos'] in var_dict['data_from_blacktagged_queries']):
                                    var_dict['item_isBlacktagged']=True
                                elif (not (var_dict['blacktags'] == '')):
                                    if (var_dict['media_type_lower'] == 'movie'):
                                        var_dict['item_isBlacktagged']=get_isMOVIE_Tagged(the_dict,item,user_info,var_dict['blacktags'])
                                    elif (var_dict['media_type_lower'] == 'episode'):
                                        var_dict['item_isBlacktagged']=get_isEPISODE_Tagged(the_dict,item,user_info,var_dict['blacktags'])
                                    elif (var_dict['media_type_lower'] == 'audio'):
                                        var_dict['item_isBlacktagged']=get_isAUDIO_Tagged(the_dict,item,user_info,var_dict['blacktags'])
                                    elif (var_dict['media_type_lower'] == 'audiobook'):
                                        var_dict['item_isBlacktagged']=get_isAUDIOBOOK_Tagged(the_dict,item,user_info,var_dict['blacktags'])

                                var_dict['isBlacktagged_Display']=var_dict['item_isBlacktagged']

                                #blacktag behavior enabled
                                var_dict.update(parse_actionedConfigurationBehavior('blacktagged',item,user_info,var_dict,the_dict))

##########################################################################################################################################

                                var_dict['isWhitelisted_Display']=False
                                #check if we are at a whitelist queried var_dict['data_list_pos']
                                if (var_dict['data_list_pos'] in var_dict['data_from_whitelisted_queries']):
                                    var_dict['item_isWhitelisted']=get_isItemWhitelisted_Blacklisted('whitelist','whitelist',item,user_info,var_dict,the_dict)
                                    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryId']=var_dict['this_whitelist_lib']['lib_id']
                                    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryPath']=var_dict['this_whitelist_lib']['path']
                                    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryNetPath']=var_dict['this_whitelist_lib']['network_path']
                                else: #check if we are at a blacklist queried var_dict['data_list_pos']
                                    var_dict['item_isWhitelisted']=get_isItemWhitelisted_Blacklisted('blacklist','whitelist',item,user_info,var_dict,the_dict)
                                    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryId']=var_dict['this_blacklist_lib']['lib_id']
                                    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryPath']=var_dict['this_blacklist_lib']['path']
                                    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryNetPath']=var_dict['this_blacklist_lib']['network_path']

                                var_dict['isWhitelisted_Display']=var_dict['item_isWhitelisted']

                                #whitelist behavior enabled
                                var_dict.update(parse_actionedConfigurationBehavior('whitelisted',item,user_info,var_dict,the_dict))

##########################################################################################################################################

                                var_dict['isBlacklisted_Display']=False
                                #check if we are at a blacklist queried var_dict['data_list_pos']
                                if (var_dict['data_list_pos'] in var_dict['data_from_blacklisted_queries']):
                                    var_dict['item_isBlacklisted']=get_isItemWhitelisted_Blacklisted('blacklist','blacklist',item,user_info,var_dict,the_dict)
                                    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryId']=var_dict['this_blacklist_lib']['lib_id']
                                    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryPath']=var_dict['this_blacklist_lib']['path']
                                    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryNetPath']=var_dict['this_blacklist_lib']['network_path']
                                else: #check if we are at a whitelist queried var_dict['data_list_pos']
                                    var_dict['item_isBlacklisted']=get_isItemWhitelisted_Blacklisted('whitelist','blacklist',item,user_info,var_dict,the_dict)
                                    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryId']=var_dict['this_whitelist_lib']['lib_id']
                                    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryPath']=var_dict['this_whitelist_lib']['path']
                                    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryNetPath']=var_dict['this_whitelist_lib']['network_path']

                                var_dict['isBlacklisted_Display']=var_dict['item_isBlacklisted']

                                #blacklist behavior enabled
                                var_dict.update(parse_actionedConfigurationBehavior('blacklisted',item,user_info,var_dict,the_dict))

##########################################################################################################################################

                                #Decide how to handle the fav_local, fav_adv, whitetag, blacktag, whitelist, and blacklist flags
                                var_dict['showItemAsDeleted']=get_singleUserDeleteStatus(var_dict,the_dict)

##########################################################################################################################################

                                #Only applies to episodes; prep for minimum number and minimum played number of episodes
                                if (var_dict['minimum_number_episodes'] or var_dict['minimum_number_played_episodes']):
                                    #Get seriesId and compare it to what the episode thinks its seriesId is
                                    series_info = get_SERIES_itemInfo(item,user_info,the_dict)
                                    if ((not ('SeriesId' in item)) or (not (item['SeriesId'] == series_info['Id']))):
                                        if (series_info):
                                            item['SeriesId']=series_info['Id']

                                    if not (item['SeriesId'] in var_dict['mediaCounts_byUserId'][user_info['user_id']]):
                                        RecursiveItemCount=int(series_info['RecursiveItemCount'])
                                        UnplayedItemCount=int(series_info['UserData']['UnplayedItemCount'])
                                        PlayedEpisodeCount=RecursiveItemCount - UnplayedItemCount

                                    if not ('TotalEpisodeCount' in var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']]):
                                        var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']]['TotalEpisodeCount']=RecursiveItemCount
                                    if not ('UnplayedEpisodeCount' in var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']]):
                                        var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']]['UnplayedEpisodeCount']=UnplayedItemCount
                                    if not ('PlayedEpisodeCount' in var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']]):
                                        var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']]['PlayedEpisodeCount']=PlayedEpisodeCount

##########################################################################################################################################

                                #Build output state dictionary
                                '''
                                output_state_dict={'isFavorited_Display':var_dict['isFavorited_Display'],
                                                    'isWhitetagged_Display':var_dict['isWhitetagged_Display'],
                                                    'isBlacktagged_Display':var_dict['isBlacktagged_Display'],
                                                    'isWhitelisted_Display':var_dict['isWhitelisted_Display'],
                                                    'isBlacklisted_Display':var_dict['isBlacklisted_Display'],
                                                    'showItemAsDeleted':var_dict['showItemAsDeleted'],
                                                    'print_media_delete_info':var_dict['print_media_delete_info'],
                                                    'print_media_keep_info':var_dict['print_media_keep_info'],
                                                    'media_delete_info_format':var_dict['media_delete_info_format'],
                                                    'media_keep_info_format':var_dict['media_keep_info_format']}
                                '''

                                #Build and display media item output details for currently processing user
                                build_print_media_item_details(item,var_dict,the_dict)
                                #if (var_dict['media_type_lower'] == 'episode'):
                                    #build_print_media_item_details(the_dict,item,var_dict['media_type_lower'],output_state_dict,get_days_since_played(item['UserData']['LastPlayedDate'],the_dict),get_days_since_created(item['DateCreated'],the_dict),get_season_episode(item['ParentIndexNumber'],item['IndexNumber'],the_dict))
                                #else:
                                    #build_print_media_item_details(the_dict,item,var_dict['media_type_lower'],output_state_dict,get_days_since_played(item['UserData']['LastPlayedDate'],the_dict),get_days_since_created(item['DateCreated'],the_dict))

##########################################################################################################################################

                            #Add media item Id to tracking list so it is not processed more than once
                            var_dict['user_processed_item_Ids'].add(item['Id'])

                    var_dict['data_list_pos'] += 1

            #currentSubPosition += 1

############# End Media #############

    #if (the_dict['DEBUG']):
        #print_common_delete_keep_info=True
        #appendTo_DEBUG_log("\n",1,the_dict)
    #print_byType(the_dict['console_separator_'],print_common_delete_keep_info,the_dict,the_dict['user_header_format'])
    print_byType(the_dict['console_separator_'],the_dict['advanced_settings']['console_controls']['headers']['user']['show'],the_dict,the_dict['advanced_settings']['console_controls']['headers']['user']['formatting'])

    the_dict[var_dict['media_dict_str']][user_info['user_id']]['deleteItems_Media']=var_dict['deleteItems_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['deleteItemsIdTracker_Media']=var_dict['deleteItemsIdTracker_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['deleteItems_createdMedia']=var_dict['deleteItems_createdMedia']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['deleteItemsIdTracker_createdMedia']=var_dict['deleteItemsIdTracker_createdMedia']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['isblacklisted_and_played_byUserId_Media']=var_dict['isblacklisted_and_played_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['isblacklisted_extraInfo_byUserId_Media']=var_dict['isblacklisted_extraInfo_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['iswhitelisted_and_played_byUserId_Media']=var_dict['iswhitelisted_and_played_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['iswhitelisted_extraInfo_byUserId_Media']=var_dict['iswhitelisted_extraInfo_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['isblacktagged_and_played_byUserId_Media']=var_dict['isblacktagged_and_played_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['isblacktagged_extraInfo_byUserId_Media']=var_dict['isblacktagged_extraInfo_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['iswhitetagged_and_played_byUserId_Media']=var_dict['iswhitetagged_and_played_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['iswhitetagged_extraInfo_byUserId_Media']=var_dict['iswhitetagged_extraInfo_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['isfavorited_and_played_byUserId_Media']=var_dict['isfavorited_and_played_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['isfavorited_extraInfo_byUserId_Media']=var_dict['isfavorited_extraInfo_byUserId_Media']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['mediaCounts_byUserId']=var_dict['mediaCounts_byUserId']

    #media_returns['media_dict']=media_dict
    media_returns['media_dict']=the_dict[var_dict['media_dict_str']]
    media_returns['media_found']=var_dict['media_found']

    return media_returns


'''
def getMedia(the_dict):

    movie_dict={}
    episode_dict={}
    audio_dict={}
    audiobook_dict={}

    #Get items that could be ready for deletion
    for user_key in the_dict['user_keys_json']:
        movie_returns=[]
        episode_returns=[]
        audio_returns=[]
        audiobook_returns=[]
        movie_dict[user_key]={}
        episode_dict[user_key]={}
        audio_dict[user_key]={}
        audiobook_dict[user_key]={}

        print_user_header(user_key,the_dict)

        #query the server for movie media items
        #movie_dict,movie_found=get_mediaItems('movie',the_dict,movie_dict,user_key)
        movie_returns=get_mediaItems('movie',the_dict,movie_dict,user_key,movie_returns)
        #query the server for episode media items
        #episode_dict,episode_found=get_mediaItems('episode',the_dict,episode_dict,user_key)
        episode_returns=get_mediaItems('episode',the_dict,episode_dict,user_key,episode_returns)
        #query the server for audio media items
        #audio_dict,audio_found=get_mediaItems('audio',the_dict,audio_dict,user_key)
        audio_returns=get_mediaItems('audio',the_dict,audio_dict,user_key,audio_returns)
        #query the server for audiobook media items
         #audioBook media type only applies to jellyfin
         #Jellyfin sets audiobooks to a media type of audioBook
         #Emby sets audiobooks to a media type of audio (see audio section)
        #audiobook_dict,audiobook_found=get_mediaItems('audiobook',the_dict,audiobook_dict,user_key)
        audiobook_returns=get_mediaItems('audiobook',the_dict,audiobook_dict,user_key,audiobook_returns)
 
        movie_dict.update(movie_returns[0])
        movie_found=movie_returns[1]
        episode_dict.update(episode_returns[0])
        episode_found=episode_returns[1]
        audio_dict.update(audio_returns[0])
        audio_found=audio_returns[1]
        audiobook_dict.update(audiobook_returns[0])
        audiobook_found=audiobook_returns[1]
 
        if (isEmbyServer(the_dict['server_brand'])):
            audiobook_found=False

        the_dict['currentUserPosition']+=1

        media_found=(movie_found or episode_found or audio_found or audiobook_found)

        if not (the_dict['all_media_disabled']):
            if not (media_found):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n",1,the_dict)
                print_byType('[NO PLAYED, WHITELISTED, OR TAGGED MEDIA ITEMS]\n',the_dict['print_script_warning'],the_dict)

    return movie_dict,episode_dict,audio_dict,audiobook_dict
'''


def init_getMedia(the_dict):

    #movie_dict={}
    #episode_dict={}
    #audio_dict={}
    #audiobook_dict={}

    #movie_dict['media_type']='movie'
    #episode_dict['media_type']='episode'
    #audio_dict['media_type']='audio'
    #audiobook_dict['media_type']='audiobook'

    the_dict['movie_dict']={}
    the_dict['movie_dict']['media_type']='movie'
    the_dict['episode_dict']={}
    the_dict['episode_dict']['media_type']='episode'
    the_dict['audio_dict']={}
    the_dict['audio_dict']['media_type']='audio'
    the_dict['audiobook_dict']={}
    the_dict['audiobook_dict']['media_type']='audiobook'

    #Determine played and created date for each media type; UTC time used for media items; needed for get_mediaItems() and run_postProcessing()
    the_dict['cut_off_date_played_media']={}
    the_dict['cut_off_date_created_media']={}
    the_dict['cut_off_date_played_media']['movie']=the_dict['date_time_now_tz_utc'] - timedelta(days=the_dict['basic_settings']['filter_statements']['movie']['played']['condition_days'])
    the_dict['cut_off_date_created_media']['movie']=the_dict['date_time_now_tz_utc'] - timedelta(days=the_dict['basic_settings']['filter_statements']['movie']['created']['condition_days'])
    the_dict['cut_off_date_played_media']['episode']=the_dict['date_time_now_tz_utc'] - timedelta(days=the_dict['basic_settings']['filter_statements']['episode']['played']['condition_days'])
    the_dict['cut_off_date_created_media']['episode']=the_dict['date_time_now_tz_utc'] - timedelta(days=the_dict['basic_settings']['filter_statements']['episode']['created']['condition_days'])
    the_dict['cut_off_date_played_media']['audio']=the_dict['date_time_now_tz_utc'] - timedelta(days=the_dict['basic_settings']['filter_statements']['audio']['played']['condition_days'])
    the_dict['cut_off_date_created_media']['audio']=the_dict['date_time_now_tz_utc'] - timedelta(days=the_dict['basic_settings']['filter_statements']['audio']['created']['condition_days'])
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        the_dict['cut_off_date_played_media']['audiobook']=the_dict['date_time_now_tz_utc'] - timedelta(days=the_dict['basic_settings']['filter_statements']['audiobook']['played']['condition_days'])
        the_dict['cut_off_date_created_media']['audiobook']=the_dict['date_time_now_tz_utc'] - timedelta(days=the_dict['basic_settings']['filter_statements']['audiobook']['created']['condition_days'])
    else:
        the_dict['cut_off_date_played_media']['audiobook']=the_dict['date_time_now_tz_utc'] - timedelta(days=-1)
        the_dict['cut_off_date_created_media']['audiobook']=the_dict['date_time_now_tz_utc'] - timedelta(days=-1)


    #the_dict['currentUserPosition']=the_dict['admin_settings']['users'].index(user_info)
    the_dict['currentUserPosition']=0

    #Get items that could be ready for deletion
    #for user_key in the_dict['user_keys_json']:
    for user_info in the_dict['admin_settings']['users']:
        the_dict['movie_dict'][user_info['user_id']]={}
        the_dict['episode_dict'][user_info['user_id']]={}
        the_dict['audio_dict'][user_info['user_id']]={}
        the_dict['audiobook_dict'][user_info['user_id']]={}

        print_user_header(user_info,the_dict)

        #get values for media delete/keep items
        movie_delete=the_dict['advanced_settings']['console_controls']['movie']['delete']['show']
        movie_keep=the_dict['advanced_settings']['console_controls']['movie']['keep']['show']
        episode_delete=the_dict['advanced_settings']['console_controls']['episode']['delete']['show']
        episode_keep=the_dict['advanced_settings']['console_controls']['episode']['keep']['show']
        audio_delete=the_dict['advanced_settings']['console_controls']['audio']['delete']['show']
        audio_keep=the_dict['advanced_settings']['console_controls']['audio']['keep']['show']
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            audiobook_delete=the_dict['advanced_settings']['console_controls']['audiobook']['delete']['show']
            audiobook_keep=the_dict['advanced_settings']['console_controls']['audiobook']['keep']['show']

        #when debug is disabled AND no media delete/keep items are being output to the console; allow multiprocessing
        if (
           (not (the_dict['DEBUG'])) and
           ((not (movie_delete or movie_keep)) and
           (not (episode_delete or episode_keep)) and
           (not (audio_delete or audio_keep)) and
           ((isEmbyServer(the_dict['admin_settings']['server']['brand'])) or
           (isJellyfinServer(the_dict['admin_settings']['server']['brand']) and
           (not (audiobook_delete or audiobook_keep)))))
           ):

            #print('Start Get Media: ' + datetime.now().strftime('%Y%m%d%H%M%S'))

            #create dictionary for media that can possibly be deleted
            movie_returns=multiprocessing.Manager().dict()
            episode_returns=multiprocessing.Manager().dict()
            audio_returns=multiprocessing.Manager().dict()
            if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
                audiobook_returns=multiprocessing.Manager().dict()

            #prepare for post processing; return dictionary of lists of media items to be deleted
            #setup for multiprocessing of the post processing of each media type
            mpp_movieGetMedia=multiprocessing.Process(target=get_mediaItems,args=(the_dict,the_dict['movie_dict']['media_type'],user_info,movie_returns))
            mpp_episodeGetMedia=multiprocessing.Process(target=get_mediaItems,args=(the_dict,the_dict['episode_dict']['media_type'],user_info,episode_returns))
            mpp_audioGetMedia=multiprocessing.Process(target=get_mediaItems,args=(the_dict,the_dict['audio_dict']['media_type'],user_info,audio_returns))
            if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
                mpp_audiobookGetMedia=multiprocessing.Process(target=get_mediaItems,args=(the_dict,the_dict['audibook_dict']['media_type'],user_info,audiobook_returns))

            #start all multi processes
            #order intentially: Audio, Episodes, Movies, Audiobooks
            if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
                mpp_audioGetMedia.start(),mpp_episodeGetMedia.start(),mpp_movieGetMedia.start(),mpp_audiobookGetMedia.start()
                mpp_audioGetMedia.join(), mpp_episodeGetMedia.join(), mpp_movieGetMedia.join(), mpp_audiobookGetMedia.join()
                mpp_audioGetMedia.close(),mpp_episodeGetMedia.close(),mpp_movieGetMedia.close(),mpp_audiobookGetMedia.close()
            else:
                mpp_audioGetMedia.start(),mpp_episodeGetMedia.start(),mpp_movieGetMedia.start()
                mpp_audioGetMedia.join(), mpp_episodeGetMedia.join(), mpp_movieGetMedia.join()
                mpp_audioGetMedia.close(),mpp_episodeGetMedia.close(),mpp_movieGetMedia.close()

            #print('Stop Get Media: ' + datetime.now().strftime('%Y%m%d%H%M%S'))
        else: ##when debug is enabled or any media delete/keep items are being output to the console; do not allow multiprocessing
            movie_returns={}
            episode_returns={}
            audio_returns={}
            if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
                audiobook_returns={}

            #query the server for movie media items
            movie_returns=get_mediaItems(the_dict,the_dict['movie_dict']['media_type'],user_info,movie_returns)
            #query the server for episode media items
            episode_returns=get_mediaItems(the_dict,the_dict['episode_dict']['media_type'],user_info,episode_returns)
            #query the server for audio media items
            audio_returns=get_mediaItems(the_dict,the_dict['audio_dict']['media_type'],user_info,audio_returns)
            if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
                #query the server for audiobook media items
                #audioBook media type only applies to jellyfin
                #Jellyfin sets audiobooks to a media type of audioBook
                #Emby sets audiobooks to a media type of audio (Emby users, see audio section)
                audiobook_returns=get_mediaItems(the_dict,the_dict['audiobook_dict']['media_type'],user_info,audiobook_returns)

        #if (movie_returns):
        the_dict['movie_dict'].update(movie_returns['media_dict'])
        movie_found=movie_returns['media_found']
        #if (episode_returns):
        the_dict['episode_dict'].update(episode_returns['media_dict'])
        episode_found=episode_returns['media_found']
        #if (audio_returns):
        the_dict['audio_dict'].update(audio_returns['media_dict'])
        audio_found=audio_returns['media_found']
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            #if (audiobook_returns):
            the_dict['audiobook_dict'].update(audiobook_returns['media_dict'])
            audiobook_found=audiobook_returns['media_found']
        else:
            the_dict['audiobook_dict']={}
            audiobook_found=False

        the_dict['currentUserPosition']+=1

        media_found=(movie_found or episode_found or audio_found or audiobook_found)

        if not (the_dict['all_media_disabled']):
            if not (media_found):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n",1,the_dict)
                print_byType('[NO PLAYED, WHITELISTED, OR TAGGED MEDIA ITEMS]\n',the_dict['advanced_settings']['console_controls']['warnings']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])

    #return movie_dict,episode_dict,audio_dict,audiobook_dict
    return the_dict