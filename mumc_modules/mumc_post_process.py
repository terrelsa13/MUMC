#!/usr/bin/env python3
import multiprocessing
from datetime import timedelta
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_blacklist_whitelist import whitelist_and_blacklist_playedPatternCleanup
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
def addItem_removeItem_fromDeleteList_usingBehavioralPatterns(action_type,postproc_dict):
    itemsDictionary=postproc_dict['is' + action_type + '_and_played_byUserId_Media']
    itemsExtraDictionary=postproc_dict['is' + action_type + '_extraInfo_byUserId_Media']
    #deleteItems=postproc_dict['deleteItems_Media']
    #deleteItemsIdTracker=postproc_dict['deleteItemsIdTracker_Media']

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
                    #all_all - Every monitored user(s) must meet the Played Count and Played Count Inequality of both the played_filter_* and created_filter_*
                    if ((itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == andIt) or
                        (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == andIt + '_' + andIt)):
                        playedControl=(isMeetingPlayedFilter_dict[itemId] & isMeetingCreatedPlayedFilter_dict[itemId]) == max_binary_value
                    #any - One or more monitored user(s) must meet the Played Count and Played Count Inequality of either the played_filter_* or created_filter_*
                    #any_any - One or more monitored user(s) must meet the Played Count and Played Count Inequality of either the played_filter_* or created_filter_*
                    elif ((itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == orIt) or
                          (itemsExtraDictionary['MonitoredUsersMeetPlayedFilter'] == orIt + '_' + orIt)):
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
                        if (not (item['Id'] in postproc_dict['deleteItemsIdTracker_Media'])):
                            postproc_dict['deleteItems_Media'].append(item)
                            postproc_dict['deleteItemsIdTracker_Media'].append(item['Id'])
                    elif (addItemToDeleteList == False):
                        while item['Id'] in postproc_dict['deleteItemsIdTracker_Media']:
                            try:
                                if (item in postproc_dict['deleteItems_Media']):
                                    postproc_dict['deleteItems_Media'].remove(item)
                                    postproc_dict['deleteItemsIdTracker_Media'].remove(item['Id'])
                                else:
                                    for delItem in postproc_dict['deleteItems_Media']:
                                        if (item['Id'] == delItem['Id']):
                                            postproc_dict['deleteItems_Media'].remove(delItem)
                                            postproc_dict['deleteItemsIdTracker_Media'].remove(item['Id'])
                            except:
                                postproc_dict['deleteItems_Media'].append('ITEM ERROR: Unable To Remove Media Item From Delete List.')
                                postproc_dict['deleteItemsIdTracker_Media'].append(item['Id'])
                                itemId_tracker.remove(itemId)

    #return postproc_dict['deleteItems_Media'],postproc_dict['deleteItemsIdTracker_Media']
    return postproc_dict


'''
#add played and created data for item during pre-processing
def update_byUserId_playedStates(extra_byUserId_Media,userKey,itemId,postproc_dict):

    extra_byUserId_Media[userKey][itemId]['PlayedDays']=postproc_dict['media_played_days']
    extra_byUserId_Media[userKey][itemId]['CreatedDays']=postproc_dict['media_created_days']
    extra_byUserId_Media[userKey][itemId]['CutOffDatePlayed']=postproc_dict['cut_off_date_played_media']
    extra_byUserId_Media[userKey][itemId]['CutOffDateCreated']=postproc_dict['cut_off_date_created_media']
    extra_byUserId_Media[userKey][itemId]['PlayedCountComparison']=postproc_dict['media_played_count_comparison']
    extra_byUserId_Media[userKey][itemId]['PlayedCount']=postproc_dict['media_played_count']
    extra_byUserId_Media[userKey][itemId]['CreatedPlayedCountComparison']=postproc_dict['media_created_played_count_comparison']
    extra_byUserId_Media[userKey][itemId]['CreatedPlayedCount']=postproc_dict['media_created_played_count']

    return extra_byUserId_Media
'''


