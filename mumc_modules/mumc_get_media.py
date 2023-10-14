#!/usr/bin/env python3
import multiprocessing
from datetime import timedelta
from collections import defaultdict
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType
from mumc_modules.mumc_favorited import get_isMOVIE_Fav,get_isMOVIE_AdvancedFav,get_isEPISODE_Fav,get_isEPISODE_AdvancedFav,get_isAUDIO_Fav,get_isAUDIO_AdvancedFav,get_isAUDIOBOOK_Fav,get_isAUDIOBOOK_AdvancedFav
from mumc_modules.mumc_tagged import get_isMOVIE_Tagged,get_isEPISODE_Tagged,get_isAUDIO_Tagged,get_isAUDIOBOOK_Tagged
from mumc_modules.mumc_blacklist_whitelist import get_isItemWhitelisted_Blacklisted
from mumc_modules.mumc_prepare_item import prepare_MOVIEoutput,prepare_EPISODEoutput,prepare_AUDIOoutput,prepare_AUDIOBOOKoutput
from mumc_modules.mumc_console_info import build_print_media_item_details,print_user_header
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_played_created import get_playedCreatedDays_playedCreatedCounts
from mumc_modules.mumc_item_info import get_SERIES_itemInfo
from mumc_modules.mumc_get_watched import init_blacklist_watched_query,init_whitelist_watched_query,blacklist_watched_query,whitelist_watched_query
from mumc_modules.mumc_get_blacktagged import init_blacklist_blacktagged_query,init_whitelist_blacktagged_query,blacklist_blacktagged_query,whitelist_blacktagged_query
from mumc_modules.mumc_get_whitetagged import init_blacklist_whitetagged_query,init_whitelist_whitetagged_query,blacklist_whitetagged_query,whitelist_whitetagged_query
from mumc_modules.mumc_get_favorited import init_blacklist_favorited_query,init_whitelist_favorited_query,blacklist_favorited_query,whitelist_favorited_query


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

    isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingAction']=item_isActioned
    isactioned_extra_byUserId[user_key][item['Id']]['itemIsPlayed']=itemIsPlayed
    isactioned_extra_byUserId[user_key][item['Id']]['itemPlayedCount']=itemPlayedCount
    isactioned_extra_byUserId[user_key][item['Id']]['item_matches_played_days_filter']=item_matches_played_days_filter
    isactioned_extra_byUserId[user_key][item['Id']]['item_matches_played_count_filter']=item_matches_played_count_filter
    isactioned_extra_byUserId[user_key][item['Id']]['item_matches_created_days_filter']=item_matches_created_days_filter
    isactioned_extra_byUserId[user_key][item['Id']]['item_matches_created_played_count_filter']=item_matches_created_played_count_filter

    isactioned_extra_byUserId[user_key][item['Id']]['IsMeetingPlayedFilter']=(item_matches_played_days_filter and item_matches_played_count_filter)

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

    var_dict['advFav_media']={}
    var_dict['advFav_media']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['favorited']['extra']

    if (var_dict['media_type_lower'] == 'episode'):
        var_dict['minimum_number_episodes']=the_dict['advanced_settings']['episode_control']['minimum_episodes']
        var_dict['minimum_number_played_episodes']=the_dict['advanced_settings']['episode_control']['minimum_played_episodes']
    else:
        var_dict['minimum_number_episodes']=0
        var_dict['minimum_number_played_episodes']=0

    var_dict['media_query_favorited']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['favorited']
    var_dict['media_query_whitetagged']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['whitetagged']
    var_dict['media_query_blacktagged']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['blacktagged']
    var_dict['media_query_whitelisted']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['whitelisted']
    var_dict['media_query_blacklisted']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['blacklisted']

    #Determine played or created time; UTC time used for media items; determine played and created date for each media type
    var_dict['cut_off_date_played_media']=the_dict['cut_off_date_played_media'][var_dict['media_type_lower']]
    var_dict['cut_off_date_created_media']=the_dict['cut_off_date_created_media'][var_dict['media_type_lower']]

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
    #var_dict['deleteItems_Media']=[]
    #var_dict['deleteItemsIdTracker_Media']=[]
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

    var_dict['whitelist_length'] = sum(1 for _ in user_info['whitelist'])
    var_dict['blacklist_length'] = sum(1 for _ in user_info['blacklist'])
    if (var_dict['whitelist_length'] > var_dict['blacklist_length']):
        var_dict['shortest_list_length']=var_dict['blacklist_length']
        var_dict['list_diff']=var_dict['whitelist_length'] - var_dict['blacklist_length']
        #longest_list='whitelist'
        var_dict['shortest_list']='blacklist'
    elif (var_dict['blacklist_length'] > var_dict['whitelist_length']):
        var_dict['shortest_list_length']=var_dict['whitelist_length']
        var_dict['list_diff']=var_dict['blacklist_length'] - var_dict['whitelist_length']
        #longest_list='blacklist'
        var_dict['shortest_list']='whitelist'
    else:
        var_dict['shortest_list_length']=0
        var_dict['list_diff']=0
        #longest_list=''
        var_dict['shortest_list']='whitelist'

    for listlen in range(var_dict['list_diff']):
        user_info[var_dict['shortest_list']].insert((var_dict['shortest_list_length']+listlen),{'lib_id':None,'collection_type':None,'path':None,'network_path':None,'lib_enabled':False})

    var_dict['media_found']=False

