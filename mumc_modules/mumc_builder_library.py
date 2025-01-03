import copy
import uuid
from mumc_modules.mumc_compare_items import keys_exist
from mumc_modules.mumc_server_type import isJellyfinServer


def create_library_dicts(the_dict):

    temp_lib_dict={}
    the_dict['all_libraries_list']=[]
    the_dict['all_library_ids_list']=[]
    the_dict['all_library_paths_list']=[]
    the_dict['all_library_network_paths_list']=[]
    the_dict['all_library_collection_types_list']=[]
    the_dict['all_library_path_ids_list']=[]

    #Emby and Jellyfin use different key-names for their libraryId
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        libraryGuid='ItemId'
    else:
        libraryGuid='Guid'

    for lib in the_dict['all_libraries']:
        libpos=the_dict['all_libraries'].index(lib)

        for pathinfo in lib['LibraryOptions']['PathInfos']:
            pathpos=lib['LibraryOptions']['PathInfos'].index(pathinfo)

            if (not (((lib['Name'] == 'Recordings') and (lib['LibraryOptions']['PathInfos'][pathpos]['Path'].endswith('recordings'))) or
                     ((lib['Name'] == 'Collections') and (lib['CollectionType'] == 'boxsets')))):

                temp_lib_dict['lib_id']=the_dict['all_libraries'][libpos][libraryGuid]
                if (('CollectionType' in lib) and
                    (not (lib['CollectionType'] == ''))):
                    temp_lib_dict['collection_type']=lib['CollectionType']
                else:
                    temp_lib_dict['collection_type']=None
                if (('Path' in lib['LibraryOptions']['PathInfos'][pathpos]) and
                    (not (lib['LibraryOptions']['PathInfos'][pathpos]['Path'] == ''))):
                    temp_lib_dict['path']=lib['LibraryOptions']['PathInfos'][pathpos]['Path']
                else:
                    temp_lib_dict['path']=None
                if (('NetworkPath' in lib['LibraryOptions']['PathInfos'][pathpos]) and
                    (not (lib['LibraryOptions']['PathInfos'][pathpos]['NetworkPath'] == ''))):
                    temp_lib_dict['network_path']=lib['LibraryOptions']['PathInfos'][pathpos]['NetworkPath']
                else:
                    temp_lib_dict['network_path']=None

                
                if (not (isJellyfinServer(the_dict['admin_settings']['server']['brand']))):
                    for lib_info in the_dict['all_library_subfolders']:
                        for subfolder_info in lib_info['SubFolders']:
                            if (subfolder_info['Path'] == temp_lib_dict['path']):
                                temp_lib_dict['subfolder_id']=subfolder_info['Id']
                                break
                else:
                    temp_lib_dict['subfolder_id']=None
                

                temp_lib_dict['lib_enabled']=True

                the_dict['all_libraries_list'].append(copy.deepcopy(temp_lib_dict))
                the_dict['all_library_ids_list'].append(temp_lib_dict['lib_id'])
                the_dict['all_library_paths_list'].append(temp_lib_dict['path'])
                the_dict['all_library_network_paths_list'].append(temp_lib_dict['network_path'])
                the_dict['all_library_collection_types_list'].append(temp_lib_dict['collection_type'])
                the_dict['all_library_path_ids_list'].append(temp_lib_dict['subfolder_id'])

    the_dict.pop('all_libraries')
    
    return the_dict


def reorder_user_policy_libararies(the_dict):
    for user_data in the_dict['all_users']:
        user_data_pos=the_dict['all_users'].index(user_data)
        if (not (user_data['Policy']['EnableAllFolders'])):
            sorted_lib_id_list=[]
            temp_lib_data=user_data['Policy']['EnabledFolders'].copy()
            for sort_item in the_dict['all_library_ids_list']:
                if (sort_item in temp_lib_data):
                    sort_item_pos=temp_lib_data.index(sort_item)
                    if (not (sort_item in sorted_lib_id_list)):
                        sorted_lib_id_list.append(sort_item)
                    temp_lib_data[sort_item_pos]=None
            the_dict['all_users'][user_data_pos]['Policy']['EnabledFolders']=sorted_lib_id_list

    return the_dict


