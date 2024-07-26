from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_compare_items import get_isItemMatching
from mumc_modules.mumc_server_type import isEmbyServer


def get_opposing_listing_type(listing_type):
    if (listing_type == 'blacklist'):
        return 'whitelist'
    else: #(listing_type == 'whitelist'):
        return 'blacklist'


#Determine if media item is whitelisted/blacklisted for the current user or for another user
def get_isItemWhitelisted_Blacklisted(checklist,item,user_info,the_dict):

    library_matching_behavior=the_dict['admin_settings']['behavior']['matching']

    user_wlbllib_key_json=[]
    user_wlbllib_path_json=[]
    user_wlbllib_netpath_json=[]
    for looplist in user_info[checklist]:
        if (library_matching_behavior.casefold() == 'byid'):
            if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
                if (('subfolder_id' in looplist) and (not (looplist['subfolder_id'] == None))):
                    user_wlbllib_key_json.append(looplist['subfolder_id'])
                else:
                    user_wlbllib_key_json.append(looplist['lib_id'])
            else:
                user_wlbllib_key_json.append(looplist['lib_id'])
        elif (library_matching_behavior.casefold() == 'bypath'):
            user_wlbllib_path_json.append(looplist['path'])
        elif (library_matching_behavior.casefold() == 'bynetworkpath'):
            user_wlbllib_netpath_json.append(looplist['network_path'])

    if (library_matching_behavior.casefold() == 'byid'):
        item_isWhitelisted_isBlacklisted=get_isItemMatching(item['mumc']['lib_id'],user_wlbllib_key_json,the_dict)
    elif (library_matching_behavior.casefold() == 'bypath'):
        item_isWhitelisted_isBlacklisted=get_isItemMatching(item['mumc']['path'],user_wlbllib_path_json,the_dict)
    elif (library_matching_behavior.casefold() == 'bynetworkpath'):
        item_isWhitelisted_isBlacklisted=get_isItemMatching(item['mumc']['network_path'],user_wlbllib_netpath_json,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n\nItem is whitelisted/blacklisted for this user: ' + str(item_isWhitelisted_isBlacklisted),2,the_dict)
        appendTo_DEBUG_log('\nMatching whitelisted/blacklisted value for this user is: ' + str(item_isWhitelisted_isBlacklisted['match_value']),2,the_dict)
        appendTo_DEBUG_log('\nitemLibraryID is: ' + str(item['mumc']['lib_id']),2,the_dict)
        appendTo_DEBUG_log('\nitemLibraryPath is: ' + str(item['mumc']['path']),2,the_dict)
        appendTo_DEBUG_log('\nitemLibraryNetPath is: ' + str(item['mumc']['network_path']),2,the_dict)
        appendTo_DEBUG_log('\nWhitelisted/Blacklisted Keys are: ' + ','.join(map(str, user_wlbllib_key_json)),2,the_dict)
        appendTo_DEBUG_log('\nWhitelisted/Blacklisted Paths are: ' + ','.join(map(str, user_wlbllib_path_json)),2,the_dict)
        appendTo_DEBUG_log('\nWhitelisted/Blacklisted NetworkPaths are: ' + ','.join(map(str, user_wlbllib_netpath_json)),2,the_dict)

    return item_isWhitelisted_isBlacklisted['any_match']