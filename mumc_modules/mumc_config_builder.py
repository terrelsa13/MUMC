#!/usr/bin/env python3
import urllib.request as urlrequest
from collections import defaultdict
import json
import os
from mumc_config_defaults import get_default_config_values
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json,write_to_file,print_byType
from mumc_modules.mumc_url import requestURL
from mumc_modules.mumc_server_type import isJellyfinServer,isEmbyServer
from mumc_modules.mumc_config_questions import get_brand,get_url,get_port,get_base,get_admin_username,get_admin_password,get_library_setup_behavior,get_library_matching_behavior,get_tag_name
from mumc_modules.mumc_versions import get_script_version
from mumc_modules.mumc_console_info import print_all_media_disabled,build_new_config_setup_to_delete_media
from mumc_modules.mumc_configuration import mumc_configuration_builder
from mumc_modules.mumc_configuration_yaml import yaml_configurationBuilder
from mumc_modules.mumc_config_updater import yaml_configurationUpdater


#api call to get admin account authentication token
def get_authentication_key(the_dict):
    #login info
    values = {'Username' : the_dict['username'], 'Pw' : the_dict['password']}
    #DATA = urlparse.urlencode(values)
    #DATA = DATA.encode('ascii')
    DATA = convert2json(values)
    DATA = DATA.encode('utf-8')

    #works for both Emby and Jellyfin
    xAuth = 'Authorization'
    #assuming jellyfin will eventually change to this
    #if (isEmbyServer()):
        #xAuth = 'X-Emby-Authorization'
    #else #(isJellyfinServer()):
        #xAuth = 'X-Jellyfin-Authorization'

    headers = {xAuth : 'Emby UserId="' + the_dict['username']  + '", Client="mumc.py", Device="Multi-User Media Cleaner", DeviceId="MUMC", Version="' + get_script_version() + '", Token=""', 'Content-Type' : 'application/json'}

    req = urlrequest.Request(url=the_dict['server_url'] + '/Users/AuthenticateByName', data=DATA, method='POST', headers=headers)

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    data=requestURL(req, preConfigDebug, 'get_authentication_key', 3, the_dict)

    return(data['AccessToken'])


#Unpack library data structure from config
def user_lib_builder(json_lib_entry,the_dict,list_type):
    if (isinstance(json_lib_entry, str)):
        lib_json=json.loads(json_lib_entry)
    elif (isinstance(json_lib_entry, list)):
        lib_json=json_lib_entry
    built_user_id=[]
    built_user_name=[]
    built_libid=[]
    built_collectiontype=[]
    built_path=[]
    built_networkpath=[]
    built_selection=[]
    datapos=0

    #loop thru each monitored users library entries
    for currentUser in lib_json:
        libid_append=''
        collectiontype_append=''
        path_append=''
        networkpath_append=''
        selection_append=''
        libid_init=True
        collectiontype_init=True
        path_init=True
        networkpath_init=True
        selection_init=True
        #loop thru each key for this user
        for keySlots in currentUser:
            #Store userId
            if (keySlots == 'user_id'):
                built_user_id.append(currentUser[keySlots])
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log('\nBuilding library for user with Id: ' + currentUser[keySlots],3,the_dict)
            elif (keySlots == 'user_name'):
                built_user_name.append(currentUser[keySlots])
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nBuilding library for user with name: '" + currentUser[keySlots] + "'",3,the_dict)
            #Store library data
            else:
                if (keySlots == list_type):
                    xpos=0
                    #loop thru each library data item for this library
                    for keySlotLibDataEntry in currentUser[keySlots]:
                        for keySlotLibData in keySlotLibDataEntry:
                            #Store libId
                            if (keySlotLibData == 'libid'):
                                if ((libid_append == '') and (libid_init)):
                                    libid_append=currentUser[keySlots][xpos][keySlotLibData]
                                    libid_init=False
                                else:
                                    if not (currentUser[keySlots][xpos][keySlotLibData] == ''):
                                        libid_append=libid_append + ',' + currentUser[keySlots][xpos][keySlotLibData]
                                    else:
                                        libid_append=libid_append + ','
                                    libid_init=False
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log('\nLibrary Id: ' + str(currentUser[keySlots][xpos][keySlotLibData]),3,the_dict)
                            #Store collectionType
                            elif (keySlotLibData == 'collectiontype'):
                                if ((collectiontype_append == '') and (collectiontype_init)):
                                    collectiontype_append=currentUser[keySlots][xpos][keySlotLibData]
                                    collectiontype_init=False
                                else:
                                    if not (currentUser[keySlots][xpos][keySlotLibData] == ''):
                                        collectiontype_append=collectiontype_append + ',' + currentUser[keySlots][xpos][keySlotLibData]
                                    else:
                                        collectiontype_append=collectiontype_append + ','
                                    collectiontype_init=False
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nCollection Type: '" + currentUser[keySlots][xpos][keySlotLibData] + "'",3,the_dict)
                            #Store path
                            elif (keySlotLibData == 'path'):
                                if ((path_append == '') and (path_init)):
                                    path_append=currentUser[keySlots][xpos][keySlotLibData]
                                    path_init=False
                                else:
                                    if not (currentUser[keySlots][xpos][keySlotLibData] == ''):
                                        path_append=path_append + ',' + currentUser[keySlots][xpos][keySlotLibData]
                                    else:
                                        path_append=path_append + ','
                                    path_init=False
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nPath: '" + currentUser[keySlots][xpos][keySlotLibData] + "'",3,the_dict)
                            #Store networkPath
                            elif (keySlotLibData == 'networkpath'):
                                if ((networkpath_append == '') and (networkpath_init)):
                                    networkpath_append=currentUser[keySlots][xpos][keySlotLibData]
                                    networkpath_init=False
                                else:
                                    if not (currentUser[keySlots][xpos][keySlotLibData] == ''):
                                        networkpath_append=networkpath_append + ',' + currentUser[keySlots][xpos][keySlotLibData]
                                    else:
                                        networkpath_append=networkpath_append + ','
                                    networkpath_init=False
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nNetwork Path: '" + currentUser[keySlots][xpos][keySlotLibData] + "'",3,the_dict)
                            #Store networkPath
                            elif (keySlotLibData == 'selection'):
                                if ((selection_append == '') and (selection_init)):
                                    selection_append=str(currentUser[keySlots][xpos][keySlotLibData])
                                    selection_init=False
                                else:
                                    if not (currentUser[keySlots][xpos][keySlotLibData] == ''):
                                        selection_append=selection_append + ',' + str(currentUser[keySlots][xpos][keySlotLibData])
                                    else:
                                        selection_append=selection_append + ','
                                    selection_init=False
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nSelection: '" + str(currentUser[keySlots][xpos][keySlotLibData]) + "'",3,the_dict)
                        xpos+=1
        built_libid.insert(datapos,libid_append)
        built_collectiontype.insert(datapos,collectiontype_append)
        built_networkpath.insert(datapos,networkpath_append)
        built_path.insert(datapos,path_append)
        built_selection.insert(datapos,selection_append)
        datapos+=1
    return(built_user_id,built_user_name,built_libid,built_collectiontype,built_path,built_networkpath,built_selection)


