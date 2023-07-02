#!/usr/bin/env python3
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_blacklist import blacklist_playedPatternCleanup
from mumc_modules.mumc_whitelist import whitelist_playedPatternCleanup
from mumc_modules.mumc_favorited import favorites_playedPatternCleanup
from mumc_modules.mumc_minimum_episodes import get_minEpisodesToKeep
from mumc_modules.mumc_console_info import print_post_processing_started,print_post_processing_verbal_progress,print_post_processing_verbal_progress_min_episode,print_post_processing_completed


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


def build_behaviorPattern(isMeeting_dict,behavior_pattern_dict,itemsDictionary,itemsExtraDictionary):

    itemId=behavior_pattern_dict['itemId']
    subUserId=behavior_pattern_dict['subUserId']

    if (isMeeting_dict and (itemId in isMeeting_dict)):
        if (itemId in itemsDictionary[subUserId]):
            if (itemsExtraDictionary[subUserId][itemId]['IsMeetingAction']):
                isMeeting_dict[itemId]<<=1
                isMeeting_dict[itemId]+=1
            else:
                isMeeting_dict[itemId]<<=1
    else:
        if (itemId in itemsDictionary[subUserId]):
            if (itemsExtraDictionary[subUserId][itemId]['IsMeetingAction']):
                isMeeting_dict[itemId]=1
            else:
                isMeeting_dict[itemId]=0
        else:
            isMeeting_dict[itemId]=1

    return isMeeting_dict


