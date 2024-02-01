import copy
from mumc_modules.mumc_compare_items import keys_exist
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_blacklist_whitelist import get_opposing_listing_type,get_matching_listing_type


def create_library_dicts(the_dict):

    temp_lib_dict={}
    the_dict['all_libraries_list']=[]
    the_dict['all_library_ids_list']=[]
    the_dict['all_library_paths_list']=[]
    the_dict['all_library_network_paths_list']=[]
    the_dict['all_library_collection_types_list']=[]

    #Emby and Jellyfin use different key-names for their libraryId
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        libraryGuid='ItemId'
    else:
        libraryGuid='Guid'

    for libs in the_dict['all_libraries']:
        libpos=the_dict['all_libraries'].index(libs)

        for subdata in libs['LibraryOptions']['PathInfos']:
            pathpos=libs['LibraryOptions']['PathInfos'].index(subdata)
            temp_lib_dict['lib_id']=the_dict['all_libraries'][libpos][libraryGuid]
            if (('CollectionType' in libs) and
                (not (libs['CollectionType'] == ''))):
                temp_lib_dict['collection_type']=libs['CollectionType']
            else:
                temp_lib_dict['collection_type']=None
            if (('Path' in libs['LibraryOptions']['PathInfos'][pathpos]) and
                (not (libs['LibraryOptions']['PathInfos'][pathpos]['Path'] == ''))):
                temp_lib_dict['path']=libs['LibraryOptions']['PathInfos'][pathpos]['Path']
            else:
                temp_lib_dict['path']=None
            if (('NetworkPath' in libs['LibraryOptions']['PathInfos'][pathpos]) and
                (not (libs['LibraryOptions']['PathInfos'][pathpos]['NetworkPath'] == ''))):
                temp_lib_dict['network_path']=libs['LibraryOptions']['PathInfos'][pathpos]['NetworkPath']
            else:
                temp_lib_dict['network_path']=None
            temp_lib_dict['lib_enabled']=True

            the_dict['all_libraries_list'].append(copy.deepcopy(temp_lib_dict))
            the_dict['all_library_ids_list'].append(temp_lib_dict['lib_id'])
            the_dict['all_library_paths_list'].append(temp_lib_dict['path'])
            the_dict['all_library_network_paths_list'].append(temp_lib_dict['network_path'])
            the_dict['all_library_collection_types_list'].append(temp_lib_dict['collection_type'])

    the_dict.pop('all_libraries')
    
    return the_dict


def create_library_path_id_dicts(the_dict):

    the_dict['all_library_path_ids_list']=[]

    for path_str in the_dict['all_library_paths_list']:
        path_found=False
        for lib_data in the_dict['all_library_subfolders']:
            if (not (path_found)):
                for folder_data in lib_data['SubFolders']:
                    if (folder_data['Path'] == path_str):
                        the_dict['all_library_path_ids_list'].append(folder_data['Id'])
                        path_found=True
                        break
            else:
                break
        if (not (path_found)):
            the_dict['all_library_path_ids_list'].append(None)

    the_dict.pop('all_library_subfolders')

    return the_dict


def update_existing_user_libraries(the_dict):
    opposing_listing_type=get_opposing_listing_type(the_dict)
    matching_listing_type=get_matching_listing_type(the_dict)

    for prev_user in the_dict['prev_users_dict']:
        if (not(prev_user == None)):
            prev_user_index=the_dict['prev_users_dict'].index(prev_user)
            for lib_info in prev_user[matching_listing_type]:
                list_index=prev_user[matching_listing_type].index(lib_info)
                for lib_id_index in range(len(the_dict['all_library_ids_list'])):
                    if ((lib_info['lib_id'] == the_dict['all_library_ids_list'][lib_id_index]) and (lib_info['path'] == the_dict['all_library_paths_list'][lib_id_index])):
                        the_dict['prev_users_dict'][prev_user_index][matching_listing_type][list_index]['network_path']=the_dict['all_library_network_paths_list'][lib_id_index]
                        the_dict['prev_users_dict'][prev_user_index][matching_listing_type][list_index]['collection_type']=the_dict['all_library_collection_types_list'][lib_id_index]
                        break
            for lib_info in prev_user[opposing_listing_type]:
                list_index=prev_user[opposing_listing_type].index(lib_info)
                for lib_id_index in range(len(the_dict['all_library_ids_list'])):
                    if ((lib_info['lib_id'] == the_dict['all_library_ids_list'][lib_id_index]) and (lib_info['path'] == the_dict['all_library_paths_list'][lib_id_index])):
                        the_dict['prev_users_dict'][prev_user_index][opposing_listing_type][list_index]['network_path']=the_dict['all_library_network_paths_list'][lib_id_index]
                        the_dict['prev_users_dict'][prev_user_index][opposing_listing_type][list_index]['collection_type']=the_dict['all_library_collection_types_list'][lib_id_index]
                        break

    for user_pos in range(len(the_dict['prev_users_dict'])):
        if (not (the_dict['prev_users_dict'][user_pos] == None)):
            the_dict['all_users_dict'][user_pos]=copy.deepcopy(the_dict['prev_users_dict'][user_pos])

    return the_dict