def buildUserLibraries(the_dict):
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nBuilding Whitelisted Libraries...",2,the_dict)
    #Build the library data from the data structures stored in the configuration file
    wluser_keys_json_verify,wluser_names_json_verify,user_wllib_keys_json,user_wllib_collectiontype_json,user_wllib_path_json,user_wllib_netpath_json,user_wllib_seluser_wllib_selection_jsonection_json=user_lib_builder(the_dict['user_wl_libs'],the_dict,'whitelist')

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nBuilding Blacklisted Libraries...",2,the_dict)
    #Build the library data from the data structures stored in the configuration file
    bluser_keys_json_verify,bluser_names_json_verify,user_bllib_keys_json,user_bllib_collectiontype_json,user_bllib_path_json,user_bllib_netpath_json,user_bllib_selection_json=user_lib_builder(the_dict['user_bl_libs'],the_dict,'blacklist')

    #verify userIds are in same order for both blacklisted and whitelisted libraries
    if (wluser_keys_json_verify == bluser_keys_json_verify):
        user_keys_json = bluser_keys_json_verify
    else:
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both',2,the_dict)
        raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both')

    #verify userNames are in same order for both blacklisted and whitelisted libraries
    if (not (wluser_names_json_verify == bluser_names_json_verify)):
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both',2,the_dict)
        raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both')

    the_dict['wluser_keys_json_verify']=wluser_keys_json_verify
    the_dict['wluser_names_json_verify']=wluser_names_json_verify
    the_dict['user_wllib_keys_json']=user_wllib_keys_json
    the_dict['user_wllib_collectiontype_json']=user_wllib_collectiontype_json
    the_dict['user_wllib_path_json']=user_wllib_path_json
    the_dict['user_wllib_netpath_json']=user_wllib_netpath_json
    the_dict['user_wllib_selection_json']=user_wllib_selection_json

    the_dict['bluser_keys_json_verify']=bluser_keys_json_verify
    the_dict['bluser_names_json_verify']=bluser_names_json_verify
    the_dict['user_bllib_keys_json']=user_bllib_keys_json
    the_dict['user_bllib_collectiontype_json']=user_bllib_collectiontype_json
    the_dict['user_bllib_path_json']=user_bllib_path_json
    the_dict['user_bllib_netpath_json']=user_bllib_netpath_json
    the_dict['user_bllib_selection_json']=user_bllib_selection_json
    
    the_dict['user_keys_json']=user_keys_json

    the_dict['currentPosition']=0

    return the_dict


#Create output string to show library information to user for them to choose
def parse_library_data_for_display(libFolder,subLibPath,the_dict):

    if (isJellyfinServer(the_dict['server_brand'])):
        libraryGuid='ItemId'
    else:
        libraryGuid='Guid'

    libDisplayString=' - ' + libFolder['Name']

    if ('LibraryOptions' in libFolder):
        if ('PathInfos' in libFolder['LibraryOptions']):
            if not (len(libFolder['LibraryOptions']['PathInfos']) == 0):
                if ('Path' in libFolder['LibraryOptions']['PathInfos'][subLibPath]):
                    libDisplayString+=' - ' + libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path']
                if ('NetworkPath' in libFolder['LibraryOptions']['PathInfos'][subLibPath]):
                    libDisplayString+=' - ' + libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath']

    if (libraryGuid in libFolder):
        libDisplayString+=' - LibId: ' + libFolder[libraryGuid]

    return libDisplayString



