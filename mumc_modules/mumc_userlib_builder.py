#!/usr/bin/env python3
import urllib.request as urlrequest
from collections import defaultdict
from operator import attrgetter
import json
import os
from mumc_config_defaults import get_default_config_values
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json,write_to_file,print_byType
from mumc_modules.mumc_url import requestURL
from mumc_modules.mumc_server_type import isJellyfinServer,isEmbyServer
from mumc_modules.mumc_setup_questions import get_brand,get_url,get_port,get_base,get_admin_username,get_admin_password,get_library_setup_behavior,get_library_matching_behavior,get_tag_name
from mumc_modules.mumc_versions import get_script_version
from mumc_modules.mumc_console_info import print_all_media_disabled,build_new_config_setup_to_delete_media
from mumc_modules.mumc_configuration import mumc_configuration_builder
from mumc_modules.mumc_configuration_yaml import yaml_configurationBuilder
from mumc_modules.mumc_config_updater import yaml_configurationUpdater
from mumc_modules.mumc_config_skeleton import setYAMLConfigSkeleton
from mumc_modules.mumc_compare_items import keys_exist
from mumc_modules.mumc_sort import sortLibSelection

'''
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
'''

'''
def buildUserLibraries(the_dict):
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nBuilding Whitelisted Libraries...",2,the_dict)
    #Build the library data from the data structures stored in the configuration file
    wluser_keys_json_verify,wluser_names_json_verify,user_wllib_keys_json,user_wllib_collectiontype_json,user_wllib_path_json,user_wllib_netpath_json,user_wllib_selection_json=user_lib_builder(the_dict['user_wl_libs'],the_dict,'whitelist')

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

    the_dict['currentUserPosition']=0

    return the_dict
'''

#Create output string to show library information to user for them to choose
def parse_library_data_for_display(libFolder):

    #if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        #libraryGuid='ItemId'
    #else:
        #libraryGuid='Guid'

    libDisplayString=' - ' + libFolder['collection_type']

    #if ('LibraryOptions' in libFolder):
    #if ('PathInfos' in libFolder['LibraryOptions']):
    #if not (len(libFolder['LibraryOptions']['PathInfos']) == 0):
    if (('path' in libFolder) and (not (libFolder['path'] == None))):
        libDisplayString+=' - Path: ' + libFolder['path']
    if (('network_path' in libFolder) and (not (libFolder['network_path'] == None))):
        libDisplayString+=' - NetPath: ' + libFolder['network_path']
    if ('lib_id' in libFolder):
        libDisplayString+=' - LibId: ' + libFolder['lib_id']

    return libDisplayString