#add played and created data for item during post-processing
def add_missingItems_byUserId_playedStates(prefix_str,postproc_dict,the_dict):
    userId_tracker=[]
    itemId_tracker=[]

    itemsDictionary=postproc_dict['is' + prefix_str + '_and_played_byUserId_Media']
    itemsExtraDictionary=postproc_dict['is' + prefix_str + '_extraInfo_byUserId_Media']

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
                    itemsExtraDictionary[subUserId][itemId]['PlayedDays']=postproc_dict['media_played_days']
                    itemsExtraDictionary[subUserId][itemId]['CreatedDays']=postproc_dict['media_created_days']
                    itemsExtraDictionary[subUserId][itemId]['CutOffDatePlayed']=postproc_dict['cut_off_date_played_media']
                    itemsExtraDictionary[subUserId][itemId]['CutOffDateCreated']=postproc_dict['cut_off_date_created_media']
                    itemsExtraDictionary[subUserId][itemId]['PlayedCountComparison']=postproc_dict['media_played_count_comparison']
                    itemsExtraDictionary[subUserId][itemId]['PlayedCount']=postproc_dict['media_played_count']
                    itemsExtraDictionary[subUserId][itemId]['CreatedPlayedCountComparison']=postproc_dict['media_created_played_count_comparison']
                    itemsExtraDictionary[subUserId][itemId]['CreatedPlayedCount']=postproc_dict['media_created_played_count']

    postproc_dict['is' + prefix_str + '_extraInfo_byUserId_Media']=itemsExtraDictionary

    #return itemsExtraDictionary
    return postproc_dict