def create_library_path_id_dicts(the_dict):

    guid_list=[]
    the_dict['all_library_path_ids_list']=[]

    for path_str in the_dict['all_library_paths_list']:
        path_found=False
        for lib_data in the_dict['all_library_subfolders']:
            if (not (path_found)):
                for folder_data in lib_data['SubFolders']:
                    if (folder_data['Path'] == path_str):
                        if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
                            #generate guid
                            folder_data['Id']=str(uuid.uuid4().hex)
                            #check if we have already generated this guid for a subfolder
                            while (folder_data['Id'] in guid_list):
                                #if we have; create a new guid and check again
                                folder_data['Id']=str(uuid.uuid4().hex)
                        the_dict['all_library_path_ids_list'].append(folder_data['Id'])
                        path_found=True
                        break
            else:
                break
        if (not (path_found)):
            the_dict['all_library_path_ids_list'].append(None)

    the_dict.pop('all_library_subfolders')

    return the_dict


def update_users_with_path_ids(the_dict):
    for user_data in the_dict['admin_settings']['users']:
        user_index=the_dict['admin_settings']['users'].index(user_data)
        for lib_data in user_data[the_dict['matching_listing_type']]:
            lib_index=user_data[the_dict['matching_listing_type']].index(lib_data)
            if (lib_data['subfolder_id'] == None):
                if (lib_data['path'] in the_dict['all_library_paths_list']):
                    path_index=the_dict['all_library_paths_list'].index(lib_data['path'])
                    the_dict['admin_settings']['users'][user_index][the_dict['matching_listing_type']][lib_index]['subfolder_id']=the_dict['all_library_path_ids_list'][path_index]
                    the_dict['all_users_dict'][user_index][the_dict['matching_listing_type']][lib_index]['subfolder_id']=the_dict['all_library_path_ids_list'][path_index]
                    if (not (the_dict['prev_users_dict'][user_index] == None)):
                        the_dict['prev_users_dict'][user_index][the_dict['matching_listing_type']][lib_index]['subfolder_id']=the_dict['all_library_path_ids_list'][path_index]
        for lib_data in user_data[the_dict['opposing_listing_type']]:
            lib_index=user_data[the_dict['opposing_listing_type']].index(lib_data)
            if (lib_data['subfolder_id'] == None):
                if (lib_data['path'] in the_dict['all_library_paths_list']):
                    path_index=the_dict['all_library_paths_list'].index(lib_data['path'])
                    the_dict['admin_settings']['users'][user_index][the_dict['opposing_listing_type']][lib_index]['subfolder_id']=the_dict['all_library_path_ids_list'][path_index]
                    the_dict['all_users_dict'][user_index][the_dict['opposing_listing_type']][lib_index]['subfolder_id']=the_dict['all_library_path_ids_list'][path_index]
                    if (not (the_dict['prev_users_dict'][user_index] == None)):
                        the_dict['prev_users_dict'][user_index][the_dict['opposing_listing_type']][lib_index]['subfolder_id']=the_dict['all_library_path_ids_list'][path_index]

    return the_dict


def update_existing_user_libraries(the_dict):

    for prev_user in the_dict['prev_users_dict']:
        if (not(prev_user == None)):
            prev_user_index=the_dict['prev_users_dict'].index(prev_user)
            for lib_info in prev_user[the_dict['matching_listing_type']]:
                list_index=prev_user[the_dict['matching_listing_type']].index(lib_info)
                for lib_id_index in range(len(the_dict['all_library_ids_list'])):
                    if ((lib_info['lib_id'] == the_dict['all_library_ids_list'][lib_id_index]) and (lib_info['path'] == the_dict['all_library_paths_list'][lib_id_index])):
                        the_dict['prev_users_dict'][prev_user_index][the_dict['matching_listing_type']][list_index]['network_path']=the_dict['all_library_network_paths_list'][lib_id_index]
                        the_dict['prev_users_dict'][prev_user_index][the_dict['matching_listing_type']][list_index]['collection_type']=the_dict['all_library_collection_types_list'][lib_id_index]
                        break
            for lib_info in prev_user[the_dict['opposing_listing_type']]:
                list_index=prev_user[the_dict['opposing_listing_type']].index(lib_info)
                for lib_id_index in range(len(the_dict['all_library_ids_list'])):
                    if ((lib_info['lib_id'] == the_dict['all_library_ids_list'][lib_id_index]) and (lib_info['path'] == the_dict['all_library_paths_list'][lib_id_index])):
                        the_dict['prev_users_dict'][prev_user_index][the_dict['opposing_listing_type']][list_index]['network_path']=the_dict['all_library_network_paths_list'][lib_id_index]
                        the_dict['prev_users_dict'][prev_user_index][the_dict['opposing_listing_type']][list_index]['collection_type']=the_dict['all_library_collection_types_list'][lib_id_index]
                        break

    for user_pos in range(len(the_dict['prev_users_dict'])):
        if (not (the_dict['prev_users_dict'][user_pos] == None)):
            the_dict['all_users_dict'][user_pos]=copy.deepcopy(the_dict['prev_users_dict'][user_pos])

    return the_dict