#Add/Remove item to/from delete list if meeting favorite/whitetagged/blacktagged/whitelisted pattern and played pattern
def addItem_removeItem_fromDeleteList_usingBehavioralPatterns(itemsDictionary,itemsExtraDictionary,deleteItems,deleteItemsIdTracker):
    isMeetingAction_dict={}
    isMeetingPlayedFilter_dict={}
    isMeetingCreatedPlayedFilter_dict={}
    behavior_pattern_dict={}
    itemId_tracker=[]
    userId_tracker=[]

    andIt='all'
    orIt='any'

    addIt='delete'
    #removeIt='keep'

    if (('MonitoredUsersAction' in itemsExtraDictionary) and ('MonitoredUsersMeetPlayedFilter' in itemsExtraDictionary)):
        #actionFilter=itemsExtraDictionary['MonitoredUsersAction']
        methodFilter=itemsExtraDictionary['ConfiguredBehavior']
        behaviorFilter=itemsExtraDictionary['ActionBehavior']
        #wordFilter=itemsExtraDictionary['ActionType']

        for userId in itemsDictionary:
            userId_tracker.append(userId)

        userId_tracker_len=len(userId_tracker)
        max_binary_value=(2**userId_tracker_len)-1

        for userId in itemsDictionary:
            for itemId in itemsDictionary[userId]:

                behavior_pattern_dict['itemId']=itemId

                if not (itemId in itemId_tracker):
                    itemId_tracker.append(itemId)
                    item=itemsDictionary[userId][itemId]

                    for subUserId in userId_tracker:

                        behavior_pattern_dict['subUserId']=subUserId

                        isMeetingAction_dict=build_behaviorPattern(isMeetingAction_dict,behavior_pattern_dict,itemsDictionary,itemsExtraDictionary)
                        isMeetingPlayedFilter_dict=build_behaviorPattern(isMeetingPlayedFilter_dict,behavior_pattern_dict,itemsDictionary,itemsExtraDictionary)
                        isMeetingCreatedPlayedFilter_dict=build_behaviorPattern(isMeetingCreatedPlayedFilter_dict,behavior_pattern_dict,itemsDictionary,itemsExtraDictionary)

                    #all - Every monitored user must have the media item blacklisted/whitelites/blacktagged/whitetagged/favortied
                    if (itemsExtraDictionary['MonitoredUsersAction'] == andIt):
                        actionControl=isMeetingAction_dict[itemId] == max_binary_value
                    #any - One or more monitored users must have the media item blacklisted/whitelisted/favorited (does not apply to blacktagged/whitetagged)
                    elif (itemsExtraDictionary['MonitoredUsersAction'] == orIt):
                        actionControl=isMeetingAction_dict[itemId] >= 1
                    #ignore - Should never get here
                    else: #(itemsExtraDictionary['MonitoredUsersAction'] == 'ignore'):
                        #actionControl=True
                        raise RuntimeError('\nMedia Item with itemId: ' + itemId + ' does not have appropriate actionControl assigned during post processing of ' + itemsExtraDictionary['ActionType'] + ' items')

                    #all - Every monitored user(s) must meet the Played Count and Played Count Inequality of both the played_filter_* and created_filter_*
                    if (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == andIt):
                        playedControl=(isMeetingPlayedFilter_dict[itemId] & isMeetingCreatedPlayedFilter_dict[itemId]) == max_binary_value
                    #any - One or more monitored user(s) must meet the Played Count and Played Count Inequality of either the played_filter_* or created_filter_*
                    elif (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == orIt):
                        playedControl=(isMeetingPlayedFilter_dict[itemId] | isMeetingCreatedPlayedFilter_dict[itemId]) >= 1
                    #all_any - Every monitored user(s) must meet the Played Count and Played Count Inequality of either the played_filter_* or created_filter_*
                    elif (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == (andIt + '_' + orIt)):
                        playedControl=(isMeetingPlayedFilter_dict[itemId] | isMeetingCreatedPlayedFilter_dict[itemId]) == max_binary_value
                    #any_all - One or more monitored user(s) must meet the Played Count and Played Count Inequality of both the played_filter_* and created_filter_*
                    elif (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == (orIt + '_' + andIt)):
                        playedControl=(isMeetingPlayedFilter_dict[itemId] & isMeetingCreatedPlayedFilter_dict[itemId]) >= 1
                    #all_played - Every monitored user(s) must meet the Played Count and Played Count Inequality of the played_filter_*
                    elif (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == (andIt + '_played')):
                        playedControl=isMeetingPlayedFilter_dict[itemId] == max_binary_value
                    #any_played - One or more monitored user(s) must meet the Played Count and Played Count Inequality of the played_filter_*
                    elif (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == (orIt + '_played')):
                        playedControl=isMeetingPlayedFilter_dict[itemId] >= 1
                    #all_created - Every monitored user(s) must meet the Played Count and Played Count Inequality of the created_filter_*
                    elif (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == (andIt + '_created')):
                        playedControl=isMeetingCreatedPlayedFilter_dict[itemId] == max_binary_value
                    #any_created - One or more monitored user(s) must meet the Played Count and Played Count Inequality of the created_filter_*
                    elif (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == (orIt + '_created')):
                        playedControl=isMeetingCreatedPlayedFilter_dict[itemId] >= 1
                    #ignore - Ignore if monitored user(s) meet the Played Count and Played Count Inequality of both the played_filter_* and created_filter_*
                    else: #(itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == 'ignore'):
                        playedControl=True

                    behavioralControl=actionControl and playedControl

                    if (behavioralControl):
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
                                deleteItems.append('ITEM ERROR: Unable To Remove Media Item From Delete List.')
                                deleteItemsIdTracker.append(item['Id'])
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
def add_missingItems_byUserId_playedStates(the_dict,itemsDictionary,itemsExtraDictionary,postproc_dict):
    userId_tracker=[]
    itemId_tracker=[]

    media_played_days=postproc_dict['media_played_days']
    media_created_days=postproc_dict['media_created_days']
    cut_off_date_played_media=postproc_dict['cut_off_date_played_media']
    cut_off_date_created_media=postproc_dict['cut_off_date_created_media']
    media_played_count_comparison=postproc_dict['media_played_count_comparison']
    media_played_count=postproc_dict['media_played_count']
    media_created_played_count_comparison=postproc_dict['media_created_played_count_comparison']
    media_created_played_count=postproc_dict['media_created_played_count']

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

    postproc_dict={}

    postproc_dict['mediaType']=media_dict['mediaType'].upper()

    postproc_dict['library_matching_behavior']=the_dict['library_matching_behavior']
    postproc_dict['bluser_keys_json_verify']=the_dict['bluser_keys_json_verify']
    postproc_dict['user_bllib_keys_json']=the_dict['user_bllib_keys_json']
    postproc_dict['user_bllib_netpath_json']=the_dict['user_bllib_netpath_json']
    postproc_dict['user_bllib_path_json']=the_dict['user_bllib_path_json']
    postproc_dict['wluser_keys_json_verify']=the_dict['wluser_keys_json_verify']
    postproc_dict['user_wllib_keys_json']=the_dict['user_wllib_keys_json']
    postproc_dict['user_wllib_netpath_json']=the_dict['user_wllib_netpath_json']
    postproc_dict['user_wllib_path_json']=the_dict['user_wllib_path_json']

    postproc_dict['cut_off_date_played_media']=the_dict['cut_off_date_played_media']
    postproc_dict['cut_off_date_created_media']=the_dict['cut_off_date_created_media']
    postproc_dict['minimum_number_episodes']=the_dict['minimum_number_episodes']
    postproc_dict['minimum_number_played_episodes']=the_dict['minimum_number_played_episodes']

    if (postproc_dict['mediaType'] == 'MOVIE'):
        postproc_dict['media_played_days']=the_dict['played_filter_movie'][0]
        postproc_dict['media_created_days']=the_dict['created_filter_movie'][0]
        postproc_dict['media_played_count_comparison']=the_dict['played_filter_movie'][1]
        postproc_dict['media_created_played_count_comparison']=the_dict['created_filter_movie'][1]
        postproc_dict['media_played_count']=the_dict['played_filter_movie'][2]
        postproc_dict['media_created_played_count']=the_dict['created_filter_movie'][2]
        postproc_dict['media_created_played_behavioral_control']=the_dict['created_filter_movie'][3]
        postproc_dict['blacklisted_behavior_media']=the_dict['blacklisted_behavior_movie']
        postproc_dict['whitelisted_behavior_media']=the_dict['blacklisted_behavior_movie']
        postproc_dict['blacktagged_behavior_media']=the_dict['blacklisted_behavior_movie']
        postproc_dict['whitetagged_behavior_media']=the_dict['blacklisted_behavior_movie']
        postproc_dict['favorited_behavior_media']=the_dict['blacklisted_behavior_movie']
        postproc_dict['advFav0_media']=the_dict['favorited_advanced_movie_genre']
        postproc_dict['advFav1_media']=the_dict['favorited_advanced_movie_library_genre']
        postproc_dict['advFav2_media']=0
        postproc_dict['advFav3_media']=0
        postproc_dict['advFav4_media']=0
        postproc_dict['advFav5_media']=0
        postproc_dict['print_media_post_processing']=the_dict['print_movie_post_processing_info']
        postproc_dict['media_post_processing_format']=the_dict['movie_post_processing_format']
    elif (postproc_dict['mediaType'] == 'EPISODE'):
        postproc_dict['media_played_days']=the_dict['played_filter_episode'][0]
        postproc_dict['media_created_days']=the_dict['created_filter_episode'][0]
        postproc_dict['media_played_count_comparison']=the_dict['played_filter_episode'][1]
        postproc_dict['media_created_played_count_comparison']=the_dict['created_filter_episode'][1]
        postproc_dict['media_played_count']=the_dict['played_filter_episode'][2]
        postproc_dict['media_created_played_count']=the_dict['created_filter_episode'][2]
        postproc_dict['media_created_played_behavioral_control']=the_dict['created_filter_episode'][3]
        postproc_dict['blacklisted_behavior_media']=the_dict['blacklisted_behavior_episode']
        postproc_dict['whitelisted_behavior_media']=the_dict['blacklisted_behavior_episode']
        postproc_dict['blacktagged_behavior_media']=the_dict['blacklisted_behavior_episode']
        postproc_dict['whitetagged_behavior_media']=the_dict['blacklisted_behavior_episode']
        postproc_dict['favorited_behavior_media']=the_dict['blacklisted_behavior_episode']
        postproc_dict['advFav0_media']=the_dict['favorited_advanced_episode_genre']
        postproc_dict['advFav1_media']=the_dict['favorited_advanced_season_genre']
        postproc_dict['advFav2_media']=the_dict['favorited_advanced_series_genre']
        postproc_dict['advFav3_media']=the_dict['favorited_advanced_tv_library_genre']
        postproc_dict['advFav4_media']=the_dict['favorited_advanced_tv_studio_network']
        postproc_dict['advFav5_media']=the_dict['favorited_advanced_tv_studio_network_genre']
        postproc_dict['print_media_post_processing']=the_dict['print_episode_post_processing_info']
        postproc_dict['media_post_processing_format']=the_dict['episode_post_processing_format']
    elif (postproc_dict['mediaType'] == 'AUDIO'):
        postproc_dict['media_played_days']=the_dict['played_filter_audio'][0]
        postproc_dict['media_created_days']=the_dict['created_filter_audio'][0]
        postproc_dict['media_played_count_comparison']=the_dict['played_filter_audio'][1]
        postproc_dict['media_created_played_count_comparison']=the_dict['created_filter_audio'][1]
        postproc_dict['media_played_count']=the_dict['played_filter_audio'][2]
        postproc_dict['media_created_played_count']=the_dict['created_filter_audio'][2]
        postproc_dict['media_created_played_behavioral_control']=the_dict['created_filter_audio'][3]
        postproc_dict['blacklisted_behavior_media']=the_dict['blacklisted_behavior_audio']
        postproc_dict['whitelisted_behavior_media']=the_dict['blacklisted_behavior_audio']
        postproc_dict['blacktagged_behavior_media']=the_dict['blacklisted_behavior_audio']
        postproc_dict['whitetagged_behavior_media']=the_dict['blacklisted_behavior_audio']
        postproc_dict['favorited_behavior_media']=the_dict['blacklisted_behavior_audio']
        postproc_dict['advFav0_media']=the_dict['favorited_advanced_track_genre']
        postproc_dict['advFav1_media']=the_dict['favorited_advanced_album_genre']
        postproc_dict['advFav2_media']=the_dict['favorited_advanced_music_library_genre']
        postproc_dict['advFav3_media']=the_dict['favorited_advanced_track_artist']
        postproc_dict['advFav4_media']=the_dict['favorited_advanced_album_artist']
        postproc_dict['advFav5_media']=0
        postproc_dict['print_media_post_processing']=the_dict['print_audio_post_processing_info']
        postproc_dict['media_post_processing_format']=the_dict['audio_post_processing_format']
    elif (postproc_dict['mediaType'] == 'AUDIOBOOK'):
        postproc_dict['media_played_days']=the_dict['played_filter_audiobook'][0]
        postproc_dict['media_created_days']=the_dict['created_filter_audiobook'][0]
        postproc_dict['media_played_count_comparison']=the_dict['played_filter_audiobook'][1]
        postproc_dict['media_created_played_count_comparison']=the_dict['created_filter_audiobook'][1]
        postproc_dict['media_played_count']=the_dict['played_filter_audiobook'][2]
        postproc_dict['media_created_played_count']=the_dict['created_filter_audiobook'][2]
        postproc_dict['media_created_played_behavioral_control']=the_dict['created_filter_audiobook'][3]
        postproc_dict['blacklisted_behavior_media']=the_dict['blacklisted_behavior_audiobook']
        postproc_dict['whitelisted_behavior_media']=the_dict['blacklisted_behavior_audiobook']
        postproc_dict['blacktagged_behavior_media']=the_dict['blacklisted_behavior_audiobook']
        postproc_dict['whitetagged_behavior_media']=the_dict['blacklisted_behavior_audiobook']
        postproc_dict['favorited_behavior_media']=the_dict['blacklisted_behavior_audiobook']
        postproc_dict['advFav0_media']=the_dict['favorited_advanced_audiobook_track_genre']
        postproc_dict['advFav1_media']=the_dict['favorited_advanced_audiobook_genre']
        postproc_dict['advFav2_media']=the_dict['favorited_advanced_audiobook_library_genre']
        postproc_dict['advFav3_media']=the_dict['favorited_advanced_audiobook_track_author']
        postproc_dict['advFav4_media']=the_dict['favorited_advanced_audiobook_author']
        postproc_dict['advFav5_media']=the_dict['favorited_advanced_audiobook_library_author']
        postproc_dict['print_media_post_processing']=the_dict['print_audiobook_post_processing_info']
        postproc_dict['media_post_processing_format']=the_dict['audiobook_post_processing_format']

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
    if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):

        print_post_processing_started(the_dict,postproc_dict)

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
            appendTo_DEBUG_log("\nList Of Possible Created " + postproc_dict['mediaType'] + " Items To Be Deleted: " + str(len(deleteItems_createdMedia)),3,the_dict)
            appendTo_DEBUG_log("\n" + convert2json(deleteItems_createdMedia),4,the_dict)
            appendTo_DEBUG_log("\nList Of Possible Behavioral " + postproc_dict['mediaType'] + " Items To Be Deleted: " + str(len(deleteItems_behavioralMedia)),3,the_dict)
            appendTo_DEBUG_log("\n" + convert2json(deleteItems_behavioralMedia),4,the_dict)

        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['media_created_played_behavioral_control'])):
            deleteItems_Media=deleteItems_behavioralMedia + deleteItems_createdMedia
            deleteItemsIdTracker_Media=deleteItemsIdTracker_behavioralMedia + deleteItemsIdTracker_createdMedia
            appendTo_DEBUG_log("\nCombining List Of Possible Created media with List Of Possible Behavioral media for post processing",3,the_dict)
        else:
            deleteItems_Media=deleteItems_behavioralMedia
            deleteItemsIdTracker_Media=deleteItemsIdTracker_behavioralMedia
            appendTo_DEBUG_log("\nOnly using List Of Possible Behavioral media for post processing",3,the_dict)

        #Add blacklisted items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['blacklisted_behavior_media'][3] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'BLACKLISTED')
            isblacklisted_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,isblacklisted_and_played_byUserId_Media,isblacklisted_extraInfo_byUserId_Media,postproc_dict)
            isblacklisted_and_played_byUserId_Media,isblacklisted_extraInfo_byUserId_Media=blacklist_playedPatternCleanup(the_dict,isblacklisted_and_played_byUserId_Media,isblacklisted_extraInfo_byUserId_Media,postproc_dict)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(isblacklisted_and_played_byUserId_Media,isblacklisted_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\nisblacklisted_Played_" + postproc_dict['mediaType'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(isblacklisted_and_played_byUserId_Media),3,the_dict)
                isblacklisted_extraInfo_byUserId_Media=convert_timeToString(isblacklisted_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(isblacklisted_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add whitelisted items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['whitelisted_behavior_media'][3] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'WHITELISTED')
            iswhitelisted_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,iswhitelisted_and_played_byUserId_Media,iswhitelisted_extraInfo_byUserId_Media,postproc_dict)
            iswhitelisted_and_played_byUserId_Media,iswhitelisted_extraInfo_byUserId_Media=whitelist_playedPatternCleanup(the_dict,iswhitelisted_and_played_byUserId_Media,iswhitelisted_extraInfo_byUserId_Media,postproc_dict)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(iswhitelisted_and_played_byUserId_Media,iswhitelisted_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\niswhitelisted_Played_" + postproc_dict['mediaType'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(iswhitelisted_and_played_byUserId_Media),3,the_dict)
                iswhitelisted_extraInfo_byUserId_Media=convert_timeToString(iswhitelisted_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(iswhitelisted_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add blacktagged items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['blacktagged_behavior_media'][3] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'BLACKTAGGED')
            isblacktagged_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,isblacktagged_and_played_byUserId_Media,isblacktagged_extraInfo_byUserId_Media,postproc_dict)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(isblacktagged_and_played_byUserId_Media,isblacktagged_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\nisblacktagged_Played_" + postproc_dict['mediaType'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(isblacktagged_and_played_byUserId_Media),3,the_dict)
                isblacktagged_extraInfo_byUserId_Media=convert_timeToString(isblacktagged_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(isblacktagged_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add whitetagged items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['whitetagged_behavior_media'][3] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'WHITETAGGED')
            iswhitetagged_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,iswhitetagged_and_played_byUserId_Media,iswhitetagged_extraInfo_byUserId_Media,postproc_dict)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(iswhitetagged_and_played_byUserId_Media,iswhitetagged_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\niswhitetagged_Played_" + postproc_dict['mediaType'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(iswhitetagged_and_played_byUserId_Media),3,the_dict)
                iswhitetagged_extraInfo_byUserId_Media=convert_timeToString(iswhitetagged_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(iswhitetagged_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add favorited items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['favorited_behavior_media'][3] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'FAVORITED')
            isfavorited_extraInfo_byUserId_Media=add_missingItems_byUserId_playedStates(the_dict,isfavorited_and_played_byUserId_Media,isfavorited_extraInfo_byUserId_Media,postproc_dict)

            isfavorited_and_played_byUserId_Media,isfavorited_extraInfo_byUserId_Media=favorites_playedPatternCleanup(the_dict,isfavorited_and_played_byUserId_Media,isfavorited_extraInfo_byUserId_Media,postproc_dict)
            deleteItems_Media,deleteItemsIdTracker_Media=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(isfavorited_and_played_byUserId_Media,isfavorited_extraInfo_byUserId_Media,deleteItems_Media,deleteItemsIdTracker_Media)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\nisfavorited_Played_" + postproc_dict['mediaType'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(isfavorited_and_played_byUserId_Media),3,the_dict)
                isfavorited_extraInfo_byUserId_Media=convert_timeToString(isfavorited_extraInfo_byUserId_Media)
                appendTo_DEBUG_log("\n" + convert2json(isfavorited_extraInfo_byUserId_Media),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #only applies to episodes
        if (postproc_dict['mediaType'] == 'episode'):
            #Keep a minimum number of episodes
            if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and ((postproc_dict['minimum_number_episodes'] >= 1) or (postproc_dict['minimum_number_played_episodes'] >= 1))):
                print_post_processing_verbal_progress_min_episode(the_dict,postproc_dict)
                #Remove episode from deletion list to meet miniumum number of remaining episodes in a series
                deleteItems_Media=get_minEpisodesToKeep(mediaCounts_byUserId, deleteItems_Media, the_dict)

            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('-----------------------------------------------------------',2,the_dict)
                appendTo_DEBUG_log('',2,the_dict)
                if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and ((postproc_dict['minimum_number_episodes'] >= 1) or (postproc_dict['minimum_number_played_episodes'] >= 1))):
                    appendTo_DEBUG_log('\nmediaCounts_byUserId: ',3,the_dict)
                    appendTo_DEBUG_log("\n" + convert2json(mediaCounts_byUserId),3,the_dict)
                    appendTo_DEBUG_log("\n",3,the_dict)

        deleteItems+=deleteItems_Media
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (not (postproc_dict['media_created_played_behavioral_control']))):
            deleteItems+=deleteItems_createdMedia

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nFinalized List Of Items To Be Deleted: " + str(len(deleteItems)),3,the_dict)
            for mediaItem in deleteItems:
                if ('CutOffDatePlayed' in mediaItem):
                    deleteItems['CutOffDatePlayed']=str(mediaItem['CutOffDatePlayed'])
                if ('CutOffDateCreated' in mediaItem):
                    deleteItems['CutOffDateCreated']=str(mediaItem['CutOffDateCreated'])
            appendTo_DEBUG_log("\n" + convert2json(deleteItems),4,the_dict)

        print_post_processing_completed(the_dict,postproc_dict)

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