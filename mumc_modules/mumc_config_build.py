#!/usr/bin/env python3
import urllib.request as urlrequest
from collections import defaultdict
import json
import os
from mumc_config_defaults import get_default_config_values
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json,write_to_file
from mumc_modules.mumc_url import requestURL
from mumc_modules.mumc_server_type import isJellyfinServer,isEmbyServer
from mumc_modules.mumc_config_questions import get_brand,get_url,get_port,get_base,get_admin_username,get_admin_password,get_library_setup_behavior,get_library_matching_behavior,get_tag_name
from mumc_modules.mumc_versions import get_script_version


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
def user_lib_builder(json_lib_entry,the_dict):
    if (isinstance(json_lib_entry, str)):
        lib_json=json.loads(json_lib_entry)
    elif (isinstance(json_lib_entry, list)):
        lib_json=json_lib_entry
    built_userid=[]
    built_username=[]
    built_libid=[]
    built_collectiontype=[]
    built_networkpath=[]
    built_path=[]
    datapos=0

    #loop thru each monitored users library entries
    for currentUser in lib_json:
        libid_append=''
        collectiontype_append=''
        networkpath_append=''
        path_append=''
        libid_init=True
        collectiontype_init=True
        networkpath_init=True
        path_init=True
        #loop thru each key for this user
        for keySlots in currentUser:
            #Store userId
            if (keySlots == 'userid'):
                built_userid.append(currentUser[keySlots])
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log('\nBuilding library for user with Id: ' + currentUser[keySlots],3,the_dict)
            elif (keySlots == 'username'):
                built_username.append(currentUser[keySlots])
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nBuilding library for user with name: '" + currentUser[keySlots] + "'",3,the_dict)
            #Store library data
            else:
                #loop thru each library data item for this library
                for keySlotLibData in currentUser[keySlots]:
                    #Store libId
                    if (keySlotLibData == 'libid'):
                        if ((libid_append == '') and (libid_init)):
                            libid_append=currentUser[keySlots][keySlotLibData]
                            libid_init=False
                        else:
                            if not (currentUser[keySlots][keySlotLibData] == ''):
                                libid_append=libid_append + ',' + currentUser[keySlots][keySlotLibData]
                            else:
                                libid_append=libid_append + ','
                            libid_init=False
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log('\nLibrary Id: ' + currentUser[keySlots][keySlotLibData],3,the_dict)
                    #Store collectionType
                    elif (keySlotLibData == 'collectiontype'):
                        if ((collectiontype_append == '') and (collectiontype_init)):
                            collectiontype_append=currentUser[keySlots][keySlotLibData]
                            collectiontype_init=False
                        else:
                            if not (currentUser[keySlots][keySlotLibData] == ''):
                                collectiontype_append=collectiontype_append + ',' + currentUser[keySlots][keySlotLibData]
                            else:
                                collectiontype_append=collectiontype_append + ','
                            collectiontype_init=False
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log("\nCollection Type: '" + currentUser[keySlots][keySlotLibData] + "'",3,the_dict)
                    #Store path
                    elif (keySlotLibData == 'path'):
                        if ((path_append == '') and (path_init)):
                            path_append=currentUser[keySlots][keySlotLibData]
                            path_init=False
                        else:
                            if not (currentUser[keySlots][keySlotLibData] == ''):
                                path_append=path_append + ',' + currentUser[keySlots][keySlotLibData]
                            else:
                                path_append=path_append + ','
                            path_init=False
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log("\nPath: '" + currentUser[keySlots][keySlotLibData] + "'",3,the_dict)
                    #Store networkPath
                    elif (keySlotLibData == 'networkpath'):
                        if ((networkpath_append == '') and (networkpath_init)):
                            networkpath_append=currentUser[keySlots][keySlotLibData]
                            networkpath_init=False
                        else:
                            if not (currentUser[keySlots][keySlotLibData] == ''):
                                networkpath_append=networkpath_append + ',' + currentUser[keySlots][keySlotLibData]
                            else:
                                networkpath_append=networkpath_append + ','
                            networkpath_init=False
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log("\nNetwork Path: '" + currentUser[keySlots][keySlotLibData] + "'",3,the_dict)
        built_libid.insert(datapos,libid_append)
        built_collectiontype.insert(datapos,collectiontype_append)
        built_path.insert(datapos,path_append)
        built_networkpath.insert(datapos,networkpath_append)
        datapos+=1
    return(built_userid,built_username,built_libid,built_collectiontype,built_networkpath,built_path)


