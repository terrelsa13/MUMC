#!/usr/bin/env python3
from mumc_modules.mumc_url import api_query_handler
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_favorited import getChildren_favoritedMediaItems
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer


def init_blacklist_favorited_query(var_dict):
    #Initialize api_query_handler() variables for Favorited from Blacklist media items
    var_dict['StartIndex_Favorited_From_Blacklist']=0
    var_dict['TotalItems_Favorited_From_Blacklist']=1
    var_dict['QueryLimit_Favorited_From_Blacklist']=1
    var_dict['QueriesRemaining_Favorited_From_Blacklist']=True
    var_dict['APIDebugMsg_Favorited_From_Blacklist']=var_dict['media_type_lower'] + '_Favorited_From_Blacklisted_media_items'

    if (var_dict['this_blacklist_lib']['lib_enabled']):
            #Build query for Favorited_From_Blacklist media items
        var_dict['IncludeItemTypes_Favorited_From_Blacklist']=var_dict['media_type_title']
        var_dict['FieldsState_Favorited_From_Blacklist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
        var_dict['SortBy_Favorited_From_Blacklist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Favorited_From_Blacklist']='Ascending'
        var_dict['EnableUserData_Favorited_From_Blacklist']='True'
        var_dict['Recursive_Favorited_From_Blacklist']='True'
        var_dict['EnableImages_Favorited_From_Blacklist']='False'
        var_dict['CollapseBoxSetItems_Favorited_From_Blacklist']='False'
        var_dict['IsFavorite_From_Blacklist']='True'

        if (var_dict['media_type_lower'] == 'movie'):
            var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',BoxSet,CollectionFolder'

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',Season,Series,CollectionFolder'
            var_dict['FieldsState_Favorited_From_Blacklist']=var_dict['FieldsState_Favorited_From_Blacklist'] + ',SeriesStudio,seriesStatus'
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Favorited_From_Blacklist']='SeriesSortName,' + var_dict['SortBy_Favorited_From_Blacklist']
            else:
                var_dict['SortBy_Favorited_From_Blacklist']='SeriesName,' + var_dict['SortBy_Favorited_From_Blacklist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict['FieldsState_Favorited_From_Blacklist']=var_dict['FieldsState_Favorited_From_Blacklist'] + ',ArtistItems,AlbumId,AlbumArtist'
            var_dict['SortBy_Favorited_From_Blacklist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Favorited_From_Blacklist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
            else:
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',MusicAlbum,Playlist,CollectionFolder'
                elif (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict['IncludeItemTypes_Favorited_From_Blacklist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

    return var_dict


def init_whitelist_favorited_query(var_dict):
    #Initialize api_query_handler() variables for Favorited from Whitelist media items
    var_dict['StartIndex_Favorited_From_Whitelist']=0
    var_dict['TotalItems_Favorited_From_Whitelist']=1
    var_dict['QueryLimit_Favorited_From_Whitelist']=1
    var_dict['QueriesRemaining_Favorited_From_Whitelist']=True
    var_dict['APIDebugMsg_Favorited_From_Whitelist']=var_dict['media_type_lower'] + '_Favorited_From_Whitelisted_media_items'

    if (var_dict['this_whitelist_lib']['lib_enabled']):
        #Build query for Favorited_From_Whitelist media items
        var_dict['IncludeItemTypes_Favorited_From_Whitelist']=var_dict['media_type_title']
        var_dict['FieldsState_Favorited_From_Whitelist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
        var_dict['SortBy_Favorited_From_Whitelist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Favorited_From_Whitelist']='Ascending'
        var_dict['EnableUserData_Favorited_From_Whitelist']='True'
        var_dict['Recursive_Favorited_From_Whitelist']='True'
        var_dict['EnableImages_Favorited_From_Whitelist']='False'
        var_dict['CollapseBoxSetItems_Favorited_From_Whitelist']='False'
        var_dict['IsFavorite_From_Whitelist']='True'

        if (var_dict['media_type_lower'] == 'movie'):
            var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',BoxSet,CollectionFolder'

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',Season,Series,CollectionFolder'
            var_dict['FieldsState_Favorited_From_Whitelist']=var_dict['FieldsState_Favorited_From_Whitelist'] + ',SeriesStudio,seriesStatus'
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Favorited_From_Whitelist']='SeriesSortName,' + var_dict['SortBy_Favorited_From_Whitelist']
            else:
                var_dict['SortBy_Favorited_From_Whitelist']='SeriesName,' + var_dict['SortBy_Favorited_From_Whitelist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict['FieldsState_Favorited_From_Whitelist']=var_dict['FieldsState_Favorited_From_Whitelist'] + ',ArtistItems,AlbumId,AlbumArtist'
            var_dict['SortBy_Favorited_From_Whitelist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Favorited_From_Whitelist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
            else:
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                elif (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict['IncludeItemTypes_Favorited_From_Whitelist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

    return var_dict


def blacklist_favorited_query(user_info,var_dict,the_dict):
    if (var_dict['this_blacklist_lib']['lib_enabled']):
        #Built query for Favorited from Blacklist media items
        var_dict['apiQuery_Favorited_From_Blacklist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_blacklist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Favorited_From_Blacklist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Favorited_From_Blacklist']) + '&Limit=' + str(var_dict['QueryLimit_Favorited_From_Blacklist']) + '&Fields=' + var_dict['FieldsState_Favorited_From_Blacklist'] +
        '&Recursive=' + var_dict['Recursive_Favorited_From_Blacklist'] + '&SortBy=' + var_dict['SortBy_Favorited_From_Blacklist'] + '&SortOrder=' + var_dict['SortOrder_Favorited_From_Blacklist'] + '&EnableImages=' + var_dict['EnableImages_Favorited_From_Blacklist'] +
        '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Favorited_From_Blacklist'] + '&IsFavorite=' + var_dict['IsFavorite_From_Blacklist'] + '&EnableUserData=' + var_dict['EnableUserData_Favorited_From_Blacklist'] + '&api_key=' + var_dict['auth_key'])

        #Send the API query for for Favorited from Blacklist media items
        var_dict=api_query_handler('Favorited_From_Blacklist',var_dict,the_dict)

        #Define reasoning for lookup
        var_dict['APIDebugMsg_Child_Of_Favorited_Item_From_Blacklist']='Child_Of_Favorited_Item_From_Blacklist'
        var_dict['data_Child_Of_Favorited_Item_From_Blacklist']=getChildren_favoritedMediaItems('From_Blacklist',user_info,var_dict,the_dict)

    else:
        #When no media items are blacklisted; simulate an empty query being returned
        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
        var_dict['data_Favorited_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Favorited_From_Blacklist']=0
        var_dict['QueriesRemaining_Favorited_From_Blacklist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo favorited media items are blacklisted",2,the_dict)

        var_dict['data_Child_Of_Favorited_Item_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Child_Of_Favorited_Item_From_Blacklistt']=0
        var_dict['QueriesRemaining_Child_Of_Favorited_Item_From_Blacklist']=False

    var_dict['data_Favorited_From_Blacklist']['lib_id']=var_dict['this_blacklist_lib']['lib_id']
    var_dict['data_Favorited_From_Blacklist']['path']=var_dict['this_blacklist_lib']['path']
    var_dict['data_Favorited_From_Blacklist']['network_path']=var_dict['this_blacklist_lib']['network_path']
    var_dict['data_Child_Of_Favorited_Item_From_Blacklist']['lib_id']=var_dict['this_blacklist_lib']['lib_id']
    var_dict['data_Child_Of_Favorited_Item_From_Blacklist']['path']=var_dict['this_blacklist_lib']['path']
    var_dict['data_Child_Of_Favorited_Item_From_Blacklist']['network_path']=var_dict['this_blacklist_lib']['network_path']

    return var_dict


def whitelist_favorited_query(user_info,var_dict,the_dict):
    if (var_dict['this_whitelist_lib']['lib_enabled']):
        #Built query for Favorited From Whitelist media items
        var_dict['apiQuery_Favorited_From_Whitelist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_whitelist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Favorited_From_Whitelist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Favorited_From_Whitelist']) + '&Limit=' + str(var_dict['QueryLimit_Favorited_From_Whitelist']) + '&Fields=' + var_dict['FieldsState_Favorited_From_Whitelist'] +
        '&Recursive=' + var_dict['Recursive_Favorited_From_Whitelist'] + '&SortBy=' + var_dict['SortBy_Favorited_From_Whitelist'] + '&SortOrder=' + var_dict['SortOrder_Favorited_From_Whitelist'] + '&EnableImages=' + var_dict['EnableImages_Favorited_From_Whitelist'] +
        '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Favorited_From_Whitelist'] + '&IsFavorite=' + var_dict['IsFavorite_From_Whitelist'] + '&EnableUserData=' + var_dict['EnableUserData_Favorited_From_Whitelist'] + '&api_key=' + var_dict['auth_key'])

        #Send the API query for for Favorited from Whitelist media items
        var_dict=api_query_handler('Favorited_From_Whitelist',var_dict,the_dict)

        #Define reasoning for lookup
        var_dict['APIDebugMsg_Child_Of_Favorited_Item_From_Whitelist']='Child_Of_Favorited_Item_From_Whitelist'
        var_dict['data_Child_Of_Favorited_Item_From_Whitelist']=getChildren_favoritedMediaItems('From_Whitelist',user_info,var_dict,the_dict)

    else:
        #When no media items are whitelisted; simulate an empty query being returned
        #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
        var_dict['data_Favorited_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Favorited_From_Whitelist']=0
        var_dict['QueriesRemaining_Favorited_From_Whitelist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo favorited media items are whitelisted",2,the_dict)

        var_dict['data_Child_Of_Favorited_Item_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Child_Of_Favorited_Item_From_Whitelistt']=0
        var_dict['QueriesRemaining_Child_Of_Favorited_Item_From_Whitelist']=False

    var_dict['data_Favorited_From_Whitelist']['lib_id']=var_dict['this_whitelist_lib']['lib_id']
    var_dict['data_Favorited_From_Whitelist']['path']=var_dict['this_whitelist_lib']['path']
    var_dict['data_Favorited_From_Whitelist']['network_path']=var_dict['this_whitelist_lib']['network_path']
    var_dict['data_Child_Of_Favorited_Item_From_Whitelist']['lib_id']=var_dict['this_whitelist_lib']['lib_id']
    var_dict['data_Child_Of_Favorited_Item_From_Whitelist']['path']=var_dict['this_whitelist_lib']['path']
    var_dict['data_Child_Of_Favorited_Item_From_Whitelist']['network_path']=var_dict['this_whitelist_lib']['network_path']

    return var_dict