def remove_libraries_from_existing_users(the_dict):

    for existing_user in the_dict['prev_users_dict']:
        if (not(existing_user == None)):
            enabled_lib_id_list=[]
            if (the_dict['all_users'][the_dict['prev_users_dict'].index(existing_user)]['Policy']['EnableAllFolders']):
                enabled_lib_id_list=the_dict['all_library_ids_list']
            else:
                for enabled_lib_id in the_dict['all_users'][the_dict['prev_users_dict'].index(existing_user)]['Policy']['EnabledFolders']:
                    enabled_lib_id_list.append(enabled_lib_id)

            for lib_id in enabled_lib_id_list:
                if (not (lib_id in the_dict['library_ids_per_user'][existing_user['user_id']])):
                    the_dict['library_ids_per_user'][existing_user['user_id']].append(lib_id)

            for lib_info in the_dict['prev_users_dict'][the_dict['prev_users_dict'].index(existing_user)][the_dict['opposing_listing_type']]:
                if (not (lib_info['lib_id'] in enabled_lib_id_list)):
                    the_dict['all_users_dict'][the_dict['prev_users_dict'].index(existing_user)][the_dict['opposing_listing_type']].remove(lib_info)
            for lib_info in the_dict['prev_users_dict'][the_dict['prev_users_dict'].index(existing_user)][the_dict['matching_listing_type']]:
                if (not (lib_info['lib_id'] in enabled_lib_id_list)):
                    the_dict['all_users_dict'][the_dict['prev_users_dict'].index(existing_user)][the_dict['matching_listing_type']].remove(lib_info)

    for user_pos in range(len(the_dict['prev_users_dict'])):
        if (not (the_dict['prev_users_dict'][user_pos] == None)):
            the_dict['prev_users_dict'][user_pos]=copy.deepcopy(the_dict['all_users_dict'][user_pos])

    return the_dict


#subfolder ids can be updated by doing the following:
# Emby > Manage Server > Users > Select User > Select Access > Save
# Repeat this for each user or the users with non-aligned folder ids
def remove_subfolders_from_existing_users(the_dict):

    temp_the_dict={}
    temp_the_dict['prev_users_dict']=copy.deepcopy(the_dict['prev_users_dict'])

    prev_users_dict_len=0
    for prev_users_dict_data in temp_the_dict['prev_users_dict']:
        if (not(prev_users_dict_data == None)):
            prev_users_dict_len+=1

    for user_data in the_dict['all_users']:
        user_index=the_dict['all_users'].index(user_data)
        if (user_index < prev_users_dict_len):
            for path_id in the_dict['all_library_path_ids_list']:
                if (not (path_id == None)):
                    path_index=the_dict['all_library_path_ids_list'].index(path_id)
                    built_path=str(the_dict['all_library_ids_list'][path_index]) + '_' + str(path_id)
                    if (built_path in user_data['Policy']['ExcludedSubFolders']):
                        remove_path=the_dict['all_library_paths_list'][path_index]
                        remove_network_path=the_dict['all_library_network_paths_list'][path_index]

                        for lib_info in the_dict['prev_users_dict'][user_index][the_dict['opposing_listing_type']]:
                            lib_index=temp_the_dict['prev_users_dict'][user_index][the_dict['opposing_listing_type']].index(lib_info)
                            if ((lib_info['path'] == remove_path) or (lib_info['network_path'] == remove_network_path)):
                                temp_the_dict['prev_users_dict'][user_index][the_dict['opposing_listing_type']].pop(lib_index)

                        for lib_info in the_dict['prev_users_dict'][user_index][the_dict['matching_listing_type']]:
                            lib_index=temp_the_dict['prev_users_dict'][user_index][the_dict['matching_listing_type']].index(lib_info)
                            if ((lib_info['path'] == remove_path) or (lib_info['network_path'] == remove_network_path)):
                                temp_the_dict['prev_users_dict'][user_index][the_dict['matching_listing_type']].pop(lib_index)
        else:
            break

    the_dict['prev_users_dict']=temp_the_dict['prev_users_dict']
    for user_pos in range(len(the_dict['prev_users_dict'])):
        if (not (the_dict['prev_users_dict'][user_pos] == None)):
            the_dict['all_users_dict'][user_pos]=temp_the_dict['prev_users_dict'][user_pos]

    return the_dict


