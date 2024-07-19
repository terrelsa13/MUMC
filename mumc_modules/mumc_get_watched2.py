from mumc_modules.mumc_url import api_query_handler,build_request_message,api_query_handler2
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_played_created import get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue


def init_blacklist_watched_query2(user_info,var_dict,the_dict):
    #Initialize api_query_handler() variables for watched media items in blacklists
    var_dict[user_info['user_id']]['StartIndex_Blacklist']=0
    var_dict[user_info['user_id']]['TotalItems_Blacklist']=1
    var_dict[user_info['user_id']]['QueryLimit_Blacklist']=1
    var_dict[user_info['user_id']]['QueriesRemaining_Blacklist']=True
    var_dict[user_info['user_id']]['APIDebugMsg_Blacklist']=var_dict['media_type_lower'] + '_blacklist_media_items'

    if (var_dict['this_blacklist_lib']['lib_enabled'] and
        var_dict['enable_media_query_blacklisted_played']):
        #Build query for watched media items in blacklists
        var_dict[user_info['user_id']]['IncludeItemTypes_Blacklist']=var_dict['media_type_title']
        var_dict[user_info['user_id']]['FieldsState_Blacklist']='ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
        var_dict[user_info['user_id']]['SortBy_Blacklist']='ParentIndexNumber,IndexNumber,Name'
        var_dict[user_info['user_id']]['SortOrder_Blacklist']='Ascending'
        var_dict[user_info['user_id']]['EnableUserData_Blacklist']='True'
        var_dict[user_info['user_id']]['Recursive_Blacklist']='True'
        var_dict[user_info['user_id']]['EnableImages_Blacklist']='False'
        var_dict[user_info['user_id']]['CollapseBoxSetItems_Blacklist']='False'
        var_dict[user_info['user_id']]['IsPlayedState_Blacklist']=get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(the_dict,var_dict)

        if (isEmbyServer(var_dict['server_brand'])):
            var_dict[user_info['user_id']]['FieldsState_Blacklist']+=',UserDataPlayCount,UserDataLastPlayedDate'

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict[user_info['user_id']]['FieldsState_Blacklist']+=',SeriesStudio,seriesStatus'
            var_dict[user_info['user_id']]['SortBy_Blacklist']='SeriesSortName,' + var_dict[user_info['user_id']]['SortBy_Blacklist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict[user_info['user_id']]['FieldsState_Blacklist']+=',ArtistItems,AlbumId,AlbumArtist' 
            var_dict[user_info['user_id']]['SortBy_Blacklist']='Artists,PremiereDate,ProductionYear,Album,' + var_dict[user_info['user_id']]['SortBy_Blacklist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict[user_info['user_id']]['IncludeItemTypes_Blacklist']+=',audiobook,book'
            else:
                if (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict[user_info['user_id']]['IncludeItemTypes_Blacklist']=',book'

    return var_dict


def init_whitelist_watched_query2(user_info,var_dict,the_dict):
    #Initialize api_query_handler() variables for watched media items in whitelists
    var_dict[user_info['user_id']]['StartIndex_Whitelist']=0
    var_dict[user_info['user_id']]['TotalItems_Whitelist']=1
    var_dict[user_info['user_id']]['QueryLimit_Whitelist']=1
    var_dict[user_info['user_id']]['QueriesRemaining_Whitelist']=True
    var_dict[user_info['user_id']]['APIDebugMsg_Whitelist']=var_dict['media_type_lower'] + '_whitelist_media_items'

    if (var_dict['this_whitelist_lib']['lib_enabled'] and
        var_dict['enable_media_query_whitelist_played']):
        #Build query for watched media items in whitelists
        var_dict[user_info['user_id']]['IncludeItemTypes_Whitelist']=var_dict['media_type_title']
        var_dict[user_info['user_id']]['FieldsState_Whitelist']='ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
        var_dict[user_info['user_id']]['SortBy_Whitelist']='ParentIndexNumber,IndexNumber,Name'
        var_dict[user_info['user_id']]['SortOrder_Whitelist']='Ascending'
        var_dict[user_info['user_id']]['EnableUserData_Whitelist']='True'
        var_dict[user_info['user_id']]['Recursive_Whitelist']='True'
        var_dict[user_info['user_id']]['EnableImages_Whitelist']='False'
        var_dict[user_info['user_id']]['CollapseBoxSetItems_Whitelist']='False'
        var_dict[user_info['user_id']]['IsPlayedState_Whitelist']=get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(the_dict,var_dict)

        if (isEmbyServer(var_dict['server_brand'])):
            var_dict[user_info['user_id']]['FieldsState_Whitelist']+=',UserDataPlayCount,UserDataLastPlayedDate'

        if (var_dict['media_type_lower'] == 'episode'):
            var_dict[user_info['user_id']]['FieldsState_Whitelist']+=',SeriesStudio,seriesStatus'
            var_dict[user_info['user_id']]['SortBy_Whitelist']='SeriesSortName,' + var_dict[user_info['user_id']]['SortBy_Whitelist']

        if ((var_dict['media_type_lower'] == 'audio') or (var_dict['media_type_lower'] == 'audiobook')):
            var_dict[user_info['user_id']]['FieldsState_Whitelist']+=',ArtistItems,AlbumId,AlbumArtist'
            var_dict[user_info['user_id']]['SortBy_Whitelist']='Artist,PremiereDate,ProductionYear,Album,' + var_dict[user_info['user_id']]['SortBy_Whitelist']
            if (isEmbyServer(var_dict['server_brand'])):
                if (var_dict['media_type_lower'] == 'audio'):
                    var_dict[user_info['user_id']]['IncludeItemTypes_Whitelist']+=',AudioBook,Book'
            else:
                if (var_dict['media_type_lower'] == 'audiobook'):
                    var_dict[user_info['user_id']]['IncludeItemTypes_Whitelist']=',Book'

    return var_dict


def blacklist_watched_query2(user_info,var_dict,the_dict):

    if (isJellyfinServer(var_dict['server_brand'])):
        parent_id=var_dict['this_blacklist_lib']['lib_id']
    else:
        if (('subfolder_id' in var_dict['this_blacklist_lib']) and (not (var_dict['this_blacklist_lib']['subfolder_id'] == None))):
            parent_id=var_dict['this_blacklist_lib']['subfolder_id']
        else:
            parent_id=var_dict['this_blacklist_lib']['lib_id']

    if (var_dict['this_blacklist_lib']['lib_enabled'] and
        var_dict['enable_media_query_blacklisted_played']):

        #Built query for watched items in blacklists
        url=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + parent_id + '&IncludeItemTypes=' + var_dict[user_info['user_id']]['IncludeItemTypes_Blacklist'] +
        '&StartIndex=' + str(var_dict[user_info['user_id']]['StartIndex_Blacklist']) + '&Limit=' + str(var_dict[user_info['user_id']]['QueryLimit_Blacklist']) + '&IsPlayed=' + var_dict[user_info['user_id']]['IsPlayedState_Blacklist'] +
        '&Fields=' + var_dict[user_info['user_id']]['FieldsState_Blacklist'] + '&Recursive=' + var_dict[user_info['user_id']]['Recursive_Blacklist'] + '&SortBy=' + var_dict[user_info['user_id']]['SortBy_Blacklist'] + '&SortOrder=' + var_dict[user_info['user_id']]['SortOrder_Blacklist'] +
        '&EnableImages=' + var_dict[user_info['user_id']]['EnableImages_Blacklist'] + '&CollapseBoxSetItems=' + var_dict[user_info['user_id']]['CollapseBoxSetItems_Blacklist'] + '&EnableUserData=' + var_dict[user_info['user_id']]['EnableUserData_Blacklist'])

        var_dict[user_info['user_id']]['apiQuery_Blacklist']=build_request_message(url,the_dict)

        #Send the API query for for watched media items in blacklists
        var_dict[user_info['user_id']]=api_query_handler2('Blacklist',user_info['user_id'],var_dict,the_dict)
    else:
        #When no media items are blacklisted; simulate an empty query being returned
        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
        var_dict[user_info['user_id']]['data_Blacklist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict[user_info['user_id']]['QueryLimit_Blacklist']=0
        var_dict[user_info['user_id']]['QueriesRemaining_Blacklist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo watched media items are blacklisted",2,the_dict)

    var_dict[user_info['user_id']]['data_Blacklist']['lib_id']=parent_id
    var_dict[user_info['user_id']]['data_Blacklist']['path']=var_dict['this_blacklist_lib']['path']
    var_dict[user_info['user_id']]['data_Blacklist']['network_path']=var_dict['this_blacklist_lib']['network_path']

    return var_dict


def whitelist_watched_query2(user_info,var_dict,the_dict):

    if (isJellyfinServer(var_dict['server_brand'])):
        parent_id=var_dict['this_whitelist_lib']['lib_id']
    else:
        if (('subfolder_id' in var_dict['this_whitelist_lib']) and (not (var_dict['this_whitelist_lib']['subfolder_id'] == None))):
            parent_id=var_dict['this_whitelist_lib']['subfolder_id']
        else:
            parent_id=var_dict['this_whitelist_lib']['lib_id']

    if (var_dict['this_whitelist_lib']['lib_enabled'] and
        var_dict['enable_media_query_whitelist_played']):

        #Built query for watched items in whitelists
        url=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + parent_id + '&IncludeItemTypes=' + var_dict[user_info['user_id']]['IncludeItemTypes_Whitelist'] +
        '&StartIndex=' + str(var_dict[user_info['user_id']]['StartIndex_Whitelist']) + '&Limit=' + str(var_dict[user_info['user_id']]['QueryLimit_Whitelist']) + '&IsPlayed=' + var_dict[user_info['user_id']]['IsPlayedState_Whitelist'] +
        '&Fields=' + var_dict[user_info['user_id']]['FieldsState_Whitelist'] + '&Recursive=' + var_dict[user_info['user_id']]['Recursive_Whitelist'] + '&SortBy=' + var_dict[user_info['user_id']]['SortBy_Whitelist'] + '&SortOrder=' + var_dict[user_info['user_id']]['SortOrder_Whitelist'] +
        '&EnableImages=' + var_dict[user_info['user_id']]['EnableImages_Whitelist'] + '&CollapseBoxSetItems=' + var_dict[user_info['user_id']]['CollapseBoxSetItems_Whitelist'] + '&EnableUserData=' + var_dict[user_info['user_id']]['EnableUserData_Whitelist'])

        var_dict[user_info['user_id']]['apiQuery_Whitelist']=build_request_message(url,the_dict)

        #Send the API query for for watched media items in whitelists
        var_dict[user_info['user_id']]=api_query_handler2('Whitelist',user_info['user_id'],var_dict,the_dict)
    else:
        #When no media items are whitelisted; simulate an empty query being returned
        #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
        var_dict[user_info['user_id']]['data_Whitelist']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict[user_info['user_id']]['QueryLimit_Whitelist']=0
        var_dict[user_info['user_id']]['QueriesRemaining_Whitelist']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nNo watched media items are whitelisted",2,the_dict)

    var_dict[user_info['user_id']]['data_Whitelist']['lib_id']=parent_id
    var_dict[user_info['user_id']]['data_Whitelist']['path']=var_dict['this_whitelist_lib']['path']
    var_dict[user_info['user_id']]['data_Whitelist']['network_path']=var_dict['this_whitelist_lib']['network_path']

    return var_dict