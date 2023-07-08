#!/usr/bin/env python3
import multiprocessing
import urllib.parse as urlparse
from datetime import timedelta,datetime
from collections import defaultdict
from mumc_modules.mumc_url import api_query_handler
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType
from mumc_modules.mumc_favorited import getChildren_favoritedMediaItems,get_isMOVIE_Fav,get_isMOVIE_AdvancedFav,get_isEPISODE_Fav,get_isEPISODE_AdvancedFav,get_isAUDIO_Fav,get_isAUDIO_AdvancedFav,get_isAUDIOBOOK_Fav,get_isAUDIOBOOK_AdvancedFav
from mumc_modules.mumc_tagged import getChildren_taggedMediaItems,get_isMOVIE_Tagged,get_isEPISODE_Tagged,get_isAUDIO_Tagged,get_isAUDIOBOOK_Tagged,list_to_urlparsed_string
from mumc_modules.mumc_blacklist import get_isItemBlacklisted
from mumc_modules.mumc_whitelist import get_isItemWhitelisted
from mumc_modules.mumc_prepare_item import prepare_MOVIEoutput,prepare_EPISODEoutput,prepare_AUDIOoutput,prepare_AUDIOBOOKoutput
from mumc_modules.mumc_days_since import get_days_since_played,get_days_since_created
from mumc_modules.mumc_console_info import build_print_media_item_details,print_user_header
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_played_created import get_isPlayedCreated_FilterValue,get_playedCreatedDays_playedCreatedCounts
from mumc_modules.mumc_item_info import get_SERIES_itemInfo
from mumc_modules.mumc_season_episode import get_season_episode


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
def parse_actionedConfigurationBehavior(the_dict,item,isactioned_extra_byUserId,user_key,theActionType,isActioned_and_played_byUserId,action_behavior,item_isActioned,item_matches_played_days_filter,item_matches_played_count_filter,item_matches_created_days_filter,item_matches_created_played_count_filter,itemIsPlayed,itemPlayedCount):

    isactioned_extra_byUserId['ActionBehavior']=action_behavior[3]
    isactioned_extra_byUserId['ActionType']=theActionType
    isactioned_extra_byUserId['MonitoredUsersAction']=action_behavior[1].casefold()
    isactioned_extra_byUserId['MonitoredUsersMeetPlayedFilter']=action_behavior[2].casefold()
    isactioned_extra_byUserId['ConfiguredBehavior']=action_behavior[0].casefold()

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

    return isActioned_and_played_byUserId,isactioned_extra_byUserId


#decide if this item is ok to be deleted; still has to meet other criteria
def get_singleUserDeleteStatus(the_dict,item_matches_played_count_filter,item_matches_played_days_filter,item_matches_created_played_count_filter,item_matches_created_days_filter,
                               item_isFavorited,item_isFavorited_Advanced,item_isWhiteTagged,item_isBlackTagged,item_isWhiteListed,item_isBlackListed):

    #when item is favorited do not allow it to be deleted
    if (item_isFavorited or item_isFavorited_Advanced):
        okToDelete=False
    #when item is whitetagged do not allow it to be deleted
    elif (item_isWhiteTagged):
        okToDelete=False
    #when item is blacktagged allow it to be deleted
    elif (item_isBlackTagged and ((item_matches_played_count_filter and item_matches_played_days_filter) or (item_matches_created_played_count_filter and item_matches_created_days_filter))):
        okToDelete=True
    #when item is whitelisted do not allow it to be deleted
    elif (item_isWhiteListed):
        okToDelete=False
    #when item is blacklisted allow it to be deleted
    elif (item_isBlackListed and ((item_matches_played_count_filter and item_matches_played_days_filter) or (item_matches_created_played_count_filter and item_matches_created_days_filter))):
        okToDelete=True
    else: #do not allow item to be deleted
        okToDelete=False

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nIs Media Item OK To Delete: " + str(okToDelete),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item Favorited For This User: " + str(item_isFavorited),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item An Advanced Favorite: " + str(item_isFavorited_Advanced),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item WhiteTagged: " + str(item_isWhiteTagged),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item BlackTagged: " + str(item_isBlackTagged),2,the_dict)
        appendTo_DEBUG_log("\nDoes Media Item Match The Play Count Filter: " + str(item_matches_played_count_filter),2,the_dict)
        appendTo_DEBUG_log("\nDoes Media Item Meet Number Of Days Since Played: " + str(item_matches_played_days_filter),2,the_dict)
        appendTo_DEBUG_log("\nDoes Media Item Match The Created Played Count Filter: " + str(item_matches_created_played_count_filter),2,the_dict)
        appendTo_DEBUG_log("\nDoes Media Item Meet Number Of Days Since Created-Played: " + str(item_matches_created_days_filter),2,the_dict)
        appendTo_DEBUG_log("\nIs Media Item WhiteListed For This User: " + str(item_isWhiteListed),2,the_dict)

    return okToDelete


