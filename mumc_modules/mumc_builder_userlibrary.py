import copy
from mumc_modules.mumc_server_type import isEmbyServer
from mumc_modules.mumc_user_queries import get_all_users
from mumc_modules.mumc_get_folders import add_subfolder_id_placeholders
from mumc_modules.mumc_library_queries import get_all_libraries,get_all_library_subfolders
from mumc_modules.mumc_builder_user import create_user_dicts,reorder_all_users,show_hide_gui_disabled_users,print_users_to_console,get_user_selection,is_valid_user_selected,build_library_data_for_selected_user,print_library_data_for_selected_user,save_library_data_for_selected_user,select_all_users,filter_library_folder_data_for_selected_user,update_fake_user_dict,swap_users,build_user_selection_list,jellyfin_filter_library_data_for_selected_user,remove_key_from_user
from mumc_modules.mumc_builder_library import create_library_dicts,create_library_path_id_dicts,update_existing_user_libraries,remove_libraries_from_existing_users,remove_subfolders_from_existing_users,remove_nonexisting_subfolders_from_existing_users,add_libraries_to_existing_users,add_libraries_to_new_users,add_selection_and_selected_keys,get_library_selections,is_valid_library_selected,swap_libraries,remove_key_from_blacklist_whitelist,select_all_unselected_libraries,pre_build_all_library_data,build_all_library_data,reorder_libraries_before_printing,autoselect_subfolders_with_same_library_id,reorder_user_policy_libararies,update_users_with_path_ids


#run the user and library builder
def get_users_and_libraries(the_dict):

    the_dict['all_users']=get_all_users(the_dict)
    the_dict['all_libraries']=get_all_libraries(the_dict)

    #Emby and Jellyfin use different key-names for their libraryId
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        libraryGuid='Guid'
    else:
        libraryGuid='ItemId'

    the_dict['all_libraries']=sorted(the_dict['all_libraries'],key=lambda all_lib_ids: all_lib_ids[libraryGuid])

    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        the_dict['all_library_subfolders']=get_all_library_subfolders(the_dict)

    the_dict=add_subfolder_id_placeholders('blacklist',the_dict)
    the_dict=add_subfolder_id_placeholders('whitelist',the_dict)

    for user_info in the_dict['admin_settings']['users']:
        user_info_index=the_dict['admin_settings']['users'].index(user_info)
        the_dict['admin_settings']['users'][user_info_index]['whitelist']=sorted(the_dict['admin_settings']['users'][user_info_index]['whitelist'],key=lambda all_lib_ids: all_lib_ids['lib_id'])
        the_dict['admin_settings']['users'][user_info_index]['blacklist']=sorted(the_dict['admin_settings']['users'][user_info_index]['blacklist'],key=lambda all_lib_ids: all_lib_ids['lib_id'])

    the_dict['all_users_dict']=copy.deepcopy(the_dict['admin_settings']['users'])
    the_dict['prev_users_dict']=copy.deepcopy(the_dict['admin_settings']['users'])

    the_dict['prev_user_ids_list']=[]
    for user in the_dict['prev_users_dict']:
        the_dict['prev_user_ids_list'].append(user['user_id'])

    the_dict['library_ids_per_user']={}
    the_dict['library_paths_per_user']={}
    the_dict['library_networkpaths_per_user']={}
    the_dict['all_user_ids_list']=the_dict['prev_user_ids_list'].copy()
    for user in the_dict['all_users']:
        the_dict['library_ids_per_user'][user['Id']]=[]
        if (not (user['Id'] in the_dict['all_user_ids_list'])):
            the_dict['all_user_ids_list'].append(user['Id'])
            the_dict['prev_user_ids_list'].append(None)
            the_dict['prev_users_dict'].append(None)

    the_dict=create_user_dicts(the_dict)
    the_dict=reorder_all_users(the_dict)
    the_dict=show_hide_gui_disabled_users(the_dict)
    the_dict=create_library_dicts(the_dict)
    the_dict=reorder_user_policy_libararies(the_dict)
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        the_dict=create_library_path_id_dicts(the_dict)
        the_dict=update_users_with_path_ids(the_dict)
    the_dict=update_existing_user_libraries(the_dict)
    the_dict=remove_libraries_from_existing_users(the_dict)
    the_dict=add_libraries_to_existing_users(the_dict)
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        the_dict=remove_subfolders_from_existing_users(the_dict)
        the_dict=remove_nonexisting_subfolders_from_existing_users(the_dict)
    the_dict=add_libraries_to_new_users(the_dict)
    the_dict=add_selection_and_selected_keys(the_dict)

    the_dict['user_stop_loop']=False
    the_dict['atleast_one_user_selected']=False

    #choose user and/or library selector types
    if (the_dict['user_library_selection'] == 0):
        #select user and associate desired libraries to be monitored for each user
        the_dict=select_users_select_libraries(the_dict)
    elif (the_dict['user_library_selection'] == 1):
        #select user and automatically associate all libraries each user has access to
        the_dict=select_users_all_libraries(the_dict)
    else: #(the_dict['user_library_selection'] == 2):
        #select libraries and automatically associate them to users that have access
        the_dict=all_users_select_libraries(the_dict)

    the_dict['admin_settings']['users']=the_dict['prev_users_dict']
    while None in the_dict['admin_settings']['users']:
        the_dict['admin_settings']['users'].remove(None)

    the_dict=remove_key_from_blacklist_whitelist('selection',the_dict)
    the_dict=remove_key_from_blacklist_whitelist('selected',the_dict)
    the_dict=remove_key_from_user('userPosition',the_dict)

    return the_dict['admin_settings']['users']


