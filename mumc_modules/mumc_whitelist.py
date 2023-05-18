#!/usr/bin/env python3
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_compare_items import get_isItemMatching_doesItemStartWith
from mumc_modules.mumc_played_created import get_playedCreatedDays_playedCreatedCounts
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo


#Determine if media item whitelisted for the current user or for another user
def get_isItemWhitelisted(the_dict,item,LibraryID,LibraryNetPath,LibraryPath,library_matching_behavior,user_wllib_key_json,user_wllib_netpath_json,user_wllib_path_json):
    item_isWhiteListed=False
    itemWhiteListedValue=''

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    if (library_matching_behavior == 'byid'):
        item_isWhiteListed, itemWhiteListedValue=get_isItemMatching_doesItemStartWith(LibraryID,user_wllib_key_json,the_dict)
    elif (library_matching_behavior == 'bypath'):
        if ("Path" in item):
            ItemPath = item["Path"]
        elif (("MediaSources" in item) and ("Path" in item["MediaSources"])):
            ItemPath = item["MediaSources"]["Path"]
        else:
            ItemPath = LibraryPath
        item_isWhiteListed, itemWhiteListedValue=get_isItemMatching_doesItemStartWith(ItemPath,user_wllib_path_json,the_dict)
    elif (library_matching_behavior == 'bynetworkpath'):
        if ("Path" in item):
            ItemNetPath = item["Path"]
        elif (("MediaSources" in item) and ("Path" in item["MediaSources"])):
            ItemNetPath = item["MediaSources"]["Path"]
        else:
            ItemNetPath = LibraryNetPath
        item_isWhiteListed, itemWhiteListedValue=get_isItemMatching_doesItemStartWith(ItemNetPath,user_wllib_netpath_json,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\nItem is whitelisted/blacklisted for this user: ' + str(item_isWhiteListed),2,the_dict)
        appendTo_DEBUG_log('\nMatching whitelisted/blacklisted value for this user is: ' + str(itemWhiteListedValue),2,the_dict)
        appendTo_DEBUG_log('\nLibraryId is: ' + LibraryID,2,the_dict)
        appendTo_DEBUG_log('\nLibraryPath is: ' + LibraryPath,2,the_dict)
        appendTo_DEBUG_log('\nLibraryNetPath is: ' + LibraryNetPath,2,the_dict)
        appendTo_DEBUG_log('\nWhitelisted/Blacklisted Keys are: ' + user_wllib_key_json,2,the_dict)
        appendTo_DEBUG_log('\nWhitelisted/Blacklisted Paths are: ' + user_wllib_path_json,2,the_dict)
        appendTo_DEBUG_log('\nWhitelisted/Blacklisted NetworkPaths are: ' + user_wllib_netpath_json,2,the_dict)

    return item_isWhiteListed


#Because we are not searching directly for unplayed whitelisted items; cleanup needs to happen to help the behavioral patterns make sense
def whitelist_playedPatternCleanup(the_dict,itemsDictionary,itemsExtraDictionary,library_matching_behavior,wluser_keys_json_verify,user_wllib_keys_json,user_wllib_netpaths_json,user_wllib_paths_json):
    itemId_tracker=[]

    if (('MonitoredUsersAction' in itemsExtraDictionary) and ('MonitoredUsersMeetPlayedFilter' in itemsExtraDictionary)):

        for userId in itemsDictionary:
            for itemId in itemsDictionary[userId]:
                if not (itemId in itemId_tracker):
                    itemId_tracker.append(itemId)
                    item=itemsDictionary[userId][itemId]
                    for subUserId in wluser_keys_json_verify:
                        if (not(userId == subUserId)):
                            if (not(item['Id'] in itemsDictionary[subUserId])):
                                itemsExtraDictionary[subUserId][item['Id']]={}
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nAdd missing itemid " + str(item['Id']) + " to " + str(itemsExtraDictionary[subUserId]),3,the_dict)
                            if (not('IsMeetingAction' in itemsExtraDictionary[subUserId][item['Id']])):
                                itemsExtraDictionary[subUserId][item['Id']]['IsMeetingAction']=get_isItemWhitelisted(the_dict,item,itemsExtraDictionary[userId][item['Id']]['WhitelistBlacklistLibraryId'],itemsExtraDictionary[userId][item['Id']]['WhitelistBlacklistLibraryNetPath'],itemsExtraDictionary[userId][item['Id']]['WhitelistBlacklistLibraryPath'],library_matching_behavior,
                                user_wllib_keys_json[wluser_keys_json_verify.index(subUserId)],user_wllib_netpaths_json[wluser_keys_json_verify.index(subUserId)],user_wllib_paths_json[wluser_keys_json_verify.index(subUserId)])
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nIsMeetingAction: " + str(itemsExtraDictionary[subUserId][item['Id']]['IsMeetingAction']),3,the_dict)
                            if (not('IsMeetingPlayedFilter' in itemsExtraDictionary[subUserId][item['Id']])):
                                #if ((behaviorFilter == 0) or (behaviorFilter == 1) or (behaviorFilter == 2)):
                                    #itemsExtraDictionary[subUserId][item['Id']]['IsMeetingPlayedFilter']=True
                                #else:
                                item_matches_played_days_filter,x,item_matches_played_count_filter,y=get_playedCreatedDays_playedCreatedCounts(the_dict,get_ADDITIONAL_itemInfo(subUserId,item['Id'],'playedPatternCleanup',the_dict),itemsExtraDictionary[userId][item['Id']]['PlayedDays'],itemsExtraDictionary[userId][item['Id']]['CreatedDays'],itemsExtraDictionary[userId][item['Id']]['CutOffDatePlayed'],itemsExtraDictionary[userId][item['Id']]['CutOffDateCreated'],itemsExtraDictionary[userId][item['Id']]['PlayedCountComparison'],itemsExtraDictionary[userId][item['Id']]['PlayedCount'],itemsExtraDictionary[userId][item['Id']]['CreatedPlayedCountComparison'],itemsExtraDictionary[userId][item['Id']]['CreatedPlayedCount'])
                                itemsExtraDictionary[subUserId][item['Id']]['IsMeetingPlayedFilter']=(item_matches_played_days_filter and item_matches_played_count_filter)
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\IsMeetingPlayedFilter: " + str(itemsExtraDictionary[subUserId][item['Id']]['IsMeetingPlayedFilter']),3,the_dict)
                            if (not(item['Id'] in itemsDictionary[subUserId])):
                                itemsDictionary[subUserId][item['Id']]=get_ADDITIONAL_itemInfo(subUserId,item['Id'],'whitelist_playedPatternCleanup',the_dict)
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\Add item with id: " + str(item['Id']) + "to dictionary",3,the_dict)

    return itemsDictionary,itemsExtraDictionary