import copy
import uuid
import multiprocessing
from datetime import timedelta
from collections import defaultdict
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType,convert2json
from mumc_modules.mumc_favorited import get_isMOVIE_Fav,get_isMOVIE_AdvancedFav,get_isEPISODE_Fav,get_isEPISODE_AdvancedFav,get_isAUDIO_Fav,get_isAUDIO_AdvancedFav,get_isAUDIOBOOK_Fav,get_isAUDIOBOOK_AdvancedFav
from mumc_modules.mumc_tagged import get_isMOVIE_Tagged,get_isEPISODE_Tagged,get_isAUDIO_Tagged,get_isAUDIOBOOK_Tagged,addTags_To_mediaItem
from mumc_modules.mumc_blacklist_whitelist import get_isItemWhitelisted_Blacklisted
from mumc_modules.mumc_prepare_item import prepare_MOVIEoutput,prepare_EPISODEoutput,prepare_AUDIOoutput,prepare_AUDIOBOOKoutput
from mumc_modules.mumc_console_info import build_print_media_item_details,print_user_header
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_played_created import get_playedDays_createdPlayedDays_playedCounts_createdPlayedCounts
from mumc_modules.mumc_item_info import get_SERIES_itemInfo
#from mumc_modules.mumc_get_watched import init_blacklist_watched_query2,init_whitelist_watched_query2,blacklist_watched_query2,whitelist_watched_query2
#from mumc_modules.mumc_get_blacktagged import init_blacklist_blacktagged_query2,init_whitelist_blacktagged_query2,blacklist_blacktagged_query2,whitelist_blacktagged_query2
#from mumc_modules.mumc_get_whitetagged import init_blacklist_whitetagged_query2,init_whitelist_whitetagged_query2,blacklist_whitetagged_query2,whitelist_whitetagged_query2
#from mumc_modules.mumc_get_favorited import init_blacklist_favorited_query2,init_whitelist_favorited_query2,blacklist_favorited_query2,whitelist_favorited_query2
from mumc_modules.mumc_get_watched2 import init_blacklist_watched_query2,init_whitelist_watched_query2,blacklist_watched_query2,whitelist_watched_query2
from mumc_modules.mumc_get_blacktagged2 import init_blacklist_blacktagged_query2,init_whitelist_blacktagged_query2,blacklist_blacktagged_query2,whitelist_blacktagged_query2
from mumc_modules.mumc_get_whitetagged2 import init_blacklist_whitetagged_query2,init_whitelist_whitetagged_query2,blacklist_whitetagged_query2,whitelist_whitetagged_query2
from mumc_modules.mumc_get_favorited2 import init_blacklist_favorited_query2,init_whitelist_favorited_query2,blacklist_favorited_query2,whitelist_favorited_query2
from mumc_modules.mumc_user_queries import get_single_user
from mumc_modules.mumc_configuration_yaml import filterYAMLConfigKeys_ToKeep
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo
from mumc_modules.mumc_post_process2 import init_postProcessing2
from mumc_modules.mumc_sort2 import sortDeleteLists2
from mumc_modules.mumc_delete import print_and_delete_items


