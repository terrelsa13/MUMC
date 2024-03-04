from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_compare_items import get_isItemMatching_doesItemStartWith
from mumc_modules.mumc_played_created import get_playedCreatedDays_playedCreatedCounts
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo


def get_opposing_listing_type(the_dict):
    if (the_dict['admin_settings']['behavior']['list'] == 'blacklist'):
        opposing_listing_type='whitelist'
    else: #(the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
        opposing_listing_type='blacklist'
    return opposing_listing_type


def get_matching_listing_type(the_dict):
    if (the_dict['admin_settings']['behavior']['list'] == 'blacklist'):
        matching_listing_type='blacklist'
    else: #(the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
        matching_listing_type='whitelist'
    return matching_listing_type


#Determine if media item is whitelisted/blacklisted for the current user or for another user
def get_isItemWhitelisted_Blacklisted(checklist,item,user_info,the_dict):

    library_matching_behavior=the_dict['admin_settings']['behavior']['matching']

    user_wlbllib_key_json=[]
    user_wlbllib_path_json=[]
    user_wlbllib_netpath_json=[]
    for looplist in user_info[checklist]:
        if (library_matching_behavior.casefold() == 'byid'):
            user_wlbllib_key_json.append(looplist['lib_id'])
        elif (library_matching_behavior.casefold() == 'bypath'):
            user_wlbllib_path_json.append(looplist['path'])
        elif (library_matching_behavior.casefold() == 'bynetworkpath'):
            user_wlbllib_netpath_json.append(looplist['network_path'])

    item_isWhitelisted_isBlacklisted=False
    itemWhitelistedBlacklistedValue=''

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    if (library_matching_behavior.casefold() == 'byid'):
        item_isWhitelisted_isBlacklisted, itemWhitelistedBlacklistedValue=get_isItemMatching_doesItemStartWith(item['mumc']['lib_id'],user_wlbllib_key_json,the_dict)
    elif (library_matching_behavior.casefold() == 'bypath'):
        item_isWhitelisted_isBlacklisted, itemWhitelistedBlacklistedValue=get_isItemMatching_doesItemStartWith(item['mumc']['path'],user_wlbllib_path_json,the_dict)
    elif (library_matching_behavior.casefold() == 'bynetworkpath'):
        item_isWhitelisted_isBlacklisted, itemWhitelistedBlacklistedValue=get_isItemMatching_doesItemStartWith(item['mumc']['network_path'],user_wlbllib_netpath_json,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\nItem is whitelisted/blacklisted for this user: ' + str(item_isWhitelisted_isBlacklisted),2,the_dict)
        appendTo_DEBUG_log('\nMatching whitelisted/blacklisted value for this user is: ' + str(itemWhitelistedBlacklistedValue),2,the_dict)
        appendTo_DEBUG_log('\nitemLibraryID is: ' + str(item['mumc']['lib_id']),2,the_dict)
        appendTo_DEBUG_log('\nitemLibraryPath is: ' + str(item['mumc']['path']),2,the_dict)
        appendTo_DEBUG_log('\nitemLibraryNetPath is: ' + str(item['mumc']['network_path']),2,the_dict)
        appendTo_DEBUG_log('\nWhitelisted/Blacklisted Keys are: ' + ','.join(map(str, user_wlbllib_key_json)),2,the_dict)
        appendTo_DEBUG_log('\nWhitelisted/Blacklisted Paths are: ' + ','.join(map(str, user_wlbllib_path_json)),2,the_dict)
        appendTo_DEBUG_log('\nWhitelisted/Blacklisted NetworkPaths are: ' + ','.join(map(str, user_wlbllib_netpath_json)),2,the_dict)

    return item_isWhitelisted_isBlacklisted


#Because we are not searching directly for unplayed black/whitelisted items; cleanup needs to happen to help the behavioral patterns make sense
def whitelist_and_blacklist_playedPatternCleanup(prefix_str,postproc_dict,the_dict):
    itemId_tracker=[]

    itemsDictionary=postproc_dict['is' + prefix_str + '_and_played_byUserId_Media']
    itemsExtraDictionary=postproc_dict['is' + prefix_str + '_extraInfo_byUserId_Media']
    postproc_dict['user_info']=the_dict['enabled_users']
    baselist=prefix_str[0:prefix_str.rfind("ed")]
    checklist=baselist

    played_created_days_counts_dict={}

    if (('MonitoredUsersAction' in itemsExtraDictionary) and ('MonitoredUsersMeetPlayedFilter' in itemsExtraDictionary)):

        for userId in itemsDictionary:
            for itemId in itemsDictionary[userId]:
                if not (itemId in itemId_tracker):
                    itemId_tracker.append(itemId)
                    item=itemsDictionary[userId][itemId]
                    for sub_user_info in postproc_dict['user_info']:
                        if (not(userId == sub_user_info['user_id'])):
                            if (not(item['Id'] in itemsDictionary[sub_user_info['user_id']])):
                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]={}
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nAdd missing itemid " + str(item['Id']) + " to " + str(itemsExtraDictionary[sub_user_info['user_id']]),3,the_dict)
                            if (not('IsMeetingAction' in itemsExtraDictionary[sub_user_info['user_id']][item['Id']])):

                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['IsMeetingAction']=get_isItemWhitelisted_Blacklisted(checklist,item,sub_user_info,the_dict)

                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nIsMeetingAction: " + str(itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['IsMeetingAction']),3,the_dict)
                            if (not('IsMeetingPlayedFilter' in itemsExtraDictionary[sub_user_info['user_id']][item['Id']])):

                                mediaItemAdditionalInfo=get_ADDITIONAL_itemInfo(sub_user_info,item['Id'],'playedPatternCleanup',the_dict)
                                played_created_days_counts_dict=get_playedCreatedDays_playedCreatedCounts(the_dict,mediaItemAdditionalInfo,postproc_dict)

                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['itemIsPlayed']=played_created_days_counts_dict['itemIsPlayed']
                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['itemPlayedCount']=played_created_days_counts_dict['itemPlayedCount']
                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['item_matches_played_days_filter']=played_created_days_counts_dict['item_matches_played_days_filter'] #meeting played X days ago?
                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['item_matches_created_days_filter']=played_created_days_counts_dict['item_matches_created_days_filter'] #meeting created X days ago?
                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['item_matches_played_count_filter']=played_created_days_counts_dict['item_matches_played_count_filter'] #played X number of times?
                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['item_matches_created_played_count_filter']=played_created_days_counts_dict['item_matches_created_played_count_filter'] #created-played X number of times?
                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['IsMeetingPlayedFilter']=(played_created_days_counts_dict['item_matches_played_days_filter'] and played_created_days_counts_dict['item_matches_played_count_filter']) #meeting complete played_filter_*?
                                itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['IsMeetingCreatedPlayedFilter']=(played_created_days_counts_dict['item_matches_created_days_filter'] and played_created_days_counts_dict['item_matches_created_played_count_filter']) #meeting complete created_filter_*?

                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\itemIsPlayed: " + str(itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['itemIsPlayed']),3,the_dict)
                                    appendTo_DEBUG_log("\itemPlayedCount: " + str(itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['itemPlayedCount']),3,the_dict)
                                    appendTo_DEBUG_log("\item_matches_played_days_filter: " + str(itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['item_matches_played_days_filter']),3,the_dict)
                                    appendTo_DEBUG_log("\item_matches_created_days_filter: " + str(itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['item_matches_created_days_filter']),3,the_dict)
                                    appendTo_DEBUG_log("\item_matches_played_count_filter: " + str(itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['item_matches_played_count_filter']),3,the_dict)
                                    appendTo_DEBUG_log("\item_matches_created_played_count_filter: " + str(itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['item_matches_created_played_count_filter']),3,the_dict)
                                    appendTo_DEBUG_log("\IsMeetingPlayedFilter: " + str(itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['IsMeetingPlayedFilter']),3,the_dict)
                                    appendTo_DEBUG_log("\IsMeetingCreatedPlayedFilter: " + str(itemsExtraDictionary[sub_user_info['user_id']][item['Id']]['IsMeetingCreatedPlayedFilter']),3,the_dict)
                            if (not(item['Id'] in itemsDictionary[sub_user_info['user_id']])):
                                itemsDictionary[sub_user_info['user_id']][item['Id']]=get_ADDITIONAL_itemInfo(sub_user_info,item['Id'],'whitelist_playedPatternCleanup',the_dict)
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\Add item with id: " + str(item['Id']) + "to dictionary",3,the_dict)

    postproc_dict['is' + prefix_str + '_and_played_byUserId_Media']=itemsDictionary
    postproc_dict['is' + prefix_str + '_extraInfo_byUserId_Media']=itemsExtraDictionary

    return postproc_dict