# get played, favorited, and tagged media items
# save media items ready to be deleted
# remove media items with exceptions (i.e. favorited, whitelisted, whitetagged, etc...)
def get_media_items(mediaType,the_dict,media_dict,user_key,media_returns):

    mediaType_lower=mediaType.casefold()
    mediaType_upper=mediaType.upper()
    mediaType_title=mediaType.title()

    server_url=the_dict['server_url']
    auth_key=the_dict['auth_key']
    whitetags=the_dict['whitetag']
    blacktags=the_dict['blacktag']
    library_matching_behavior=the_dict['library_matching_behavior']

    user_bllib_keys_json=the_dict['user_bllib_keys_json']
    user_bllib_netpath_json=the_dict['user_bllib_netpath_json']
    user_bllib_path_json=the_dict['user_bllib_path_json']
    user_wllib_keys_json=the_dict['user_wllib_keys_json']
    user_wllib_netpath_json=the_dict['user_wllib_netpath_json']
    user_wllib_path_json=the_dict['user_wllib_path_json']

    if (mediaType_lower == 'movie'):
        if (not(mediaType in media_dict)):
            media_dict['mediaType']=mediaType.casefold()
        media_played_days=the_dict['played_filter_movie'][0]
        media_created_days=the_dict['created_filter_movie'][0]
        media_played_count_comparison=the_dict['played_filter_movie'][1]
        media_created_played_count_comparison=the_dict['created_filter_movie'][1]
        media_played_count=the_dict['played_filter_movie'][2]
        media_created_played_count=the_dict['created_filter_movie'][2]
        print_media_delete_info=the_dict['print_movie_delete_info']
        print_media_keep_info=the_dict['print_movie_keep_info']
        media_delete_info_format=the_dict['movie_delete_info_format']
        media_keep_info_format=the_dict['movie_keep_info_format']
        favorited_behavior_media=the_dict['favorited_behavior_movie']
        advFav0_media=the_dict['favorited_advanced_movie_genre']
        advFav1_media=the_dict['favorited_advanced_movie_library_genre']
        advFav2_media=0
        advFav3_media=0
        advFav4_media=0
        advFav5_media=0
        whitetagged_behavior_media=the_dict['whitetagged_behavior_movie']
        whitetags.extend(the_dict['movie_whitetag'])
        blacktagged_behavior_media=the_dict['blacktagged_behavior_movie']
        blacktags.extend(the_dict['movie_blacktag'])
        whitelisted_behavior_media=the_dict['whitelisted_behavior_movie']
        blacklisted_behavior_media=the_dict['blacklisted_behavior_movie']
    elif (mediaType_lower == 'episode'):
        if (not(mediaType in media_dict)):
            media_dict['mediaType']=mediaType.casefold()
        media_played_days=the_dict['played_filter_episode'][0]
        media_created_days=the_dict['created_filter_episode'][0]
        media_played_count_comparison=the_dict['played_filter_episode'][1]
        media_created_played_count_comparison=the_dict['created_filter_episode'][1]
        media_played_count=the_dict['played_filter_episode'][2]
        media_created_played_count=the_dict['created_filter_episode'][2]
        print_media_delete_info=the_dict['print_episode_delete_info']
        print_media_keep_info=the_dict['print_episode_keep_info']
        media_delete_info_format=the_dict['episode_delete_info_format']
        media_keep_info_format=the_dict['episode_keep_info_format']
        favorited_behavior_media=the_dict['favorited_behavior_episode']
        advFav0_media=the_dict['favorited_advanced_episode_genre']
        advFav1_media=the_dict['favorited_advanced_season_genre']
        advFav2_media=the_dict['favorited_advanced_series_genre']
        advFav3_media=the_dict['favorited_advanced_tv_library_genre']
        advFav4_media=the_dict['favorited_advanced_tv_studio_network']
        advFav5_media=the_dict['favorited_advanced_tv_studio_network_genre']
        whitetagged_behavior_media=the_dict['whitetagged_behavior_episode']
        whitetags.extend(the_dict['episode_whitetag'])
        blacktagged_behavior_media=the_dict['blacktagged_behavior_episode']
        blacktags.extend(the_dict['episode_blacktag'])
        whitelisted_behavior_media=the_dict['whitelisted_behavior_episode']
        blacklisted_behavior_media=the_dict['blacklisted_behavior_episode']
    elif (mediaType_lower == 'audio'):
        if (not(mediaType in media_dict)):
            media_dict['mediaType']=mediaType.casefold()
        media_played_days=the_dict['played_filter_audio'][0]
        media_created_days=the_dict['created_filter_audio'][0]
        media_played_count_comparison=the_dict['played_filter_audio'][1]
        media_created_played_count_comparison=the_dict['created_filter_audio'][1]
        media_played_count=the_dict['played_filter_audio'][2]
        media_created_played_count=the_dict['created_filter_audio'][2]
        print_media_delete_info=the_dict['print_audio_delete_info']
        print_media_keep_info=the_dict['print_audio_keep_info']
        media_delete_info_format=the_dict['audio_delete_info_format']
        media_keep_info_format=the_dict['audio_keep_info_format']
        favorited_behavior_media=the_dict['favorited_behavior_audio']
        advFav0_media=the_dict['favorited_advanced_track_genre']
        advFav1_media=the_dict['favorited_advanced_album_genre']
        advFav2_media=the_dict['favorited_advanced_music_library_genre']
        advFav3_media=the_dict['favorited_advanced_track_artist']
        advFav4_media=the_dict['favorited_advanced_album_artist']
        advFav5_media=0
        whitetagged_behavior_media=the_dict['whitetagged_behavior_audio']
        whitetags.extend(the_dict['audio_whitetag'])
        blacktagged_behavior_media=the_dict['blacktagged_behavior_audio']
        blacktags.extend(the_dict['audio_blacktag'])
        whitelisted_behavior_media=the_dict['whitelisted_behavior_audio']
        blacklisted_behavior_media=the_dict['blacklisted_behavior_audio']
    elif (mediaType_lower == 'audiobook'):
        if (not(mediaType in media_dict)):
            media_dict['mediaType']=mediaType.casefold()
        if (isJellyfinServer(the_dict['server_brand'])):
            media_played_days=the_dict['played_filter_audiobook'][0]
            media_created_days=the_dict['created_filter_audiobook'][0]
            media_played_count_comparison=the_dict['played_filter_audiobook'][1]
            media_created_played_count_comparison=the_dict['created_filter_audiobook'][1]
            media_played_count=the_dict['played_filter_audiobook'][2]
            media_created_played_count=the_dict['created_filter_audiobook'][2]
            print_media_delete_info=the_dict['print_audiobook_delete_info']
            print_media_keep_info=the_dict['print_audiobook_keep_info']
            media_delete_info_format=the_dict['audiobook_delete_info_format']
            media_keep_info_format=the_dict['audiobook_keep_info_format']
            favorited_behavior_media=the_dict['favorited_behavior_audiobook']
            advFav0_media=the_dict['favorited_advanced_audiobook_track_genre']
            advFav1_media=the_dict['favorited_advanced_audiobook_genre']
            advFav2_media=the_dict['favorited_advanced_audiobook_library_genre']
            advFav3_media=the_dict['favorited_advanced_audiobook_track_author']
            advFav4_media=the_dict['favorited_advanced_audiobook_author']
            advFav5_media=the_dict['favorited_advanced_audiobook_library_author']
            whitetagged_behavior_media=the_dict['whitetagged_behavior_audiobook']
            whitetags.extend(the_dict['audiobook_whitetag'])
            blacktagged_behavior_media=the_dict['blacktagged_behavior_audiobook']
            blacktags.extend(the_dict['audiobook_blacktag'])
            whitelisted_behavior_media=the_dict['whitelisted_behavior_audiobook']
            blacklisted_behavior_media=the_dict['blacklisted_behavior_audiobook']
        else: #(isEmbyServer(the_dict)):
            media_played_days=-1
            media_created_days=-1
            media_played_count_comparison='=='
            media_created_played_count_comparison='=='
            media_played_count=1
            media_created_played_count=0
            print_media_delete_info=False
            print_media_keep_info=False
            media_delete_info_format=['','','']
            media_keep_info_format=['','','']
            favorited_behavior_media=['keep','any','ignore',0]
            advFav0_media=0
            advFav1_media=0
            advFav2_media=0
            advFav3_media=0
            advFav4_media=0
            advFav5_media=0
            whitetagged_behavior_media=['keep','any','ignore',0]
            whitetags=whitetags
            blacktagged_behavior_media=['keep','any','ignore',0]
            blacktags=blacktags
            whitelisted_behavior_media=['keep','any','ignore',0]
            blacklisted_behavior_media=['keep','any','ignore',0]

    if ((media_played_days >= 0) or (media_created_days >= 0)):
        cut_off_date_played_media=the_dict['date_time_now_tz_utc'] - timedelta(media_played_days)
        cut_off_date_created_media=the_dict['date_time_now_tz_utc'] - timedelta(media_created_days)

        the_dict['cut_off_date_played_media']=cut_off_date_played_media
        the_dict['cut_off_date_created_media']=cut_off_date_created_media

        if (mediaType_lower == 'episode'):
            minimum_number_episodes=the_dict['minimum_number_episodes']
            minimum_number_played_episodes=the_dict['minimum_number_played_episodes']
        else:
            minimum_number_episodes=0
            minimum_number_played_episodes=0

    #dictionary of favortied and played items by userId
    isfavorited_and_played_byUserId_Media={}
    isfavorited_extraInfo_byUserId_Media={}
    #dictionary of whitetagged items by userId
    iswhitetagged_and_played_byUserId_Media={}
    iswhitetagged_extraInfo_byUserId_Media={}
    #dictionary of blacktagged items by userId
    isblacktagged_and_played_byUserId_Media={}
    isblacktagged_extraInfo_byUserId_Media={}
    #dictionary of whitelisted items by userId
    iswhitelisted_and_played_byUserId_Media={}
    iswhitelisted_extraInfo_byUserId_Media={}
    #dictionary of blacklisted items by userId
    isblacklisted_and_played_byUserId_Media={}
    isblacklisted_extraInfo_byUserId_Media={}
    #dictionary of media item counts by userId
    mediaCounts_byUserId={}

    if (the_dict['DEBUG']):
        print_media_delete_info=True
        print_media_keep_info=True

    print_common_delete_keep_info=(print_media_delete_info or print_media_keep_info)
    the_dict['print_common_delete_keep_info']=print_common_delete_keep_info

    #lists of items to be deleted
    deleteItems_Media=[]
    deleteItemsIdTracker_Media=[]
    deleteItems_createdMedia=[]
    deleteItemsIdTracker_createdMedia=[]

    #dictionary of favortied and played items by userId
    isfavorited_and_played_byUserId_Media[user_key]={}
    isfavorited_extraInfo_byUserId_Media[user_key]={}
    #dictionary of whitetagged items by userId
    iswhitetagged_and_played_byUserId_Media[user_key]={}
    iswhitetagged_extraInfo_byUserId_Media[user_key]={}
    #dictionary of blacktagged items by userId
    isblacktagged_and_played_byUserId_Media[user_key]={}
    isblacktagged_extraInfo_byUserId_Media[user_key]={}
    #dictionary of whitelisted items by userId
    iswhitelisted_and_played_byUserId_Media[user_key]={}
    iswhitelisted_extraInfo_byUserId_Media[user_key]={}
    #dictionary of blacklisted items by userId
    isblacklisted_and_played_byUserId_Media[user_key]={}
    isblacklisted_extraInfo_byUserId_Media[user_key]={}
    #dictionary of media item counts by userId
    mediaCounts_byUserId[user_key]=defaultdict(dict)

    currentPosition=the_dict['currentPosition']

    #get library attributes for user in this position
    user_bllib_keys_json_lensplit=user_bllib_keys_json[currentPosition].split(',')
    user_wllib_keys_json_lensplit=user_wllib_keys_json[currentPosition].split(',')
    user_bllib_netpath_json_lensplit=user_bllib_netpath_json[currentPosition].split(',')
    user_wllib_netpath_json_lensplit=user_wllib_netpath_json[currentPosition].split(',')
    user_bllib_path_json_lensplit=user_bllib_path_json[currentPosition].split(',')
    user_wllib_path_json_lensplit=user_wllib_path_json[currentPosition].split(',')

    #get length of library attributes
    len_user_bllib_keys_json_lensplit=len(user_bllib_keys_json_lensplit)
    len_user_wllib_keys_json_lensplit=len(user_wllib_keys_json_lensplit)
    len_user_bllib_netpath_json_lensplit=len(user_bllib_netpath_json_lensplit)
    len_user_wllib_netpath_json_lensplit=len(user_wllib_netpath_json_lensplit)
    len_user_bllib_path_json_lensplit=len(user_bllib_path_json_lensplit)
    len_user_wllib_path_json_lensplit=len(user_wllib_path_json_lensplit)

    #find min length of library attributes
    min_attribute_length=min(len_user_bllib_keys_json_lensplit,len_user_wllib_keys_json_lensplit,
                                len_user_bllib_netpath_json_lensplit,len_user_wllib_netpath_json_lensplit,
                                len_user_bllib_path_json_lensplit,len_user_wllib_path_json_lensplit)

    #find max length of library attributes
    max_attribute_length=max(len_user_bllib_keys_json_lensplit,len_user_wllib_keys_json_lensplit,
                                len_user_bllib_netpath_json_lensplit,len_user_wllib_netpath_json_lensplit,
                                len_user_bllib_path_json_lensplit,len_user_wllib_path_json_lensplit)

    #make all list attributes the same length
    while not (min_attribute_length == max_attribute_length):
        if (len_user_bllib_keys_json_lensplit < max_attribute_length):
            user_bllib_keys_json_lensplit.append('')
            len_user_bllib_keys_json_lensplit += 1
        if (len_user_wllib_keys_json_lensplit < max_attribute_length):
            user_wllib_keys_json_lensplit.append('')
            len_user_wllib_keys_json_lensplit += 1

        if (len_user_bllib_netpath_json_lensplit < max_attribute_length):
            user_bllib_netpath_json_lensplit.append('')
            len_user_bllib_netpath_json_lensplit += 1
        if (len_user_wllib_netpath_json_lensplit < max_attribute_length):
            user_wllib_netpath_json_lensplit.append('')
            len_user_wllib_netpath_json_lensplit += 1

        if (len_user_bllib_path_json_lensplit < max_attribute_length):
            user_bllib_path_json_lensplit.append('')
            len_user_bllib_path_json_lensplit += 1
        if (len_user_wllib_path_json_lensplit < max_attribute_length):
            user_wllib_path_json_lensplit.append('')
            len_user_wllib_path_json_lensplit += 1
        min_attribute_length += 1

    media_found=False

