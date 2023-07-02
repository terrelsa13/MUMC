#!/usr/bin/env python3
from mumc_modules.mumc_whitelist import get_isItemWhitelisted,whitelist_playedPatternCleanup,whitelist_and_blacklist_playedPatternCleanup


#Determine if media item whitelisted for the current user or for another user
def get_isItemBlacklisted(the_dict,item,LibraryID,LibraryNetPath,LibraryPath,library_matching_behavior,user_bllib_key_json,user_bllib_netpath_json,user_bllib_path_json):
    return get_isItemWhitelisted(the_dict,item,LibraryID,LibraryNetPath,LibraryPath,library_matching_behavior,user_bllib_key_json,user_bllib_netpath_json,user_bllib_path_json)


#Because we are not searching directly for unplayed blacklisted items; cleanup needs to happen to make the behavioral patterns make sense
def blacklist_playedPatternCleanup(the_dict,itemsDictionary,itemsExtraDictionary,postproc_dict):
    whiteblack_dict={}

    whiteblack_dict['library_matching_behavior']=postproc_dict['library_matching_behavior']
    whiteblack_dict['wl_bl_user_keys_json_verify']=postproc_dict['bluser_keys_json_verify']
    whiteblack_dict['user_wl_bl_lib_keys_json']=postproc_dict['user_bllib_keys_json']
    whiteblack_dict['user_wl_bl_lib_netpath_json']=postproc_dict['user_bllib_netpath_json']
    whiteblack_dict['user_wl_bl_lib_path_json']=postproc_dict['user_bllib_path_json']

    return whitelist_and_blacklist_playedPatternCleanup(the_dict,itemsDictionary,itemsExtraDictionary,whiteblack_dict)