def remove_nonexisting_subfolders_from_existing_users(the_dict):
    temp_the_dict={}
    temp_the_dict['all_users_dict']=copy.deepcopy(the_dict['all_users_dict'])
    temp_the_dict['prev_users_dict']=copy.deepcopy(the_dict['prev_users_dict'])

    for user_info in the_dict['prev_users_dict']:
        if (not (user_info == None)):
            user_index=the_dict['prev_users_dict'].index(user_info)
            temp_the_dict['all_users_dict'][user_index][the_dict['opposing_listing_type']].clear()
            temp_the_dict['all_users_dict'][user_index][the_dict['matching_listing_type']].clear()
            temp_the_dict['prev_users_dict'][user_index][the_dict['opposing_listing_type']].clear()
            temp_the_dict['prev_users_dict'][user_index][the_dict['matching_listing_type']].clear()

            for lib_info in user_info[the_dict['opposing_listing_type']]:
                folder_index=-1
                if (lib_info['path'] in the_dict['all_library_paths_list']):
                    folder_index=the_dict['all_library_paths_list'].index(lib_info['path'])

                if (folder_index >= 0):
                    if ((lib_info['path'] == the_dict['all_library_paths_list'][folder_index]) and
                        (lib_info['network_path'] == the_dict['all_library_network_paths_list'][folder_index]) and
                        (lib_info['collection_type'] == the_dict['all_library_collection_types_list'][folder_index])):
                        temp_the_dict['all_users_dict'][user_index][the_dict['opposing_listing_type']].append(lib_info)
                        temp_the_dict['prev_users_dict'][user_index][the_dict['opposing_listing_type']].append(lib_info)

            for lib_info in user_info[the_dict['matching_listing_type']]:
                folder_index=-1
                if (lib_info['path'] in the_dict['all_library_paths_list']):
                    folder_index=the_dict['all_library_paths_list'].index(lib_info['path'])

                if (folder_index >= 0):
                    if ((lib_info['path'] == the_dict['all_library_paths_list'][folder_index]) and
                        (lib_info['network_path'] == the_dict['all_library_network_paths_list'][folder_index]) and
                        (lib_info['collection_type'] == the_dict['all_library_collection_types_list'][folder_index])):
                        temp_the_dict['all_users_dict'][user_index][the_dict['matching_listing_type']].append(lib_info)
                        temp_the_dict['prev_users_dict'][user_index][the_dict['matching_listing_type']].append(lib_info)

    the_dict['all_users_dict']=temp_the_dict['all_users_dict']
    the_dict['prev_users_dict']=temp_the_dict['prev_users_dict']

    return the_dict