############# Media #############

    if ((media_played_days >= 0) or (media_created_days >= 0)):

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nProcessing " + mediaType_upper + " Items For UserId: " + str(user_key),2,the_dict)

        user_processed_itemsId=set()

        currentSubPosition=0

        for LibraryID_BlkLst,LibraryID_WhtLst,LibraryNetPath_BlkLst,LibraryNetPath_WhtLst,LibraryPath_BlkLst,LibraryPath_WhtLst in zip(user_bllib_keys_json_lensplit,user_wllib_keys_json_lensplit,user_bllib_netpath_json_lensplit,user_wllib_netpath_json_lensplit,user_bllib_path_json_lensplit,user_wllib_path_json_lensplit):

            #Initialize api_query_handler() variables for watched media items in blacklists
            StartIndex_Blacklist=0
            TotalItems_Blacklist=1
            QueryLimit_Blacklist=1
            QueriesRemaining_Blacklist=True
            APIDebugMsg_Blacklist=mediaType_lower + '_blacklist_media_items'

            if not (LibraryID_BlkLst == ''):
                #Build query for watched media items in blacklists
                IncludeItemTypes_Blacklist=mediaType_title
                FieldsState_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_Blacklist='ParentIndexNumber,IndexNumber,Name'
                SortOrder_Blacklist='Ascending'
                EnableUserData_Blacklist='True'
                Recursive_Blacklist='True'
                EnableImages_Blacklist='False'
                CollapseBoxSetItems_Blacklist='False'
                IsPlayedState_Blacklist=get_isPlayedCreated_FilterValue(the_dict,media_played_days,media_created_days,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count)

                if (mediaType_lower == 'episode'):
                    FieldsState_Blacklist=FieldsState_Blacklist + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(the_dict['server_brand'])):
                        SortBy_Blacklist='SeriesSortName,' + SortBy_Blacklist
                    else:
                        SortBy_Blacklist='SeriesName,' + SortBy_Blacklist

                if ((mediaType_lower == 'audio') or (mediaType_lower == 'audiobook')):
                    FieldsState_Blacklist=FieldsState_Blacklist + ',ArtistItems,AlbumId,AlbumArtist' 
                    SortBy_Blacklist='Artists,PremiereDate,ProductionYear,Album,' + SortBy_Blacklist
                    if (isEmbyServer(the_dict['server_brand'])):
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_Blacklist+=',audiobook,book'
                    else:
                        if (mediaType_lower == 'audiobook'):
                            IncludeItemTypes_Blacklist=',book'

            #Initialize api_query_handler() variables for watched media items in whitelists
            StartIndex_Whitelist=0
            TotalItems_Whitelist=1
            QueryLimit_Whitelist=1
            QueriesRemaining_Whitelist=True
            APIDebugMsg_Whitelist=mediaType_lower + '_whitelist_media_items'

            if not (LibraryID_WhtLst == ''):
                #Build query for watched media items in whitelists
                IncludeItemTypes_Whitelist=mediaType_title
                FieldsState_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_Whitelist='ParentIndexNumber,IndexNumber,Name'
                SortOrder_Whitelist='Ascending'
                EnableUserData_Whitelist='True'
                Recursive_Whitelist='True'
                EnableImages_Whitelist='False'
                CollapseBoxSetItems_Whitelist='False'
                IsPlayedState_Whitelist=get_isPlayedCreated_FilterValue(the_dict,media_played_days,media_created_days,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count)

                if (mediaType_lower == 'episode'):
                    FieldsState_Whitelist=FieldsState_Whitelist + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(the_dict['server_brand'])):
                        SortBy_Whitelist='SeriesSortName,' + SortBy_Whitelist
                    else:
                        SortBy_Whitelist='SeriesName,' + SortBy_Whitelist

                if ((mediaType_lower == 'audio') or (mediaType_lower == 'audiobook')):
                    FieldsState_Whitelist=FieldsState_Whitelist + ',ArtistItems,AlbumId,AlbumArtist'
                    SortBy_Whitelist='Artist,PremiereDate,ProductionYear,Album,' + SortBy_Whitelist
                    if (isEmbyServer(the_dict['server_brand'])):
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_Whitelist+=',AudioBook,Book'
                    else:
                        if (mediaType_lower == 'audiobook'):
                            IncludeItemTypes_Whitelist=',Book'

            #Initialize api_query_handler() variables for Favorited from Blacklist media items
            StartIndex_Favorited_From_Blacklist=0
            TotalItems_Favorited_From_Blacklist=1
            QueryLimit_Favorited_From_Blacklist=1
            QueriesRemaining_Favorited_From_Blacklist=True
            APIDebugMsg_Favorited_From_Blacklist=mediaType_lower + '_Favorited_From_Blacklist_media_items'

            if not (LibraryID_BlkLst == ''):
                    #Build query for Favorited_From_Blacklist media items
                IncludeItemTypes_Favorited_From_Blacklist=mediaType_title
                FieldsState_Favorited_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_Favorited_From_Blacklist='ParentIndexNumber,IndexNumber,Name'
                SortOrder_Favorited_From_Blacklist='Ascending'
                EnableUserData_Favorited_From_Blacklist='True'
                Recursive_Favorited_From_Blacklist='True'
                EnableImages_Favorited_From_Blacklist='False'
                CollapseBoxSetItems_Favorited_From_Blacklist='False'
                IsFavorite_From_Blacklist='True'

                if (mediaType_lower == 'movie'):
                    IncludeItemTypes_Favorited_From_Blacklist+=',BoxSet,CollectionFolder'

                if (mediaType_lower == 'episode'):
                    IncludeItemTypes_Favorited_From_Blacklist+=',Season,Series,CollectionFolder'
                    FieldsState_Favorited_From_Blacklist=FieldsState_Favorited_From_Blacklist + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(the_dict['server_brand'])):
                        SortBy_Favorited_From_Blacklist='SeriesSortName,' + SortBy_Favorited_From_Blacklist
                    else:
                        SortBy_Favorited_From_Blacklist='SeriesName,' + SortBy_Favorited_From_Blacklist

                if ((mediaType_lower == 'audio') or (mediaType_lower == 'audiobook')):
                    FieldsState_Favorited_From_Blacklist=FieldsState_Favorited_From_Blacklist + ',ArtistItems,AlbumId,AlbumArtist'
                    SortBy_Favorited_From_Blacklist='Artist,PremiereDate,ProductionYear,Album,' + SortBy_Favorited_From_Blacklist
                    if (isEmbyServer(the_dict['server_brand'])):
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_Favorited_From_Blacklist+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_Favorited_From_Blacklist+=',MusicAlbum,Playlist,CollectionFolder'
                        elif (mediaType_lower == 'audiobook'):
                            IncludeItemTypes_Favorited_From_Blacklist+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for Favorited from Whitelist media items
            StartIndex_Favorited_From_Whitelist=0
            TotalItems_Favorited_From_Whitelist=1
            QueryLimit_Favorited_From_Whitelist=1
            QueriesRemaining_Favorited_From_Whitelist=True
            APIDebugMsg_Favorited_From_Whitelist=mediaType_lower + '_Favorited_From_Whitelist_media_items'

            if not (LibraryID_WhtLst == ''):
                #Build query for Favorited_From_Whitelist media items
                IncludeItemTypes_Favorited_From_Whitelist=mediaType_title
                FieldsState_Favorited_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_Favorited_From_Whitelist='ParentIndexNumber,IndexNumber,Name'
                SortOrder_Favorited_From_Whitelist='Ascending'
                EnableUserData_Favorited_From_Whitelist='True'
                Recursive_Favorited_From_Whitelist='True'
                EnableImages_Favorited_From_Whitelist='False'
                CollapseBoxSetItems_Favorited_From_Whitelist='False'
                IsFavorite_From_Whitelist='True'

                if (mediaType_lower == 'movie'):
                    IncludeItemTypes_Favorited_From_Whitelist+=',BoxSet,CollectionFolder'

                if (mediaType_lower == 'episode'):
                    IncludeItemTypes_Favorited_From_Whitelist+=',Season,Series,CollectionFolder'
                    FieldsState_Favorited_From_Whitelist=FieldsState_Favorited_From_Whitelist + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(the_dict['server_brand'])):
                        SortBy_Favorited_From_Whitelist='SeriesSortName,' + SortBy_Favorited_From_Whitelist
                    else:
                        SortBy_Favorited_From_Whitelist='SeriesName,' + SortBy_Favorited_From_Whitelist

                if ((mediaType_lower == 'audio') or (mediaType_lower == 'audiobook')):
                    FieldsState_Favorited_From_Whitelist=FieldsState_Favorited_From_Whitelist + ',ArtistItems,AlbumId,AlbumArtist'
                    SortBy_Favorited_From_Whitelist='Artist,PremiereDate,ProductionYear,Album,' + SortBy_Favorited_From_Whitelist
                    if (isEmbyServer(the_dict['server_brand'])):
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_Favorited_From_Whitelist+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_Favorited_From_Whitelist+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                        elif (mediaType_lower == 'audiobook'):
                            IncludeItemTypes_Favorited_From_Whitelist+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for tagged media items
            StartIndex_BlackTagged_From_BlackList=0
            TotalItems_BlackTagged_From_BlackList=1
            QueryLimit_BlackTagged_From_BlackList=1
            QueriesRemaining_BlackTagged_From_BlackList=True
            APIDebugMsg_BlackTagged_From_BlackList=mediaType_lower + '_blacktagged_from_blacklist_media_items'

            if not (LibraryID_BlkLst == ''):
                #Build query for blacktagged media items from blacklist
                IncludeItemTypes_BlackTagged_From_BlackList=mediaType_title
                FieldsState_BlackTagged_From_BlackList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_BlackTagged_From_BlackList='ParentIndexNumber,IndexNumber,Name'
                SortOrder_BlackTagged_From_BlackList='Ascending'
                EnableUserData_Blacktagged_From_BlackList='True'
                Recursive_Blacktagged_From_BlackList='True'
                EnableImages_Blacktagged_From_BlackList='False'
                CollapseBoxSetItems_Blacktagged_From_BlackList='False'
                #Encode blacktags so they are url acceptable
                BlackTags_Tagged=list_to_urlparsed_string(blacktags)

                if (mediaType_lower == 'movie'):
                    IncludeItemTypes_BlackTagged_From_BlackList+=',BoxSet,CollectionFolder'

                if (mediaType_lower == 'episode'):
                    IncludeItemTypes_BlackTagged_From_BlackList+=',Season,Series,CollectionFolder'
                    FieldsState_BlackTagged_From_BlackList=FieldsState_BlackTagged_From_BlackList + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(the_dict['server_brand'])):
                        SortBy_BlackTagged_From_BlackList='SeriesSortName,' + SortBy_BlackTagged_From_BlackList
                    else:
                        SortBy_BlackTagged_From_BlackList='SeriesName,' + SortBy_BlackTagged_From_BlackList

                if ((mediaType_lower == 'audio') or (mediaType_lower == 'audiobook')):
                    FieldsState_BlackTagged_From_BlackList=FieldsState_BlackTagged_From_BlackList + ',ArtistItems,AlbumId,AlbumArtist'
                    SortBy_BlackTagged_From_BlackList='Artist,PremiereDate,ProductionYear,Album,' + SortBy_BlackTagged_From_BlackList
                    if (isEmbyServer(the_dict['server_brand'])):
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_BlackTagged_From_BlackList+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_BlackTagged_From_BlackList+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                        elif (mediaType_lower == 'audiobook'):
                            IncludeItemTypes_BlackTagged_From_BlackList+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for tagged media items
            StartIndex_BlackTagged_From_WhiteList=0
            TotalItems_BlackTagged_From_WhiteList=1
            QueryLimit_BlackTagged_From_WhiteList=1
            QueriesRemaining_BlackTagged_From_WhiteList=True
            APIDebugMsg_BlackTagged_From_WhiteList=mediaType_lower + '_blacktagged_fromwhitelisted_media_items'

            if not (LibraryID_WhtLst == ''):
                #Build query for blacktagged media items from whitelist
                IncludeItemTypes_BlackTagged_From_WhiteList=mediaType_title
                FieldsState_BlackTagged_From_WhiteList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_BlackTagged_From_WhiteList='ParentIndexNumber,IndexNumber,Name'
                SortOrder_BlackTagged_From_WhiteList='Ascending'
                EnableUserData_Blacktagged_From_WhiteList='True'
                Recursive_Blacktagged_From_WhiteList='True'
                EnableImages_Blacktagged_From_WhiteList='False'
                CollapseBoxSetItems_Blacktagged_From_WhiteList='False'
                #Encode blacktags so they are url acceptable
                BlackTags_Tagged=list_to_urlparsed_string(blacktags)

                if (mediaType_lower == 'movie'):
                    IncludeItemTypes_BlackTagged_From_WhiteList+=',BoxSet,CollectionFolder'

                if (mediaType_lower == 'episode'):
                    IncludeItemTypes_BlackTagged_From_WhiteList+=',Season,Series,CollectionFolder'
                    FieldsState_BlackTagged_From_WhiteList=FieldsState_BlackTagged_From_WhiteList + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(the_dict['server_brand'])):
                        SortBy_BlackTagged_From_WhiteList='SeriesSortName,' + SortBy_BlackTagged_From_WhiteList
                    else:
                        SortBy_BlackTagged_From_WhiteList='SeriesName,' + SortBy_BlackTagged_From_WhiteList

                if ((mediaType_lower == 'audio') or (mediaType_lower == 'audiobook')):
                    FieldsState_BlackTagged_From_WhiteList=FieldsState_BlackTagged_From_WhiteList + ',ArtistItems,AlbumId,AlbumArtist'
                    SortBy_BlackTagged_From_WhiteList='Artist,PremiereDate,ProductionYear,Album,' + SortBy_BlackTagged_From_WhiteList
                    if (isEmbyServer(the_dict['server_brand'])):
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_BlackTagged_From_WhiteList+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_BlackTagged_From_WhiteList+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                        elif (mediaType_lower == 'audiobook'):
                            IncludeItemTypes_BlackTagged_From_WhiteList+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for tagged media items
            StartIndex_WhiteTagged_From_Blacklist=0
            TotalItems_WhiteTagged_From_Blacklist=1
            QueryLimit_WhiteTagged_From_Blacklist=1
            QueriesRemaining_WhiteTagged_From_Blacklist=True
            APIDebugMsg_WhiteTagged_From_Blacklist=mediaType_lower + '_whitetagged_media_items'

            if not (LibraryID_BlkLst == ''):
                #Build query for whitetagged media items from blacklist
                IncludeItemTypes_WhiteTagged_From_Blacklist=mediaType_title
                FieldsState_WhiteTagged_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_WhiteTagged_From_Blacklist='ParentIndexNumber,IndexNumber,Name'
                SortOrder_WhiteTagged_From_Blacklist='Ascending'
                EnableUserData_Whitetagged_From_Blacklist='True'
                Recursive_Whitetagged_From_Blacklist='True'
                EnableImages_Whitetagged_From_Blacklist='False'
                CollapseBoxSetItems_Whitetagged_From_Blacklist='False'
                #Encode whitetags so they are url acceptable
                WhiteTags_Tagged=list_to_urlparsed_string(whitetags)

                if (mediaType_lower == 'movie'):
                    IncludeItemTypes_WhiteTagged_From_Blacklist+=',BoxSet,CollectionFolder'

                if (mediaType_lower == 'episode'):
                    IncludeItemTypes_WhiteTagged_From_Blacklist+=',Season,Series,CollectionFolder'
                    FieldsState_WhiteTagged_From_Blacklist=FieldsState_WhiteTagged_From_Blacklist + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(the_dict['server_brand'])):
                        SortBy_WhiteTagged_From_Blacklist='SeriesSortName,' + SortBy_WhiteTagged_From_Blacklist
                    else:
                        SortBy_WhiteTagged_From_Blacklist='SeriesName,' + SortBy_WhiteTagged_From_Blacklist

                if ((mediaType_lower == 'audio') or (mediaType_lower == 'audiobook')):
                    FieldsState_WhiteTagged_From_Blacklist=FieldsState_WhiteTagged_From_Blacklist + ',ArtistItems,AlbumId,AlbumArtist'
                    SortBy_WhiteTagged_From_Blacklist='Artist,PremiereDate,ProductionYear,Album,' + SortBy_WhiteTagged_From_Blacklist
                    if (isEmbyServer(the_dict['server_brand'])):
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_WhiteTagged_From_Blacklist+=',Audio,AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_WhiteTagged_From_Blacklist+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                        elif (mediaType_lower == 'audiobook'):
                            IncludeItemTypes_WhiteTagged_From_Blacklist+=',Book,MusicAlbum,Playlist,CollectionFolder'

            #Initialize api_query_handler() variables for tagged media items
            StartIndex_WhiteTagged_From_Whitelist=0
            TotalItems_WhiteTagged_From_Whitelist=1
            QueryLimit_WhiteTagged_From_Whitelist=1
            QueriesRemaining_WhiteTagged_From_Whitelist=True
            APIDebugMsg_WhiteTagged_From_Whitelist=mediaType_lower + '_whitetagged_media_items'

            if not (LibraryID_WhtLst == ''):
                #Build query for whitetagged media items from whitelist
                IncludeItemTypes_WhiteTagged_From_Whitelist=mediaType_title
                FieldsState_WhiteTagged_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_WhiteTagged_From_Whitelist='ParentIndexNumber,IndexNumber,Name'
                SortOrder_WhiteTagged_From_Whitelist='Ascending'
                EnableUserData_Whitetagged_From_Whitelist='True'
                Recursive_Whitetagged_From_Whitelist='True'
                EnableImages_Whitetagged_From_Whitelist='False'
                CollapseBoxSetItems_Whitetagged_From_Whitelist='False'
                #Encode whitetags so they are url acceptable
                WhiteTags_Tagged=list_to_urlparsed_string(whitetags)

                if (mediaType_lower == 'movie'):
                    IncludeItemTypes_WhiteTagged_From_Whitelist+=',BoxSet,CollectionFolder'

                if (mediaType_lower == 'episode'):
                    IncludeItemTypes_WhiteTagged_From_Whitelist+=',Season,Series,CollectionFolder'
                    FieldsState_WhiteTagged_From_Whitelist=FieldsState_WhiteTagged_From_Whitelist + ',SeriesStudio,seriesStatus'
                    if (isJellyfinServer(the_dict['server_brand'])):
                        SortBy_WhiteTagged_From_Whitelist='SeriesSortName,' + SortBy_WhiteTagged_From_Whitelist
                    else:
                        SortBy_WhiteTagged_From_Whitelist='SeriesName,' + SortBy_WhiteTagged_From_Whitelist

                if ((mediaType_lower == 'audio') or (mediaType_lower == 'audiobook')):
                    FieldsState_WhiteTagged_From_Whitelist=FieldsState_WhiteTagged_From_Whitelist + ',ArtistItems,AlbumId,AlbumArtist'
                    SortBy_WhiteTagged_From_Whitelist='Artist,PremiereDate,ProductionYear,Album,' + SortBy_WhiteTagged_From_Whitelist
                    if (isEmbyServer(the_dict['server_brand'])):
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_WhiteTagged_From_Whitelist+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
                    else:
                        if (mediaType_lower == 'audio'):
                            IncludeItemTypes_WhiteTagged_From_Whitelist+=',MusicAlbum,Playlist,CollectionFolder'
                        elif (mediaType_lower == 'audiobook'):
                            IncludeItemTypes_WhiteTagged_From_Whitelist+=',Book,MusicAlbum,Playlist,CollectionFolder'

            QueryItemsRemaining_All=True

            while (QueryItemsRemaining_All):

                if not (LibraryID_BlkLst == ''):
                    #Built query for watched items in blacklists
                    apiQuery_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Blacklist +
                    '&StartIndex=' + str(StartIndex_Blacklist) + '&Limit=' + str(QueryLimit_Blacklist) + '&IsPlayed=' + IsPlayedState_Blacklist +
                    '&Fields=' + FieldsState_Blacklist + '&Recursive=' + Recursive_Blacklist + '&SortBy=' + SortBy_Blacklist + '&SortOrder=' + SortOrder_Blacklist +
                    '&EnableImages=' + EnableImages_Blacklist + '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacklist + '&EnableUserData=' + EnableUserData_Blacklist + '&api_key=' + auth_key)

                    #Send the API query for for watched media items in blacklists
                    data_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,QueriesRemaining_Blacklist=api_query_handler(apiQuery_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,APIDebugMsg_Blacklist,the_dict)
                else:
                    #When no media items are blacklisted; simulate an empty query being returned
                    #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                    data_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    QueryLimit_Blacklist=0
                    QueriesRemaining_Blacklist=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo watched media items are blacklisted",2,the_dict)

                if not (LibraryID_WhtLst == ''):
                    #Built query for watched items in whitelists
                    apiQuery_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_Whitelist +
                    '&StartIndex=' + str(StartIndex_Whitelist) + '&Limit=' + str(QueryLimit_Whitelist) + '&IsPlayed=' + IsPlayedState_Whitelist +
                    '&Fields=' + FieldsState_Whitelist + '&Recursive=' + Recursive_Whitelist + '&SortBy=' + SortBy_Whitelist + '&SortOrder=' + SortOrder_Whitelist +
                    '&EnableImages=' + EnableImages_Whitelist + '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitelist + '&EnableUserData=' + EnableUserData_Whitelist + '&api_key=' + auth_key)

                    #Send the API query for for watched media items in whitelists
                    data_Whitelist,StartIndex_Whitelist,TotalItems_Whitelist,QueryLimit_Whitelist,QueriesRemaining_Whitelist=api_query_handler(apiQuery_Whitelist,StartIndex_Whitelist,TotalItems_Whitelist,QueryLimit_Whitelist,APIDebugMsg_Whitelist,the_dict)
                else:
                    #When no media items are whitelisted; simulate an empty query being returned
                    #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
                    data_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    QueryLimit_Whitelist=0
                    QueriesRemaining_Whitelist=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo watched media items are whitelisted",2,the_dict)

                if not (LibraryID_BlkLst == ''):
                    #Built query for Favorited from Blacklist media items
                    apiQuery_Favorited_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Blacklist +
                    '&StartIndex=' + str(StartIndex_Favorited_From_Blacklist) + '&Limit=' + str(QueryLimit_Favorited_From_Blacklist) + '&Fields=' + FieldsState_Favorited_From_Blacklist +
                    '&Recursive=' + Recursive_Favorited_From_Blacklist + '&SortBy=' + SortBy_Favorited_From_Blacklist + '&SortOrder=' + SortOrder_Favorited_From_Blacklist + '&EnableImages=' + EnableImages_Favorited_From_Blacklist +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Blacklist + '&IsFavorite=' + IsFavorite_From_Blacklist + '&EnableUserData=' + EnableUserData_Favorited_From_Blacklist + '&api_key=' + auth_key)

                    #Send the API query for for Favorited from Blacklist media items
                    data_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,QueriesRemaining_Favorited_From_Blacklist=api_query_handler(apiQuery_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,APIDebugMsg_Favorited_From_Blacklist,the_dict)
                else:
                    #When no media items are blacklisted; simulate an empty query being returned
                    #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                    data_Favorited_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    QueryLimit_Favorited_From_Blacklist=0
                    QueriesRemaining_Favorited_From_Blacklist=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo favorited media items are blacklisted",2,the_dict)

                if not (LibraryID_WhtLst == ''):
                    #Built query for Favorited From Whitelist media items
                    apiQuery_Favorited_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Whitelist +
                    '&StartIndex=' + str(StartIndex_Favorited_From_Whitelist) + '&Limit=' + str(QueryLimit_Favorited_From_Whitelist) + '&Fields=' + FieldsState_Favorited_From_Whitelist +
                    '&Recursive=' + Recursive_Favorited_From_Whitelist + '&SortBy=' + SortBy_Favorited_From_Whitelist + '&SortOrder=' + SortOrder_Favorited_From_Whitelist + '&EnableImages=' + EnableImages_Favorited_From_Whitelist +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Whitelist + '&IsFavorite=' + IsFavorite_From_Whitelist + '&EnableUserData=' + EnableUserData_Favorited_From_Whitelist + '&api_key=' + auth_key)

                    #Send the API query for for Favorited from Whitelist media items
                    data_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,QueriesRemaining_Favorited_From_Whitelist=api_query_handler(apiQuery_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,APIDebugMsg_Favorited_From_Whitelist,the_dict)
                else:
                    #When no media items are whitelisted; simulate an empty query being returned
                    #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
                    data_Favorited_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    QueryLimit_Favorited_From_Whitelist=0
                    QueriesRemaining_Favorited_From_Whitelist=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo favorited media items are whitelisted",2,the_dict)

                #Check if blacktag or blacklist are not an empty strings
                if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                    #Built query for blacktagged from blacklist media items
                    apiQuery_BlackTagged_From_BlackList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_BlackList +
                    '&StartIndex=' + str(StartIndex_BlackTagged_From_BlackList) + '&Limit=' + str(QueryLimit_BlackTagged_From_BlackList) + '&Fields=' + FieldsState_BlackTagged_From_BlackList +
                    '&Recursive=' + Recursive_Blacktagged_From_BlackList + '&SortBy=' + SortBy_BlackTagged_From_BlackList + '&SortOrder=' + SortOrder_BlackTagged_From_BlackList + '&EnableImages=' + EnableImages_Blacktagged_From_BlackList +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_BlackList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_BlackList + '&api_key=' + auth_key)

                    #Send the API query for for blacktagged from blacklist media items
                    data_Blacktagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,QueriesRemaining_BlackTagged_From_BlackList=api_query_handler(apiQuery_BlackTagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,APIDebugMsg_BlackTagged_From_BlackList,the_dict)
                else: #((BlackTags_Tagged == '') or (LibraryID_BlkLst == ''))
                    data_Blacktagged_From_BlackList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    QueryLimit_BlackTagged_From_BlackList=0
                    QueriesRemaining_BlackTagged_From_BlackList=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo blacktagged media items are blacklisted",2,the_dict)

                #Check if blacktag or whitelist are not an empty strings
                if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                    #Built query for blacktagged from whitelist media items
                    apiQuery_BlackTagged_From_WhiteList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_WhiteList +
                    '&StartIndex=' + str(StartIndex_BlackTagged_From_WhiteList) + '&Limit=' + str(QueryLimit_BlackTagged_From_WhiteList) + '&Fields=' + FieldsState_BlackTagged_From_WhiteList +
                    '&Recursive=' + Recursive_Blacktagged_From_WhiteList + '&SortBy=' + SortBy_BlackTagged_From_WhiteList + '&SortOrder=' + SortOrder_BlackTagged_From_WhiteList + '&EnableImages=' + EnableImages_Blacktagged_From_WhiteList +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_WhiteList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_WhiteList + '&api_key=' + auth_key)

                    #Send the API query for for blacktagged from whitelist media items
                    data_Blacktagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,QueriesRemaining_BlackTagged_From_WhiteList=api_query_handler(apiQuery_BlackTagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,APIDebugMsg_BlackTagged_From_WhiteList,the_dict)
                else: #((BlackTags_Tagged == '') or (LibraryID_WhtLst == ''))
                    data_Blacktagged_From_WhiteList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    QueryLimit_BlackTagged_From_WhiteList=0
                    QueriesRemaining_BlackTagged_From_WhiteList=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo blacktagged media items are whitelisted",2,the_dict)

                #Check if whitetag or blacklist are not an empty strings
                if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                    #Built query for whitetagged from Blacklist media items
                    apiQuery_WhiteTagged_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Blacklist +
                    '&StartIndex=' + str(StartIndex_WhiteTagged_From_Blacklist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Blacklist) + '&Fields=' + FieldsState_WhiteTagged_From_Blacklist +
                    '&Recursive=' + Recursive_Whitetagged_From_Blacklist + '&SortBy=' + SortBy_WhiteTagged_From_Blacklist + '&SortOrder=' + SortOrder_WhiteTagged_From_Blacklist + '&EnableImages=' + EnableImages_Whitetagged_From_Blacklist +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Blacklist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Blacklist + '&api_key=' + auth_key)

                    #Send the API query for for whitetagged from Blacklist= media items
                    data_Whitetagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,QueriesRemaining_WhiteTagged_From_Blacklist=api_query_handler(apiQuery_WhiteTagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,APIDebugMsg_WhiteTagged_From_Blacklist,the_dict)
                else: #(WhiteTags_Tagged_From_Blacklist == '')
                    data_Whitetagged_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    QueryLimit_WhiteTagged_From_Blacklist=0
                    QueriesRemaining_WhiteTagged_From_Blacklist=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo whitetagged media items are blacklisted",2,the_dict)

                #Check if whitetag or whitelist are not an empty strings
                if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                    #Built query for whitetagged_From_Whitelist= media items
                    apiQuery_WhiteTagged_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Whitelist +
                    '&StartIndex=' + str(StartIndex_WhiteTagged_From_Whitelist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Whitelist) + '&Fields=' + FieldsState_WhiteTagged_From_Whitelist +
                    '&Recursive=' + Recursive_Whitetagged_From_Whitelist + '&SortBy=' + SortBy_WhiteTagged_From_Whitelist + '&SortOrder=' + SortOrder_WhiteTagged_From_Whitelist + '&EnableImages=' + EnableImages_Whitetagged_From_Whitelist +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Whitelist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Whitelist + '&api_key=' + auth_key)

                    #Send the API query for for whitetagged_From_Whitelist= media items
                    data_Whitetagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,QueriesRemaining_WhiteTagged_From_Whitelist=api_query_handler(apiQuery_WhiteTagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,APIDebugMsg_WhiteTagged_From_Whitelist,the_dict)
                else: #(WhiteTags_Tagged == '')
                    data_Whitetagged_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                    QueryLimit_WhiteTagged_From_Whitelist=0
                    QueriesRemaining_WhiteTagged_From_Whitelist=False
                    if (the_dict['DEBUG']):
                        appendTo_DEBUG_log("\n\nNo whitetagged media items are whitelisted",2,the_dict)

                #Define reasoning for lookup
                APIDebugMsg_Favorited_From_Blacklist_Child='favorited_From_Blacklist_from_blacklist_child'
                data_Favorited_From_Blacklist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Blacklist,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Favorited_From_Blacklist_Child,media_played_days,media_created_days,the_dict)
                #Define reasoning for lookup
                APIDebugMsg_Favorited_From_Whitelist_Child='favorited_From_Whitelist_fromwhitelisted_child'
                data_Favorited_From_Whitelist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Whitelist,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Favorited_From_Whitelist_Child,media_played_days,media_created_days,the_dict)

                #Define reasoning for lookup
                APIDebugMsg_Blacktag_From_BlackList_Child='blacktagged_child_from_blacklist_child'
                data_Blacktagged_From_BlackList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_BlackList,blacktags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Blacktag_From_BlackList_Child,media_played_days,media_created_days,the_dict)
                #Define reasoning for lookup
                APIDebugMsg_Blacktag_From_WhiteList_Child='blacktagged_child_fromwhitelisted_child'
                data_Blacktagged_From_WhiteList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_WhiteList,blacktags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Blacktag_From_WhiteList_Child,media_played_days,media_created_days,the_dict)
                #Define reasoning for lookup
                APIDebugMsg_Whitetag_From_Blacklist_Child='whitetagged_child_from_blacklist_child'
                data_Whitetagged_From_Blacklist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Blacklist,whitetags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Whitetag_From_Blacklist_Child,media_played_days,media_created_days,the_dict)
                #Define reasoning for lookup
                APIDebugMsg_Whitetag_From_Whitelist_Child='whitetagged_child_from_blacklist_child'
                data_Whitetagged_From_Whitelist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Whitelist,whitetags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Whitetag_From_Whitelist_Child,media_played_days,media_created_days,the_dict)

                #Combine dictionaries into list of dictionaries
                #Order here is important
                data_lists=[data_Favorited_From_Whitelist, #0
                            data_Favorited_From_Whitelist_Children, #1
                            data_Whitetagged_From_Whitelist, #2
                            data_Whitetagged_From_Whitelist_Children, #3
                            data_Blacktagged_From_WhiteList, #4
                            data_Blacktagged_From_WhiteList_Children, #5
                            data_Favorited_From_Blacklist, #6
                            data_Favorited_From_Blacklist_Children, #7
                            data_Whitetagged_From_Blacklist, #8
                            data_Whitetagged_From_Blacklist_Children, #9
                            data_Blacktagged_From_BlackList, #10
                            data_Blacktagged_From_BlackList_Children, #11
                            data_Blacklist, #12
                            data_Whitelist] #13

                #Order here is important (must match above)
                data_from_favorited_queries=[0,1,6,7]
                data_from_whitetagged_queries=[2,3,8,9]
                data_from_blacktagged_queries=[4,5,10,11]
                data_from_whitelisted_queries=[0,1,2,3,4,5,13]
                data_from_blacklisted_queries=[6,7,8,9,10,11,12]

                #Determine if we are done processing queries or if there are still queries to be sent
                QueryItemsRemaining_All=(QueriesRemaining_Favorited_From_Blacklist |
                                            QueriesRemaining_Favorited_From_Whitelist |
                                            QueriesRemaining_WhiteTagged_From_Blacklist |
                                            QueriesRemaining_WhiteTagged_From_Whitelist |
                                            QueriesRemaining_BlackTagged_From_BlackList |
                                            QueriesRemaining_BlackTagged_From_WhiteList |
                                            QueriesRemaining_Blacklist |
                                            QueriesRemaining_Whitelist)

                #track where we are in the data_lists
                data_list_pos=0

                #Determine if media item is shown as DELETE or KEEP
                #Loop thru each dictionary in data_lists[#]
                for data_dict in data_lists:

                    #Loop thru each data_dict['Items'] item
                    for item in data_dict['Items']:

                        #Check if item was already processed for this user
                        if not (item['Id'] in user_processed_itemsId):

                            if (the_dict['DEBUG']):
                                #Double newline for DEBUG log formatting
                                appendTo_DEBUG_log("\n\nInspecting Media Item: " + str(item['Id']),2,the_dict)

                            media_found=True

                            itemIsMonitored=False
                            if (item['Type'] == mediaType_title):
                                for mediasource in item['MediaSources']:
                                    itemIsMonitored=get_isItemMonitored(mediasource,the_dict)

                            #determine how to show media item
                            if (itemIsMonitored):

                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nProcessing " + mediaType_title + " Item: " + str(item['Id']),2,the_dict)

                                #Fill in the blanks
                                if (mediaType_lower == 'movie'):
                                    item=prepare_MOVIEoutput(the_dict,item,user_key,the_dict['movie_set_missing_last_played_date'])
                                elif (mediaType_lower == 'episode'):
                                    item=prepare_EPISODEoutput(the_dict,item,user_key,the_dict['episode_set_missing_last_played_date'])
                                elif (mediaType_lower == 'audio'):
                                    item=prepare_AUDIOoutput(the_dict,item,user_key,the_dict['audio_set_missing_last_played_date'],mediaType_lower)
                                elif (mediaType_lower == 'audiobook'):
                                    item=prepare_AUDIOBOOKoutput(the_dict,item,user_key,the_dict['audiobook_set_missing_last_played_date'],mediaType_lower)

                                isfavorited_extraInfo_byUserId_Media[user_key][item['Id']]={}
                                iswhitetagged_extraInfo_byUserId_Media[user_key][item['Id']]={}
                                isblacktagged_extraInfo_byUserId_Media[user_key][item['Id']]={}
                                iswhitelisted_extraInfo_byUserId_Media[user_key][item['Id']]={}
                                isblacklisted_extraInfo_byUserId_Media[user_key][item['Id']]={}