def buildUserLibraries(the_dict):
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nBuilding Blacklisted Libraries...",2,the_dict)
    #Build the library data from the data structures stored in the configuration file
    bluser_keys_json_verify,bluser_names_json_verify,user_bllib_keys_json,user_bllib_collectiontype_json,user_bllib_netpath_json,user_bllib_path_json=user_lib_builder(the_dict['user_bl_libs'],the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nBuilding Whitelisted Libraries...",2,the_dict)
    #Build the library data from the data structures stored in the configuration file
    wluser_keys_json_verify,wluser_names_json_verify,user_wllib_keys_json,user_wllib_collectiontype_json,user_wllib_netpath_json,user_wllib_path_json=user_lib_builder(the_dict['user_wl_libs'],the_dict)

    #verify userIds are in same order for both blacklisted and whitelisted libraries
    if (bluser_keys_json_verify == wluser_keys_json_verify):
        user_keys_json = bluser_keys_json_verify
    else:
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both',2,the_dict)
        raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both')

    #verify userNames are in same order for both blacklisted and whitelisted libraries
    if (not (bluser_names_json_verify == wluser_names_json_verify)):
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both',2,the_dict)
        raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both')

    the_dict['bluser_keys_json_verify']=bluser_keys_json_verify
    the_dict['bluser_names_json_verify']=bluser_names_json_verify
    the_dict['user_bllib_keys_json']=user_bllib_keys_json
    the_dict['user_bllib_collectiontype_json']=user_bllib_collectiontype_json
    the_dict['user_bllib_netpath_json']=user_bllib_netpath_json
    the_dict['user_bllib_path_json']=user_bllib_path_json
    the_dict['wluser_keys_json_verify']=wluser_keys_json_verify
    the_dict['wluser_names_json_verify']=wluser_names_json_verify
    the_dict['user_wllib_keys_json']=user_wllib_keys_json
    the_dict['user_wllib_collectiontype_json']=user_wllib_collectiontype_json
    the_dict['user_wllib_netpath_json']=user_wllib_netpath_json
    the_dict['user_wllib_path_json']=user_wllib_path_json
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
        bluser_keys_json_verify,bluser_names_json_verify,w,x,y,z=user_lib_builder(the_dict['user_bl_libs'],the_dict)
        #Build the library data from the data structures stored in the configuration file
        wluser_keys_json_verify,wluser_names_json_verify,w,x,y,z=user_lib_builder(the_dict['user_wl_libs'],the_dict)

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
        usernames_userkeys=the_dict['user_keys']
        #Pre-populate the existing userkeys and libraries; only new users are fully shown; existing user will display minimal info
        for rerun_userkey in user_keys_json:
            userId_set.add(rerun_userkey)
            if (rerun_userkey == bluser_keys_json_verify[i]):
                #userId_bllib_dict[rerun_userkey]=json.loads(cfg.user_bl_libs)[i]
                userId_bllib_dict[rerun_userkey]=the_dict['user_bl_libs'][i]
                for usernames_userkeys_str in usernames_userkeys:
                    usernames_userkeys_list=usernames_userkeys_str.split(":")
                    if (len(usernames_userkeys_list) == 2):
                        if (usernames_userkeys_list[1] == rerun_userkey):
                            userId_bllib_dict[rerun_userkey]['username']=usernames_userkeys_list[0]
                    else:
                        raise ValueError('\nUnable to edit config when username contains colon (:).')
            else:
                raise ValueError('\nValueError: Order of user_keys and user_wl libs are not in the same order.')
            if (rerun_userkey == wluser_keys_json_verify[i]):
                #userId_wllib_dict[rerun_userkey]=json.loads(cfg.user_wl_libs)[i]
                userId_wllib_dict[rerun_userkey]=the_dict['user_wl_libs'][i]
                for usernames_userkeys_str in usernames_userkeys:
                    usernames_userkeys_list=usernames_userkeys_str.split(":")
                    if (len(usernames_userkeys_list) == 2):
                        if (usernames_userkeys_list[1] == rerun_userkey):
                            userId_wllib_dict[rerun_userkey]['username']=usernames_userkeys_list[0]
                    else:
                        raise ValueError('\nUnable to edit config when username contains colon (:).')
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
        the_dict['library_setup_behavior']=get_library_setup_behavior(None)
        print('-----------------------------------------------------------')

        #ask user how they want media items to be matched to libraries/folders
        the_dict['library_matching_behavior']=get_library_matching_behavior(None)
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
        the_dict['library_setup_behavior']=get_library_setup_behavior(the_dict['library_setup_behavior'])
        print('-----------------------------------------------------------')
        #ask user how they want media items to be matched to libraries/folders
        #library_matching_behavior=get_library_matching_behavior(cfg.library_matching_behavior.lower())
        the_dict['library_matching_behavior']=get_library_matching_behavior(the_dict['library_matching_behavior'].lower())
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
        user_keys=json.dumps(userkeys_bllibs_list)
        #user_keys=json.dumps(userkeys_wllibs_list) #Only need to dump userkeys once
        user_bl_libs=json.dumps(userbllibs_list)
        user_wl_libs=json.dumps(userwllibs_list)
    else:
        raise ValueError('Error! User key values do not match.')

    print('-----------------------------------------------------------')
    config_file=''
    config_file += "#-------------Basic Config Options Start Here---------------#\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Played Filter Statements\n"
    config_file += "#\n"
    config_file += "# [A,B,C]\n"
    config_file += "#\n"
    config_file += "# A - Condition Days\n"
    config_file += "# B - Played Count Inequality\n"
    config_file += "# C - Played Count\n"
    config_file += "#\n"
    config_file += "# Condition Days (A): Find media items last played at least this many days ago\n"
    config_file += "#   0-730500 - Number of days filter will use to determine when the media item was last played\n"
    config_file += "#  -1 - To disable deleting specified media type\n"
    config_file += "#\n"
    config_file += "# Played Count Inequality (B): Delete media items within this range based off of the chosen *_played_count.\n"
    config_file += "#   > - Filter media items with a played count greater than *_played_count days ago\n"
    config_file += "#   < - Filter media items with a played count less than *_played_count days ago\n"
    config_file += "#   >= - Filter media items with a played count greater than or equal to *_played_count days ago\n"
    config_file += "#   <= - Filter media items with a played count less than or equal to *_played_count days ago\n"
    config_file += "#   == - Filter media items with a played count equal to *_played_count days ago\n"
    config_file += "#   not > - Filter media items with a played count not greater than *_played_count days ago\n"
    config_file += "#   not < - Filter media items with a played count not less than *_played_count days ago\n"
    config_file += "#   not >= - Filter media items with a played count not greater than or equal to *_played_count days ago\n"
    config_file += "#   not <= - Filter media items with a played count not less than or equal to *_played_count days ago\n"
    config_file += "#   not == - Filter media items with a played count not equal to *_played_count days ago\n"
    config_file += "#\n"
    config_file += "# Played Count (C): Find media items with a played count relative to this number.\n"
    config_file += "#   1-730500 - Number of times a media item has been played\n"
    config_file += "#\n"
    config_file += "# ([-1,'>=',1] : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "played_filter_movie=" + str(get_default_config_values('played_filter_movie')) + "\n"
        config_file += "played_filter_episode=" + str(get_default_config_values('played_filter_episode')) + "\n"
        config_file += "played_filter_audio=" + str(get_default_config_values('played_filter_audio')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "played_filter_audiobook=" + str(get_default_config_values('played_filter_audiobook')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "played_filter_movie=" + str(cfg.played_filter_movie) + "\n"
        config_file += "played_filter_episode=" + str(cfg.played_filter_episode) + "\n"
        config_file += "played_filter_audio=" + str(cfg.played_filter_audio) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "played_filter_audiobook=" + str(cfg.played_filter_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Created Filter Statements\n"
    config_file += "#\n"
    config_file += "# [A,B,C,D]\n"
    config_file += "#\n"
    config_file += "# A - Condition Days\n"
    config_file += "# B - Played Count Inequality\n"
    config_file += "# C - Played Count\n"
    config_file += "# D - Behaviorial Control\n"
    config_file += "#\n"
    config_file += "# Condition Days (A): Find media items created at least this many days ago\n"
    config_file += "#   0-730500 - Number of days filter will use to determine when the media item was created\n"
    config_file += "#  -1 - To disable deleting specified media type\n"
    config_file += "#\n"
    config_file += "# Played Count Inequality (B): Delete media items within this range based off of the chosen *_played_count.\n"
    config_file += "#   > - Filter media items with a played count greater than *_played_count days ago\n"
    config_file += "#   < - Filter media items with a played count less than *_played_count days ago\n"
    config_file += "#   >= - Filter media items with a played count greater than or equal to *_played_count days ago\n"
    config_file += "#   <= - Filter media items with a played count less than or equal to *_played_count days ago\n"
    config_file += "#   == - Filter media items with a played count equal to *_played_count days ago\n"
    config_file += "#   not > - Filter media items with a played count not greater than *_played_count days ago\n"
    config_file += "#   not < - Filter media items with a played count not less than *_played_count days ago\n"
    config_file += "#   not >= - Filter media items with a played count not greater than or equal to *_played_count days ago\n"
    config_file += "#   not <= - Filter media items with a played count not less than or equal to *_played_count days ago\n"
    config_file += "#   not == - Filter media items with a played count not equal to *_played_count days ago\n"
    config_file += "#\n"
    config_file += "# Played Count (C): Find media items with a played count relative to this number.\n"
    config_file += "#   0-730500 - Number of times a media item has been played\n"
    config_file += "#\n"
    config_file += "# Behavioral Control (D): Determine if favorited_behavior_*, whitetagged_behavior_*, blacktagged_behavior_*,\n"
    config_file += "#  whitelisted_behavior_*, and blacklisted_behavior_* apply to media items meeting the created_filter_*.\n"
    config_file += "#   False - Media items meeting the created_filter_* will be deleted regardless of favorited_behavior_*,\n"
    config_file += "#    whitetagged_behavior_*, blacktagged_behavior_*, whitelisted_behavior_*, and blacklisted_behavior_*\n"
    config_file += "#   True - Media items meeting the created_filter_* will also have to meet configured behaviors; favorited_behavior_*,\n"
    config_file += "#    whitetagged_behavior_*, blacktagged_behavior_*, whitelisted_behavior_*, and blacklisted_behavior_*\n"
    config_file += "#\n"
    config_file += "# ([-1,'>=',1,True] : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "created_filter_movie=" + str(get_default_config_values('created_filter_movie')) + "\n"
        config_file += "created_filter_episode=" + str(get_default_config_values('created_filter_episode')) + "\n"
        config_file += "created_filter_audio=" + str(get_default_config_values('created_filter_audio')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "created_filter_audiobook=" + str(get_default_config_values('created_filter_audiobook')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "created_filter_movie=" + str(cfg.created_filter_movie) + "\n"
        config_file += "created_filter_episode=" + str(cfg.created_filter_episode) + "\n"
        config_file += "created_filter_audio=" + str(cfg.created_filter_audio) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "created_filter_audiobook=" + str(cfg.created_filter_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#------------Advanced Config Options Start Here-------------#\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Favorited Behavioral Statements\n"
    config_file += "#\n"
    config_file += "# Favoriting is the first (and highest) priority\n"
    config_file += "#  Whitetagging behavior is ignored\n"
    config_file += "#  Blacktagging behavior is ignored\n"
    config_file += "#  Whitelisting behavior is ignored\n"
    config_file += "#  Blacklisting behavior is ignored\n"
    config_file += "#\n"
    config_file += "# [W, X, Y, Z]\n"
    config_file += "#\n"
    config_file += "# W - Action\n"
    config_file += "# X - User Conditional\n"
    config_file += "# Y - Played Conditional\n"
    config_file += "# Z - Action Control\n"
    config_file += "#\n"
    config_file += "# Action (W): Specify which action should be taken when (X) and (Y) is True.\n"
    config_file += "#   delete - Delete media item from server\n"
    config_file += "#   keep - Do NOT delete media item from server\n"
    config_file += "#\n"
    config_file += "# User Conditional (X): Specify how monitored users must have the media item favorited.\n"
    config_file += "#   all - Every monitored user must have the media item favorited\n"
    config_file += "#   any - One or more monitored users must have the media item favorited\n"
    config_file += "#\n"
    config_file += "# Played Conditional (Y): Specify how monitored users must meet played_filter_*.\n"
    config_file += "#   all - Every monitored user must meet the played_filter_*\n"
    config_file += "#   any - One or more monitored users must meet the played_filter_*\n"
    config_file += "#   ignore - Ignore if monitored users meet the played_filter_*\n"
    config_file += "#\n"
    config_file += "# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False\n"
    config_file += "#   0 - No action taken on True; No action taken on False (disabled)\n"
    config_file += "#   1 - No action taken on True; Action taken on False\n"
    config_file += "#   2 - No action taken on True; Opposite action taken on False\n"
    config_file += "#   3 - Action taken on True; No action taken on False (recommended)\n"
    config_file += "#   4 - Action taken on True; Action taken on False\n"
    config_file += "#   5 - Action taken on True; Opposite action taken on False (recommended)\n"
    config_file += "#   6 - Opposite action taken on True; No action taken on False\n"
    config_file += "#   7 - Opposite action taken on True; Action taken on False\n"
    config_file += "#   8 - Opposite action taken on True; Opposite action taken on False\n"
    config_file += "#\n"
    config_file += "# (['keep','any','ignore',3] : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "favorited_behavior_movie=" + str(get_default_config_values('favorited_behavior_movie')) + "\n"
        config_file += "favorited_behavior_episode=" + str(get_default_config_values('favorited_behavior_episode')) + "\n"
        config_file += "favorited_behavior_audio=" + str(get_default_config_values('favorited_behavior_audio')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "favorited_behavior_audiobook=" + str(get_default_config_values('favorited_behavior_audiobook')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "favorited_behavior_movie=" + str(cfg.favorited_behavior_movie) + "\n"
        config_file += "favorited_behavior_episode=" + str(cfg.favorited_behavior_episode) + "\n"
        config_file += "favorited_behavior_audio=" + str(cfg.favorited_behavior_audio) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "favorited_behavior_audiobook=" + str(cfg.favorited_behavior_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Advanced movie favorites configurations\n"
    config_file += "#     Requires 'favorited_behavior_movie[3]>=0'\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "#  Keep movie based on the genres\n"
    config_file += "#  0 - ok to delete movie when genres are set as a favorite\n"
    config_file += "#  1 - keep movie if FIRST genre listed is set as a favorite\n"
    config_file += "#  2 - keep movie if ANY genre listed is set as a favorite\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "favorited_advanced_movie_genre=" + str(get_default_config_values('favorited_advanced_movie_genre')) + "\n"
        config_file += "favorited_advanced_movie_library_genre=" + str(get_default_config_values('favorited_advanced_movie_library_genre')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "favorited_advanced_movie_genre=" + str(cfg.favorited_advanced_movie_genre) + "\n"
        config_file += "favorited_advanced_movie_library_genre=" + str(cfg.favorited_advanced_movie_library_genre) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Advanced episode favorites configurations\n"
    config_file += "#     Requires 'favorited_behavior_episode[3]>=0'\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "#  Keep episode based on the genre(s) or studio-network(s)\n"
    config_file += "#  0 - ok to delete episode when its genres or studio-networks are set as a favorite\n"
    config_file += "#  1 - keep episode if FIRST genre or studio-network is set as a favorite\n"
    config_file += "#  2 - keep episode if ANY genres or studio-networks are set as a favorite\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "favorited_advanced_episode_genre=" + str(get_default_config_values('favorited_advanced_episode_genre')) + "\n"
        config_file += "favorited_advanced_season_genre=" + str(get_default_config_values('favorited_advanced_season_genre')) + "\n"
        config_file += "favorited_advanced_series_genre=" + str(get_default_config_values('favorited_advanced_series_genre')) + "\n"
        config_file += "favorited_advanced_tv_library_genre=" + str(get_default_config_values('favorited_advanced_tv_library_genre')) + "\n"
        config_file += "favorited_advanced_tv_studio_network=" + str(get_default_config_values('favorited_advanced_tv_studio_network')) + "\n"
        config_file += "favorited_advanced_tv_studio_network_genre=" + str(get_default_config_values('favorited_advanced_tv_studio_network_genre')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "favorited_advanced_episode_genre=" + str(cfg.favorited_advanced_episode_genre) + "\n"
        config_file += "favorited_advanced_season_genre=" + str(cfg.favorited_advanced_season_genre) + "\n"
        config_file += "favorited_advanced_series_genre=" + str(cfg.favorited_advanced_series_genre) + "\n"
        config_file += "favorited_advanced_tv_library_genre=" + str(cfg.favorited_advanced_tv_library_genre) + "\n"
        config_file += "favorited_advanced_tv_studio_network=" + str(cfg.favorited_advanced_tv_studio_network) + "\n"
        config_file += "favorited_advanced_tv_studio_network_genre=" + str(cfg.favorited_advanced_tv_studio_network_genre) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Advanced track favorites configurations\n"
    config_file += "#     Requires 'favorited_behavior_audio[3]>=0'\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "#  Keep track based on the genre(s) or artist(s)\n"
    config_file += "#  0 - ok to delete track when its genres or artists are set as a favorite\n"
    config_file += "#  1 - keep track if FIRST genre or artist is set as a favorite\n"
    config_file += "#  2 - keep track if ANY genres or artists are set as a favorite\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "favorited_advanced_track_genre=" + str(get_default_config_values('favorited_advanced_track_genre')) + "\n"
        config_file += "favorited_advanced_album_genre=" + str(get_default_config_values('favorited_advanced_album_genre')) + "\n"
        config_file += "favorited_advanced_music_library_genre=" + str(get_default_config_values('favorited_advanced_music_library_genre')) + "\n"
        config_file += "favorited_advanced_track_artist=" + str(get_default_config_values('favorited_advanced_track_artist')) + "\n"
        config_file += "favorited_advanced_album_artist=" + str(get_default_config_values('favorited_advanced_album_artist')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "favorited_advanced_track_genre=" + str(cfg.favorited_advanced_track_genre) + "\n"
        config_file += "favorited_advanced_album_genre=" + str(cfg.favorited_advanced_album_genre) + "\n"
        config_file += "favorited_advanced_music_library_genre=" + str(cfg.favorited_advanced_music_library_genre) + "\n"
        config_file += "favorited_advanced_track_artist=" + str(cfg.favorited_advanced_track_artist) + "\n"
        config_file += "favorited_advanced_album_artist=" + str(cfg.favorited_advanced_album_artist) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    if (isJellyfinServer(the_dict['server_brand'])):
        config_file += "\n"
        config_file += "#----------------------------------------------------------#\n"
        config_file += "# Advanced audio book favorites configurations\n"
        config_file += "#     Requires 'favorited_behavior_audiobook[3]>=0'\n"
        config_file += "#----------------------------------------------------------#\n"
        config_file += "#  Keep audio book track based on the genres or authors\n"
        config_file += "#  0 - ok to delete audio book track when its genres or authors are set as a favorite\n"
        config_file += "#  1 - keep audio book track if FIRST genre or author is set as a favorite\n"
        config_file += "#  2 - keep audio book track if ANY genres or authors are set as a favorite\n"
        config_file += "# (0 : default)\n"
        config_file += "#----------------------------------------------------------#\n"
        if not (the_dict['UPDATE_CONFIG']):
            config_file += "favorited_advanced_audiobook_track_genre=" + str(get_default_config_values('favorited_advanced_audiobook_track_genre')) + "\n"
            config_file += "favorited_advanced_audiobook_genre=" + str(get_default_config_values('favorited_advanced_audiobook_genre')) + "\n"
            config_file += "favorited_advanced_audiobook_library_genre=" + str(get_default_config_values('favorited_advanced_audiobook_library_genre')) + "\n"
            config_file += "favorited_advanced_audiobook_track_author=" + str(get_default_config_values('favorited_advanced_audiobook_track_author')) + "\n"
            config_file += "favorited_advanced_audiobook_author=" + str(get_default_config_values('favorited_advanced_audiobook_author')) + "\n"
        elif (the_dict['UPDATE_CONFIG']):
            config_file += "favorited_advanced_audiobook_track_genre=" + str(cfg.favorited_advanced_audiobook_track_genre) + "\n"
            config_file += "favorited_advanced_audiobook_genre=" + str(cfg.favorited_advanced_audiobook_genre) + "\n"
            config_file += "favorited_advanced_audiobook_library_genre=" + str(cfg.favorited_advanced_audiobook_library_genre) + "\n"
            config_file += "favorited_advanced_audiobook_track_author=" + str(cfg.favorited_advanced_audiobook_track_author) + "\n"
            config_file += "favorited_advanced_audiobook_author=" + str(cfg.favorited_advanced_audiobook_author) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# User entered whitetag name; chosen during setup\n"
    config_file += "#  Use a comma \',\' to seperate multiple tag names\n"
    config_file += "#   Ex: tagname,tag name,tag-name\n"
    config_file += "#  Backslash \'\\\' not allowed\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "whitetag='" + the_dict['whitetag'] + "'\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "whitetag='" + cfg.whitetag + "'\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Whitetagged Behavioral Statements\n"
    config_file += "#  Tags applied to a media item are seen by all users\n"
    config_file += "#\n"
    config_file += "# Whitetagging is the second priority\n"
    config_file += "#  Blacktagging behavior is ignored\n"
    config_file += "#  Whitelisting behavior is ignored\n"
    config_file += "#  Blacklisting behavior is ignored\n"
    config_file += "#\n"
    config_file += "# [W, X, Y, Z]\n"
    config_file += "#\n"
    config_file += "# W - Action\n"
    config_file += "# X - User Conditional\n"
    config_file += "# Y - Played Conditional\n"
    config_file += "# Z - Action Control\n"
    config_file += "#\n"
    config_file += "# Action (W): Specify which action should be taken when (X) and (Y) is True.\n"
    config_file += "#   delete - Delete media item from server\n"
    config_file += "#   keep - Do NOT delete media item from server\n"
    config_file += "#\n"
    config_file += "# User Conditional (X): Specify how monitored users must have the media item whitetagged.\n"
    config_file += "#   all - Every monitored user must have the media item whitetagged\n"
    config_file += "#   any - N/A; Tags apply to all users\n"
    config_file += "#\n"
    config_file += "# Played Conditional (Y): Specify how monitored users must meet played_filter_*.\n"
    config_file += "#   all - Every monitored user must meet the played_filter_*\n"
    config_file += "#   any - One or more monitored users must meet the played_filter_*\n"
    config_file += "#   ignore - Ignore if monitored users meet the played_filter_*\n"
    config_file += "#\n"
    config_file += "# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False\n"
    config_file += "#   0 - No action taken on True; No action taken on False (disabled)\n"
    config_file += "#   1 - No action taken on True; Action taken on False\n"
    config_file += "#   2 - No action taken on True; Opposite action taken on False\n"
    config_file += "#   3 - Action taken on True; No action taken on False (recommended)\n"
    config_file += "#   4 - Action taken on True; Action taken on False\n"
    config_file += "#   5 - Action taken on True; Opposite action taken on False (recommended)\n"
    config_file += "#   6 - Opposite action taken on True; No action taken on False\n"
    config_file += "#   7 - Opposite action taken on True; Action taken on False\n"
    config_file += "#   8 - Opposite action taken on True; Opposite action taken on False\n"
    config_file += "#\n"
    config_file += "# (['keep','all','ignore',0] : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "whitetagged_behavior_movie=" + str(get_default_config_values('whitetagged_behavior_movie')) + "\n"
        config_file += "whitetagged_behavior_episode=" + str(get_default_config_values('whitetagged_behavior_episode')) + "\n"
        config_file += "whitetagged_behavior_audio=" + str(get_default_config_values('whitetagged_behavior_audio')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "whitetagged_behavior_audiobook=" + str(get_default_config_values('whitetagged_behavior_audiobook')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "whitetagged_behavior_movie=" + str(cfg.whitetagged_behavior_movie) + "\n"
        config_file += "whitetagged_behavior_episode=" + str(cfg.whitetagged_behavior_episode) + "\n"
        config_file += "whitetagged_behavior_audio=" + str(cfg.whitetagged_behavior_audio) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "whitetagged_behavior_audiobook=" + str(cfg.whitetagged_behavior_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# User entered blacktag name; chosen during setup\n"
    config_file += "#  Use a comma \',\' to seperate multiple tag names\n"
    config_file += "#   Ex: tagname,tag name,tag-name\n"
    config_file += "#  Backslash \'\\\' not allowed\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "blacktag='" + the_dict['blacktag'] + "'\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "blacktag='" + cfg.blacktag + "'\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Blacktagged Behavioral Statements\n"
    config_file += "#  Tags applied to a media item are seen by all users\n"
    config_file += "#\n"
    config_file += "# Blacktagging is the third priority\n"
    config_file += "#  Whitelisting behavior is ignored\n"
    config_file += "#  Blacklisting behavior is ignored\n"
    config_file += "#\n"
    config_file += "# [W, X, Y, Z]\n"
    config_file += "#\n"
    config_file += "# W - Action\n"
    config_file += "# X - User Conditional\n"
    config_file += "# Y - Played Conditional\n"
    config_file += "# Z - Action Control\n"
    config_file += "#\n"
    config_file += "# Action (W): Specify which action should be taken when (X) and (Y) is True.\n"
    config_file += "#   delete - Delete media item from server\n"
    config_file += "#   keep - Do NOT delete media item from server\n"
    config_file += "#\n"
    config_file += "# User Conditional (X): Specify how monitored users must have the media item blacktagged.\n"
    config_file += "#   all - Every monitored user must have the media item blacktagged\n"
    config_file += "#   any - N/A; Tags apply to all users\n"
    config_file += "#\n"
    config_file += "# Played Conditional (Y): Specify how monitored users must meet played_filter_*.\n"
    config_file += "#   all - Every monitored user must meet the played_filter_*\n"
    config_file += "#   any - One or more monitored users must meet the played_filter_*\n"
    config_file += "#   ignore - Ignore if monitored users meet the played_filter_*\n"
    config_file += "#\n"
    config_file += "# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False\n"
    config_file += "#   0 - No action taken on True; No action taken on False (disabled)\n"
    config_file += "#   1 - No action taken on True; Action taken on False\n"
    config_file += "#   2 - No action taken on True; Opposite action taken on False\n"
    config_file += "#   3 - Action taken on True; No action taken on False (recommended)\n"
    config_file += "#   4 - Action taken on True; Action taken on False\n"
    config_file += "#   5 - Action taken on True; Opposite action taken on False (recommended)\n"
    config_file += "#   6 - Opposite action taken on True; No action taken on False\n"
    config_file += "#   7 - Opposite action taken on True; Action taken on False\n"
    config_file += "#   8 - Opposite action taken on True; Opposite action taken on False\n"
    config_file += "#\n"
    config_file += "# (['delete','all','any',0] : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "blacktagged_behavior_movie=" + str(get_default_config_values('blacktagged_behavior_movie')) + "\n"
        config_file += "blacktagged_behavior_episode=" + str(get_default_config_values('blacktagged_behavior_episode')) + "\n"
        config_file += "blacktagged_behavior_audio=" + str(get_default_config_values('blacktagged_behavior_audio')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "blacktagged_behavior_audiobook=" + str(get_default_config_values('blacktagged_behavior_audiobook')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "blacktagged_behavior_movie=" + str(cfg.blacktagged_behavior_movie) + "\n"
        config_file += "blacktagged_behavior_episode=" + str(cfg.blacktagged_behavior_episode) + "\n"
        config_file += "blacktagged_behavior_audio=" + str(cfg.blacktagged_behavior_audio) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "blacktagged_behavior_audiobook=" + str(cfg.blacktagged_behavior_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Whitelisted Behavioral Statements\n"
    config_file += "#\n"
    config_file += "# Whitelisting is the fourth priority\n"
    config_file += "#  Blacklisting behavior is ignored\n"
    config_file += "#\n"
    config_file += "# [W, X, Y, Z]\n"
    config_file += "#\n"
    config_file += "# W - Action\n"
    config_file += "# X - User Conditional\n"
    config_file += "# Y - Played Conditional\n"
    config_file += "# Z - Action Control\n"
    config_file += "#\n"
    config_file += "# Action (W): Specify which action should be taken when (X) and (Y) is True.\n"
    config_file += "#   delete - Delete media item from server\n"
    config_file += "#   keep - Do NOT delete media item from server\n"
    config_file += "#\n"
    config_file += "# User Conditional (X): Specify how monitored users must have the media item whitelisted.\n"
    config_file += "#   all - Every monitored user must have the media item whitelisted\n"
    config_file += "#   any - One or more monitored users must have the media item whitelisted\n"
    config_file += "#\n"
    config_file += "# Played Conditional (Y): Specify how monitored users must meet played_filter_*.\n"
    config_file += "#   all - Every monitored user must meet the played_filter_*\n"
    config_file += "#   any - One or more monitored users must meet the played_filter_*\n"
    config_file += "#   ignore - Ignore if monitored users meet the played_filter_*\n"
    config_file += "#\n"
    config_file += "# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False\n"
    config_file += "#   0 - No action taken on True; No action taken on False (disabled)\n"
    config_file += "#   1 - No action taken on True; Action taken on False\n"
    config_file += "#   2 - No action taken on True; Opposite action taken on False\n"
    config_file += "#   3 - Action taken on True; No action taken on False (recommended)\n"
    config_file += "#   4 - Action taken on True; Action taken on False\n"
    config_file += "#   5 - Action taken on True; Opposite action taken on False (recommended)\n"
    config_file += "#   6 - Opposite action taken on True; No action taken on False\n"
    config_file += "#   7 - Opposite action taken on True; Action taken on False\n"
    config_file += "#   8 - Opposite action taken on True; Opposite action taken on False\n"
    config_file += "#\n"
    config_file += "# (['keep','any','ignore',3] : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "whitelisted_behavior_movie=" + str(get_default_config_values('whitelisted_behavior_movie')) + "\n"
        config_file += "whitelisted_behavior_episode=" + str(get_default_config_values('whitelisted_behavior_episode')) + "\n"
        config_file += "whitelisted_behavior_audio=" + str(get_default_config_values('whitelisted_behavior_audio')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "whitelisted_behavior_audiobook=" + str(get_default_config_values('whitelisted_behavior_audiobook')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "whitelisted_behavior_movie=" + str(cfg.whitelisted_behavior_movie) + "\n"
        config_file += "whitelisted_behavior_episode=" + str(cfg.whitelisted_behavior_episode) + "\n"
        config_file += "whitelisted_behavior_audio=" + str(cfg.whitelisted_behavior_audio) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "whitelisted_behavior_audiobook=" + str(cfg.whitelisted_behavior_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Blacklisted Behavioral Statements\n"
    config_file += "#\n"
    config_file += "# Blacklisting is the fifth (and lowest) priority\n"
    config_file += "#\n"
    config_file += "# [W, X, Y, Z]\n"
    config_file += "#\n"
    config_file += "# W - Action\n"
    config_file += "# X - User Conditional\n"
    config_file += "# Y - Played Conditional\n"
    config_file += "# Z - Action Control\n"
    config_file += "#\n"
    config_file += "# Action (W): Specify which action should be taken when (X) and (Y) is True.\n"
    config_file += "#   delete - Delete media item from server\n"
    config_file += "#   keep - Do NOT delete media item from server\n"
    config_file += "#\n"
    config_file += "# User Conditional (X): Specify how monitored users must have the media item blacklisted.\n"
    config_file += "#   all - Every monitored user must have the media item blacklisted\n"
    config_file += "#   any - One or more monitored users must have the media item blacklisted\n"
    config_file += "#\n"
    config_file += "# Played Conditional (Y): Specify how monitored users must meet played_filter_*.\n"
    config_file += "#   all - Every monitored user must meet the played_filter_*\n"
    config_file += "#   any - One or more monitored users must meet the played_filter_*\n"
    config_file += "#   ignore - Ignore if monitored users meet the played_filter_*\n"
    config_file += "#\n"
    config_file += "# Action Control (Z): Specify the action the script will take when (X) and (Y) is True/False\n"
    config_file += "#   0 - No action taken on True; No action taken on False (disabled)\n"
    config_file += "#   1 - No action taken on True; Action taken on False\n"
    config_file += "#   2 - No action taken on True; Opposite action taken on False\n"
    config_file += "#   3 - Action taken on True; No action taken on False (recommended)\n"
    config_file += "#   4 - Action taken on True; Action taken on False\n"
    config_file += "#   5 - Action taken on True; Opposite action taken on False (recommended)\n"
    config_file += "#   6 - Opposite action taken on True; No action taken on False\n"
    config_file += "#   7 - Opposite action taken on True; Action taken on False\n"
    config_file += "#   8 - Opposite action taken on True; Opposite action taken on False\n"
    config_file += "#\n"
    config_file += "# (['delete','any','any',3] : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "blacklisted_behavior_movie=" + str(get_default_config_values('blacklisted_behavior_movie')) + "\n"
        config_file += "blacklisted_behavior_episode=" + str(get_default_config_values('blacklisted_behavior_episode')) + "\n"
        config_file += "blacklisted_behavior_audio=" + str(get_default_config_values('blacklisted_behavior_audio')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "blacklisted_behavior_audiobook=" + str(get_default_config_values('blacklisted_behavior_audiobook')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "blacklisted_behavior_movie=" + str(cfg.blacklisted_behavior_movie) + "\n"
        config_file += "blacklisted_behavior_episode=" + str(cfg.blacklisted_behavior_episode) + "\n"
        config_file += "blacklisted_behavior_audio=" + str(cfg.blacklisted_behavior_audio) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "blacklisted_behavior_audiobook=" + str(cfg.blacklisted_behavior_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide the minimum number of episodes to remain in all tv series'\n"
    config_file += "# This ignores the played and unplayed states of episodes\n"
    config_file += "#  0 - Episodes will be deleted based on the Filter and Behavioral Statements\n"
    config_file += "#  1-730500 - Episodes will be deleted based on the Filter and Behavioral Statements;\n"
    config_file += "#              unless the remaining played and unplayed episodes are less than or\n"
    config_file += "#              equal to the chosen value\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "minimum_number_episodes=" + str(get_default_config_values('minimum_number_episodes')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "minimum_number_episodes=" + str(cfg.minimum_number_episodes) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide the minimum number of played episodes to remain in all tv series'\n"
    config_file += "# Keeping one or more played epsiodes for each series allows the \"Next Up\"\n"
    config_file += "#  functionality to notify user(s) when a new episode for a series\n"
    config_file += "#  is available\n"
    config_file += "# This value applies only to played and episodes\n"
    config_file += "#  0 - Episodes will be deleted based on the Filter and Behavioral Statements\n"
    config_file += "#  1-730500 - Episodes will be deleted based on the Filter and Behavioral Statements;\n"
    config_file += "#              unless the remaining played episodes are less than or equal to the\n"
    config_file += "#              chosen value\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "minimum_number_played_episodes=" + str(get_default_config_values('minimum_number_played_episodes')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "minimum_number_played_episodes=" + str(cfg.minimum_number_played_episodes) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide how 'minimum_number_episodes' and 'minimum_number_played_episodes' will behave.\n"
    config_file += "# The minimum number of played and unplayed episodes will vary for each user and for each\n"
    config_file += "#  series when multiple users are watching the same series at different paces.\n"
    config_file += "# The following option gives a mechanism to control this in different ways.\n"
    config_file += "# The 'minimum_number_episodes' and 'minimum_number_played_episodes' will be based off of...\n"
    config_file += "#  'User's Name' - The UserName specified; If matching UserName not found script will assume default.\n"
    config_file += "#  'User's Id' - The UserId specified; If matching UserName not found script will assume default.\n"
    config_file += "#  'Max Played' - The first user with the highest number of played episodes to be deleted for each series.\n"
    config_file += "#  'Min Played' - The first user with the lowest number of played episodes to be deleted for each series.\n"
    config_file += "#  'Max Unplayed' - The first user with the highest number of unplayed episodes to be deleted for each series.\n"
    config_file += "#  'Min Unplayed' - The first user with the lowest number of unplayed episodes to be deleted for each series.\n"
    config_file += "# The Max/Min Played/Unplayed values can be mixed and matched. For example...\n"
    config_file += "#  'Max Unplayed Min Played' - The number played episodes to be deleted is based off the user\n"
    config_file += "#                                with the highest number of unplayed episodes to be deleted for a\n"
    config_file += "#                                specified series. The number of unplayed episodes to be deleted is\n"
    config_file += "#                                based off the user with the lowest number of played episodes to be\n"
    config_file += "#                                deleted for a specified series.\n"
    config_file += "# ('Min Played Min Unplayed' : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "minimum_number_episodes_behavior='" + str(get_default_config_values('minimum_number_episodes_behavior')) + "'\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "minimum_number_episodes_behavior='" + str(cfg.minimum_number_episodes_behavior) + "'\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Add last played date for items missing the LastPlayedDate data\n"
    config_file += "# When played state is imported from Trakt the LastPlayedDate is\n"
    config_file += "#  not populated. To allow the script to maintain functionality\n"
    config_file += "#  the current date and time the script is run can be used as the\n"
    config_file += "#  LastPlayedDate value.\n"
    config_file += "#  False - Do not set the LastPlayedDate; days since played will show as\n"
    config_file += "#        the number of days since 1970-Jan-01 00:00:00hrs for any media\n"
    config_file += "#        items missng the LastPlayedDate data.\n"
    config_file += "#  True - Set the LastPlayedDate; the current date-time the script is\n"
    config_file += "#        run will be saved as the LastPlayedDate for any media items\n"
    config_file += "#        missing the LastPlayedDate data. Only media items missing the\n"
    config_file += "#        LastPlayedDate data are modified\n"
    config_file += "# (True : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "movie_set_missing_last_played_date=" + str(get_default_config_values('movie_set_missing_last_played_date')) + "\n"
        config_file += "episode_set_missing_last_played_date=" + str(get_default_config_values('episode_set_missing_last_played_date')) + "\n"
        config_file += "audio_set_missing_last_played_date=" + str(get_default_config_values('audio_set_missing_last_played_date')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "audiobook_set_missing_last_played_date=" + str(get_default_config_values('audiobook_set_missing_last_played_date')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "movie_set_missing_last_played_date=" + str(cfg.movie_set_missing_last_played_date) + "\n"
        config_file += "episode_set_missing_last_played_date=" + str(cfg.episode_set_missing_last_played_date) + "\n"
        config_file += "audio_set_missing_last_played_date=" + str(cfg.audio_set_missing_last_played_date) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "audiobook_set_missing_last_played_date=" + str(cfg.audiobook_set_missing_last_played_date) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Enable/Disable console outputs by type\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Should the script print its output to the console\n"
    config_file += "#  False - Do not print this output type to the console\n"
    config_file += "#  True - Print this output type to the console\n"
    config_file += "# (True : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "print_script_header=" + str(get_default_config_values('print_script_header')) + "\n"
        config_file += "print_warnings=" + str(get_default_config_values('print_warnings')) + "\n"
        config_file += "print_user_header=" + str(get_default_config_values('print_user_header')) + "\n"
        config_file += "print_movie_delete_info=" + str(get_default_config_values('print_movie_delete_info')) + "\n"
        config_file += "print_movie_keep_info=" + str(get_default_config_values('print_movie_keep_info')) + "\n"
        config_file += "print_episode_delete_info=" + str(get_default_config_values('print_episode_delete_info')) + "\n"
        config_file += "print_episode_keep_info=" + str(get_default_config_values('print_episode_keep_info')) + "\n"
        config_file += "print_audio_delete_info=" + str(get_default_config_values('print_audio_delete_info')) + "\n"
        config_file += "print_audio_keep_info=" + str(get_default_config_values('print_audio_keep_info')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "print_audiobook_delete_info=" + str(get_default_config_values('print_audiobook_delete_info')) + "\n"
            config_file += "print_audiobook_keep_info=" + str(get_default_config_values('print_audiobook_keep_info')) + "\n"
        config_file += "print_summary_header=" + str(get_default_config_values('print_summary_header')) + "\n"
        config_file += "print_movie_summary=" + str(get_default_config_values('print_movie_summary')) + "\n"
        config_file += "print_episode_summary=" + str(get_default_config_values('print_episode_summary')) + "\n"
        config_file += "print_audio_summary=" + str(get_default_config_values('print_audio_summary')) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "print_audiobook_summary=" + str(get_default_config_values('print_audiobook_summary')) + "\n"
        config_file += "print_script_footer=" + str(get_default_config_values('print_script_footer')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "print_script_header=" + str(cfg.print_script_header) + "\n"
        config_file += "print_warnings=" + str(cfg.print_warnings) + "\n"
        config_file += "print_user_header=" + str(cfg.print_user_header) + "\n"
        config_file += "print_movie_delete_info=" + str(cfg.print_movie_delete_info) + "\n"
        config_file += "print_movie_keep_info=" + str(cfg.print_movie_keep_info) + "\n"
        config_file += "print_episode_delete_info=" + str(cfg.print_episode_delete_info) + "\n"
        config_file += "print_episode_keep_info=" + str(cfg.print_episode_keep_info) + "\n"
        config_file += "print_audio_delete_info=" + str(cfg.print_audio_delete_info) + "\n"
        config_file += "print_audio_keep_info=" + str(cfg.print_audio_keep_info) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "print_audiobook_delete_info=" + str(cfg.print_audiobook_delete_info) + "\n"
            config_file += "print_audiobook_keep_info=" + str(cfg.print_audiobook_keep_info) + "\n"
        config_file += "print_summary_header=" + str(cfg.print_summary_header) + "\n"
        config_file += "print_movie_summary=" + str(cfg.print_movie_summary) + "\n"
        config_file += "print_episode_summary=" + str(cfg.print_episode_summary) + "\n"
        config_file += "print_audio_summary=" + str(cfg.print_audio_summary) + "\n"
        if (isJellyfinServer(the_dict['server_brand'])):
            config_file += "print_audiobook_summary=" + str(cfg.print_audiobook_summary) + "\n"
        config_file += "print_script_footer=" + str(get_default_config_values('print_script_footer')) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Set to True to add new users or edit existing users\n"
    config_file += "# Must be a boolean True or False value\n"
    config_file += "#  False - Operate normally\n"
    config_file += "#  True  - Enable configuration editor mode; will NOT delete media items\n"
    config_file += "#           Resets to dry run mode (REMOVE_FILES=False)\n"
    config_file += "# (False : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "UPDATE_CONFIG=False\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "UPDATE_CONFIG=" + str(cfg.UPDATE_CONFIG) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Must be a boolean True or False value\n"
    config_file += "#  False - Disables the ability to delete media (dry run mode)\n"
    config_file += "#  True - Enable the ability to delete media\n"
    config_file += "# (False : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "REMOVE_FILES=False\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#---------!!!DO NOT MODIFY ANYTHING BELOW!!!----------------#\n"
    config_file += "# These are automatically created during setup.\n"
    config_file += "#   If you do not know EXACTLY what you are doing; changing these\n"
    config_file += "#      may cause script failure.\n"
    config_file += "#   The only way to recover from script failure is to revert the\n"
    config_file += "#      config back to the way it was OR rebuild a new config.\n"
    config_file += "#----------------------------------------------------------#\n"
    #config_file += "#----------------------------------------------------------#\n"    
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Server branding; chosen during setup\n"
    config_file += "#  0 - 'emby'\n"
    config_file += "#  1 - 'jellyfin'\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "server_brand='" + the_dict['server_brand'] + "'\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "server_brand='" + cfg.server_brand + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Server URL; created during setup\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "server_url='" + the_dict['server_url'] + "'\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "server_url='" + cfg.server_url + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Authentication Key; requested from server during setup\n"
    config_file += "#  Used for API queries sent to the server\n"
    config_file += "#  Also know as an Access Token\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "auth_key='" + the_dict['auth_key'] + "'\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "auth_key='" + cfg.auth_key + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide how the script will use the libraries chosen for each user\n"
    config_file += "#  Only used during creation or editing of the configuration file\n"
    config_file += "#  0 - blacklist - Chosen libraries will blacklisted\n"
    config_file += "#                  All other libraries will be whitelisted\n"
    config_file += "#  1 - whitelist - Chosen libraries will whitelisted\n"
    config_file += "#                  All other libraries will be blacklisted\n"
    config_file += "# (blacklist : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "library_setup_behavior='" + the_dict['library_setup_behavior'] + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide how the script will match media items to libraries\n"
    config_file += "#  0 - byId - Media items will be matched to libraries using \'LibraryIds\'\n"
    config_file += "#  1 - byPath - Media items will be matched to libraries using \'Paths\'\n"
    config_file += "#  2 - byNetwork Path - Media items will be matched to libraries using \'NetworkPaths\'\n"
    config_file += "# Filtering byId does not apply to the rules below.\n"
    config_file += "# Filtering byPath requires no shared network folders are configured.\n"
    config_file += "# Filtering byNetworkPath requires shared network folders are configured.\n"
    config_file += "# (byId : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "library_matching_behavior='" + the_dict['library_matching_behavior'] + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# User UserName(s) and UserId(s) of monitored account(s); chosen during setup\n"
    config_file += "# The order of the UserName(s):UserId(s) here must match the order of the\n"
    config_file += "#  UserId(s)/UserNames(s) in user_bl_libs and user_wl_libs\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "user_keys='" + user_keys + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Blacklisted libraries with corresponding user keys(s)\n"
    config_file += "# These libraries are typically searched for media items to delete\n"
    config_file += "# Chosen during setup\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "user_bl_libs='" + user_bl_libs + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Whitelisted libraries with corresponding user keys(s)\n"
    config_file += "# These libraries are typically not searched for media items to delete\n"
    config_file += "# Chosen during setup\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "user_wl_libs='" + user_wl_libs + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# API query attempts\n"
    config_file += "# Number of times to retry an API request\n"
    config_file += "#  Delay between initial attempt and the first retry is 1 second\n"
    config_file += "#  The delay will double with each attempt after the first retry\n"
    config_file += "#  Delay between the orginal request and retry #1 is (2^0) 1 second\n"
    config_file += "#  Delay between retry #1 and retry #2 is (2^1) 2 seconds\n"
    config_file += "#  Delay between retry #2 and retry #3 is (2^2) 4 seconds\n"
    config_file += "#  Delay between retry #3 and retry #4 is (2^3) 8 seconds\n"
    config_file += "#  Delay between retry #4 and retry #5 is (2^4) 16 seconds\n"
    config_file += "#  Delay between retry #5 and retry #6 is (2^5) 32 seconds\n"
    config_file += "#  ...\n"
    config_file += "#  Delay between retry #15 and retry #16 is (2^15) 32768 seconds\n"
    config_file += "#  0-16 - number of retry attempts\n"
    config_file += "#  (4 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_attempts=4\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_attempts=" + str(cfg.api_query_attempts) + "\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# API query item limit\n"
    config_file += "# To keep the server running smoothly we do not want it to return a\n"
    config_file += "#  large amount of metadata from a single API query\n"
    config_file += "# If the server lags or bogs down when this script runs try lowering\n"
    config_file += "#  this value to allow the server to return smaller amounts of data\n"
    config_file += "# ALL media items and their metadata are processed regardless of this value\n"
    config_file += "#  1-10000 - maximum number of media items the server will return for each API query\n"
    config_file += "#  (25 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_item_limit=25\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_item_limit=" + str(cfg.api_query_item_limit) + "\n"

    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# API cache maximum size\n"
    config_file += "# To keep the script running efficiently we do not want to send the\n"
    config_file += "#  same requests to the server repeatedly\n"
    config_file += "# If any single data entry is larger than the cache size, that data entry\n"
    config_file += "#  will not be cached\n"
    config_file += "# 0.1MB of cache is better than 0MB of cache\n"
    config_file += "# Recommend setting DEBUG=1 to print the cache stats to determine the\n"
    config_file += "#  best cache settings (i.e. size, fallback behavior, and last accessed time)\n"
    config_file += "#\n"
    config_file += "# MegaByte Sizing Reference\n"
    config_file += "#  1MB = 1048576 Bytes\n"
    config_file += "#  1000MB = 1GB\n"
    config_file += "#  10000MB = 10GB\n"
    config_file += "#\n"
    config_file += "#  0 - Disable cache\n"
    config_file += "#  1-10000 - Size of cache in megabytes (MB)\n"
    config_file += "#  (32 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_cache_size=" + str(get_default_config_values('api_query_cache_size')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_cache_size=" + str(cfg.api_query_cache_size) + "\n"

    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# API cache fallback behavior\n"
    config_file += "# By default the script is a hybrid LFU-LRU RAM Cache\n"
    config_file += "#\n"
    config_file += "# 1.First the cache is filled\n"
    config_file += "# 2.Once full the cache uses api_query_cache_last_accessed_time to\n"
    config_file += "#    establish a minimum age an entry has to be for removal\n"
    config_file += "# 3.Then the oldest entry meeting the minimum age (from step 2) with\n"
    config_file += "#    the lowest number of hits (reads) is removed\n"
    config_file += "# 4.If no entrys meet the minimum age or all have the same number of\n"
    config_file += "#    cache hits (reads); api_query_cache_fallback_behavior is used\n"
    config_file += "# Recommend setting DEBUG=1 to print the cache stats to determine the\n"
    config_file += "#  best cache settings (i.e. size, fallback behavior, and last accessed time)\n"
    config_file += "#\n"
    config_file += "# Fallback To\n"
    config_file += "#  'FIFO' - First In First Out (first entry is removed)\n"
    config_file += "#  'LFU' - Least Frequently Used (first entry with the lowest number of hits is removed)\n"
    config_file += "#  'LRU' - Least Recently Used (first entry with the oldest access time is removed)\n"
    config_file += "#  (LRU : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_cache_fallback_behavior='" + str(get_default_config_values('api_query_cache_fallback_behavior')) + "'\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_cache_fallback_behavior='" + str(cfg.api_query_cache_fallback_behavior) + "'\n"

    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# API cache entry minium age\n"
    config_file += "#\n"
    config_file += "# Once full the cache uses api_query_cache_last_accessed_time to\n"
    config_file += "#  establish a minimum age an entry has to be for removal\n"
    config_file += "#\n"
    config_file += "# Bigger is NOT always better. The older an entry is allowed to be, the lower\n"
    config_file += "#  the number of elgible entries for removal when cache is full.\n"
    config_file += "#  When this happens the script will not be able to find an entry that\n"
    config_file += "#  satisfies LFU-LRU and will use api_query_cache_fallback_behavior\n"
    config_file += "#  until there is enough space in cache for the newest entry.\n"
    config_file += "# Of course setting a bigger cache size means needing to remove less\n"
    config_file += "#  cache entries.\n"
    config_file += "# Increase api_query_cache_size before increasing this api_query_cache_last_accessed_time\n"
    config_file += "# Recommend setting DEBUG=1 to print the cache stats to determine the\n"
    config_file += "#  best cache settings (i.e. size, fallback behavior, and last accessed time)\n"
    config_file += "#\n"
    config_file += "# Millisecond Timing Reference\n"
    config_file += "#  1ms = 0.001s\n"
    config_file += "#  1000ms = 1s\n"
    config_file += "#  100000ms = 100s\n"
    config_file += "#\n"
    config_file += "#  0-600000 - Minimum cached entry age for removal in milliseconds (ms)\n"
    config_file += "#  (200 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_cache_last_accessed_time=" + str(get_default_config_values('api_query_cache_last_accessed_time')) + "\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "api_query_cache_last_accessed_time=" + str(cfg.api_query_cache_last_accessed_time) + "\n"

    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Must be an integer value\n"
    config_file += "#  Debug log file save to: /the/script/directory/mumc_DEBUG.log\n"
    config_file += "#  The debug log file can be large (i.e. 10s to 100s of MBytes)\n"
    config_file += "#  Recommend only enabling DEBUG when necessary\n"
    config_file += "#   0 - Debug messaging disabled\n"
    config_file += "#   1 - Level 1 debug messaging enabled\n"
    config_file += "#   2 - Level 2 debug messaging enabled\n"
    config_file += "#   3 - Level 3 debug messaging enabled\n"
    config_file += "#   4 - Level 4 debug messaging enabled\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (the_dict['UPDATE_CONFIG']):
        config_file += "DEBUG=0\n"
    elif (the_dict['UPDATE_CONFIG']):
        config_file += "DEBUG=" + str(the_dict['DEBUG']) + "\n"
    config_file += "\n"
    config_file += "#-------------End Config Options----------------------------#"

    #Save the config file to the directory this script is running from
    write_to_file(config_file,os.path.join(the_dict['cwd'],the_dict['config_file_name']))

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
                    print('\n\n-----------------------------------------------------------')
                    print('* Config file is not setup to find media.')
                    print('-----------------------------------------------------------')
                    print('To find media open mumc_config.py in a text editor:')
                    print('* Set \'played_filter_movie[A]\' or \'created_filter_movie[A]\' to zero or a positive number')
                    print('* Set \'played_filter_episode[A]\' or \'created_filter_episode[A]\' to zero or a positive number')
                    print('* Set \'played_filter_audio[A]\' or \'created_filter_audio[A]\' to zero or a positive number')
                    if (isJellyfinServer(the_dict['server_brand'])):
                        print('* Set \'played_filter_audiobook[A]\' or \'created_filter_audiobook[A]\' to zero or a positive number')
            if not (the_dict['REMOVE_FILES']):
                print('-----------------------------------------------------------')
                print('* Config file is not setup to delete media.')
                print('* Config file is in dry run mode to prevent deleting media.')
                print('-----------------------------------------------------------')
                print('To delete media open mumc_config.py in a text editor:')
                print('* Set REMOVE_FILES=\'True\'')
            print('-----------------------------------------------------------')
            print('*Edit the mumc_config.py file and try running again.')
            print('-----------------------------------------------------------')

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