#!/usr/bin/env python3
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType,convert2json
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_blacklist import blacklist_playedPatternCleanup
from mumc_modules.mumc_whitelist import whitelist_playedPatternCleanup
from mumc_modules.mumc_favorited import favorites_playedPatternCleanup
from mumc_modules.mumc_minimum_episodes import get_minEpisodesToKeep


def convert_timeToString(byUserId_item):
    for userId in byUserId_item:
        if (not((userId == 'ActionBehavior') or (userId == 'ActionType') or (userId == 'MonitoredUsersAction') or
                (userId == 'MonitoredUsersMeetPlayedFilter') or(userId == 'ConfiguredBehavior'))):
            for itemId in byUserId_item[userId]:
                if ('CutOffDatePlayed' in byUserId_item[userId][itemId]):
                    byUserId_item[userId][itemId]['CutOffDatePlayed']=str(byUserId_item[userId][itemId]['CutOffDatePlayed'])
                if ('CutOffDateCreated' in byUserId_item[userId][itemId]):
                    byUserId_item[userId][itemId]['CutOffDateCreated']=str(byUserId_item[userId][itemId]['CutOffDateCreated'])

    return(byUserId_item)


#Add/Remove item to/from delete list if meeting favorite/whitetagged/blacktagged/whitelisted pattern and played pattern
def addItem_removeItem_fromDeleteList_usingBehavioralPatterns(itemsDictionary,itemsExtraDictionary,deleteItems,deleteItemsIdTracker):
    isMeetingAction_dict={}
    isMeetingPlayedFilter_dict={}
    itemId_tracker=[]
    userId_tracker=[]

    andIt='all'
    orIt='any'

    addIt='delete'
    #removeIt='keep'

    if (('MonitoredUsersAction' in itemsExtraDictionary) and ('MonitoredUsersMeetPlayedFilter' in itemsExtraDictionary)):
        actionFilter=itemsExtraDictionary['MonitoredUsersAction']
        playedFilter=itemsExtraDictionary['MonitoredUsersMeetPlayedFilter']
        methodFilter=itemsExtraDictionary['ConfiguredBehavior']
        behaviorFilter=itemsExtraDictionary['ActionBehavior']
        #wordFilter=itemsExtraDictionary['ActionType']

        for userId in itemsDictionary:
            userId_tracker.append(userId)

        for userId in itemsDictionary:
            for itemId in itemsDictionary[userId]:
                if not (itemId in itemId_tracker):
                    firstMeetingActionLoop=True
                    firstPlayedFilterLoop=True
                    itemId_tracker.append(itemId)
                    item=itemsDictionary[userId][itemId]
                    for subUserId in userId_tracker:
                        if (firstMeetingActionLoop):
                            if (itemId in itemsDictionary[subUserId]):
                                if (not(itemsExtraDictionary[subUserId][itemId]['IsMeetingAction'] == None)):
                                    isMeetingAction_dict[itemId]=itemsExtraDictionary[subUserId][itemId]['IsMeetingAction']
                                    firstMeetingActionLoop=False
                        else:
                            if (itemId in itemsDictionary[subUserId]):
                                if (actionFilter == andIt):
                                    if (not(itemsExtraDictionary[subUserId][itemId]['IsMeetingAction'] == None)):
                                        isMeetingAction_dict[itemId]&=itemsExtraDictionary[subUserId][itemId]['IsMeetingAction']
                                elif (actionFilter == orIt):
                                    if (not(itemsExtraDictionary[subUserId][itemId]['IsMeetingAction'] == None)):
                                        isMeetingAction_dict[itemId]|=itemsExtraDictionary[subUserId][itemId]['IsMeetingAction']
                            else:
                                if (actionFilter == andIt):
                                    isMeetingAction_dict[itemId]&=False
                                elif (actionFilter == orIt):
                                    isMeetingAction_dict[itemId]|=False

                        if (firstPlayedFilterLoop):
                            if (itemId in itemsDictionary[subUserId]):
                                #Yes verify 'IsMeetingAction' is NOT None on purpose; only want to use this if action is True or False
                                if (not(itemsExtraDictionary[subUserId][itemId]['IsMeetingAction'] == None)):
                                    isMeetingPlayedFilter_dict[itemId]=itemsExtraDictionary[subUserId][itemId]['IsMeetingPlayedFilter']
                                    firstPlayedFilterLoop=False
                        else:
                            if (itemId in itemsDictionary[subUserId]):
                                if (playedFilter == andIt):
                                    #Yes verify 'IsMeetingAction' is NOT None on purpose; only want to use this if action is True or False
                                    if (not(itemsExtraDictionary[subUserId][itemId]['IsMeetingAction'] == None)):
                                        isMeetingPlayedFilter_dict[itemId]&=itemsExtraDictionary[subUserId][itemId]['IsMeetingPlayedFilter']
                                elif (playedFilter == orIt):
                                    #Yes verify 'IsMeetingAction' is NOT None on purpose; only want to use this if action is True or False
                                    if (not(itemsExtraDictionary[subUserId][itemId]['IsMeetingAction'] == None)):
                                        isMeetingPlayedFilter_dict[itemId]|=itemsExtraDictionary[subUserId][itemId]['IsMeetingPlayedFilter']
                                else:
                                    #Yes verify 'IsMeetingAction' is NOT None on purpose; only want to use this if action is True or False
                                    if (not(itemsExtraDictionary[subUserId][itemId]['IsMeetingAction'] == None)):
                                        isMeetingPlayedFilter_dict[itemId]=True
                            else:
                                if (playedFilter == andIt):
                                    isMeetingPlayedFilter_dict[itemId]&=False
                                elif (playedFilter == orIt):
                                    isMeetingPlayedFilter_dict[itemId]|=False
                                else:
                                    isMeetingPlayedFilter_dict[itemId]=True

                    if (isMeetingAction_dict[itemId] and isMeetingPlayedFilter_dict[itemId]):
                        if ((behaviorFilter == 0) or (behaviorFilter == 1) or (behaviorFilter == 2)):
                            #No action taken on True
                            addItemToDeleteList=None
                        elif ((behaviorFilter == 3) or (behaviorFilter == 4) or (behaviorFilter == 5)):
                            #Action taken on True
                            if (methodFilter == addIt):
                                addItemToDeleteList=True
                            else: #(methodFilter == removeIt):
                                addItemToDeleteList=False
                        else: #((behaviorFilter == 6) or (behaviorFilter == 7) or (behaviorFilter == 8)):
                            #Opposite action taken on True
                            if (methodFilter == addIt):
                                addItemToDeleteList=False
                            else: #(methodFilter == removeIt):
                                addItemToDeleteList=True
                    else:
                        if ((behaviorFilter == 0) or (behaviorFilter == 3) or (behaviorFilter == 6)):
                            #No action taken on False
                            addItemToDeleteList=None
                        elif ((behaviorFilter == 1) or (behaviorFilter == 4) or (behaviorFilter == 7)):
                            #Action taken on False
                            if (methodFilter == addIt):
                                addItemToDeleteList=True
                            else: #(methodFilter == removeIt):
                                addItemToDeleteList=False
                        else: #((behaviorFilter == 2) or (behaviorFilter == 5) or (behaviorFilter == 8)):
                            #Opposite action taken on False
                            if (methodFilter == addIt):
                                addItemToDeleteList=False
                            else: #(methodFilter == removeIt):
                                addItemToDeleteList=True

                    if (addItemToDeleteList == True):
                        if (not (item['Id'] in deleteItemsIdTracker)):
                            deleteItems.append(item)
                            deleteItemsIdTracker.append(item['Id'])
                    elif (addItemToDeleteList == False):
                        while item['Id'] in deleteItemsIdTracker:
                            try:
                                if (item in deleteItems):
                                    deleteItems.remove(item)
                                    deleteItemsIdTracker.remove(item['Id'])
                                else:
                                    for delItem in deleteItems:
                                        if (item['Id'] == delItem['Id']):
                                            deleteItems.remove(delItem)
                                            deleteItemsIdTracker.remove(item['Id'])
                            except:
                                itemId_tracker.remove(itemId)

    return deleteItems,deleteItemsIdTracker