##########################################################################################################################################

                                #Get determine if item meets played days, created days, played counts, and played-created counts
                                itemIsPlayed,itemPlayedCount,item_matches_played_days_filter,item_matches_created_days_filter,item_matches_played_count_filter,item_matches_created_played_count_filter\
                                =get_playedCreatedDays_playedCreatedCounts(the_dict,item,media_played_days,media_created_days,cut_off_date_played_media,cut_off_date_created_media,
                                                                            media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count)

##########################################################################################################################################

                                if (item_matches_created_days_filter and item_matches_created_played_count_filter):
                                    if (not (item['Id'] in deleteItemsIdTracker_createdMedia)):
                                        deleteItemsIdTracker_createdMedia.append(item['Id'])
                                        deleteItems_createdMedia.append(item)

##########################################################################################################################################

                                item_isFavorited=False
                                #Get if media item is set as favorite
                                if (data_list_pos in data_from_favorited_queries):
                                    item_isFavorited=True
                                else:
                                    if (mediaType_lower == 'movie'):
                                        item_isFavorited=get_isMOVIE_Fav(the_dict,item,user_key)
                                    elif (mediaType_lower == 'episode'):
                                        item_isFavorited=get_isEPISODE_Fav(the_dict,item,user_key)
                                    elif (mediaType_lower == 'audio'):
                                        item_isFavorited=get_isAUDIO_Fav(the_dict,item,user_key,'Audio')
                                    elif (mediaType_lower == 'audiobook'):
                                        item_isFavorited=get_isAUDIOBOOK_Fav(the_dict,item,user_key,'AudioBook')

                                #Get if media item is set as an advanced favorite
                                item_isFavorited_Advanced=False
                                if ((favorited_behavior_media[3] >= 0) and (advFav0_media or advFav1_media or advFav2_media or advFav3_media or advFav4_media or advFav5_media)):
                                    if (mediaType_lower == 'movie'):
                                        item_isFavorited_Advanced=get_isMOVIE_AdvancedFav(the_dict,item,user_key,advFav0_media,advFav1_media)
                                    elif (mediaType_lower == 'episode'):
                                        item_isFavorited_Advanced=get_isEPISODE_AdvancedFav(the_dict,item,user_key,advFav0_media,advFav1_media, advFav2_media,advFav3_media,advFav4_media,advFav5_media)
                                    elif (mediaType_lower == 'audio'):
                                        item_isFavorited_Advanced=get_isAUDIO_AdvancedFav(the_dict,item,user_key,'Audio',advFav0_media,advFav1_media,advFav2_media,advFav3_media,advFav4_media)
                                    elif (mediaType_lower == 'audiobook'):
                                        item_isFavorited_Advanced=get_isAUDIOBOOK_AdvancedFav(the_dict,item,user_key,'AudioBook',advFav0_media,advFav1_media,advFav2_media,advFav3_media,advFav4_media,advFav5_media)

                                #Determine what will show as the favorite status for this user and media item
                                isFavorited_Display=(item_isFavorited or item_isFavorited_Advanced)

                                #favorite behavior enabled
                                isfavorited_and_played_byUserId_Media,isfavorited_extraInfo_byUserId_Media=parse_actionedConfigurationBehavior(the_dict,item,isfavorited_extraInfo_byUserId_Media,user_key,'favorited',isfavorited_and_played_byUserId_Media,favorited_behavior_media,(item_isFavorited or item_isFavorited_Advanced),item_matches_played_days_filter,item_matches_played_count_filter,item_matches_created_days_filter,item_matches_created_played_count_filter,itemIsPlayed,itemPlayedCount)