#Store the chosen library's data in temporary location for use when building blacklist and whitelist
def parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,pos,the_dict):

    if (isJellyfinServer(the_dict['server_brand'])):
        libraryGuid='ItemId'
    else:
        libraryGuid='Guid'

    libraryTemp_dict[pos]['libid']=libFolder[libraryGuid]

    if ('CollectionType' in libFolder):
        libraryTemp_dict[pos]['collectiontype']=libFolder['CollectionType']
    else:
        libraryTemp_dict[pos]['collectiontype']='Unknown'

    if ('LibraryOptions' in libFolder):
        if ('PathInfos' in libFolder['LibraryOptions']):
            if not (len(libFolder['LibraryOptions']['PathInfos']) == 0):
                if ('Path' in libFolder['LibraryOptions']['PathInfos'][subLibPath]):
                    libraryTemp_dict[pos]['path']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path']
                else:
                    libraryTemp_dict[pos]['path']=''
                if ('NetworkPath' in libFolder['LibraryOptions']['PathInfos'][subLibPath]):
                    libraryTemp_dict[pos]['networkpath']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath']
                else:
                    libraryTemp_dict[pos]['networkpath']=''
            else:
                libraryTemp_dict[pos]['path']=''
                libraryTemp_dict[pos]['networkpath']=''
        else:
            libraryTemp_dict[pos]['path']=''
            libraryTemp_dict[pos]['networkpath']=''
    else:
        libraryTemp_dict[pos]['path']=''
        libraryTemp_dict[pos]['networkpath']=''

    return libraryTemp_dict


#Parse library Paths For Back Slash; Replace With Forward Slash
def cleanup_library_paths(libPath_str):
    libPath_str=libPath_str.replace('\\','/')
    return(libPath_str)