def remove_libraries_from_existing_users(the_dict):
    opposing_listing_type=get_opposing_listing_type(the_dict)
    matching_listing_type=get_matching_listing_type(the_dict)

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

            for lib_info in the_dict['prev_users_dict'][the_dict['prev_users_dict'].index(existing_user)][opposing_listing_type]:
                if (not (lib_info['lib_id'] in enabled_lib_id_list)):
                    the_dict['all_users_dict'][the_dict['prev_users_dict'].index(existing_user)][opposing_listing_type].remove(lib_info)
            for lib_info in the_dict['prev_users_dict'][the_dict['prev_users_dict'].index(existing_user)][matching_listing_type]:
                if (not (lib_info['lib_id'] in enabled_lib_id_list)):
                    the_dict['all_users_dict'][the_dict['prev_users_dict'].index(existing_user)][matching_listing_type].remove(lib_info)

    for user_pos in range(len(the_dict['prev_users_dict'])):
        if (not (the_dict['prev_users_dict'][user_pos] == None)):
            the_dict['prev_users_dict'][user_pos]=copy.deepcopy(the_dict['all_users_dict'][user_pos])

    return the_dict


#subfolder ids can be updated by doing the following:
# Emby/Jellyfin > Manage Server > Users > Select User > Select Access > Save
# Repeat this for each user or the users with non-aligned folder ids
def remove_subfolders_from_existing_users(the_dict):

    temp_the_dict={}
    temp_the_dict['prev_users_dict']=copy.deepcopy(the_dict['prev_users_dict'])
    opposing_listing_type=get_opposing_listing_type(the_dict)
    matching_listing_type=get_matching_listing_type(the_dict)
    
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

                        for lib_info in the_dict['prev_users_dict'][user_index][opposing_listing_type]:
                            lib_index=temp_the_dict['prev_users_dict'][user_index][opposing_listing_type].index(lib_info)
                            if ((lib_info['path'] == remove_path) or (lib_info['network_path'] == remove_network_path)):
                                temp_the_dict['prev_users_dict'][user_index][opposing_listing_type].pop(lib_index)

                        for lib_info in the_dict['prev_users_dict'][user_index][matching_listing_type]:
                            lib_index=temp_the_dict['prev_users_dict'][user_index][matching_listing_type].index(lib_info)
                            if ((lib_info['path'] == remove_path) or (lib_info[matching_listing_type] == remove_network_path)):
                                temp_the_dict['prev_users_dict'][user_index][matching_listing_type].pop(lib_index)
        else:
            break

    the_dict['prev_users_dict']=temp_the_dict['prev_users_dict']
    for user_pos in range(len(the_dict['prev_users_dict'])):
        if (not (the_dict['prev_users_dict'][user_pos] == None)):
            the_dict['all_users_dict'][user_pos]=temp_the_dict['prev_users_dict'][user_pos]

    return the_dict


def add_libraries_to_existing_users(the_dict):
    opposing_listing_type=get_opposing_listing_type(the_dict)
    matching_listing_type=get_matching_listing_type(the_dict)

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
            for lib_info in the_dict['prev_users_dict'][the_dict['prev_users_dict'].index(existing_user)][opposing_listing_type]:
                existing_lib_info_list.append(lib_info)
                existing_lib_id_list.append(lib_info['lib_id'])
            for lib_info in the_dict['prev_users_dict'][the_dict['prev_users_dict'].index(existing_user)][matching_listing_type]:
                existing_lib_info_list.append(lib_info)
                existing_lib_id_list.append(lib_info['lib_id'])

            for enabled_lib_id in enabled_lib_id_list:
                if (not (enabled_lib_id in existing_lib_id_list)):
                    for all_lib_id_pos in range(len(the_dict['all_library_ids_list'])):
                        if (the_dict['all_library_ids_list'][all_lib_id_pos] == enabled_lib_id):
                            the_dict['all_users_dict'][the_dict['prev_users_dict'].index(existing_user)][opposing_listing_type].append(the_dict['all_libraries_list'][all_lib_id_pos])
                else:
                    for existing_lib_id in existing_lib_id_list:
                        for all_lib_pos in range(len(the_dict['all_library_ids_list'])):
                            if (existing_lib_id == the_dict['all_library_ids_list'][all_lib_pos]):
                                if (not (the_dict['all_libraries_list'][all_lib_pos] in existing_lib_info_list)):
                                    the_dict['all_users_dict'][the_dict['prev_users_dict'].index(existing_user)][opposing_listing_type].append(the_dict['all_libraries_list'][all_lib_pos])
                                    existing_lib_info_list.append(the_dict['all_libraries_list'][all_lib_pos])
                                    existing_lib_id_list.append(the_dict['all_library_ids_list'][all_lib_pos])

    for user_pos in range(len(the_dict['prev_users_dict'])):
        if (not (the_dict['prev_users_dict'][user_pos] == None)):
            the_dict['prev_users_dict'][user_pos]=copy.deepcopy(the_dict['all_users_dict'][user_pos])

    return the_dict