############# Media #############

    if ((var_dict['media_played_days'] >= 0) or (var_dict['media_created_days'] >= 0)):

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nProcessing " + var_dict['media_type_upper'] + " Items For UserId: " + str(user_info['user_id']),2,the_dict)

        var_dict['user_processed_item_Ids']=set()

        for var_dict['this_whitelist_lib'],var_dict['this_blacklist_lib'] in zip (user_info['whitelist'],user_info['blacklist']):

            var_dict=init_blacklist_favorited_query(var_dict)
            var_dict=init_whitelist_favorited_query(var_dict)
            var_dict=init_blacklist_whitetagged_query(var_dict)
            var_dict=init_whitelist_whitetagged_query(var_dict)
            var_dict=init_blacklist_blacktagged_query(var_dict)
            var_dict=init_whitelist_blacktagged_query(var_dict)
            var_dict=init_blacklist_watched_query(var_dict,the_dict)
            var_dict=init_whitelist_watched_query(var_dict,the_dict)

            var_dict['QueryItemsRemaining_All']=True

            while (var_dict['QueryItemsRemaining_All']):

                var_dict=blacklist_favorited_query(user_info,var_dict,the_dict)
                var_dict=whitelist_favorited_query(user_info,var_dict,the_dict)
                var_dict=blacklist_whitetagged_query(user_info,var_dict,the_dict)
                var_dict=whitelist_whitetagged_query(user_info,var_dict,the_dict)
                var_dict=blacklist_blacktagged_query(user_info,var_dict,the_dict)
                var_dict=whitelist_blacktagged_query(user_info,var_dict,the_dict)
                var_dict=blacklist_watched_query(user_info,var_dict,the_dict)
                var_dict=whitelist_watched_query(user_info,var_dict,the_dict)

                #Combine dictionaries into list of dictionaries
                #Order here is important
                var_dict['data_lists']=[var_dict['data_Favorited_From_Whitelist'], #0
                                        var_dict['data_Child_Of_Favorited_Item_From_Whitelist'], #1
                                        var_dict['data_Whitetagged_From_Whitelist'], #2
                                        var_dict['data_Child_Of_Whitetagged_From_Whitelist'], #3
                                        var_dict['data_Blacktagged_From_Whitelist'], #4
                                        var_dict['data_Child_Of_Blacktagged_From_Whitelist'], #5
                                        var_dict['data_Favorited_From_Blacklist'], #6APIDebugMsg_Whitetag_From_Blacklist_Child
                                        var_dict['data_Child_Of_Favorited_Item_From_Blacklist'], #7
                                        var_dict['data_Whitetagged_From_Blacklist'], #8
                                        var_dict['data_Child_Of_Whitetagged_From_Blacklist'], #9
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

                            #Save lib_id for each media item; needed during post processing
                            item['mumc']={}
                            item['mumc']['lib_id']=var_dict['data_dict']['lib_id']
                            item['mumc']['path']=var_dict['data_dict']['path']
                            item['mumc']['network_path']=var_dict['data_dict']['network_path']

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
                                    item=prepare_MOVIEoutput(the_dict,item,user_info,var_dict)
                                elif (var_dict['media_type_lower'] == 'episode'):
                                    item=prepare_EPISODEoutput(the_dict,item,user_info,var_dict)
                                elif (var_dict['media_type_lower'] == 'audio'):
                                    item=prepare_AUDIOoutput(the_dict,item,user_info,var_dict)
                                elif (var_dict['media_type_lower'] == 'audiobook'):
                                    item=prepare_AUDIOBOOKoutput(the_dict,item,user_info,var_dict)

                                var_dict['isfavorited_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
                                var_dict['iswhitetagged_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
                                var_dict['isblacktagged_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
                                var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
                                var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}

##########################################################################################################################################

                                #Determine if item meets played days, created days, played counts, and played-created counts
                                var_dict.update(get_playedCreatedDays_playedCreatedCounts(the_dict,item,var_dict))

##########################################################################################################################################

                                #If item meets created days filter, create-played days count, and created-played inequality then save for post-processing
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
                                        var_dict['item_isFavorited']=get_isAUDIO_Fav(the_dict,item,user_info,var_dict)
                                    elif (var_dict['media_type_lower'] == 'audiobook'):
                                        var_dict['item_isFavorited']=get_isAUDIOBOOK_Fav(the_dict,item,user_info,var_dict)

                                #Get if media item is set as an advanced favorite
                                var_dict['item_isFavorited_Advanced']=False
                                if (var_dict['favorited_behavior_media']['action_control'] and (any(var_dict['advFav_media']) > 0)):
                                    if (var_dict['media_type_lower'] == 'movie'):
                                        var_dict['item_isFavorited_Advanced']=get_isMOVIE_AdvancedFav(the_dict,item,user_info,var_dict)
                                    elif (var_dict['media_type_lower'] == 'episode'):
                                        var_dict['item_isFavorited_Advanced']=get_isEPISODE_AdvancedFav(the_dict,item,user_info,var_dict)
                                    elif (var_dict['media_type_lower'] == 'audio'):
                                        var_dict['item_isFavorited_Advanced']=get_isAUDIO_AdvancedFav(the_dict,item,user_info,var_dict)
                                    elif (var_dict['media_type_lower'] == 'audiobook'):
                                        var_dict['item_isFavorited_Advanced']=get_isAUDIOBOOK_AdvancedFav(the_dict,item,user_info,var_dict)

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
                                    var_dict['item_isWhitelisted']=get_isItemWhitelisted_Blacklisted('whitelist',item,user_info,the_dict)
                                    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryId']=var_dict['this_whitelist_lib']['lib_id']
                                    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryPath']=var_dict['this_whitelist_lib']['path']
                                    var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryNetPath']=var_dict['this_whitelist_lib']['network_path']
                                else: #check if we are at a blacklist queried var_dict['data_list_pos']
                                    var_dict['item_isWhitelisted']=get_isItemWhitelisted_Blacklisted('whitelist',item,user_info,the_dict)
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
                                    var_dict['item_isBlacklisted']=get_isItemWhitelisted_Blacklisted('blacklist',item,user_info,the_dict)
                                    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryId']=var_dict['this_blacklist_lib']['lib_id']
                                    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryPath']=var_dict['this_blacklist_lib']['path']
                                    var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]['WhitelistBlacklistLibraryNetPath']=var_dict['this_blacklist_lib']['network_path']
                                else: #check if we are at a whitelist queried var_dict['data_list_pos']
                                    var_dict['item_isBlacklisted']=get_isItemWhitelisted_Blacklisted('blacklist',item,user_info,the_dict)
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

                                #Build and display media item output details for currently processing user
                                build_print_media_item_details(item,var_dict,the_dict)

##########################################################################################################################################

                            #Add media item Id to tracking list so it is not processed more than once
                            var_dict['user_processed_item_Ids'].add(item['Id'])

                    var_dict['data_list_pos'] += 1

############# End Media #############

    print_byType(the_dict['console_separator_'],the_dict['advanced_settings']['console_controls']['headers']['user']['show'],the_dict,the_dict['advanced_settings']['console_controls']['headers']['user']['formatting'])

    #the_dict[var_dict['media_dict_str']][user_info['user_id']]['deleteItems_Media']=var_dict['deleteItems_Media']
    #the_dict[var_dict['media_dict_str']][user_info['user_id']]['deleteItemsIdTracker_Media']=var_dict['deleteItemsIdTracker_Media']
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

    media_returns['media_dict']=the_dict[var_dict['media_dict_str']]
    media_returns['media_found']=var_dict['media_found']

    return media_returns


def init_getMedia(the_dict):

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

    the_dict['currentUserPosition']=0

    #Get items that could be ready for deletion
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

    return the_dict