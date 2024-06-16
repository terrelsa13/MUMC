from mumc_modules.mumc_url import api_query_handler,build_request_message
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_library_queries import get_all_library_subfolders
from mumc_modules.mumc_paths import save_yaml_config
from mumc_modules.mumc_versions import get_script_version,get_semantic_version_parts


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



def add_subfolder_id_placeholders(list_type,the_dict):
    for user_info in the_dict['admin_settings']['users']:
        user_index=the_dict['admin_settings']['users'].index(user_info)
        for lib_info in user_info[list_type]:
            lib_index=user_info[list_type].index(lib_info)
            if (not ('subfolder_id' in lib_info)):
                the_dict['admin_settings']['users'][user_index][list_type][lib_index]['subfolder_id']=None

    return the_dict


def populate_config_with_subfolder_ids(cfg,init_dict):

    #check if version number in mumc_config.yaml is < 5.8.18
    config_version_dict=get_semantic_version_parts(cfg['version'])
    get_subfolder_ids=False
    if (int(config_version_dict['major']) <= 5):
        if (int(config_version_dict['minor']) <= 8):
            if (int(config_version_dict['patch']) < 18):
                get_subfolder_ids=True

    #check if version number in mumc_config.yaml is < 5.8.18
    if (get_subfolder_ids):
        #add subfolder_ids
        #loop thru users
        for user_data in cfg['admin_settings']['users']:
            #loop thru user's dict keys
            for user_list_data in user_data:
                #check if key is blacklist or whitelist
                if ((user_list_data == 'blacklist') or (user_list_data == 'whitelist')):
                    #loop thru user's blacklist or whitelist libraries
                    for user_lib_entry_data in user_data[user_list_data]:
                        #check if Emby
                        if (isEmbyServer(cfg['admin_settings']['server']['brand'])):
                            #get subfolder data for all libraries
                            library_subfolders=get_all_library_subfolders(cfg|init_dict)
                            #loop thru libraries from query
                            for sub_lib_data in library_subfolders:
                                #check if uesr's library_id and query's library_id match
                                if (sub_lib_data['Guid'] == user_lib_entry_data['lib_id']):
                                    #loop thru subfolders of matching library
                                    for subfolder_data in sub_lib_data['SubFolders']:
                                        #check if path exists in user's library data
                                        if ('path' in user_lib_entry_data):
                                            #check if user's library path matches subfolder's library path
                                            if (subfolder_data['Path'] == user_lib_entry_data['path']):
                                                #save subfolder_id
                                                user_lib_entry_data['subfolder_id']=subfolder_data['Id']
                                                break
                                        else:
                                            #path and network path do not exist
                                            user_lib_entry_data['subfolder_id']=None
                                            break
                        else:
                            user_lib_entry_data['subfolder_id']=None

        cfg['version']=get_script_version()

        save_yaml_config(cfg,init_dict['mumc_path'] / init_dict['config_file_name_yaml'])

    return cfg