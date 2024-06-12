from mumc_modules.mumc_url import api_query_handler,build_request_message
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_tagged import getChildren_taggedMediaItems,list_to_urlparsed_string
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer


def init_blacklist_whitetagged_query(var_dict):
    #Initialize api_query_handler() variables for whitetagged from blacklist media items
    var_dict['StartIndex_Whitetagged_From_Blacklist']=0
    var_dict['TotalItems_Whitetagged_From_Blacklist']=1
    var_dict['QueryLimit_Whitetagged_From_Blacklist']=1
    var_dict['QueriesRemaining_Whitetagged_From_Blacklist']=True
    var_dict['APIDebugMsg_Whitetagged_From_Blacklist']=var_dict['media_type_lower'] + '_whitetagged_from_blacklisted_media_items'
    #Encode whitetags so they are url acceptable
    var_dict['Whitetags_Parsed']=list_to_urlparsed_string(var_dict['whitetags'])

    if (var_dict['this_blacklist_lib']['lib_enabled'] and
        var_dict['enable_media_query_blacklisted_whitetagged']):
        #Build query for whitetagged media items from blacklist
        var_dict['IncludeItemTypes_Whitetagged_From_Blacklist']=var_dict['media_type_title']
        var_dict['FieldsState_Whitetagged_From_Blacklist']='ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
        var_dict['SortBy_Whitetagged_From_Blacklist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Whitetagged_From_Blacklist']='Ascending'
        var_dict['EnableUserData_Whitetagged_From_Blacklist']='True'
        var_dict['Recursive_Whitetagged_From_Blacklist']='True'
        var_dict['EnableImages_Whitetagged_From_Blacklist']='False'
        var_dict['CollapseBoxSetItems_Whitetagged_From_Blacklist']='False'

        if (isEmbyServer(var_dict['server_brand'])):
            var_dict['FieldsState_Whitetagged_From_Blacklist']+=',UserDataPlayCount,UserDataLastPlayedDate'

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
    #Encode whitetags so they are url acceptable
    var_dict['Whitetags_Parsed']=list_to_urlparsed_string(var_dict['whitetags'])

    if (var_dict['this_whitelist_lib']['lib_enabled'] and
        var_dict['enable_media_query_whitelisted_whitetagged']):
        #Build query for whitetagged media items from whitelist
        var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']=var_dict['media_type_title']
        var_dict['FieldsState_Whitetagged_From_Whitelist']='ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
        var_dict['SortBy_Whitetagged_From_Whitelist']='ParentIndexNumber,IndexNumber,Name'
        var_dict['SortOrder_Whitetagged_From_Whitelist']='Ascending'
        var_dict['EnableUserData_Whitetagged_From_Whitelist']='True'
        var_dict['Recursive_Whitetagged_From_Whitelist']='True'
        var_dict['EnableImages_Whitetagged_From_Whitelist']='False'
        var_dict['CollapseBoxSetItems_Whitetagged_From_Whitelist']='False'

        if (isEmbyServer(var_dict['server_brand'])):
            var_dict['FieldsState_Whitetagged_From_Whitelist']+=',UserDataPlayCount,UserDataLastPlayedDate'

        if (var_dict['media_type_lower'] == 'movie'):
            var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',BoxSet,CollectionFolder'

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict['IncludeItemTypes_Whitetagged_From_Whitelist']+=',Season,Series,CollectionFolder'
            var_dict['FieldsState_Whitetagged_From_Whitelist']+=',SeriesStudio,seriesStatus'
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Whitetagged_From_Whitelist']='SeriesSortName,' + var_dict['SortBy_Whitetagged_From_Whitelist']
            else:
                var_dict['SortBy_Whitetagged_From_Whitelist']='SeriesName,' + var_dict['SortBy_Whitetagged_From_Whitelist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict['FieldsState_Whitetagged_From_Whitelist']+=',ArtistItems,AlbumId,AlbumArtist'
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

    if (isJellyfinServer(var_dict['server_brand'])):
        parent_id=var_dict['this_blacklist_lib']['lib_id']
    else:
        if (('subfolder_id' in var_dict['this_blacklist_lib']) and (not (var_dict['this_blacklist_lib']['subfolder_id'] == None))):
            parent_id=var_dict['this_blacklist_lib']['subfolder_id']
        else:
            parent_id=var_dict['this_blacklist_lib']['lib_id']

    #Check if whitetag or blacklist are not an empty strings
    if ((not (var_dict['Whitetags_Parsed'] == '')) and
        var_dict['this_blacklist_lib']['lib_enabled'] and
        var_dict['enable_media_query_blacklisted_whitetagged']):

        #Built query for whitetagged from Blacklist media items
        url=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + parent_id + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Whitetagged_From_Blacklist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Whitetagged_From_Blacklist']) + '&Limit=' + str(var_dict['QueryLimit_Whitetagged_From_Blacklist']) + '&Fields=' + var_dict['FieldsState_Whitetagged_From_Blacklist'] +
        '&Recursive=' + var_dict['Recursive_Whitetagged_From_Blacklist'] + '&SortBy=' + var_dict['SortBy_Whitetagged_From_Blacklist'] + '&SortOrder=' + var_dict['SortOrder_Whitetagged_From_Blacklist'] + '&EnableImages=' + var_dict['EnableImages_Whitetagged_From_Blacklist'] +
        '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Whitetagged_From_Blacklist'] + '&Tags=' + var_dict['Whitetags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Whitetagged_From_Blacklist'])

        var_dict['apiQuery_Whitetagged_From_Blacklist']=build_request_message(url,the_dict)

        #Send the API query for for whitetagged from Blacklist= media items
        var_dict=api_query_handler('Whitetagged_From_Blacklist',var_dict,the_dict)

        #Define reasoning for lookup
        var_dict['APIDebugMsg_Child_Of_Whitetagged_From_Blacklist']='Child_Of_Whitetagged_Item_From_Blacklist'
        var_dict['data_Child_Of_Whitetagged_From_Blacklist']=getChildren_taggedMediaItems('Whitetagged_From_Blacklist',user_info,var_dict,the_dict)

        var_dict['data_Whitetagged_From_Blacklist']['lib_id']=parent_id
        var_dict['data_Child_Of_Whitetagged_From_Blacklist']['lib_id']=parent_id

    else: #(Whitetags_Tagged_From_Blacklist == '')
        var_dict['data_Whitetagged_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Whitetagged_From_Blacklist']=0
        var_dict['QueriesRemaining_Whitetagged_From_Blacklist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo whitetagged media items are blacklisted",2,the_dict)

        var_dict['data_Child_Of_Whitetagged_From_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Child_Of_Whitetagged_From_Blacklist']=0
        var_dict['QueriesRemaining_Child_Of_Whitetagged_From_Blacklist']=False

    var_dict['data_Whitetagged_From_Blacklist']['lib_id']=parent_id
    var_dict['data_Whitetagged_From_Blacklist']['path']=var_dict['this_blacklist_lib']['path']
    var_dict['data_Whitetagged_From_Blacklist']['network_path']=var_dict['this_blacklist_lib']['network_path']
    var_dict['data_Child_Of_Whitetagged_From_Blacklist']['lib_id']=parent_id
    var_dict['data_Child_Of_Whitetagged_From_Blacklist']['path']=var_dict['this_blacklist_lib']['path']
    var_dict['data_Child_Of_Whitetagged_From_Blacklist']['network_path']=var_dict['this_blacklist_lib']['network_path']

    return var_dict


def whitelist_whitetagged_query(user_info,var_dict,the_dict):

    if (isJellyfinServer(var_dict['server_brand'])):
        parent_id=var_dict['this_whitelist_lib']['lib_id']
    else:
        if (('subfolder_id' in var_dict['this_whitelist_lib']) and (not (var_dict['this_whitelist_lib']['subfolder_id'] == None))):
            parent_id=var_dict['this_whitelist_lib']['subfolder_id']
        else:
            parent_id=var_dict['this_whitelist_lib']['lib_id']

    #Check if whitetag or whitelist are not an empty strings
    if ((not (var_dict['Whitetags_Parsed'] == '')) and
        var_dict['this_whitelist_lib']['lib_enabled'] and
        var_dict['enable_media_query_whitelisted_whitetagged']):

        #Built query for whitetagged from Whitelist media items
        url=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + parent_id + '&IncludeItemTypes=' + var_dict['IncludeItemTypes_Whitetagged_From_Whitelist'] +
        '&StartIndex=' + str(var_dict['StartIndex_Whitetagged_From_Whitelist']) + '&Limit=' + str(var_dict['QueryLimit_Whitetagged_From_Whitelist']) + '&Fields=' + var_dict['FieldsState_Whitetagged_From_Whitelist'] +
        '&Recursive=' + var_dict['Recursive_Whitetagged_From_Whitelist'] + '&SortBy=' + var_dict['SortBy_Whitetagged_From_Whitelist'] + '&SortOrder=' + var_dict['SortOrder_Whitetagged_From_Whitelist'] + '&EnableImages=' + var_dict['EnableImages_Whitetagged_From_Whitelist'] +
        '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Whitetagged_From_Whitelist'] + '&Tags=' + var_dict['Whitetags_Parsed'] + '&EnableUserData=' + var_dict['EnableUserData_Whitetagged_From_Whitelist'])

        var_dict['apiQuery_Whitetagged_From_Whitelist']=build_request_message(url,the_dict)

        #Send the API query for for whitetagged from Whitelist= media items
        var_dict=api_query_handler('Whitetagged_From_Whitelist',var_dict,the_dict)

        #Define reasoning for lookup
        var_dict['APIDebugMsg_Child_Of_Whitetagged_From_Whitelist']='Child_Of_Whitetagged_Item_From_Whitelist'
        var_dict['data_Child_Of_Whitetagged_From_Whitelist']=getChildren_taggedMediaItems('Whitetagged_From_Whitelist',user_info,var_dict,the_dict)

    else: #(var_dict['Whitetags_Parsed'] == '')
        var_dict['data_Whitetagged_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Whitetagged_From_Whitelist']=0
        var_dict['QueriesRemaining_Whitetagged_From_Whitelist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo whitetagged media items are whitelisted",2,the_dict)

        var_dict['data_Child_Of_Whitetagged_From_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Child_Of_Whitetagged_From_Whitelist']=0
        var_dict['QueriesRemaining_Child_Of_Whitetagged_From_Whitelist']=False

    var_dict['data_Whitetagged_From_Whitelist']['lib_id']=parent_id
    var_dict['data_Whitetagged_From_Whitelist']['path']=var_dict['this_whitelist_lib']['path']
    var_dict['data_Whitetagged_From_Whitelist']['network_path']=var_dict['this_whitelist_lib']['network_path']
    var_dict['data_Child_Of_Whitetagged_From_Whitelist']['lib_id']=parent_id
    var_dict['data_Child_Of_Whitetagged_From_Whitelist']['path']=var_dict['this_whitelist_lib']['path']
    var_dict['data_Child_Of_Whitetagged_From_Whitelist']['network_path']=var_dict['this_whitelist_lib']['network_path']

    return var_dict