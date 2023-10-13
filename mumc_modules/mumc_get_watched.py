#!/usr/bin/env python3
from mumc_modules.mumc_url import api_query_handler
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_played_created import get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue


def init_blacklist_watched_query(var_dict,the_dict):
    #Initialize api_query_handler() variables for watched media items in blacklists
    var_dict['StartIndex_Blacklist']=0
    var_dict['TotalItems_Blacklist']=1
    var_dict['QueryLimit_Blacklist']=1
    var_dict['QueriesRemaining_Blacklist']=True
    var_dict['APIDebugMsg_Blacklist']=var_dict['media_type_lower'] + '_blacklist_media_items'

    if (var_dict['this_blacklist_lib']['lib_enabled'] and
        var_dict['media_query_blacklisted']):
        #Build query for watched media items in blacklists
        var_dict['IncludeItemTypes_Blacklist']=var_dict['media_type_title']
        var_dict['FieldsState_Blacklist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
        var_dict['SortBy_Blacklist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Blacklist']='Ascending'
        var_dict['EnableUserData_Blacklist']='True'
        var_dict['Recursive_Blacklist']='True'
        var_dict['EnableImages_Blacklist']='False'
        var_dict['CollapseBoxSetItems_Blacklist']='False'
        var_dict['IsPlayedState_Blacklist']=get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(the_dict,var_dict)

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict['FieldsState_Blacklist']=var_dict['FieldsState_Blacklist'] + ',SeriesStudio,seriesStatus'
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Blacklist']='SeriesSortName,' + var_dict['SortBy_Blacklist']
            else:
                var_dict['SortBy_Blacklist']='SeriesName,' + var_dict['SortBy_Blacklist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict['FieldsState_Blacklist']=var_dict['FieldsState_Blacklist'] + ',ArtistItems,AlbumId,AlbumArtist' 
            var_dict['SortBy_Blacklist']='Artists,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Blacklist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Blacklist']+=',audiobook,book'
            else:
                if (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict['IncludeItemTypes_Blacklist']=',book'

    return var_dict


def init_whitelist_watched_query(var_dict,the_dict):
    #Initialize api_query_handler() variables for watched media items in whitelists
    var_dict['StartIndex_Whitelist']=0
    var_dict['TotalItems_Whitelist']=1
    var_dict['QueryLimit_Whitelist']=1
    var_dict['QueriesRemaining_Whitelist']=True
    var_dict['APIDebugMsg_Whitelist']=var_dict['media_type_lower'] + '_whitelist_media_items'

    if (var_dict['this_whitelist_lib']['lib_enabled'] and
        var_dict['media_query_whitelisted']):
        #Build query for watched media items in whitelists
        var_dict['IncludeItemTypes_Whitelist']=var_dict['media_type_title']
        var_dict['FieldsState_Whitelist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
        var_dict['SortBy_Whitelist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Whitelist']='Ascending'
        var_dict['EnableUserData_Whitelist']='True'
        var_dict['Recursive_Whitelist']='True'
        var_dict['EnableImages_Whitelist']='False'
        var_dict['CollapseBoxSetItems_Whitelist']='False'
        var_dict['IsPlayedState_Whitelist']=get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(the_dict,var_dict)

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict['FieldsState_Whitelist']=var_dict['FieldsState_Whitelist'] + ',SeriesStudio,seriesStatus'
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Whitelist']='SeriesSortName,' + var_dict['SortBy_Whitelist']
            else:
                var_dict['SortBy_Whitelist']='SeriesName,' + var_dict['SortBy_Whitelist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict['FieldsState_Whitelist']=var_dict['FieldsState_Whitelist'] + ',ArtistItems,AlbumId,AlbumArtist'
            var_dict['SortBy_Whitelist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Whitelist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Whitelist']+=',AudioBook,Book'
            else:
                if (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict['IncludeItemTypes_Whitelist']=',Book'

    return var_dict


def blacklist_watched_query(user_info,var_dict,the_dict):
    if (var_dict['this_blacklist_lib']['lib_enabled'] and
        var_dict['media_query_blacklisted']):

        #Built query for watched items in blacklists
        var_dict['apiQuery_Blacklist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_blacklist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Blacklist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Blacklist']) + '&Limit=' + str(var_dict['QueryLimit_Blacklist']) + '&IsPlayed=' + var_dict['IsPlayedState_Blacklist'] +
        '&Fields=' + var_dict['FieldsState_Blacklist'] + '&Recursive=' + var_dict['Recursive_Blacklist'] + '&SortBy=' + var_dict['SortBy_Blacklist'] + '&SortOrder=' + var_dict['SortOrder_Blacklist'] +
        '&EnableImages=' + var_dict['EnableImages_Blacklist'] + '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Blacklist'] + '&EnableUserData=' + var_dict['EnableUserData_Blacklist'] + '&api_key=' + var_dict['auth_key'])

        #Send the API query for for watched media items in blacklists
        var_dict=api_query_handler('Blacklist',var_dict,the_dict)
    else:
        #When no media items are blacklisted; simulate an empty query being returned
        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
        var_dict['data_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Blacklist']=0
        var_dict['QueriesRemaining_Blacklist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo watched media items are blacklisted",2,the_dict)

    var_dict['data_Blacklist']['lib_id']=var_dict['this_blacklist_lib']['lib_id']
    var_dict['data_Blacklist']['path']=var_dict['this_blacklist_lib']['path']
    var_dict['data_Blacklist']['network_path']=var_dict['this_blacklist_lib']['network_path']

    return var_dict


def whitelist_watched_query(user_info,var_dict,the_dict):
    if (var_dict['this_whitelist_lib']['lib_enabled'] and
        var_dict['media_query_whitelisted']):

        #Built query for watched items in whitelists
        var_dict['apiQuery_Whitelist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_whitelist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Whitelist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Whitelist']) + '&Limit=' + str(var_dict['QueryLimit_Whitelist']) + '&IsPlayed=' + var_dict['IsPlayedState_Whitelist'] +
        '&Fields=' + var_dict['FieldsState_Whitelist'] + '&Recursive=' + var_dict['Recursive_Whitelist'] + '&SortBy=' + var_dict['SortBy_Whitelist'] + '&SortOrder=' + var_dict['SortOrder_Whitelist'] +
        '&EnableImages=' + var_dict['EnableImages_Whitelist'] + '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Whitelist'] + '&EnableUserData=' + var_dict['EnableUserData_Whitelist'] + '&api_key=' + var_dict['auth_key'])

        #Send the API query for for watched media items in whitelists
        var_dict=api_query_handler('Whitelist',var_dict,the_dict)
    else:
        #When no media items are whitelisted; simulate an empty query being returned
        #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
        var_dict['data_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Whitelist']=0
        var_dict['QueriesRemaining_Whitelist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo watched media items are whitelisted",2,the_dict)

    var_dict['data_Whitelist']['lib_id']=var_dict['this_whitelist_lib']['lib_id']
    var_dict['data_Whitelist']['path']=var_dict['this_whitelist_lib']['path']
    var_dict['data_Whitelist']['network_path']=var_dict['this_whitelist_lib']['network_path']

    return var_dict