def run_postProcessing(the_dict,media_dict):

    postproc_dict={}

    #postproc_dict['media_type']=media_dict['media_type'].casefold()
    postproc_dict['media_type_lower']=media_dict['media_type'].casefold()
    postproc_dict['media_type_upper']=media_dict['media_type'].upper()
    postproc_dict['media_type_title']=media_dict['media_type'].title()

    postproc_dict['media_dict_str']=the_dict[postproc_dict['media_type_lower'] + '_dict']['media_type'] + '_dict'

    postproc_dict['admin_settings']={}
    postproc_dict['admin_settings']['behavior']={}
    postproc_dict['admin_settings']['behavior']['matching']=the_dict['admin_settings']['behavior']['matching']
    postproc_dict['admin_settings']['users']=the_dict['admin_settings']['users']
    
    '''
    postproc_dict['bluser_keys_json_verify']=the_dict['bluser_keys_json_verify']
    postproc_dict['user_bllib_keys_json']=the_dict['user_bllib_keys_json']
    postproc_dict['user_bllib_netpath_json']=the_dict['user_bllib_netpath_json']
    postproc_dict['user_bllib_path_json']=the_dict['user_bllib_path_json']
    postproc_dict['wluser_keys_json_verify']=the_dict['wluser_keys_json_verify']
    postproc_dict['user_wllib_keys_json']=the_dict['user_wllib_keys_json']
    postproc_dict['user_wllib_netpath_json']=the_dict['user_wllib_netpath_json']
    postproc_dict['user_wllib_path_json']=the_dict['user_wllib_path_json']
    '''

    postproc_dict['advanced_settings']={}
    postproc_dict['advanced_settings']['episode_control']=the_dict['advanced_settings']['episode_control']
    #postproc_dict['minimum_number_episodes']=the_dict['minimum_number_episodes']
    #postproc_dict['minimum_number_played_episodes']=the_dict['minimum_number_played_episodes']
    postproc_dict['minimum_number_episodes']=the_dict['advanced_settings']['episode_control']['minimum_episodes']
    postproc_dict['minimum_number_played_episodes']=the_dict['advanced_settings']['episode_control']['minimum_played_episodes']
    postproc_dict['minimum_number_episodes_behavior']=the_dict['advanced_settings']['episode_control']['minimum_episodes_behavior']

    postproc_dict['media_played_days']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['played']['condition_days']
    postproc_dict['media_created_days']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['created']['condition_days']
    postproc_dict['media_played_count_comparison']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['played']['count_equality']
    postproc_dict['media_created_played_count_comparison']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['created']['count_equality']
    postproc_dict['media_played_count']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['played']['count']
    postproc_dict['media_created_played_count']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['created']['count']
    postproc_dict['media_created_played_behavioral_control']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['created']['behavioral_control']

    postproc_dict['favorited_behavior_media']={}
    postproc_dict['favorited_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['action']
    postproc_dict['favorited_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['user_conditional']
    postproc_dict['favorited_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['played_conditional']
    postproc_dict['favorited_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['action_control']
    postproc_dict['whitetagged_behavior_media']={}
    postproc_dict['whitetagged_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitetagged']['action']
    postproc_dict['whitetagged_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitetagged']['user_conditional']
    postproc_dict['whitetagged_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitetagged']['played_conditional']
    postproc_dict['whitetagged_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitetagged']['action_control']
    postproc_dict['blacktagged_behavior_media']={}
    postproc_dict['blacktagged_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacktagged']['action']
    postproc_dict['blacktagged_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacktagged']['user_conditional']
    postproc_dict['blacktagged_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacktagged']['played_conditional']
    postproc_dict['blacktagged_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacktagged']['action_control']
    postproc_dict['whitelisted_behavior_media']={}
    postproc_dict['whitelisted_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitelisted']['action']
    postproc_dict['whitelisted_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitelisted']['user_conditional']
    postproc_dict['whitelisted_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitelisted']['played_conditional']
    postproc_dict['whitelisted_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitelisted']['action_control']
    postproc_dict['blacklisted_behavior_media']={}
    postproc_dict['blacklisted_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacklisted']['action']
    postproc_dict['blacklisted_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacklisted']['user_conditional']
    postproc_dict['blacklisted_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacklisted']['played_conditional']
    postproc_dict['blacklisted_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacklisted']['action_control']
    postproc_dict['print_media_post_processing']=the_dict['advanced_settings']['console_controls'][postproc_dict['media_type_lower']]['post_processing']['show']
    postproc_dict['media_post_processing_format']=the_dict['advanced_settings']['console_controls'][postproc_dict['media_type_lower']]['post_processing']['formatting']

    '''
    if (postproc_dict['media_type'] == 'movie'):
        postproc_dict['advFav0_media']=the_dict['favorited_advanced_movie_genre']
        postproc_dict['advFav1_media']=the_dict['favorited_advanced_movie_library_genre']
        postproc_dict['advFav2_media']=0
        postproc_dict['advFav3_media']=0
        postproc_dict['advFav4_media']=0
        postproc_dict['advFav5_media']=0
        postproc_dict['print_media_post_processing']=the_dict['print_movie_post_processing_info']
        postproc_dict['media_post_processing_format']=the_dict['movie_post_processing_format']
    elif (postproc_dict['media_type'] == 'episode'):
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
    elif (postproc_dict['media_type'] == 'audio'):
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
    elif (postproc_dict['media_type'] == 'audiobook'):
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
    '''

    postproc_dict['advFav_media']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['extra']

    '''
    postproc_dict['advFav_media']=[]
    if (postproc_dict['media_type_lower'] == 'movie'):
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['genre'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['library_genre'])
        #advFav2_media=0
        #advFav3_media=0
        #advFav4_media=0
        #advFav5_media=0
    elif (postproc_dict['media_type_lower'] == 'episode'):
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['genre'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['season_genre'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['series_genre'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['library_genre'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network_genre'])
    elif (postproc_dict['media_type_lower'] == 'audio'):
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['genre'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_genre'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['library_genre'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['track_artist'])
        postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_artist'])
    elif (postproc_dict['media_type_lower'] == 'audiobook'):
        if (isJellyfinServer(postproc_dict['server_brand'])):
            postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['genre'])
            postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['audiobook_genre'])
            postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_genre'])
            postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['track_author'])
            postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['author'])
            postproc_dict['advFav_media'].append(the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_author'])
        else: #(isEmbyServer(the_dict)):
            pass

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
    '''

    #postproc_dict['cut_off_date_played_media']=the_dict['date_time_now_tz_utc'] - timedelta(postproc_dict['media_played_days'])
    #postproc_dict['cut_off_date_created_media']=the_dict['date_time_now_tz_utc'] - timedelta(postproc_dict['media_created_days'])
    postproc_dict['cut_off_date_played_media']=the_dict['cut_off_date_played_media'][postproc_dict['media_type_lower']]
    postproc_dict['cut_off_date_created_media']=the_dict['cut_off_date_created_media'][postproc_dict['media_type_lower']]

    #lists and dictionaries of items to be deleted
    postproc_dict['deleteItems']=[]
    postproc_dict['deleteItems_Media']=[]
    postproc_dict['deleteItemsIdTracker_Media']=[]
    postproc_dict['deleteItems_createdMedia']=[]
    postproc_dict['deleteItemsIdTracker_createdMedia']=[]
    postproc_dict['deleteItems_behavioralMedia']=[]
    postproc_dict['deleteItemsIdTracker_behavioralMedia']=[]
    postproc_dict['isblacklisted_and_played_byUserId_Media']={}
    postproc_dict['isblacklisted_extraInfo_byUserId_Media']={}
    postproc_dict['iswhitelisted_and_played_byUserId_Media']={}
    postproc_dict['iswhitelisted_extraInfo_byUserId_Media']={}
    postproc_dict['isblacktagged_and_played_byUserId_Media']={}
    postproc_dict['isblacktagged_extraInfo_byUserId_Media']={}
    postproc_dict['iswhitetagged_and_played_byUserId_Media']={}
    postproc_dict['iswhitetagged_extraInfo_byUserId_Media']={}
    postproc_dict['isfavorited_and_played_byUserId_Media']={}
    postproc_dict['isfavorited_extraInfo_byUserId_Media']={}
    postproc_dict['mediaCounts_byUserId']={}

    #check media is enabled before post-processing
    if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):

        print_post_processing_started(the_dict,postproc_dict)

        for user_key in media_dict:
            if (not(user_key == 'media_type')):
                postproc_dict['deleteItems_Media'] = postproc_dict['deleteItems_Media'] + media_dict[user_key]['deleteItems_Media']
                postproc_dict['deleteItemsIdTracker_Media'] = postproc_dict['deleteItemsIdTracker_Media'] + media_dict[user_key]['deleteItemsIdTracker_Media']
                postproc_dict['deleteItems_createdMedia'] = postproc_dict['deleteItems_createdMedia'] + media_dict[user_key]['deleteItems_createdMedia']
                postproc_dict['deleteItemsIdTracker_createdMedia'] = postproc_dict['deleteItemsIdTracker_createdMedia'] + media_dict[user_key]['deleteItemsIdTracker_createdMedia']
                postproc_dict['isblacklisted_and_played_byUserId_Media'] |= media_dict[user_key]['isblacklisted_and_played_byUserId_Media']
                postproc_dict['isblacklisted_extraInfo_byUserId_Media'] |= media_dict[user_key]['isblacklisted_extraInfo_byUserId_Media']
                postproc_dict['iswhitelisted_and_played_byUserId_Media'] |= media_dict[user_key]['iswhitelisted_and_played_byUserId_Media']
                postproc_dict['iswhitelisted_extraInfo_byUserId_Media'] |= media_dict[user_key]['iswhitelisted_extraInfo_byUserId_Media']
                postproc_dict['isblacktagged_and_played_byUserId_Media'] |= media_dict[user_key]['isblacktagged_and_played_byUserId_Media']
                postproc_dict['isblacktagged_extraInfo_byUserId_Media'] |= media_dict[user_key]['isblacktagged_extraInfo_byUserId_Media']
                postproc_dict['iswhitetagged_and_played_byUserId_Media'] |= media_dict[user_key]['iswhitetagged_and_played_byUserId_Media']
                postproc_dict['iswhitetagged_extraInfo_byUserId_Media'] |= media_dict[user_key]['iswhitetagged_extraInfo_byUserId_Media']
                postproc_dict['isfavorited_and_played_byUserId_Media'] |= media_dict[user_key]['isfavorited_and_played_byUserId_Media']
                postproc_dict['isfavorited_extraInfo_byUserId_Media'] |= media_dict[user_key]['isfavorited_extraInfo_byUserId_Media']
                postproc_dict['mediaCounts_byUserId'] |= media_dict[user_key]['mediaCounts_byUserId']

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nList Of Possible Created " + postproc_dict['media_type_lower'] + " Items To Be Deleted: " + str(len(postproc_dict['deleteItems_createdMedia'])),3,the_dict)
            appendTo_DEBUG_log("\n" + convert2json(postproc_dict['deleteItems_createdMedia']),4,the_dict)
            appendTo_DEBUG_log("\nList Of Possible Behavioral " + postproc_dict['media_type_lower'] + " Items To Be Deleted: " + str(len(postproc_dict['deleteItems_behavioralMedia'])),3,the_dict)
            appendTo_DEBUG_log("\n" + convert2json(postproc_dict['deleteItems_behavioralMedia']),4,the_dict)

        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['media_created_played_behavioral_control'])):
            postproc_dict['deleteItems_Media']=postproc_dict['deleteItems_behavioralMedia'] + postproc_dict['deleteItems_createdMedia']
            postproc_dict['deleteItemsIdTracker_Media']=postproc_dict['deleteItemsIdTracker_behavioralMedia'] + postproc_dict['deleteItemsIdTracker_createdMedia']
            appendTo_DEBUG_log("\nCombining List Of Possible Created media with List Of Possible Behavioral media for post processing",3,the_dict)
        else:
            postproc_dict['deleteItems_Media']=postproc_dict['deleteItems_behavioralMedia']
            postproc_dict['deleteItemsIdTracker_Media']=postproc_dict['deleteItemsIdTracker_behavioralMedia']
            appendTo_DEBUG_log("\nOnly using List Of Possible Behavioral media for post processing",3,the_dict)

        #Add blacklisted items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['blacklisted_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'blacklisted')
            postproc_dict=add_missingItems_byUserId_playedStates('blacklisted',postproc_dict,the_dict)
            postproc_dict=whitelist_and_blacklist_playedPatternCleanup('blacklisted',postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('blacklisted',postproc_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\nisblacklisted_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['isblacklisted_and_played_byUserId_Media']),3,the_dict)
                postproc_dict['isblacklisted_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['isblacklisted_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['isblacklisted_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add whitelisted items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['whitelisted_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'WHITELISTED')
            postproc_dict=add_missingItems_byUserId_playedStates('whitelisted',postproc_dict,the_dict)
            postproc_dict=whitelist_and_blacklist_playedPatternCleanup('whitelisted',postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('whitelisted',postproc_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\niswhitelisted_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['iswhitelisted_and_played_byUserId_Media']),3,the_dict)
                postproc_dict['iswhitelisted_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['iswhitelisted_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['iswhitelisted_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add blacktagged items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['blacktagged_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'BLACKTAGGED')
            postproc_dict=add_missingItems_byUserId_playedStates('blacktagged',postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('blacktagged',postproc_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\nisblacktagged_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['isblacktagged_and_played_byUserId_Media']),3,the_dict)
                postproc_dict['isblacktagged_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['isblacktagged_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['isblacktagged_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add whitetagged items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['whitetagged_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'WHITETAGGED')
            postproc_dict=add_missingItems_byUserId_playedStates('whitetagged',postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('whitetagged',postproc_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\niswhitetagged_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['iswhitetagged_and_played_byUserId_Media']),3,the_dict)
                postproc_dict['iswhitetagged_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['iswhitetagged_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['iswhitetagged_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #Add favorited items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['favorited_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'FAVORITED')
            postproc_dict=add_missingItems_byUserId_playedStates('favorited',postproc_dict,the_dict)
            postproc_dict=favorites_playedPatternCleanup(postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('favorited',postproc_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\nisfavorited_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['isfavorited_and_played_byUserId_Media']),3,the_dict)
                postproc_dict['isfavorited_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['isfavorited_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['isfavorited_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

        #only applies to episodes
        if (postproc_dict['media_type_lower'] == 'episode'):
            #Keep a minimum number of episodes
            if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and ((postproc_dict['minimum_number_episodes'] >= 1) or (postproc_dict['minimum_number_played_episodes'] >= 1))):
                print_post_processing_verbal_progress_min_episode(the_dict,postproc_dict)
                #Remove episode from deletion list to meet miniumum number of remaining episodes in a series
                postproc_dict=get_minEpisodesToKeep(postproc_dict,the_dict)

            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('-----------------------------------------------------------',2,the_dict)
                appendTo_DEBUG_log('',2,the_dict)
                if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and ((postproc_dict['minimum_number_episodes'] >= 1) or (postproc_dict['minimum_number_played_episodes'] >= 1))):
                    appendTo_DEBUG_log('\nmediaCounts_byUserId: ',3,the_dict)
                    appendTo_DEBUG_log("\n" + convert2json(postproc_dict['mediaCounts_byUserId']),3,the_dict)
                    appendTo_DEBUG_log("\n",3,the_dict)

        postproc_dict['deleteItems_Media']+=postproc_dict['deleteItems_Media']
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (not (postproc_dict['media_created_played_behavioral_control']))):
            postproc_dict['deleteItems_Media']+=postproc_dict['deleteItems_createdMedia']

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nFinalized List Of Items To Be Deleted: " + str(len(postproc_dict['deleteItems_Media'])),3,the_dict)
            for mediaItem in postproc_dict['deleteItems_Media']:
                if ('CutOffDatePlayed' in mediaItem):
                    postproc_dict['deleteItems_Media']['CutOffDatePlayed']=str(mediaItem['CutOffDatePlayed'])
                if ('CutOffDateCreated' in mediaItem):
                    postproc_dict['deleteItems_Media']['CutOffDateCreated']=str(mediaItem['CutOffDateCreated'])
            appendTo_DEBUG_log("\n" + convert2json(postproc_dict['deleteItems_Media']),4,the_dict)

        print_post_processing_completed(the_dict,postproc_dict)

    return postproc_dict['deleteItems_Media']


def postProcessing(the_dict,media_dict,deleteItems_dict):
    if (not (the_dict['all_media_disabled'])):
        #perform post processing for each media type
        #if (not (media_dict['media_type'] == 'audiobook')):
        deleteItems_media=run_postProcessing(the_dict,media_dict)
        #else:
            #if (isJellyfinServer(the_dict['server_brand'])):
                #deleteItems_media=run_postProcessing(the_dict,media_dict)
            #else:
                #deleteItems_media=[]

        #verify the specific media_type is not already in the dictionary as a key
        #if it is not; go ahead and add it and set it == deleteItems_media
        #if it is; join to the existing list so the previous information is not lost
        if (not (media_dict['media_type'] in deleteItems_dict)):
            deleteItems_dict[media_dict['media_type']]=deleteItems_media
        else:
            deleteItems_dict[media_dict['media_type']]+=deleteItems_media

    return deleteItems_dict


def init_postProcessing(the_dict):

    movie_dict=the_dict['movie_dict']
    episode_dict=the_dict['episode_dict']
    audio_dict=the_dict['audio_dict']
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        audiobook_dict=the_dict['audiobook_dict']
    else:
        audiobook_dict={}
        audiobook_dict['media_type']='audiobook'

    #when debug is disabled allow mulitprocessing
    if (not (the_dict['DEBUG'])):
        #print('\nStart Post Prcoessing: ' + datetime.now().strftime('%Y%m%d%H%M%S'))

        deleteItems_dict=multiprocessing.Manager().dict()

        #prepare for post processing; return lists of media items to be deleted
        #deleteItems_movie,deleteItems_episode,deleteItems_audio,deleteItems_audiobook=postProcessing(the_dict,movie_dict,episode_dict,audio_dict,audiobook_dict)

        #prepare for post processing; return dictionary of lists of media items to be deleted
        #setup for multiprocessing of the post processing of each media type
        mpp_movie_post_process=multiprocessing.Process(target=postProcessing,args=(the_dict,movie_dict,deleteItems_dict))
        mpp_episodePostProcess=multiprocessing.Process(target=postProcessing,args=(the_dict,episode_dict,deleteItems_dict))
        mpp_audioPostProcess=multiprocessing.Process(target=postProcessing,args=(the_dict,audio_dict,deleteItems_dict))
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            mpp_audiobookPostProcess=multiprocessing.Process(target=postProcessing,args=(the_dict,audiobook_dict,deleteItems_dict))

        #start all multi processes
        #order intentially: Audio, Episodes, Movies, Audiobooks
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            mpp_audioPostProcess.start(),mpp_episodePostProcess.start(),mpp_movie_post_process.start(),mpp_audiobookPostProcess.start()
            mpp_audioPostProcess.join(), mpp_episodePostProcess.join(), mpp_movie_post_process.join(), mpp_audiobookPostProcess.join()
            mpp_audioPostProcess.close(),mpp_episodePostProcess.close(),mpp_movie_post_process.close(),mpp_audiobookPostProcess.close()
        else:
            mpp_audioPostProcess.start(),mpp_episodePostProcess.start(),mpp_movie_post_process.start()
            mpp_audioPostProcess.join(), mpp_episodePostProcess.join(), mpp_movie_post_process.join()
            mpp_audioPostProcess.close(),mpp_episodePostProcess.close(),mpp_movie_post_process.close()
            deleteItems_dict['audiobook']=[]

        #print('Stop Post Prcoessing: ' + datetime.now().strftime('%Y%m%d%H%M%S'))
    else: #when debug enabled do not allow multiprocessing; this will allow stepping thru debug
        deleteItems_dict={}

        deleteItems_dict=postProcessing(the_dict,movie_dict,deleteItems_dict)
        deleteItems_dict=postProcessing(the_dict,episode_dict,deleteItems_dict)
        deleteItems_dict=postProcessing(the_dict,audio_dict,deleteItems_dict)
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            deleteItems_dict=postProcessing(the_dict,audiobook_dict,deleteItems_dict)
        else:
            deleteItems_dict['audiobook']=[]

    return deleteItems_dict