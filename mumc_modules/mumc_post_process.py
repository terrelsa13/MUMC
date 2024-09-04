import multiprocessing
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_blacklist_whitelist import get_isItemWhitelisted_Blacklisted
from mumc_modules.mumc_minimum_episodes import get_minEpisodesToKeep
from mumc_modules.mumc_console_info import print_post_processing_started,print_post_processing_verbal_progress,print_post_processing_verbal_progress_min_episode,print_post_processing_completed
from mumc_modules.mumc_days_since import convert_timeToString
from mumc_modules.mumc_tagged import get_isMOVIE_Tagged,get_isEPISODE_Tagged,get_isAUDIO_Tagged,get_isAUDIOBOOK_Tagged,get_isPlayedCreated_FilterStatementTag
from mumc_modules.mumc_played_created import get_playedDays_createdPlayedDays_playedCounts_createdPlayedCounts,getTag_playedDays_createdPlayedDays_playedCounts_createdPlayedCounts
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo
from mumc_modules.mumc_favorited import get_isMOVIE_Fav,get_isEPISODE_Fav,get_isAUDIO_Fav,get_isAUDIOBOOK_Fav,get_isMOVIE_AdvancedFav,get_isEPISODE_AdvancedFav,get_isAUDIO_AdvancedFav,get_isAUDIOBOOK_AdvancedFav
#from memory_profiler import profile


def build_behaviorPattern(isMeeting_dict,behavior_pattern_dict,isbehavior_extraInfo_byUserId_Media):

    itemId=behavior_pattern_dict['itemId']
    userId=behavior_pattern_dict['userId']
    userBehaviorInfo=isbehavior_extraInfo_byUserId_Media[userId]

    if (isMeeting_dict and (itemId in isMeeting_dict)):
        if (itemId in userBehaviorInfo):
            if (userBehaviorInfo[itemId][isMeeting_dict['IsMeeting']]):
                isMeeting_dict[itemId]<<=1
                isMeeting_dict[itemId]+=1
            else:
                isMeeting_dict[itemId]<<=1
        else:
            isMeeting_dict[itemId]<<=1
    else:
        if (itemId in userBehaviorInfo):
            if (userBehaviorInfo[itemId][isMeeting_dict['IsMeeting']]):
                isMeeting_dict[itemId]=1
            else:
                isMeeting_dict[itemId]=0
        else:
            isMeeting_dict[itemId]=0

    return isMeeting_dict


