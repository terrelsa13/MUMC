#!/usr/bin/env python3
import multiprocessing
import urllib.parse as urlparse
from datetime import timedelta,datetime
from collections import defaultdict
from mumc_modules.mumc_url import api_query_handler
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType
from mumc_modules.mumc_favorited import getChildren_favoritedMediaItems,get_isMOVIE_Fav,get_isMOVIE_AdvancedFav,get_isEPISODE_Fav,get_isEPISODE_AdvancedFav,get_isAUDIO_Fav,get_isAUDIO_AdvancedFav,get_isAUDIOBOOK_Fav,get_isAUDIOBOOK_AdvancedFav
from mumc_modules.mumc_tagged import getChildren_taggedMediaItems,get_isMOVIE_Tagged,get_isEPISODE_Tagged,get_isAUDIO_Tagged,get_isAUDIOBOOK_Tagged,list_to_urlparsed_string
from mumc_modules.mumc_blacklist_whitelist import get_isItemWhitelisted_Blacklisted
from mumc_modules.mumc_prepare_item import prepare_MOVIEoutput,prepare_EPISODEoutput,prepare_AUDIOoutput,prepare_AUDIOBOOKoutput
from mumc_modules.mumc_days_since import get_days_since_played,get_days_since_created
from mumc_modules.mumc_console_info import build_print_media_item_details,print_user_header
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_played_created import get_isPlayedCreated_FilterValue,get_playedCreatedDays_playedCreatedCounts
from mumc_modules.mumc_item_info import get_SERIES_itemInfo
from mumc_modules.mumc_season_episode import get_season_episode
from mumc_modules.mumc_compare_items import keys_exist