##########################################################################################################################################

                                item_isWhiteTagged=False
                                if (data_list_pos in data_from_whitetagged_queries):
                                    item_isWhiteTagged=True
                                elif (not (whitetags == '')):
                                    if (mediaType_lower == 'movie'):
                                        item_isWhiteTagged=get_isMOVIE_Tagged(the_dict,item,user_key,whitetags)
                                    elif (mediaType_lower == 'episode'):
                                        item_isWhiteTagged=get_isEPISODE_Tagged(the_dict,item,user_key,whitetags)
                                    elif (mediaType_lower == 'audio'):
                                        item_isWhiteTagged=get_isAUDIO_Tagged(the_dict,item,user_key,whitetags)
                                    elif (mediaType_lower == 'audiobook'):
                                        item_isWhiteTagged=get_isAUDIOBOOK_Tagged(the_dict,item,user_key,whitetags)

                                isWhiteTagged_Display=item_isWhiteTagged

                                #whitetag behavior enabled
                                iswhitetagged_and_played_byUserId_Media,iswhitetagged_extraInfo_byUserId_Media=parse_actionedConfigurationBehavior(the_dict,item,iswhitetagged_extraInfo_byUserId_Media,user_key,'whitetagged',iswhitetagged_and_played_byUserId_Media,whitetagged_behavior_media,item_isWhiteTagged,item_matches_played_days_filter,item_matches_played_count_filter,item_matches_created_days_filter,item_matches_created_played_count_filter,itemIsPlayed,itemPlayedCount)

