from mumc_modules.mumc_output import print_byType,open_and_return_file,save_yaml_config
from mumc_modules.mumc_setup_questions import get_brand,get_server_url,get_admin_username,get_admin_password,get_library_setup_behavior,get_library_matching_behavior,get_tag_name,get_show_disabled_users,get_user_and_library_selection_type
from mumc_modules.mumc_key_authentication import authenticate_user_by_name
from mumc_modules.mumc_versions import get_script_version
from mumc_modules.mumc_console_info import print_all_media_disabled,built_new_config_not_setup_to_delete_media
from mumc_modules.mumc_config_updater import yaml_configurationUpdater
from mumc_modules.mumc_builder_userlibrary import build_users_and_libraries
from mumc_modules.mumc_init import getIsAnyMediaEnabled
from mumc_modules.mumc_blacklist_whitelist import get_unpreferred_listing_type
from mumc_modules.mumc_paths_files import get_default_config_path
import copy


def filterYAMLConfigKeys_ToKeep(dirty_dict,*clean_keys):

    return {cleanKey:dirty_dict[cleanKey] for cleanKey in clean_keys}


def yaml_configurationBuilder(the_dict):

    #strip out uneccessary data
    config_data=filterYAMLConfigKeys_ToKeep(copy.deepcopy(the_dict),'version','basic_settings','advanced_settings','admin_settings','DEBUG')

    config_data['basic_settings']['filter_statements'].pop('audio')

    config_data['basic_settings']['filter_statements'].pop('audiobook')

    config_data['basic_settings'].pop('filter_tags')
    config_data['advanced_settings'].pop('filter_statements')
    config_data['advanced_settings'].pop('behavioral_statements')
    config_data['advanced_settings'].pop('behavioral_tags')

    if (config_data['advanced_settings']['whitetags']['global'] == []):
        config_data['advanced_settings'].pop('whitetags')
    else:
        config_data['advanced_settings']['whitetags'].pop('movie')
        config_data['advanced_settings']['whitetags'].pop('episode')
        config_data['advanced_settings']['whitetags'].pop('audio')
        config_data['advanced_settings']['whitetags'].pop('audiobook')
    if (config_data['advanced_settings']['blacktags']['global'] == []):
        config_data['advanced_settings'].pop('blacktags')
    else:
        config_data['advanced_settings']['blacktags'].pop('movie')
        config_data['advanced_settings']['blacktags'].pop('episode')
        config_data['advanced_settings']['blacktags'].pop('audio')
        config_data['advanced_settings']['blacktags'].pop('audiobook')

    config_data['advanced_settings'].pop('delete_empty_folders')
    config_data['advanced_settings'].pop('radarr')
    config_data['advanced_settings'].pop('sonarr')
    #config_data['advanced_settings'].pop('lidarr')
    #config_data['advanced_settings'].pop('readarr')
    config_data['advanced_settings'].pop('trakt_fix')
    config_data['advanced_settings'].pop('console_controls')
    config_data['advanced_settings'].pop('UPDATE_CONFIG')

    if ((config_data['admin_settings']['behavior']['list'] == 'blacklist') and (config_data['admin_settings']['behavior']['matching'] == 'byId') and (config_data['admin_settings']['behavior']['users']['monitor_disabled'])):
        config_data['admin_settings'].pop('behavior')
    else:
        if (config_data['admin_settings']['behavior']['list'] == 'blacklist'):
            config_data['admin_settings']['behavior'].pop('list')

        if (config_data['admin_settings']['behavior']['matching'] == 'byId'):
            config_data['admin_settings']['behavior'].pop('matching')

        if (config_data['admin_settings']['behavior']['users']['monitor_disabled']):
            config_data['admin_settings']['behavior'].pop('users')

    config_data['advanced_settings'].pop('episode_control')

    #if ((config_data['admin_settings']['media_managers']['radarr']['url'] == None) and (config_data['admin_settings']['media_managers']['radarr']['api_key'] == None)):
    if (config_data['admin_settings']['media_managers']['radarr'] == [{'enabled':True,'url':'','api_key':''}]):
        config_data['admin_settings']['media_managers'].pop('radarr')
    else:
        for arr in config_data['admin_settings']['media_managers']['radarr']:
            if (arr['enabled'] or (arr['enabled'] == None)):
                #config_data['admin_settings']['media_managers']['radarr'].pop('enabled')
                arr.pop('enabled')
            if ((arr['url'] == None) or (arr['url'] == '')):
                #config_data['admin_settings']['media_managers']['radarr'].pop('url')
                arr.pop('url')
            if ((arr['api_key'] == None) or (arr['api_key'] == '')):
                #config_data['admin_settings']['media_managers']['radarr'].pop('api_key')
                arr.pop('api_key')

    #if ((config_data['admin_settings']['media_managers']['sonarr']['url'] == None) and (config_data['admin_settings']['media_managers']['sonarr']['api_key'] == None)):
    if (config_data['admin_settings']['media_managers']['sonarr'] == [{'enabled':True,'url':'','api_key':''}]):
        config_data['admin_settings']['media_managers'].pop('sonarr')
    else:
        for arr in config_data['admin_settings']['media_managers']['sonarr']:
            if (arr['enabled'] or (arr['enabled'] == None)):
                #config_data['admin_settings']['media_managers']['sonarr'].pop('enabled')
                arr.pop('enabled')
            if ((arr['url'] == None) or (arr['url'] == '')):
                #config_data['admin_settings']['media_managers']['sonarr'].pop('url')
                arr.pop('url')
            if ((arr['api_key'] == None) or (arr['api_key'] == '')):
                #config_data['admin_settings']['media_managers']['sonarr'].pop('api_key')
                arr.pop('api_key')

    ##if ((config_data['admin_settings']['media_managers']['lidarr']['url'] == None) and (config_data['admin_settings']['media_managers']['lidarr']['api_key'] == None)):
    #if (config_data['admin_settings']['media_managers']['lidarr'] == [{'enabled':True,'url':'','api_key':''}]):
        #config_data['admin_settings']['media_managers'].pop('lidarr')
    #else:
        #for arr in config_data['admin_settings']['media_managers']['lidarr']:
            #if (arr['enabled'] or (arr['enabled'] == None)):
                ##config_data['admin_settings']['media_managers']['lidarr'].pop('enabled')
                #arr.pop('enabled')
            #if ((arr['url'] == None) or (arr['url'] == '')):
                ##config_data['admin_settings']['media_managers']['lidarr'].pop('url')
                #arr.pop('url')
            #if ((arr['api_key'] == None) or (arr['api_key'] == '')):
                ##config_data['admin_settings']['media_managers']['lidarr'].pop('api_key')
                #arr.pop('api_key')

    ##if ((config_data['admin_settings']['media_managers']['readarr']['url'] == None) and (config_data['admin_settings']['media_managers']['readarr']['api_key'] == None)):
    #if (config_data['admin_settings']['media_managers']['readarr'] == [{'enabled':True,'url':'','api_key':''}]):
        #config_data['admin_settings']['media_managers'].pop('readarr')
    #else:
        #for arr in config_data['admin_settings']['media_managers']['readarr']:
            #if (arr['enabled'] or (arr['enabled'] == None)):
                ##config_data['admin_settings']['media_managers']['readarr'].pop('enabled')
                #arr.pop('enabled')
            #if ((arr['url'] == None) or (arr['url'] == '')):
                ##config_data['admin_settings']['media_managers']['readarr'].pop('url')
                #arr.pop('url')
            #if ((arr['api_key'] == None) or (arr['api_key'] == '')):
                ##config_data['admin_settings']['media_managers']['readarr'].pop('api_key')
                #arr.pop('api_key')

    if (config_data['admin_settings']['media_managers'] == {}):
        config_data['admin_settings'].pop('media_managers')

    config_data['admin_settings'].pop('api_controls')
    config_data['admin_settings'].pop('cache')
    config_data['admin_settings'].pop('output_controls')

    #save yaml config file
    save_yaml_config(config_data,the_dict['config_file_path'] / the_dict['config_file_name_yaml'])