#Add/Remove item to/from delete list if meeting favorite/whitetagged/blacktagged/whitelisted pattern and played pattern
def addItem_removeItem_fromDeleteList_usingBehavioralPatterns(behavior_str,postproc_dict,thisFilterTag=None):
    isbehavior_extraInfo_byUserId_Media=postproc_dict['is' + behavior_str + '_extraInfo_byUserId_Media']
    isbehavior_extraInfo_Tracker=isbehavior_extraInfo_byUserId_Media['is' + behavior_str + '_extraInfo_Tracker']
    isbehavior_extraInfo_byUserId_Media['userId_list']=postproc_dict['enabled_user_ids']
    media_data=postproc_dict['media_data']

    isMeetingAction_dict={'IsMeeting':'IsMeetingAction'}
    isMeetingPlayedFilter_dict={'IsMeeting':'IsMeetingPlayedFilter'}
    isMeetingCreatedPlayedFilter_dict={'IsMeeting':'IsMeetingCreatedPlayedFilter'}
    behavior_pattern_dict={}

    andIt='all'
    orIt='any'

    #add item to the delete list
    deleteIt='delete'
    #remove item from the delete list
    #keepIt='keep'
    #no action taken on item
    #noneIt=None

    for itemId in isbehavior_extraInfo_Tracker:

        #if (not (thisFilterTag == None)):
            

        if (('MonitoredUsersAction' in isbehavior_extraInfo_byUserId_Media) and ('MonitoredUsersMeetPlayedFilter' in isbehavior_extraInfo_byUserId_Media)):
            configuredBehavior=isbehavior_extraInfo_byUserId_Media['ConfiguredBehavior']
            actionControl=isbehavior_extraInfo_byUserId_Media['ActionControl']
            dynamicBehavior=isbehavior_extraInfo_byUserId_Media['DynamicBehavior']
            monitoredUsersMeetPlayedFilter=isbehavior_extraInfo_byUserId_Media['MonitoredUsersMeetPlayedFilter']
            monitoredUsersAction=isbehavior_extraInfo_byUserId_Media['MonitoredUsersAction']

            if (actionControl):

                max_binary_value_base=(2**len(isbehavior_extraInfo_byUserId_Media['userId_list']))-1

                #reset max_binary_value to max_binary_value_base before processing the next item
                max_binary_value=max_binary_value_base

                #if (not (itemId in behavior_pattern_dict)):
                behavior_pattern_dict['itemId']=itemId

                for userId in isbehavior_extraInfo_byUserId_Media['userId_list']:

                    behavior_pattern_dict['userId']=userId

                    isMeetingAction_dict=build_behaviorPattern(isMeetingAction_dict,behavior_pattern_dict,isbehavior_extraInfo_byUserId_Media)
                    isMeetingPlayedFilter_dict=build_behaviorPattern(isMeetingPlayedFilter_dict,behavior_pattern_dict,isbehavior_extraInfo_byUserId_Media)
                    isMeetingCreatedPlayedFilter_dict=build_behaviorPattern(isMeetingCreatedPlayedFilter_dict,behavior_pattern_dict,isbehavior_extraInfo_byUserId_Media)

                #all - Every monitored user must have the media item blacklisted/whitelisted/blacktagged/whitetagged/favorited
                if (monitoredUsersAction == andIt):
                    if (not dynamicBehavior):
                        userConditional=(isMeetingAction_dict[itemId] == max_binary_value)
                    else:
                        #set the new mask for dynamic_behavior
                        max_binary_value=isMeetingAction_dict[itemId]
                        #we are only checking users with the matching conditional_behavior
                        if (max_binary_value):
                            #this is automatically True if max_binary_value > 0; meaning at least one user has the matching conditional_behavior
                            userConditional=True
                        else:
                            #this is automatically false if max_binary_value == 0; meaning no users have the matching conditional_behavior
                            userConditional=False
                #any - One or more monitored users must have the media item blacklisted/whitelisted/favorited (does not apply to blacktagged/whitetagged)
                elif (monitoredUsersAction == orIt):
                    if (not dynamicBehavior):
                        userConditional=(isMeetingAction_dict[itemId] >= 1)
                    else:
                        #set the new mask for dynamic_behavior
                        max_binary_value=isMeetingAction_dict[itemId]
                        #we are only checking users with the matching conditional_behavior
                        if (max_binary_value):
                            #this is automatically True if max_binary_value > 0; meaning at least one user has the matching conditional_behavior
                            userConditional=True
                        else:
                            #this is automatically false if max_binary_value == 0; meaning no users have the matching conditional_behavior
                            userConditional=False
                #ignore - Should never get here
                else: #(monitoredUsersAction == 'ignore'):
                    raise RuntimeError('\nMedia Item with itemId: ' + itemId + ' does not have appropriate userConditional assigned during post processing of ' + isbehavior_extraInfo_byUserId_Media['ActionType'] + ' items')

                #all - Every monitored user(s) must meet the Played Count and Played Count Inequality of both the played_filter_* and created_filter_*
                #all_all - Every monitored user(s) must meet the Played Count and Played Count Inequality of both the played_filter_* and created_filter_*
                if ((monitoredUsersMeetPlayedFilter == andIt) or
                    (monitoredUsersMeetPlayedFilter == andIt + '_' + andIt)):
                    if (not (dynamicBehavior)):
                        playedControl=((isMeetingPlayedFilter_dict[itemId] & isMeetingCreatedPlayedFilter_dict[itemId]) == max_binary_value)
                    else:
                        playedControl=(((isMeetingPlayedFilter_dict[itemId] & isMeetingCreatedPlayedFilter_dict[itemId]) & max_binary_value) == max_binary_value)
                #any - One or more monitored user(s) must meet the Played Count and Played Count Inequality of either the played_filter_* or created_filter_*
                #any_any - One or more monitored user(s) must meet the Played Count and Played Count Inequality of either the played_filter_* or created_filter_*
                elif ((monitoredUsersMeetPlayedFilter == orIt) or
                    (monitoredUsersMeetPlayedFilter == orIt + '_' + orIt)):
                    if (not (dynamicBehavior)):
                        playedControl=((isMeetingPlayedFilter_dict[itemId] | isMeetingCreatedPlayedFilter_dict[itemId]) >= 1)
                    else:
                        playedControl=(((isMeetingPlayedFilter_dict[itemId] | isMeetingCreatedPlayedFilter_dict[itemId]) & max_binary_value) >= 1)
                #all_any - Every monitored user(s) must meet the Played Count and Played Count Inequality of either the played_filter_* or created_filter_*
                elif (monitoredUsersMeetPlayedFilter == (andIt + '_' + orIt)):
                    if (not (dynamicBehavior)):
                        playedControl=((isMeetingPlayedFilter_dict[itemId] | isMeetingCreatedPlayedFilter_dict[itemId]) == max_binary_value)
                    else:
                        playedControl=(((isMeetingPlayedFilter_dict[itemId] | isMeetingCreatedPlayedFilter_dict[itemId]) & max_binary_value) == max_binary_value)
                #any_all - One or more monitored user(s) must meet the Played Count and Played Count Inequality of both the played_filter_* and created_filter_*
                elif (monitoredUsersMeetPlayedFilter == (orIt + '_' + andIt)):
                    if (not (dynamicBehavior)):
                        playedControl=((isMeetingPlayedFilter_dict[itemId] & isMeetingCreatedPlayedFilter_dict[itemId]) >= 1)
                    else:
                        playedControl=(((isMeetingPlayedFilter_dict[itemId] & isMeetingCreatedPlayedFilter_dict[itemId]) & max_binary_value) >= 1)
                #all_played - Every monitored user(s) must meet the Played Count and Played Count Inequality of the played_filter_*
                elif (monitoredUsersMeetPlayedFilter == (andIt + '_played')):
                    if (not (dynamicBehavior)):
                        playedControl=(isMeetingPlayedFilter_dict[itemId] == max_binary_value)
                    else:
                        playedControl=((isMeetingPlayedFilter_dict[itemId] & max_binary_value) == max_binary_value)
                #any_played - One or more monitored user(s) must meet the Played Count and Played Count Inequality of the played_filter_*
                elif (monitoredUsersMeetPlayedFilter == (orIt + '_played')):
                    if (not (dynamicBehavior)):
                        playedControl=(isMeetingPlayedFilter_dict[itemId] >= 1)
                    else:
                        playedControl=((isMeetingPlayedFilter_dict[itemId] & max_binary_value) >= 1)
                #all_created - Every monitored user(s) must meet the Played Count and Played Count Inequality of the created_filter_*
                elif (monitoredUsersMeetPlayedFilter == (andIt + '_created')):
                    if (not (dynamicBehavior)):
                        playedControl=(isMeetingCreatedPlayedFilter_dict[itemId] == max_binary_value)
                    else:
                        playedControl=((isMeetingCreatedPlayedFilter_dict[itemId] & max_binary_value) == max_binary_value)
                #any_created - One or more monitored user(s) must meet the Played Count and Played Count Inequality of the created_filter_*
                elif (monitoredUsersMeetPlayedFilter == (orIt + '_created')):
                    if (not (dynamicBehavior)):
                        playedControl=(isMeetingCreatedPlayedFilter_dict[itemId] >= 1)
                    else:
                        playedControl=((isMeetingCreatedPlayedFilter_dict[itemId] & max_binary_value) >= 1)
                #ignore - Ignore if monitored user(s) meet the Played Count and Played Count Inequality of both the played_filter_* and created_filter_*
                else: #(monitoredUsersMeetPlayedFilter == 'ignore'):
                    playedControl=True

                behavioralControl=(userConditional and playedControl)

                if (behavioralControl):
                    if ((actionControl == 0) or (actionControl == 1) or (actionControl == 2)):
                        #No action taken on True
                        addItemToDeleteList=None
                    elif ((actionControl == 3) or (actionControl == 4) or (actionControl == 5)):
                        #Action taken on True
                        if (configuredBehavior == deleteIt):
                            addItemToDeleteList=True
                        else: #(configuredBehavior == keepIt):
                            addItemToDeleteList=False
                    else: #((actionControl == 6) or (actionControl == 7) or (actionControl == 8)):
                        #Opposite action taken on True
                        if (configuredBehavior == deleteIt):
                            addItemToDeleteList=False
                        else: #(configuredBehavior == keepIt):
                            addItemToDeleteList=True
                else:
                    if ((actionControl == 0) or (actionControl == 3) or (actionControl == 6)):
                        #No action taken on False
                        addItemToDeleteList=None
                    elif ((actionControl == 1) or (actionControl == 4) or (actionControl == 7)):
                        #Action taken on False
                        if (configuredBehavior == deleteIt):
                            addItemToDeleteList=True
                        else: #(configuredBehavior == keepIt):
                            addItemToDeleteList=False
                    else: #((actionControl == 2) or (actionControl == 5) or (actionControl == 8)):
                        #Opposite action taken on False
                        if (configuredBehavior == deleteIt):
                            addItemToDeleteList=False
                        else: #(configuredBehavior == keepIt):
                            addItemToDeleteList=True

                if (addItemToDeleteList == True):
                    if (not (itemId in postproc_dict['deleteItems_Tracker'])):
                        postproc_dict['deleteItems'].append(media_data[itemId])
                        postproc_dict['deleteItems_Tracker'].append(itemId)
                elif (addItemToDeleteList == False):
                    while itemId in postproc_dict['deleteItems_Tracker']:
                        media_item_index=postproc_dict['deleteItems_Tracker'].index(itemId)
                        try:
                            postproc_dict['deleteItems'].pop(media_item_index)
                            postproc_dict['deleteItems_Tracker'].pop(media_item_index)
                        except:
                            raise IndexError('Unable To Remove ' + postproc_dict['media_type_upper'] + ' with Id: ' + itemId + ' From deleteItems List.')

    #postproc_dict['is' + behavior_str + '_extraInfo_byUserId_Media'].pop('is' + behavior_str + '_extraInfo_Tracker')
    postproc_dict['is' + behavior_str + '_extraInfo_byUserId_Media'].pop('userId_list')

    return postproc_dict