def select_users_select_libraries(the_dict):

    while (the_dict['user_stop_loop'] == False):
        the_dict=print_users_to_console(the_dict)
        the_dict=get_user_selection(the_dict)
        the_dict=is_valid_user_selected(the_dict)

        if ((not the_dict['user_stop_loop']) and the_dict['user_valid_selection']):
            the_dict=build_library_data_for_selected_user(the_dict)
            the_dict['library_stop_loop']=False
            while (the_dict['library_stop_loop'] == False):
                the_dict=reorder_libraries_before_printing(the_dict)
                the_dict=print_library_data_for_selected_user(the_dict)
                the_dict=get_library_selections(the_dict)
                the_dict['library_valid_selection']=False
                the_dict=is_valid_library_selected(the_dict)
                if (the_dict['library_valid_selection']):
                    if (not (isEmbyServer(the_dict['admin_settings']['server']['brand']))):
                        the_dict=autoselect_subfolders_with_same_library_id(the_dict)
                    the_dict=swap_libraries(the_dict)
            the_dict=save_library_data_for_selected_user(the_dict)

    return the_dict


def select_users_all_libraries(the_dict):

    while (the_dict['user_stop_loop'] == False):
        the_dict=print_users_to_console(the_dict)
        the_dict=get_user_selection(the_dict)
        the_dict=is_valid_user_selected(the_dict)

        if (the_dict['user_stop_loop'] and the_dict['user_valid_selection']):
            the_dict=build_user_selection_list(the_dict)
            for selected_user in the_dict['user_selection_list']:
                the_dict['user_selection_int']=selected_user
                the_dict=build_library_data_for_selected_user(the_dict)
                the_dict['library_stop_loop']=False
                while (the_dict['library_stop_loop'] == False):
                    the_dict=reorder_libraries_before_printing(the_dict)
                    the_dict=print_library_data_for_selected_user(the_dict)
                    the_dict=select_all_unselected_libraries(the_dict)
                    the_dict['library_stop_loop'] = True
                    the_dict['library_valid_selection']=False
                    the_dict=is_valid_library_selected(the_dict)
                    if (the_dict['library_valid_selection']):
                        the_dict=swap_libraries(the_dict)
                the_dict=save_library_data_for_selected_user(the_dict)
        else:
            the_dict=swap_users(the_dict)

    return the_dict


def all_users_select_libraries(the_dict):

    the_dict=pre_build_all_library_data(the_dict)

    while (the_dict['user_stop_loop'] == False):
        the_dict=print_users_to_console(the_dict)
        the_dict=select_all_users(the_dict)
        the_dict=is_valid_user_selected(the_dict)

        if ((not the_dict['user_stop_loop']) and the_dict['user_valid_selection']):
            the_dict=build_all_library_data(the_dict)
            the_dict=reorder_libraries_before_printing(the_dict)
            the_dict=print_library_data_for_selected_user(the_dict)
            the_dict=get_library_selections(the_dict)
            the_dict['library_valid_selection']=False
            the_dict=is_valid_library_selected(the_dict)

        if (the_dict['library_valid_selection']):
            if (not (isEmbyServer(the_dict['admin_settings']['server']['brand']))):
                the_dict=autoselect_subfolders_with_same_library_id(the_dict)
            the_dict=swap_libraries(the_dict)
            the_dict=update_fake_user_dict(the_dict)

    for selected_user in the_dict['user_selection_list']:
        the_dict['user_selection_int']=selected_user
        if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
            the_dict=filter_library_folder_data_for_selected_user(the_dict)
        else:
            the_dict=jellyfin_filter_library_data_for_selected_user(the_dict)
        the_dict=save_library_data_for_selected_user(the_dict)
        the_dict=build_all_library_data(the_dict)

    return the_dict