def add_libraries_to_existing_users(the_dict):

    for existing_user in the_dict['prev_users_dict']:
        if (not(existing_user == None)):
            enabled_lib_id_list=[]
            if (the_dict['all_users'][the_dict['prev_users_dict'].index(existing_user)]['Policy']['EnableAllFolders']):
                enabled_lib_id_list=the_dict['all_library_ids_list']
            else:
                for enabled_lib_id in the_dict['all_users'][the_dict['prev_users_dict'].index(existing_user)]['Policy']['EnabledFolders']:
                    enabled_lib_id_list.append(enabled_lib_id)

            for lib_id in enabled_lib_id_list:
                if (not (lib_id in the_dict['library_ids_per_user'][existing_user['user_id']])):
                    the_dict['library_ids_per_user'][existing_user['user_id']].append(lib_id)

            existing_lib_info_list=[]
            existing_lib_id_list=[]
            for lib_info in the_dict['prev_users_dict'][the_dict['prev_users_dict'].index(existing_user)][the_dict['opposing_listing_type']]:
                existing_lib_info_list.append(lib_info)
                existing_lib_id_list.append(lib_info['lib_id'])
            for lib_info in the_dict['prev_users_dict'][the_dict['prev_users_dict'].index(existing_user)][the_dict['matching_listing_type']]:
                existing_lib_info_list.append(lib_info)
                existing_lib_id_list.append(lib_info['lib_id'])

            for enabled_lib_id in enabled_lib_id_list:
                if (not (enabled_lib_id in existing_lib_id_list)):
                    for all_lib_id_pos in range(len(the_dict['all_library_ids_list'])):
                        if (the_dict['all_library_ids_list'][all_lib_id_pos] == enabled_lib_id):
                            the_dict['all_users_dict'][the_dict['prev_users_dict'].index(existing_user)][the_dict['opposing_listing_type']].append(the_dict['all_libraries_list'][all_lib_id_pos])
                else:
                    for existing_lib_id in existing_lib_id_list:
                        exisiting_lib_id_index=existing_lib_id_list.index(existing_lib_id)
                        for all_lib_pos in range(len(the_dict['all_library_ids_list'])):
                            if (existing_lib_id == the_dict['all_library_ids_list'][all_lib_pos]):
                                #remove "lib_enabled" before comparison
                                #"lib_enabled" is expected to be manually changed in the config and therefore should be ignored for the comparison
                                all_libraries_list_lib_enabled=the_dict['all_libraries_list'][all_lib_pos].pop('lib_enabled',None)
                                existing_lib_info_list_lib_enabled=existing_lib_info_list[exisiting_lib_id_index].pop('lib_enabled',None)

                                libraries_match=True
                                if (not (the_dict['all_libraries_list'][all_lib_pos] == existing_lib_info_list[exisiting_lib_id_index])):
                                    libraries_match=False

                                #re-add "lib_enabled" after comparison
                                if (not (all_libraries_list_lib_enabled == None)):
                                    the_dict['all_libraries_list'][all_lib_pos]['lib_enabled']=all_libraries_list_lib_enabled
                                if (not (existing_lib_info_list_lib_enabled == None)):
                                    existing_lib_info_list[exisiting_lib_id_index]['lib_enabled']=existing_lib_info_list_lib_enabled

                                #if libraries do not match; add the "new" library for this user
                                if (not (libraries_match)):
                                    the_dict['all_users_dict'][the_dict['prev_users_dict'].index(existing_user)][the_dict['opposing_listing_type']].append(the_dict['all_libraries_list'][all_lib_pos])
                                    existing_lib_info_list.append(the_dict['all_libraries_list'][all_lib_pos])
                                    existing_lib_id_list.append(the_dict['all_library_ids_list'][all_lib_pos])

    for user_pos in range(len(the_dict['prev_users_dict'])):
        if (not (the_dict['prev_users_dict'][user_pos] == None)):
            the_dict['prev_users_dict'][user_pos]=copy.deepcopy(the_dict['all_users_dict'][user_pos])

    return the_dict


def add_libraries_to_new_users(the_dict):

    temp_the_dict={}
    temp_the_dict['all_users_dict']=copy.deepcopy(the_dict['all_users_dict'])
    

    for existing_user in the_dict['all_users_dict']:
        existing_user_index=the_dict['all_users_dict'].index(existing_user)
        if (existing_user in the_dict['prev_users_dict']):
            temp_the_dict['all_users_dict'][existing_user_index]=None

    for this_user in temp_the_dict['all_users_dict']:
        this_user_index=temp_the_dict['all_users_dict'].index(this_user)
        enabled_lib_id_list=[]
        if (not (this_user == None)):
            if (the_dict['all_users'][this_user_index]['Policy']['EnableAllFolders']):
                enabled_lib_id_list=the_dict['all_library_ids_list']
            else:
                for enabled_lib_id in the_dict['all_users'][this_user_index]['Policy']['EnabledFolders']:
                    for x in range(the_dict['all_library_ids_list'].count(enabled_lib_id)):
                        enabled_lib_id_list.append(enabled_lib_id)
                        x=x

            for lib_id in enabled_lib_id_list:
                if (not (lib_id in the_dict['library_ids_per_user'][this_user['user_id']])):
                    the_dict['library_ids_per_user'][this_user['user_id']].append(lib_id)

            temp_the_dict['all_library_ids_list']=copy.deepcopy(the_dict['all_library_ids_list'])
            for lib_id in enabled_lib_id_list:
                lib_index=temp_the_dict['all_library_ids_list'].index(lib_id)
                temp_the_dict['all_users_dict'][this_user_index][the_dict['opposing_listing_type']].append(the_dict['all_libraries_list'][lib_index])
                if (not (lib_id in the_dict['library_ids_per_user'][this_user['user_id']])):
                    the_dict['library_ids_per_user'][this_user['user_id']].append(lib_id)
                temp_the_dict['all_library_ids_list'][lib_index]=None

    for user_pos in range(len(the_dict['all_users_dict'])):
        if (not (temp_the_dict['all_users_dict'][user_pos] == None)):
            the_dict['all_users_dict'][user_pos]=temp_the_dict['all_users_dict'][user_pos]

    return the_dict


