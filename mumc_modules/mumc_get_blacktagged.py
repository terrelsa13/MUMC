
from mumc_modules.mumc_url import api_query_handler
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_tagged import getChildren_taggedMediaItems,list_to_urlparsed_string
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer


def init_blacklist_blacktagged_query(var_dict):
    #Initialize api_query_handler() variables for blacktagged from blacklist media items
    var_dict['StartIndex_Blacktagged_From_Blacklist']=0
    var_dict['TotalItems_Blacktagged_From_Blacklist']=1
    var_dict['QueryLimit_Blacktagged_From_Blacklist']=1
    var_dict['QueriesRemaining_Blacktagged_From_Blacklist']=True
    var_dict['APIDebugMsg_Blacktagged_From_Blacklist']=var_dict['media_type_lower'] + '_blacktagged_from_blacklist_media_items'
    #Encode blacktags so they are url acceptable
    var_dict['Blacktags_Parsed']=list_to_urlparsed_string(var_dict['blacktags'])

    if (var_dict['this_blacklist_lib']['lib_enabled'] and
        var_dict['media_query_blacklisted'] and
        var_dict['media_query_blacktagged']):
        #Build query for blacktagged media items from blacklist
        var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']=var_dict['media_type_title']
        var_dict['FieldsState_Blacktagged_From_Blacklist']='ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
        var_dict['SortBy_Blacktagged_From_Blacklist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Blacktagged_From_Blacklist']='Ascending'
        var_dict['EnableUserData_Blacktagged_From_Blacklist']='True'
        var_dict['Recursive_Blacktagged_From_Blacklist']='True'
        var_dict['EnableImages_Blacktagged_From_Blacklist']='False'
        var_dict['CollapseBoxSetItems_Blacktagged_From_Blacklist']='False'

        if (var_dict['media_type_lower'] == 'movie'):
            var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',BoxSet,CollectionFolder'

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',Season,Series,CollectionFolder'
            var_dict['FieldsState_Blacktagged_From_Blacklist']=var_dict['FieldsState_Blacktagged_From_Blacklist'] + ',SeriesStudio,seriesStatus'
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Blacktagged_From_Blacklist']='SeriesSortName,' + var_dict['SortBy_Blacktagged_From_Blacklist']
            else:
                var_dict['SortBy_Blacktagged_From_Blacklist']='SeriesName,' + var_dict['SortBy_Blacktagged_From_Blacklist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict['FieldsState_Blacktagged_From_Blacklist']=var_dict['FieldsState_Blacktagged_From_Blacklist'] + ',ArtistItems,AlbumId,AlbumArtist'
            var_dict['SortBy_Blacktagged_From_Blacklist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Blacktagged_From_Blacklist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
            else:
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                elif (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Blacklist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

    return var_dict


def init_whitelist_blacktagged_query(var_dict):
    #Initialize api_query_handler() variables for blacktagged from whitelist media items
    var_dict['StartIndex_Blacktagged_From_Whitelist']=0
    var_dict['TotalItems_Blacktagged_From_Whitelist']=1
    var_dict['QueryLimit_Blacktagged_From_Whitelist']=1
    var_dict['QueriesRemaining_Blacktagged_From_Whitelist']=True
    var_dict['APIDebugMsg_Blacktagged_From_Whitelist']=var_dict['media_type_lower'] + '_blacktagged_from whitelisted_media_items'
    #Encode blacktags so they are url acceptable
    var_dict['Blacktags_Parsed']=list_to_urlparsed_string(var_dict['blacktags'])

    if (var_dict['this_whitelist_lib']['lib_enabled'] and
        var_dict['media_query_whitelisted'] and
        var_dict['media_query_blacktagged']):
        #Build query for blacktagged media items from whitelist
        var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']=var_dict['media_type_title']
        var_dict['FieldsState_Blacktagged_From_Whitelist']='ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,UserDataPlayCount,UserDataLastPlayedDate'
        var_dict['SortBy_Blacktagged_From_Whitelist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Blacktagged_From_Whitelist']='Ascending'
        var_dict['EnableUserData_Blacktagged_From_Whitelist']='True'
        var_dict['Recursive_Blacktagged_From_Whitelist']='True'
        var_dict['EnableImages_Blacktagged_From_Whitelist']='False'
        var_dict['CollapseBoxSetItems_Blacktagged_From_Whitelist']='False'

        if (var_dict['media_type_lower'] == 'movie'):
            var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',BoxSet,CollectionFolder'

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',Season,Series,CollectionFolder'
            var_dict['FieldsState_Blacktagged_From_Whitelist']=var_dict['FieldsState_Blacktagged_From_Whitelist'] + ',SeriesStudio,seriesStatus'
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Blacktagged_From_Whitelist']='SeriesSortName,' + var_dict['SortBy_Blacktagged_From_Whitelist']
            else:
                var_dict['SortBy_Blacktagged_From_Whitelist']='SeriesName,' + var_dict['SortBy_Blacktagged_From_Whitelist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict['FieldsState_Blacktagged_From_Whitelist']=var_dict['FieldsState_Blacktagged_From_Whitelist'] + ',ArtistItems,AlbumId,AlbumArtist'
            var_dict['SortBy_Blacktagged_From_Whitelist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict['SortBy_Blacktagged_From_Whitelist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',AudioBook,Book,MusicAlbum,Playlist,CollectionFolder'
            else:
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',Audio,MusicAlbum,Playlist,CollectionFolder'
                elif (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict['IncludeItemTypes_Blacktagged_From_Whitelist']+=',Book,MusicAlbum,Playlist,CollectionFolder'

    return var_dict


def blacklist_blacktagged_query(user_info,var_dict,the_dict):
    #Check if blacktag or blacklist are not an empty strings
    if ((not (var_dict['Blacktags_Parsed'] == '')) and
        var_dict['this_blacklist_lib']['lib_enabled'] and
        var_dict['media_query_blacklisted'] and
        var_dict['media_query_blacktagged']):

        #Built query for blacktagged from blacklist media items
        var_dict['apiQuery_Blacktagged_From_Blacklist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_blacklist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Blacktagged_From_Blacklist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Blacktagged_From_Blacklist']) + '&Limit=' + str(var_dict['QueryLimit_Blacktagged_From_Blacklist']) + '&Fields=' + var_dict['FieldsState_Blacktagged_From_Blacklist'] +
        '&Recursive=' + var_dict['Recursive_Blacktagged_From_Blacklist'] + '&SortBy=' + var_dict['SortBy_Blacktagged_From_Blacklist'] + '&SortOrder=' + var_dict['SortOrder_Blacktagged_From_Blacklist'] + '&EnableImages=' + var_dict['EnableImages_Blacktagged_From_Blacklist'] +
        '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Blacktagged_From_Blacklist'] + '&Tags=' + var_dict['Blacktags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Blacktagged_From_Blacklist'] + '&api_key=' + var_dict['auth_key'])

        #Send the API query for for blacktagged from blacklist media items
        var_dict=api_query_handler('Blacktagged_From_Blacklist',var_dict,the_dict)

        #Define reasoning for lookup
        var_dict['APIDebugMsg_Child_Of_Blacktagged_From_Blacklist']='Child_Of_Blacktagged_Item_From_Blacklist'
        var_dict['data_Child_Of_Blacktagged_From_Blacklist']=getChildren_taggedMediaItems('Blacktagged_From_Blacklist',user_info,var_dict,the_dict)

    else: #((var_dict['Blacktags_Parsed'] == '') or (var_dict['this_blacklist_lib']['lib_id'] == ''))
        var_dict['data_Blacktagged_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Blacktagged_From_Blacklist']=0
        var_dict['QueriesRemaining_Blacktagged_From_Blacklist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo blacktagged media items are blacklisted",2,the_dict)

        var_dict['data_Child_Of_Blacktagged_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Child_Of_Blacktagged_From_Blacklist']=0
        var_dict['QueriesRemaining_Child_Of_Blacktagged_From_Blacklist']=False

    var_dict['data_Blacktagged_From_Blacklist']['lib_id']=var_dict['this_blacklist_lib']['lib_id']
    var_dict['data_Blacktagged_From_Blacklist']['path']=var_dict['this_blacklist_lib']['path']
    var_dict['data_Blacktagged_From_Blacklist']['network_path']=var_dict['this_blacklist_lib']['lib_id']
    var_dict['data_Child_Of_Blacktagged_From_Blacklist']['lib_id']=var_dict['this_blacklist_lib']['lib_id']
    var_dict['data_Child_Of_Blacktagged_From_Blacklist']['path']=var_dict['this_blacklist_lib']['path']
    var_dict['data_Child_Of_Blacktagged_From_Blacklist']['network_path']=var_dict['this_blacklist_lib']['network_path']

    return var_dict


def whitelist_blacktagged_query(user_info,var_dict,the_dict):
    #Check if blacktag or whitelist are not an empty strings
    if ((not (var_dict['Blacktags_Parsed'] == '')) and
        var_dict['this_whitelist_lib']['lib_enabled'] and
        var_dict['media_query_whitelisted'] and
        var_dict['media_query_blacktagged']):

        #Built query for blacktagged from whitelist media items
        var_dict['apiQuery_Blacktagged_From_Whitelist']=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + var_dict['this_whitelist_lib']['lib_id'] + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Blacktagged_From_Whitelist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Blacktagged_From_Whitelist']) + '&Limit=' + str(var_dict['QueryLimit_Blacktagged_From_Whitelist']) + '&Fields=' + var_dict['FieldsState_Blacktagged_From_Whitelist'] +
        '&Recursive=' + var_dict['Recursive_Blacktagged_From_Whitelist'] + '&SortBy=' + var_dict['SortBy_Blacktagged_From_Whitelist'] + '&SortOrder=' + var_dict['SortOrder_Blacktagged_From_Whitelist'] + '&EnableImages=' + var_dict['EnableImages_Blacktagged_From_Whitelist'] +
        '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Blacktagged_From_Whitelist'] + '&Tags=' + var_dict['Blacktags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Blacktagged_From_Whitelist'] + '&api_key=' + var_dict['auth_key'])

        #Send the API query for for blacktagged from whitelist media items
        var_dict=api_query_handler('Blacktagged_From_Whitelist',var_dict,the_dict)

        #Define reasoning for lookup
        var_dict['APIDebugMsg_Child_Of_Blacktagged_From_Whitelist']='Child_Of_Blacktagged_Item_From_Whitelist'
        var_dict['data_Child_Of_Blacktagged_From_Whitelist']=getChildren_taggedMediaItems('Blacktagged_From_Whitelist',user_info,var_dict,the_dict)

    else: #((var_dict['Blacktags_Parsed'] == '') or (var_dict['this_whitelist_lib']['lib_id'] == ''))
        var_dict['data_Blacktagged_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Blacktagged_From_Whitelist']=0
        var_dict['QueriesRemaining_Blacktagged_From_Whitelist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo blacktagged media items are whitelisted",2,the_dict)

        var_dict['data_Child_Of_Blacktagged_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Child_Of_Blacktagged_From_Whitelist']=0
        var_dict['QueriesRemaining_Child_Of_Blacktagged_From_Whitelist']=False

    var_dict['data_Blacktagged_From_Whitelist']['lib_id']=var_dict['this_whitelist_lib']['lib_id']
    var_dict['data_Blacktagged_From_Whitelist']['path']=var_dict['this_whitelist_lib']['path']
    var_dict['data_Blacktagged_From_Whitelist']['network_path']=var_dict['this_whitelist_lib']['network_path']
    var_dict['data_Child_Of_Blacktagged_From_Whitelist']['lib_id']=var_dict['this_whitelist_lib']['lib_id']
    var_dict['data_Child_Of_Blacktagged_From_Whitelist']['path']=var_dict['this_whitelist_lib']['path']
    var_dict['data_Child_Of_Blacktagged_From_Whitelist']['network_path']=var_dict['this_whitelist_lib']['network_path']

    return var_dict