
from collections import defaultdict
import copy
from mumc_modules.mumc_url import requestURL
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_compare_items import keys_exist
from mumc_modules.mumc_sort import sortLibSelection


#Create output string to show library information to user for them to choose
def parse_library_data_for_display(libFolder):

    libDisplayString=' - ' + libFolder['collection_type']

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
    if (not (libPath_str == None)):
        libPath_str=libPath_str.replace('\\','/')
    return(libPath_str)


#API call to get library folders; choose which libraries to blacklist and whitelist
def get_library_folders(infotext, specified_user_data, mandatory, the_dict):
    #get all library paths for a given user

    #set user specific variables
    user_policy=specified_user_data['Policy']
    user_id=specified_user_data['Id']
    user_pos=specified_user_data['userPosition']

    #define empty dictionaries
    libraryTemp_dict=defaultdict(dict)
    library_tracker=[]
    enabledFolderIds_set=set()

    if (the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
        oppList='blacklist'
        realList='whitelist'
    else: #(realList == 'blacklist'):
        oppList='whitelist'
        realList='blacklist'

    prevProcessedUser=False
    #check if this user has already been processed for this run session
    for liblist in the_dict['admin_settings']['users'][user_pos][oppList]:
        if (not (liblist['selection'] == None)):
            prevProcessedUser=True
    #check if this user has already been processed for this run session
    for liblist in the_dict['admin_settings']['users'][user_pos][realList]:
        if (not (liblist['selection'] == None)):
            prevProcessedUser=True

    for liblist in the_dict['admin_settings']['users'][user_pos][realList]:
        the_dict['admin_settings']['users'][user_pos][oppList].append(liblist)
    #clear all libraries from the realList
    the_dict['admin_settings']['users'][user_pos][realList].clear()

    if (prevProcessedUser):
        #sort libraries in oppList by selection key
        the_dict['admin_settings']['users'][user_pos][oppList]=sorted(the_dict['admin_settings']['users'][user_pos][oppList],key=sortLibSelection)

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
                    stop_loop=True
                    print('')
                else:
                    print('')
                    path_number_float=float(input_path_number)
                    if ((path_number_float % 1) == 0):
                        path_number_int=int(path_number_float)
                        if ((path_number_int >= 0) and (path_number_int < j)):
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
                                                the_dict['admin_settings']['users'][user_pos][realList].append(libsToSearch)
                                                the_dict['admin_settings']['users'][user_pos][oppList].remove(libsToSearch)
                                                library_tracker.append(typeMatches)
                                        z+=1

                            #When all libraries selected we can automatically exit the library chooser
                            if (the_dict['admin_settings']['users'][user_pos][oppList] == []):
                                stop_loop=True
                                print('')
                            else:
                                stop_loop=False

                        else:
                            print('\nIgnoring Out Of Range Value: ' + input_path_number + '\n')
                    else:
                        print('\nIgnoring Decimal Value: ' + input_path_number + '\n')
            except:
                print('\nIgnoring Non-Whole Number Value: ' + input_path_number + '\n')

    #Determine how many entries are in the "choosen" and "not choosen" data structures
    #When both have libirary data; parse both data structures
    for libItems in the_dict['admin_settings']['users'][user_pos][oppList]:
        libItems['path']=cleanup_library_paths(libItems['path'])
        libItems['network_path']=cleanup_library_paths(libItems['network_path'])
    for libItems in the_dict['admin_settings']['users'][user_pos][realList]:
        libItems['path']=cleanup_library_paths(libItems['path'])
        libItems['network_path']=cleanup_library_paths(libItems['network_path'])

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
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        #the jellyfin endpoint is /Users
        req=(the_dict['admin_settings']['server']['url'] + '/Users?api_key=' + the_dict['admin_settings']['server']['auth_key'])
    else:
        #the emby endpoint is /Users/Query
        req=(the_dict['admin_settings']['server']['url'] + '/Users/Query?api_key=' + the_dict['admin_settings']['server']['auth_key'])

    #preConfigDebug = True
    preConfigDebug = False

    #api call
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        #jellyfin returns a list of users
        data_all_users=requestURL(req, preConfigDebug, 'get_users', 3, the_dict)
    else:
        #emby returns a dictionary with a key called 'Items' with a list of users as the value
        data_all_users=requestURL(req, preConfigDebug, 'get_users', 3, the_dict)
        data_all_users=data_all_users['Items']

    #Request for libraries (i.e. movies, tvshows, audio, etc...)
    req_folders=(the_dict['admin_settings']['server']['url'] + '/Library/VirtualFolders?api_key=' + the_dict['admin_settings']['server']['auth_key'])

    #preConfigDebug = True
    preConfigDebug = False

    #api calls
    data_folders = requestURL(req_folders, preConfigDebug, 'get_media_folders', 3, the_dict)

    the_dict['data_folders']=[]

    data_users_list=[]
    users_dict_temp={}
    lib_dict={}
    whitelist_list=[]
    blacklist_list=[]

    libpos_dict={}
    libpos_list=[]
    user_temp_list=[]
    user_id_list=[]
    user_id_dict={}
    user_id_existing_list=[]
    user_id_existing_dict={}
    usersdata_existing=the_dict['admin_settings']['users'].copy()

    #define empty userId dictionary
    userId_dict={}
    #define empty monitored library dictionary
    userId_bllib_dict={}
    #define empty whitelisted library dictionary
    userId_wllib_dict={}
    #define empty userId lists
    userId_list=[]
    userId_ReRun_list=[]

    #Check if not running for the first time
    if (the_dict['advanced_settings']['UPDATE_CONFIG']):
        i=0
        usernames_userkeys={}
        for user_info in the_dict['admin_settings']['users']:
            usernames_userkeys[user_info['user_name']]=user_info['user_id']
            userId_list.append(user_info['user_id'])
        #Pre-populate the existing userkeys and libraries; only new users are fully shown; existing user will display minimal info
        for rerun_userkey in userId_list:
            userId_bllib_dict[rerun_userkey]={}
            userId_bllib_dict[rerun_userkey]['username']=the_dict['admin_settings']['users'][i]['user_name']
            userId_bllib_dict[rerun_userkey]['userid']=rerun_userkey
            userId_wllib_dict[rerun_userkey]={}
            userId_wllib_dict[rerun_userkey]['username']=the_dict['admin_settings']['users'][i]['user_name']
            userId_wllib_dict[rerun_userkey]['userid']=rerun_userkey
            i += 1

    #Emby and Jellyfin use different key-names for their libraryId
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        libraryGuid='ItemId'
    else:
        libraryGuid='Guid'

    #Build library staging dictionaries for unprocessed users
     #for new users put the library dictionary data in the opposite blacklist/whitelist behavior list
    for folder in data_folders:
        #if (not (folder['CollectionType'] == 'boxsets')):
        if (not (folder['LibraryOptions']['PathInfos'] == [])):
            the_dict['data_folders'].append(folder)
            libpos_list.append(folder[libraryGuid])
            libpos_dict[folder[libraryGuid]]=libpos_list.index(folder[libraryGuid])
            for libpos in range(len(folder['LibraryOptions']['PathInfos'])):
                lib_dict['lib_id']=folder[libraryGuid]
                if ('CollectionType' in folder):
                    lib_dict['collection_type']=folder['CollectionType']
                else:
                    lib_dict['collection_type']=None
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
                #put all libraries in the opposite list
                if (the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
                    blacklist_list.append(lib_dict.copy())
                else: #(the_dict['admin_settings']['behavior']['list'] == 'blacklist'):
                    whitelist_list.append(lib_dict.copy())

    #Remove users disabled in the GUI
    for data_user in data_all_users:
        if (not (data_user['Policy']['IsDisabled'])):
            data_users_list.append(data_user)

    #Build list and dictionary with mirrored userId and position information for ALL users
    for userdata in data_users_list:
        user_id_list.append(userdata['Id'])
        user_id_dict[userdata['Id']]=user_id_list.index(userdata['Id'])

    #Build list and dictionary with mirrored userId and position information for EXISTING users
    for userdata in usersdata_existing:
        user_id_existing_list.append(userdata['user_id'])
        user_id_existing_dict[userdata['user_id']]=user_id_existing_list.index(userdata['user_id'])
        #Add selection key to each whitelist entry for existing users
        for eachLib in userdata['whitelist']:
            eachLib['selection']=None
        #Add selection key to each blacklist entry for existing users
        for eachLib in userdata['blacklist']:
            eachLib['selection']=None

    #Update the_dict['admin_settings']['users'] with ALL users and their possible dictionaries
     #For EXISTING users update with their existing library selections
     #For NEW users update with their possible library selections
    for userdata in data_users_list:
        if (userdata['Id'] in user_id_existing_list):
            user_temp_list.append(copy.deepcopy(usersdata_existing[user_id_existing_list.index(userdata['Id'])]))
        else:
            users_dict_temp['user_id']=userdata['Id']
            users_dict_temp['user_name']=userdata['Name']
            users_dict_temp['whitelist']=whitelist_list.copy()
            users_dict_temp['blacklist']=blacklist_list.copy()
            user_temp_list.append(copy.deepcopy(users_dict_temp))

    the_dict['admin_settings']['users']=copy.deepcopy(user_temp_list)

    stop_loop=False
    single_user=False
    one_user_selected = False
    #Loop until all user accounts selected or until manually stopped with a blank entry
    while (stop_loop == False):
        i=0
        #Determine if we are looking at a mulitple user setup or a single user setup
        if (len(data_users_list) > 1):
            for user in data_users_list:
                data_users_list[i]['userPosition']=i
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
            for user in data_users_list:
                data_users_list[i]['userPosition']=i
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
                userId_list.append(userId_dict[user_number_int])

                #Depending on library setup behavior the chosen libraries will either be treated as blacklisted libraries or whitelisted libraries
                if (the_dict['admin_settings']['behavior']['list'] == 'blacklist'):
                    message='Enter number of the library folder(s) to blacklist (aka monitor) for the selected user.\nMedia in blacklisted library folder(s) will be monitored for deletion.'
                    the_dict=get_library_folders(message,data_users_list[user_number_int],False,the_dict)
                else: #(the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
                    message='Enter number of the library folder(s) to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                    the_dict=get_library_folders(message,data_users_list[user_number_int],False,the_dict)

            #We get here when we are done selecting users to monitor
            elif ((user_number == '') and (userId_list)):
                stop_loop=True
                print('')
            #We get here if there are muliple users and we tried not to select any; at least one must be selected
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
                        the_dict=get_library_folders(message,data_users_list[user_number_int],False,the_dict)
                    else: #(the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
                        message='Enter number of the library folder(s) to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                        the_dict=get_library_folders(message,data_users_list[user_number_int],False,the_dict)

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

    return the_dict['admin_settings']['users']