#add played and created data for item during pre-processing
def update_byUserId_playedStates(extra_byUserId_Media,userKey,itemId,media_played_days,media_created_days,cut_off_date_played_media,
                                 cut_off_date_created_media,media_played_count_comparison,media_played_count,
                                 media_created_played_count_comparison,media_created_played_count):
    extra_byUserId_Media[userKey][itemId]['PlayedDays']=media_played_days
    extra_byUserId_Media[userKey][itemId]['CreatedDays']=media_created_days
    extra_byUserId_Media[userKey][itemId]['CutOffDatePlayed']=cut_off_date_played_media
    extra_byUserId_Media[userKey][itemId]['CutOffDateCreated']=cut_off_date_created_media
    extra_byUserId_Media[userKey][itemId]['PlayedCountComparison']=media_played_count_comparison
    extra_byUserId_Media[userKey][itemId]['PlayedCount']=media_played_count
    extra_byUserId_Media[userKey][itemId]['CreatedPlayedCountComparison']=media_created_played_count_comparison
    extra_byUserId_Media[userKey][itemId]['CreatedPlayedCount']=media_created_played_count

    return extra_byUserId_Media


#add played and created data for item during post-processing
def add_missingItems_byUserId_playedStates(the_dict,itemsDictionary,itemsExtraDictionary,media_played_days,media_created_days,cut_off_date_played_media,cut_off_date_created_media,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count):
    userId_tracker=[]
    itemId_tracker=[]

    for userId in itemsDictionary:
        userId_tracker.append(userId)

    for userId in itemsDictionary:
        for itemId in itemsDictionary[userId]:
            if not (itemId in itemId_tracker):
                itemId_tracker.append(itemId)
                for subUserId in userId_tracker:
                    if (not(itemId in itemsExtraDictionary[subUserId])):
                        itemsExtraDictionary[subUserId][itemId]={}
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log("\nAdding missing played state for item " + str(itemId) + " to itemsExtraDictionary for user " + str(subUserId),3,the_dict)
                    itemsExtraDictionary=update_byUserId_playedStates(itemsExtraDictionary,subUserId,itemId,media_played_days,media_created_days,cut_off_date_played_media,cut_off_date_created_media,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count)

    return itemsExtraDictionary


