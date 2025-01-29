from mumc_modules.mumc_output import print_byType
from mumc_modules.mumc_setup_questions import get_brand,get_url,get_port,get_base,get_admin_username,get_admin_password,get_library_setup_behavior,get_library_matching_behavior,get_tag_name,get_show_disabled_users,get_user_and_library_selection_type,proceed_arr_setup,get_arr_url,get_arr_port,get_arr_base_url,get_arr_api
from mumc_modules.mumc_key_authentication import authenticate_user_by_name
from mumc_modules.mumc_versions import get_script_version
from mumc_modules.mumc_console_info import print_all_media_disabled,built_new_config_not_setup_to_delete_media
from mumc_modules.mumc_configuration_yaml import yaml_configurationBuilder
from mumc_modules.mumc_config_updater import yaml_configurationUpdater
from mumc_modules.mumc_config_skeleton import setYAMLConfigSkeleton
from mumc_modules.mumc_builder_userlibrary import get_users_and_libraries
from mumc_modules.mumc_init import getIsAnyMediaEnabled
from mumc_modules.mumc_blacklist_whitelist import get_opposing_listing_type


#get user input needed to build or edit the mumc_config.yaml file
def build_configuration_file(the_dict,orig_dict={}):

    print('----------------------------------------------------------------------------------------')
    print('Version: ' + get_script_version())
    the_dict['version']=get_script_version()

    #Building the config
    if (not the_dict['advanced_settings']['UPDATE_CONFIG']):
        print('----------------------------------------------------------------------------------------')
        #ask user for server brand (i.e. emby or jellyfin)
        the_dict['admin_settings']={}
        the_dict['admin_settings']['server']={}
        if ('-server_brand' in the_dict['argv']):
            the_dict['admin_settings']['server']['brand']=the_dict['argv']['-server_brand']
        else:
            the_dict['admin_settings']['server']['brand']=get_brand()
        the_dict['server_brand']=the_dict['admin_settings']['server']['brand']

        if ('-config_updater' in the_dict['argv']):
            the_dict['advanced_settings']['UPDATE_CONFIG']=the_dict['argv']['-config_updater']
        the_dict['UPDATE_CONFIG']=the_dict['advanced_settings']['UPDATE_CONFIG']
        the_dict=setYAMLConfigSkeleton(the_dict)
        the_dict['admin_settings']['server']['brand']=the_dict['server_brand']
        the_dict['advanced_settings']['UPDATE_CONFIG']=the_dict['UPDATE_CONFIG']
        the_dict.pop('server_brand')
        the_dict.pop('UPDATE_CONFIG')

        print('----------------------------------------------------------------------------------------')
        #ask user for server's url
        if ('-server_url' in the_dict['argv']):
            the_dict['url']=the_dict['argv']['-server_url']
        else:
            the_dict['url']=get_url()
        print('----------------------------------------------------------------------------------------')
        #ask user for the emby or jellyfin port number
        if ('-server_port' in the_dict['argv']):
            the_dict['port']=the_dict['argv']['-server_port']
        else:
            the_dict['port']=get_port()
        print('----------------------------------------------------------------------------------------')
        #ask user for base-url
        if ('-server_base_url' in the_dict['argv']):
            the_dict['base']=the_dict['argv']['-server_base_url']
        else:
            the_dict['base']=get_base(the_dict['admin_settings']['server']['brand'])
        #contruct FQDN
        if (len(str(the_dict['port'])) and len(str(the_dict['base']))):
            the_dict['admin_settings']['server']['url']=the_dict['url'] + ':' + str(the_dict['port']) + '/' + str(the_dict['base'])
        elif (len(str(the_dict['port'])) and (not len(str(the_dict['base'])))):
            the_dict['admin_settings']['server']['url']=the_dict['url'] + ':' + str(the_dict['port'])
        elif ((not len(str(the_dict['port']))) and len(str(the_dict['base']))):
            the_dict['admin_settings']['server']['url']=the_dict['url'] + '/' + str(the_dict['base'])
        else:
            the_dict['admin_settings']['server']['url']=the_dict['url']
        #Remove server, port, and base so they cannot be used later
        the_dict.pop('url')
        the_dict.pop('port')
        the_dict.pop('base')
        print('----------------------------------------------------------------------------------------')

        #define username and password so it can be popped later without generating an error
        the_dict['username']=None
        the_dict['password']=None

        #check if server_auth_key CMD option exists
        if ('-server_auth_key' in the_dict['argv']):
            the_dict['admin_settings']['server']['auth_key']=the_dict['argv']['-server_auth_key']

            if ('-server_admin_id' in the_dict['argv']):
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


    #store the opposing and matching listing types to be used in get_users_and_libraries()
    the_dict['opposing_listing_type']=get_opposing_listing_type(the_dict['admin_settings']['behavior']['list'])
    the_dict['matching_listing_type']=the_dict['admin_settings']['behavior']['list']

    #ask if users disabled in the GUI should be monitored; this also controls if they are shown during selection of monitored_users
    the_dict['admin_settings']['behavior']['users']={}
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
    the_dict['admin_settings']['users']=get_users_and_libraries(the_dict)

    print('----------------------------------------------------------------------------------------')

    #Add Sonarr and Radarr API settings to MUMC
    #arrDict={'Radarr':'7878','Sonarr':'8989','Lidarr':'8686','Readarr':'8787'}
    arrDict={'Radarr':'7878','Sonarr':'8989'}

    for arr in arrDict:
        #define *arr dict
        the_dict['admin_settings']['media_managers'][arr.casefold()]={}
        the_dict['admin_settings']['media_managers'][arr.casefold()]['enabled']=True
        the_dict[arr.casefold() + '_url']=None
        the_dict[arr.casefold() + '_port']=None
        the_dict[arr.casefold() + '_base_url']=None
        the_dict[arr.casefold() + '_api']=None

        if ('-' + arr.casefold() + '_url' in the_dict['argv']):
            #save *arr url command option
            the_dict[arr.casefold() + '_url']=the_dict['argv']['-' + arr.casefold() + '_url']

            if ('-' + arr.casefold() + '_port' in the_dict['argv']):
                #save *arr port command option
                the_dict[arr.casefold() + '_port']=the_dict['argv']['-' + arr.casefold() + '_port']
            else:
                #save *arr manual port input
                the_dict[arr.casefold() + '_port']=get_arr_port(arr,arrDict[arr])

            if ('-' + arr.casefold() + '_base_url' in the_dict['argv']):
                #save *arr base_url command option
                the_dict[arr.casefold() + '_base_url']=the_dict['argv']['-' + arr.casefold() + '_base_url']
            else:
                #save *arr manual base_url input
                the_dict[arr.casefold() + '_base_url']=get_arr_base_url(arr)

        elif ('-' + arr.casefold() + '_port' in the_dict['argv']):
            #save *arr manual url input
            the_dict[arr.casefold() + '_url']=get_arr_url(arr)

            #save *arr port command option
            the_dict[arr.casefold() + '_port']=the_dict['argv']['-' + arr.casefold() + '_port']

            if ('-' + arr.casefold() + '_base_url' in the_dict['argv']):
                #save *arr base_url command option
                the_dict[arr.casefold() + '_base_url']=the_dict['argv']['-' + arr.casefold() + '_base_url']
            else:
                #save *arr manual base_url input
                the_dict[arr.casefold() + '_base_url']=get_arr_base_url(arr)

        elif ('-' + arr.casefold() + '_base_url' in the_dict['argv']):
            #save *arr manual url input
            the_dict[arr.casefold() + '_url']=get_arr_url(arr)

            #save *arr manual port input
            the_dict[arr.casefold() + '_port']=get_arr_port(arr)

            #save *arr base_url command option
            the_dict[arr.casefold() + '_base_url']=the_dict['argv']['-' + arr.casefold() + '_base_url']

        elif ((not (('-d' in the_dict['argv']) or ('-container' in the_dict['argv']))) and (proceed_arr_setup(arr))):
            #save *arr manual url input
            the_dict[arr.casefold() + '_url']=get_arr_url(arr)

            #save *arr manual port input
            the_dict[arr.casefold() + '_port']=get_arr_port(arr,arrDict[arr])

            #save *arr manual base_url input
            the_dict[arr.casefold() + '_base_url']=get_arr_base_url(arr)

        else:
            #disable *arr
            the_dict['admin_settings']['media_managers'][arr.casefold()]['enabled']=False

        if (the_dict['admin_settings']['media_managers'][arr.casefold()]['enabled']):

            #contruct *arr FQDN
            if (len(str(the_dict[arr.casefold() + '_port'])) and len(str(the_dict[arr.casefold() + '_base_url']))):
                #*arr url with port and base url
                the_dict['admin_settings']['media_managers'][arr.casefold()]['url']=the_dict[arr.casefold() + '_url'] + ':' + str(the_dict[arr.casefold() + '_port']) + '/' + str(the_dict[arr.casefold() + '_base_url'])
            elif (len(str(the_dict[arr.casefold() + '_port'])) and (not len(str(the_dict[arr.casefold() + '_base_url'])))):
                #*arr url with port
                the_dict['admin_settings']['media_managers'][arr.casefold()]['url']=the_dict[arr.casefold() + '_url'] + ':' + str(the_dict[arr.casefold() + '_port'])
            elif ((not len(str(the_dict[arr.casefold() + '_port']))) and len(str(the_dict[arr.casefold() + '_base_url']))):
                #*arr url with base url
                the_dict['admin_settings']['media_managers'][arr.casefold()]['url']=the_dict[arr.casefold() + '_url'] + '/' + str(the_dict[arr.casefold() + '_base_url'])
            else:
                #*arr url
                the_dict['admin_settings']['media_managers'][arr.casefold()]['url']=the_dict[arr.casefold() + '_url']

            #get *arr API key
            if ('-' + arr.casefold() + '_api' in the_dict['argv']):
                #save *arr api command option
                the_dict['admin_settings']['media_managers'][arr.casefold()]['api_key']=the_dict['argv']['-' + arr.casefold() + '_api']
            elif (not (('-d' in the_dict['argv']) or ('-container' in the_dict['argv']))):
                #save *arr manual apiinput
                the_dict['admin_settings']['media_managers'][arr.casefold()]['api_key']=get_arr_api(arr)

        #Remove *arr_url, *arr_port, and *arr_api so they cannot be used later
        the_dict.pop(arr.casefold() + '_api')
        the_dict.pop(arr.casefold() + '_base_url')
        the_dict.pop(arr.casefold() + '_port')
        the_dict.pop(arr.casefold() + '_url')

        print('----------------------------------------------------------------------------------------')

    print('----------------------------------------------------------------------------------------')

    #set REMOVE_FILES
    the_dict['advanced_settings']['REMOVE_FILES']=False

    print('----------------------------------------------------------------------------------------')

    #Build and save new yaml config file
    if (not the_dict['advanced_settings']['UPDATE_CONFIG']):
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