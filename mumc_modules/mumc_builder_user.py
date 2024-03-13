import copy
from mumc_modules.mumc_blacklist_whitelist import get_opposing_listing_type


def create_user_dicts(the_dict):

    for user in the_dict['all_users']:
        if (not (user['Id'] in the_dict['prev_user_ids_list'])):
            user_dict={}
            user_dict['user_id']=user['Id']
            user_dict['user_name']=user['Name']
            user_dict['whitelist']=[]
            user_dict['blacklist']=[]

            the_dict['all_users_dict'].append(user_dict)
   
    return the_dict


def reorder_all_users(the_dict):
    temp_the_dict={}
    temp_the_dict['all_users']=[]
    for aud in the_dict['all_users_dict']:
        for au in the_dict['all_users']:
            if (aud['user_id'] == au['Id']):
                 temp_the_dict['all_users'].append(au)
                 break

    the_dict['all_users']=temp_the_dict['all_users']

    return the_dict


def show_hide_gui_disabled_users(the_dict):
    temp_dict={}
    temp_dict['all_users']=copy.deepcopy(the_dict['all_users'])
    #Should disabled users be shown or hidden?
    if (not (the_dict['admin_settings']['behavior']['users']['monitor_disabled'])):
        #Remove/Hide users disabled in the GUI
        for user_data in reversed(temp_dict['all_users']):
            user_data_index=temp_dict['all_users'].index(user_data)
            if (user_data['Policy']['IsDisabled']):
                the_dict['all_users'].pop(user_data_index)
                the_dict['all_users_dict'].pop(user_data_index)
                the_dict['all_user_ids_list'].pop(user_data_index)
                the_dict['library_ids_per_user'].pop(temp_dict['all_users'][user_data_index]['Id'])
                try:
                    the_dict['prev_users_dict'].pop(user_data_index)
                except IndexError:
                    pass
                try:
                    the_dict['prev_user_ids_list'].pop(user_data_index)
                except IndexError:
                    pass

    return the_dict


def print_users_to_console(the_dict):

    if (len(the_dict['all_users_dict']) > 1):
        for user in the_dict['all_users_dict']:
            the_dict['user_index_total']=the_dict['all_users_dict'].index(user)
            the_dict['all_users_dict'][the_dict['user_index_total']]['userPosition']=the_dict['user_index_total']

            if ((the_dict['user_library_selection_type'] == 0) or (the_dict['user_library_selection_type'] == 1)):
                try:
                    print(str(the_dict['user_index_total']) +' - '+ the_dict['prev_users_dict'][the_dict['user_index_total']]['user_name'] + ' - ')
                except (IndexError,TypeError):
                    print(str(the_dict['user_index_total']) +' - '+ the_dict['all_users_dict'][the_dict['user_index_total']]['user_name'] + ' - ' + user['user_id'])

        print('')

    return the_dict


def get_user_selection(the_dict):
    if (the_dict['atleast_one_user_selected'] == False):
        if (the_dict['user_library_selection_type'] == 0):
            the_dict['user_selection_str']=input('Select one user at a time.\nEnter number of the user to monitor: ')
        elif (the_dict['user_library_selection_type'] == 1):
            the_dict['user_selection_str']=input('Select one or more users.\n*Use a comma or space to separate multiple selections.\nLeave blank when finished: ')
        else: #(the_dict['user_library_selection_type'] == 2):
            pass
    #When multiple explain how to select each user; when coming back to the user selection show this
    else: #((i >= 1) and (the_dict['atleast_one_user_selected'] == True)):
        if (the_dict['user_index_total'] >= 1):
            print('Monitoring multiple users is possible.')
        if (the_dict['user_library_selection_type'] == 0):
            the_dict['user_selection_str']=input('Select one user at a time.\nEnter number of the next user to monitor; leave blank when finished: ')
        elif (the_dict['user_library_selection_type'] == 1):
            the_dict['user_selection_str']=input('Select one or more users.\n*Use a comma or space to separate multiple selections.\nLeave blank when finished: ')
        else: #(the_dict['user_library_selection_type'] == 2):
            pass
    
    print('')
        
    return the_dict


def select_all_users(the_dict):
    the_dict['user_selection_str']=''

    for user_id in the_dict['all_user_ids_list']:
        the_dict['user_selection_str']+=str(the_dict['all_user_ids_list'].index(user_id)) + ','

    return the_dict