def run_post_processing(the_dict,media_dict):

    mediaType=media_dict['mediaType'].upper()

    library_matching_behavior=the_dict['library_matching_behavior']
    bluser_keys_json_verify=the_dict['bluser_keys_json_verify']
    user_bllib_keys_json=the_dict['user_bllib_keys_json']
    user_bllib_netpath_json=the_dict['user_bllib_netpath_json']
    user_bllib_path_json=the_dict['user_bllib_path_json']
    wluser_keys_json_verify=the_dict['wluser_keys_json_verify']
    user_wllib_keys_json=the_dict['user_wllib_keys_json']
    user_wllib_netpath_json=the_dict['user_wllib_netpath_json']
    user_wllib_path_json=the_dict['user_wllib_path_json']

    cut_off_date_played_media=the_dict['cut_off_date_played_media']
    cut_off_date_created_media=the_dict['cut_off_date_created_media']
    minimum_number_episodes=the_dict['minimum_number_episodes']
    minimum_number_played_episodes=the_dict['minimum_number_played_episodes']
    print_common_delete_keep_info=the_dict['print_common_delete_keep_info']

    if (mediaType == 'MOVIE'):
        media_played_days=the_dict['played_filter_movie'][0]
        media_created_days=the_dict['created_filter_movie'][0]
        media_played_count_comparison=the_dict['played_filter_movie'][1]
        media_created_played_count_comparison=the_dict['created_filter_movie'][1]
        media_played_count=the_dict['played_filter_movie'][2]
        media_created_played_count=the_dict['created_filter_movie'][2]
        media_created_played_behavioral_control=the_dict['created_filter_movie'][3]
        blacklisted_behavior_media=the_dict['blacklisted_behavior_movie']
        whitelisted_behavior_media=the_dict['blacklisted_behavior_movie']
        blacktagged_behavior_media=the_dict['blacklisted_behavior_movie']
        whitetagged_behavior_media=the_dict['blacklisted_behavior_movie']
        favorited_behavior_media=the_dict['blacklisted_behavior_movie']
        advFav0_media=the_dict['favorited_advanced_movie_genre']
        advFav1_media=the_dict['favorited_advanced_movie_library_genre']
        advFav2_media=0
        advFav3_media=0
        advFav4_media=0
        advFav5_media=0
    elif (mediaType == 'EPISODE'):
        media_played_days=the_dict['played_filter_episode'][0]
        media_created_days=the_dict['created_filter_episode'][0]
        media_played_count_comparison=the_dict['played_filter_episode'][1]
        media_created_played_count_comparison=the_dict['created_filter_episode'][1]
        media_played_count=the_dict['played_filter_episode'][2]
        media_created_played_count=the_dict['created_filter_episode'][2]
        media_created_played_behavioral_control=the_dict['created_filter_episode'][3]
        blacklisted_behavior_media=the_dict['blacklisted_behavior_episode']
        whitelisted_behavior_media=the_dict['blacklisted_behavior_episode']
        blacktagged_behavior_media=the_dict['blacklisted_behavior_episode']
        whitetagged_behavior_media=the_dict['blacklisted_behavior_episode']
        favorited_behavior_media=the_dict['blacklisted_behavior_episode']
        advFav0_media=the_dict['favorited_advanced_episode_genre']
        advFav1_media=the_dict['favorited_advanced_season_genre']
        advFav2_media=the_dict['favorited_advanced_series_genre']
        advFav3_media=the_dict['favorited_advanced_tv_library_genre']
        advFav4_media=the_dict['favorited_advanced_tv_studio_network']
        advFav5_media=the_dict['favorited_advanced_tv_studio_network_genre']
    elif (mediaType == 'AUDIO'):
        media_played_days=the_dict['played_filter_audio'][0]
        media_created_days=the_dict['created_filter_audio'][0]
        media_played_count_comparison=the_dict['played_filter_audio'][1]
        media_created_played_count_comparison=the_dict['created_filter_audio'][1]
        media_played_count=the_dict['played_filter_audio'][2]
        media_created_played_count=the_dict['created_filter_audio'][2]
        media_created_played_behavioral_control=the_dict['created_filter_audio'][3]
        blacklisted_behavior_media=the_dict['blacklisted_behavior_audio']
        whitelisted_behavior_media=the_dict['blacklisted_behavior_audio']
        blacktagged_behavior_media=the_dict['blacklisted_behavior_audio']
        whitetagged_behavior_media=the_dict['blacklisted_behavior_audio']
        favorited_behavior_media=the_dict['blacklisted_behavior_audio']
        advFav0_media=the_dict['favorited_advanced_track_genre']
        advFav1_media=the_dict['favorited_advanced_album_genre']
        advFav2_media=the_dict['favorited_advanced_music_library_genre']
        advFav3_media=the_dict['favorited_advanced_track_artist']
        advFav4_media=the_dict['favorited_advanced_album_artist']
        advFav5_media=0
    elif (mediaType == 'AUDIOBOOK'):
        media_played_days=the_dict['played_filter_audiobook'][0]
        media_created_days=the_dict['created_filter_audiobook'][0]
        media_played_count_comparison=the_dict['played_filter_audiobook'][1]
        media_created_played_count_comparison=the_dict['created_filter_audiobook'][1]
        media_played_count=the_dict['played_filter_audiobook'][2]
        media_created_played_count=the_dict['created_filter_audiobook'][2]
        media_created_played_behavioral_control=the_dict['created_filter_audiobook'][3]
        blacklisted_behavior_media=the_dict['blacklisted_behavior_audiobook']
        whitelisted_behavior_media=the_dict['blacklisted_behavior_audiobook']
        blacktagged_behavior_media=the_dict['blacklisted_behavior_audiobook']
        whitetagged_behavior_media=the_dict['blacklisted_behavior_audiobook']
        favorited_behavior_media=the_dict['blacklisted_behavior_audiobook']
        advFav0_media=the_dict['favorited_advanced_audiobook_track_genre']
        advFav1_media=the_dict['favorited_advanced_audiobook_genre']
        advFav2_media=the_dict['favorited_advanced_audiobook_library_genre']
        advFav3_media=the_dict['favorited_advanced_audiobook_track_author']
        advFav4_media=the_dict['favorited_advanced_audiobook_author']
        advFav5_media=0

    #lists and dictionaries of items to be deleted
    deleteItems=[]
    deleteItems_Media=[]
    deleteItemsIdTracker_Media=[]
    deleteItems_createdMedia=[]
    deleteItemsIdTracker_createdMedia=[]
    deleteItems_behavioralMedia=[]
    deleteItemsIdTracker_behavioralMedia=[]
    isblacklisted_and_played_byUserId_Media={}
    isblacklisted_extraInfo_byUserId_Media={}
    iswhitelisted_and_played_byUserId_Media={}
    iswhitelisted_extraInfo_byUserId_Media={}
    isblacktagged_and_played_byUserId_Media={}
    isblacktagged_extraInfo_byUserId_Media={}
    iswhitetagged_and_played_byUserId_Media={}
    iswhitetagged_extraInfo_byUserId_Media={}
    isfavorited_and_played_byUserId_Media={}
    isfavorited_extraInfo_byUserId_Media={}
    mediaCounts_byUserId={}

    #check media is enabled before post-processing
    if ((media_played_days >= 0) or (media_created_days >= 0)):

        print_byType("\n" + mediaType + " POST PROCESSING STARTED...",print_common_delete_keep_info,the_dict)

        for user_key in media_dict:
            if (not(user_key == 'mediaType')):
                deleteItems_Media = deleteItems_Media + media_dict[user_key]['deleteItems_Media']
                deleteItemsIdTracker_Media = deleteItemsIdTracker_Media + media_dict[user_key]['deleteItemsIdTracker_Media']
                deleteItems_createdMedia = deleteItems_createdMedia + media_dict[user_key]['deleteItems_createdMedia']
                deleteItemsIdTracker_createdMedia = deleteItemsIdTracker_createdMedia + media_dict[user_key]['deleteItemsIdTracker_createdMedia']
                isblacklisted_and_played_byUserId_Media |= media_dict[user_key]['isblacklisted_and_played_byUserId_Media']
                isblacklisted_extraInfo_byUserId_Media |= media_dict[user_key]['isblacklisted_extraInfo_byUserId_Media']
                iswhitelisted_and_played_byUserId_Media |= media_dict[user_key]['iswhitelisted_and_played_byUserId_Media']
                iswhitelisted_extraInfo_byUserId_Media |= media_dict[user_key]['iswhitelisted_extraInfo_byUserId_Media']
                isblacktagged_and_played_byUserId_Media |= media_dict[user_key]['isblacktagged_and_played_byUserId_Media']
                isblacktagged_extraInfo_byUserId_Media |= media_dict[user_key]['isblacktagged_extraInfo_byUserId_Media']
                iswhitetagged_and_played_byUserId_Media |= media_dict[user_key]['iswhitetagged_and_played_byUserId_Media']
                iswhitetagged_extraInfo_byUserId_Media |= media_dict[user_key]['iswhitetagged_extraInfo_byUserId_Media']
                isfavorited_and_played_byUserId_Media |= media_dict[user_key]['isfavorited_and_played_byUserId_Media']
                isfavorited_extraInfo_byUserId_Media |= media_dict[user_key]['isfavorited_extraInfo_byUserId_Media']
                mediaCounts_byUserId |= media_dict[user_key]['mediaCounts_byUserId']

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nList Of Possible Created " + mediaType + " Items To Be Deleted: " + str(len(deleteItems_createdMedia)),3,the_dict)
            appendTo_DEBUG_log("\n" + convert2json(deleteItems_createdMedia),4,the_dict)
            appendTo_DEBUG_log("\nList Of Possible Behavioral " + mediaType + " Items To Be Deleted: " + str(len(deleteItems_behavioralMedia)),3,the_dict)
            appendTo_DEBUG_log("\n" + convert2json(deleteItems_behavioralMedia),4,the_dict)

        if (((media_played_days >= 0) or (media_created_days >= 0)) and (media_created_played_behavioral_control)):
            deleteItems_Media=deleteItems_behavioralMedia + deleteItems_createdMedia
            deleteItemsIdTracker_Media=deleteItemsIdTracker_behavioralMedia + deleteItemsIdTracker_createdMedia
        else:
            deleteItems_Media=deleteItems_behavioralMedia
            deleteItemsIdTracker_Media=deleteItemsIdTracker_behavioralMedia

        #Add blacklisted items to delete list that meet the defined played state
        if (((media_played_days >= 0) or (media_created_days >= 0)) and (blacklisted_behavior_media[3] >= 0)):
            if (not(mediaType == "AUDIO")):
                print_byType("\nPROCESSING BLACKLISTED " + mediaType + "S...",print_common_delete_keep_info,the_dict)
            else:
                print_byType("\nPROCESSING BLACKLISTED " + mediaType + "...",print_common_delete_keep_info,the_dict)
            isblacklisted_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,isblacklisted_and_played_byUserId_Media,isblacklisted_extraInfo_byUserId_Media,media_played_days,media_created_days,cut_off_date_played_media,cut_off_date_created_media,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count)
            isblacklisted_and_played_byUserId_Media,isblacklisted_extraInfo_byUserId_Media=blacklist_playedPatternCleanup(the_dict,isblacklisted_and_played_byUserId_Media,isblacklisted_extraInfo_byUserId_Media,library_matching_behavior,bluser_keys_json_verify,user_bllib_keys_json,user_bllib_netpath_json,user_bllib_path_json)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(isblacklisted_and_played_byUserId_Media,isblacklisted_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((media_played_days >= 0) or (media_created_days >= 0)):
                appendTo_DEBUG_log("\nisblacklisted_Played_" + mediaType + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(isblacklisted_and_played_byUserId_Media),3,the_dict)
                isblacklisted_extraInfo_byUserId_Media=convert_timeToString(isblacklisted_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(isblacklisted_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add whitelisted items to delete list that meet the defined played state
        if (((media_played_days >= 0) or (media_created_days >= 0)) and (whitelisted_behavior_media[3] >= 0)):
            if (not(mediaType == "AUDIO")):
                print_byType("\nPROCESSING WHITELISTED " + mediaType + "S...",print_common_delete_keep_info,the_dict)
            else:
                print_byType("\nPROCESSING WHITELISTED " + mediaType + "...",print_common_delete_keep_info,the_dict)
            iswhitelisted_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,iswhitelisted_and_played_byUserId_Media,iswhitelisted_extraInfo_byUserId_Media,media_played_days,media_created_days,cut_off_date_played_media,cut_off_date_created_media,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count)
            iswhitelisted_and_played_byUserId_Media,iswhitelisted_extraInfo_byUserId_Media=whitelist_playedPatternCleanup(the_dict,iswhitelisted_and_played_byUserId_Media,iswhitelisted_extraInfo_byUserId_Media,library_matching_behavior,wluser_keys_json_verify,user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(iswhitelisted_and_played_byUserId_Media,iswhitelisted_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((media_played_days >= 0) or (media_created_days >= 0)):
                appendTo_DEBUG_log("\niswhitelisted_Played_" + mediaType + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(iswhitelisted_and_played_byUserId_Media),3,the_dict)
                iswhitelisted_extraInfo_byUserId_Media=convert_timeToString(iswhitelisted_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(iswhitelisted_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add blacktagged items to delete list that meet the defined played state
        if (((media_played_days >= 0) or (media_created_days >= 0)) and (blacktagged_behavior_media[3] >= 0)):
            if (not(mediaType == "AUDIO")):
                print_byType("\nPROCESSING BLACKTAGGED " + mediaType + "S...",print_common_delete_keep_info,the_dict)
            else:
                print_byType("\nPROCESSING BLACKTAGGED " + mediaType + "...",print_common_delete_keep_info,the_dict)
            isblacktagged_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,isblacktagged_and_played_byUserId_Media,isblacktagged_extraInfo_byUserId_Media,media_played_days,media_created_days,cut_off_date_played_media,cut_off_date_created_media,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(isblacktagged_and_played_byUserId_Media,isblacktagged_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((media_played_days >= 0) or (media_created_days >= 0)):
                appendTo_DEBUG_log("\nisblacktagged_Played_" + mediaType + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(isblacktagged_and_played_byUserId_Media),3,the_dict)
                isblacktagged_extraInfo_byUserId_Media=convert_timeToString(isblacktagged_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(isblacktagged_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add whitetagged items to delete list that meet the defined played state
        if (((media_played_days >= 0) or (media_created_days >= 0)) and (whitetagged_behavior_media[3] >= 0)):
            if (not(mediaType == "AUDIO")):
                print_byType("\nPROCESSING WHITETAGGED " + mediaType + "S...",print_common_delete_keep_info,the_dict)
            else:
                print_byType("\nPROCESSING WHITETAGGED " + mediaType + "...",print_common_delete_keep_info,the_dict)
            iswhitetagged_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,iswhitetagged_and_played_byUserId_Media,iswhitetagged_extraInfo_byUserId_Media,media_played_days,media_created_days,cut_off_date_played_media,cut_off_date_created_media,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(iswhitetagged_and_played_byUserId_Media,iswhitetagged_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((media_played_days >= 0) or (media_created_days >= 0)):
                appendTo_DEBUG_log("\niswhitetagged_Played_" + mediaType + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(iswhitetagged_and_played_byUserId_Media),3,the_dict)
                iswhitetagged_extraInfo_byUserId_Media=convert_timeToString(iswhitetagged_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(iswhitetagged_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add favorited items to delete list that meet the defined played state
        if (((media_played_days >= 0) or (media_created_days >= 0)) and (favorited_behavior_media[3] >= 0)):
            if (not(mediaType == "AUDIO")):
                print_byType("\nPROCESSING FAVORITED " + mediaType + "S...",print_common_delete_keep_info,the_dict)
            else:
                print_byType("\nPROCESSING FAVORITED " + mediaType + "...",print_common_delete_keep_info,the_dict)
            isfavorited_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,isfavorited_and_played_byUserId_Media,isfavorited_extraInfo_byUserId_Media,media_played_days,media_created_days,cut_off_date_played_media,cut_off_date_created_media,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count)

            isfavorited_and_played_byUserId_Media,isfavorited_extraInfo_byUserId_Media=favorites_playedPatternCleanup(the_dict,isfavorited_and_played_byUserId_Media,isfavorited_extraInfo_byUserId_Media,favorited_behavior_media,advFav0_media,advFav1_media,advFav2_media,advFav3_media,advFav4_media,advFav5_media)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(isfavorited_and_played_byUserId_Media,isfavorited_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((media_played_days >= 0) or (media_created_days >= 0)):
                appendTo_DEBUG_log("\nisfavorited_Played_" + mediaType + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(isfavorited_and_played_byUserId_Media),3,the_dict)
                isfavorited_extraInfo_byUserId_Media=convert_timeToString(isfavorited_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(isfavorited_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #only applies to episodes
        if (mediaType == 'episode'):
            #Keep a minimum number of episodes
            if (((media_played_days >= 0) or (media_created_days >= 0)) and ((minimum_number_episodes >= 1) or (minimum_number_played_episodes >= 1))):
                print_byType("\nPROCESSING MINIMUM NUMBER " + mediaType + "S...",print_common_delete_keep_info,the_dict)
                #Remove episode from deletion list to meet miniumum number of remaining episodes in a series
                deleteItems_Media=get_minEpisodesToKeep(mediaCounts_byUserId, deleteItems_Media, the_dict)

            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('-----------------------------------------------------------',2,the_dict)
                appendTo_DEBUG_log('',2,the_dict)
                if (((media_played_days >= 0) or (media_created_days >= 0)) and ((minimum_number_episodes >= 1) or (minimum_number_played_episodes >= 1))):
                    appendTo_DEBUG_log('\nmediaCounts_byUserId: ',3,the_dict)
                    appendTo_DEBUG_log("\n" + convert2json(mediaCounts_byUserId),3,the_dict)
                    appendTo_DEBUG_log("\n",3,the_dict)

        deleteItems+=deleteItems_Media
        if (((media_played_days >= 0) or (media_created_days >= 0)) and (not (media_created_played_behavioral_control))):
            deleteItems+=deleteItems_createdMedia

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nFinalized List Of Items To Be Deleted: " + str(len(deleteItems)),3,the_dict)
            for mediaItem in deleteItems:
                if ('CutOffDatePlayed' in mediaItem):
                    deleteItems['CutOffDatePlayed']=str(mediaItem['CutOffDatePlayed'])
                if ('CutOffDateCreated' in mediaItem):
                    deleteItems['CutOffDateCreated']=str(mediaItem['CutOffDateCreated'])
            appendTo_DEBUG_log("\n" + convert2json(deleteItems),4,the_dict)

        print_byType("\n" + mediaType + " POST PROCESSING COMPLETE.",print_common_delete_keep_info,the_dict)

        if (the_dict['DEBUG']):
            print_common_delete_keep_info=True
        #print_byType('\n',print_common_delete_keep_info,the_dict)

    return deleteItems


def postProcessing(the_dict,media_dict,deleteItems_dict):
    if (not (the_dict['all_media_disabled'])):
        #perform post processing for each media type
        if (not (media_dict['mediaType'] == 'audiobook')):
            deleteItems_media=run_post_processing(the_dict,media_dict)
        else:
            if (isJellyfinServer(the_dict['server_brand'])):
                deleteItems_media=run_post_processing(the_dict,media_dict)
            else:
                deleteItems_media=[]

        #verify the specific mediaType is not already in the dictionary as a key
        #if it is not; go ahead and add it and set it == deleteItems_media
        #if it is; join to the existing list so the previous information is not lost
        if (not (media_dict['mediaType'] in deleteItems_dict)):
            deleteItems_dict[media_dict['mediaType']]=deleteItems_media
        else:
            deleteItems_dict[media_dict['mediaType']]+=deleteItems_media

    return deleteItems_dict