#Because we are not searching directly for unplayed black/whitelisted items; cleanup needs to happen to help the behavioral patterns make sense
def behavior_playedPatternCleanup(behavior_str,postproc_dict,the_dict):
    isbehavior_extraInfo_byUserId_Media=postproc_dict['is' + behavior_str + '_extraInfo_byUserId_Media']
    isbehavior_extraInfo_Tracker=isbehavior_extraInfo_byUserId_Media['is' + behavior_str + '_extraInfo_Tracker']
    media_data=postproc_dict['media_data']

    if (('MonitoredUsersAction' in isbehavior_extraInfo_byUserId_Media) and ('MonitoredUsersMeetPlayedFilter' in isbehavior_extraInfo_byUserId_Media) and ('ActionType' in isbehavior_extraInfo_byUserId_Media)):

        #assign after verifying isbehavior_extraInfo_byUserId_Media is populated (aka not empty)
        ActionType=isbehavior_extraInfo_byUserId_Media['ActionType']

        if ((ActionType == 'blacktagged') or (ActionType == 'whitetagged')):
            #remove whitespace(s) from the beginning and end of each tag
            tags_filter = [tagstr for tagstr in the_dict['basic_settings']['filter_tags'][postproc_dict['media_type_lower']][ActionType.replace('ged','s')] if tagstr.strip()]
            tags_media_specific = [tagstr for tagstr in the_dict['advanced_settings'][ActionType.replace('ged','s')][postproc_dict['media_type_lower']] if tagstr.strip()]
            tags_global = [tagstr for tagstr in the_dict['advanced_settings'][ActionType.replace('ged','s')]['global'] if tagstr.strip()]

            #combine tags and remove any duplicates
            media_tags=list(set(tags_filter + tags_media_specific + tags_global))

        for userInfo in postproc_dict['enabled_users']:
            for itemId in isbehavior_extraInfo_Tracker:

                if (not(itemId in isbehavior_extraInfo_byUserId_Media[userInfo['user_id']])):
                    isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]={}                                

                #before getting additional item info check if user has access to the parent library of the media_item
                if (media_data[itemId]['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][userInfo['user_id']]):

                    if (not('IsMeetingAction' in isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId])):

                        if ((ActionType == 'blacklisted') or (ActionType == 'whitelisted')):
                            isActioned=get_isItemWhitelisted_Blacklisted(ActionType.replace('ed',''),media_data[itemId],userInfo,the_dict)
                            isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingAction']=isActioned

                        elif ((ActionType == 'blacktagged') or (ActionType == 'whitetagged')):
                            if (postproc_dict['media_type_lower'] == 'movie'):
                                isActioned,matchedTags=get_isMOVIE_Tagged(the_dict,media_data[itemId],userInfo,media_tags)
                            elif (postproc_dict['media_type_lower'] == 'episode'):
                                isActioned,matchedTags=get_isEPISODE_Tagged(the_dict,media_data[itemId],userInfo,media_tags)
                            elif (postproc_dict['media_type_lower'] == 'audio'):
                                isActioned,matchedTags=get_isAUDIO_Tagged(the_dict,media_data[itemId],userInfo,media_tags)
                            elif (postproc_dict['media_type_lower'] == 'audiobook'):
                                isActioned,matchedTags=get_isAUDIOBOOK_Tagged(the_dict,media_data[itemId],userInfo,media_tags)
                            else:
                                raise RuntimeError('\nMedia Item with itemId: ' + itemId + ' does not have appropriate media_type assigned during post processing of ' + ActionType + ' items')

                            isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingAction']=isActioned

                        elif (ActionType == 'favorited'):
                            itemIsFav=False
                            itemIsAdvFav=False

                            mediaItemAdditionalInfo=get_ADDITIONAL_itemInfo(userInfo,itemId,ActionType + 'playedPatternCleanup',the_dict)
                            mediaItemAdditionalInfo['mumc']=media_data[itemId]['mumc']

                            if (postproc_dict['media_type_lower'] == 'movie'):
                                itemIsFav=get_isMOVIE_Fav(the_dict,mediaItemAdditionalInfo,userInfo)
                            elif (postproc_dict['media_type_lower'] == 'episode'):
                                itemIsFav=get_isEPISODE_Fav(the_dict,mediaItemAdditionalInfo,userInfo)
                            elif (postproc_dict['media_type_lower'] == 'audio'):
                                itemIsFav=get_isAUDIO_Fav(the_dict,mediaItemAdditionalInfo,userInfo,'Audio')
                            elif (postproc_dict['media_type_lower'] == 'audiobook'):
                                itemIsFav=get_isAUDIOBOOK_Fav(the_dict,mediaItemAdditionalInfo,userInfo,'AudioBook')
                            else:
                                raise RuntimeError('\nMedia Item with itemId: ' + itemId + ' does not have appropriate media_type assigned during post processing of ' + ActionType + ' items')

                            for advFavItem in postproc_dict['advFav_media']:
                                if ((postproc_dict['advFav_media'][advFavItem]) and (isbehavior_extraInfo_byUserId_Media['ActionControl'])):
                                    if (postproc_dict['media_type_lower'] == 'movie'):
                                        itemIsAdvFav=get_isMOVIE_AdvancedFav(the_dict,mediaItemAdditionalInfo,userInfo,postproc_dict)
                                    elif (postproc_dict['media_type_lower'] == 'episode'):
                                        itemIsAdvFav=get_isEPISODE_AdvancedFav(the_dict,mediaItemAdditionalInfo,userInfo,postproc_dict)
                                    elif (postproc_dict['media_type_lower'] == 'audio'):
                                        itemIsAdvFav=get_isAUDIO_AdvancedFav(the_dict,mediaItemAdditionalInfo,userInfo,postproc_dict)
                                    elif (postproc_dict['media_type_lower'] == 'audiobook'):
                                        itemIsAdvFav=get_isAUDIOBOOK_AdvancedFav(the_dict,mediaItemAdditionalInfo,userInfo,postproc_dict)
                                    else:
                                        raise RuntimeError('\nMedia Item with itemId: ' + itemId + ' does not have appropriate media_type assigned during post processing of advanced_' + ActionType + ' items')
                                    break

                            isActioned=(itemIsFav or itemIsAdvFav)
                            isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingAction']=isActioned

                        else:
                            raise RuntimeError('\nMedia Item with itemId: ' + itemId + ' does not have appropriate behavior assigned during post processing of ' + ActionType + ' items')

                    if (not(('IsMeetingPlayedFilter' in isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]) or ('IsMeetingCreatedPlayedFilter' in isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]))):
                        played_created_days_counts_dict={}
                        mediaItemAdditionalInfo=get_ADDITIONAL_itemInfo(userInfo,itemId,ActionType + 'playedPatternCleanup',the_dict)
                        played_created_days_counts_dict=get_playedDays_createdPlayedDays_playedCounts_createdPlayedCounts(the_dict,mediaItemAdditionalInfo,postproc_dict)

                        if ((ActionType == 'blacktagged') or (ActionType == 'whitetagged')):
                            postproc_dict['matched_filter_' + ActionType.replace('ged','s')]={}
                            #postproc_dict['matched_filter_blacktags']={}
                            for thisTag in matchedTags:
                                if (thisTag in postproc_dict[ActionType.replace('ged','') + '_filter_statements']):
                                    postproc_dict['matched_filter_' + ActionType.replace('ged','s')][thisTag]={}
                                    #postproc_dict['matched_filter_' + ActionType.replace('ged','s')][thisTag]=False
                                    #postproc_dict['matched_filter_' + ActionType.replace('ged','s')][thisTag]={}
                                    #postproc_dict['matched_filter_' + ActionType.replace('ged','s')][thisTag]['matching_played_tag']=False
                                    #postproc_dict['matched_filter_' + ActionType.replace('ged','s')][thisTag]['matching_created_tag']=False
                                #if (not ((filterStatementTag:=get_isPlayedCreated_FilterStatementTag(thisTag)) == False)):
                                    #if ('media_played_days' in filterStatementTag):
                                        #tagType_Played_Created='played'
                                    #elif ('media_created_days' in filterStatementTag):
                                        #tagType_Played_Created='created'
                                    #filterStatementTag['cut_off_date_' + tagType_Played_Created + '_media']=postproc_dict['date_time_now_tz_utc'] - timedelta(days=the_dict['basic_settings'][ActionType.replace('ged','') + '_filter_statements'][postproc_dict['media_type_lower']][thisTag]['media_' + tagType_Played_Created + '_days'])
                                    #postproc_dict[thisTag]=filterStatementTag
                                #postproc_dict['matched_filter_' + ActionType.replace('ged','s')][thisTag]=False
                            #postproc_dict.update(played_created_days_counts_dict)
                            postproc_dict=getTag_playedDays_createdPlayedDays_playedCounts_createdPlayedCounts(ActionType.replace('ged',''),the_dict,mediaItemAdditionalInfo,postproc_dict)
                            #update played_created_days_counts_dict with updated values from filter tags
                            #played_created_days_counts_dict['item_matches_played_days_filter']=postproc_dict['item_matches_played_days_filter']
                            #played_created_days_counts_dict['item_matches_played_count_filter']=postproc_dict['item_matches_played_count_filter']
                            #played_created_days_counts_dict['item_matches_created_days_filter']=postproc_dict['item_matches_created_days_filter']
                            #played_created_days_counts_dict['item_matches_created_played_count_filter']=postproc_dict['item_matches_created_played_count_filter']
                            isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMatchingFilter' + ActionType.replace('ged','s')]=postproc_dict['matched_filter_' + ActionType.replace('ged','s')]

                    if (not('IsMeetingPlayedFilter' in isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId])):
                        isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingPlayedFilter']=(played_created_days_counts_dict['item_matches_played_days_filter'] and played_created_days_counts_dict['item_matches_played_count_filter']) #meeting complete played_filter_*?

                    if (not('IsMeetingCreatedPlayedFilter' in isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId])):
                        isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingCreatedPlayedFilter']=(played_created_days_counts_dict['item_matches_created_days_filter'] and played_created_days_counts_dict['item_matches_created_played_count_filter']) #meeting complete created_filter_*?

                    #isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMatchingFilter'+ActionType.replace('ged','s').title()]=postproc_dict['matched_filter_' + ActionType.replace('ged','s')]
                else:
                    isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingAction']=None
                    isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingPlayedFilter']=None #meeting complete played_filter_*?
                    isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingCreatedPlayedFilter']=None #meeting complete created_filter_*?
                    #isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMatchingFilter'+ActionType.replace('ged','s').title()]=None

                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nIsMeetingAction: " + str(isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingAction']),3,the_dict)
                    appendTo_DEBUG_log("\nIsMeetingPlayedFilter: " + str(isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingPlayedFilter']),3,the_dict)
                    appendTo_DEBUG_log("\nIsMeetingCreatedPlayedFilter: " + str(isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]['IsMeetingCreatedPlayedFilter']) + "\n",3,the_dict)

    postproc_dict['is' + behavior_str + '_extraInfo_byUserId_Media']=isbehavior_extraInfo_byUserId_Media

    return postproc_dict


def addItem_removeItem_fromDeleteList_usingBehavioralTagPatterns(tagType,high_priority,postproc_dict,the_dict):

    orig_behavioral_info=postproc_dict['is' + tagType + '_extraInfo_byUserId_Media'].copy()

    for thisFilterTag in reversed(the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]):
        if ((thisFilterTag in postproc_dict[tagType.replace('ged','') + '_filter_statements']) and (postproc_dict['behavioral_tag_high_priority'][thisFilterTag] == high_priority)):
            if (thisFilterTag in postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags']):
                postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['DynamicBehavior']=postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['DynamicBehavior']
                postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['ActionControl']=postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionControl']
                postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['ActionType']=postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionType']
                postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['MonitoredUsersAction']=postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersAction']
                postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['MonitoredUsersMeetPlayedFilter']=postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersMeetPlayedFilter']
                postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['ConfiguredBehavior']=postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ConfiguredBehavior']
            else:
                postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']=orig_behavioral_info
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns(tagType,postproc_dict,thisFilterTag)

    return postproc_dict


#add played and created data for item during post-processing
def add_missingItems_byUserId_playedStates(behavior_str,postproc_dict,the_dict):
    isbehavior_extraInfo_byUserId_Media=postproc_dict['is' + behavior_str + '_extraInfo_byUserId_Media']
    isbehavior_extraInfo_Tracker=isbehavior_extraInfo_byUserId_Media['is' + behavior_str + '_extraInfo_Tracker']

    for userInfo in postproc_dict['enabled_users']:
        for itemId in isbehavior_extraInfo_Tracker:
            if (not(itemId in isbehavior_extraInfo_byUserId_Media[userInfo['user_id']])):
                isbehavior_extraInfo_byUserId_Media[userInfo['user_id']][itemId]={}
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nAdding missing played state for item " + str(itemId) + " to isbehavior_extraInfo_byUserId_Media for user " + str(userInfo['user_id']),3,the_dict)

    postproc_dict['is' + behavior_str + '_extraInfo_byUserId_Media']=isbehavior_extraInfo_byUserId_Media

    return postproc_dict


#@profile
def postProcessing(the_dict,media_dict):

    postproc_dict={}

    postproc_dict['media_type_lower']=media_dict['media_type'].casefold()
    postproc_dict['media_type_upper']=media_dict['media_type'].upper()
    postproc_dict['media_type_title']=media_dict['media_type'].title()

    postproc_dict['media_dict_str']=the_dict[postproc_dict['media_type_lower'] + '_dict']['media_type'] + '_dict'

    postproc_dict['admin_settings']={}
    postproc_dict['admin_settings']['behavior']={}
    postproc_dict['admin_settings']['behavior']['matching']=the_dict['admin_settings']['behavior']['matching']
    postproc_dict['admin_settings']['users']=the_dict['admin_settings']['users']
    #postproc_dict['admin_settings']=the_dict['admin_settings']

    postproc_dict['advanced_settings']={}
    postproc_dict['advanced_settings']['episode_control']=the_dict['advanced_settings']['episode_control']
    #postproc_dict['advanced_settings']=the_dict['advanced_settings']

    postproc_dict['minimum_number_episodes']=the_dict['advanced_settings']['episode_control']['minimum_episodes']
    postproc_dict['minimum_number_played_episodes']=the_dict['advanced_settings']['episode_control']['minimum_played_episodes']
    postproc_dict['minimum_number_episodes_behavior']=the_dict['advanced_settings']['episode_control']['minimum_episodes_behavior']

    postproc_dict['media_played_days']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['played']['condition_days']
    postproc_dict['media_created_days']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['created']['condition_days']
    postproc_dict['media_played_count_comparison']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['played']['count_equality']
    postproc_dict['media_created_played_count_comparison']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['created']['count_equality']
    postproc_dict['media_played_count']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['played']['count']
    postproc_dict['media_created_played_count']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['created']['count']
    postproc_dict['media_created_behavioral_control']=the_dict['basic_settings']['filter_statements'][postproc_dict['media_type_lower']]['created']['behavioral_control']

    postproc_dict['whitetag_filter_statements']=the_dict['basic_settings']['whitetag_filter_statements'][postproc_dict['media_type_lower']]
    postproc_dict['blacktag_filter_statements']=the_dict['basic_settings']['blacktag_filter_statements'][postproc_dict['media_type_lower']]

    postproc_dict['filter_tag_played_days']=the_dict['filter_tag_played_days'][postproc_dict['media_type_lower']]
    postproc_dict['filter_tag_created_days']=the_dict['filter_tag_created_days'][postproc_dict['media_type_lower']]

    postproc_dict['favorited_behavior_media']={}
    postproc_dict['favorited_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['action']
    postproc_dict['favorited_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['user_conditional']
    postproc_dict['favorited_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['played_conditional']
    postproc_dict['favorited_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['action_control']
    postproc_dict['favorited_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['dynamic_behavior']
    postproc_dict['whitetagged_behavior_media']={}
    postproc_dict['whitetagged_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitetagged']['action']
    postproc_dict['whitetagged_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitetagged']['user_conditional']
    postproc_dict['whitetagged_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitetagged']['played_conditional']
    postproc_dict['whitetagged_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitetagged']['action_control']
    postproc_dict['whitetagged_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitetagged']['dynamic_behavior']
    postproc_dict['blacktagged_behavior_media']={}
    postproc_dict['blacktagged_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacktagged']['action']
    postproc_dict['blacktagged_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacktagged']['user_conditional']
    postproc_dict['blacktagged_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacktagged']['played_conditional']
    postproc_dict['blacktagged_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacktagged']['action_control']
    postproc_dict['blacktagged_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacktagged']['dynamic_behavior']
    postproc_dict['whitelisted_behavior_media']={}
    postproc_dict['whitelisted_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitelisted']['action']
    postproc_dict['whitelisted_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitelisted']['user_conditional']
    postproc_dict['whitelisted_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitelisted']['played_conditional']
    postproc_dict['whitelisted_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitelisted']['action_control']
    postproc_dict['whitelisted_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['whitelisted']['dynamic_behavior']
    postproc_dict['blacklisted_behavior_media']={}
    postproc_dict['blacklisted_behavior_media']['action']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacklisted']['action']
    postproc_dict['blacklisted_behavior_media']['user_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacklisted']['user_conditional']
    postproc_dict['blacklisted_behavior_media']['played_conditional']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacklisted']['played_conditional']
    postproc_dict['blacklisted_behavior_media']['action_control']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacklisted']['action_control']
    postproc_dict['blacklisted_behavior_media']['dynamic_behavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['blacklisted']['dynamic_behavior']
    postproc_dict['print_media_post_processing']=the_dict['advanced_settings']['console_controls'][postproc_dict['media_type_lower']]['post_processing']['show']
    postproc_dict['media_post_processing_format']=the_dict['advanced_settings']['console_controls'][postproc_dict['media_type_lower']]['post_processing']['formatting']

    postproc_dict['advFav_media']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]['favorited']['extra']

    postproc_dict['cut_off_date_played_media']=the_dict['cut_off_date_played_media'][postproc_dict['media_type_lower']]
    postproc_dict['cut_off_date_created_media']=the_dict['cut_off_date_created_media'][postproc_dict['media_type_lower']]

    #list of enabled users
    postproc_dict['enabled_users']=the_dict['enabled_users']
    postproc_dict['enabled_user_ids']=the_dict['enabled_user_ids']

    #media item info
    postproc_dict['media_data']=media_dict['media_data']

    #created media items
    postproc_dict['deleteItemsIdTracker_createdMedia']=media_dict['deleteItemsIdTracker_createdMedia']

    #behavioral extra item info
    postproc_dict['isblacklisted_extraInfo_byUserId_Media']={}
    postproc_dict['iswhitelisted_extraInfo_byUserId_Media']={}
    postproc_dict['isblacktagged_extraInfo_byUserId_Media']={}
    postproc_dict['iswhitetagged_extraInfo_byUserId_Media']={}
    postproc_dict['isfavorited_extraInfo_byUserId_Media']={}

    postproc_dict['isblacklisted_extraInfo_byUserId_Media']['isblacklisted_extraInfo_Tracker']=list(set(media_dict['isblacklisted_extraInfo_Tracker']))
    postproc_dict['iswhitelisted_extraInfo_byUserId_Media']['iswhitelisted_extraInfo_Tracker']=list(set(media_dict['iswhitelisted_extraInfo_Tracker']))
    postproc_dict['isblacktagged_extraInfo_byUserId_Media']['isblacktagged_extraInfo_Tracker']=list(set(media_dict['isblacktagged_extraInfo_Tracker']))
    postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['iswhitetagged_extraInfo_Tracker']=list(set(media_dict['iswhitetagged_extraInfo_Tracker']))
    postproc_dict['isfavorited_extraInfo_byUserId_Media']['isfavorited_extraInfo_Tracker']=list(set(media_dict['isfavorited_extraInfo_Tracker']))

    postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags']={}
    postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags']={}
    postproc_dict['behavioral_tag_high_priority']={}
    if (not (the_dict['advanced_settings']['behavioral_tags'][postproc_dict['media_type_lower']] == None)):
        #for thisTag in the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]:
        for thisTag in the_dict['advanced_settings']['behavioral_tags'][postproc_dict['media_type_lower']]:
            if (get_isPlayedCreated_FilterStatementTag(thisTag)):
                #if (thisTag in postproc_dict['whitetag_filter_statements']):
                    #postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]={}
                    #postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['DynamicBehavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['dynamic_behavior']
                    #postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['ActionControl']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['action_control']
                    #postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['ActionType']='whitetagged'
                    #postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['MonitoredUsersAction']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['user_conditional']
                    #postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['MonitoredUsersMeetPlayedFilter']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['played_conditional']
                    #postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['ConfiguredBehavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['action']
                #elif (thisTag in postproc_dict['blacktag_filter_statements']):
                    #postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]={}
                    #postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['DynamicBehavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['dynamic_behavior']
                    #postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['ActionControl']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['action_control']
                    #postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['ActionType']='blacktagged'
                    #postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['MonitoredUsersAction']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['user_conditional']
                    #postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['MonitoredUsersMeetPlayedFilter']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['played_conditional']
                    #postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['ConfiguredBehavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][thisTag]['action']

                if (thisTag in postproc_dict['whitetag_filter_statements']):
                    tagType='whitetagged'
                elif (thisTag in postproc_dict['blacktag_filter_statements']):
                    tagType='blacktagged'
                else:
                    tagType=None

                if (not (tagType == None)):
                    if (thisTag in the_dict['advanced_settings']['behavioral_tags'][postproc_dict['media_type_lower']]):
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]={}
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['DynamicBehavior']=the_dict['advanced_settings']['behavioral_tags'][postproc_dict['media_type_lower']][thisTag]['dynamic_behavior']
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['ActionControl']=the_dict['advanced_settings']['behavioral_tags'][postproc_dict['media_type_lower']][thisTag]['action_control']
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['ActionType']='' + tagType + ''
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['MonitoredUsersAction']=the_dict['advanced_settings']['behavioral_tags'][postproc_dict['media_type_lower']][thisTag]['user_conditional']
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['MonitoredUsersMeetPlayedFilter']=the_dict['advanced_settings']['behavioral_tags'][postproc_dict['media_type_lower']][thisTag]['played_conditional']
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][thisTag]['ConfiguredBehavior']=the_dict['advanced_settings']['behavioral_tags'][postproc_dict['media_type_lower']][thisTag]['action']
                        postproc_dict['behavioral_tag_high_priority'][thisTag]=the_dict['advanced_settings']['behavioral_tags'][postproc_dict['media_type_lower']][thisTag]['high_priority']
                    else:
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][tagType]={}
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][tagType]['DynamicBehavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][tagType]['dynamic_behavior']
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][tagType]['ActionControl']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][tagType]['action_control']
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][tagType]['ActionType']='blacktagged'
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][tagType]['MonitoredUsersAction']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][tagType]['user_conditional']
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][tagType]['MonitoredUsersMeetPlayedFilter']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][tagType]['played_conditional']
                        postproc_dict['is' + tagType + '_extraInfo_byUserId_Media']['behavioral_tags'][tagType]['ConfiguredBehavior']=the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']][tagType]['action']
                        postproc_dict['behavioral_tag_high_priority'][thisTag]=False

    #episode counts
    postproc_dict['mediaCounts_byUserId']={}

    #list of items to be deleted
    postproc_dict['deleteItems']=[]
    postproc_dict['deleteItems_Tracker']=[]

    postproc_dict['enabled_users']=the_dict['enabled_users']

    postproc_dict['filter_whitetag_enabled']=False
    for filter_tag in the_dict['basic_settings']['whitetag_filter_statements'][postproc_dict['media_type_lower']]:
        if ('media_played_days' in the_dict['basic_settings']['whitetag_filter_statements'][postproc_dict['media_type_lower']][filter_tag]):
            if (the_dict['basic_settings']['whitetag_filter_statements'][postproc_dict['media_type_lower']][filter_tag]['media_played_days'] >= 0):
                postproc_dict['filter_whitetag_enabled']=True
                break
        if ('media_created_days' in the_dict['basic_settings']['whitetag_filter_statements'][postproc_dict['media_type_lower']][filter_tag]):
            if (the_dict['basic_settings']['whitetag_filter_statements'][postproc_dict['media_type_lower']][filter_tag]['media_created_days'] >= 0):
                postproc_dict['filter_whitetag_enabled']=True
                break

    postproc_dict['filter_blacktag_enabled']=False
    for filter_tag in the_dict['basic_settings']['blacktag_filter_statements'][postproc_dict['media_type_lower']]:
        if ('media_played_days' in the_dict['basic_settings']['blacktag_filter_statements'][postproc_dict['media_type_lower']][filter_tag]):
            if (the_dict['basic_settings']['blacktag_filter_statements'][postproc_dict['media_type_lower']][filter_tag]['media_played_days'] >= 0):
                postproc_dict['filter_blacktag_enabled']=True
                break
        if ('media_created_days' in the_dict['basic_settings']['blacktag_filter_statements'][postproc_dict['media_type_lower']][filter_tag]):
            if (the_dict['basic_settings']['blacktag_filter_statements'][postproc_dict['media_type_lower']][filter_tag]['media_created_days'] >= 0):
                postproc_dict['filter_blacktag_enabled']=True
                break

    #check media is enabled before post-processing
    #if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
    if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0) or (postproc_dict['filter_tag_played_days']) or (postproc_dict['filter_tag_created_days'])):

        print_post_processing_started(the_dict,postproc_dict)

        for user_key in media_dict:
            if (not ((user_key == 'media_type') or (user_key == 'media_data') or (user_key == 'deleteItemsIdTracker_createdMedia') or
                     (user_key == 'isfavorited_extraInfo_Tracker') or (user_key == 'iswhitetagged_extraInfo_Tracker') or (user_key == 'isblacktagged_extraInfo_Tracker') or
                     (user_key == 'iswhitelisted_extraInfo_Tracker') or (user_key == 'isblacklisted_extraInfo_Tracker'))):

                postproc_dict['isblacklisted_extraInfo_byUserId_Media'].update(media_dict[user_key]['isblacklisted_extraInfo_byUserId_Media'])
                postproc_dict['iswhitelisted_extraInfo_byUserId_Media'].update(media_dict[user_key]['iswhitelisted_extraInfo_byUserId_Media'])
                postproc_dict['isblacktagged_extraInfo_byUserId_Media'].update(media_dict[user_key]['isblacktagged_extraInfo_byUserId_Media'])
                postproc_dict['iswhitetagged_extraInfo_byUserId_Media'].update(media_dict[user_key]['iswhitetagged_extraInfo_byUserId_Media'])
                postproc_dict['isfavorited_extraInfo_byUserId_Media'].update(media_dict[user_key]['isfavorited_extraInfo_byUserId_Media'])

                postproc_dict['mediaCounts_byUserId'].update(media_dict[user_key]['mediaCounts_byUserId'])

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nList Of Possible Created " + postproc_dict['media_type_lower'] + " Items To Be Deleted: " + str(len(postproc_dict['deleteItemsIdTracker_createdMedia'])),3,the_dict)
            appendTo_DEBUG_log("\n" + convert2json(postproc_dict['deleteItemsIdTracker_createdMedia']),4,the_dict)

        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['media_created_behavioral_control'])):
            appendTo_DEBUG_log("\nCombined List Of Possible Behavioral media with List Of Possible Created media for post processing",3,the_dict)
        else:
            appendTo_DEBUG_log("\nOnly using List Of Possible Behavioral media for post processing",3,the_dict)