#get user input needed to build or edit the mumc_config.yaml file
def build_configuration_file(the_dict,orig_dict={}):

    print('----------------------------------------------------------------------------------------')
    print('Version: ' + get_script_version())

    #Building the config
    if (not the_dict['advanced_settings']['UPDATE_CONFIG']):

        the_dict.update(open_and_return_file(get_default_config_path(the_dict['script_file_path'])))
        the_dict['version']=get_script_version()

        print('----------------------------------------------------------------------------------------')

        #ask user for server brand (i.e. emby or jellyfin)
        if ('-server_brand' in the_dict['argv']):
            the_dict['admin_settings']['server']['brand']=the_dict['argv']['-server_brand']
        else:
            the_dict['admin_settings']['server']['brand']=get_brand()
        the_dict['server_brand']=the_dict['admin_settings']['server']['brand']

        if ('-config_updater' in the_dict['argv']):
            the_dict['advanced_settings']['UPDATE_CONFIG']=the_dict['argv']['-config_updater']
        the_dict['UPDATE_CONFIG']=the_dict['advanced_settings']['UPDATE_CONFIG']

        the_dict.pop('server_brand')
        the_dict.pop('UPDATE_CONFIG')

        print('----------------------------------------------------------------------------------------')

        #ask user for server url
        if ('-server_url' in the_dict['argv']):
            the_dict['admin_settings']['server']['url']=the_dict['argv']['-server_url']
        else:
            the_dict['admin_settings']['server']['url']=get_server_url()

        print('----------------------------------------------------------------------------------------')

        #define username and password so it can be popped later without generating an error
        the_dict['username']=None
        the_dict['password']=None

        #check if server_auth_key CMD option exists
        if (('-server_auth_key' in the_dict['argv']) and (not (the_dict['argv']["-server_auth_key"] == ""))):
            the_dict['admin_settings']['server']['auth_key']=the_dict['argv']['-server_auth_key']

            if (('-server_admin_id' in the_dict['argv']) and (not (the_dict['argv']["-server_admin_id"] == ""))):
                the_dict['admin_settings']['server']['admin_id']=the_dict['argv']['-server_admin_id']
        else:
            #ask user for administrator username
            if ('-admin_username' in the_dict['argv']):
                the_dict['username']=the_dict['argv']['-admin_username']
            else:
                the_dict['username']=get_admin_username()

            print('----------------------------------------------------------------------------------------')

            #ask user for administrator password
            if ('-admin_password' in the_dict['argv']):
                the_dict['password']=the_dict['argv']['-admin_password']
            else:
                the_dict['password']=get_admin_password()

            print('----------------------------------------------------------------------------------------')

            #ask server for authentication key and administrator id using administrator username/password
            authenticated_user_data=authenticate_user_by_name(the_dict['username'],the_dict['password'],the_dict)

            the_dict['admin_settings']['server']['auth_key']=authenticated_user_data['AccessToken']
            the_dict['admin_settings']['server']['admin_id']=authenticated_user_data['User']['Id']


        '''
        authenticated_user_data=authenticate_user_by_name(the_dict['username'],the_dict['password'],the_dict)
        #get all existing labelled authentication keys
        labelled_authentication_keys=get_labelled_authentication_keys(authenticated_user_data,the_dict)
        #parse for existing labelled MUMC specific authentication key
        the_dict['admin_settings']['server']['auth_key']=get_MUMC_labelled_authentication_key(labelled_authentication_keys,the_dict)

        #if there is not already an exsiting labelled MUMC specific key then create one
        if (not the_dict['admin_settings']['server']['auth_key']):
            #create labelled MUMC specific authentication key
            create_labelled_authentication_key(authenticated_user_data,the_dict)
            #clear previously cached data from get_labelled_authentication_keys() so the same key data is not returned
            # which would not contain the newly created labelled MUMC key
            the_dict['cached_data'].removeCachedEntry(labelled_authentication_keys['request_url'])
            #get all existing labelled authentication keys
            labelled_authentication_keys=get_labelled_authentication_keys(authenticated_user_data,the_dict)
            #parse for existing labelled MUMC specific authentication key
            the_dict['admin_settings']['server']['auth_key']=get_MUMC_labelled_authentication_key(labelled_authentication_keys,the_dict)
        '''

        #Remove username and password so they cannot be used later
        the_dict.pop('username')
        the_dict.pop('password')

        #ask user how they want to choose libraries/folders
        if ('-list_behavior' in the_dict['argv']):
            the_dict['admin_settings']['behavior']['list']=the_dict['argv']['-list_behavior']
        else:
            the_dict['admin_settings']['behavior']['list']=get_library_setup_behavior()

        print('----------------------------------------------------------------------------------------')

        #ask user how they want media items to be matched to libraries/folders
        if ('-matching_behavior' in the_dict['argv']):
            the_dict['admin_settings']['behavior']['matching']=the_dict['argv']['-matching_behavior']
        else:
            the_dict['admin_settings']['behavior']['matching']=get_library_matching_behavior()

        print('----------------------------------------------------------------------------------------')

        #Initialize for compare with other tag to prevent using the same tag in both blacktag and whitetag
        the_dict['advanced_settings']['blacktags']['global']=[]
        the_dict['advanced_settings']['whitetags']['global']=[]

        #ask user for global blacktag(s)
        if ('-global_blacktags' in the_dict['argv']):
            the_dict['advanced_settings']['blacktags']['global']=the_dict['argv']['-global_blacktags']
        else:
            the_dict['advanced_settings']['blacktags']['global']=get_tag_name('blacktag',the_dict['advanced_settings']['whitetags']['global'])

        print('----------------------------------------------------------------------------------------')

        #ask user for global whitetag(s)
        if ('-global_whitetags' in the_dict['argv']):
            the_dict['advanced_settings']['whitetags']['global']=the_dict['argv']['-global_whitetags']
        else:
            the_dict['advanced_settings']['whitetags']['global']=get_tag_name('whitetag',the_dict['advanced_settings']['blacktags']['global'])

        print('----------------------------------------------------------------------------------------')

    #Updating the config; Prepare to run the config editor
    else: #(the_dict['advanced_settings']['UPDATE_CONFIG']):

        the_dict['version']=get_script_version()

        print('----------------------------------------------------------------------------------------')

        #ask user how they want to choose libraries/folders
        if ('-list_behavior' in the_dict['argv']):
            the_dict['admin_settings']['behavior']['list']=the_dict['argv']['-list_behavior']
        else:
            the_dict['admin_settings']['behavior']['list']=get_library_setup_behavior(the_dict['admin_settings']['behavior']['list'])

        print('----------------------------------------------------------------------------------------')

        #ask user how they want media items to be matched to libraries/folders
        if ('-matching_behavior' in the_dict['argv']):
            the_dict['admin_settings']['behavior']['matching']=the_dict['argv']['-matching_behavior']
        else:
            the_dict['admin_settings']['behavior']['matching']=get_library_matching_behavior(the_dict['admin_settings']['behavior']['matching'])

        print('----------------------------------------------------------------------------------------')

    #store preferred listing type to be used in get_users_and_libraries()
    the_dict['preferred_listing_type']=the_dict['admin_settings']['behavior']['list']
    #store unpreferred listing type to be used in get_users_and_libraries()
    the_dict['unpreferred_listing_type']=get_unpreferred_listing_type(the_dict['admin_settings']['behavior']['list'])

    #ask if users disabled in the GUI should be monitored; this also controls if they are shown during selection of monitored_users
    #the_dict['admin_settings']['behavior']['users']={}
    if ('-monitor_disabled_users' in the_dict['argv']):
        the_dict['admin_settings']['behavior']['users']['monitor_disabled']=the_dict['argv']['-monitor_disabled_users']
    else:
        the_dict['admin_settings']['behavior']['users']['monitor_disabled']=get_show_disabled_users()

    print('----------------------------------------------------------------------------------------')

    #ask how to select users and libraries
    if ('-user_library_selection' in the_dict['argv']):
        the_dict['user_library_selection']=the_dict['argv']['-user_library_selection']
    else:
        the_dict['user_library_selection']=get_user_and_library_selection_type(the_dict['admin_settings']['behavior']['list'])

    print('----------------------------------------------------------------------------------------')

    #run the user and library selector
    the_dict['admin_settings']['users']=build_users_and_libraries(the_dict)

    print('----------------------------------------------------------------------------------------')

    #Add Sonarr and Radarr API settings to MUMC
    #arrDict={'Radarr':'7878','Sonarr':'8989','Lidarr':'8686','Readarr':'8787'}
    arrDict={'Radarr':'7878','Sonarr':'8989'}

    #loop thru each *arr
    for arr in arrDict:
        #check if *arr_url and *arr_api_key exist
        if (('-' + arr.casefold() + '_url' in the_dict['argv']) and ('-' + arr.casefold() + '_api_key' in the_dict['argv'])):
            #create empty list
            arr_list=[]
            #loop thru each argv *arr instance
            for arr_url,arr_api_key in zip(the_dict['argv']['-' + arr.casefold() + '_url'],the_dict['argv']['-' + arr.casefold() + '_api_key']):
                #set url found to false
                arr_url_has_value=False
                #set api_key found to false
                arr_api_key_has_value=False
                #check if url is empty string or None
                if (not ((arr_url == '') or (arr_url == None))):
                    #set url found to true
                    arr_url_has_value=True
                #check if api_key is empty string or None
                if (not ((arr_api_key == '') or (arr_api_key == None))):
                    #set api_key found to true
                    arr_api_key_has_value=True
                #append url and api_key pair to arr_list
                arr_list.append({'enabled':(arr_url_has_value and arr_api_key_has_value),'url':arr_url,'api_key':arr_api_key})

            the_dict['admin_settings']['media_managers'][arr.casefold()]=arr_list

    #set REMOVE_FILES
    the_dict['advanced_settings']['REMOVE_FILES']=False

    #Build and save new yaml config file
    if (not (the_dict['advanced_settings']['UPDATE_CONFIG'])):
        yaml_configurationBuilder(the_dict)

        try:
            the_dict=getIsAnyMediaEnabled(the_dict)

            if (the_dict['all_media_disabled']):
                print_all_media_disabled(the_dict)

            strings_list_to_print=built_new_config_not_setup_to_delete_media('',the_dict)
            print_byType(strings_list_to_print,the_dict['advanced_settings']['console_controls']['warnings']['script']['show'],the_dict,the_dict['formatting'])

        #the exception
        except (AttributeError, ModuleNotFoundError):
            #something went wrong
            #mumc_config.yaml should have been created by now
            #we are here because the mumc_config.yaml file does not exist
            #this is either the first time the script is running or mumc_config.yaml file was deleted

            #raise error
            raise RuntimeError('\nConfigError: Cannot find or open mumc_config.yaml')

    else: #(the_dict['advanced_settings']['UPDATE_CONFIG']):
        yaml_configurationUpdater(the_dict,orig_dict)


#get user input needed to edit the mumc_config.yaml file
def edit_configuration_file(the_dict,orig_dict):
    #Did we get here from the -u command line argument?
      #If yes, then the_dict['advanced_settings']['UPDATE_CONFIG'] needs to be manually be set to True
    if (not (the_dict['advanced_settings']['UPDATE_CONFIG'])):
        the_dict['advanced_settings']['UPDATE_CONFIG']=True
    build_configuration_file(the_dict,orig_dict)