#Store the chosen library's data in temporary location for use when building blacklist and whitelist
def parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,pos,the_dict):

    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
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
def get_library_folders(infotext, specified_user_data, mandatory, the_dict):
    #get all library paths for a given user

    #set user specific variables
    user_policy=specified_user_data['Policy']
    user_id=specified_user_data['Id']
    user_name=specified_user_data['Name']
    user_pos=specified_user_data['userPosition']

    #Request for libraries (i.e. movies, tvshows, audio, etc...)
    req_folders=(the_dict['admin_settings']['server']['url'] + '/Library/VirtualFolders?api_key=' + the_dict['admin_settings']['server']['auth_key'])

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
    #libMatchedNumbers=[]

    if (the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
        oppList='blacklist'
        realList='whitelist'
    else: #(realList == 'blacklist'):
        oppList='whitelist'
        realList='blacklist'

    #check if this user has already been processed for this run session
    if (the_dict['admin_settings']['users'][user_pos][realList]):
        if (not (the_dict['admin_settings']['users'][user_pos][realList][0]['selection'] == None)):
            the_dict['admin_settings']['users'][user_pos][realList]=sorted(the_dict['admin_settings']['users'][user_pos][realList],key=sortLibSelection)
            for libElem in the_dict['admin_settings']['users'][user_pos][realList]:
                the_dict['admin_settings']['users'][user_pos][oppList].insert(libElem['selection'],libElem.copy())
            the_dict['admin_settings']['users'][user_pos][realList].clear()

    #Check if this user has permission to access to all libraries or only specific libraries
    # then remove libraries user does not have access to
    if not (user_policy['EnableAllFolders']):
        for okFolders in user_policy['EnabledFolders']:
            enabledFolderIds_set.add(okFolders)

        #copy list so we loop and modify
        temp_user_libs=the_dict['admin_settings']['users'][user_pos][oppList].copy()
        #reverse, so we remove list items from the bottom up
        temp_user_libs.reverse()
        #Remove libraries this user does not have access to
        for listinfo in temp_user_libs:
            if (not (listinfo['lib_id'] in enabledFolderIds_set)):
                the_dict['admin_settings']['users'][user_pos][oppList].remove(listinfo)

    staticFolders_list=[]
    staticFolders_list=the_dict['admin_settings']['users'][user_pos][oppList].copy()
    #staticFolders_list.extend(the_dict['admin_settings']['users'][user_pos][realList].copy())

    i=0
    '''
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
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
    '''

    #Go thru libaries this user has permissions to access and show them on the screen
    stop_loop=False
    first_run=True
    libInfoPrinted=False
    selectionSet=0
    while (stop_loop == False):
        j=0
        k=0
        showpos_correlation={}
        for libFolder in staticFolders_list:
            if (('lib_id' in libFolder) and ('collection_type' in libFolder)):
                #for subLibPath in range(len(libFolder['LibraryOptions']['PathInfos'])):
                #option made here to check for either ItemId or Path when deciding what to show
                # when ItemId libraries with multiple folders but same libId will be removed together
                # when Path libraries with multiple folders but the same libId will be removed individually
                if ((the_dict['admin_settings']['behavior']['matching'] == 'byId')):
                    if (not (libFolder['lib_id'] in library_tracker)):
                        print(str(j) + parse_library_data_for_display(libFolder))
                        libInfoPrinted=True
                    else:
                        #show blank entry
                        print(str(j) + ' - ' + libFolder['collection_type'] + ' - ' )
                        libInfoPrinted=True
                    if not ('userid' in libraryTemp_dict):
                        libraryTemp_dict['userid']=user_id
                    #libraryTemp_dict=parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,k,the_dict)
                elif ((the_dict['admin_settings']['behavior']['matching'] == 'byPath')):
                    if (not (libFolder['path'] in library_tracker)):
                        print(str(j) + parse_library_data_for_display(libFolder))
                        libInfoPrinted=True
                    else:
                        #show blank entry
                        print(str(j) + ' - ' + libFolder['collection_type'] + ' - ' )
                        libInfoPrinted=True
                    if not ('userid' in libraryTemp_dict):
                        libraryTemp_dict['userid']=user_id
                    #libraryTemp_dict=parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,k,the_dict)
                elif ((the_dict['admin_settings']['behavior']['matching'] == 'byNetworkPath')):
                    if ((not (libFolder['network_path'] in library_tracker))):
                        print(str(j) + parse_library_data_for_display(libFolder))
                        libInfoPrinted=True
                    else:
                        #show blank entry
                        print(str(j) + ' - ' + libFolder['collection_type'] + ' - ' )
                        libInfoPrinted=True
                    if not ('userid' in libraryTemp_dict):
                        libraryTemp_dict['userid']=user_id
                    #libraryTemp_dict=parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,k,the_dict)

                #Only set the selection the first time the library info is printed
                if (selectionSet < len(staticFolders_list)):
                    the_dict['admin_settings']['users'][user_pos][oppList][staticFolders_list.index(libFolder)]['selection']=j
                    staticFolders_list[staticFolders_list.index(libFolder)]['selection']=j
                    selectionSet+=1

                if (libInfoPrinted):
                    showpos_correlation[k]=j
                    k += 1
                if (((the_dict['admin_settings']['behavior']['matching'] == 'byPath') or (the_dict['admin_settings']['behavior']['matching'] == 'byNetworkPath')) and (libInfoPrinted)):
                    libInfoPrinted=False
                    j += 1
            if ((the_dict['admin_settings']['behavior']['matching'] == 'byId') and (libInfoPrinted)):
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
                    #Add valid library selections to the library dicitonary
                    '''
                    if not ('userid' in library_dict):
                        library_dict['userid']=libraryTemp_dict['userid']
                    if not ('username' in library_dict):
                        library_dict['username']=user_name
                    '''
                    #when whitelisting and no specific libraries chosen; remove all libraries from blacklist
                    #if (realList == 'whitelist'):
                        #the_dict['admin_settings']['users'][user_pos]['blacklist'].clear()
                    #when blacklisting and no specific libraries chosen; remove all libraries from whitelist
                    #else: #if (realList == 'blacklist'):
                        #the_dict['admin_settings']['users'][user_pos]['whitelist'].clear()
                    stop_loop=True
                    print('')
                else:
                    print('')
                    path_number_float=float(input_path_number)
                    if ((path_number_float % 1) == 0):
                        path_number_int=int(path_number_float)
                        if ((path_number_int >= 0) and (path_number_int < j)):
                            #Add valid library selecitons to the library dicitonary
                            #if not ('userid' in library_dict):
                                #library_dict['userid']=libraryTemp_dict['userid']
                            #if not ('username' in library_dict):
                                #library_dict['username']=user_name
                            for showpos in showpos_correlation:
                                libMatchFound=False
                                if (showpos_correlation[showpos] == path_number_int):
                                    if (the_dict['admin_settings']['behavior']['matching'] == 'byId'):
                                        byType='lib_id'
                                    elif (the_dict['admin_settings']['behavior']['matching'] == 'byPath'):
                                        byType='path'
                                    else: #(the_dict['admin_settings']['behavior']['matching'] == 'byNetworkPath'):
                                        byType='network_path'
                                    typeMatches=staticFolders_list[showpos][byType]
                                    libMatchFound=True

                                if (libMatchFound):
                                    z=0
                                    for libsToSearch in staticFolders_list:
                                        if (libsToSearch[byType] == typeMatches):
                                            if (not (typeMatches in library_tracker)):
                                                #if (not (path_number_int in libMatchedNumbers)):
                                                    #libMatchedNumbers.append(path_number_int)
                                                #the_dict['admin_settings']['users'][user_pos][oppList][the_dict['admin_settings']['users'][user_pos][oppList].index(libsToSearch)]['selection']=path_number_int
                                                the_dict['admin_settings']['users'][user_pos][realList].append(libsToSearch)
                                                the_dict['admin_settings']['users'][user_pos][oppList].remove(libsToSearch)
                                                library_tracker.append(typeMatches)
                                        z+=1

                                    '''
                                    for checkallpos in libraryTemp_dict:
                                        libMatchFound=False
                                        if not ((checkallpos == 'userid') or (checkallpos in library_dict)):
                                            if ((the_dict['admin_settings']['behavior']['matching'] == 'byId') and (libraryTemp_dict[showpos]['libid'] == libraryTemp_dict[checkallpos]['libid'])):
                                                libMatchFound=True
                                                library_dict[checkallpos]['libid']=libraryTemp_dict[checkallpos]['libid']
                                                library_dict[checkallpos]['collectiontype']=libraryTemp_dict[checkallpos]['collectiontype']
                                                library_dict[checkallpos]['path']=libraryTemp_dict[checkallpos]['path']
                                                library_dict[checkallpos]['networkpath']=libraryTemp_dict[checkallpos]['networkpath']
                                            elif ((the_dict['admin_settings']['behavior']['matching'] == 'byPath') and (libraryTemp_dict[showpos]['path'] == libraryTemp_dict[checkallpos]['path'])):
                                                libMatchFound=True
                                                library_dict[checkallpos]['libid']=libraryTemp_dict[checkallpos]['libid']
                                                library_dict[checkallpos]['collectiontype']=libraryTemp_dict[checkallpos]['collectiontype']
                                                library_dict[checkallpos]['path']=libraryTemp_dict[checkallpos]['path']
                                                library_dict[checkallpos]['networkpath']=libraryTemp_dict[checkallpos]['networkpath']
                                            elif ((the_dict['admin_settings']['behavior']['matching'] == 'byNetworkPath') and (libraryTemp_dict[showpos]['networkpath'] == libraryTemp_dict[checkallpos]['networkpath'])):
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
                                                if (( not (library_dict[checkallpos].get('libid') == '')) and (the_dict['admin_settings']['behavior']['matching'] == 'byId')):
                                                    library_tracker.append(library_dict[checkallpos]['libid'])
                                                elif (( not (library_dict[checkallpos].get('path') == '')) and (the_dict['admin_settings']['behavior']['matching'] == 'byPath')):
                                                    library_tracker.append(library_dict[checkallpos]['path'])
                                                elif (( not (library_dict[checkallpos].get('networkpath') == '')) and (the_dict['admin_settings']['behavior']['matching'] == 'byNetworkPath')):
                                                    library_tracker.append(library_dict[checkallpos]['networkpath'])
                                    '''

                            #When all libraries selected we can automatically exit the library chooser
                            #if (len(library_tracker) >= len(showpos_correlation)):
                            #if (len(the_dict['admin_settings']['users'][user_pos][oppList]) == 0):
                            if (the_dict['admin_settings']['users'][user_pos][oppList] == []):
                                stop_loop=True
                                print('')
                            else:
                                stop_loop=False

                            #if(preConfigDebug):
                                #print('libraryTemp_dict = ' + str(libraryTemp_dict) + '\n')
                                #print('library_dict = ' + str(library_dict) + '\n')
                                #print('not_library_dict = ' + str(not_library_dict) + '\n')
                                #print('library_tracker = ' + str(library_tracker) + '\n')

                        else:
                            print('\nIgnoring Out Of Range Value: ' + input_path_number + '\n')
                    else:
                        print('\nIgnoring Decimal Value: ' + input_path_number + '\n')
            except:
                print('\nIgnoring Non-Whole Number Value: ' + input_path_number + '\n')

    #Determine how many entries are in the "choosen" and "not choosen" data structures
    #When both have libirary data; parse both data structures
    #the_dict['admin_settings']['users'][user_pos][realList].append(libsToSearch)
    #the_dict['admin_settings']['users'][user_pos][oppList].pop(z)
    for libItems in the_dict['admin_settings']['users'][user_pos][oppList]:
        libItems['path']=cleanup_library_paths(libItems['path'])
        libItems['network_path']=cleanup_library_paths(libItems['network_path'])
    for libItems in the_dict['admin_settings']['users'][user_pos][realList]:
        libItems['path']=cleanup_library_paths(libItems['path'])
        libItems['network_path']=cleanup_library_paths(libItems['network_path'])
    '''
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
    #When only one has library data; parse that data structure
    elif ((len(library_dict) == 2) and (len(not_library_dict) > 2)):
        for entry in not_library_dict:
            if not ((entry == 'userid') or (entry == 'username')):
                not_library_dict[entry]['path']=cleanup_library_paths(not_library_dict[entry].get('path'))
                not_library_dict[entry]['networkpath']=cleanup_library_paths(not_library_dict[entry].get('networkpath'))
        #libraries for blacklist and whitelist
        return(not_library_dict,library_dict)
    #When only one has library data; parse that data structure
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
    '''
    return the_dict


def removeUnselectedUsers(userId_list,the_dict):
    tempUsersList=[]
    tempUsersList=the_dict['admin_settings']['users'].copy()
    #Remove any unselected user(s)
    for checkUser in tempUsersList:
        if (not (checkUser['user_id'] in userId_list)):
            the_dict['admin_settings']['users'].remove(checkUser)

    return the_dict


def removeSelectionKey(the_dict):
    tempUsersList=[]
    tempUsersList=the_dict['admin_settings']['users'].copy()
    for tempUser in tempUsersList:
        for tempLibs in tempUser:
            thislist=None
            if (tempLibs == 'whitelist'):
                thislist = 'whitelist'
            elif (tempLibs == 'blacklist'):
                thislist = 'blacklist'
            if (thislist):
                for wblist in tempUser[tempLibs]:
                    if (keys_exist(wblist,'selection')):
                        the_dict['admin_settings']['users'][the_dict['admin_settings']['users'].index(tempUser)]\
                                [thislist][the_dict['admin_settings']['users'][the_dict['admin_settings']['users'].index(tempUser)]\
                                [thislist].index(wblist)].pop('selection')

    return the_dict


#API call to get all user accounts
#Choose account(s) this script will use to delete played media
#Choosen account(s) do NOT need to have "Allow Media Deletion From" enabled in the UI
def get_users_and_libraries(the_dict):
    #Get all users
    req=(the_dict['admin_settings']['server']['url'] + '/Users?api_key=' + the_dict['admin_settings']['server']['auth_key'])

    #preConfigDebug = True
    preConfigDebug = False

    #api call
    data_users=requestURL(req, preConfigDebug, 'get_users', 3, the_dict)

    #Request for libraries (i.e. movies, tvshows, audio, etc...)
    req_folders=(the_dict['admin_settings']['server']['url'] + '/Library/VirtualFolders?api_key=' + the_dict['admin_settings']['server']['auth_key'])

    #preConfigDebug = True
    preConfigDebug = False

    #api calls
    data_folders = requestURL(req_folders, preConfigDebug, 'get_media_folders', 3, the_dict)

    the_dict['data_folders']=[]

    #users_list=[]
    users_dict={}
    users_dict_temp={}
    lib_dict={}
    whitelist_dict={}
    whitelist_list=[]
    blacklist_dict={}
    blacklist_list=[]

    #define empty userId dictionary
    userId_dict={}
    #define empty monitored library dictionary
    userId_bllib_dict={}
    userId_bllib_list=[]
    #define empty whitelisted library dictionary
    userId_wllib_dict={}
    userId_wllib_list=[]
    #define empty userId lists
    userId_list=[]
    userId_ReRun_list=[]
    #user_keys_json=''

    #Check if not running for the first time
    if (the_dict['advanced_settings']['UPDATE_CONFIG']):
        #Build the library data from the data structures stored in the configuration file
        #bluser_keys_json_verify,bluser_names_json_verify,v,w,x,y,z=user_lib_builder(the_dict['admin_settings']['users'],'blacklist')
        #Build the library data from the data structures stored in the configuration file
        #wluser_keys_json_verify,wluser_names_json_verify,v,w,x,y,z=user_lib_builder(the_dict['user_wl_libs'],the_dict,'whitelist')

        #verify userIds are in same order for both blacklist and whitelist libraries
        #if (bluser_keys_json_verify == wluser_keys_json_verify):
            #user_keys_json = bluser_keys_json_verify
        #else:
            #raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both')

        #verify userNames are in same order for both blacklist and whitelist libraries
        #if (not (bluser_names_json_verify == wluser_names_json_verify)):
            #raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userNames need to be in the same order for both')

        i=0
        #usernames_userkeys=json.loads(the_dict['user_keys'])
        #usernames_userkeys=the_dict['user_names']
        usernames_userkeys={}
        #user_keys_json=[]
        for user_info in the_dict['admin_settings']['users']:
            usernames_userkeys[user_info['user_name']]=user_info['user_id']
            #user_keys_json.append(user_info['user_id'])
            userId_list.append(user_info['user_id'])
        #Pre-populate the existing userkeys and libraries; only new users are fully shown; existing user will display minimal info
        for rerun_userkey in userId_list:
            #userId_list.add(rerun_userkey)
            #if (rerun_userkey == bluser_keys_json_verify[i]):
                #userId_bllib_dict[rerun_userkey]=json.loads(cfg.user_bl_libs)[i]
            userId_bllib_dict[rerun_userkey]={}
                #for usernames_userkeys_str in usernames_userkeys:
                    #usernames_userkeys_list=usernames_userkeys_str.split(":")
                    #if (len(usernames_userkeys_list) == 2):
                        #if (usernames_userkeys_list[1] == rerun_userkey):
                            #userId_bllib_dict[rerun_userkey]['username']=usernames_userkeys_list[0]
            userId_bllib_dict[rerun_userkey]['username']=the_dict['admin_settings']['users'][i]['user_name']
            userId_bllib_dict[rerun_userkey]['userid']=rerun_userkey
                    #else:
                        #raise ValueError('\nUnable to edit config when username contains colon (:).')
            #else:
                #raise ValueError('\nValueError: Order of user_keys and user_wl libs are not in the same order.')
            #if (rerun_userkey == wluser_keys_json_verify[i]):
                #userId_wllib_dict[rerun_userkey]=json.loads(cfg.user_wl_libs)[i]
            userId_wllib_dict[rerun_userkey]={}
                #for usernames_userkeys_str in usernames_userkeys:
                    #usernames_userkeys_list=usernames_userkeys_str.split(":")
                    #if (len(usernames_userkeys_list) == 2):
                        #if (usernames_userkeys_list[1] == rerun_userkey):
                            #userId_wllib_dict[rerun_userkey]['username']=usernames_userkeys_list[0]
            userId_wllib_dict[rerun_userkey]['username']=the_dict['admin_settings']['users'][i]['user_name']
            userId_wllib_dict[rerun_userkey]['userid']=rerun_userkey
                    #else:
                        #raise ValueError('\nUnable to edit config when username contains colon (:).')
            #else:
                #raise ValueError('\nValueError: Order of user_keys and user_bl libs are not in the same order.')
            i += 1

        #Uncomment if the config editor should only allow adding new users
        #This means the script will not allow editing exisitng users until a new user is added
        #if ((len(user_keys_json)) == (len(data_users))):
            #print('-----------------------------------------------------------')
            #print('No new user(s) found.')
            #print('-----------------------------------------------------------')
            #print('Verify new user(s) added to the Emby/Jellyfin server.')
            #return(userId_bllib_dict, userId_wllib_dict)
    #else:

    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        libraryGuid='ItemId'
    else:
        libraryGuid='Guid'

    libpos_dict={}
    libpos_list=[]

    for folder in data_folders:
        if (not (folder['CollectionType'] == 'boxsets')):
            the_dict['data_folders'].append(folder)
            libpos_list.append(folder[libraryGuid])
            libpos_dict[folder[libraryGuid]]=libpos_list.index(folder[libraryGuid])
            for libpos in range(len(folder['LibraryOptions']['PathInfos'])):
                lib_dict['lib_id']=folder[libraryGuid]
                #lib_dict['lib_enabled']=True
                lib_dict['collection_type']=folder['CollectionType']
                if ('Path' in folder['LibraryOptions']['PathInfos'][libpos]):
                    lib_dict['path']=folder['LibraryOptions']['PathInfos'][libpos]['Path']
                else:
                    lib_dict['path']=None
                if ('NetworkPath' in folder['LibraryOptions']['PathInfos'][libpos]):
                    lib_dict['network_path']=folder['LibraryOptions']['PathInfos'][libpos]['NetworkPath']
                else:
                    lib_dict['network_path']=None
                lib_dict['lib_enabled']=True
                lib_dict['selection']=None
                if (the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
                    blacklist_list.append(lib_dict.copy())
                else: #(the_dict['admin_settings']['behavior']['list'] == 'blacklist'):
                    whitelist_list.append(lib_dict.copy())

    #whitelist_dict['whitelist']=whitelist_list
    #blacklist_dict['blacklist']=blacklist_list

    user_temp_list=[]
    user_id_list=[]
    user_id_dict={}
    usersdata_existing=the_dict['admin_settings']['users'].copy()
    user_id_existing_list=[]
    user_id_existing_dict={}

    for userdata in data_users:
        user_id_list.append(userdata['Id'])
        user_id_dict[userdata['Id']]=user_id_list.index(userdata['Id'])
    #for userpos in range(len(data_users)):
        #user_id_dict[data_users[userpos]['Id']]=userpos

    for userdata in usersdata_existing:
        user_id_existing_list.append(userdata['user_id'])
        user_id_existing_dict[userdata['user_id']]=user_id_existing_list.index(userdata['user_id'])
        for eachLib in userdata['whitelist']:
            eachLib['selection']=None
        for eachLib in userdata['blacklist']:
            eachLib['selection']=None
    #for userpos in range(len(usersdata_existing)):
        #user_id_existing_dict[usersdata_existing[userpos]['user_id']]=userpos

    for userdata in data_users:
        if (userdata['Id'] in user_id_existing_list):
            bltmplist=[]
            wltmplist=[]
            users_dict_temp['user_id']=userdata['Id']
            users_dict_temp['user_name']=userdata['Name']
            users_dict_temp['whitelist']=[]
            users_dict_temp['blacklist']=[]
            #add existing users and populate the 'selection' key with the correct library position
            atmp=usersdata_existing[user_id_existing_list.index(userdata['Id'])]
            for wlist in atmp['whitelist']:
                if (wlist['lib_id'] in libpos_list):
                    btmp=wlist.copy()
                    btmp['selection']=libpos_dict[btmp['lib_id']]
                    bltmplist.append(btmp)
            users_dict_temp['whitelist']=bltmplist
            for blist in atmp['blacklist']:
                if (blist['lib_id'] in libpos_list):
                    btmp=blist.copy()
                    btmp['selection']=libpos_dict[btmp['lib_id']]
                    wltmplist.append(btmp)
            users_dict_temp['blacklist']=wltmplist
            user_temp_list.append(users_dict_temp.copy())
        else:
            users_dict_temp['user_id']=userdata['Id']
            users_dict_temp['user_name']=userdata['Name']
            #users_dict.update(users_dict_temp.copy())
            #users_dict.update(whitelist_dict)
            #users_dict.update(blacklist_dict)
            users_dict_temp['whitelist']=whitelist_list
            users_dict_temp['blacklist']=blacklist_list
            #users_dict.update(users_dict_temp.copy())
            #users_list.append(users_dict.copy())
            #the_dict['admin_settings']['users'].append(users_dict_temp.copy())
            user_temp_list.append(users_dict_temp.copy())

        '''
        for userdata in data_users:
            users_dict_temp['user_id']=userdata['Id']
            users_dict_temp['user_name']=userdata['Name']
            users_dict.update(users_dict_temp.copy())
            #users_dict.update(whitelist_dict)
            #users_dict.update(blacklist_dict)
            users_dict['whitelist']=whitelist_list.copy()
            users_dict['blacklist']=blacklist_list.copy()
            #users_list.append(users_dict.copy())
            the_dict['admin_settings']['users'].append(users_dict.copy())
        '''

    the_dict['admin_settings']['users']=user_temp_list

    stop_loop=False
    single_user=False
    one_user_selected = False
    #Loop until all user accounts selected or until manually stopped with a blank entry
    while (stop_loop == False):
        i=0
        #Determine if we are looking at a mulitple user setup or a single user setup
        if (len(data_users) > 1):
            for user in data_users:
                data_users[i]['userPosition']=i
                if not (user['Id'] in userId_list):
                    print(str(i) +' - '+ user['Name'] + ' - ' + user['Id'])
                    userId_dict[i]=user['Id']
                else:
                    #show blank entry
                    print(str(i) +' - '+ user['Name'] + ' - ')
                    userId_dict[i]=user['Id']
                i += 1
        else: #Single user setup
            single_user=True
            for user in data_users:
                data_users[i]['userPosition']=i
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
                userId_list.add(userId_dict[user_number_int])

                #Depending on library setup behavior the chosen libraries will either be treated as blacklisted libraries or whitelisted libraries
                if (the_dict['admin_settings']['behavior']['list'] == 'blacklist'):
                    message='Enter number of the library folder(s) to blacklist (aka monitor) for the selected user.\nMedia in blacklisted library folder(s) will be monitored for deletion.'
                    #userId_wllib_dict[userId_dict[user_number_int]],userId_bllib_dict[userId_dict[user_number_int]]=get_library_folders(message,data_users[user_number_int],False,the_dict)
                    the_dict=get_library_folders(message,data_users[user_number_int],False,the_dict)
                else: #(the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
                    message='Enter number of the library folder(s) to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                    #userId_bllib_dict[userId_dict[user_number_int]],userId_wllib_dict[userId_dict[user_number_int]]=get_library_folders(message,data_users[user_number_int],False,the_dict)
                    the_dict=get_library_folders(message,data_users[user_number_int],False,the_dict)

            #We get here when we are done selecting users to monitor
            #elif ((user_number == '') and (not (len(userId_list) == 0))):
            elif ((user_number == '') and (userId_list)):
                stop_loop=True
                print('')
            #We get here if there are muliple users and we tried not to select any; at least one must be selected
            #elif ((user_number == '') and (len(userId_list) == 0)):
            elif ((user_number == '') and (not userId_list)):
                print('\nMust select at least one user. Try again.\n')
            #When multiple users we get here to allow selecting libraries for the specified user
            elif not (user_number == ''):
                user_number_float=float(user_number)
                if ((user_number_float % 1) == 0):
                    user_number_int=int(user_number_float)
                if ((user_number_int >= 0) and (user_number_int < i)):
                    one_user_selected=True
                    if (not (userId_dict[user_number_int] in userId_list)):
                        userId_list.append(userId_dict[user_number_int])
                    if (the_dict['advanced_settings']['UPDATE_CONFIG']):
                        userId_ReRun_list.append(userId_dict[user_number_int])

                    #Depending on library setup behavior the chosen libraries will either be treated as blacklisted libraries or whitelisted libraries
                    if (the_dict['admin_settings']['behavior']['list'] == 'blacklist'):
                        message='Enter number of the library folder(s) to blacklist (aka monitor) for the selected user.\nMedia in blacklisted library folder(s) will be monitored for deletion.'
                        #userId_wllib_dict[userId_dict[user_number_int]],userId_bllib_dict[userId_dict[user_number_int]]=get_library_folders(message,data_users[user_number_int],False,the_dict)
                        the_dict=get_library_folders(message,data_users[user_number_int],False,the_dict)
                    else: #(the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
                        message='Enter number of the library folder(s) to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                        #userId_bllib_dict[userId_dict[user_number_int]],userId_wllib_dict[userId_dict[user_number_int]]=get_library_folders(message,data_users[user_number_int],False,the_dict)
                        the_dict=get_library_folders(message,data_users[user_number_int],False,the_dict)

                    if ((len(userId_list) >= i) and (the_dict['advanced_settings']['UPDATE_CONFIG'] == False)):
                        stop_loop=True
                    elif ((len(userId_ReRun_list) >= i) and (the_dict['advanced_settings']['UPDATE_CONFIG'] == True)):
                        stop_loop=True
                    else:
                        stop_loop=False
                else:
                    print('\nInvalid value. Try again.\n')
            else:
                print('\nUnknown value. Try again.\n')
        except:
            print('\nException When Selecting User. Try again.\n')

    the_dict=removeUnselectedUsers(userId_list,the_dict)

    the_dict=removeSelectionKey(the_dict)

    #return(userId_bllib_dict, userId_wllib_dict)
    return the_dict['admin_settings']['users']