def build_library_data_for_selected_user(the_dict):
    temp_the_dict={}
    temp_the_dict['library_info_print_all_list']=[]
    temp_the_dict['library_info_print_opposing_list']=[]
    temp_the_dict['library_info_print_matching_list']=[]
    temp_the_dict['all_users_dict']=copy.deepcopy(the_dict['all_users_dict'])
    opposing_listing_type=get_opposing_listing_type(the_dict['admin_settings']['behavior']['list'])
    matching_listing_type=the_dict['admin_settings']['behavior']['list']

    user_index=the_dict['user_selection_int']

    for lib_data in temp_the_dict['all_users_dict'][user_index][matching_listing_type]:
        lib_index=temp_the_dict['all_users_dict'][user_index][matching_listing_type].index(lib_data)
        temp_the_dict['library_info_print_all_list'].append(the_dict['all_users_dict'][user_index][matching_listing_type][lib_index].copy())
        temp_the_dict['library_info_print_opposing_list'].append(None)
        temp_the_dict['library_info_print_matching_list'].append(the_dict['all_users_dict'][user_index][matching_listing_type][lib_index].copy())

    for lib_data in temp_the_dict['all_users_dict'][user_index][opposing_listing_type]:
        lib_index=temp_the_dict['all_users_dict'][user_index][opposing_listing_type].index(lib_data)
        temp_the_dict['library_info_print_all_list'].append(the_dict['all_users_dict'][user_index][opposing_listing_type][lib_index].copy())
        temp_the_dict['library_info_print_opposing_list'].append(the_dict['all_users_dict'][user_index][opposing_listing_type][lib_index].copy())
        temp_the_dict['library_info_print_matching_list'].append(None)
    
    the_dict['library_info_print_all_list']=temp_the_dict['library_info_print_all_list']
    the_dict['library_info_print_opposing_list']=temp_the_dict['library_info_print_opposing_list']
    the_dict['library_info_print_matching_list']=temp_the_dict['library_info_print_matching_list']
    
    return the_dict


def filter_library_data_for_selected_user(the_dict):

    temp_the_dict={}
    temp_the_dict['all_library_ids_list']=copy.deepcopy(the_dict['all_library_ids_list'])

    for path_id in the_dict['all_library_ids_list']:
        path_index=temp_the_dict['all_library_ids_list'].index(path_id)
        if (the_dict['all_library_ids_list'][path_index] and the_dict['all_library_path_ids_list'][path_index]):
            lib_id_folder_id=str(the_dict['all_library_ids_list'][path_index] + '_' + the_dict['all_library_path_ids_list'][path_index])
            if (lib_id_folder_id in the_dict['all_users'][the_dict['user_selection_int']]['Policy']['ExcludedSubFolders']):
                the_dict['library_info_print_all_list'][path_index]=False
                the_dict['library_info_print_opposing_list'][path_index]=False
                the_dict['library_info_print_matching_list'][path_index]=False
        temp_the_dict['all_library_ids_list'][path_index]=None

    while False in the_dict['library_info_print_all_list']:
        the_dict['library_info_print_all_list'].remove(False)
        the_dict['library_info_print_opposing_list'].remove(False)
        the_dict['library_info_print_matching_list'].remove(False)

    return the_dict


def print_library_data_for_selected_user(the_dict):

    if (the_dict['user_valid_selection']):
        #Depending on library setup behavior the chosen libraries will either be treated as blacklisted libraries or whitelisted libraries
        listing_type=the_dict['admin_settings']['behavior']['list']
        if (listing_type == 'blacklist'):
            monitor_type='monitored for'
        else: #(listing_type == 'whitelist'):
            monitor_type='excluded from'
        message='Enter number of the library folder(s) to ' + str(listing_type) + ' (aka monitor) for the selected user.'
        message+='\nMedia in ' + str(listing_type) + 'ed library folder(s) will be ' + str(monitor_type) + ' deletion.'

    for lib_info in the_dict['library_info_print_all_list']:
        print_string=str(lib_info['selection'])
        print_string+=' - ' + str(lib_info['collection_type'])
        if (not (lib_info['selected'])):
            print_string+=' - Path: ' + str(lib_info['path'])
            print_string+=' - NetPath: ' + str(lib_info['network_path'])
            print_string+=' - LibId: ' + str(lib_info['lib_id'])

        if ((the_dict['user_library_selection_type'] == 0) or (the_dict['user_library_selection_type'] == 2)):
            print(print_string)

    if ((the_dict['user_library_selection_type'] == 0) or (the_dict['user_library_selection_type'] == 2)):
        print('')

    return the_dict