##########################################################################################################################################

                                item_isBlackTagged=False
                                if (data_list_pos in data_from_blacktagged_queries):
                                    item_isBlackTagged=True
                                elif (not (blacktags == '')):
                                    if (mediaType_lower == 'movie'):
                                        item_isBlackTagged=get_isMOVIE_Tagged(the_dict,item,user_key,blacktags)
                                    elif (mediaType_lower == 'episode'):
                                        item_isBlackTagged=get_isEPISODE_Tagged(the_dict,item,user_key,blacktags)
                                    elif (mediaType_lower == 'audio'):
                                        item_isBlackTagged=get_isAUDIO_Tagged(the_dict,item,user_key,blacktags)
                                    elif (mediaType_lower == 'audiobook'):
                                        item_isBlackTagged=get_isAUDIOBOOK_Tagged(the_dict,item,user_key,blacktags)

                                isBlackTagged_Display=item_isBlackTagged

                                #blacktag behavior enabled
                                isblacktagged_and_played_byUserId_Media,isblacktagged_extraInfo_byUserId_Media=parse_actionedConfigurationBehavior(the_dict,item,isblacktagged_extraInfo_byUserId_Media,user_key,'blacktagged',isblacktagged_and_played_byUserId_Media,blacktagged_behavior_media,item_isBlackTagged,item_matches_played_days_filter,item_matches_played_count_filter,item_matches_created_days_filter,item_matches_created_played_count_filter,itemIsPlayed,itemPlayedCount)