def add_selection_and_selected_keys(the_dict):

    temp_the_dict={}
    temp_the_dict['all_users_dict']=copy.deepcopy(the_dict['all_users_dict'])
    temp_the_dict['prev_users_dict']=copy.deepcopy(the_dict['prev_users_dict'])

    prev_users_dict_len=0
    for prev_users_dict_data in temp_the_dict['prev_users_dict']:
        if (not(prev_users_dict_data == None)):
            prev_users_dict_len+=1

    for user_info in temp_the_dict['all_users_dict']:
        user_index=temp_the_dict['all_users_dict'].index(user_info)
        for list_info in user_info[the_dict['opposing_listing_type']]:
            lib_list_index=user_info[the_dict['opposing_listing_type']].index(list_info)
            temp_the_dict['all_users_dict'][user_index][the_dict['opposing_listing_type']][lib_list_index]['selection']=None
            temp_the_dict['all_users_dict'][user_index][the_dict['opposing_listing_type']][lib_list_index]['selected']=False

            if (user_index < prev_users_dict_len):
                temp_the_dict['prev_users_dict'][user_index][the_dict['opposing_listing_type']][lib_list_index]['selection']=None
                temp_the_dict['prev_users_dict'][user_index][the_dict['opposing_listing_type']][lib_list_index]['selected']=False

        for list_info in user_info[the_dict['matching_listing_type']]:
            lib_list_index=user_info[the_dict['matching_listing_type']].index(list_info)
            temp_the_dict['all_users_dict'][user_index][the_dict['matching_listing_type']][lib_list_index]['selection']=None
            temp_the_dict['all_users_dict'][user_index][the_dict['matching_listing_type']][lib_list_index]['selected']=True

            if (user_index < prev_users_dict_len):
                temp_the_dict['prev_users_dict'][user_index][the_dict['matching_listing_type']][lib_list_index]['selection']=None
                temp_the_dict['prev_users_dict'][user_index][the_dict['matching_listing_type']][lib_list_index]['selected']=True

    the_dict['all_users_dict']=temp_the_dict['all_users_dict']
    the_dict['prev_users_dict']=temp_the_dict['prev_users_dict']

    return the_dict


def get_library_selections(the_dict):
    #Wait for user input telling us which library they are have selected
    print('Select one or more libraries.')
    print('Unselect a library by selecting it again.')
    print('*Use a comma or space to separate multiple selections.')
    the_dict['selected_libraries_str']=input('Leave blank when finished: ')
    print('')

    return the_dict


def select_all_unselected_libraries(the_dict):
    the_dict['selected_libraries_str']=''

    for lib_data in the_dict['library_info_print_all_list']:
        if (lib_data in the_dict['library_info_print_opposing_list']):
            the_dict['selected_libraries_str']+=str(the_dict['library_info_print_all_list'].index(lib_data)) + ','

    return the_dict


def is_valid_library_selected(the_dict):
    print_error=''
    the_dict['library_selection_list']=[]

    #replace spaces with commas (assuming people will use spaces because the space bar is bigger and easier to push)
    the_dict['comma_selected_libraries_str']=the_dict['selected_libraries_str'].replace(' ',',')
    #convert string to list
    the_dict['selected_libraries_list_of_strs']=the_dict['comma_selected_libraries_str'].split(',')
    #remove blanks
    while ('' in the_dict['selected_libraries_list_of_strs']):
        the_dict['selected_libraries_list_of_strs'].remove('')

    #remove duplicate strings
    the_dict['selected_libraries_list_of_strs']=list(set(the_dict['selected_libraries_list_of_strs']))
    the_dict['selected_libraries_list_of_strs'].sort()

    try:
        if (the_dict['selected_libraries_list_of_strs']):
            for selected_library_str in the_dict['selected_libraries_list_of_strs']:
                #We get here to allow selecting libraries for the specified library
                the_dict['library_selection_float']=float(selected_library_str)
                if ((the_dict['library_selection_float'] % 1) == 0):
                    the_dict['library_selection_int']=int(the_dict['library_selection_float'])
                else:
                    the_dict['library_selection_int']=None
                    print_error+='Invalid value. Try again.\n'

                if (not (the_dict['library_selection_int'] == None)):
                    if ((the_dict['library_selection_int'] >= 0) and (the_dict['library_selection_int'] < len(the_dict['library_info_print_all_list']))):
                        the_dict['library_selection_list'].append(the_dict['library_selection_int'])
                        the_dict['library_valid_selection']=True
                    else:
                        print_error+='Value Out Of Range. Try again.\n'

        else:
            if (not (the_dict['user_library_selection_type'] == 2)):
                the_dict['library_stop_loop']=True
            else: #(the_dict['user_library_selection_type'] == 2):
                the_dict['user_stop_loop']=True
    except:
        print_error+='Error When Selecting library. Try again.\n'

    if (not (print_error == '')):
        print(str(selected_library_str) + ' - ' + str(print_error) + '\n')
        the_dict['library_valid_selection']=False
    else:
        #remove duplicate integers and sort
        the_dict['library_selection_list']=list(set(the_dict['library_selection_list']))
        the_dict['library_selection_list'].sort()

    return the_dict