def init_blacklist_whitetagged_query(var_dict):
    #Initialize api_query_handler() variables for whitetagged from blacklist media items
    var_dict['StartIndex_Whitetagged_From_Blacklist']=0
    var_dict['TotalItems_Whitetagged_From_Blacklist']=1
    var_dict['QueryLimit_Whitetagged_From_Blacklist']=1
    var_dict['QueriesRemaining_Whitetagged_From_Blacklist']=True
    var_dict['APIDebugMsg_Whitetagged_From_Blacklist']=var_dict['media_type_lower'] + '_whitetagged_from_blacklisted_media_items'

    #if not (var_dict['this_blacklist_lib']['lib_id'] == ''):
    if (var_dict['this_blacklist_lib']['lib_enabled']):
        #Build query for whitetagged media items from blacklist
        var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']=var_dict['media_type_title']
        var_dict['FieldsState_Whitetagged_From_Blacklist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
        var_dict['SortBy_Whitetagged_From_Blacklist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Whitetagged_From_Blacklist']='Ascending'
        var_dict['EnableUserData_Whitetagged_From_Blacklist']='True'
        var_dict['Recursive_Whitetagged_From_Blacklist']='True'
        var_dict['EnableImages_Whitetagged_From_Blacklist']='False'
        var_dict['CollapseBoxSetItems_Whitetagged_From_Blacklist']='False'
        #Encode whitetags so they are url acceptable
        var_dict['Whitetags_Parsed']=list_to_urlparsed_string(var_dict['whitetags'])

        if (var_dict['media_type_lower'] == 'movie'):
            var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',BoxSet,CollectionFolder'

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',Season,Series,CollectionFolder'
            var_dict['FieldsState_Whitetagged_From_Blacklist']=var_dict['FieldsState_Whitetagged_From_Blacklist'] + ',SeriesStudio,seriesStatus'
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Whitetagged_From_Blacklist']='SeriesSortName,' + var_dict['SortBy_Whitetagged_From_Blacklist']
            else:
                var_dict['SortBy_Whitetagged_From_Blacklist']='SeriesName,' + var_dict['SortBy_Whitetagged_From_Blacklist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict['FieldsState_Whitetagged_From_Blacklist']=var_dict['FieldsState_Whitetagged_From_Blacklist'] + ',ArtistItems,AlbumId,AlbumArtist'
            var_dict['SortBy_Whitetagged_From_Blacklist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Whitetagged_From_Blacklist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',Audio,AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
            else:
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                elif (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

    return var_dict


def init_whitelist_whitetagged_query(var_dict):
    #Initialize api_query_handler() variables for whitetagged from whitelist media items
    var_dict['StartIndex_Whitetagged_From_Whitelist']=0
    var_dict['TotalItems_Whitetagged_From_Whitelist']=1
    var_dict['QueryLimit_Whitetagged_From_Whitelist']=1
    var_dict['QueriesRemaining_Whitetagged_From_Whitelist']=True
    var_dict['APIDebugMsg_Whitetagged_From_Whitelist']=var_dict['media_type_lower'] + '_whitetagged_from_whitelisted_media_items'

    #if not (var_dict['this_whitelist_lib']['lib_id'] == ''):
    if (var_dict['this_whitelist_lib']['lib_enabled']):
        #Build query for whitetagged media items from whitelist
        var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']=var_dict['media_type_title']
        var_dict['FieldsState_Whitetagged_From_Whitelist']='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
        var_dict['SortBy_Whitetagged_From_Whitelist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Whitetagged_From_Whitelist']='Ascending'
        var_dict['EnableUserData_Whitetagged_From_Whitelist']='True'
        var_dict['Recursive_Whitetagged_From_Whitelist']='True'
        var_dict['EnableImages_Whitetagged_From_Whitelist']='False'
        var_dict['CollapseBoxSetItems_Whitetagged_From_Whitelist']='False'
        #Encode whitetags so they are url acceptable
        var_dict['Whitetags_Parsed']=list_to_urlparsed_string(var_dict['whitetags'])

        if (var_dict['media_type_lower'] == 'movie'):
            var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',BoxSet,CollectionFolder'

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',Season,Series,CollectionFolder'
            var_dict['FieldsState_Whitetagged_From_Whitelist']=var_dict['FieldsState_Whitetagged_From_Whitelist'] + ',SeriesStudio,seriesStatus'
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Whitetagged_From_Whitelist']='SeriesSortName,' + var_dict['SortBy_Whitetagged_From_Whitelist']
            else:
                var_dict['SortBy_Whitetagged_From_Whitelist']='SeriesName,' + var_dict['SortBy_Whitetagged_From_Whitelist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict['FieldsState_Whitetagged_From_Whitelist']=var_dict['FieldsState_Whitetagged_From_Whitelist'] + ',ArtistItems,AlbumId,AlbumArtist'
            var_dict['SortBy_Whitetagged_From_Whitelist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Whitetagged_From_Whitelist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
            else:
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',MusicAlbum,Playlist,CollectionFolder'
                elif (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

    return var_dict


def blacklist_whitetagged_query(user_info,var_dict,the_dict):
    #Check if whitetag or blacklist are not an empty strings
    #if (( not (var_dict['Whitetags_Parsed'] == '')) and ( not (var_dict['this_blacklist_lib']['lib_id'] == ''))):
    if ((not var_dict['Whitetags_Parsed']) and (var_dict['this_blacklist_lib']['lib_enabled'])):
        #Built query for whitetagged from Blacklist media items
        var_dict['apiQuery_Whitetagged_From_Blacklist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_blacklist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Whitetagged_From_Blacklist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Whitetagged_From_Blacklist']) + '&Limit=' + str(var_dict['QueryLimit_Whitetagged_From_Blacklist']) + '&Fields=' + var_dict['FieldsState_Whitetagged_From_Blacklist'] +
        '&Recursive=' + var_dict['Recursive_Whitetagged_From_Blacklist'] + '&SortBy=' + var_dict['SortBy_Whitetagged_From_Blacklist'] + '&SortOrder=' + var_dict['SortOrder_Whitetagged_From_Blacklist'] + '&EnableImages=' + var_dict['EnableImages_Whitetagged_From_Blacklist'] +
        '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Whitetagged_From_Blacklist'] + '&Tags=' + var_dict['Whitetags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Whitetagged_From_Blacklist'] + '&api_key=' + var_dict['auth_key'])

        var_dict['data_Whitetagged_From_Blacklist']['lib_id']=var_dict['this_blacklist_lib']['lib_id']
        var_dict['data_Child_Of_Whitetagged_From_Blacklist_Children']['lib_id']=var_dict['this_blacklist_lib']['lib_id']

        #Send the API query for for whitetagged from Blacklist= media items
        #var_dict['data_Whitetagged_From_Blacklist'],var_dict['StartIndex_Whitetagged_From_Blacklist'],var_dict['TotalItems_Whitetagged_From_Blacklist'],var_dict['QueryLimit_Whitetagged_From_Blacklist'],var_dict['QueriesRemaining_Whitetagged_From_Blacklist']=api_query_handler(var_dict['apiQuery_Whitetagged_From_Blacklist'],var_dict['StartIndex_Whitetagged_From_Blacklist'],var_dict['TotalItems_Whitetagged_From_Blacklist'],var_dict['QueryLimit_Whitetagged_From_Blacklist'],var_dict['APIDebugMsg_Whitetagged_From_Blacklist'],the_dict)
        var_dict=api_query_handler('Whitetagged_From_Blacklist',var_dict,the_dict)

        #Define reasoning for lookup
        var_dict['APIDebugMsg_Child_Of_Whitetagged_From_Blacklist']='Child_Of_Whitetagged_Item_From_Blacklist'
        #data_Whitetagged_From_Blacklist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Blacklist,whitetags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Whitetag_From_Blacklist_Child,media_played_days,media_created_days)
        var_dict['data_Child_Of_Whitetagged_From_Blacklist_Children']=getChildren_taggedMediaItems('Whitetagged_From_Blacklist',user_info,var_dict,the_dict)

    else: #(Whitetags_Tagged_From_Blacklist == '')
        var_dict['data_Whitetagged_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Whitetagged_From_Blacklist']=0
        var_dict['QueriesRemaining_Whitetagged_From_Blacklist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo whitetagged media items are blacklisted",2,the_dict)

    return var_dict


def whitelist_whitetagged_query(user_info,var_dict,the_dict):
    #Check if whitetag or whitelist are not an empty strings
    #if (( not (var_dict['Whitetags_Parsed'] == '')) and ( not (var_dict['this_whitelist_lib']['lib_id'] == ''))):
    if ((not var_dict['Whitetags_Parsed']) and (var_dict['this_whitelist_lib']['lib_enabled'])):
        #Built query for whitetagged_From_Whitelist= media items
        var_dict['apiQuery_Whitetagged_From_Whitelist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_whitelist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Whitetagged_From_Whitelist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Whitetagged_From_Whitelist']) + '&Limit=' + str(var_dict['QueryLimit_Whitetagged_From_Whitelist']) + '&Fields=' + var_dict['FieldsState_Whitetagged_From_Whitelist'] +
        '&Recursive=' + var_dict['Recursive_Whitetagged_From_Whitelist'] + '&SortBy=' + var_dict['SortBy_Whitetagged_From_Whitelist'] + '&SortOrder=' + var_dict['SortOrder_Whitetagged_From_Whitelist'] + '&EnableImages=' + var_dict['EnableImages_Whitetagged_From_Whitelist'] +
        '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Whitetagged_From_Whitelist'] + '&Tags=' + var_dict['Whitetags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Whitetagged_From_Whitelist'] + '&api_key=' + var_dict['auth_key'])

        var_dict['data_Whitetagged_From_Whitelist']['lib_id']=var_dict['this_blacklist_lib']['lib_id']
        var_dict['data_Child_Of_Whitetagged_From_Whitelist_Children']['lib_id']=var_dict['this_blacklist_lib']['lib_id']

        #Send the API query for for whitetagged_From_Whitelist= media items
        #var_dict['data_Whitetagged_From_Whitelist'],var_dict['StartIndex_Whitetagged_From_Whitelist'],var_dict['TotalItems_Whitetagged_From_Whitelist'],var_dict['QueryLimit_Whitetagged_From_Whitelist'],var_dict['QueriesRemaining_Whitetagged_From_Whitelist']=api_query_handler(var_dict['apiQuery_Whitetagged_From_Whitelist'],var_dict['StartIndex_Whitetagged_From_Whitelist'],var_dict['TotalItems_Whitetagged_From_Whitelist'],var_dict['QueryLimit_Whitetagged_From_Whitelist'],var_dict['APIDebugMsg_Whitetagged_From_Whitelist'],the_dict)
        var_dict=api_query_handler('Whitetagged_From_Whitelist',var_dict,the_dict)

        #Define reasoning for lookup
        var_dict['APIDebugMsg_Child_Of_Whitetagged_From_Whitelist']='Child_Of_Whitetagged_Item_From_Whitelist'
        #data_Whitetagged_From_Whitelist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Whitelist,whitetags,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,APIDebugMsg_Whitetag_From_Whitelist_Child,media_played_days,media_created_days)
        var_dict['data_Child_Of_Whitetagged_From_Whitelist_Children']=getChildren_taggedMediaItems('Whitetagged_From_Whitelist',user_info,var_dict,the_dict)

    else: #(var_dict['Whitetags_Parsed'] == '')
        var_dict['data_Whitetagged_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Whitetagged_From_Whitelist']=0
        var_dict['QueriesRemaining_Whitetagged_From_Whitelist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo whitetagged media items are whitelisted",2,the_dict)

    return var_dict