##########################################################################################################################################

                                isWhiteListed_Display=False
                                #check if we are at a whitelist queried data_list_pos
                                if (data_list_pos in data_from_whitelisted_queries):
                                    item_isWhiteListed=get_isItemWhitelisted(the_dict,item,LibraryID_WhtLst,LibraryNetPath_WhtLst,LibraryPath_WhtLst,library_matching_behavior,
                                                                                    user_wllib_keys_json[currentPosition],user_wllib_netpath_json[currentPosition],user_wllib_path_json[currentPosition])
                                    iswhitelisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryId']=LibraryID_WhtLst
                                    iswhitelisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryPath']=LibraryPath_WhtLst
                                    iswhitelisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryNetPath']=LibraryNetPath_WhtLst
                                else: #check if we are at a blacklist queried data_list_pos
                                    item_isWhiteListed=get_isItemWhitelisted(the_dict,item,LibraryID_BlkLst,LibraryNetPath_BlkLst,LibraryPath_BlkLst,library_matching_behavior,
                                                                                    user_wllib_keys_json[currentPosition],user_wllib_netpath_json[currentPosition],user_wllib_path_json[currentPosition])
                                    iswhitelisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryId']=LibraryID_BlkLst
                                    iswhitelisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryPath']=LibraryPath_BlkLst
                                    iswhitelisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryNetPath']=LibraryNetPath_BlkLst

                                isWhiteListed_Display=item_isWhiteListed

                                #whitelist behavior enabled
                                iswhitelisted_and_played_byUserId_Media,iswhitelisted_extraInfo_byUserId_Media=parse_actionedConfigurationBehavior(the_dict,item,iswhitelisted_extraInfo_byUserId_Media,user_key,'whitelisted',iswhitelisted_and_played_byUserId_Media,whitelisted_behavior_media,item_isWhiteListed,item_matches_played_days_filter,item_matches_played_count_filter,item_matches_created_days_filter,item_matches_created_played_count_filter,itemIsPlayed,itemPlayedCount)

##########################################################################################################################################

                                isBlackListed_Display=False
                                #check if we are at a blacklist queried data_list_pos
                                if (data_list_pos in data_from_blacklisted_queries):
                                    item_isBlackListed=get_isItemBlacklisted(the_dict,item,LibraryID_BlkLst,LibraryNetPath_BlkLst,LibraryPath_BlkLst,library_matching_behavior,
                                                                                    user_bllib_keys_json[currentPosition],user_bllib_netpath_json[currentPosition],user_bllib_path_json[currentPosition])
                                    isblacklisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryId']=LibraryID_BlkLst
                                    isblacklisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryPath']=LibraryPath_BlkLst
                                    isblacklisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryNetPath']=LibraryNetPath_BlkLst
                                else: #check if we are at a whitelist queried data_list_pos
                                    item_isBlackListed=get_isItemBlacklisted(the_dict,item,LibraryID_WhtLst,LibraryNetPath_WhtLst,LibraryPath_WhtLst,library_matching_behavior,
                                                                                    user_bllib_keys_json[currentPosition],user_bllib_netpath_json[currentPosition],user_bllib_path_json[currentPosition])
                                    isblacklisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryId']=LibraryID_WhtLst
                                    isblacklisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryPath']=LibraryPath_WhtLst
                                    isblacklisted_extraInfo_byUserId_Media[user_key][item['Id']]['WhitelistBlacklistLibraryNetPath']=LibraryNetPath_WhtLst

                                isBlackListed_Display=item_isBlackListed

                                #blacklist behavior enabled
                                isblacklisted_and_played_byUserId_Media,isblacklisted_extraInfo_byUserId_Media=parse_actionedConfigurationBehavior(the_dict,item,isblacklisted_extraInfo_byUserId_Media,user_key,'blacklisted',isblacklisted_and_played_byUserId_Media,blacklisted_behavior_media,item_isBlackListed,item_matches_played_days_filter,item_matches_played_count_filter,item_matches_created_days_filter,item_matches_created_played_count_filter,itemIsPlayed,itemPlayedCount)

##########################################################################################################################################

                                #Decide how to handle the fav_local, fav_adv, whitetag, blacktag, whitelist, and blacklist flags
                                showItemAsDeleted=get_singleUserDeleteStatus(the_dict,item_matches_played_count_filter,item_matches_played_days_filter,item_matches_created_played_count_filter,item_matches_created_days_filter,item_isFavorited,item_isFavorited_Advanced,item_isWhiteTagged,item_isBlackTagged,item_isWhiteListed,item_isBlackListed)

##########################################################################################################################################

                                #Only applies to episodes; prep for minimum number and minimum played number of episodes
                                if (minimum_number_episodes or minimum_number_played_episodes):
                                    #Get seriesId and compare it to what the episode thinks its seriesId is
                                    series_info = get_SERIES_itemInfo(item,user_key,the_dict)
                                    if ((not ('SeriesId' in item)) or (not (item['SeriesId'] == series_info['Id']))):
                                        if (series_info):
                                            item['SeriesId']=series_info['Id']

                                    if not (item['SeriesId'] in mediaCounts_byUserId[user_key]):
                                        RecursiveItemCount=int(series_info['RecursiveItemCount'])
                                        UnplayedItemCount=int(series_info['UserData']['UnplayedItemCount'])
                                        PlayedEpisodeCount=RecursiveItemCount - UnplayedItemCount

                                    if not ('TotalEpisodeCount' in mediaCounts_byUserId[user_key][item['SeriesId']]):
                                        mediaCounts_byUserId[user_key][item['SeriesId']]['TotalEpisodeCount']=RecursiveItemCount
                                    if not ('UnplayedEpisodeCount' in mediaCounts_byUserId[user_key][item['SeriesId']]):
                                        mediaCounts_byUserId[user_key][item['SeriesId']]['UnplayedEpisodeCount']=UnplayedItemCount
                                    if not ('PlayedEpisodeCount' in mediaCounts_byUserId[user_key][item['SeriesId']]):
                                        mediaCounts_byUserId[user_key][item['SeriesId']]['PlayedEpisodeCount']=PlayedEpisodeCount