########BLACKLIST###################################################################################################################################
        #Add blacklisted items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['blacklisted_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'blacklisted')
            postproc_dict=behavior_playedPatternCleanup('blacklisted',postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('blacklisted',postproc_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\nisblacklisted_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                postproc_dict['isblacklisted_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['isblacklisted_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['isblacklisted_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

########WHITELIST###################################################################################################################################
        #Add whitelisted items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['whitelisted_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'WHITELISTED')
            postproc_dict=behavior_playedPatternCleanup('whitelisted',postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('whitelisted',postproc_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\niswhitelisted_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                postproc_dict['iswhitelisted_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['iswhitelisted_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['iswhitelisted_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

########BLACKTAG####################################################################################################################################
        #Add blacktagged items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0) or postproc_dict['filter_blacktag_enabled']) and (postproc_dict['blacktagged_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'BLACKTAGGED')
            postproc_dict=behavior_playedPatternCleanup('blacktagged',postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('blacktagged',postproc_dict)

########FILTER BLACKTAG#############################################################################################################################
            '''
            orig_behavioral_info=postproc_dict['isblacktagged_extraInfo_byUserId_Media'].copy()
            for thisFilterTag in reversed(the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]):
                if ((thisFilterTag in postproc_dict['blacktag_filter_statements']) and (not postproc_dict['behavioral_tag_high_priority'][thisFilterTag])):
                    if (thisFilterTag in postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags']):
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['DynamicBehavior']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['DynamicBehavior']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['ActionControl']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionControl']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['ActionType']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionType']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['MonitoredUsersAction']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersAction']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['MonitoredUsersMeetPlayedFilter']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersMeetPlayedFilter']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['ConfiguredBehavior']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ConfiguredBehavior']
                    else:
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']=orig_behavioral_info
                    postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('blacktagged',postproc_dict,thisFilterTag)
            '''
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralTagPatterns('blacktagged',False,postproc_dict,the_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\nisblacktagged_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                postproc_dict['isblacktagged_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['isblacktagged_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['isblacktagged_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

########WHITETAG####################################################################################################################################
        #Add whitetagged items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0) or postproc_dict['filter_whitetag_enabled']) and (postproc_dict['whitetagged_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'WHITETAGGED')
            postproc_dict=behavior_playedPatternCleanup('whitetagged',postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('whitetagged',postproc_dict)

########FILTER WHITETAG#############################################################################################################################
            '''
            orig_behavioral_info=postproc_dict['iswhitetagged_extraInfo_byUserId_Media'].copy()
            for thisFilterTag in reversed(the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]):
                if ((thisFilterTag in postproc_dict['whitetag_filter_statements']) and (not postproc_dict['behavioral_tag_high_priority'][thisFilterTag])):
                    if (thisFilterTag in postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags']):
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['DynamicBehavior']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['DynamicBehavior']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['ActionControl']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionControl']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['ActionType']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionType']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['MonitoredUsersAction']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersAction']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['MonitoredUsersMeetPlayedFilter']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersMeetPlayedFilter']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['ConfiguredBehavior']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ConfiguredBehavior']
                    else:
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']=orig_behavioral_info
                    postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('whitetagged',postproc_dict,thisFilterTag)
            '''
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralTagPatterns('whitetagged',False,postproc_dict,the_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\niswhitetagged_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                postproc_dict['iswhitetagged_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['iswhitetagged_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['iswhitetagged_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

########FAVORITE####################################################################################################################################
        #Add favorited items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)) and (postproc_dict['favorited_behavior_media']['action_control'] >= 0)):
            print_post_processing_verbal_progress(the_dict,postproc_dict,'FAVORITED')
            postproc_dict=behavior_playedPatternCleanup('favorited',postproc_dict,the_dict)
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('favorited',postproc_dict)

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n-----------------------------------------------------------",3,the_dict)
            appendTo_DEBUG_log("\n",3,the_dict)
            if ((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0)):
                appendTo_DEBUG_log("\nisfavorited_Played_" + postproc_dict['media_type_lower'] + ":",3,the_dict)
                postproc_dict['isfavorited_extraInfo_byUserId_Media']=convert_timeToString(postproc_dict['isfavorited_extraInfo_byUserId_Media'])
                appendTo_DEBUG_log("\n" + convert2json(postproc_dict['isfavorited_extraInfo_byUserId_Media']),3,the_dict)
                appendTo_DEBUG_log("\n",3,the_dict)

########FILTER BLACKTAG#############################################################################################################################
        #Add blacktagged items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0) or postproc_dict['filter_blacktag_enabled']) and (postproc_dict['blacktagged_behavior_media']['action_control'] >= 0)):
            '''
            orig_behavioral_info=postproc_dict['isblacktagged_extraInfo_byUserId_Media'].copy()
            for thisFilterTag in reversed(the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]):
                if ((thisFilterTag in postproc_dict['blacktag_filter_statements']) and postproc_dict['behavioral_tag_high_priority'][thisFilterTag]):
                    if (thisFilterTag in postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags']):
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['DynamicBehavior']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['DynamicBehavior']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['ActionControl']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionControl']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['ActionType']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionType']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['MonitoredUsersAction']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersAction']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['MonitoredUsersMeetPlayedFilter']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersMeetPlayedFilter']
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']['ConfiguredBehavior']=postproc_dict['isblacktagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ConfiguredBehavior']
                    else:
                        postproc_dict['isblacktagged_extraInfo_byUserId_Media']=orig_behavioral_info
                    postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('blacktagged',postproc_dict,thisFilterTag)
            '''
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralTagPatterns('blacktagged',True,postproc_dict,the_dict)

########FILTER WHITETAG#############################################################################################################################
        #Add whitetagged items to delete list that meet the defined played state
        if (((postproc_dict['media_played_days'] >= 0) or (postproc_dict['media_created_days'] >= 0) or postproc_dict['filter_whitetag_enabled']) and (postproc_dict['whitetagged_behavior_media']['action_control'] >= 0)):
            '''
            orig_behavioral_info=postproc_dict['iswhitetagged_extraInfo_byUserId_Media'].copy()
            for thisFilterTag in reversed(the_dict['advanced_settings']['behavioral_statements'][postproc_dict['media_type_lower']]):
                if ((thisFilterTag in postproc_dict['whitetag_filter_statements']) and postproc_dict['behavioral_tag_high_priority'][thisFilterTag]):
                    if (thisFilterTag in postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags']):
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['DynamicBehavior']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['DynamicBehavior']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['ActionControl']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionControl']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['ActionType']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ActionType']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['MonitoredUsersAction']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersAction']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['MonitoredUsersMeetPlayedFilter']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['MonitoredUsersMeetPlayedFilter']
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['ConfiguredBehavior']=postproc_dict['iswhitetagged_extraInfo_byUserId_Media']['behavioral_tags'][thisFilterTag]['ConfiguredBehavior']
                    else:
                        postproc_dict['iswhitetagged_extraInfo_byUserId_Media']=orig_behavioral_info
                    postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralPatterns('whitetagged',postproc_dict,thisFilterTag)
            '''
            postproc_dict=addItem_removeItem_fromDeleteList_usingBehavioralTagPatterns('whitetagged',True,postproc_dict,the_dict)

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

        #postproc_dict['deleteItems_Media']+=postproc_dict['deleteItems_Media']
        if (not (postproc_dict['media_created_behavioral_control'])):
            for itemId in postproc_dict['deleteItemsIdTracker_createdMedia']:
                if (not (itemId in postproc_dict['deleteItems_Tracker'])):
                    postproc_dict['deleteItems_Tracker'].append(itemId)
                    postproc_dict['deleteItems'].append(postproc_dict['media_data'][itemId])

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n" + convert2json(postproc_dict['deleteItems']),4,the_dict)

        print_post_processing_completed(the_dict,postproc_dict)

    return postproc_dict['deleteItems']


#@profile
def start_postProcessing(the_dict,media_dict,deleteItems_dict):
    if (not (the_dict['all_media_disabled'])):
        #perform post processing for each media type
        deleteItems_media=postProcessing(the_dict,media_dict)

        #verify the specific media_type is not already in the dictionary as a key
        #if it is not; go ahead and add it and set it == deleteItems_media
        #if it is; join to the existing list so the previous information is not lost
        if (not (media_dict['media_type'] in deleteItems_dict)):
            deleteItems_dict[media_dict['media_type']]=deleteItems_media
        else:
            deleteItems_dict[media_dict['media_type']]+=deleteItems_media

    return deleteItems_dict


#@profile
def init_postProcessing(the_dict):

    movie_dict=the_dict['movie_dict']
    episode_dict=the_dict['episode_dict']
    audio_dict=the_dict['audio_dict']
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        audiobook_dict=the_dict['audiobook_dict']
    else:
        audiobook_dict={}
        audiobook_dict['media_type']='audiobook'
    #recording_dict=the_dict['recording_dict']

    #when debug is disabled allow mulitprocessing
    if (not (the_dict['DEBUG'])):

        deleteItems_dict=multiprocessing.Manager().dict()

        #prepare for post processing; return dictionary of lists of media items to be deleted
        #setup for multiprocessing of the post processing of each media type
        mpp_movie_post_process=multiprocessing.Process(target=start_postProcessing,args=(the_dict,movie_dict,deleteItems_dict))
        mpp_episodePostProcess=multiprocessing.Process(target=start_postProcessing,args=(the_dict,episode_dict,deleteItems_dict))
        mpp_audioPostProcess=multiprocessing.Process(target=start_postProcessing,args=(the_dict,audio_dict,deleteItems_dict))
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            mpp_audiobookPostProcess=multiprocessing.Process(target=start_postProcessing,args=(the_dict,audiobook_dict,deleteItems_dict))
        #mpp_recordingPostProcess=multiprocessing.Process(target=start_postProcessing,args=(the_dict,recording_dict,deleteItems_dict))

        #start all multi processes
        #order intentially: Audio, Episodes, Movies, Audiobooks
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            #mpp_audioPostProcess.start(),mpp_episodePostProcess.start(),mpp_movie_post_process.start(),mpp_audiobookPostProcess.start(),mpp_recordingPostProcess.start()
            #mpp_audioPostProcess.join(), mpp_episodePostProcess.join(), mpp_movie_post_process.join(), mpp_audiobookPostProcess.join(),mpp_recordingPostProcess.join()
            #mpp_audioPostProcess.close(),mpp_episodePostProcess.close(),mpp_movie_post_process.close(),mpp_audiobookPostProcess.close(),mpp_recordingPostProcess.close()
            mpp_audioPostProcess.start(),mpp_episodePostProcess.start(),mpp_movie_post_process.start(),mpp_audiobookPostProcess.start()
            mpp_audioPostProcess.join(), mpp_episodePostProcess.join(), mpp_movie_post_process.join(), mpp_audiobookPostProcess.join()
            mpp_audioPostProcess.close(),mpp_episodePostProcess.close(),mpp_movie_post_process.close(),mpp_audiobookPostProcess.close()
        else:
            #mpp_audioPostProcess.start(),mpp_episodePostProcess.start(),mpp_movie_post_process.start(),mpp_recordingPostProcess.start()
            #mpp_audioPostProcess.join(), mpp_episodePostProcess.join(), mpp_movie_post_process.join(),mpp_recordingPostProcess.join()
            #mpp_audioPostProcess.close(),mpp_episodePostProcess.close(),mpp_movie_post_process.close(),mpp_recordingPostProcess.close()
            mpp_audioPostProcess.start(),mpp_episodePostProcess.start(),mpp_movie_post_process.start()
            mpp_audioPostProcess.join(), mpp_episodePostProcess.join(), mpp_movie_post_process.join()
            mpp_audioPostProcess.close(),mpp_episodePostProcess.close(),mpp_movie_post_process.close()
            deleteItems_dict['audiobook']=[]

    else: #when debug enabled do not allow multiprocessing; this will allow stepping thru debug
        deleteItems_dict={}

        deleteItems_dict=start_postProcessing(the_dict,movie_dict,deleteItems_dict)
        deleteItems_dict=start_postProcessing(the_dict,episode_dict,deleteItems_dict)
        deleteItems_dict=start_postProcessing(the_dict,audio_dict,deleteItems_dict)
        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            deleteItems_dict=start_postProcessing(the_dict,audiobook_dict,deleteItems_dict)
        else:
            deleteItems_dict['audiobook']=[]
        #deleteItems_dict=start_postProcessing(the_dict,recording_dict,deleteItems_dict)

    return deleteItems_dict