def autoselect_subfolders_with_same_library_id(the_dict):

    temp_the_dict={}
    temp_the_dict['all_library_ids_list']=copy.deepcopy(the_dict['all_library_ids_list'])
    temp_the_dict['library_selection_list']=copy.deepcopy(the_dict['library_selection_list'])

    for selected_library_int in the_dict['library_selection_list']:
        base_lib_id=the_dict['all_library_ids_list'][selected_library_int]
        temp_the_dict['all_library_ids_list'][selected_library_int]=None
        if (base_lib_id in temp_the_dict['all_library_ids_list']):
            lib_id_index=temp_the_dict['all_library_ids_list'].index(base_lib_id)
            if (not (lib_id_index in temp_the_dict['library_selection_list'])):
                temp_the_dict['library_selection_list'].append(lib_id_index)

    the_dict['library_selection_list']=temp_the_dict['library_selection_list']
    the_dict['library_selection_list'].sort()
 
    return the_dict



def reorder_libraries_before_printing(the_dict):
    the_dict['library_order']=[]

    for lib_info in the_dict['library_info_print_all_list']:
        if (not (lib_info['selection'] == None)):
            the_dict['library_order'].append(None)

    for lib_info in the_dict['library_info_print_all_list']:
        if (not (lib_info['selection'] == None)):
            the_dict['library_order'][lib_info['selection']]=lib_info

    for lib_info in the_dict['library_info_print_all_list']:
        if (lib_info['selection'] == None):
            lib_index=the_dict['library_info_print_all_list'].index(lib_info)
            the_dict['library_info_print_all_list'][lib_index]['selection']=lib_index
            if (not (the_dict['library_info_print_opposing_list'][lib_index] == None)):
                the_dict['library_info_print_opposing_list'][lib_index]['selection']=lib_index
            if (not (the_dict['library_info_print_matching_list'][lib_index] == None)):
                the_dict['library_info_print_matching_list'][lib_index]['selection']=lib_index
            the_dict['library_order'].append(lib_info)

    the_dict['library_info_print_all_list'].clear()
    the_dict['library_info_print_opposing_list'].clear()
    the_dict['library_info_print_matching_list'].clear()
    for lib_info in the_dict['library_order']:
        the_dict['library_info_print_all_list'].append(lib_info)
        if (lib_info['selected']):
            the_dict['library_info_print_opposing_list'].append(None)
            the_dict['library_info_print_matching_list'].append(lib_info)
        else:
            the_dict['library_info_print_opposing_list'].append(lib_info)
            the_dict['library_info_print_matching_list'].append(None)

    return the_dict


def swap_libraries(the_dict):
    temp_the_dict={}
    temp_the_dict['library_info_print_opposing_list']=copy.deepcopy(the_dict['library_info_print_opposing_list'])
    temp_the_dict['library_info_print_matching_list']=copy.deepcopy(the_dict['library_info_print_matching_list'])

    for selection in the_dict['library_selection_list']:
        if (not (temp_the_dict['library_info_print_opposing_list'][selection] == None )):
            the_dict['library_info_print_matching_list'][selection]=the_dict['library_info_print_opposing_list'][selection]
            the_dict['library_info_print_matching_list'][selection]['selected']=True
            the_dict['library_info_print_all_list'][selection]['selected']=True
            the_dict['library_info_print_opposing_list'][selection]=None

    for selection in the_dict['library_selection_list']:
        if (not (temp_the_dict['library_info_print_matching_list'][selection] == None )):
            the_dict['library_info_print_opposing_list'][selection]=the_dict['library_info_print_matching_list'][selection]
            the_dict['library_info_print_opposing_list'][selection]['selected']=False
            the_dict['library_info_print_all_list'][selection]['selected']=False
            the_dict['library_info_print_matching_list'][selection]=None

    return the_dict