##########################################################################################################################################

                                #Build output state dictionary
                                output_state_dict={'isFavorited_Display':isFavorited_Display,
                                                    'isWhiteTagged_Display':isWhiteTagged_Display,
                                                    'isBlackTagged_Display':isBlackTagged_Display,
                                                    'isWhiteListed_Display':isWhiteListed_Display,
                                                    'isBlackListed_Display':isBlackListed_Display,
                                                    'showItemAsDeleted':showItemAsDeleted,
                                                    'print_media_delete_info':print_media_delete_info,
                                                    'print_media_keep_info':print_media_keep_info,
                                                    'media_delete_info_format':media_delete_info_format,
                                                    'media_keep_info_format':media_keep_info_format}

                                #Build and display media item output details for currently processing user
                                if (mediaType.casefold() == 'episode'):
                                    build_print_media_item_details(the_dict,item,mediaType,output_state_dict,get_days_since_played(item['UserData']['LastPlayedDate'],the_dict),get_days_since_created(item['DateCreated'],the_dict),get_season_episode(item['ParentIndexNumber'],item['IndexNumber'],the_dict))
                                else:
                                    build_print_media_item_details(the_dict,item,mediaType,output_state_dict,get_days_since_played(item['UserData']['LastPlayedDate'],the_dict),get_days_since_created(item['DateCreated'],the_dict))

##########################################################################################################################################

                            #Add media item Id to tracking list so it is not processed more than once
                            user_processed_itemsId.add(item['Id'])

                    data_list_pos += 1

            currentSubPosition += 1

############# End Media #############

    #if (the_dict['DEBUG']):
        #print_common_delete_keep_info=True
        #appendTo_DEBUG_log("\n",1,the_dict)
    print_byType(the_dict['console_separator_'],print_common_delete_keep_info,the_dict,the_dict['user_header_format'])

    media_dict[user_key]['deleteItems_Media']=deleteItems_Media
    media_dict[user_key]['deleteItemsIdTracker_Media']=deleteItemsIdTracker_Media
    media_dict[user_key]['deleteItems_createdMedia']=deleteItems_createdMedia
    media_dict[user_key]['deleteItemsIdTracker_createdMedia']=deleteItemsIdTracker_createdMedia
    media_dict[user_key]['isblacklisted_and_played_byUserId_Media']=isblacklisted_and_played_byUserId_Media
    media_dict[user_key]['isblacklisted_extraInfo_byUserId_Media']=isblacklisted_extraInfo_byUserId_Media
    media_dict[user_key]['iswhitelisted_and_played_byUserId_Media']=iswhitelisted_and_played_byUserId_Media
    media_dict[user_key]['iswhitelisted_extraInfo_byUserId_Media']=iswhitelisted_extraInfo_byUserId_Media
    media_dict[user_key]['isblacktagged_and_played_byUserId_Media']=isblacktagged_and_played_byUserId_Media
    media_dict[user_key]['isblacktagged_extraInfo_byUserId_Media']=isblacktagged_extraInfo_byUserId_Media
    media_dict[user_key]['iswhitetagged_and_played_byUserId_Media']=iswhitetagged_and_played_byUserId_Media
    media_dict[user_key]['iswhitetagged_extraInfo_byUserId_Media']=iswhitetagged_extraInfo_byUserId_Media
    media_dict[user_key]['isfavorited_and_played_byUserId_Media']=isfavorited_and_played_byUserId_Media
    media_dict[user_key]['isfavorited_extraInfo_byUserId_Media']=isfavorited_extraInfo_byUserId_Media
    media_dict[user_key]['mediaCounts_byUserId']=mediaCounts_byUserId

    media_returns['media_dict']=media_dict
    media_returns['media_found']=media_found

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
        #movie_dict,movie_found=get_media_items('movie',the_dict,movie_dict,user_key)
        movie_returns=get_media_items('movie',the_dict,movie_dict,user_key,movie_returns)
        #query the server for episode media items
        #episode_dict,episode_found=get_media_items('episode',the_dict,episode_dict,user_key)
        episode_returns=get_media_items('episode',the_dict,episode_dict,user_key,episode_returns)
        #query the server for audio media items
        #audio_dict,audio_found=get_media_items('audio',the_dict,audio_dict,user_key)
        audio_returns=get_media_items('audio',the_dict,audio_dict,user_key,audio_returns)
        #query the server for audiobook media items
         #audioBook media type only applies to jellyfin
         #Jellyfin sets audiobooks to a media type of audioBook
         #Emby sets audiobooks to a media type of audio (see audio section)
        #audiobook_dict,audiobook_found=get_media_items('audiobook',the_dict,audiobook_dict,user_key)
        audiobook_returns=get_media_items('audiobook',the_dict,audiobook_dict,user_key,audiobook_returns)
 
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

        the_dict['currentPosition']+=1

        media_found=(movie_found or episode_found or audio_found or audiobook_found)

        if not (the_dict['all_media_disabled']):
            if not (media_found):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n",1,the_dict)
                print_byType('[NO PLAYED, WHITELISTED, OR TAGGED MEDIA ITEMS]\n',the_dict['print_script_warning'],the_dict)

    return movie_dict,episode_dict,audio_dict,audiobook_dict
'''


def getMedia(the_dict):

    movie_dict={}
    episode_dict={}
    audio_dict={}
    audiobook_dict={}

    #Get items that could be ready for deletion
    for user_key in the_dict['user_keys_json']:
        movie_dict[user_key]={}
        episode_dict[user_key]={}
        audio_dict[user_key]={}
        audiobook_dict[user_key]={}

        print_user_header(user_key,the_dict)

        #when debug is disabled and no media delete/keep items are being output to the console; allow multiprocessing
        if (
           (not (the_dict['DEBUG'])) and
           ((not (the_dict['print_movie_delete_info'] or the_dict['print_movie_keep_info'])) and
           (not (the_dict['print_episode_delete_info'] or the_dict['print_episode_keep_info'])) and
           (not (the_dict['print_audio_delete_info'] or the_dict['print_audio_keep_info'])) and
           ((isEmbyServer(the_dict['server_brand'])) or
           (isJellyfinServer(the_dict['server_brand']) and
           (not (the_dict['print_audiobook_delete_info'] or the_dict['print_audiobook_keep_info'])))))
           ):

            #print('Start Get Media: ' + datetime.now().strftime('%Y%m%d%H%M%S'))

            movie_returns=multiprocessing.Manager().dict()
            episode_returns=multiprocessing.Manager().dict()
            audio_returns=multiprocessing.Manager().dict()
            audiobook_returns=multiprocessing.Manager().dict()

            #prepare for post processing; return dictionary of lists of media items to be deleted
            #setup for multiprocessing of the post processing of each media type
            mpp_movieGetMedia=multiprocessing.Process(target=get_media_items,args=('movie',the_dict,movie_dict,user_key,movie_returns))
            mpp_episodeGetMedia=multiprocessing.Process(target=get_media_items,args=('episode',the_dict,episode_dict,user_key,episode_returns))
            mpp_audioGetMedia=multiprocessing.Process(target=get_media_items,args=('audio',the_dict,audio_dict,user_key,audio_returns))
            mpp_audiobookGetMedia=multiprocessing.Process(target=get_media_items,args=('audiobook',the_dict,audiobook_dict,user_key,audiobook_returns))

            #start all multi processes
            #order intentially: Audio, Episodes, Movies, Audiobooks
            mpp_audioGetMedia.start(),mpp_episodeGetMedia.start(),mpp_movieGetMedia.start(),mpp_audiobookGetMedia.start()
            mpp_audioGetMedia.join(), mpp_episodeGetMedia.join(), mpp_movieGetMedia.join(), mpp_audiobookGetMedia.join()
            mpp_audioGetMedia.close(),mpp_episodeGetMedia.close(),mpp_movieGetMedia.close(),mpp_audiobookGetMedia.close()

            #print('Stop Get Media: ' + datetime.now().strftime('%Y%m%d%H%M%S'))
        else: ##when debug is enabled or any media delete/keep items are being output to the console; do not allow multiprocessing
            movie_returns={}
            episode_returns={}
            audio_returns={}
            audiobook_returns={}

            #query the server for movie media items
            movie_returns=get_media_items('movie',the_dict,movie_dict,user_key,movie_returns)
            #query the server for episode media items
            episode_returns=get_media_items('episode',the_dict,episode_dict,user_key,episode_returns)
            #query the server for audio media items
            audio_returns=get_media_items('audio',the_dict,audio_dict,user_key,audio_returns)
            #query the server for audiobook media items
            #audioBook media type only applies to jellyfin
            #Jellyfin sets audiobooks to a media type of audioBook
            #Emby sets audiobooks to a media type of audio (see audio section)
            audiobook_returns=get_media_items('audiobook',the_dict,audiobook_dict,user_key,audiobook_returns)

        #if (movie_returns):
        movie_dict.update(movie_returns['media_dict'])
        movie_found=movie_returns['media_found']
        #if (episode_returns):
        episode_dict.update(episode_returns['media_dict'])
        episode_found=episode_returns['media_found']
        #if (audio_returns):
        audio_dict.update(audio_returns['media_dict'])
        audio_found=audio_returns['media_found']
        #if (audiobook_returns):
        audiobook_dict.update(audiobook_returns['media_dict'])
        audiobook_found=audiobook_returns['media_found']
 
        if (isEmbyServer(the_dict['server_brand'])):
            audiobook_found=False

        the_dict['currentPosition']+=1

        media_found=(movie_found or episode_found or audio_found or audiobook_found)

        if not (the_dict['all_media_disabled']):
            if not (media_found):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n",1,the_dict)
                print_byType('[NO PLAYED, WHITELISTED, OR TAGGED MEDIA ITEMS]\n',the_dict['print_script_warning'],the_dict,the_dict['script_warnings_format'])

    return movie_dict,episode_dict,audio_dict,audiobook_dict