def is_valid_user_selected(the_dict):
    print_error=''
    the_dict['user_selection_list']=[]

    #replace spaces with commas (assuming people will use spaces because the space bar is bigger and easier to push)
    the_dict['comma_selected_user_str']=the_dict['user_selection_str'].replace(' ',',')
    #convert string to list
    the_dict['selected_user_list_of_strs']=the_dict['comma_selected_user_str'].split(',')
    #remove blanks
    while ('' in the_dict['selected_user_list_of_strs']):
        the_dict['selected_user_list_of_strs'].remove('')
    #remove duplicate strings
    the_dict['selected_user_list_of_strs']=list(set(the_dict['selected_user_list_of_strs']))

    try:
        selected_user_str=None

        #We get here when we are done selecting users to monitor
        if ((the_dict['selected_user_list_of_strs'] == []) and (the_dict['atleast_one_user_selected'])):
            the_dict['user_stop_loop']=True
            print('')
        #We get here if we tried not to select any users; at least one must be selected
        elif ((the_dict['selected_user_list_of_strs'][0] == '') and (not (the_dict['atleast_one_user_selected']))):
            print_error('\nMust select at least one user. Try again.\n')
        #We get here to allow selecting users
        elif (not (the_dict['selected_user_list_of_strs'][0] == '')):
            for selected_user_str in the_dict['selected_user_list_of_strs']:
                #We get here to allow selecting libraries for the specified library
                the_dict['user_selection_float']=float(selected_user_str)
                if ((the_dict['user_selection_float'] % 1) == 0):
                    the_dict['user_selection_int']=int(the_dict['user_selection_float'])
                else:
                    the_dict['user_selection_int']=None
                    print_error+='Invalid value. Try again.\n'

                if (not (the_dict['user_selection_int'] == None)):
                    if ((the_dict['user_selection_int'] >= 0) and (the_dict['user_selection_int'] < len(the_dict['all_user_ids_list']))):
                        the_dict['user_selection_list'].append(the_dict['user_selection_int'])
                        the_dict['atleast_one_user_selected']=True
                        the_dict['user_valid_selection']=True
                    else:
                        print_error+='Value Out Of Range. Try again.\n'
    except:
        print_error+='Error When Selecting library. Try again.\n'

    if (the_dict['user_library_selection_type'] == 0):
        if (len(the_dict['user_selection_list']) > 1):
            print_error='Must not select more than a single user at a time. Try again.\n'
            selected_user_str=the_dict['user_selection_list']

    if (not (print_error == '')):
        print(str(selected_user_str) + ' - ' + str(print_error) + '\n')
        the_dict['user_valid_selection']=False
    else:
        #remove duplicate integers and sort
        the_dict['user_selection_list']=list(set(the_dict['user_selection_list']))
        the_dict['user_selection_list'].sort()

    return the_dict


def save_library_data_for_selected_user(the_dict):
    temp_the_dict={}
    temp_the_dict['all_users_dict']=copy.deepcopy(the_dict['all_users_dict'])
    opposing_listing_type=get_opposing_listing_type(the_dict['admin_settings']['behavior']['list'])
    matching_listing_type=the_dict['admin_settings']['behavior']['list']

    user_index=the_dict['user_selection_int']

    temp_the_dict['all_users_dict'][user_index][opposing_listing_type]=[]
    temp_the_dict['all_users_dict'][user_index][matching_listing_type]=[]

    for lib_data in the_dict['library_info_print_all_list']:
        if (lib_data['selected']):
            temp_the_dict['all_users_dict'][user_index][matching_listing_type].append(lib_data)
        else:
            temp_the_dict['all_users_dict'][user_index][opposing_listing_type].append(lib_data)

    the_dict['all_users_dict']=temp_the_dict['all_users_dict']

    for user_pos in range(len(the_dict['prev_users_dict'])):
        if (not (the_dict['prev_users_dict'][user_pos] == None)):
            the_dict['prev_users_dict'][user_pos]=copy.deepcopy(the_dict['all_users_dict'][user_pos])
    
    if (the_dict['prev_users_dict'][user_index] == None):
        the_dict['prev_users_dict'][user_index]=the_dict['all_users_dict'][user_index]
        the_dict['prev_user_ids_list'][user_index]=the_dict['all_user_ids_list'][user_index]
    
    return the_dict


def update_fake_user_dict(the_dict):
    fake_user_index=0
    opposing_listing_type=get_opposing_listing_type(the_dict['admin_settings']['behavior']['list'])
    matching_listing_type=the_dict['admin_settings']['behavior']['list']
    the_dict['fake_user_dict'][fake_user_index][opposing_listing_type].clear()
    the_dict['fake_user_dict'][fake_user_index][matching_listing_type].clear()

    for lib_info in the_dict['library_info_print_opposing_list']:
        if (not (lib_info == None)):
            the_dict['fake_user_dict'][fake_user_index][opposing_listing_type].append(lib_info)

    for lib_info in the_dict['library_info_print_matching_list']:
        if (not (lib_info == None)):
            the_dict['fake_user_dict'][fake_user_index][matching_listing_type].append(lib_info)

    return the_dict


def build_user_selection_list(the_dict):
    for user_info in the_dict['prev_users_dict']:
        user_index=the_dict['prev_users_dict'].index(user_info)
        if (not (user_info == None)):
            the_dict['user_selection_list'].append(user_index)

    return the_dict


def swap_users(the_dict):
    for selected_user in the_dict['user_selection_list']:
        if (the_dict['prev_users_dict'][selected_user] == None):
            the_dict['prev_users_dict'][selected_user]=the_dict['all_users_dict'][selected_user]
        else:
            the_dict['prev_users_dict'][selected_user]=None

    return the_dict