#Determine if item can be monitored
def get_isItemMonitored2(mediasource,the_dict):
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
def parse_actionedConfigurationBehavior2(theActionType,item,user_info,var_dict,the_dict):

    if (theActionType == 'favorited'):
        #isactioned_extra_byUserId=var_dict['isfavorited_extraInfo_byUserId_Media']
        isactioned_extra_byUserId={}
        isactioned_extra_byUserId[item['Id']]={}
        #user_key=user_info['user_id']
        action_behavior=var_dict['favorited_behavior_media']
        item_isActioned=(var_dict['item_isFavorited'] or var_dict['item_isFavorited_Advanced'])
    elif (theActionType == 'whitetagged'):
        #isactioned_extra_byUserId=var_dict['iswhitetagged_extraInfo_byUserId_Media']
        isactioned_extra_byUserId={}
        isactioned_extra_byUserId[item['Id']]={}
        #user_key=user_info['user_id']
        action_behavior=var_dict['whitetagged_behavior_media']
        item_isActioned=var_dict['item_isWhitetagged']
    elif (theActionType == 'blacktagged'):
        #isactioned_extra_byUserId=var_dict['isblacktagged_extraInfo_byUserId_Media']
        isactioned_extra_byUserId={}
        isactioned_extra_byUserId[item['Id']]={}
        #user_key=user_info['user_id']
        action_behavior=var_dict['blacktagged_behavior_media']
        item_isActioned=var_dict['item_isBlacktagged']
    elif (theActionType == 'whitelisted'):
        #isactioned_extra_byUserId=var_dict['iswhitelisted_extraInfo_byUserId_Media']
        isactioned_extra_byUserId={}
        isactioned_extra_byUserId[item['Id']]={}
        #user_key=user_info['user_id']
        action_behavior=var_dict['whitelisted_behavior_media']
        item_isActioned=var_dict['item_isWhitelisted']
    elif (theActionType == 'blacklisted'):
        #isactioned_extra_byUserId=var_dict['isblacklisted_extraInfo_byUserId_Media']
        isactioned_extra_byUserId={}
        isactioned_extra_byUserId[item['Id']]={}
        #user_key=user_info['user_id']
        action_behavior=var_dict['blacklisted_behavior_media']
        item_isActioned=var_dict['item_isBlacklisted']
    else: #(theActionType == 'unknown'):
        #generate error
        pass

    item_matches_played_days_filter=var_dict['item_matches_played_days_filter']
    item_matches_played_count_filter=var_dict['item_matches_played_count_filter']
    item_matches_created_days_filter=var_dict['item_matches_created_days_filter']
    item_matches_created_played_count_filter=var_dict['item_matches_created_played_count_filter']

    #isactioned_extra_byUserId[item['Id']]={}

    isactioned_extra_byUserId[item['Id']]['IsMeetingAction']=item_isActioned

    isactioned_extra_byUserId[item['Id']]['IsMeetingPlayedFilter']=(item_matches_played_days_filter and item_matches_played_count_filter)

    isactioned_extra_byUserId[item['Id']]['IsMeetingCreatedPlayedFilter']=(item_matches_created_days_filter and item_matches_created_played_count_filter)

    if (not ((item['Id'] in var_dict['deleteItemsIdTracker_Media']) or (item['Id'] in var_dict['deleteItemsIdTracker_createdMedia']))):
        var_dict['media_data'][item['Id']]=filterYAMLConfigKeys_ToKeep(item,*var_dict['itemKeyFilter'])
        var_dict['deleteItemsIdTracker_Media'].append(item['Id'])

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nIsMeetingAction=" + str(isactioned_extra_byUserId[item['Id']]['IsMeetingAction']),3,the_dict)
        appendTo_DEBUG_log("\nIsMeetingPlayedFilter=" + str(isactioned_extra_byUserId[item['Id']]['IsMeetingPlayedFilter']),3,the_dict)
        appendTo_DEBUG_log("\nItemId=" + str(item['Id']),3,the_dict)

    return_dict={}

    if (theActionType == 'favorited'):
        return_dict['isfavorited_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    elif (theActionType == 'whitetagged'):
        return_dict['iswhitetagged_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    elif (theActionType == 'blacktagged'):
        return_dict['isblacktagged_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    elif (theActionType == 'whitelisted'):
        return_dict['iswhitelisted_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    elif (theActionType == 'blacklisted'):
        return_dict['isblacklisted_extraInfo_byUserId_Media']=isactioned_extra_byUserId
    else: #(theActionType == 'unknown'):
        #generate error
        pass

    return return_dict


#decide if this item is ok to be deleted; still has to meet other criteria
def get_singleUserDeleteStatus2(var_dict,the_dict):

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


def preProcessing(item,user_info,var_dict,the_dict):

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

##########################################################################################################################################

    #var_dict['isfavorited_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
    #var_dict['iswhitetagged_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
    #var_dict['isblacktagged_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
    #var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}
    #var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']][item['Id']]={}

    var_dict[user_info['user_id']]['isfavorited_extraInfo_byUserId_Media']={}
    var_dict[user_info['user_id']]['iswhitetagged_extraInfo_byUserId_Media']={}
    var_dict[user_info['user_id']]['isblacktagged_extraInfo_byUserId_Media']={}
    var_dict[user_info['user_id']]['iswhitelisted_extraInfo_byUserId_Media']={}
    var_dict[user_info['user_id']]['isblacklisted_extraInfo_byUserId_Media']={}

    var_dict[user_info['user_id']]['isfavorited_extraInfo_byUserId_Media'][item['Id']]={}
    var_dict[user_info['user_id']]['iswhitetagged_extraInfo_byUserId_Media'][item['Id']]={}
    var_dict[user_info['user_id']]['isblacktagged_extraInfo_byUserId_Media'][item['Id']]={}
    var_dict[user_info['user_id']]['iswhitelisted_extraInfo_byUserId_Media'][item['Id']]={}
    var_dict[user_info['user_id']]['isblacklisted_extraInfo_byUserId_Media'][item['Id']]={}

##########################################################################################################################################

    #Determine if item meets played days, created days, played counts, and played-created counts
    var_dict.update(get_playedDays_createdPlayedDays_playedCounts_createdPlayedCounts(the_dict,item,var_dict))

##########################################################################################################################################

    #If item meets created days filter, create-played days count, and created-played inequality then save for post-processing
    if (var_dict['item_matches_created_days_filter'] and var_dict['item_matches_created_played_count_filter']):
        if (not ((item['Id'] in var_dict['deleteItemsIdTracker_Media']) or (item['Id'] in var_dict['deleteItemsIdTracker_createdMedia']))):
            if (var_dict['media_behavioral_control']):
                    var_dict['deleteItemsIdTracker_Media'].append(item['Id'])
                    var_dict['media_data'][item['Id']]=filterYAMLConfigKeys_ToKeep(item,*var_dict['itemKeyFilter'])
            else:
                    var_dict['deleteItemsIdTracker_createdMedia'].append(item['Id'])
                    var_dict['media_data'][item['Id']]=filterYAMLConfigKeys_ToKeep(item,*var_dict['itemKeyFilter'])

##########################################################################################################################################

    var_dict['item_isFavorited']=False
    #Get if media item is set as favorite
    #if (var_dict['data_list_pos'] in var_dict['data_from_favorited_queries']):
        #var_dict['item_isFavorited']=True
    #else:
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
    if (var_dict['favorited_behavior_media']['action_control'] and (any(var_dict['advFav_media'].values()) > 0)):
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
    if (var_dict['item_isFavorited'] or var_dict['item_isFavorited_Advanced']):
        if (not (item['Id'] in var_dict['isfavorited_extraInfo_Tracker'])):
            var_dict['isfavorited_extraInfo_Tracker'].append(item['Id'])
        var_dict[user_info['user_id']].update(parse_actionedConfigurationBehavior2('favorited',item,user_info,var_dict,the_dict))
    #else:
        #var_dict[user_info['user_id']]['isfavorited_extraInfo_byUserId_Media'].pop(item['Id'])

    var_dict[user_info['user_id']]['isfavorited_extraInfo_byUserId_Media'][item['Id']]['CutOffDatePlayed']=var_dict['cut_off_date_played_media']
    var_dict[user_info['user_id']]['isfavorited_extraInfo_byUserId_Media'][item['Id']]['CutOffDateCreated']=var_dict['cut_off_date_created_media']

##########################################################################################################################################

    matched_tags=[]
    var_dict['item_isWhitetagged']=False
    #if (var_dict['data_list_pos'] in var_dict['data_from_whitetagged_queries']):
        #var_dict['item_isWhitetagged']=True
    #elif (not (var_dict['whitetags'] == [])):
    if (var_dict['media_type_lower'] == 'movie'):
        var_dict['item_isWhitetagged'],matched_tags=get_isMOVIE_Tagged(the_dict,item,user_info,var_dict['whitetags'])
    elif (var_dict['media_type_lower'] == 'episode'):
        var_dict['item_isWhitetagged'],matched_tags=get_isEPISODE_Tagged(the_dict,item,user_info,var_dict['whitetags'])
    elif (var_dict['media_type_lower'] == 'audio'):
        var_dict['item_isWhitetagged'],matched_tags=get_isAUDIO_Tagged(the_dict,item,user_info,var_dict['whitetags'])
    elif (var_dict['media_type_lower'] == 'audiobook'):
        var_dict['item_isWhitetagged'],matched_tags=get_isAUDIOBOOK_Tagged(the_dict,item,user_info,var_dict['whitetags'])

    #add matching tags to media_item
    if (matched_tags):
        item=addTags_To_mediaItem(matched_tags,item,the_dict)

    var_dict['isWhitetagged_Display']=var_dict['item_isWhitetagged']

    #whitetag behavior enabled
    if (var_dict['item_isWhitetagged']):
        if (not (item['Id'] in var_dict['iswhitetagged_extraInfo_Tracker'])):
            var_dict['iswhitetagged_extraInfo_Tracker'].append(item['Id'])
        var_dict[user_info['user_id']].update(parse_actionedConfigurationBehavior2('whitetagged',item,user_info,var_dict,the_dict))
    #else:
        #var_dict[user_info['user_id']]['iswhitetagged_extraInfo_byUserId_Media'].pop(item['Id'])

    var_dict[user_info['user_id']]['iswhitetagged_extraInfo_byUserId_Media'][item['Id']]['CutOffDatePlayed']=var_dict['cut_off_date_played_media']
    var_dict[user_info['user_id']]['iswhitetagged_extraInfo_byUserId_Media'][item['Id']]['CutOffDateCreated']=var_dict['cut_off_date_created_media']

##########################################################################################################################################

    matched_tags=[]
    var_dict['item_isBlacktagged']=False
    #if (var_dict['data_list_pos'] in var_dict['data_from_blacktagged_queries']):
        #var_dict['item_isBlacktagged']=True
    #elif (not (var_dict['blacktags'] == [])):
    if (var_dict['media_type_lower'] == 'movie'):
        var_dict['item_isBlacktagged'],matched_tags=get_isMOVIE_Tagged(the_dict,item,user_info,var_dict['blacktags'])
    elif (var_dict['media_type_lower'] == 'episode'):
        var_dict['item_isBlacktagged'],matched_tags=get_isEPISODE_Tagged(the_dict,item,user_info,var_dict['blacktags'])
    elif (var_dict['media_type_lower'] == 'audio'):
        var_dict['item_isBlacktagged'],matched_tags=get_isAUDIO_Tagged(the_dict,item,user_info,var_dict['blacktags'])
    elif (var_dict['media_type_lower'] == 'audiobook'):
        var_dict['item_isBlacktagged'],matched_tags=get_isAUDIOBOOK_Tagged(the_dict,item,user_info,var_dict['blacktags'])

    #add matching tags to media_item
    if (matched_tags):
        item=addTags_To_mediaItem(matched_tags,item,the_dict)

    var_dict['isBlacktagged_Display']=var_dict['item_isBlacktagged']

    #blacktag behavior enabled
    if (var_dict['item_isBlacktagged']):
        if (not (item['Id'] in var_dict['isblacktagged_extraInfo_Tracker'])):
            var_dict['isblacktagged_extraInfo_Tracker'].append(item['Id'])
        var_dict[user_info['user_id']].update(parse_actionedConfigurationBehavior2('blacktagged',item,user_info,var_dict,the_dict))
    #else:
        #var_dict[user_info['user_id']]['isblacktagged_extraInfo_byUserId_Media'].pop(item['Id'])

    var_dict[user_info['user_id']]['isblacktagged_extraInfo_byUserId_Media'][item['Id']]['CutOffDatePlayed']=var_dict['cut_off_date_played_media']
    var_dict[user_info['user_id']]['isblacktagged_extraInfo_byUserId_Media'][item['Id']]['CutOffDateCreated']=var_dict['cut_off_date_created_media']

##########################################################################################################################################

    var_dict['isWhitelisted_Display']=False
    #check if we are at a whitelist queried var_dict['data_list_pos']
    #if (var_dict['data_list_pos'] in var_dict['data_from_whitelisted_queries']):
        #var_dict['item_isWhitelisted']=get_isItemWhitelisted_Blacklisted('whitelist',item,user_info,the_dict)
    #else: #check if we are at a blacklist queried var_dict['data_list_pos']
    var_dict['item_isWhitelisted']=get_isItemWhitelisted_Blacklisted('whitelist',item,user_info,the_dict)

    var_dict['isWhitelisted_Display']=var_dict['item_isWhitelisted']

    #whitelist behavior enabled
    if (var_dict['item_isWhitelisted']):
        if (not (item['Id'] in var_dict['iswhitelisted_extraInfo_Tracker'])):
            var_dict['iswhitelisted_extraInfo_Tracker'].append(item['Id'])
        var_dict[user_info['user_id']].update(parse_actionedConfigurationBehavior2('whitelisted',item,user_info,var_dict,the_dict))
    #else:
        #var_dict[user_info['user_id']]['iswhitelisted_extraInfo_byUserId_Media'].pop(item['Id'])

    var_dict[user_info['user_id']]['iswhitelisted_extraInfo_byUserId_Media'][item['Id']]['CutOffDatePlayed']=var_dict['cut_off_date_played_media']
    var_dict[user_info['user_id']]['iswhitelisted_extraInfo_byUserId_Media'][item['Id']]['CutOffDateCreated']=var_dict['cut_off_date_created_media']

##########################################################################################################################################

    var_dict['isBlacklisted_Display']=False
    #check if we are at a blacklist queried var_dict['data_list_pos']
    #if (var_dict['data_list_pos'] in var_dict['data_from_blacklisted_queries']):
        #var_dict['item_isBlacklisted']=get_isItemWhitelisted_Blacklisted('blacklist',item,user_info,the_dict)
    #else: #check if we are at a whitelist queried var_dict['data_list_pos']
    var_dict['item_isBlacklisted']=get_isItemWhitelisted_Blacklisted('blacklist',item,user_info,the_dict)

    var_dict['isBlacklisted_Display']=var_dict['item_isBlacklisted']

    #blacklist behavior enabled
    if (var_dict['item_isBlacklisted']):
        if (not (item['Id'] in var_dict['isblacklisted_extraInfo_Tracker'])):
            var_dict['isblacklisted_extraInfo_Tracker'].append(item['Id'])
        var_dict[user_info['user_id']].update(parse_actionedConfigurationBehavior2('blacklisted',item,user_info,var_dict,the_dict))
    #else:
        #var_dict[user_info['user_id']]['isblacklisted_extraInfo_byUserId_Media'].pop(item['Id'])

    var_dict[user_info['user_id']]['isblacklisted_extraInfo_byUserId_Media'][item['Id']]['CutOffDatePlayed']=var_dict['cut_off_date_played_media']
    var_dict[user_info['user_id']]['isblacklisted_extraInfo_byUserId_Media'][item['Id']]['CutOffDateCreated']=var_dict['cut_off_date_created_media']

##########################################################################################################################################

    #Decide how to handle the fav_local, fav_adv, whitetag, blacktag, whitelist, and blacklist flags
    var_dict['showItemAsDeleted']=get_singleUserDeleteStatus2(var_dict,the_dict)

##########################################################################################################################################

    #Only applies to episodes; prep for minimum number and minimum played number of episodes
    if (var_dict['minimum_number_episodes'] or var_dict['minimum_number_played_episodes']):
        #Get seriesId and compare it to what the episode thinks its seriesId is
        series_info = get_SERIES_itemInfo(item,user_info,the_dict)
        if ((not ('SeriesId' in item)) or (not (item['SeriesId'] == series_info['Id']))):
            if (series_info):
                item['SeriesId']=series_info['Id']

        #if (not (item['SeriesId'] in var_dict['mediaCounts_byUserId'][user_info['user_id']])):
        if (not (item['SeriesId'] in var_dict['mediaCounts_byUserId'])):
            RecursiveItemCount=int(series_info['RecursiveItemCount'])
            UnplayedItemCount=int(series_info['UserData']['UnplayedItemCount'])
            PlayedEpisodeCount=RecursiveItemCount - UnplayedItemCount

        #if (not ('TotalEpisodeCount' in var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']])):
            #var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']]['TotalEpisodeCount']=RecursiveItemCount
        #if (not ('UnplayedEpisodeCount' in var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']])):
            #var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']]['UnplayedEpisodeCount']=UnplayedItemCount
        #if (not ('PlayedEpisodeCount' in var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']])):
            #var_dict['mediaCounts_byUserId'][user_info['user_id']][item['SeriesId']]['PlayedEpisodeCount']=PlayedEpisodeCount

        if (not ('TotalEpisodeCount' in var_dict['mediaCounts_byUserId'][item['SeriesId']])):
            var_dict['mediaCounts_byUserId'][item['SeriesId']]['TotalEpisodeCount']=RecursiveItemCount
        if (not ('UnplayedEpisodeCount' in var_dict['mediaCounts_byUserId'][item['SeriesId']])):
            var_dict['mediaCounts_byUserId'][item['SeriesId']]['UnplayedEpisodeCount']=UnplayedItemCount
        if (not ('PlayedEpisodeCount' in var_dict['mediaCounts_byUserId'][item['SeriesId']])):
            var_dict['mediaCounts_byUserId'][item['SeriesId']]['PlayedEpisodeCount']=PlayedEpisodeCount

##########################################################################################################################################

    #Build and display media item output details for currently processing user
    build_print_media_item_details(item,var_dict,the_dict)

##########################################################################################################################################

    the_dict[var_dict['media_dict_str']]['media_data']|=var_dict['media_data']
    the_dict[var_dict['media_dict_str']]['deleteItemsIdTracker_Media']=var_dict['deleteItemsIdTracker_Media']
    
    the_dict[var_dict['media_dict_str']]['deleteItemsIdTracker_createdMedia']=list(set(the_dict[var_dict['media_dict_str']]['deleteItemsIdTracker_createdMedia'] + var_dict['deleteItemsIdTracker_createdMedia']))
    the_dict[var_dict['media_dict_str']]['deleteItemsIdTracker_createdMedia'].sort()
    
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['isblacklisted_extraInfo_byUserId_Media']=var_dict[user_info['user_id']]['isblacklisted_extraInfo_byUserId_Media']
    #the_dict[var_dict['media_dict_str']]['isblacklisted_extraInfo_Tracker']+=var_dict['isblacklisted_extraInfo_Tracker']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['iswhitelisted_extraInfo_byUserId_Media']=var_dict[user_info['user_id']]['iswhitelisted_extraInfo_byUserId_Media']
    #the_dict[var_dict['media_dict_str']]['iswhitelisted_extraInfo_Tracker']+=var_dict['iswhitelisted_extraInfo_Tracker']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['isblacktagged_extraInfo_byUserId_Media']=var_dict[user_info['user_id']]['isblacktagged_extraInfo_byUserId_Media']
    #the_dict[var_dict['media_dict_str']]['isblacktagged_extraInfo_Tracker']+=var_dict['isblacktagged_extraInfo_Tracker']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['iswhitetagged_extraInfo_byUserId_Media']=var_dict[user_info['user_id']]['iswhitetagged_extraInfo_byUserId_Media']
    #the_dict[var_dict['media_dict_str']]['iswhitetagged_extraInfo_Tracker']+=var_dict['iswhitetagged_extraInfo_Tracker']
    the_dict[var_dict['media_dict_str']][user_info['user_id']]['isfavorited_extraInfo_byUserId_Media']=var_dict[user_info['user_id']]['isfavorited_extraInfo_byUserId_Media']
    #the_dict[var_dict['media_dict_str']]['isfavorited_extraInfo_Tracker']+=var_dict['isfavorited_extraInfo_Tracker']

    the_dict[var_dict['media_dict_str']][user_info['user_id']]['mediaCounts_byUserId']=var_dict['mediaCounts_byUserId']

    return var_dict


# get played, favorited, and tagged media items
# save media items ready to be deleted
# remove media items with exceptions (i.e. favorited, whitelisted, whitetagged, etc...)
def get_mediaItems2(the_dict,media_type,media_returns):

    deleteItems_dict={}
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

    var_dict['all_whitelists']=the_dict['all_whitelists']
    var_dict['all_blacklists']=the_dict['all_blacklists']

    var_dict['media_played_days']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['played']['condition_days']
    var_dict['media_created_days']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['created']['condition_days']
    var_dict['media_played_count_comparison']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['played']['count_equality']
    var_dict['media_created_played_count_comparison']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['created']['count_equality']
    var_dict['media_played_count']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['played']['count']
    var_dict['media_created_played_count']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['created']['count']
    var_dict['media_behavioral_control']=the_dict['basic_settings']['filter_statements'][var_dict['media_type_lower']]['created']['behavioral_control']
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
    var_dict['favorited_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['favorited']['dynamic_behavior']
    var_dict['whitetagged_behavior_media']={}
    var_dict['whitetagged_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['action']
    var_dict['whitetagged_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['user_conditional']
    var_dict['whitetagged_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['played_conditional']
    var_dict['whitetagged_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['action_control']
    var_dict['whitetagged_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitetagged']['dynamic_behavior']
    var_dict['blacktagged_behavior_media']={}
    var_dict['blacktagged_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['action']
    var_dict['blacktagged_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['user_conditional']
    var_dict['blacktagged_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['played_conditional']
    var_dict['blacktagged_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['action_control']
    var_dict['blacktagged_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacktagged']['dynamic_behavior']
    var_dict['whitelisted_behavior_media']={}
    var_dict['whitelisted_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitelisted']['action']
    var_dict['whitelisted_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitelisted']['user_conditional']
    var_dict['whitelisted_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitelisted']['played_conditional']
    var_dict['whitelisted_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitelisted']['action_control']
    var_dict['whitelisted_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['whitelisted']['dynamic_behavior']
    var_dict['blacklisted_behavior_media']={}
    var_dict['blacklisted_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacklisted']['action']
    var_dict['blacklisted_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacklisted']['user_conditional']
    var_dict['blacklisted_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacklisted']['played_conditional']
    var_dict['blacklisted_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacklisted']['action_control']
    var_dict['blacklisted_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][var_dict['media_type_lower']]['blacklisted']['dynamic_behavior']
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

    var_dict['enable_media_query_whitelisted_favorited']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['whitelisted']['favorited']
    var_dict['enable_media_query_whitelisted_whitetagged']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['whitelisted']['whitetagged']
    var_dict['enable_media_query_whitelisted_blacktagged']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['whitelisted']['blacktagged']
    var_dict['enable_media_query_whitelist_played']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['whitelisted']['played']

    var_dict['enable_media_query_blacklisted_favorited']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['blacklisted']['favorited']
    var_dict['enable_media_query_blacklisted_whitetagged']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['blacklisted']['whitetagged']
    var_dict['enable_media_query_blacklisted_blacktagged']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['blacklisted']['blacktagged']
    var_dict['enable_media_query_blacklisted_played']=the_dict['advanced_settings']['filter_statements'][var_dict['media_type_lower']]['query_filter']['blacklisted']['played']

    #Determine played or created time; UTC time used for media items; determine played and created date for each media type
    var_dict['cut_off_date_played_media']=the_dict['cut_off_date_played_media'][var_dict['media_type_lower']]
    var_dict['cut_off_date_created_media']=the_dict['cut_off_date_created_media'][var_dict['media_type_lower']]

    #dictionary of favortied and played items by userId
    var_dict['isfavorited_extraInfo_byUserId_Media']={}
    var_dict['isfavorited_extraInfo_Tracker']=the_dict[var_dict['media_dict_str']]['isfavorited_extraInfo_Tracker']
    #dictionary of whitetagged items by userId
    var_dict['iswhitetagged_extraInfo_byUserId_Media']={}
    var_dict['iswhitetagged_extraInfo_Tracker']=the_dict[var_dict['media_dict_str']]['iswhitetagged_extraInfo_Tracker']
    #dictionary of blacktagged items by userId
    var_dict['isblacktagged_extraInfo_byUserId_Media']={}
    var_dict['isblacktagged_extraInfo_Tracker']=the_dict[var_dict['media_dict_str']]['isblacktagged_extraInfo_Tracker']
    #dictionary of whitelisted items by userId
    var_dict['iswhitelisted_extraInfo_byUserId_Media']={}
    var_dict['iswhitelisted_extraInfo_Tracker']=the_dict[var_dict['media_dict_str']]['iswhitelisted_extraInfo_Tracker']
    #dictionary of blacklisted items by userId
    var_dict['isblacklisted_extraInfo_byUserId_Media']={}
    var_dict['isblacklisted_extraInfo_Tracker']=the_dict[var_dict['media_dict_str']]['isblacklisted_extraInfo_Tracker']
    #dictionary of media item counts by userId
    var_dict['mediaCounts_byUserId']={}

    #lists of media items
    var_dict['media_data']=the_dict[var_dict['media_dict_str']]['media_data']

    #list of possible played media items by userId
    var_dict['deleteItemsIdTracker_Media']=[]

    #list of possible created media items by userId
    var_dict['deleteItemsIdTracker_createdMedia']=the_dict[var_dict['media_dict_str']]['deleteItemsIdTracker_createdMedia']

    #the tag key is different between Emby and Jellyfin
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        tagKey='TagItems'
    else:
        tagKey='Tags'

    #create filter tuple for item data
    if (var_dict['media_type_lower'] == 'movie'):
        var_dict['itemKeyFilter']=('Name','Id','DateCreated','Path','Genres','IsFolder','Type','Studios','GenreItems','mumc',tagKey)
    elif (var_dict['media_type_lower'] == 'episode'):
        var_dict['itemKeyFilter']=('Name','Id','DateCreated','Path','Genres','IsFolder','Type','Studios','GenreItems','mumc',tagKey,'IndexNumber','ParentIndexNumber','SeriesName','SeriesId','SeasonId','SeriesStudio')
    elif ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
        var_dict['itemKeyFilter']=('Name','Id','DateCreated','Path','Genres','IsFolder','Type','Studios','GenreItems','mumc',tagKey,'IndexNumber','ParentIndexNumber','ArtistItems','AlbumId','AlbumArtist')

    for user_info in the_dict['enabled_users']:
        #dictionary of favortied and played items by userId
        var_dict['isfavorited_extraInfo_byUserId_Media'][user_info['user_id']]={}
        #dictionary of whitetagged items by userId
        var_dict['iswhitetagged_extraInfo_byUserId_Media'][user_info['user_id']]={}
        #dictionary of blacktagged items by userId
        var_dict['isblacktagged_extraInfo_byUserId_Media'][user_info['user_id']]={}
        #dictionary of whitelisted items by userId
        var_dict['iswhitelisted_extraInfo_byUserId_Media'][user_info['user_id']]={}
        #dictionary of blacklisted items by userId
        var_dict['isblacklisted_extraInfo_byUserId_Media'][user_info['user_id']]={}
        #dictionary of media item counts by userId
        #var_dict['mediaCounts_byUserId'][user_info['user_id']]=defaultdict(dict)
        var_dict['mediaCounts_byUserId']={}

    #var_dict['currentUserPosition']=the_dict['currentUserPosition']

    '''
    #var_dict['whitelist_length'] = sum(1 for _ in user_info['whitelist'])
    #var_dict['blacklist_length'] = sum(1 for _ in user_info['blacklist'])
    var_dict['whitelist_length'] = sum(1 for _ in var_dict['all_whitelists'])
    var_dict['blacklist_length'] = sum(1 for _ in var_dict['all_blacklists'])
    if (var_dict['whitelist_length'] > var_dict['blacklist_length']):
        var_dict['shortest_list_length']=var_dict['blacklist_length']
        var_dict['list_diff']=var_dict['whitelist_length'] - var_dict['blacklist_length']
        var_dict['shortest_list']='blacklist'
    elif (var_dict['blacklist_length'] > var_dict['whitelist_length']):
        var_dict['shortest_list_length']=var_dict['whitelist_length']
        var_dict['list_diff']=var_dict['blacklist_length'] - var_dict['whitelist_length']
        var_dict['shortest_list']='whitelist'
    else:
        var_dict['shortest_list_length']=0
        var_dict['list_diff']=0
        var_dict['shortest_list']='whitelist'

    for _ in range(var_dict['list_diff']):
        #user_info[var_dict['shortest_list']].insert((var_dict['shortest_list_length']+listlen),{'lib_id':None,'subfolder_id':None,'collection_type':None,'path':None,'network_path':None,'lib_enabled':False})
        var_dict['all_' + var_dict['shortest_list'] + 's'].append({'lib_id':None,'subfolder_id':None,'collection_type':None,'path':None,'network_path':None,'lib_enabled':False})
        #var_dict['all_' + var_dict['shortest_list'] + 's'].insert((var_dict['shortest_list_length']+listlen),str(uuid.uuid4().hex))
        #var_dict['all_' + var_dict['shortest_list'] + 's'].insert((var_dict['shortest_list_length']+listlen),None)
        #var_dict['all_' + var_dict['shortest_list'] + 's'].append(None)
    '''

    var_dict['media_found']=False

############# Media #############

    if ((var_dict['media_played_days'] >= 0) or (var_dict['media_created_days'] >= 0)):

        #if (the_dict['DEBUG']):
            #appendTo_DEBUG_log("\n\nProcessing " + var_dict['media_type_upper'] + " Items For UserId: " + str(user_info['user_id']),2,the_dict)

        var_dict['user_processed_item_Ids']=set()

        #for var_dict['this_whitelist_lib'],var_dict['this_blacklist_lib'] in zip (user_info['whitelist'],user_info['blacklist']):
        for var_dict['this_whitelist_lib'],var_dict['this_blacklist_lib'] in zip (var_dict['all_whitelists'],var_dict['all_blacklists']):

            '''
            var_dict=init_blacklist_favorited_query2(var_dict)
            var_dict=init_whitelist_favorited_query2(var_dict)
            var_dict=init_blacklist_whitetagged_query2(var_dict)
            var_dict=init_whitelist_whitetagged_query2(var_dict)
            var_dict=init_blacklist_blacktagged_query2(var_dict)
            var_dict=init_whitelist_blacktagged_query2(var_dict)
            var_dict=init_blacklist_watched_query2(var_dict,the_dict)
            var_dict=init_whitelist_watched_query2(var_dict,the_dict)
            '''

            if (the_dict['DEBUG']):
                for user_info in the_dict['enabled_users']:
                    var_dict[user_info['user_id']]={}
                    var_dict=init_blacklist_favorited_query2(user_info,var_dict)
                    var_dict=init_whitelist_favorited_query2(user_info,var_dict)
                    var_dict=init_blacklist_whitetagged_query2(user_info,var_dict)
                    var_dict=init_whitelist_whitetagged_query2(user_info,var_dict)
                    var_dict=init_blacklist_blacktagged_query2(user_info,var_dict)
                    var_dict=init_whitelist_blacktagged_query2(user_info,var_dict)
                    var_dict=init_blacklist_watched_query2(user_info,var_dict,the_dict)
                    var_dict=init_whitelist_watched_query2(user_info,var_dict,the_dict)
            else:
                processesList = []
                for user_info in the_dict['enabled_users']:
                    var_dict[user_info['user_id']]=multiprocessing.Manager().dict()
                    init_single_user_blist_fav_query=multiprocessing.Process(target=init_blacklist_favorited_query2, args=(user_info,var_dict))
                    init_single_user_wlist_fav_query=multiprocessing.Process(target=init_whitelist_favorited_query2, args=(user_info,var_dict))
                    init_single_user_blist_wtag_query=multiprocessing.Process(target=init_blacklist_whitetagged_query2, args=(user_info,var_dict))
                    init_single_user_wlist_wtag_query=multiprocessing.Process(target=init_whitelist_whitetagged_query2, args=(user_info,var_dict))
                    init_single_user_blist_btag_query=multiprocessing.Process(target=init_blacklist_blacktagged_query2, args=(user_info,var_dict))
                    init_single_user_wlist_btag_query=multiprocessing.Process(target=init_whitelist_blacktagged_query2, args=(user_info,var_dict))
                    init_single_user_blist_watch_query=multiprocessing.Process(target=init_blacklist_watched_query2, args=(user_info,var_dict,the_dict))
                    init_single_user_wlist_watch_query=multiprocessing.Process(target=init_whitelist_watched_query2, args=(user_info,var_dict,the_dict))
                    processesList.append(init_single_user_blist_fav_query)
                    processesList.append(init_single_user_wlist_fav_query)
                    processesList.append(init_single_user_blist_wtag_query)
                    processesList.append(init_single_user_wlist_wtag_query)
                    processesList.append(init_single_user_blist_btag_query)
                    processesList.append(init_single_user_wlist_btag_query)
                    processesList.append(init_single_user_blist_watch_query)
                    processesList.append(init_single_user_wlist_watch_query)
                    init_single_user_blist_fav_query.start()
                    init_single_user_wlist_fav_query.start()
                    init_single_user_blist_wtag_query.start()
                    init_single_user_wlist_wtag_query.start()
                    init_single_user_blist_btag_query.start()
                    init_single_user_wlist_btag_query.start()
                    init_single_user_blist_watch_query.start()
                    init_single_user_wlist_watch_query.start()
                for m in processesList:
                    m.join()
                for m in processesList:
                    m.close()

            var_dict['QueryItemsRemaining_All']=True

            while (var_dict['QueryItemsRemaining_All']):

                var_dict['QueryItemsRemaining_All']=False

                #var_dict=blacklist_favorited_query2(user_info,var_dict,the_dict)
                #var_dict=whitelist_favorited_query2(user_info,var_dict,the_dict)
                #var_dict=blacklist_whitetagged_query2(user_info,var_dict,the_dict)
                #var_dict=whitelist_whitetagged_query2(user_info,var_dict,the_dict)
                #var_dict=blacklist_blacktagged_query2(user_info,var_dict,the_dict)
                #var_dict=whitelist_blacktagged_query2(user_info,var_dict,the_dict)
                #var_dict=blacklist_watched_query2(user_info,var_dict,the_dict)
                #var_dict=whitelist_watched_query2(user_info,var_dict,the_dict)

                if (the_dict['DEBUG']):
                    for user_info in the_dict['enabled_users']:
                        #var_dict[user_info['user_id']]={}
                        var_dict=blacklist_favorited_query2(user_info,var_dict,the_dict)
                        var_dict=whitelist_favorited_query2(user_info,var_dict,the_dict)
                        var_dict=blacklist_whitetagged_query2(user_info,var_dict,the_dict)
                        var_dict=whitelist_whitetagged_query2(user_info,var_dict,the_dict)
                        var_dict=blacklist_blacktagged_query2(user_info,var_dict,the_dict)
                        var_dict=whitelist_blacktagged_query2(user_info,var_dict,the_dict)
                        var_dict=blacklist_watched_query2(user_info,var_dict,the_dict)
                        var_dict=whitelist_watched_query2(user_info,var_dict,the_dict)
                else:
                    processesList = []
                    for user_info in the_dict['enabled_users']:
                        #var_dict[user_info['user_id']]=multiprocessing.Manager().dict()
                        single_user_blist_fav_query=multiprocessing.Process(target=blacklist_favorited_query2, args=(user_info,var_dict,the_dict))
                        single_user_wlist_fav_query=multiprocessing.Process(target=whitelist_favorited_query2, args=(user_info,var_dict,the_dict))
                        single_user_blist_wtag_query=multiprocessing.Process(target=blacklist_whitetagged_query2, args=(user_info,var_dict,the_dict))
                        single_user_wlist_wtag_query=multiprocessing.Process(target=whitelist_whitetagged_query2, args=(user_info,var_dict,the_dict))
                        single_user_blist_btag_query=multiprocessing.Process(target=blacklist_blacktagged_query2, args=(user_info,var_dict,the_dict))
                        single_user_wlist_btag_query=multiprocessing.Process(target=whitelist_blacktagged_query2, args=(user_info,var_dict,the_dict))
                        single_user_blist_watch_query=multiprocessing.Process(target=blacklist_watched_query2, args=(user_info,var_dict,the_dict))
                        single_user_wlist_watch_query=multiprocessing.Process(target=whitelist_watched_query2, args=(user_info,var_dict,the_dict))
                        processesList.append(single_user_blist_fav_query)
                        processesList.append(single_user_wlist_fav_query)
                        processesList.append(single_user_blist_wtag_query)
                        processesList.append(single_user_wlist_wtag_query)
                        processesList.append(single_user_blist_btag_query)
                        processesList.append(single_user_wlist_btag_query)
                        processesList.append(single_user_blist_watch_query)
                        processesList.append(single_user_wlist_watch_query)
                        single_user_blist_fav_query.start()
                        single_user_wlist_fav_query.start()
                        single_user_blist_wtag_query.start()
                        single_user_wlist_wtag_query.start()
                        single_user_blist_btag_query.start()
                        single_user_wlist_btag_query.start()
                        single_user_blist_watch_query.start()
                        single_user_wlist_watch_query.start()
                    for m in processesList:
                        m.join()
                    for m in processesList:
                        m.close()

                #Order here is important (must match above)
                var_dict['data_from_favorited_queries']=[0,1,6,7]
                var_dict['data_from_whitetagged_queries']=[2,3,8,9]
                var_dict['data_from_blacktagged_queries']=[4,5,10,11]
                var_dict['data_from_whitelisted_queries']=[0,1,2,3,4,5,13]
                var_dict['data_from_blacklisted_queries']=[6,7,8,9,10,11,12]

                var_dict['data_lists']=[]
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})
                var_dict['data_lists'].append({'Items':[],'lib_id':'','path':'','network_path':''})

                if (isJellyfinServer(var_dict['server_brand'])):
                    whitelist_parent_id=var_dict['this_whitelist_lib']['lib_id']
                    blacklist_parent_id=var_dict['this_blacklist_lib']['lib_id']
                else:
                    if (('subfolder_id' in var_dict['this_whitelist_lib']) and (not (var_dict['this_whitelist_lib']['subfolder_id'] == None))):
                        whitelist_parent_id=var_dict['this_whitelist_lib']['subfolder_id']
                    else:
                        whitelist_parent_id=var_dict['this_whitelist_lib']['lib_id']
                    if (('subfolder_id' in var_dict['this_blacklist_lib']) and (not (var_dict['this_blacklist_lib']['subfolder_id'] == None))):
                        blacklist_parent_id=var_dict['this_blacklist_lib']['subfolder_id']
                    else:
                        blacklist_parent_id=var_dict['this_blacklist_lib']['lib_id']

                for user_info in the_dict['enabled_users']:
                    #Combine dictionaries into list of dictionaries
                    #Order here is important
                    var_dict['data_lists'][0]['Items'].extend(var_dict[user_info['user_id']]['data_Favorited_From_Whitelist']['Items']) #0
                    if (not (var_dict['data_lists'][0]['Items'] == [])):
                        var_dict['data_lists'][0]['lib_id']=whitelist_parent_id
                        var_dict['data_lists'][0]['path']=var_dict['this_whitelist_lib']['path']
                        var_dict['data_lists'][0]['network_path']=var_dict['this_whitelist_lib']['network_path']
                    var_dict['data_lists'][1]['Items'].extend(var_dict[user_info['user_id']]['data_Child_Of_Favorited_Item_From_Whitelist']['Items']) #1
                    if (not (var_dict['data_lists'][1]['Items'] == [])):
                        var_dict['data_lists'][1]['lib_id']=whitelist_parent_id
                        var_dict['data_lists'][1]['path']=var_dict['this_whitelist_lib']['path']
                        var_dict['data_lists'][1]['network_path']=var_dict['this_whitelist_lib']['network_path']
                    var_dict['data_lists'][2]['Items'].extend(var_dict[user_info['user_id']]['data_Whitetagged_From_Whitelist']['Items']) #2
                    if (not (var_dict['data_lists'][2]['Items'] == [])):
                        var_dict['data_lists'][2]['lib_id']=whitelist_parent_id
                        var_dict['data_lists'][2]['path']=var_dict['this_whitelist_lib']['path']
                        var_dict['data_lists'][2]['network_path']=var_dict['this_whitelist_lib']['network_path']
                    var_dict['data_lists'][3]['Items'].extend(var_dict[user_info['user_id']]['data_Child_Of_Whitetagged_From_Whitelist']['Items']) #3
                    if (not (var_dict['data_lists'][3]['Items'] == [])):
                        var_dict['data_lists'][3]['lib_id']=whitelist_parent_id
                        var_dict['data_lists'][3]['path']=var_dict['this_whitelist_lib']['path']
                        var_dict['data_lists'][3]['network_path']=var_dict['this_whitelist_lib']['network_path']
                    var_dict['data_lists'][4]['Items'].extend(var_dict[user_info['user_id']]['data_Blacktagged_From_Whitelist']['Items']) #4
                    if (not (var_dict['data_lists'][4]['Items'] == [])):
                        var_dict['data_lists'][4]['lib_id']=whitelist_parent_id
                        var_dict['data_lists'][4]['path']=var_dict['this_whitelist_lib']['path']
                        var_dict['data_lists'][4]['network_path']=var_dict['this_whitelist_lib']['network_path']
                    var_dict['data_lists'][5]['Items'].extend(var_dict[user_info['user_id']]['data_Child_Of_Blacktagged_From_Whitelist']['Items']) #5
                    if (not (var_dict['data_lists'][5]['Items'] == [])):
                        var_dict['data_lists'][5]['lib_id']=whitelist_parent_id
                        var_dict['data_lists'][5]['path']=var_dict['this_whitelist_lib']['path']
                        var_dict['data_lists'][5]['network_path']=var_dict['this_whitelist_lib']['network_path']
                    var_dict['data_lists'][6]['Items'].extend(var_dict[user_info['user_id']]['data_Favorited_From_Blacklist']['Items']) #6
                    if (not (var_dict['data_lists'][6]['Items'] == [])):
                        var_dict['data_lists'][6]['lib_id']=blacklist_parent_id
                        var_dict['data_lists'][6]['path']=var_dict['this_blacklist_lib']['path']
                        var_dict['data_lists'][6]['network_path']=var_dict['this_blacklist_lib']['network_path']
                    var_dict['data_lists'][7]['Items'].extend(var_dict[user_info['user_id']]['data_Child_Of_Favorited_Item_From_Blacklist']['Items']) #7
                    if (not (var_dict['data_lists'][7]['Items'] == [])):
                        var_dict['data_lists'][7]['lib_id']=blacklist_parent_id
                        var_dict['data_lists'][7]['path']=var_dict['this_blacklist_lib']['path']
                        var_dict['data_lists'][7]['network_path']=var_dict['this_blacklist_lib']['network_path']
                    var_dict['data_lists'][8]['Items'].extend(var_dict[user_info['user_id']]['data_Whitetagged_From_Blacklist']['Items']) #8
                    if (not (var_dict['data_lists'][8]['Items'] == [])):
                        var_dict['data_lists'][8]['lib_id']=blacklist_parent_id
                        var_dict['data_lists'][8]['path']=var_dict['this_blacklist_lib']['path']
                        var_dict['data_lists'][8]['network_path']=var_dict['this_blacklist_lib']['network_path']
                    var_dict['data_lists'][9]['Items'].extend(var_dict[user_info['user_id']]['data_Child_Of_Whitetagged_From_Blacklist']['Items']) #9
                    if (not (var_dict['data_lists'][9]['Items'] == [])):
                        var_dict['data_lists'][9]['lib_id']=blacklist_parent_id
                        var_dict['data_lists'][9]['path']=var_dict['this_blacklist_lib']['path']
                        var_dict['data_lists'][9]['network_path']=var_dict['this_blacklist_lib']['network_path']
                    var_dict['data_lists'][10]['Items'].extend(var_dict[user_info['user_id']]['data_Blacktagged_From_Blacklist']['Items']) #10
                    if (not (var_dict['data_lists'][10]['Items'] == [])):
                        var_dict['data_lists'][10]['lib_id']=blacklist_parent_id
                        var_dict['data_lists'][10]['path']=var_dict['this_blacklist_lib']['path']
                        var_dict['data_lists'][10]['network_path']=var_dict['this_blacklist_lib']['network_path']
                    var_dict['data_lists'][11]['Items'].extend(var_dict[user_info['user_id']]['data_Child_Of_Blacktagged_From_Blacklist']['Items']) #11
                    if (not (var_dict['data_lists'][11]['Items'] == [])):
                        var_dict['data_lists'][11]['lib_id']=blacklist_parent_id
                        var_dict['data_lists'][11]['path']=var_dict['this_blacklist_lib']['path']
                        var_dict['data_lists'][11]['network_path']=var_dict['this_blacklist_lib']['network_path']
                    var_dict['data_lists'][12]['Items'].extend(var_dict[user_info['user_id']]['data_Blacklist']['Items']) #12
                    if (not (var_dict['data_lists'][12]['Items'] == [])):
                        var_dict['data_lists'][12]['lib_id']=blacklist_parent_id
                        var_dict['data_lists'][12]['path']=var_dict['this_blacklist_lib']['path']
                        var_dict['data_lists'][12]['network_path']=var_dict['this_blacklist_lib']['network_path']
                    var_dict['data_lists'][13]['Items'].extend(var_dict[user_info['user_id']]['data_Whitelist']['Items']) #13
                    if (not (var_dict['data_lists'][13]['Items'] == [])):
                        var_dict['data_lists'][13]['lib_id']=whitelist_parent_id
                        var_dict['data_lists'][13]['path']=var_dict['this_whitelist_lib']['path']
                        var_dict['data_lists'][13]['network_path']=var_dict['this_whitelist_lib']['network_path']

                    #Determine if we are done processing queries or if there are still queries to be sent
                    var_dict[user_info['user_id']]['QueryItemsRemaining_All']=var_dict[user_info['user_id']]['QueriesRemaining_Favorited_From_Blacklist'] | \
                                                                               var_dict[user_info['user_id']]['QueriesRemaining_Favorited_From_Whitelist'] | \
                                                                               var_dict[user_info['user_id']]['QueriesRemaining_Whitetagged_From_Blacklist'] | \
                                                                               var_dict[user_info['user_id']]['QueriesRemaining_Whitetagged_From_Whitelist'] | \
                                                                               var_dict[user_info['user_id']]['QueriesRemaining_Blacktagged_From_Blacklist'] | \
                                                                               var_dict[user_info['user_id']]['QueriesRemaining_Blacktagged_From_Whitelist'] | \
                                                                               var_dict[user_info['user_id']]['QueriesRemaining_Blacklist'] | \
                                                                               var_dict[user_info['user_id']]['QueriesRemaining_Whitelist']

                    var_dict['QueryItemsRemaining_All']|=var_dict[user_info['user_id']]['QueryItemsRemaining_All']

                #track where we are in the var_dict['data_lists']
                var_dict['data_list_pos']=0

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
                            if (item['Type'].casefold() == var_dict['media_type_lower']):
                                for var_dict['mediasource'] in item['MediaSources']:
                                    var_dict['itemIsMonitored']=get_isItemMonitored2(var_dict['mediasource'],the_dict)

                            #determine how to show media item
                            if (var_dict['itemIsMonitored']):

                                if (the_dict['DEBUG']):
                                    for user_info in the_dict['enabled_users']:
                                        #var_dict[user_info['user_id']]=multiprocessing.Manager().dict()
                                        user_item=get_ADDITIONAL_itemInfo(user_info,item['Id'],'get_preprocessing_item_info_for_user_' + str(user_info['user_id']),the_dict)
                                        #Save lib_id for each media item; needed during pre processing
                                        user_item['mumc']={}
                                        user_item['mumc']['lib_id']=var_dict['data_dict']['lib_id']
                                        user_item['mumc']['path']=var_dict['data_dict']['path']
                                        user_item['mumc']['network_path']=var_dict['data_dict']['network_path']
                                        var_dict=preProcessing(user_item,user_info,var_dict,the_dict)
                                else:
                                    processesList = []
                                    for user_info in the_dict['enabled_users']:
                                        #var_dict[user_info['user_id']]=multiprocessing.Manager().dict()
                                        user_item=get_ADDITIONAL_itemInfo(user_info,item['Id'],'get_preprocessing_item_info_for_user_' + str(user_info['user_id']),the_dict)
                                        #Save lib_id for each media item; needed during pre processing
                                        user_item['mumc']={}
                                        user_item['mumc']['lib_id']=var_dict['data_dict']['lib_id']
                                        user_item['mumc']['path']=var_dict['data_dict']['path']
                                        user_item['mumc']['network_path']=var_dict['data_dict']['network_path']
                                        single_user_pre_process=multiprocessing.Process(target=preProcessing, args=(user_item,user_info,var_dict,the_dict))
                                        processesList.append(single_user_pre_process)
                                        single_user_pre_process.start()

                                    for u in processesList:
                                        u.join()
                                    for u in processesList:
                                        u.close()

##########################################################################################################################################

                                print_byType(the_dict['console_separator_'],the_dict['advanced_settings']['console_controls']['headers']['user']['show'],the_dict,the_dict['advanced_settings']['console_controls']['headers']['user']['formatting'])

                                '''
                                the_dict[var_dict['media_dict_str']]['media_data']|=var_dict['media_data']
                                the_dict[var_dict['media_dict_str']][user_info['user_id']]['deleteItemsIdTracker_Media']=var_dict['deleteItemsIdTracker_Media']
                                
                                the_dict[var_dict['media_dict_str']]['deleteItemsIdTracker_createdMedia']=list(set(the_dict[var_dict['media_dict_str']]['deleteItemsIdTracker_createdMedia'] + var_dict['deleteItemsIdTracker_createdMedia']))
                                the_dict[var_dict['media_dict_str']]['deleteItemsIdTracker_createdMedia'].sort()
                                
                                the_dict[var_dict['media_dict_str']][user_info['user_id']]['isblacklisted_extraInfo_byUserId_Media']=var_dict['isblacklisted_extraInfo_byUserId_Media']
                                the_dict[var_dict['media_dict_str']]['isblacklisted_extraInfo_Tracker']+=var_dict['isblacklisted_extraInfo_Tracker']
                                the_dict[var_dict['media_dict_str']][user_info['user_id']]['iswhitelisted_extraInfo_byUserId_Media']=var_dict['iswhitelisted_extraInfo_byUserId_Media']
                                the_dict[var_dict['media_dict_str']]['iswhitelisted_extraInfo_Tracker']+=var_dict['iswhitelisted_extraInfo_Tracker']
                                the_dict[var_dict['media_dict_str']][user_info['user_id']]['isblacktagged_extraInfo_byUserId_Media']=var_dict['isblacktagged_extraInfo_byUserId_Media']
                                the_dict[var_dict['media_dict_str']]['isblacktagged_extraInfo_Tracker']+=var_dict['isblacktagged_extraInfo_Tracker']
                                the_dict[var_dict['media_dict_str']][user_info['user_id']]['iswhitetagged_extraInfo_byUserId_Media']=var_dict['iswhitetagged_extraInfo_byUserId_Media']
                                the_dict[var_dict['media_dict_str']]['iswhitetagged_extraInfo_Tracker']+=var_dict['iswhitetagged_extraInfo_Tracker']
                                the_dict[var_dict['media_dict_str']][user_info['user_id']]['isfavorited_extraInfo_byUserId_Media']=var_dict['isfavorited_extraInfo_byUserId_Media']
                                the_dict[var_dict['media_dict_str']]['isfavorited_extraInfo_Tracker']+=var_dict['isfavorited_extraInfo_Tracker']

                                the_dict[var_dict['media_dict_str']][user_info['user_id']]['mediaCounts_byUserId']=var_dict['mediaCounts_byUserId']
                                '''

                                media_returns['media_dict']=the_dict[var_dict['media_dict_str']]
                                media_returns['media_found']=var_dict['media_found']

##########################################################################################################################################

                            #Add media item Id to tracking list so it is not processed more than once
                            var_dict['user_processed_item_Ids'].add(item['Id'])

##########################################################################################################################################

                        #init_postProcessing2(the_dict)
                        deleteItems_dict.update(init_postProcessing2(var_dict['media_type_lower'],the_dict))

                        #delete media_item here
                        #sort lists of items to be deleted into a single list
                        deleteItems=sortDeleteLists2(var_dict['media_type_lower'],deleteItems_dict)

                        deleteItems_dict.clear()

                        if (deleteItems):
                            #output to console the items to be deleted; then delete media items
                            print_and_delete_items(deleteItems,the_dict,var_dict['media_type_lower'])

                        #remove old media_item data before moving on to the new media_item
                        the_dict=clear_old_media_items(var_dict['media_type_lower'],the_dict)
                        #the_dict=clear_old_media_items('movie',the_dict)
                        #the_dict=clear_old_media_items('episode',the_dict)
                        #the_dict=clear_old_media_items('audio',the_dict)
                        #the_dict=clear_old_media_items('audiobook',the_dict)

##########################################################################################################################################

                    var_dict['data_list_pos'] += 1

############# End Media #############

    return media_returns


def clear_old_media_items(media_type,the_dict):
    try:
        the_dict[media_type + '_dict']['media_data'].clear()
    except:
        pass
    try:
        the_dict[media_type + '_dict']['deleteItemsIdTracker_Media'].clear()
    except:
        pass
    try:
        the_dict[media_type + '_dict']['deleteItemsIdTracker_createdMedia'].clear()
    except:
        pass
    try:
        the_dict[media_type + '_dict']['isfavorited_extraInfo_Tracker'].clear()
    except:
        pass
    try:
        the_dict[media_type + '_dict']['iswhitetagged_extraInfo_Tracker'].clear()
    except:
        pass
    try:
        the_dict[media_type + '_dict']['isblacktagged_extraInfo_Tracker'].clear()
    except:
        pass
    try:
        the_dict[media_type + '_dict']['iswhitelisted_extraInfo_Tracker'].clear()
    except:
        pass
    try:
        the_dict[media_type + '_dict']['isblacklisted_extraInfo_Tracker'].clear()
    except:
        pass

    for userId in the_dict['enabled_user_ids']:
        try:
            the_dict[media_type + '_dict'][userId].clear()
        except:
            pass

    return the_dict


def init_getMedia2(the_dict):

    the_dict['movie_dict']={}
    the_dict['movie_dict']['media_type']='movie'
    the_dict['movie_dict']['media_data']={}
    the_dict['movie_dict']['deleteItemsIdTracker_createdMedia']=[]
    the_dict['movie_dict']['isfavorited_extraInfo_Tracker']=[]
    the_dict['movie_dict']['iswhitetagged_extraInfo_Tracker']=[]
    the_dict['movie_dict']['isblacktagged_extraInfo_Tracker']=[]
    the_dict['movie_dict']['iswhitelisted_extraInfo_Tracker']=[]
    the_dict['movie_dict']['isblacklisted_extraInfo_Tracker']=[]

    the_dict['episode_dict']={}
    the_dict['episode_dict']['media_type']='episode'
    the_dict['episode_dict']['media_data']={}
    the_dict['episode_dict']['deleteItemsIdTracker_createdMedia']=[]
    the_dict['episode_dict']['isfavorited_extraInfo_Tracker']=[]
    the_dict['episode_dict']['iswhitetagged_extraInfo_Tracker']=[]
    the_dict['episode_dict']['isblacktagged_extraInfo_Tracker']=[]
    the_dict['episode_dict']['iswhitelisted_extraInfo_Tracker']=[]
    the_dict['episode_dict']['isblacklisted_extraInfo_Tracker']=[]

    the_dict['audio_dict']={}
    the_dict['audio_dict']['media_type']='audio'
    the_dict['audio_dict']['media_data']={}
    the_dict['audio_dict']['deleteItemsIdTracker_createdMedia']=[]
    the_dict['audio_dict']['isfavorited_extraInfo_Tracker']=[]
    the_dict['audio_dict']['iswhitetagged_extraInfo_Tracker']=[]
    the_dict['audio_dict']['isblacktagged_extraInfo_Tracker']=[]
    the_dict['audio_dict']['iswhitelisted_extraInfo_Tracker']=[]
    the_dict['audio_dict']['isblacklisted_extraInfo_Tracker']=[]

    the_dict['audiobook_dict']={}
    the_dict['audiobook_dict']['media_type']='audiobook'
    the_dict['audiobook_dict']['media_data']={}
    the_dict['audiobook_dict']['deleteItemsIdTracker_createdMedia']=[]
    the_dict['audiobook_dict']['isfavorited_extraInfo_Tracker']=[]
    the_dict['audiobook_dict']['iswhitetagged_extraInfo_Tracker']=[]
    the_dict['audiobook_dict']['isblacktagged_extraInfo_Tracker']=[]
    the_dict['audiobook_dict']['iswhitelisted_extraInfo_Tracker']=[]
    the_dict['audiobook_dict']['isblacklisted_extraInfo_Tracker']=[]

    #Determine played and created date for each media type; UTC time used for media items; needed for get_mediaItems2() and postProcessing()
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

    #the_dict['currentUserPosition']=0

    monitor_disabled_users=the_dict['admin_settings']['behavior']['users']['monitor_disabled']
    the_dict['enabled_users']=[]
    the_dict['enabled_user_ids']=[]
    the_dict['disabled_users']=[]
    the_dict['disabled_user_ids']=[]
    #Get items that could be ready for deletion
    for user_info in the_dict['admin_settings']['users']:

        #get user info about this monitored_user
        this_users_info=get_single_user(user_info['user_id'],the_dict)
        
        #determine if this monitored_user should be processed for get_media()
        #remember this information for post-processing
        #if user is disabled
        if (this_users_info['Policy']['IsDisabled']):
            #check the monitor_disabled_users config value
            if (monitor_disabled_users):
                #mark the user as enabled
                the_dict['enabled_users'].append(user_info)
                the_dict['enabled_user_ids'].append(user_info['user_id'])
        #if user is enabled; mark the user as enabled
        else:
            the_dict['enabled_users'].append(user_info)
            the_dict['enabled_user_ids'].append(user_info['user_id'])

    #Create userId list of accessible libraries
    the_dict['byUserId_accessibleLibraries']={}
    the_dict['byUserId_accessibleLibraryParents']={}
    the_dict['all_whitelists']=[]
    the_dict['all_blacklists']=[]

    for user_info in the_dict['admin_settings']['users']:
        the_dict['byUserId_accessibleLibraries'][user_info['user_id']]=[]
        the_dict['byUserId_accessibleLibraryParents'][user_info['user_id']]=[]

        for lib_info in user_info['whitelist']:
            if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
                library_id='lib_id'
                parent_id='lib_id'
            else:
                if (('subfolder_id' in lib_info) and (not (lib_info['subfolder_id'] == None))):
                    library_id='subfolder_id'
                    parent_id='lib_id'
                else:
                    library_id='lib_id'
                    parent_id='lib_id'

            if (not (lib_info[library_id] == None)):
                the_dict['byUserId_accessibleLibraries'][user_info['user_id']].append(lib_info[library_id])
                the_dict['byUserId_accessibleLibraryParents'][user_info['user_id']].append(lib_info[parent_id])
                if (not (lib_info in the_dict['all_whitelists'])):
                    the_dict['all_whitelists'].append({})
                    this_index=the_dict['all_whitelists'].index({})
                    the_dict['all_whitelists'][this_index]['lib_id']=lib_info['lib_id']
                    the_dict['all_whitelists'][this_index]['collection_type']=lib_info['collection_type']
                    the_dict['all_whitelists'][this_index]['path']=lib_info['path']
                    the_dict['all_whitelists'][this_index]['network_path']=lib_info['network_path']
                    the_dict['all_whitelists'][this_index]['subfolder_id']=lib_info['subfolder_id']
                    the_dict['all_whitelists'][this_index]['lib_enabled']=lib_info['lib_enabled']

        for lib_info in user_info['blacklist']:
            if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
                library_id='lib_id'
                parent_id='lib_id'
            else:
                if (('subfolder_id' in lib_info) and (not (lib_info['subfolder_id'] == None))):
                    library_id='subfolder_id'
                    parent_id='lib_id'
                else:
                    library_id='lib_id'
                    parent_id='lib_id'

            if (not (lib_info[library_id] == None)):
                the_dict['byUserId_accessibleLibraries'][user_info['user_id']].append(lib_info[library_id])
                the_dict['byUserId_accessibleLibraryParents'][user_info['user_id']].append(lib_info[parent_id])
                if (not (lib_info in the_dict['all_blacklists'])):
                    the_dict['all_blacklists'].append({})
                    this_index=the_dict['all_blacklists'].index({})
                    the_dict['all_blacklists'][this_index]['lib_id']=lib_info['lib_id']
                    the_dict['all_blacklists'][this_index]['collection_type']=lib_info['collection_type']
                    the_dict['all_blacklists'][this_index]['path']=lib_info['path']
                    the_dict['all_blacklists'][this_index]['network_path']=lib_info['network_path']
                    the_dict['all_blacklists'][this_index]['subfolder_id']=lib_info['subfolder_id']
                    the_dict['all_blacklists'][this_index]['lib_enabled']=lib_info['lib_enabled']

    the_dict['whitelist_length'] = sum(1 for _ in the_dict['all_whitelists'])
    the_dict['blacklist_length'] = sum(1 for _ in the_dict['all_blacklists'])
    if (the_dict['whitelist_length'] > the_dict['blacklist_length']):
        the_dict['shortest_list_length']=the_dict['blacklist_length']
        the_dict['list_diff']=the_dict['whitelist_length'] - the_dict['blacklist_length']
        the_dict['shortest_list']='blacklist'
    elif (the_dict['blacklist_length'] > the_dict['whitelist_length']):
        the_dict['shortest_list_length']=the_dict['whitelist_length']
        the_dict['list_diff']=the_dict['blacklist_length'] - the_dict['whitelist_length']
        the_dict['shortest_list']='whitelist'
    else:
        the_dict['shortest_list_length']=0
        the_dict['list_diff']=0
        the_dict['shortest_list']='whitelist'

    for _ in range(the_dict['list_diff']):
        the_dict['all_' + the_dict['shortest_list'] + 's'].append({'lib_id':None,'subfolder_id':None,'collection_type':None,'path':None,'network_path':None,'lib_enabled':False})

    for user_info in the_dict['admin_settings']['users']:
        all_whitelists_len=len(the_dict['all_whitelists'])
        user_whitelist_len=len(user_info['whitelist'])
        for _ in range(all_whitelists_len - user_whitelist_len):
            user_info['whitelist'].append({'lib_id':None,'subfolder_id':None,'collection_type':None,'path':None,'network_path':None,'lib_enabled':False})

        all_blacklists_len=len(the_dict['all_blacklists'])
        user_blacklist_len=len(user_info['blacklist'])
        for _ in range(all_blacklists_len - user_blacklist_len):
            user_info['blacklist'].append({'lib_id':None,'subfolder_id':None,'collection_type':None,'path':None,'network_path':None,'lib_enabled':False})


    #before getting media, check if users still have access to their libraries in the config file
    #only applies to Emby
    #Jellyfin does not offer "excluded subfolders" data
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        for user_id in the_dict['enabled_user_ids']:
            data_single_user=get_single_user(user_id,the_dict)
            for lib_id in the_dict['byUserId_accessibleLibraries'][user_id]:
                parent_id=the_dict['byUserId_accessibleLibraryParents'][user_id][the_dict['byUserId_accessibleLibraries'][user_id].index(lib_id)]
                if ((parent_id + '_' + lib_id) in data_single_user['Policy']['ExcludedSubFolders']):
                    for user_data in the_dict['admin_settings']['users']:
                        if (user_data['user_id'] == user_id):
                            user_index=the_dict['admin_settings']['users'].index(user_data)
                            for lib_data in the_dict['admin_settings']['users'][user_index]['whitelist']:
                                if ((lib_data['lib_id'] == parent_id) and (lib_data['subfolder_id'] == lib_id)):
                                    lib_index=the_dict['admin_settings']['users'][user_index]['whitelist'].index(lib_data)
                                    the_dict['admin_settings']['users'][user_index]['whitelist'][lib_index]['lib_enabled']=False
                                    break
                            for lib_data in the_dict['admin_settings']['users'][user_index]['blacklist']:
                                if ((lib_data['lib_id'] == parent_id) and (lib_data['subfolder_id'] == lib_id)):
                                    lib_index=the_dict['admin_settings']['users'][user_index]['blacklist'].index(lib_data)
                                    the_dict['admin_settings']['users'][user_index]['blacklist'][lib_index]['lib_enabled']=False
                                    break


    #Get items that could be ready for deletion
    for user_info in the_dict['enabled_users']:

        the_dict['movie_dict'][user_info['user_id']]={}
        the_dict['episode_dict'][user_info['user_id']]={}
        the_dict['audio_dict'][user_info['user_id']]={}
        the_dict['audiobook_dict'][user_info['user_id']]={}            

    #print_user_header(user_info,the_dict)

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

    if ((the_dict['basic_settings']['filter_statements']['movie']['played']['condition_days'] == -1) and 
        (the_dict['basic_settings']['filter_statements']['movie']['created']['condition_days'] == -1)):
        movie_delete=False
        movie_keep=False
    if ((the_dict['basic_settings']['filter_statements']['episode']['played']['condition_days'] == -1) and 
        (the_dict['basic_settings']['filter_statements']['episode']['created']['condition_days'] == -1)):
        episode_delete=False
        episode_keep=False
    if ((the_dict['basic_settings']['filter_statements']['audio']['played']['condition_days'] == -1) and 
        (the_dict['basic_settings']['filter_statements']['audio']['created']['condition_days'] == -1)):
        audio_delete=False
        audio_keep=False
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        if ((the_dict['basic_settings']['filter_statements']['audiobook']['played']['condition_days'] == -1) and 
            (the_dict['basic_settings']['filter_statements']['audiobook']['created']['condition_days'] == -1)):
            audiobook_delete=False
            audiobook_keep=False

    #when debug is disabled AND no active media delete/keep items are being output to the console; allow multiprocessing
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
        mpp_movieGetMedia=multiprocessing.Process(target=get_mediaItems2,args=(the_dict,the_dict['movie_dict']['media_type'],movie_returns))
        mpp_episodeGetMedia=multiprocessing.Process(target=get_mediaItems2,args=(the_dict,the_dict['episode_dict']['media_type'],episode_returns))
        mpp_audioGetMedia=multiprocessing.Process(target=get_mediaItems2,args=(the_dict,the_dict['audio_dict']['media_type'],audio_returns))
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            mpp_audiobookGetMedia=multiprocessing.Process(target=get_mediaItems2,args=(the_dict,the_dict['audibook_dict']['media_type'],audiobook_returns))

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
        movie_returns=get_mediaItems2(the_dict,the_dict['movie_dict']['media_type'],movie_returns)
        #query the server for episode media items
        episode_returns=get_mediaItems2(the_dict,the_dict['episode_dict']['media_type'],episode_returns)
        #query the server for audio media items
        audio_returns=get_mediaItems2(the_dict,the_dict['audio_dict']['media_type'],audio_returns)
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            #query the server for audiobook media items
            #audioBook media type only applies to jellyfin
            #Jellyfin sets audiobooks to a media type of audioBook
            #Emby sets audiobooks to a media type of audio (Emby users, see audio section)
            audiobook_returns=get_mediaItems2(the_dict,the_dict['audiobook_dict']['media_type'],audiobook_returns)

    '''
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

    #the_dict['currentUserPosition']+=1

    media_found=(movie_found or episode_found or audio_found or audiobook_found)

    if (not (the_dict['all_media_disabled'])):
        if (not (media_found)):
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\n",1,the_dict)
            print_byType('[NO PLAYED, WHITELISTED, OR TAGGED MEDIA ITEMS]\n',the_dict['advanced_settings']['console_controls']['warnings']['script']['show'],the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])
    '''

    return the_dict