def add_libraries_to_new_users(the_dict):

    temp_the_dict={}
    temp_the_dict['all_users_dict']=copy.deepcopy(the_dict['all_users_dict'])
    opposing_listing_type=get_opposing_listing_type(the_dict)

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
                    enabled_lib_id_list.append(enabled_lib_id)

            for lib_id in enabled_lib_id_list:
                if (not (lib_id in the_dict['library_ids_per_user'][this_user['user_id']])):
                    the_dict['library_ids_per_user'][this_user['user_id']].append(lib_id)

            temp_the_dict['all_library_ids_list']=copy.deepcopy(the_dict['all_library_ids_list'])
            for lib_id in enabled_lib_id_list:
                lib_index=temp_the_dict['all_library_ids_list'].index(lib_id)
                temp_the_dict['all_users_dict'][this_user_index][opposing_listing_type].append(the_dict['all_libraries_list'][lib_index])
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
    opposing_listing_type=get_opposing_listing_type(the_dict)
    matching_listing_type=get_matching_listing_type(the_dict)

    prev_users_dict_len=0
    for prev_users_dict_data in temp_the_dict['prev_users_dict']:
        if (not(prev_users_dict_data == None)):
            prev_users_dict_len+=1

    for user_info in temp_the_dict['all_users_dict']:
        user_index=temp_the_dict['all_users_dict'].index(user_info)
        for list_info in user_info[opposing_listing_type]:
            wl_index=user_info[opposing_listing_type].index(list_info)
            temp_the_dict['all_users_dict'][user_index][opposing_listing_type][wl_index]['selection']=None
            temp_the_dict['all_users_dict'][user_index][opposing_listing_type][wl_index]['selected']=False

            if (user_index < prev_users_dict_len):
                temp_the_dict['prev_users_dict'][user_index][opposing_listing_type][wl_index]['selection']=None
                temp_the_dict['prev_users_dict'][user_index][opposing_listing_type][wl_index]['selected']=False

        for list_info in user_info[matching_listing_type]:
            bl_index=user_info[matching_listing_type].index(list_info)
            temp_the_dict['all_users_dict'][user_index][matching_listing_type][bl_index]['selection']=None
            temp_the_dict['all_users_dict'][user_index][matching_listing_type][bl_index]['selected']=True

            if (user_index < prev_users_dict_len):
                temp_the_dict['prev_users_dict'][user_index][matching_listing_type][bl_index]['selection']=None
                temp_the_dict['prev_users_dict'][user_index][matching_listing_type][bl_index]['selected']=True

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

    opposing_listing_type=get_opposing_listing_type(the_dict)
    matching_listing_type=get_matching_listing_type(the_dict)

    for user_data in temp_the_dict['admin_settings']['users']:
        for library_data in user_data:
            if (library_data == opposing_listing_type):
                thislist=opposing_listing_type
            elif (library_data == matching_listing_type):
                thislist=matching_listing_type
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

    opposing_listing_type=get_opposing_listing_type(the_dict)
    user_index=0

    for lib_data in the_dict['all_libraries_list']:
        lib_index=the_dict['all_libraries_list'].index(lib_data)
        temp_the_dict['library_info_print_all_list'].append(lib_data)
        temp_the_dict['library_info_print_opposing_list'].append(lib_data)
        temp_the_dict['library_info_print_matching_list'].append(None)
        temp_the_dict['fake_user_dict'][user_index][opposing_listing_type].append(lib_data)
        temp_the_dict['fake_user_dict'][user_index][opposing_listing_type][lib_index]['selection']=None
        temp_the_dict['fake_user_dict'][user_index][opposing_listing_type][lib_index]['selected']=False

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

    opposing_listing_type=get_opposing_listing_type(the_dict)
    matching_listing_type=get_matching_listing_type(the_dict)
    user_index=0

    for lib_data in temp_the_dict['fake_user_dict'][user_index][matching_listing_type]:
        lib_index=temp_the_dict['fake_user_dict'][user_index][matching_listing_type].index(lib_data)
        temp_the_dict['library_info_print_all_list'].append(the_dict['fake_user_dict'][user_index][matching_listing_type][lib_index])
        temp_the_dict['library_info_print_opposing_list'].append(None)
        temp_the_dict['library_info_print_matching_list'].append(the_dict['fake_user_dict'][user_index][matching_listing_type][lib_index])

    for lib_data in temp_the_dict['fake_user_dict'][user_index][opposing_listing_type]:
        lib_index=temp_the_dict['fake_user_dict'][user_index][opposing_listing_type].index(lib_data)
        temp_the_dict['library_info_print_all_list'].append(the_dict['fake_user_dict'][user_index][opposing_listing_type][lib_index])
        temp_the_dict['library_info_print_opposing_list'].append(the_dict['fake_user_dict'][user_index][opposing_listing_type][lib_index])
        temp_the_dict['library_info_print_matching_list'].append(None)

    the_dict['library_info_print_all_list']=temp_the_dict['library_info_print_all_list']
    the_dict['library_info_print_opposing_list']=temp_the_dict['library_info_print_opposing_list']
    the_dict['library_info_print_matching_list']=temp_the_dict['library_info_print_matching_list']
    
    return the_dict