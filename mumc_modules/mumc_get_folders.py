from mumc_modules.mumc_url import api_query_handler,build_request_message
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_server_type import isJellyfinServer


def init_empty_folder_query(var_dict):
    #Initialize api_query_handler() variables for blacktagged from blacklist media items
    var_dict['StartIndex_Empty_Folder']=0
    var_dict['TotalItems_Empty_Folder']=1
    var_dict['QueryLimit_Empty_Folder']=1
    var_dict['QueriesRemaining_Empty_Folder']=True
    var_dict['APIDebugMsg_Empty_Folder']='Empty_' + var_dict['media_type_lower'] + '_Folder_media_items'

    if (var_dict['advanced_settings']['delete_empty_folders']['episode'][var_dict['media_type_lower']]):
        #Build query for folders
        var_dict['IncludeItemTypes_Empty_Folder']=var_dict['media_type_title']
        var_dict['SortOrder_Empty_Folder']='Ascending'
        var_dict['EnableUserData_Empty_Folder']='True'
        var_dict['Recursive_Empty_Folder']='True'
        var_dict['EnableImages_Empty_Folder']='False'
        var_dict['CollapseBoxSetItems_Empty_Folder']='False'
        var_dict['IsFolder']='True'

        if (var_dict['media_type_lower'] == 'season'):
            
            var_dict['FieldsState_Empty_Folder']='ChildCount,ParentId,SeriesId,SeriesName'
            
            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Empty_Folder']='SeriesSortName,IndexNumber'
            else:
                var_dict['SortBy_Empty_Folder']='SeriesName,IndexNumber'
        elif (var_dict['media_type_lower'] == 'series'):

            var_dict['FieldsState_Empty_Folder']='ChildCount,ParentId'

            if (isJellyfinServer(var_dict['server_brand'])):
                var_dict['SortBy_Empty_Folder']='SortName'
            else:
                var_dict['SortBy_Empty_Folder']='Name'

    return var_dict


def empty_folder_query(user_info,var_dict,the_dict):
    #Check if blacktag or blacklist are not an empty strings
    if (var_dict['advanced_settings']['delete_empty_folders']['episode'][var_dict['media_type_lower']]):

        url=(var_dict['server_url'] + '/Users/' + user_info['user_id']  + '/Items?IncludeItemTypes=' + var_dict['IncludeItemTypes_Empty_Folder'] + '&ParentId&IsFolder=' + var_dict['IsFolder'] +
        '&StartIndex=' + str(var_dict['StartIndex_Empty_Folder']) + '&Limit=' + str(var_dict['QueryLimit_Empty_Folder']) + '&Fields=' + var_dict['FieldsState_Empty_Folder'] + '&Recursive=' +
        var_dict['Recursive_Empty_Folder'] + '&SortBy=' + var_dict['SortBy_Empty_Folder'] + '&SortOrder=' + var_dict['SortOrder_Empty_Folder'] + '&EnableImages=' +
        var_dict['EnableImages_Empty_Folder'] + '&CollapseBoxSetItems=' + var_dict['CollapseBoxSetItems_Empty_Folder'] + '&EnableUserData=' + var_dict['EnableUserData_Empty_Folder'])

        var_dict['apiQuery_Empty_Folder']=build_request_message(url,the_dict)

        #Send the API query for for blacktagged from blacklist media items
        var_dict=api_query_handler('Empty_Folder',var_dict,the_dict)

    else: #(not (var_dict['advanced_settings']['delete_empty_folders']['episode'][var_dict['media_type_lower']]))
        var_dict['data_Empty_Folder']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
        var_dict['QueryLimit_Empty_Folder']=0
        var_dict['QueriesRemaining_Empty_Folder']=False
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n\nDelete empty " + var_dict['media_type_title'] + " folders disabled",2,the_dict)

    return var_dict