#API call to get library folders; choose which libraries to blacklist and whitelist
def get_library_folders(infotext, user_policy, user_id, user_name, mandatory, the_dict):
    #get all library paths for a given user

    #Request for libraries (i.e. movies, tvshows, audio, etc...)
    req_folders=(the_dict['server_url'] + '/Library/VirtualFolders?api_key=' + the_dict['auth_key'])

    #preConfigDebug = True
    preConfigDebug = False

    #api calls
    data_folders = requestURL(req_folders, preConfigDebug, 'get_media_folders', 3, the_dict)

    #define empty dictionaries
    libraryTemp_dict=defaultdict(dict)
    library_dict=defaultdict(dict)
    not_library_dict=defaultdict(dict)
    library_tracker=[]
    enabledFolderIds_set=set()

    #Check if this user has permission to access to all libraries or only specific libraries
    if not (user_policy['EnableAllFolders']):
        for okFolders in range(len(user_policy['EnabledFolders'])):
            enabledFolderIds_set.add(user_policy['EnabledFolders'][okFolders])

    i=0
    if (isJellyfinServer(the_dict['server_brand'])):
        libraryGuid='ItemId'
    else:
        libraryGuid='Guid'
    #Populate all libraries into a "not chosen" data structure
    # i.e. if blacklist chosen all libraries start out as whitelisted
    # i.e. if whitelist chosen all libraries start out as blacklisted
    for libFolder in data_folders:
        if ((libraryGuid in libFolder) and ('CollectionType' in libFolder) and ((enabledFolderIds_set == set()) or (libFolder[libraryGuid] in enabledFolderIds_set))):
            for subLibPath in range(len(libFolder['LibraryOptions']['PathInfos'])):
                if not ('userid' in not_library_dict):
                    not_library_dict['userid']=user_id
                if not ('username' in not_library_dict):
                    not_library_dict['username']=user_name
                not_library_dict[i]['libid']=libFolder[libraryGuid]
                not_library_dict[i]['collectiontype']=libFolder['CollectionType']
                if (('Path' in libFolder['LibraryOptions']['PathInfos'][subLibPath])):
                    not_library_dict[i]['path']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path']
                else:
                    not_library_dict[i]['path']=''
                if (('NetworkPath' in libFolder['LibraryOptions']['PathInfos'][subLibPath])):
                    not_library_dict[i]['networkpath']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath']
                else:
                    not_library_dict[i]['networkpath']=''
                i += 1

    #Go thru libaries this user has permissions to access and show them on the screen
    stop_loop=False
    first_run=True
    libInfoPrinted=False
    while (stop_loop == False):
        j=0
        k=0
        showpos_correlation={}
        for libFolder in data_folders:
            if ((libraryGuid in libFolder) and ('CollectionType' in libFolder) and ((enabledFolderIds_set == set()) or (libFolder[libraryGuid] in enabledFolderIds_set))):
                for subLibPath in range(len(libFolder['LibraryOptions']['PathInfos'])):
                    if ((the_dict['library_matching_behavior'] == 'byId') and (libraryGuid in libFolder)):
                        #option made here to check for either ItemId or Path when deciding what to show
                        # when ItemId libraries with multiple folders but same libId will be removed together
                        # when Path libraries with multiple folders but the same libId will be removed individually
                        if ((the_dict['library_matching_behavior'] == 'byId') and ( not (libFolder[libraryGuid] in library_tracker))):
                            print(str(j) + parse_library_data_for_display(libFolder,subLibPath,the_dict))
                            libInfoPrinted=True
                        else:
                            #show blank entry
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' )
                            libInfoPrinted=True
                        if not ('userid' in libraryTemp_dict):
                            libraryTemp_dict['userid']=user_id
                        libraryTemp_dict=parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,k,the_dict)
                    elif ((the_dict['library_matching_behavior'] == 'byPath') and ('Path' in libFolder['LibraryOptions']['PathInfos'][subLibPath])):
                        #option made here to check for either ItemId or Path when deciding what to show
                        # when ItemId libraries with multiple folders but same libId will be removed together
                        # when Path libraries with multiple folders but the same libId will be removed individually
                        if ((the_dict['library_matching_behavior'] == 'byPath') and ( not (libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path'] in library_tracker))):
                            print(str(j) + parse_library_data_for_display(libFolder,subLibPath,the_dict))
                            libInfoPrinted=True
                        else:
                            #show blank entry
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' )
                            libInfoPrinted=True
                        if not ('userid' in libraryTemp_dict):
                            libraryTemp_dict['userid']=user_id
                        libraryTemp_dict=parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,k,the_dict)
                    elif ((the_dict['library_matching_behavior'] == 'byNetworkPath') and ('NetworkPath' in libFolder['LibraryOptions']['PathInfos'][subLibPath])):
                        #option made here to check for either ItemId or Path when deciding what to show
                        # when ItemId libraries with multiple folders but same libId will be removed together
                        # when Path libraries with multiple folders but the same libId will be removed individually
                        if ((the_dict['library_matching_behavior'] == 'byNetworkPath') and ( not (libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath'] in library_tracker))):
                            print(str(j) + parse_library_data_for_display(libFolder,subLibPath,the_dict))
                            libInfoPrinted=True
                        else:
                            #show blank entry
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' )
                            libInfoPrinted=True
                        if not ('userid' in libraryTemp_dict):
                            libraryTemp_dict['userid']=user_id
                        libraryTemp_dict=parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,k,the_dict)
                    if (libInfoPrinted):
                        showpos_correlation[k]=j
                        k += 1
                    if (((the_dict['library_matching_behavior'] == 'byPath') or (the_dict['library_matching_behavior'] == 'byNetworkPath')) and (libInfoPrinted)):
                        libInfoPrinted=False
                        j += 1
                if ((the_dict['library_matching_behavior'] == 'byId') and (libInfoPrinted)):
                    libInfoPrinted=False
                    j += 1

        print('')

        #Wait for user input telling us which library they are have selected
        if (j >= 1):
            print(infotext)
            #Get user input for libraries
            if ((mandatory) and (first_run)):
                first_run=False
                path_number=input('Select one or more libraries.\n*Use a comma to separate multiple selections.\nMust select at least one library to monitor: ')
            elif (mandatory):
                path_number=input('Select one or more libraries.\n*Use a comma to separate multiple selections.\nLeave blank when finished: ')
            else:
                path_number=input('Select one or more libraries.\n*Use a comma to separate multiple selections.\nLeave blank for none or when finished: ')

        #Cleanup input to allow multiple library choices at the same time
        if not (path_number == ''):
            #replace spaces with commas (assuming people will use spaces because the space bar is bigger and easier to push)
            comma_path_number=path_number.replace(' ',',')
            #convert string to list
            list_path_number=comma_path_number.split(',')
            #remove blanks
            while ('' in list_path_number):
                list_path_number.remove('')
        else: #(path_number == ''):
            #convert string to list
            list_path_number=path_number.split(',')

        #loop thru user chosen libraries
        for input_path_number in list_path_number:
            try:
                if ((input_path_number == '') and (len(library_tracker) == 0) and (mandatory)):
                    print('\nMust select at least one library to monitor for this user. Try again.\n')
                elif (input_path_number == ''):
                    #Add valid library selecitons to the library dicitonary
                    if not ('userid' in library_dict):
                        library_dict['userid']=libraryTemp_dict['userid']
                    if not ('username' in library_dict):
                        library_dict['username']=user_name
                    stop_loop=True
                    print('')
                else:
                    print('')
                    path_number_float=float(input_path_number)
                    if ((path_number_float % 1) == 0):
                        path_number_int=int(path_number_float)
                        if ((path_number_int >= 0) and (path_number_int < j)):
                            #Add valid library selecitons to the library dicitonary
                            if not ('userid' in library_dict):
                                library_dict['userid']=libraryTemp_dict['userid']
                            if not ('username' in library_dict):
                                library_dict['username']=user_name
                            for showpos in showpos_correlation:
                                if (showpos_correlation[showpos] == path_number_int):
                                    for checkallpos in libraryTemp_dict:
                                        libMatchFound=False
                                        if not ((checkallpos == 'userid') or (checkallpos in library_dict)):
                                            if ((the_dict['library_matching_behavior'] == 'byId') and (libraryTemp_dict[showpos]['libid'] == libraryTemp_dict[checkallpos]['libid'])):
                                                libMatchFound=True
                                                library_dict[checkallpos]['libid']=libraryTemp_dict[checkallpos]['libid']
                                                library_dict[checkallpos]['collectiontype']=libraryTemp_dict[checkallpos]['collectiontype']
                                                library_dict[checkallpos]['path']=libraryTemp_dict[checkallpos]['path']
                                                library_dict[checkallpos]['networkpath']=libraryTemp_dict[checkallpos]['networkpath']
                                            elif ((the_dict['library_matching_behavior'] == 'byPath') and (libraryTemp_dict[showpos]['path'] == libraryTemp_dict[checkallpos]['path'])):
                                                libMatchFound=True
                                                library_dict[checkallpos]['libid']=libraryTemp_dict[checkallpos]['libid']
                                                library_dict[checkallpos]['collectiontype']=libraryTemp_dict[checkallpos]['collectiontype']
                                                library_dict[checkallpos]['path']=libraryTemp_dict[checkallpos]['path']
                                                library_dict[checkallpos]['networkpath']=libraryTemp_dict[checkallpos]['networkpath']
                                            elif ((the_dict['library_matching_behavior'] == 'byNetworkPath') and (libraryTemp_dict[showpos]['networkpath'] == libraryTemp_dict[checkallpos]['networkpath'])):
                                                libMatchFound=True
                                                library_dict[checkallpos]['libid']=libraryTemp_dict[checkallpos]['libid']
                                                library_dict[checkallpos]['collectiontype']=libraryTemp_dict[checkallpos]['collectiontype']
                                                library_dict[checkallpos]['path']=libraryTemp_dict[checkallpos]['path']
                                                library_dict[checkallpos]['networkpath']=libraryTemp_dict[checkallpos]['networkpath']

                                            if (libMatchFound):
                                                #The chosen library is removed from the "not chosen" data structure
                                                #Remove valid library selecitons from the not_library dicitonary
                                                if (checkallpos in not_library_dict):
                                                    if not ('username' in not_library_dict):
                                                        not_library_dict['username']=user_name
                                                    not_library_dict.pop(checkallpos)

                                                #The chosen library is added to the "chosen" data structure
                                                # Add library ID/Path to chosen list type behavior
                                                if (( not (library_dict[checkallpos].get('libid') == '')) and (the_dict['library_matching_behavior'] == 'byId')):
                                                    library_tracker.append(library_dict[checkallpos]['libid'])
                                                elif (( not (library_dict[checkallpos].get('path') == '')) and (the_dict['library_matching_behavior'] == 'byPath')):
                                                    library_tracker.append(library_dict[checkallpos]['path'])
                                                elif (( not (library_dict[checkallpos].get('networkpath') == '')) and (the_dict['library_matching_behavior'] == 'byNetworkPath')):
                                                    library_tracker.append(library_dict[checkallpos]['networkpath'])

                            #When all libraries selected we can automatically exit the library chooser
                            if (len(library_tracker) >= len(showpos_correlation)):
                                stop_loop=True
                                print('')
                            else:
                                stop_loop=False

                            if(preConfigDebug):
                                print('libraryTemp_dict = ' + str(libraryTemp_dict) + '\n')
                                print('library_dict = ' + str(library_dict) + '\n')
                                print('not_library_dict = ' + str(not_library_dict) + '\n')
                                print('library_tracker = ' + str(library_tracker) + '\n')

                        else:
                            print('\nIgnoring Out Of Range Value: ' + input_path_number + '\n')
                    else:
                        print('\nIgnoring Decimal Value: ' + input_path_number + '\n')
            except:
                print('\nIgnoring Non-Whole Number Value: ' + input_path_number + '\n')

    #Determine how many entries are in the "choosen" and "not choosen" data structures
    #When both have >1 parse both data structures
    if ((len(library_dict) > 2) and (len(not_library_dict) > 2)):
        for entry in library_dict:
            if not ((entry == 'userid') or (entry == 'username')):
                library_dict[entry]['path']=cleanup_library_paths(library_dict[entry].get('path'))
                library_dict[entry]['networkpath']=cleanup_library_paths(library_dict[entry].get('networkpath'))
        for entry in not_library_dict:
            if not ((entry == 'userid') or (entry == 'username')):
                not_library_dict[entry]['path']=cleanup_library_paths(not_library_dict[entry].get('path'))
                not_library_dict[entry]['networkpath']=cleanup_library_paths(not_library_dict[entry].get('networkpath'))
        #libraries for blacklist and whitelist
        return(not_library_dict,library_dict)
    #When only one is >1 parse that data structur
    elif ((len(library_dict) == 2) and (len(not_library_dict) > 2)):
        for entry in not_library_dict:
            if not ((entry == 'userid') or (entry == 'username')):
                not_library_dict[entry]['path']=cleanup_library_paths(not_library_dict[entry].get('path'))
                not_library_dict[entry]['networkpath']=cleanup_library_paths(not_library_dict[entry].get('networkpath'))
        #libraries for blacklist and whitelist
        return(not_library_dict,library_dict)
    #When only one is >1 parse that data structur
    elif ((len(library_dict) > 2) and (len(not_library_dict) == 2)):
        for entry in library_dict:
            if not ((entry == 'userid') or (entry == 'username')):
                library_dict[entry]['path']=cleanup_library_paths(library_dict[entry].get('path'))
                library_dict[entry]['networkpath']=cleanup_library_paths(library_dict[entry].get('networkpath'))
        #libraries for blacklist and whitelist
        return(not_library_dict,library_dict)
    #If both are somehow zero just return the data without parsing
    else: #((len(library_dict) == 0) and (len(not_library_dict) == 0)):
        #This should never happen
        #empty libraries for blacklist and whitelist
        return(not_library_dict,library_dict)


#API call to get all user accounts
#Choose account(s) this script will use to delete played media
#Choosen account(s) do NOT need to have "Allow Media Deletion From" enabled in the UI
def get_users_and_libraries(the_dict):
    #Get all users
    req=(the_dict['server_url'] + '/Users?api_key=' + the_dict['auth_key'])

    #preConfigDebug = True
    preConfigDebug = False

    #api call
    data=requestURL(req, preConfigDebug, 'get_users', 3, the_dict)

    #define empty userId dictionary
    userId_dict={}
    #define empty monitored library dictionary
    userId_bllib_dict={}
    #define empty whitelisted library dictionary
    userId_wllib_dict={}
    #define empty userId set
    userId_set=set()
    userId_ReRun_set=set()
    user_keys_json=''

    #Check if not running for the first time
    if (the_dict['UPDATE_CONFIG']):
        #Build the library data from the data structures stored in the configuration file
        bluser_keys_json_verify,bluser_names_json_verify,v,w,x,y,z=user_lib_builder(the_dict['user_bl_libs'],the_dict,'blacklist')
        #Build the library data from the data structures stored in the configuration file
        wluser_keys_json_verify,wluser_names_json_verify,v,w,x,y,z=user_lib_builder(the_dict['user_wl_libs'],the_dict,'whitelist')

        #verify userIds are in same order for both blacklist and whitelist libraries
        if (bluser_keys_json_verify == wluser_keys_json_verify):
            user_keys_json = bluser_keys_json_verify
        else:
            raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both')

        #verify userNames are in same order for both blacklist and whitelist libraries
        if (not (bluser_names_json_verify == wluser_names_json_verify)):
            raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userNames need to be in the same order for both')

        i=0
        #usernames_userkeys=json.loads(the_dict['user_keys'])
        usernames_userkeys=the_dict['user_names']
        #Pre-populate the existing userkeys and libraries; only new users are fully shown; existing user will display minimal info
        for rerun_userkey in user_keys_json:
            userId_set.add(rerun_userkey)
            if (rerun_userkey == bluser_keys_json_verify[i]):
                #userId_bllib_dict[rerun_userkey]=json.loads(cfg.user_bl_libs)[i]
                userId_bllib_dict[rerun_userkey]=the_dict['user_bl_libs'][i]
                #for usernames_userkeys_str in usernames_userkeys:
                    #usernames_userkeys_list=usernames_userkeys_str.split(":")
                    #if (len(usernames_userkeys_list) == 2):
                        #if (usernames_userkeys_list[1] == rerun_userkey):
                            #userId_bllib_dict[rerun_userkey]['username']=usernames_userkeys_list[0]
                userId_bllib_dict[rerun_userkey]['username']=usernames_userkeys[rerun_userkey]
                userId_bllib_dict[rerun_userkey]['userid']=rerun_userkey
                    #else:
                        #raise ValueError('\nUnable to edit config when username contains colon (:).')
            else:
                raise ValueError('\nValueError: Order of user_keys and user_wl libs are not in the same order.')
            if (rerun_userkey == wluser_keys_json_verify[i]):
                #userId_wllib_dict[rerun_userkey]=json.loads(cfg.user_wl_libs)[i]
                userId_wllib_dict[rerun_userkey]=the_dict['user_wl_libs'][i]
                #for usernames_userkeys_str in usernames_userkeys:
                    #usernames_userkeys_list=usernames_userkeys_str.split(":")
                    #if (len(usernames_userkeys_list) == 2):
                        #if (usernames_userkeys_list[1] == rerun_userkey):
                            #userId_wllib_dict[rerun_userkey]['username']=usernames_userkeys_list[0]
                userId_wllib_dict[rerun_userkey]['username']=usernames_userkeys[rerun_userkey]
                userId_wllib_dict[rerun_userkey]['userid']=rerun_userkey
                    #else:
                        #raise ValueError('\nUnable to edit config when username contains colon (:).')
            else:
                raise ValueError('\nValueError: Order of user_keys and user_bl libs are not in the same order.')
            i += 1

        #Uncomment if the config editor should only allow adding new users
        #This means the script will not allow editing exisitng users until a new user is added
        #if ((len(user_keys_json)) == (len(data))):
            #print('-----------------------------------------------------------')
            #print('No new user(s) found.')
            #print('-----------------------------------------------------------')
            #print('Verify new user(s) added to the Emby/Jellyfin server.')
            #return(userId_bllib_dict, userId_wllib_dict)

    stop_loop=False
    single_user=False
    one_user_selected = False
    #Loop until all user accounts selected or until manually stopped with a blank entry
    while (stop_loop == False):
        i=0
        #Determine if we are looking at a mulitple user setup or a single user setup
        if (len(data) > 1):
            for user in data:
                if not (user['Id'] in userId_set):
                    print(str(i) +' - '+ user['Name'] + ' - ' + user['Id'])
                    userId_dict[i]=user['Id']
                else:
                    #show blank entry
                    print(str(i) +' - '+ user['Name'] + ' - ')
                    userId_dict[i]=user['Id']
                i += 1
        else: #Single user setup
            single_user=True
            for user in data:
                userId_dict[i]=user['Id']

        print('')

        #When single user we can prepare to exit after their libraries are selected
        if ((i == 0) and (single_user == True)):
            user_number='0'
        #When multiple explain how to select each user
        elif ((i >= 1) and (one_user_selected == False)):
            user_number=input('Select one user at a time.\nEnter number of the user to monitor: ')
            print('')
        #When multiple explain how to select each user; when coming back to the user selection show this
        else: #((i >= 1) and (one_user_selected == True)):
            print('Monitoring multiple users is possible.')
            print('When multiple users are selected; the user with the oldest last played time will determine if media can be deleted.')
            user_number=input('Select one user at a time.\nEnter number of the next user to monitor; leave blank when finished: ')
            print('')

        try:
            #When single user we know the loop will stop right after libraries are chosen
            if ((user_number == '0') and (single_user == True)):
                stop_loop=True
                one_user_selected=True
                user_number_int=int(user_number)
                userId_set.add(userId_dict[user_number_int])

                #Depending on library setup behavior the chosen libraries will either be treated as blacklisted libraries or whitelisted libraries
                if (the_dict['library_setup_behavior'] == 'blacklist'):
                    message='Enter number of the library folder to blacklist (aka monitor) for the selected user.\nMedia in blacklisted library folder(s) will be monitored for deletion.'
                    userId_wllib_dict[userId_dict[user_number_int]],userId_bllib_dict[userId_dict[user_number_int]]=get_library_folders(message,data[user_number_int]['Policy'],data[user_number_int]['Id'],data[user_number_int]['Name'],False,the_dict)
                else: #(the_dict['library_setup_behavior'] == 'whitelist'):
                    message='Enter number of the library folder to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                    userId_bllib_dict[userId_dict[user_number_int]],userId_wllib_dict[userId_dict[user_number_int]]=get_library_folders(message,data[user_number_int]['Policy'],data[user_number_int]['Id'],data[user_number_int]['Name'],False,the_dict)

            #We get here when we are done selecting users to monitor
            elif ((user_number == '') and (not (len(userId_set) == 0))):
                stop_loop=True
                print('')
            #We get here if there are muliple users and we tried not to select any; at least one must be selected
            elif ((user_number == '') and (len(userId_set) == 0)):
                print('\nMust select at least one user. Try again.\n')
            #When multiple users we get here to allow selecting libraries for the specified user
            elif not (user_number == ''):
                user_number_float=float(user_number)
                if ((user_number_float % 1) == 0):
                    user_number_int=int(user_number_float)
                if ((user_number_int >= 0) and (user_number_int < i)):
                    one_user_selected=True
                    userId_set.add(userId_dict[user_number_int])
                    if (the_dict['UPDATE_CONFIG']):
                        userId_ReRun_set.add(userId_dict[user_number_int])

                    #Depending on library setup behavior the chosen libraries will either be treated as blacklisted libraries or whitelisted libraries
                    if (the_dict['library_setup_behavior'] == 'blacklist'):
                        message='Enter number of the library folder to blacklist (aka monitor) for the selected user.\nMedia in blacklisted library folder(s) will be monitored for deletion.'
                        userId_wllib_dict[userId_dict[user_number_int]],userId_bllib_dict[userId_dict[user_number_int]]=get_library_folders(message,data[user_number_int]['Policy'],data[user_number_int]['Id'],data[user_number_int]['Name'],False,the_dict)
                    else: #(the_dict['library_setup_behavior'] == 'whitelist'):
                        message='Enter number of the library folder to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                        userId_bllib_dict[userId_dict[user_number_int]],userId_wllib_dict[userId_dict[user_number_int]]=get_library_folders(message,data[user_number_int]['Policy'],data[user_number_int]['Id'],data[user_number_int]['Name'],False,the_dict)

                    if ((len(userId_set) >= i) and (not the_dict['UPDATE_CONFIG'])):
                        stop_loop=True
                    elif ((len(userId_ReRun_set) >= i) and (the_dict['UPDATE_CONFIG'])):
                        stop_loop=True
                    else:
                        stop_loop=False
                else:
                    print('\nInvalid value. Try again.\n')
            else:
                print('\nUnknown value. Try again.\n')
        except:
            print('\nException When Selecting User. Try again.\n')

    return(userId_bllib_dict, userId_wllib_dict)


#get user input needed to build or edit the mumc_config.py file
def build_configuration_file(cfg,the_dict):

    print('-----------------------------------------------------------')
    print('Version: ' + get_script_version())

    #Building the config
    if not (the_dict['UPDATE_CONFIG']):
        print('-----------------------------------------------------------')
        #ask user for server brand (i.e. emby or jellyfin)
        the_dict['server_brand']=get_brand()

        print('-----------------------------------------------------------')
        #ask user for server's url
        the_dict['server']=get_url()
        print('-----------------------------------------------------------')
        #ask user for the emby or jellyfin port number
        the_dict['port']=get_port()
        print('-----------------------------------------------------------')
        #ask user for url-base
        the_dict['server_base']=get_base(the_dict['server_brand'])
        if (len(the_dict['port'])):
            the_dict['server_url']=the_dict['server'] + ':' + the_dict['port'] + '/' + the_dict['server_base']
        else:
            the_dict['server_url']=the_dict['server'] + '/' + the_dict['server_base']
        print('-----------------------------------------------------------')

        #ask user for administrator username
        the_dict['username']=get_admin_username()
        print('-----------------------------------------------------------')
        #ask user for administrator password
        the_dict['password']=get_admin_password()
        print('-----------------------------------------------------------')
        #ask server for authentication key using administrator username and password
        the_dict['auth_key']=get_authentication_key(the_dict)

        #ask user how they want to choose libraries/folders
        the_dict['library_setup_behavior']=get_library_setup_behavior()
        print('-----------------------------------------------------------')

        #ask user how they want media items to be matched to libraries/folders
        the_dict['library_matching_behavior']=get_library_matching_behavior()
        print('-----------------------------------------------------------')

        #Initialize for compare with other tag to prevent using the same tag in both blacktag and whitetag
        the_dict['blacktag']=''
        the_dict['whitetag']=''

        #ask user for blacktag(s)
        the_dict['blacktag']=get_tag_name('blacktag',the_dict['whitetag'])
        print('-----------------------------------------------------------')

        #ask user for whitetag(s)
        the_dict['whitetag']=get_tag_name('whitetag',the_dict['blacktag'])
        print('-----------------------------------------------------------')

        #run the user and library selector; ask user to select user and associate desired libraries to be monitored for each
        the_dict['user_keys_and_bllibs'],the_dict['user_keys_and_wllibs']=get_users_and_libraries(the_dict)
        print('-----------------------------------------------------------')

        #set REMOVE_FILES
        the_dict['REMOVE_FILES']=False

    #Updating the config; Prepare to run the config editor
    else: #(Update_Config):
        print('-----------------------------------------------------------')
        #ask user how they want to choose libraries/folders
        #library_setup_behavior=get_library_setup_behavior(cfg.library_setup_behavior)
        cfg['admin_settings']['behavior']['list']=get_library_setup_behavior(cfg['admin_settings']['behavior']['list'].casefold())
        print('-----------------------------------------------------------')
        #ask user how they want media items to be matched to libraries/folders
        #library_matching_behavior=get_library_matching_behavior(cfg.library_matching_behavior.casefold())
        cfg['admin_settings']['behavior']['matching']=get_library_matching_behavior(cfg['admin_settings']['behavior']['matching'].casefold())
        print('-----------------------------------------------------------')
        #set auth_key to allow printing username next to userkey
        #auth_key=cfg.auth_key
        #run the user and library selector; ask user to select user and associate desired libraries to be monitored for each
        the_dict['user_keys_and_bllibs'],the_dict['user_keys_and_wllibs']=get_users_and_libraries(the_dict)

    userkeys_bllibs_list=[]
    userbllibs_list=[]
    userkeys_wllibs_list=[]
    userwllibs_list=[]

    #Attach userkeys to blacklist library data structure
    for userkey, userbllib in the_dict['user_keys_and_bllibs'].items():
        #Get all users
        userkeys_bllibs_list.append(userbllib['username'] + ':' + userkey)
        userbllibs_list.append(userbllib)

    #Attach userkeys to whitelist library data structure
    for userkey, userwllib in the_dict['user_keys_and_wllibs'].items():
        userkeys_wllibs_list.append(userwllib['username'] + ':' + userkey)
        userwllibs_list.append(userwllib)

    #Check each user has an entry in blacklists and whitelists
    # Then prep the data structure for writing to the config file
    if (userkeys_bllibs_list == userkeys_wllibs_list):
        the_dict['user_keys']=json.dumps(userkeys_bllibs_list)
        #user_keys=json.dumps(userkeys_wllibs_list) #Only need to dump userkeys once
        the_dict['user_bl_libs']=json.dumps(userbllibs_list)
        the_dict['user_wl_libs']=json.dumps(userwllibs_list)
    else:
        raise ValueError('Error! User key values do not match.')

    print('-----------------------------------------------------------')
    #Build the legacy config file
    #config_file=mumc_configuration_builder(cfg,the_dict)

    #Build and save yaml config file
    if not (the_dict['UPDATE_CONFIG']):
        yaml_configurationBuilder(the_dict)
    else: #(Update_Config):
        yaml_configurationUpdater(cfg,the_dict)

    #Save the legacy config file
    #write_to_file(config_file,os.path.join(the_dict['cwd'],the_dict['config_file_name']))

    #Check config editing was not requested
    if not (the_dict['UPDATE_CONFIG']):
        try:
            #when all *_condition_days config options are disabled print notification
            if (
                (get_default_config_values('played_filter_movie')[0] == -1) and
                (get_default_config_values('created_filter_movie')[0] == -1) and
                (get_default_config_values('played_filter_episode')[0] == -1) and
                (get_default_config_values('created_filter_episode')[0] == -1) and
                (get_default_config_values('played_filter_audio')[0] == -1) and
                (get_default_config_values('created_filter_audio')[0] == -1) and
                (get_default_config_values('played_filter_audiobook')[0] == -1) and
                (((isJellyfinServer(the_dict['server_brand'])) and (get_default_config_values('played_filter_audiobook')[0] == -1)) or (isEmbyServer(the_dict['server_brand']))) and
                (((isJellyfinServer(the_dict['server_brand'])) and (get_default_config_values('created_filter_audiobook')[0] == -1)) or (isEmbyServer(the_dict['server_brand'])))
                ):
                print_all_media_disabled(the_dict)

            try:
                strings_list_to_print=['']
                strings_list_to_print=build_new_config_setup_to_delete_media(strings_list_to_print,the_dict)
                print_byType(strings_list_to_print[0],the_dict['print_script_warning'],the_dict,the_dict['script_warnings_format'])
            except:
                the_dict['print_script_warning']=True
                the_dict['script_warnings_format']=['','','']
                strings_list_to_print=['']
                strings_list_to_print=build_new_config_setup_to_delete_media(strings_list_to_print,the_dict)
                print_byType(strings_list_to_print[0],the_dict['print_script_warning'],the_dict,the_dict['script_warnings_format'])

        #the exception
        except (AttributeError, ModuleNotFoundError):
            #something went wrong
            #mumc_config.py should have been created by now
            #we are here because the mumc_config.py file does not exist
            #this is either the first time the script is running or mumc_config.py file was deleted

            #raise error
            raise RuntimeError('\nConfigError: Cannot find or open mumc_config.py')


#get user input needed to edit the mumc_config.py file
def edit_configuration_file(cfg,config_dict):
    build_configuration_file(cfg,config_dict)