def remove_key_from_blacklist_whitelist(the_key,the_dict):
    temp_the_dict={}
    temp_the_dict['admin_settings']={}
    temp_the_dict['admin_settings']['users']=the_dict['admin_settings']['users'].copy()

    for user_data in temp_the_dict['admin_settings']['users']:
        for library_data in user_data:
            if (library_data == the_dict['opposing_listing_type']):
                thislist=the_dict['opposing_listing_type']
            elif (library_data == the_dict['matching_listing_type']):
                thislist=the_dict['matching_listing_type']
            else:
                thislist=None

            if (thislist):
                for lib_data in user_data[library_data]:
                    if (keys_exist(lib_data,the_key)):
                        the_dict['admin_settings']['users'][the_dict['admin_settings']['users'].index(user_data)][thislist][the_dict['admin_settings']['users'][the_dict['admin_settings']['users'].index(user_data)][thislist].index(lib_data)].pop(the_key)

    return the_dict


def pre_build_all_library_data(the_dict):
    temp_the_dict={}
    temp_the_dict['library_info_print_all_list']=[]
    temp_the_dict['library_info_print_opposing_list']=[]
    temp_the_dict['library_info_print_matching_list']=[]
    temp_the_dict['fake_user_dict']=[]
    temp_the_dict['fake_user_dict'].append({'user_id':'0123456789abcdef0123456789abcdef','user_name':'fake_user','whitelist':[],'blacklist':[]})

    
    user_index=0

    for lib_data in the_dict['all_libraries_list']:
        lib_index=the_dict['all_libraries_list'].index(lib_data)
        temp_the_dict['library_info_print_all_list'].append(lib_data)
        temp_the_dict['library_info_print_opposing_list'].append(lib_data)
        temp_the_dict['library_info_print_matching_list'].append(None)
        temp_the_dict['fake_user_dict'][user_index][the_dict['opposing_listing_type']].append(lib_data)
        temp_the_dict['fake_user_dict'][user_index][the_dict['opposing_listing_type']][lib_index]['selection']=None
        temp_the_dict['fake_user_dict'][user_index][the_dict['opposing_listing_type']][lib_index]['selected']=False

    the_dict['library_info_print_all_list']=temp_the_dict['library_info_print_all_list']
    the_dict['library_info_print_opposing_list']=temp_the_dict['library_info_print_opposing_list']
    the_dict['library_info_print_matching_list']=temp_the_dict['library_info_print_matching_list']
    the_dict['fake_user_dict']=temp_the_dict['fake_user_dict']
    
    return the_dict


def build_all_library_data(the_dict):
    temp_the_dict={}
    temp_the_dict['library_info_print_all_list']=[]
    temp_the_dict['library_info_print_opposing_list']=[]
    temp_the_dict['library_info_print_matching_list']=[]
    temp_the_dict['fake_user_dict']=copy.deepcopy(the_dict['fake_user_dict'])

    
    
    user_index=0

    for lib_data in temp_the_dict['fake_user_dict'][user_index][the_dict['matching_listing_type']]:
        lib_index=temp_the_dict['fake_user_dict'][user_index][the_dict['matching_listing_type']].index(lib_data)
        temp_the_dict['library_info_print_all_list'].append(the_dict['fake_user_dict'][user_index][the_dict['matching_listing_type']][lib_index])
        temp_the_dict['library_info_print_opposing_list'].append(None)
        temp_the_dict['library_info_print_matching_list'].append(the_dict['fake_user_dict'][user_index][the_dict['matching_listing_type']][lib_index])

    for lib_data in temp_the_dict['fake_user_dict'][user_index][the_dict['opposing_listing_type']]:
        lib_index=temp_the_dict['fake_user_dict'][user_index][the_dict['opposing_listing_type']].index(lib_data)
        temp_the_dict['library_info_print_all_list'].append(the_dict['fake_user_dict'][user_index][the_dict['opposing_listing_type']][lib_index])
        temp_the_dict['library_info_print_opposing_list'].append(the_dict['fake_user_dict'][user_index][the_dict['opposing_listing_type']][lib_index])
        temp_the_dict['library_info_print_matching_list'].append(None)

    the_dict['library_info_print_all_list']=temp_the_dict['library_info_print_all_list']
    the_dict['library_info_print_opposing_list']=temp_the_dict['library_info_print_opposing_list']
    the_dict['library_info_print_matching_list']=temp_the_dict['library_info_print_matching_list']
    
    return the_dict