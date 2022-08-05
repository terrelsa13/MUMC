#!/usr/bin/env python3

#from pickle import TRUE
import urllib.request as request
import json, urllib
import traceback
#import hashlib
import time
import uuid
#import sys
import os
from dateutil.parser import parse
from collections import defaultdict
from datetime import datetime,date,timedelta,timezone
from mumc_config_defaults import get_default_config_values


#Get the current script version
def get_script_version():

    Version='3.1.2-beta'

    return(Version)


def convert2json(rawjson):
    #return a formatted string of the python JSON object
    ezjson = json.dumps(rawjson, sort_keys=False, indent=4)
    return(ezjson)


def print2json(rawjson):
    #create a formatted string of the python JSON object
    ezjson = convert2json(rawjson)
    print(ezjson)


#Check if json index exists
def does_index_exist(item, indexvalue):
    try:
        exists = item[indexvalue]
        if (GLOBAL_DEBUG):
            print_byType("\n" + str(indexvalue) + " exist in " + str(item),False)
    except IndexError:
        if (GLOBAL_DEBUG):
            print_byType("\n" + str(indexvalue) + " does NOT exist in " + str(item),False)
        return(False)
    return(True)


#send url request
def requestURL(url, debugBool, reqeustDebugMessage, retries):

    if (debugBool):
        #Double newline for better debug file readablilty
        print_byType("\n\n" + reqeustDebugMessage + ' - url request:',False)
        print_byType("\n" + url,False)

    #first delay if needed
        #delay value doubles each time the same API request is resent
    delay = 1
    #number of times after the intial API request to retry if an exception occurs
    retryAttempts = int(retries)

    getdata = True
    #try sending url request specified number of times
        #starting with a 1 second delay if an exception occurs and doubling the delay each attempt
    while(getdata):
        try:
            with request.urlopen(url) as response:
                if response.getcode() == 200:
                    try:
                        source = response.read()
                        data = json.loads(source)
                        getdata = False
                        if (debugBool):
                            print_byType("\nData Returned From The " + str(reqeustDebugMessage) + " Request: ...If Data Not Show Below; It Is Commented Out To Keep The DEBUG Log A Reasonable Size",False)
                            #print_byType("\n" + convert2json(data),False)
                    except Exception as err:
                        if (err.msg == 'Unauthorized'):
                            print_byType("\n" + str(err),True)
                            print_byType("\nAUTH_ERROR: User Not Authorized To Access Library",GLOBAL_debugFileName,True)
                            raise RuntimeError("\nAUTH_ERROR: User Not Authorized To Access Library")
                        else:
                            time.sleep(delay)
                            #delay value doubles each time the same API request is resent
                            delay += delay
                            if (delay >= (2**retryAttempts)):
                                print_byType("\nAn error occured, a maximum of " + str(retryAttempts) + " attempts met, and no data retrieved from the \"" + reqeustDebugMessage + "\" lookup.",True)
                                print_byType("\n" + "An error occured, a maximum of " + str(retryAttempts) + " attempts met, and no data retrieved from the \"" + reqeustDebugMessage + "\" lookup.",True)
                                return(err)
                else:
                    getdata = False
                    print_byType("\n" + "An error occurred while attempting to retrieve data from the API.",True)
                    return('Attempt to get data at: ' + reqeustDebugMessage + '. Server responded with code: ' + str(response.getcode()))
        except Exception as err:
            if (err.msg == 'Unauthorized'):
                print_byType("\n" + str(err),True)
                print_byType("\nAUTH_ERROR: User Not Authorized To Access Library",True)

                raise RuntimeError("\nAUTH_ERROR: User Not Authorized To Access Library")
            else:
                time.sleep(delay)
                #delay value doubles each time the same API request is resent
                delay += delay
                if (delay >= (2**retryAttempts)):
                    print_byType("\nAn error occured, a maximum of " + str(retryAttempts) + " attempts met, and no data retrieved from the \"" + reqeustDebugMessage + "\" lookup.",True)
                    return(err)
    return(data)


#Limit the amount of data returned for a single API call
def api_query_handler(url,StartIndex,TotalItems,QueryLimit,APIDebugMsg):

    data=requestURL(url, GLOBAL_DEBUG, APIDebugMsg, cfg.api_query_attempts)

    TotalItems = data['TotalRecordCount']
    StartIndex = StartIndex + QueryLimit
    QueryLimit = cfg.api_query_item_limit
    if ((StartIndex + QueryLimit) >= (TotalItems)):
        QueryLimit = TotalItems - StartIndex

    QueryItemsRemaining=False
    if (QueryLimit > 0):
        QueryItemsRemaining=True

    if (GLOBAL_DEBUG):
        print_byType("\nAPI Query Control Data For The NEXT LOOP: " + str(APIDebugMsg),False)
        print_byType("\nStarting at record index: " + str(StartIndex),False)
        print_byType("\nAsking for " + str(QueryLimit) + " records",False)
        print_byType("\nTotal records for this query is: " + str(TotalItems),False)
        print_byType("\nAre there records remaining: " + str(QueryItemsRemaining),False)

    return(data,StartIndex,TotalItems,QueryLimit,QueryItemsRemaining)


#emby or jellyfin?
def get_brand():
    defaultbrand='emby'
    print('0:emby\n1:jellyfin')
    brand=input('Enter number for server branding (default ' + defaultbrand + '): ')
    if (brand == ''):
        return(defaultbrand)
    elif (brand == '0'):
        return(defaultbrand)
    elif (brand == '1'):
        return('jellyfin')
    else:
        print('Invalid choice. Default to emby.')
        return(defaultbrand)


#ip address or url?
def get_url():
    defaulturl='http://localhost'
    url=input('Enter server ip or name (default ' + defaulturl + '): ')
    if (url == ''):
        return(defaulturl)
    else:
        if (url.find('://',3,8) >= 0):
            return(url)
        else:
           url='http://' + url
           print('Assuming server ip or name is: ' + url)
           return(url)


#http or https port?
def get_port():
    defaultport='8096'
    valid_port=False
    while (valid_port == False):
        print('If you have not explicity changed this option, press enter for default.')
        print('Space for no port.')
        port=input('Enter port (default ' + defaultport + '): ')
        if (port == ''):
            valid_port=True
            return(defaultport)
        elif (port == ' '):
            valid_port=True
            return('')
        else:
            try:
                port_float=float(port)
                if ((port_float % 1) == 0):
                    port_int=int(port_float)
                    if ((int(port_int) >= 1) and (int(port_int) <= 65535)):
                        valid_port=True
                        return(str(port_int))
                    else:
                        print('\nInvalid port. Try again.\n')
                else:
                    print('\nInvalid port. Try again.\n')
            except:
                print('\nInvalid port. Try again.\n')


#base url?
def get_base(brand):
    defaultbase='emby'
    #print('If you are using emby press enter for default.')
    if (brand == defaultbase):
        print('Using "/' + defaultbase + '" as base url')
        return(defaultbase)
    else:
        print('If you have not explicity changed this option in jellyfin, press enter for default.')
        print('For example: http://example.com/<baseurl>')
        base=input('Enter base url (default /' + defaultbase + '): ')
        if (base == ''):
            return(defaultbase)
        else:
            if (base.find('/',0,1) == 0):
                return(base[1:len(base)])
            else:
                return(base)


#admin username?
def get_admin_username():
    return(input('Enter admin username: '))


#admin password?
def get_admin_password():
    #print('Plain text password used to grab authentication key; hashed password stored in config file.')
    print('Plain text password used to grab authentication key; password not stored.')
    password=input('Enter admin password: ')
    return(password)


#Blacklisting or Whitelisting?
def get_library_setup_behavior(library_setup_behavior):
    defaultbehavior='blacklist'
    valid_behavior=False
    while (valid_behavior == False):
        print('Decide how the script will use the libraries chosen for each user.')
        print('0 - blacklist - Chosen libraries will blacklisted.')
        print('                All other libraries will be whitelisted.')
        print('1 - whitelist - Chosen libraries will whitelisted.')
        print('                All other libraries will be blacklisted.')
        if (library_setup_behavior == 'blacklist'):
            print('')
            print('Script previously setup using \'0 - ' + library_setup_behavior + '\'.')
        elif (library_setup_behavior == 'whitelist'):
            print('')
            print('Script previously setup using \'1 - ' + library_setup_behavior + '\'.')
        behavior=input('Choose how the script will use the chosen libraries. (default ' + defaultbehavior + '): ')
        if (behavior == ''):
            valid_behavior=True
            return(defaultbehavior)
        elif (behavior == '0'):
            valid_behavior=True
            return(defaultbehavior)
        elif (behavior == '1'):
            valid_behavior=True
            return('whitelist')
        else:
            print('\nInvalid choice. Try again.\n')


#Blacklisting or Whitelisting?
def get_library_matching_behavior(library_matching_behavior):
    defaultbehavior='byId'
    valid_behavior=False
    while (valid_behavior == False):
        print('Decide how the script will match media items to libraries.')
        print('0 - byId - Media items will be matched to libraries using \'LibraryIds\'.')
        print('1 - byPath - Media items will be matched to libraries using \'Paths\'.')
        print('2 - byNetworkPath - Media items will be matched to libraries using \'NetworkPaths\'.')
        if ((library_matching_behavior == 'byId') or (library_matching_behavior == 'byPath') or (library_matching_behavior == 'byNetworkPath')):
            print('')
            print('Script previously setup to match media items to libraries ' + library_matching_behavior + '.')
        behavior=input('Choose how the script will match media items to libraries. (default ' + defaultbehavior + '): ')
        if (behavior == ''):
            valid_behavior=True
            return(defaultbehavior)
        elif (behavior == '0'):
            valid_behavior=True
            return(defaultbehavior)
        elif (behavior == '1'):
            valid_behavior=True
            return('byPath')
        elif (behavior == '2'):
            valid_behavior=True
            return('byNetworkPath')
        else:
            print('\nInvalid choice. Try again.\n')


#Blacktagging or Whitetagging String Name?
def get_tag_name(tagbehavior,existingtag):
    defaulttag=get_default_config_values(tagbehavior)
    valid_tag=False
    while (valid_tag == False):
        print('Enter the desired ' + tagbehavior + ' name. Do not use backslash \'\\\'.')
        print('Use a comma \',\' to seperate multiple tag names.')
        print(' Ex: tagname,tag name,tag-name')
        if (defaulttag == ''):
            print('Leave blank to disable the ' + tagbehavior + 'ging functionality.')
            inputtagname=input('Input desired ' + tagbehavior + 's: ')
        else:
            inputtagname=input('Input desired ' + tagbehavior + 's (default \'' + defaulttag + '\'): ')
        #Remove duplicates
        inputtagname = ','.join(set(inputtagname.split(',')))
        if (inputtagname == ''):
            valid_tag=True
            return(defaulttag)
        else:
            if (inputtagname.find('\\') <= 0):
                #replace single quote (') with backslash-single quote (\')
                inputtagname=inputtagname.replace('\'','\\\'')
                valid_tag=True
                inputtagname_split=inputtagname.split(',')
                for inputtag in inputtagname_split:
                    if not (inputtag == ''):
                        existingtag_split=existingtag.split(',')
                        for donetag in existingtag_split:
                            if (inputtag == donetag):
                                valid_tag=False
                    else:
                        inputtagname_split.remove(inputtag)
                if (valid_tag):
                    return(','.join(inputtagname_split))
                else:
                    print('\nCannot use the same tag as a blacktag and a whitetag.\n')
                    print('Use a comma \',\' to seperate multiple tag names. Try again.\n')
            else:
                print('\nDo not use backslash \'\\\'. Try again.\n')


#Get condition days media types?
def get_condition_days(mediaType):
    defaultage=get_default_config_values(mediaType + '_condition_days')
    valid_age=False
    while (valid_age == False):
        print('Choose the number of days to wait before deleting ' + mediaType + ' media items')
        print('Valid values: 0-730500 days')
        print('             -1 to disable deleting ' + mediaType + ' media items')
        print('Press Enter to use default value')
        age=input('Enter number of days (default ' + str(defaultage) + '): ')
        if (age == ''):
            valid_age=True
            return(defaultage)
        else:
            try:
                age_float=float(age)
                if ((age_float % 1) == 0):
                    age_int=int(age_float)
                    if ((int(age_int) >= -1) and (int(age_int) <= 730500)):
                        valid_age=True
                        return(age_int)
                    else:
                        print('\nIgnoring Out Of Range ' + mediaType + ' Value. Try again.\n')
                else:
                    print('\nIgnoring ' + mediaType + ' Decimal Value. Try again.\n')
            except:
                print('\nIgnoring Non-Whole Number ' + mediaType + ' Value. Try again.\n')


#use of hashed password removed
#hash admin password
#def get_admin_password_sha1(password):
#    #password_sha1=password #input('Enter admin password (password will be hashed in config file): ')
#    password_sha1=hashlib.sha1(password.encode()).hexdigest()
#    return(password_sha1)

# Hash password if not hashed
#if cfg.admin_password_sha1 == '':
#     cfg.admin_password_sha1=hashlib.sha1(cfg.admin_password.encode()).hexdigest()
#auth_key=''
#print('Hash:'+ cfg.admin_password_sha1)


#api call to get admin account authentication token
def get_authentication_key(server_url, username, password, server_brand):
    #login info
    values = {'Username' : username, 'Pw' : password}
    #DATA = urllib.parse.urlencode(values)
    #DATA = DATA.encode('ascii')
    DATA = convert2json(values)
    DATA = DATA.encode('utf-8')

    xAuth = 'X-Emby-Authorization'
    #assuming jellyfin will eventually change to this
    #if (server_brand == 'emby'):
        #xAuth = 'X-Emby-Authorization'
    #else:
        #xAuth = 'X-Jellyfin-Authorization'

    headers = {xAuth : 'Emby UserId="' + username  + '", Client="mumc.py", Device="Multi-User Media Cleaner", DeviceId="MUMC", Version="' + get_script_version() + '", Token=""', 'Content-Type' : 'application/json'}

    req = request.Request(url=server_url + '/Users/AuthenticateByName', data=DATA, method='POST', headers=headers)

    #preConfigDebug = True
    preConfigDebug = False

    #api call
    data=requestURL(req, preConfigDebug, 'get_authentication_key', 3)

    return(data['AccessToken'])


#Unpack library data structure from config
def user_lib_builder(json_lib_entry):
    lib_json=json.loads(json_lib_entry)
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
        #loop thru each key for this user
        for keySlots in currentUser:
            #Store userId
            if (keySlots == 'userid'):
                built_userid.append(currentUser[keySlots])
                if (GLOBAL_DEBUG):
                    print_byType('\nBuilding library for user with Id: ' + currentUser[keySlots],False)
            elif (keySlots == 'username'):
                built_username.append(currentUser[keySlots])
                if (GLOBAL_DEBUG):
                    print_byType("\nBuilding library for user with name: '" + currentUser[keySlots] + "'",False)
            #Store library data
            else:
                #loop thru each library data item for this library
                for keySlotLibData in currentUser[keySlots]:
                    #Store libId
                    if (keySlotLibData == 'libid'):
                        if (libid_append == ''):
                            libid_append=currentUser[keySlots][keySlotLibData]
                        else:
                            if not (currentUser[keySlots][keySlotLibData] == ''):
                                libid_append=libid_append + ',' + currentUser[keySlots][keySlotLibData]
                            else:
                                libid_append=libid_append + ',\'\''
                        if (GLOBAL_DEBUG):
                            print_byType('\nLibrary Id: ' + currentUser[keySlots][keySlotLibData],False)
                    #Store collectionType
                    elif (keySlotLibData == 'collectiontype'):
                        if (collectiontype_append == ''):
                            collectiontype_append=currentUser[keySlots][keySlotLibData]
                        else:
                            if not (currentUser[keySlots][keySlotLibData] == ''):
                                collectiontype_append=collectiontype_append + ',' + currentUser[keySlots][keySlotLibData]
                            else:
                                collectiontype_append=collectiontype_append + ',\'\''
                        if (GLOBAL_DEBUG):
                            print_byType("\nCollection Type: '" + currentUser[keySlots][keySlotLibData] + "'",False)
                    #Store path
                    elif (keySlotLibData == 'path'):
                        if (path_append == ''):
                            path_append=currentUser[keySlots][keySlotLibData]
                        else:
                            if not (currentUser[keySlots][keySlotLibData] == ''):
                                path_append=path_append + ',' + currentUser[keySlots][keySlotLibData]
                            else:
                                path_append=path_append + ',\'\''
                        if (GLOBAL_DEBUG):
                            print_byType("\nPath: '" + currentUser[keySlots][keySlotLibData] + "'",False)
                    #Store networkPath
                    elif (keySlotLibData == 'networkpath'):
                        if (networkpath_append == ''):
                            networkpath_append=currentUser[keySlots][keySlotLibData]
                        else:
                            if not (currentUser[keySlots][keySlotLibData] == ''):
                                networkpath_append=networkpath_append + ',' + currentUser[keySlots][keySlotLibData]
                            else:
                                networkpath_append=networkpath_append + ',\'\''
                        if (GLOBAL_DEBUG):
                            print_byType("\nNetwork Path: '" + currentUser[keySlots][keySlotLibData] + "'",False)
        built_libid.insert(datapos,libid_append)
        built_collectiontype.insert(datapos,collectiontype_append)
        built_path.insert(datapos,path_append)
        built_networkpath.insert(datapos,networkpath_append)
        datapos+=1
    return(built_userid,built_username,built_libid,built_collectiontype,built_networkpath,built_path)


#Create output string to show library information to user for them to choose
def parse_library_data_for_display(libFolder,subLibPath):

    libDisplayString=' - ' + libFolder['Name']

    if ('LibraryOptions' in libFolder):
        if ('PathInfos' in libFolder['LibraryOptions']):
            if not (len(libFolder['LibraryOptions']['PathInfos']) == 0):
                if ('Path' in libFolder['LibraryOptions']['PathInfos'][subLibPath]):
                    libDisplayString+=' - ' + libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path']
                if ('NetworkPath' in libFolder['LibraryOptions']['PathInfos'][subLibPath]):
                    libDisplayString+=' - ' + libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath']

    if ('ItemId' in libFolder):
        libDisplayString+=' - LibId: ' + libFolder['ItemId']

    return libDisplayString


#Store the chosen library's data in temporary location for use when building blacklist and whitelist
def parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,pos):

    libraryTemp_dict[pos]['libid']=libFolder['ItemId']

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


#Parse library Paths
def cleanup_library_paths(libPath_str):
    libPath_str=libPath_str.replace('\\','/')
    return(libPath_str)


#API call to get library folders; choose which libraries to blacklist and whitelist
def get_library_folders(server_url, auth_key, infotext, user_policy, user_id, user_name, mandatory, library_matching_behavior):
    #get all library paths for a given user

    #Request for libraries (i.e. movies, tvshows, audio, etc...)
    req_folders=(server_url + '/Library/VirtualFolders?api_key=' + auth_key)
    #Request for channels (i.e. livetv, trailers, etc...)
    #req_channels=(server_url + '/Channels?api_key=' + auth_key)

    #preConfigDebug = True
    preConfigDebug = False

    #api calls
    data_folders = requestURL(req_folders, preConfigDebug, 'get_media_folders', 3)
    #data_channels = requestURL(req_channels, preConfigDebug, 'get_media_channels', 3)['Items']

    #define empty dictionaries
    libraryTemp_dict=defaultdict(dict)
    library_dict=defaultdict(dict)
    not_library_dict=defaultdict(dict)
    #define empty sets
    #libraryPath_set=set()
    library_tracker=[]
    enabledFolderIds_set=set()
    #delete_channels=[]

    #remove all channels that are not 'Trailers'
    #for channel in data_channels:
        #if not (channel['SortName'] == 'Trailers'):
            #delete_channels.append(channel)
    #reverse so we delete from the bottom up
    #delete_channels.reverse()
    #for delchan in range(len(delete_channels)):
        #data_channels.pop(delchan)

    #Check if this user has permission to access to all libraries or only specific libraries
    if not (user_policy['EnableAllFolders']):
        for okFolders in range(len(user_policy['EnabledFolders'])):
            enabledFolderIds_set.add(user_policy['EnabledFolders'][okFolders])
    #Check if this user has permission to access to all channels or only specific channels
    #if not (user_policy['EnableAllChannels']):
        #for okChannels in range(len(user_policy['EnabledChannels'])):
            #enabledFolderIds_set.add(user_policy['EnabledChannels'][okChannels])

    i=0
    #Populate all libraries into a "not chosen" data structure
    # i.e. if blacklist chosen all libraries start out as whitelisted
    # i.e. if whitelist chosen all libraries start out as blacklisted
    for libFolder in data_folders:
        if (('ItemId' in libFolder) and ('CollectionType' in libFolder) and ((enabledFolderIds_set == set()) or (libFolder['ItemId'] in enabledFolderIds_set))):
            for subLibPath in range(len(libFolder['LibraryOptions']['PathInfos'])):
                if not ('userid' in not_library_dict):
                    not_library_dict['userid']=user_id
                if not ('username' in not_library_dict):
                    not_library_dict['username']=user_name
                not_library_dict[i]['libid']=libFolder['ItemId']
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

    #Populate all channels into a "not chosen" data structure
    # i.e. if blacklist chosen all channels start out as whitelisted
    # i.e. if whitelist chosen all channels start out as blacklisted
    #for libChannel in data_channels:
        #if (('Id' in libChannel) and ('Type' in libChannel) and ((enabledFolderIds_set == set()) or (libChannel['Id'] in enabledFolderIds_set))):
            #if not ('userid' in not_library_dict):
                #not_library_dict['userid']=user_id
            #not_library_dict[i]['libid']=libChannel['Id']
            #not_library_dict[i]['collectiontype']=libChannel['Type']
            #not_library_dict[i]['path']=''
            #not_library_dict[i]['networkpath']=''
            #i += 1

    #Go thru libaries this user has permissions to access and show them on the screen
    stop_loop=False
    first_run=True
    libInfoPrinted=False
    while (stop_loop == False):
        j=0
        k=0
        showpos_correlation={}
        for libFolder in data_folders:
            if (('ItemId' in libFolder) and ('CollectionType' in libFolder) and ((enabledFolderIds_set == set()) or (libFolder['ItemId'] in enabledFolderIds_set))):
                for subLibPath in range(len(libFolder['LibraryOptions']['PathInfos'])):
                    if ((library_matching_behavior == 'byId') and ('ItemId' in libFolder)):
                        #option made here to check for either ItemId or Path when deciding what to show
                        # when ItemId libraries with multiple folders but same libId will be removed together
                        # when Path libraries with multiple folders but the same libId will be removed individually
                        if ((library_matching_behavior == 'byId') and ( not (libFolder['ItemId'] in library_tracker))):
                            print(str(j) + parse_library_data_for_display(libFolder,subLibPath))
                            libInfoPrinted=True
                        else:
                            #show blank entry
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' )
                            libInfoPrinted=True
                        if not ('userid' in libraryTemp_dict):
                            libraryTemp_dict['userid']=user_id
                        libraryTemp_dict=parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,k)
                    elif ((library_matching_behavior == 'byPath') and ('Path' in libFolder['LibraryOptions']['PathInfos'][subLibPath])):
                        #option made here to check for either ItemId or Path when deciding what to show
                        # when ItemId libraries with multiple folders but same libId will be removed together
                        # when Path libraries with multiple folders but the same libId will be removed individually
                        if ((library_matching_behavior == 'byPath') and ( not (libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path'] in library_tracker))):
                            print(str(j) + parse_library_data_for_display(libFolder,subLibPath))
                            libInfoPrinted=True
                        else:
                            #show blank entry
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' )
                            libInfoPrinted=True
                        if not ('userid' in libraryTemp_dict):
                            libraryTemp_dict['userid']=user_id
                        libraryTemp_dict=parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,k)
                    elif ((library_matching_behavior == 'byNetworkPath') and ('NetworkPath' in libFolder['LibraryOptions']['PathInfos'][subLibPath])):
                        #option made here to check for either ItemId or Path when deciding what to show
                        # when ItemId libraries with multiple folders but same libId will be removed together
                        # when Path libraries with multiple folders but the same libId will be removed individually
                        if ((library_matching_behavior == 'byNetworkPath') and ( not (libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath'] in library_tracker))):
                            print(str(j) + parse_library_data_for_display(libFolder,subLibPath))
                            libInfoPrinted=True
                        else:
                            #show blank entry
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' )
                            libInfoPrinted=True
                        if not ('userid' in libraryTemp_dict):
                            libraryTemp_dict['userid']=user_id
                        libraryTemp_dict=parse_library_data_for_temp_reference(libFolder,subLibPath,libraryTemp_dict,k)
                    if (libInfoPrinted):
                        showpos_correlation[k]=j
                        k += 1
                    if (((library_matching_behavior == 'byPath') or (library_matching_behavior == 'byNetworkPath')) and (libInfoPrinted)):
                        libInfoPrinted=False
                        j += 1
                if ((library_matching_behavior == 'byId') and (libInfoPrinted)):
                    libInfoPrinted=False
                    j += 1

        #Go thru channels this user has permissions to access and show them on the screen
        #for libChannel in data_channels:
            #if (('Id' in libChannel) and ('Type' in libChannel) and ((enabledFolderIds_set == set()) or (libChannel['Id'] in enabledFolderIds_set))):
                #if not (libChannel['Id'] in library_tracker):
                    #print(str(j) + ' - ' + libChannel['Name'] + ' - ' + libChannel['Type'] + ' - LibId: ' + libChannel['Id'])
                #else:
                    #show blank entry
                    #print(str(j) + ' - ' + libChannel['Name'] + ' - ' )
                #if not ('userid' in libraryTemp_dict):
                    #libraryTemp_dict['userid']=user_id
                #libraryTemp_dict[j]['libid']=libChannel['Id']
                #libraryTemp_dict[j]['collectiontype']=libChannel['Type']
                #libraryTemp_dict[j]['path']=''
                #libraryTemp_dict[j]['networkpath']=''
            #j += 1

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
                                            if ((library_matching_behavior == 'byId') and (libraryTemp_dict[showpos]['libid'] == libraryTemp_dict[checkallpos]['libid'])):
                                                libMatchFound=True
                                                library_dict[checkallpos]['libid']=libraryTemp_dict[checkallpos]['libid']
                                                library_dict[checkallpos]['collectiontype']=libraryTemp_dict[checkallpos]['collectiontype']
                                                library_dict[checkallpos]['path']=libraryTemp_dict[checkallpos]['path']
                                                library_dict[checkallpos]['networkpath']=libraryTemp_dict[checkallpos]['networkpath']
                                            elif ((library_matching_behavior == 'byPath') and (libraryTemp_dict[showpos]['path'] == libraryTemp_dict[checkallpos]['path'])):
                                                libMatchFound=True
                                                library_dict[checkallpos]['libid']=libraryTemp_dict[checkallpos]['libid']
                                                library_dict[checkallpos]['collectiontype']=libraryTemp_dict[checkallpos]['collectiontype']
                                                library_dict[checkallpos]['path']=libraryTemp_dict[checkallpos]['path']
                                                library_dict[checkallpos]['networkpath']=libraryTemp_dict[checkallpos]['networkpath']
                                            elif ((library_matching_behavior == 'byNetworkPath') and (libraryTemp_dict[showpos]['networkpath'] == libraryTemp_dict[checkallpos]['networkpath'])):
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
                                                if (( not (library_dict[checkallpos].get('libid') == '')) and (library_matching_behavior == 'byId')):
                                                    library_tracker.append(library_dict[checkallpos]['libid'])
                                                elif (( not (library_dict[checkallpos].get('path') == '')) and (library_matching_behavior == 'byPath')):
                                                    library_tracker.append(library_dict[checkallpos]['path'])
                                                elif (( not (library_dict[checkallpos].get('networkpath') == '')) and (library_matching_behavior == 'byNetworkPath')):
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
def get_users_and_libraries(server_url,auth_key,library_setup_behavior,updateConfig,library_matching_behavior):
    #Get all users
    req=(server_url + '/Users?api_key=' + auth_key)

    #preConfigDebug = True
    preConfigDebug = False

    #api call
    data=requestURL(req, preConfigDebug, 'get_users', 3)

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
    #user_bl_libs_json=''
    #user_wl_libs_json=''

    #Check if not running for the first time
    if (updateConfig):
        #Build the library data from the data structures stored in the configuration file
        bluser_keys_json_verify,bluser_names_json_verify,user_bllib_keys_json,user_bllib_collectiontype_json,user_bllib_netpath_json,user_bllib_path_json=user_lib_builder(cfg.user_bl_libs)
        #Build the library data from the data structures stored in the configuration file
        wluser_keys_json_verify,wluser_names_json_verify,user_wllib_keys_json,user_wllib_collectiontype_json,user_wllib_netpath_json,user_wllib_path_json=user_lib_builder(cfg.user_wl_libs)

        #verify userIds are in same order for both blacklist and whitelist libraries
        if (bluser_keys_json_verify == wluser_keys_json_verify):
            user_keys_json = bluser_keys_json_verify
        else:
            raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both')

        #verify userNames are in same order for both blacklist and whitelist libraries
        if (not (bluser_names_json_verify == wluser_names_json_verify)):
            raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userNames need to be in the same order for both')

        i=0
        usernames_userkeys=json.loads(cfg.user_keys)
        #Pre-populate the existing userkeys and libraries; only new users are fully shown; existing user will display minimal info
        for rerun_userkey in user_keys_json:
            userId_set.add(rerun_userkey)
            if (rerun_userkey == bluser_keys_json_verify[i]):
                userId_bllib_dict[rerun_userkey]=json.loads(cfg.user_bl_libs)[i]
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
                userId_wllib_dict[rerun_userkey]=json.loads(cfg.user_wl_libs)[i]
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
                if (library_setup_behavior == 'blacklist'):
                    message='Enter number of the library folder to blacklist (aka monitor) for the selected user.\nMedia in blacklisted library folder(s) will be monitored for deletion.'
                    userId_wllib_dict[userId_dict[user_number_int]],userId_bllib_dict[userId_dict[user_number_int]]=get_library_folders(server_url,auth_key,message,data[user_number_int]['Policy'],data[user_number_int]['Id'],data[user_number_int]['Name'],False,library_matching_behavior)
                else: #(library_setup_behavior == 'whitelist'):
                    message='Enter number of the library folder to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                    userId_bllib_dict[userId_dict[user_number_int]],userId_wllib_dict[userId_dict[user_number_int]]=get_library_folders(server_url,auth_key,message,data[user_number_int]['Policy'],data[user_number_int]['Id'],data[user_number_int]['Name'],False,library_matching_behavior)

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
                    if (updateConfig):
                        userId_ReRun_set.add(userId_dict[user_number_int])

                    #Depending on library setup behavior the chosen libraries will either be treated as blacklisted libraries or whitelisted libraries
                    if (library_setup_behavior == 'blacklist'):
                        message='Enter number of the library folder to blacklist (aka monitor) for the selected user.\nMedia in blacklisted library folder(s) will be monitored for deletion.'
                        userId_wllib_dict[userId_dict[user_number_int]],userId_bllib_dict[userId_dict[user_number_int]]=get_library_folders(server_url,auth_key,message,data[user_number_int]['Policy'],data[user_number_int]['Id'],data[user_number_int]['Name'],False,library_matching_behavior)
                    else: #(library_setup_behavior == 'whitelist'):
                        message='Enter number of the library folder to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                        userId_bllib_dict[userId_dict[user_number_int]],userId_wllib_dict[userId_dict[user_number_int]]=get_library_folders(server_url,auth_key,message,data[user_number_int]['Policy'],data[user_number_int]['Id'],data[user_number_int]['Name'],False,library_matching_behavior)

                    if ((len(userId_set) >= i) and (not updateConfig)):
                        stop_loop=True
                    elif ((len(userId_ReRun_set) >= i) and (updateConfig)):
                        stop_loop=True
                    else:
                        stop_loop=False
                else:
                    print('\nInvalid value. Try again.\n')
            else:
                print('\nInvalid value. Try again.\n')
        except:
            print('\nInvalid value. Try again.\n')

    return(userId_bllib_dict, userId_wllib_dict)


def change_working_directory(cwd):
    #Determine script directory
    script_dir = os.path.dirname(__file__)

    if (script_dir == ''):
        #script was likely run from the cwd
        #set script_dir to cwd (aka this directory) to prevent error when attempting to change to '' (aka a blank directory)
        script_dir=cwd

    #Change to script's directory
    os.chdir(script_dir)

    return script_dir

#Save file to the directory this script is running from
def save_file(dataInput,fileName,fileCreateType):
    #Create file next to the script even when cwd (Current Working Directory) is not the same
    #Get CWD
    cwd = os.getcwd()
    #Get script's directory
    script_dir = change_working_directory(cwd)
    #Open file in script's directory
    f = open(fileName, fileCreateType)
    #Write to file
    f.write(dataInput)
    #Close file
    f.close()
    #Change back to original working directory
    os.chdir(cwd)

#get user input needed to build or edit the mumc_config.py file
def build_configuration_file(cfg,updateConfig):

    print('-----------------------------------------------------------')
    print('Version: ' + get_script_version())

    #Building the config
    if not (updateConfig):
        print('-----------------------------------------------------------')
        #ask user for server brand (i.e. emby or jellyfin)
        server_brand=get_brand()

        print('-----------------------------------------------------------')
        #ask user for server's url
        server=get_url()
        print('-----------------------------------------------------------')
        #ask user for the emby or jellyfin port number
        port=get_port()
        print('-----------------------------------------------------------')
        #ask user for url-base
        server_base=get_base(server_brand)
        if (len(port)):
            server_url=server + ':' + port + '/' + server_base
        else:
            server_url=server + '/' + server_base
        print('-----------------------------------------------------------')

        #ask user for administrator username
        username=get_admin_username()
        print('-----------------------------------------------------------')
        #ask user for administrator password
        password=get_admin_password()
        print('-----------------------------------------------------------')
        #ask server for authentication key using administrator username and password
        auth_key=get_authentication_key(server_url, username, password, server_brand)

        #ask user how they want to choose libraries/folders
        library_setup_behavior=get_library_setup_behavior(None)
        print('-----------------------------------------------------------')

        #ask user how they want media items to be matched to libraries/folders
        library_matching_behavior=get_library_matching_behavior(None)
        print('-----------------------------------------------------------')

        #Initialize for compare with other tag to prevent using the same tag in both blacktag and whitetag
        blacktag=''
        whitetag=''

        #ask user for blacktag(s)
        blacktag=get_tag_name('blacktag',whitetag)
        print('-----------------------------------------------------------')

        #ask user for whitetag(s)
        whitetag=get_tag_name('whitetag',blacktag)
        print('-----------------------------------------------------------')

        #run the user and library selector; ask user to select user and associate desired libraries to be monitored for each
        user_keys_and_bllibs,user_keys_and_wllibs=get_users_and_libraries(server_url,auth_key,library_setup_behavior,updateConfig,library_matching_behavior)
        print('-----------------------------------------------------------')

        #ask user for number of days to wait before attempting to delete movie
        #movie_played_days = get_condition_days('movie')
        #print('-----------------------------------------------------------')
        #ask user for number of days to wait before attempting to delete episode
        #episode_played_days = get_condition_days('episode')
        #print('-----------------------------------------------------------')
        #ask user for number of days to wait before attempting to delete audio track
        #audio_played_days = get_condition_days('audio')
        #if (server_brand == 'jellyfin'):
            #print('-----------------------------------------------------------')
            #ask user for number of days to wait before attempting to delete audiobook track
            #audiobook_played_days = get_condition_days('audiobook')

        #set REMOVE_FILES
        REMOVE_FILES=False

    #Updating the config; Prepare to run the config editor
    else: #(Update_Config):
        print('-----------------------------------------------------------')
        #ask user how they want to choose libraries/folders
        library_setup_behavior=get_library_setup_behavior(cfg.library_setup_behavior)
        print('-----------------------------------------------------------')
        #ask user how they want media items to be matched to libraries/folders
        library_matching_behavior=get_library_matching_behavior(cfg.library_matching_behavior)
        print('-----------------------------------------------------------')
        #set auth_key to allow printing username next to userkey
        auth_key=cfg.auth_key
        #run the user and library selector; ask user to select user and associate desired libraries to be monitored for each
        user_keys_and_bllibs,user_keys_and_wllibs=get_users_and_libraries(cfg.server_url,auth_key,library_setup_behavior,updateConfig,library_matching_behavior)

        #get the server brand so it can be used when updating the config to exculed audiobook type when server_brand == 'emby'
        server_brand=cfg.server_brand

    userkeys_bllibs_list=[]
    userbllibs_list=[]
    userkeys_wllibs_list=[]
    userwllibs_list=[]

    #Attach userkeys to blacklist library data structure
    for userkey, userbllib in user_keys_and_bllibs.items():
        #Get all users
        userkeys_bllibs_list.append(userbllib['username'] + ':' + userkey)
        userbllibs_list.append(userbllib)

    #Attach userkeys to whitelist library data structure
    for userkey, userwllib in user_keys_and_wllibs.items():
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
    config_file += "# Condition Days: Delete media items last played or created at least this many days ago\n"
    config_file += "#   0-730500 - Number of days filter will use to determine when the media items was\n"
    config_file += "#              last played or when the media item was created\n"
    config_file += "#  -1 - To disable deleting specified media type\n"
    config_file += "# (-1 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "movie_played_days=" + str(get_default_config_values('movie_played_days')) + "\n"
        config_file += "movie_created_days=" + str(get_default_config_values('movie_created_days')) + "\n"
        config_file += "\n"
        config_file += "episode_played_days=" + str(get_default_config_values('episode_played_days')) + "\n"
        config_file += "episode_created_days=" + str(get_default_config_values('episode_created_days')) + "\n"
        config_file += "\n"
        config_file += "audio_played_days=" + str(get_default_config_values('audio_played_days')) + "\n"
        config_file += "audio_created_days=" + str(get_default_config_values('audio_created_days')) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "\n"
            config_file += "audiobook_played_days=" + str(get_default_config_values('audiobook_played_days')) + "\n"
            config_file += "audiobook_created_days=" + str(get_default_config_values('audiobook_created_days')) + "\n"
    elif (updateConfig):
        config_file += "movie_played_days=" + str(cfg.movie_played_days) + "\n"
        config_file += "movie_created_days=" + str(cfg.movie_created_days) + "\n"
        config_file += "\n"
        config_file += "episode_played_days=" + str(cfg.episode_played_days) + "\n"
        config_file += "episode_created_days=" + str(cfg.episode_created_days) + "\n"
        config_file += "\n"
        config_file += "audio_played_days=" + str(cfg.audio_played_days) + "\n"
        config_file += "audio_created_days=" + str(cfg.audio_created_days) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "\n"
            config_file += "audiobook_played_days=" + str(cfg.audiobook_played_days) + "\n"
            config_file += "audiobook_created_days=" + str(cfg.audiobook_created_days) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Play Count Inequality: Delete media items within this range based off of the chosen *_played_count.\n"
    config_file += "#   > - Filter media items last played or created with a play count greater than *_played_count days ago\n"
    config_file += "#   < - Filter media items last played or created with a play count less than *_played_count days ago\n"
    config_file += "#   >= - Filter media items last played or created with a play count greater than or equal to *_played_count days ago\n"
    config_file += "#   <= - Filter media items last played or created with a play count less than or equal to *_played_count days ago\n"
    config_file += "#   == - Filter media items last played or created with a play count equal to *_played_count days ago\n"
    config_file += "#   not > - Filter media items last played or created with a play count not greater than *_played_count days ago\n"
    config_file += "#   not < - Filter media items last played or created with a play count not less than *_played_count days ago\n"
    config_file += "#   not >= - Filter media items last played or created with a play count not greater than or equal to *_played_count days ago\n"
    config_file += "#   not <= - Filter media items last played or created with a play count not less than or equal to *_played_count days ago\n"
    config_file += "#   not == - Filter media items last played or created with a play count not equal to *_played_count days ago\n"
    config_file += "# (>= : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "movie_played_count_comparison='" + get_default_config_values('movie_played_count_comparison') + "'\n"
        config_file += "movie_created_played_count_comparison='" + get_default_config_values('movie_created_played_count_comparison') + "'\n"
        config_file += "\n"
        config_file += "episode_played_count_comparison='" + get_default_config_values('episode_played_count_comparison') + "'\n"
        config_file += "episode_created_played_count_comparison='" + get_default_config_values('episode_created_played_count_comparison') + "'\n"
        config_file += "\n"
        config_file += "audio_played_count_comparison='" + get_default_config_values('audio_played_count_comparison') + "'\n"
        config_file += "audio_created_played_count_comparison='" + get_default_config_values('audio_created_played_count_comparison') + "'\n"
        if (server_brand == 'jellyfin'):
            config_file += "\n"
            config_file += "audiobook_played_count_comparison='" + get_default_config_values('audiobook_played_count_comparison') + "'\n"
            config_file += "audiobook_created_played_count_comparison='" + get_default_config_values('audiobook_created_played_count_comparison') + "'\n"
    elif (updateConfig):
        config_file += "movie_played_count_comparison='" + cfg.movie_played_count_comparison + "'\n"
        config_file += "movie_created_played_count_comparison='" + cfg.movie_created_played_count_comparison + "'\n"
        config_file += "\n"
        config_file += "episode_played_count_comparison='" + cfg.episode_played_count_comparison + "'\n"
        config_file += "episode_created_played_count_comparison='" + cfg.episode_created_played_count_comparison + "'\n"
        config_file += "\n"
        config_file += "audio_played_count_comparison='" + cfg.audio_played_count_comparison + "'\n"
        config_file += "audio_created_played_count_comparison='" + cfg.audio_created_played_count_comparison + "'\n"
        if (server_brand == 'jellyfin'):
            config_file += "\n"
            config_file += "audiobook_played_count_comparison='" + cfg.audiobook_played_count_comparison + "'\n"
            config_file += "audiobook_created_played_count_comparison='" + cfg.audiobook_created_played_count_comparison + "'\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Play Count: Delete media items with a play count relative to this number.\n"
    config_file += "#   0-730500 - Number of times a media item has been played\n"
    config_file += "# (1 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "movie_played_count=" + str(get_default_config_values('movie_played_count')) + "\n"
        config_file += "movie_created_played_count=" + str(get_default_config_values('movie_created_played_count')) + "\n"
        config_file += "\n"
        config_file += "episode_played_count=" + str(get_default_config_values('episode_played_count')) + "\n"
        config_file += "episode_created_played_count=" + str(get_default_config_values('episode_created_played_count')) + "\n"
        config_file += "\n"
        config_file += "audio_played_count=" + str(get_default_config_values('audio_played_count')) + "\n"
        config_file += "audio_created_played_count=" + str(get_default_config_values('audio_created_played_count')) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "\n"
            config_file += "audiobook_played_count=" + str(get_default_config_values('audiobook_played_count')) + "\n"
            config_file += "audiobook_created_played_count=" + str(get_default_config_values('audiobook_created_played_count')) + "\n"
    elif (updateConfig):
        config_file += "movie_played_count=" + str(cfg.movie_played_count) + "\n"
        config_file += "movie_created_played_count=" + str(cfg.movie_created_played_count) + "\n"
        config_file += "\n"
        config_file += "episode_played_count=" + str(cfg.episode_played_count) + "\n"
        config_file += "episode_created_played_count=" + str(cfg.episode_created_played_count) + "\n"
        config_file += "\n"
        config_file += "audio_played_count=" + str(cfg.audio_played_count) + "\n"
        config_file += "audio_created_played_count=" + str(cfg.audio_created_played_count) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "\n"
            config_file += "audiobook_played_count=" + str(cfg.audiobook_played_count) + "\n"
            config_file += "audiobook_created_played_count=" + str(cfg.audiobook_created_played_count) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#------------Advanced Config Options Start Here-------------#\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide how play count with multiple users will behave\n"
    config_file += "#  0 - ok to delete media item when ANY monitored users meet the *_play_count_comparison and *_play_count\n"
    config_file += "#  1 - ok to delete media item when ALL monitored users meet the *_play_count_comparison and *_play_count\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "multiuser_play_count_movie=" + str(get_default_config_values('multiuser_play_count_movie')) + "\n"
        config_file += "multiuser_play_count_episode=" + str(get_default_config_values('multiuser_play_count_episode')) + "\n"
        config_file += "multiuser_play_count_audio=" + str(get_default_config_values('multiuser_play_count_audio')) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "multiuser_play_count_audiobook=" + str(get_default_config_values('multiuser_play_count_audiobook')) + "\n"
    elif (updateConfig):
        config_file += "multiuser_play_count_movie=" + str(cfg.multiuser_play_count_movie) + "\n"
        config_file += "multiuser_play_count_episode=" + str(cfg.multiuser_play_count_episode) + "\n"
        config_file += "multiuser_play_count_audio=" + str(cfg.multiuser_play_count_audio) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "multiuser_play_count_audiobook=" + str(cfg.multiuser_play_count_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide if media set as a favorite should be deleted\n"
    config_file += "# Favoriting a series, season, or network-channel will treat all child episodes as if they are favorites\n"
    config_file += "# Favoriting an artist, album-artist, or album will treat all child tracks as if they are favorites\n"
    config_file += "# Similar logic applies for other media types (movies, audio books, etc...)\n"
    config_file += "#  0 - ok to delete media items set as a favorite\n"
    config_file += "#  1 - when single user - do not delete media items when set as a favorite; when multi-user - do not delete media item when all monitored users have set it as a favorite\n"
    config_file += "#  2 - when single user - not applicable; when multi-user - do not delete media item when any monitored users have it set as a favorite\n"
    config_file += "# (1 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "keep_favorites_movie=" + str(get_default_config_values('keep_favorites_movie')) + "\n"
        config_file += "keep_favorites_episode=" + str(get_default_config_values('keep_favorites_episode')) + "\n"
        config_file += "keep_favorites_audio=" + str(get_default_config_values('keep_favorites_audio')) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "keep_favorites_audiobook=" + str(get_default_config_values('keep_favorites_audiobook')) + "\n"
    elif (updateConfig):
        config_file += "keep_favorites_movie=" + str(cfg.keep_favorites_movie) + "\n"
        config_file += "keep_favorites_episode=" + str(cfg.keep_favorites_episode) + "\n"
        config_file += "keep_favorites_audio=" + str(cfg.keep_favorites_audio) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "keep_favorites_audiobook=" + str(cfg.keep_favorites_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide how whitelists with multiple users behave\n"
    config_file += "#  0 - do not delete media item when ANY monitored users have the parent library whitelisted\n"
    config_file += "#  1 - do not delete media item when ALL monitored users have the parent library whitelisted\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "multiuser_whitelist_movie=" + str(get_default_config_values('multiuser_whitelist_movie')) + "\n"
        config_file += "multiuser_whitelist_episode=" + str(get_default_config_values('multiuser_whitelist_episode')) + "\n"
        config_file += "multiuser_whitelist_audio=" + str(get_default_config_values('multiuser_whitelist_audio')) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "multiuser_whitelist_audiobook=" + str(get_default_config_values('multiuser_whitelist_audiobook')) + "\n"
    elif (updateConfig):
        config_file += "multiuser_whitelist_movie=" + str(cfg.multiuser_whitelist_movie) + "\n"
        config_file += "multiuser_whitelist_episode=" + str(cfg.multiuser_whitelist_episode) + "\n"
        config_file += "multiuser_whitelist_audio=" + str(cfg.multiuser_whitelist_audio) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "multiuser_whitelist_audiobook=" + str(cfg.multiuser_whitelist_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# User entered blacktag name; chosen during setup\n"
    config_file += "#  Use a comma \',\' to seperate multiple tag names\n"
    config_file += "#   Ex: tagname,tag name,tag-name\n"
    config_file += "#  Backslash \'\\\' not allowed\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "blacktag='" + blacktag + "'\n"
    elif (updateConfig):
        config_file += "blacktag='" + cfg.blacktag + "'\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide when blacktagged media items are deleted\n"
    config_file += "#  0 - ok to delete blacktagged media item after ANY monitored user has watched it\n"
    config_file += "#  1 - ok to delete blacktagged media item after ALL monitored users have watched it\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "delete_blacktagged_movie=" + str(get_default_config_values('delete_blacktagged_movie')) + "\n"
        config_file += "delete_blacktagged_episode=" + str(get_default_config_values('delete_blacktagged_episode')) + "\n"
        config_file += "delete_blacktagged_audio=" + str(get_default_config_values('delete_blacktagged_audio')) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "delete_blacktagged_audiobook=" + str(get_default_config_values('delete_blacktagged_audiobook')) + "\n"
    elif (updateConfig):
        config_file += "delete_blacktagged_movie=" + str(cfg.delete_blacktagged_movie) + "\n"
        config_file += "delete_blacktagged_episode=" + str(cfg.delete_blacktagged_episode) + "\n"
        config_file += "delete_blacktagged_audio=" + str(cfg.delete_blacktagged_audio) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "delete_blacktagged_audiobook=" + str(cfg.delete_blacktagged_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# User entered whitetag name; chosen during setup\n"
    config_file += "#  Use a comma \',\' to seperate multiple tag names\n"
    config_file += "#   Ex: tagname,tag name,tag-name\n"
    config_file += "#  Backslash \'\\\' not allowed\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "whitetag='" + whitetag + "'\n"
    elif (updateConfig):
        config_file += "whitetag='" + cfg.whitetag + "'\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide the minimum number of episodes to remain in all tv series'\n"
    config_file += "# This ignores the played and unplayed states of episodes\n"
    config_file += "#  0 - Episodes will be deleted based on the Filter Statement\n"
    config_file += "#  1-730500 - Episodes will be deleted based on the Filter Statement; unless\n"
    config_file += "#              the remaining played and unplayed episodes are less than or equal\n"
    config_file += "#              to the chosen value\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "minimum_number_episodes=" + str(get_default_config_values('minimum_number_episodes')) + "\n"
    elif (updateConfig):
        config_file += "minimum_number_episodes=" + str(cfg.minimum_number_episodes) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide the minimum number of played episodes to remain in all tv series'\n"
    config_file += "# Keeping one or more played epsiodes for each series allows the \"Next Up\"\n"
    config_file += "#  functionality to notify user(s) when a new episode for a series\n"
    config_file += "#  is available\n"
    config_file += "# This value applies only to played and episodes\n"
    config_file += "#  0 - Episodes will be deleted based on the Filter Statement\n"
    config_file += "#  1-730500 - Episodes will be deleted based on the Filter Statement; unless\n"
    config_file += "#              the remaining played episodes are less than or equal to the\n"
    config_file += "#              chosen value\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "minimum_number_played_episodes=" + str(get_default_config_values('minimum_number_played_episodes')) + "\n"
    elif (updateConfig):
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
    config_file += "#                                based off the user with the lowest number of played episoded to be\n"
    config_file += "#                                deleted for a specified series.\n"
    config_file += "# ('Min Played Min Unplayed' : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "minimum_number_episodes_behavior='" + str(get_default_config_values('minimum_number_episodes_behavior')) + "'\n"
    elif (updateConfig):
        config_file += "minimum_number_episodes_behavior='" + str(cfg.minimum_number_episodes_behavior) + "'\n"
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
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Advanced movie genre configurations\n"
    config_file += "#     Requires 'keep_favorites_movie=1'\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "#  Keep movie based on the genres\n"
    config_file += "#  0 - ok to delete movie when genres are set as a favorite\n"
    config_file += "#  1 - keep movie if FIRST genre listed is set as a favorite\n"
    config_file += "#  2 - keep movie if ANY genre listed is set as a favorite\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "keep_favorites_advanced_movie_genre=" + str(get_default_config_values('keep_favorites_advanced_movie_genre')) + "\n"
        config_file += "keep_favorites_advanced_movie_library_genre=" + str(get_default_config_values('keep_favorites_advanced_movie_library_genre')) + "\n"
    elif (updateConfig):
        config_file += "keep_favorites_advanced_movie_genre=" + str(cfg.keep_favorites_advanced_movie_genre) + "\n"
        config_file += "keep_favorites_advanced_movie_library_genre=" + str(cfg.keep_favorites_advanced_movie_library_genre) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Advanced episode genre/studio-network configurations\n"
    config_file += "#     Requires 'keep_favorites_episode=1'\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "#  Keep episode based on the genre(s) or studio-network(s)\n"
    config_file += "#  0 - ok to delete episode when its genres or studio-networks are set as a favorite\n"
    config_file += "#  1 - keep episode if FIRST genre or studio-network is set as a favorite\n"
    config_file += "#  2 - keep episode if ANY genres or studio-networks are set as a favorite\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "keep_favorites_advanced_episode_genre=" + str(get_default_config_values('keep_favorites_advanced_episode_genre')) + "\n"
        config_file += "keep_favorites_advanced_season_genre=" + str(get_default_config_values('keep_favorites_advanced_season_genre')) + "\n"
        config_file += "keep_favorites_advanced_series_genre=" + str(get_default_config_values('keep_favorites_advanced_series_genre')) + "\n"
        config_file += "keep_favorites_advanced_tv_library_genre=" + str(get_default_config_values('keep_favorites_advanced_tv_library_genre')) + "\n"
        config_file += "keep_favorites_advanced_tv_studio_network=" + str(get_default_config_values('keep_favorites_advanced_tv_studio_network')) + "\n"
        config_file += "keep_favorites_advanced_tv_studio_network_genre=" + str(get_default_config_values('keep_favorites_advanced_tv_studio_network_genre')) + "\n"
    elif (updateConfig):
        config_file += "keep_favorites_advanced_episode_genre=" + str(cfg.keep_favorites_advanced_episode_genre) + "\n"
        config_file += "keep_favorites_advanced_season_genre=" + str(cfg.keep_favorites_advanced_season_genre) + "\n"
        config_file += "keep_favorites_advanced_series_genre=" + str(cfg.keep_favorites_advanced_series_genre) + "\n"
        config_file += "keep_favorites_advanced_tv_library_genre=" + str(cfg.keep_favorites_advanced_tv_library_genre) + "\n"
        config_file += "keep_favorites_advanced_tv_studio_network=" + str(cfg.keep_favorites_advanced_tv_studio_network) + "\n"
        config_file += "keep_favorites_advanced_tv_studio_network_genre=" + str(cfg.keep_favorites_advanced_tv_studio_network_genre) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Advanced track genre/artist configurations\n"
    config_file += "#     Requires 'keep_favorites_audio=1'\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "#  Keep track based on the genre(s) or artist(s)\n"
    config_file += "#  0 - ok to delete track when its genres or artists are set as a favorite\n"
    config_file += "#  1 - keep track if FIRST genre or artist is set as a favorite\n"
    config_file += "#  2 - keep track if ANY genres or artists are set as a favorite\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "keep_favorites_advanced_track_genre=" + str(get_default_config_values('keep_favorites_advanced_track_genre')) + "\n"
        config_file += "keep_favorites_advanced_album_genre=" + str(get_default_config_values('keep_favorites_advanced_album_genre')) + "\n"
        config_file += "keep_favorites_advanced_music_library_genre=" + str(get_default_config_values('keep_favorites_advanced_music_library_genre')) + "\n"
        config_file += "keep_favorites_advanced_track_artist=" + str(get_default_config_values('keep_favorites_advanced_track_artist')) + "\n"
        config_file += "keep_favorites_advanced_album_artist=" + str(get_default_config_values('keep_favorites_advanced_album_artist')) + "\n"
    elif (updateConfig):
        config_file += "keep_favorites_advanced_track_genre=" + str(cfg.keep_favorites_advanced_track_genre) + "\n"
        config_file += "keep_favorites_advanced_album_genre=" + str(cfg.keep_favorites_advanced_album_genre) + "\n"
        config_file += "keep_favorites_advanced_music_library_genre=" + str(cfg.keep_favorites_advanced_music_library_genre) + "\n"
        config_file += "keep_favorites_advanced_track_artist=" + str(cfg.keep_favorites_advanced_track_artist) + "\n"
        config_file += "keep_favorites_advanced_album_artist=" + str(cfg.keep_favorites_advanced_album_artist) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    if (server_brand == 'jellyfin'):
        config_file += "\n"
        config_file += "#----------------------------------------------------------#\n"
        config_file += "# Advanced audio book track genre/author configurations\n"
        config_file += "#     Requires 'keep_favorites_audiobook=1'\n"
        config_file += "#----------------------------------------------------------#\n"
        config_file += "#  Keep audio book track based on the genres or authors\n"
        config_file += "#  0 - ok to delete audio book track when its genres or authors are set as a favorite\n"
        config_file += "#  1 - keep audio book track if FIRST genre or author is set as a favorite\n"
        config_file += "#  2 - keep audio book track if ANY genres or authors are set as a favorite\n"
        config_file += "# (0 : default)\n"
        config_file += "#----------------------------------------------------------#\n"
        if not (updateConfig):
            config_file += "keep_favorites_advanced_audio_book_track_genre=" + str(get_default_config_values('keep_favorites_advanced_audio_book_track_genre')) + "\n"
            config_file += "keep_favorites_advanced_audio_book_genre=" + str(get_default_config_values('keep_favorites_advanced_audio_book_genre')) + "\n"
            config_file += "keep_favorites_advanced_audio_book_library_genre=" + str(get_default_config_values('keep_favorites_advanced_audio_book_library_genre')) + "\n"
            config_file += "keep_favorites_advanced_audio_book_track_author=" + str(get_default_config_values('keep_favorites_advanced_audio_book_track_author')) + "\n"
            config_file += "keep_favorites_advanced_audio_book_author=" + str(get_default_config_values('keep_favorites_advanced_audio_book_author')) + "\n"
        elif (updateConfig):
            config_file += "keep_favorites_advanced_audio_book_track_genre=" + str(cfg.keep_favorites_advanced_audio_book_track_genre) + "\n"
            config_file += "keep_favorites_advanced_audio_book_genre=" + str(cfg.keep_favorites_advanced_audio_book_genre) + "\n"
            config_file += "keep_favorites_advanced_audio_book_library_genre=" + str(cfg.keep_favorites_advanced_audio_book_library_genre) + "\n"
            config_file += "keep_favorites_advanced_audio_book_track_author=" + str(cfg.keep_favorites_advanced_audio_book_track_author) + "\n"
            config_file += "keep_favorites_advanced_audio_book_author=" + str(cfg.keep_favorites_advanced_audio_book_author) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Enable/Disable console outputs by type\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "#  Should the script print its output to the console\n"
    config_file += "#  False - Do not print this output type to the console\n"
    config_file += "#  True - Print this output type to the console\n"
    config_file += "# (True : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "print_script_header=" + str(get_default_config_values('print_script_header')) + "\n"
        config_file += "print_warnings=" + str(get_default_config_values('print_warnings')) + "\n"
        config_file += "print_user_header=" + str(get_default_config_values('print_user_header')) + "\n"
        config_file += "print_movie_delete_info=" + str(get_default_config_values('print_movie_delete_info')) + "\n"
        config_file += "print_movie_keep_info=" + str(get_default_config_values('print_movie_keep_info')) + "\n"
        config_file += "print_episode_delete_info=" + str(get_default_config_values('print_episode_delete_info')) + "\n"
        config_file += "print_episode_keep_info=" + str(get_default_config_values('print_episode_keep_info')) + "\n"
        config_file += "print_audio_delete_info=" + str(get_default_config_values('print_audio_delete_info')) + "\n"
        config_file += "print_audio_keep_info=" + str(get_default_config_values('print_audio_keep_info')) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "print_audiobook_delete_info=" + str(get_default_config_values('print_audiobook_delete_info')) + "\n"
            config_file += "print_audiobook_keep_info=" + str(get_default_config_values('print_audiobook_keep_info')) + "\n"
        config_file += "print_summary_header=" + str(get_default_config_values('print_summary_header')) + "\n"
        config_file += "print_movie_summary=" + str(get_default_config_values('print_movie_summary')) + "\n"
        config_file += "print_episode_summary=" + str(get_default_config_values('print_episode_summary')) + "\n"
        config_file += "print_audio_summary=" + str(get_default_config_values('print_audio_summary')) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "print_audiobook_summary=" + str(get_default_config_values('print_audiobook_summary')) + "\n"
    elif (updateConfig):
        config_file += "print_script_header=" + str(cfg.print_script_header) + "\n"
        config_file += "print_warnings=" + str(cfg.print_warnings) + "\n"
        config_file += "print_user_header=" + str(cfg.print_user_header) + "\n"
        config_file += "print_movie_delete_info=" + str(cfg.print_movie_delete_info) + "\n"
        config_file += "print_movie_keep_info=" + str(cfg.print_movie_keep_info) + "\n"
        config_file += "print_episode_delete_info=" + str(cfg.print_episode_delete_info) + "\n"
        config_file += "print_episode_keep_info=" + str(cfg.print_episode_keep_info) + "\n"
        config_file += "print_audio_delete_info=" + str(cfg.print_audio_delete_info) + "\n"
        config_file += "print_audio_keep_info=" + str(cfg.print_audio_keep_info) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "print_audiobook_delete_info=" + str(cfg.print_audiobook_delete_info) + "\n"
            config_file += "print_audiobook_keep_info=" + str(cfg.print_audiobook_keep_info) + "\n"
        config_file += "print_summary_header=" + str(cfg.print_summary_header) + "\n"
        config_file += "print_movie_summary=" + str(cfg.print_movie_summary) + "\n"
        config_file += "print_episode_summary=" + str(cfg.print_episode_summary) + "\n"
        config_file += "print_audio_summary=" + str(cfg.print_audio_summary) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "print_audiobook_summary=" + str(cfg.print_audiobook_summary) + "\n"
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
    if not (updateConfig):
        config_file += "UPDATE_CONFIG=False\n"
    elif (updateConfig):
        config_file += "UPDATE_CONFIG=" + str(cfg.UPDATE_CONFIG) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#---------!!!DO NOT MODIFY ANYTHING BELOW!!!----------------#\n"
    config_file += "# These are automatically created during setup.\n"
    config_file += "#   If you do not know EXACTLY what you are doing changing these\n"
    config_file += "#      can and will cause script failure.\n"
    config_file += "#   The only way to recover from script failure is to revert the\n"
    config_file += "#      config back to the way it was OR rebuilding a new config.\n"
    config_file += "#----------------------------------------------------------#\n"
    #config_file += "#----------------------------------------------------------#\n"    
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Server branding; chosen during setup\n"
    config_file += "#  0 - 'emby'\n"
    config_file += "#  1 - 'jellyfin'\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "server_brand='" + server_brand + "'\n"
    elif (updateConfig):
        config_file += "server_brand='" + cfg.server_brand + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Server URL; created during setup\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "server_url='" + server_url + "'\n"
    elif (updateConfig):
        config_file += "server_url='" + cfg.server_url + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Authentication Key; requested from server during setup\n"
    config_file += "#  Used for API queries sent to the server\n"
    config_file += "#  Also know as an Access Token\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "auth_key='" + auth_key + "'\n"
    elif (updateConfig):
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
    config_file += "library_setup_behavior='" + library_setup_behavior + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide how the script will match media items to libraries\n"
    config_file += "#  0 - byId - Media items will be matched to libraries using \'LibraryIds\'\n"
    config_file += "#  1 - byPath - Media items will be matched to libraries using \'Paths\'\n"
    config_file += "#  2 - byNetwork Path - Media items will be matched to libraries using \'NetworkPaths\'\n"
    config_file += "# (byId : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "library_matching_behavior='" + library_matching_behavior + "'\n"
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
    if not (updateConfig):
        config_file += "api_query_attempts=4\n"
    elif (updateConfig):
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
    if not (updateConfig):
        config_file += "api_query_item_limit=25\n"
    elif (updateConfig):
        config_file += "api_query_item_limit=" + str(cfg.api_query_item_limit) + "\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Must be a boolean True or False value\n"
    config_file += "# False - Debug messages disabled\n"
    config_file += "# True - Debug messages enabled\n"
    config_file += "# (False : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "DEBUG=False\n"
    elif (updateConfig):
        config_file += "DEBUG=" + str(cfg.DEBUG) + "\n"
    config_file += "\n"
    config_file += "#-------------End Config Options----------------------------#"

    #Save the config file to the directory this script is running from
    #save_file(config_file)
    save_file(config_file,GLOBAL_configFileName,"w")

    #Check config edditing wasn't requested
    if not (updateConfig):
        try:
            #when all *_condition_days config options are disabled print notification
            if (
                (get_default_config_values('movie_played_days') == -1) and
                (get_default_config_values('movie_created_days') == -1) and
                (get_default_config_values('episode_played_days') == -1) and
                (get_default_config_values('episode_created_days') == -1) and
                (get_default_config_values('audio_played_days') == -1) and
                (get_default_config_values('audio_created_days') == -1) and
                (((server_brand == 'jellyfin') and (get_default_config_values('audiobook_played_days') == -1)) or (server_brand == 'emby')) and
                (((server_brand == 'jellyfin') and (get_default_config_values('audiobook_created_days') == -1)) or (server_brand == 'emby'))
                ):
                    print('\n\n-----------------------------------------------------------')
                    print('Config file is not setup to find media.')
                    print('-----------------------------------------------------------')
                    print('To find media open mumc_config.py in a text editor:')
                    print('    Set \'movie_played_days\' or \'movie_created_days\' to zero or a positive number')
                    print('    Set \'episode_played_days\' or \'episode_created_days\' to zero or a positive number')
                    print('    Set \'audio_played_days\' or \'audio_crated_days\' to zero or a positive number')
                    if (server_brand == 'jellyfin'):
                        print('    Set \'audiobook_played_days\' or \'audiobook_created_days\' to zero or a positive number')
            if not (REMOVE_FILES):
                print('-----------------------------------------------------------')
                print('Config file is not setup to delete media.')
                print('Config file is in dry run mode to prevent deleting media.')
                print('-----------------------------------------------------------')
                print('To delete media open mumc_config.py in a text editor:')
                print('    Set REMOVE_FILES=\'True\'')
            print('-----------------------------------------------------------')
            print('Edit the mumc_config.py file and try running again.')
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
def edit_configuration_file(cfg,updateConfig):
    return build_configuration_file(cfg,updateConfig)


#Get count of days since last played
def get_days_since_played(date_last_played):

    if not ((date_last_played == 'Unplayed') or (date_last_played == 'Unknown')):

        #Get current time
        date_time_now = datetime.utcnow()

        #Keep the year, month, day, hour, minute, and seconds
        #split date_last_played after seconds
        try:
            split_date_micro_tz = date_last_played.split(".")
            date_time_last_played = datetime.strptime(date_last_played, '%Y-%m-%dT%H:%M:%S.' + split_date_micro_tz[1])
        except (ValueError):
            date_time_last_played = 'unknown date time format'

        if not (date_time_last_played == 'unknown date time format'):
            date_time_delta = date_time_now - date_time_last_played
            s_date_time_delta = str(date_time_delta)
            days_since_played = s_date_time_delta.split(' day')[0]
            if ':' in days_since_played:
                days_since_played = 'Played <1 day ago'
            elif days_since_played == '1':
                days_since_played = 'Played ' + days_since_played + ' day ago'
            else:
                days_since_played = 'Played ' + days_since_played + ' days ago'
        else:
            days_since_played='0'

        if (GLOBAL_DEBUG):
            #Double newline for DEBUG log formatting
            print_byType('\n\nCaptured UTC time is: ' + str(date_time_now),False)
            print_byType('\nDate last played or date created is: ' + str(date_last_played),False)
            print_byType('\nFormatted date last played or date created is: ' + str(date_time_last_played),False)
            print_byType('\nMedia item was played or created \'' + days_since_played + '\' day(s) ago',False)
    else:
        days_since_played=date_last_played

        if (GLOBAL_DEBUG):
            print_byType('\nMedia item was played or created \'' + days_since_played + '\' day(s) ago',False)

    return(days_since_played)


#Get count of days since last created
def get_days_since_created(date_last_created):
    return(get_days_since_played(date_last_created).replace('Played', 'Created', 1))


#get season and episode numbers; pad with zeros to make them equal lengths
def get_season_episode(ParentIndexNumber,IndexNumber):

    #convert season number to string
    season_num_str = str(ParentIndexNumber)
    #convert episode number to string
    episode_num_str = str(IndexNumber)

    #Add leading zero to single digit seasons
    if (len(season_num_str) == 1):
        season_num_str = '0' + season_num_str

    #Add leading zero to single digit episodes
    if (len(episode_num_str) == 1):
        episode_num_str = '0' + episode_num_str

    #Pad the season number or episode number with zeros until they are the same length
    while not (len(season_num_str) == len(episode_num_str)):
        #pad episode number when season number is longer
        if (len(episode_num_str) < len(season_num_str)):
            episode_num_str = '0' + episode_num_str
        #pad season number when episode number is longer
        elif (len(episode_num_str) > len(season_num_str)):
            season_num_str = '0' + season_num_str

    #Format the season and episode into something easily readable (i.e. s01.e23)
    formatted_season_episode = 's' + season_num_str + '.e' + episode_num_str

    if (GLOBAL_DEBUG):
        print_byType('\nSeason # is: ' + str(ParentIndexNumber),False)
        print_byType('\nEpisode # is: ' + str(IndexNumber),False)
        print_byType('\nPadded Season #: ' + season_num_str,False)
        print_byType('\nPadded Episode #: ' + episode_num_str,False)
        print_byType('\nFormatted season#.episode# is: ' + str(formatted_season_episode),False)

    return(formatted_season_episode)


#Get isPlayed state for API filtering
def get_isPlayed_FilterValue(filter_played_count_comparison,filter_played_count):

    if (filter_played_count_comparison == '>'):
        #Play counts 1 thru 730500
        isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == '<'):
        if ((filter_played_count == 0) or (filter_played_count == 1)):
            #Play counts 0 and 1
            isPlayed_Filter_Value='False'
        else:
            #Paly counts 0 thru 730499
            isPlayed_Filter_Value=''
    elif (filter_played_count_comparison == '>='):
        if (filter_played_count == 0):
            #Play counts 0 thru 730500
            isPlayed_Filter_Value=''
        else:
            #Play counts 1 thru 730500
            isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == '<='):
        if (filter_played_count == 0):
            #Play count 0
            isPlayed_Filter_Value='False'
        else:
            #Play counts 0 thru 730500
            isPlayed_Filter_Value=''
    elif (filter_played_count_comparison == '=='):
        if (filter_played_count == 0):
            #Play count 0
            isPlayed_Filter_Value='False'
        else:
            #Play count 1 thru 730500
            isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == 'not >'):
        if ((filter_played_count == 0) or (filter_played_count == 1)):
            #Play count 0
            isPlayed_Filter_Value='False'
        else:
            #Play count 1 thru 730499
            isPlayed_Filter_Value=''
    elif (filter_played_count_comparison == 'not <'):
        #Play counts 1 thru 730500
        isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == 'not >='):
        if ((filter_played_count == 0) or (filter_played_count == 1)):
            #Play count 0
            isPlayed_Filter_Value='False'
        else:
            #Play count 1 thru 730499
            isPlayed_Filter_Value=''
    elif (filter_played_count_comparison == 'not <='):
        #Play count 1 thru 730500
        isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == 'not =='):
        if (filter_played_count == 0):
            #Play count 1 thru 730500
            isPlayed_Filter_Value='True'
        else:
            #Play count 0 thru 730500
            isPlayed_Filter_Value=''
    else:
        #Play count comparison unknown
        isPlayed_Filter_Value=''

    if (GLOBAL_DEBUG):
        print_byType("\nIsPlayed IsCreated Filter Value: " + isPlayed_Filter_Value,False)

    return isPlayed_Filter_Value


#Get isPlayed state for API filtering
def get_isCreated_FilterValue(filter_created_played_count_comparison,filter_created_played_count):
    return get_isPlayed_FilterValue(filter_created_played_count_comparison,filter_created_played_count)


def get_isPlayedCreated_FilterValue(isPlayed_Filter_Value,isCreated_Filter_Value):

    if ((isPlayed_Filter_Value == 'False') and (isCreated_Filter_Value == 'False')):
        return isPlayed_Filter_Value
    elif ((isPlayed_Filter_Value == 'True') and (isCreated_Filter_Value == 'True')):
        return isPlayed_Filter_Value
    elif ((isPlayed_Filter_Value == 'disable') and (isCreated_Filter_Value == 'False')):
        return 'False'
    elif ((isPlayed_Filter_Value == 'disable') and (isCreated_Filter_Value == 'True')):
        return 'True'
    elif ((isPlayed_Filter_Value == 'False') and (isCreated_Filter_Value == 'disable')):
        return 'False'
    elif ((isPlayed_Filter_Value == 'True') and (isCreated_Filter_Value == 'disable')):
        return 'True'
    else:
        return ''


#Get children of favorited parents
def getChildren_favoritedMediaItems(user_key,data_Favorited,filter_played_count_comparison,filter_played_count,filter_created_played_count_comparison,filter_created_played_count,APIDebugMsg,played_days,created_days):
    server_url=cfg.server_url
    auth_key=cfg.auth_key
    child_list=[]
    StartIndex=0

    #Loop thru items returned as favorited
    for data in data_Favorited['Items']:

        #Verify media item is a parent (not a child like an episode, movie, or audio)
        if ((data['IsFolder'] == True) or (data['Type'] == 'Book')):

            user_processed_itemsId=set()

            #Initialize api_query_handler() variables for watched child media items
            StartIndex=0
            TotalItems=1
            QueryLimit=1
            QueriesRemaining=True

            if not (data['Id'] == ''):
                #Build query for child media items
                #include all item types; filter applied in first API calls for each media type in get_media_items()
                IncludeItemTypes=''
                FieldsState='Id,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,UserData'
                SortBy='SeriesName,AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                SortOrder='Ascending'
                Recursive='True'
                EnableImages='False'
                CollapseBoxSetItems='False'
                if (played_days >= 0):
                    IsPlayedState=get_isPlayed_FilterValue(filter_played_count_comparison,filter_played_count)
                else:
                    IsPlayedState='disable'
                if (created_days >= 0):
                    IsCreatedState=get_isCreated_FilterValue(filter_created_played_count_comparison,filter_created_played_count)
                else:
                    IsCreatedState='disable'
                IsPlayedState=get_isPlayedCreated_FilterValue(IsPlayedState,IsCreatedState)

                while (QueriesRemaining):

                    if not (data['Id'] == ''):
                        #Built query for child meida items
                        apiQuery=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + data['Id'] + '&IncludeItemTypes=' + IncludeItemTypes +
                        '&StartIndex=' + str(StartIndex) + '&Limit=' + str(QueryLimit) + '&IsPlayed=' + IsPlayedState + '&Fields=' + FieldsState +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems + '&Recursive=' + Recursive + '&SortBy=' + SortBy + '&SortOrder=' + SortOrder + '&EnableImages=' + EnableImages + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        children_data,StartIndex,TotalItems,QueryLimit,QueriesRemaining=api_query_handler(apiQuery,StartIndex,TotalItems,QueryLimit,APIDebugMsg)
                    else:
                        #When no media items are returned; simulate an empty query being returned
                        #this will prevent trying to compare to an empty string '' to the whitelist libraries later on
                        children_data={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit=0
                        QueriesRemaining=False
                        if (GLOBAL_DEBUG):
                            print_byType("\n\nNo " + APIDebugMsg + " media items found",False)
                            

                    #Loop thru the returned child items
                    for child_item in children_data['Items']:
                        #Check if child item has already been processed
                        if not (child_item['Id'] in user_processed_itemsId):
                            #Check if media item has any favs
                            if not ('UserData' in child_item):
                                #if it does not; add fav to metadata
                                child_item['UserData']={'IsFavorite':True}
                            elif not ('IsFavorite' in child_item['UserData']):
                                #if it does not; add fav to metadata
                                child_item['UserData']['IsFavorite']=True
                            #if child_item is not already a fav; update this temp metadata so it is a fav
                            elif not (child_item['UserData']['IsFavorite']):
                                child_item['UserData']['IsFavorite']=True

                            #assign fav to metadata
                            child_list.append(child_item)
                            user_processed_itemsId.add(child_item['Id'])

                            if (GLOBAL_DEBUG):
                                print_byType('\nChild item with Id: ' + str(child_item['Id']) + 'marked as favorite',False)

    #Return dictionary of child items along with TotalRecordCount
    return({'Items':child_list,'TotalRecordCount':len(child_list),'StartIndex':StartIndex})


#Get children of tagged parents
def getChildren_taggedMediaItems(user_key,data_Tagged,user_tags,filter_played_count_comparison,filter_played_count,filter_created_played_count_comparison,filter_created_played_count,tag_Type,played_days,created_days):
    server_url=cfg.server_url
    auth_key=cfg.auth_key
    #parent_tag=[]
    child_list=[]
    child_list_Id=[]
    StartIndex=0
    insert_tagName=user_tags.split(',')[0]
    insert_tagId=uuid.uuid4().int

    #Loop thru items returned as tagged
    for data in data_Tagged['Items']:

        #Verify media item is a parent (not a child like an episode, movie, or audio)
        if ((data['IsFolder'] == True) or (data['Type'] == 'Book')):

            user_processed_itemsId=set()

            #Initialize api_query_handler() variables for child media items
            StartIndex=0
            TotalItems=1
            QueryLimit=1
            QueriesRemaining=True
            APIDebugMsg='find_children_' + tag_Type + 'ged_media_items'

            if not (data['Id'] == ''):
                #Build query for child media items; check is not Movie, Episode, or Audio
                if not ((data['Type'] == 'Movie') and (data['Type'] == 'Episode') and (data['Type'] == 'Audio')):
                    #include all item types; filter applied in first API calls for each media type in get_media_items()
                    IncludeItemTypes=''
                    FieldsState='Id,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,UserData'
                    SortBy='SeriesName,AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                    SortOrder='Ascending'
                    Recursive='True'
                    EnableImages='False'
                    CollapseBoxSetItems='False'
                    if (played_days >= 0):
                        IsPlayedState=get_isPlayed_FilterValue(filter_played_count_comparison,filter_played_count)
                    else:
                        IsPlayedState='disable'
                    if (created_days >= 0):
                        IsCreatedState=get_isCreated_FilterValue(filter_created_played_count_comparison,filter_created_played_count)
                    else:
                        IsCreatedState='disable'
                    IsPlayedState=get_isPlayedCreated_FilterValue(IsPlayedState,IsCreatedState)

                    while (QueriesRemaining):

                        if not (data['Id'] == ''):
                            #Built query for child media items
                            apiQuery=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + data['Id'] + '&IncludeItemTypes=' + IncludeItemTypes +
                            '&StartIndex=' + str(StartIndex) + '&Limit=' + str(QueryLimit) + '&IsPlayed=' + IsPlayedState +
                            '&Fields=' + FieldsState + '&Recursive=' + Recursive + '&SortBy=' + SortBy + '&SortOrder=' + SortOrder +
                            '&CollapseBoxSet' + CollapseBoxSetItems + '&EnableImages=' + EnableImages + '&api_key=' + auth_key)

                            #Send the API query for for watched media items in blacklists
                            children_data,StartIndex,TotalItems,QueryLimit,QueriesRemaining=api_query_handler(apiQuery,StartIndex,TotalItems,QueryLimit,APIDebugMsg)
                        else:
                            #When no media items are returned; simulate an empty query being returned
                            #this will prevent trying to compare to an empty string '' to the whitelist libraries later on
                            children_data={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                            QueryLimit=0
                            QueriesRemaining=False
                            if (GLOBAL_DEBUG):
                                print_byType("\n\nNo " + APIDebugMsg + " media items found",False)

                        #Loop thru the returned child items
                        for child_item in children_data['Items']:
                            #child_itemTag=''
                            child_itemIsTagged=False
                            #Check if child item has already been processed
                            if not (child_item['Id'] in user_processed_itemsId):
                                #Emby and jellyfin store tags differently
                                if (cfg.server_brand == 'emby'):
                                    #Does 'TagItems' exist
                                    if not ('TagItems' in child_item):
                                        #if it does not; add desired tag to metadata
                                        child_item['TagItems']=[{'Name':insert_tagName,'Id':insert_tagId}]
                                    #Does 'TagItems'[] exist
                                    elif not (does_index_exist(child_item['TagItems'],0)):
                                        #if it does not; add desired tag to metadata
                                        child_item['TagItems']=[{'Name':insert_tagName,'Id':insert_tagId}]
                                    else: #Tag already exists
                                        #Determine if the existing tags are any of the tags we are looking for
                                        child_list_Id,child_itemIsTagged=get_isItemTagged(user_tags,child_list_Id,child_item)
                                        #If existing tags are not ones we are lookign for then insert desired tag
                                        if not (child_itemIsTagged):
                                            child_item['TagItems'].append({'Name':insert_tagName,'Id':insert_tagId})
                                #Emby and jellyfin store tags differently
                                else: #(cfg.server_brand == 'jellyfin')
                                    #Does 'TagItems' exist
                                    if not ('Tag' in child_item):
                                        #if it does not; add desired tag to metadata
                                        child_item['Tags']=[insert_tagName]
                                    #Does 'Tags'[] exist
                                    elif (child_item['Tags'] == []):
                                        #if it does not; add desired tag to metadata
                                        child_item['Tags'].append(insert_tagName)
                                    #else:
                                        #Determine if the existing tags are any of the tags we are looking for
                                        child_list_Id,child_itemIsTagged=get_isItemTagged(user_tags,child_list_Id,child_item)
                                        #If existing tags are not ones we are lookign for then insert desired tag
                                        if not (child_itemIsTagged):
                                            child_item['Tags'].append(insert_tagName)
                                #keep track of tagged child items
                                child_list.append(child_item)
                                user_processed_itemsId.add(child_item['Id'])

                                if (GLOBAL_DEBUG):
                                    print_byType('\nChild item with Id: ' + str(child_item['Id']) + ' tagged with tag named: ' + str(insert_tagName),False)

    #Return dictionary of child items along with TotalRecordCount
    return({'Items':child_list,'TotalRecordCount':len(child_list),'StartIndex':StartIndex})


#Determine if item can be monitored
def get_isItemMonitored(mediasource):
    #When script is run before a media item is physically available ignore that media item
    if ('Type' in mediasource) and ('Size' in mediasource):
        if ((mediasource['Type'] == 'Placeholder') and (mediasource['Size'] == 0)):
            #ignore this media item
            itemIsMonitored=False
        else:
            #ok to monitor this media item
            itemIsMonitored=True
    elif ('Type' in mediasource):
        if (mediasource['Type'] == 'Placeholder'):
            #ignore this media item
            itemIsMonitored=False
        else:
            #ok to monitor this media item
            itemIsMonitored=True
    elif ('Size' in mediasource):
        if (mediasource['Size'] == 0):
            #ignore this media item
            itemIsMonitored=False
        else:
            #ok to monitor this media item
            itemIsMonitored=True
    else:
        #ignore this media item
        itemIsMonitored=False

    if (GLOBAL_DEBUG):
        print_byType('\nMedia Item Is Monitored: ' + str(itemIsMonitored),False)

    return(itemIsMonitored)


#Determine if there is a matching item
def get_isItemMatching(item_one, item_two):

    #for Ids in Microsoft Windows, replace backslashes in Ids with forward slash
    item_one = item_one.replace('\\','/')
    item_two = item_two.replace('\\','/')

    #read and split Ids to compare to
    item_one_split=item_one.split(',')
    item_two_split=item_two.split(',')

    items_match=False

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType('\n',False)

    #determine if media Id matches one of the other Ids
    for single_item_one in item_one_split:
            for single_item_two in item_two_split:
                if (GLOBAL_DEBUG):
                    print_byType('\nComparing the below two items',False)
                    print_byType('\n\'' + str(single_item_one) + '\'' + ':' + '\'' + str(single_item_two) + '\'',False)
                if ((not (single_item_one == '')) and (not (single_item_two == '')) and
                    (not (single_item_one == "''")) and (not (single_item_two == "''")) and
                    (not (single_item_one == '""')) and (not (single_item_two == '""'))):
                    if (single_item_one == single_item_two):
                        items_match=True

                        #found a match; return true and the matching value
                        return(items_match, single_item_one)

    #nothing matched; return false and empty string
    return(items_match,'')


#Determine if media item whitelisted for the current user or for another user
def get_isItemWhitelisted(LibraryID,LibraryNetPath,LibraryPath,currentPosition,
                                user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json):

    library_matching_behavior=cfg.library_matching_behavior

    itemIsWhiteListed_Local=False
    itemWhiteListedValue_Local=''

    itemIsWhiteListed_Remote=False
    itemWhiteListedValue_Remote=''

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

    #Store media item's local and remote whitelist state
    #Get if media item is whitelisted
    for wllib_pos in range(len(user_wllib_keys_json)):
        #Looking in this users libraries
        if (wllib_pos == currentPosition):
            if not (itemIsWhiteListed_Local):
                if (library_matching_behavior == 'byId'):
                    itemIsWhiteListed_Local, itemWhiteListedValue_Local=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                elif (library_matching_behavior == 'byPath'):
                    itemIsWhiteListed_Local, itemWhiteListedValue_Local=get_isItemMatching(LibraryPath, user_wllib_path_json[wllib_pos])
                elif (library_matching_behavior == 'byNetworkPath'):
                    itemIsWhiteListed_Local, itemWhiteListedValue_Local=get_isItemMatching(LibraryNetPath, user_wllib_netpath_json[wllib_pos])

                if (GLOBAL_DEBUG):
                    print_byType('\nItem is whitelisted for this user: ' + str(itemIsWhiteListed_Local),False)
                    print_byType('\nMatching whitelisted value for this user is: ' + itemWhiteListedValue_Local,False)

        #Looking in other users libraries
        else: #(wllib_pos == currentPosition)
            if not (itemIsWhiteListed_Remote):
                if (library_matching_behavior == 'byId'):
                    itemIsWhiteListed_Remote, itemWhiteListedValue_Remote=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                elif (library_matching_behavior == 'byPath'):
                    itemIsWhiteListed_Remote, itemWhiteListedValue_Remote=get_isItemMatching(LibraryPath, user_wllib_path_json[wllib_pos])
                elif (library_matching_behavior == 'byNetworkPath'):
                    itemIsWhiteListed_Remote, itemWhiteListedValue_Remote=get_isItemMatching(LibraryNetPath, user_wllib_netpath_json[wllib_pos])

                if (GLOBAL_DEBUG):
                    print_byType('\nItem is whitelisted for another user: ' + str(itemIsWhiteListed_Remote),False)
                    print_byType('\nMatching whitelisted value for another user is: ' + itemWhiteListedValue_Remote,False)

        if (GLOBAL_DEBUG):
            print_byType('\nLibraryId is: ' + LibraryID,False)
            print_byType('\nLibraryPath is: ' + LibraryPath,False)
            print_byType('\nLibraryNetPath is: ' + LibraryNetPath,False)
            print_byType('\nWhitelisted Keys are: ' + user_wllib_keys_json[wllib_pos],False)
            print_byType('\nWhitelisted Paths are: ' + user_wllib_path_json[wllib_pos],False)
            print_byType('\nWhitelisted NetworkPaths are: ' + user_wllib_netpath_json[wllib_pos],False)

    return itemIsWhiteListed_Local,itemIsWhiteListed_Remote


#Determine if this media item is tagged
def get_isItemTagged(usertags,tagged_items,item):
    itemIsTagged=False

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

    #Emby and jellyfin store tags differently
    if (cfg.server_brand == 'emby'):
        #Check if media item is tagged
        if ((not (usertags == '')) and ('TagItems' in item)):
            #Check if media item is tagged
            taglist=set()
            #Loop thru tags; store them for comparison to the media item
            for tagpos in range(len(item['TagItems'])):
                taglist.add(item['TagItems'][tagpos]['Name'])
            #Check if any of the media items tags match the tags in the config file
            itemIsTagged, itemTaggedValue=get_isItemMatching(usertags, ','.join(map(str, taglist)))
            #Save media item's tags state
            if (itemIsTagged):
                tagged_items.append(item['Id'])
                if (GLOBAL_DEBUG):
                    print_byType('\nitem with Id ' + str(item['Id']) + 'has tag named ' + str(itemTaggedValue),False)
    #Emby and jellyfin store tags differently
    else: #(cfg.server_brand == 'jellyfin')
        #Jellyfin tags
        #Check if media item is tagged
        if ((not (usertags == '')) and ('Tags' in item)):
            #Check if media item is tagged
            taglist=set()
            #Loop thru tags; store them for comparison to the media item
            for tagpos in range(len(item['Tags'])):
                taglist.add(item['Tags'][tagpos])
            #Check if any of the media items tags match the tags in the config file
            itemIsTagged, itemTaggedValue=get_isItemMatching(usertags, ','.join(map(str, taglist)))
            #Save media item's usertags state
            if (itemIsTagged):
                tagged_items.append(item['Id'])
                if (GLOBAL_DEBUG):
                    print_byType('\nitem with Id ' + str(item['Id']) + 'has tag named ' + str(itemTaggedValue),False)

    if (GLOBAL_DEBUG):
        print_byType("\nIs Media Item: " + str(item['Id']) + " Tagged: " + str(itemIsTagged),False)

    #parenthesis intentionally omitted to return tagged_items as a set
    return itemIsTagged,tagged_items


#get additional item info needed to make a decision about a media item
def get_ADDITIONAL_itemInfo(user_key,itemId,lookupTopic):
    server_url=cfg.server_url
    auth_key=cfg.auth_key

    #Get additonal item information
    url=(server_url + '/Users/' + user_key  + '/Items/' + str(itemId) +
        '?enableImages=False&enableUserData=True&Fields=ParentId,Genres,Tags&api_key=' + auth_key)

    itemInfo=requestURL(url, cfg.DEBUG, lookupTopic, cfg.api_query_attempts)

    return(itemInfo)


#get additional channel/network/studio info needed to determine if item is favorite
def get_STUDIO_itemInfo(user_key,studioNetworkName):
    server_url=cfg.server_url
    auth_key=cfg.auth_key
    #Encode studio name
    studio_network=urllib.parse.quote(studioNetworkName)

    #Get studio item information
    url=server_url + '/Studios/' + studio_network + '&enableImages=False&enableUserData=True&api_key=' + auth_key

    itemInfo=requestURL(url, cfg.DEBUG, 'studio_network_info', cfg.api_query_attempts)

    return(itemInfo)


#determine if movie or library are tagged
def get_isMOVIE_Tagged(item,user_key,usertags):

    tagged_items=[]

    #define empty dictionary for tagged Movies
    istag_MOVIE={'movie':{},'movielibrary':{}}

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

### Movie #######################################################################################

    if ('Id' in item):

        istag_MOVIE['movie'][item['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,item)

### End Movie ###################################################################################

### Movie Library #######################################################################################

    if ('ParentId' in item):
        movielibrary_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'movie_library_info')

        istag_MOVIE['movielibrary'][movielibrary_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,movielibrary_item_info)

### End Movie Library ###################################################################################

    for istagkey in istag_MOVIE:
        for istagID in istag_MOVIE[istagkey]:
            if (istag_MOVIE[istagkey][istagID]):
                if (GLOBAL_DEBUG):
                    print_byType("\nMovie " + str(item['Id']) + " is tagged.",False)
                return(True)

    if (GLOBAL_DEBUG):
        print_byType("\nMovie " + str(item['Id']) + " is NOT tagged.",False)

    return(False)


#determine if episode, season, series, or studio-network are tagged
def get_isEPISODE_Tagged(item,user_key,usertags):

    tagged_items=[]

    #define empty dictionary for tagorited TV Series, Seasons, Episodes, and Channels/Networks
    istag_EPISODE={'episode':{},'season':{},'series':{},'tvlibrary':{},'seriesstudionetwork':{}}

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

### Episode #######################################################################################

    if ('Id' in item):

        istag_EPISODE['episode'][item['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,item)

### End Episode ###################################################################################

### Season ########################################################################################

    if ('SeasonId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeasonId'],'season_info')

        istag_EPISODE['season'][season_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,season_item_info)

    elif ('ParentId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'season_info')

        istag_EPISODE['season'][season_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,season_item_info)

### End Season ####################################################################################

### Series ########################################################################################

    if ('SeriesId' in item):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeriesId'],'series_info')

        istag_EPISODE['series'][series_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,series_item_info)

    elif ('SeriesId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeriesId'],'series_info')

        istag_EPISODE['series'][series_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,series_item_info)

    elif ('ParentId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['ParentId'],'series_info')

        istag_EPISODE['series'][series_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,series_item_info)

### End Series ####################################################################################

### TV Library ########################################################################################

    if ('ParentId' in series_item_info):
        tvlibrary_item_info = get_ADDITIONAL_itemInfo(user_key,series_item_info['ParentId'],'tv_library_info')

        istag_EPISODE['tvlibrary'][tvlibrary_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,tvlibrary_item_info)

### End TV Library ####################################################################################

### Studio Network #######################################################################################

    if (('Studios' in series_item_info) and does_index_exist(series_item_info['Studios'],0)):
        #Get studio network's item info
        tvstudionetwork_item_info = get_ADDITIONAL_itemInfo(user_key,series_item_info['Studios'][0]['Id'],'studio_network_info')

        istag_EPISODE['seriesstudionetwork'][tvstudionetwork_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,tvstudionetwork_item_info)

    elif ('SeriesStudio' in series_item_info):
        #Get series studio network's item info
        tvstudionetwork_item_info = get_STUDIO_itemInfo(user_key,series_item_info['SeriesStudio'])

        istag_EPISODE['seriesstudionetwork'][tvstudionetwork_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,tvstudionetwork_item_info)

### End Studio Network ###################################################################################

    for istagkey in istag_EPISODE:
        for istagID in istag_EPISODE[istagkey]:
            if (istag_EPISODE[istagkey][istagID]):
                if (GLOBAL_DEBUG):
                    print_byType("\nEpisode " + str(item['Id']) + " is tagged.",False)
                return(True)

    if (GLOBAL_DEBUG):
        print_byType("\nEpisode " + str(item['Id']) + " is NOT tagged.",False)

    return(False)

#determine if genres for music track, album, or music library are tagged
def get_isAUDIO_Tagged(item,user_key,usertags):

    tagged_items=[]

    #define empty dictionary for tagorited Tracks, Albums, Artists
    istag_AUDIO={'track':{},'album':{},'audiolibrary':{}}

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

### Track #########################################################################################

    tagged_items=[]

    if ('Id' in item):

        istag_AUDIO['track'][item['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,item)

        #istag_AUDIO['trackartist']=get_istag_ARTIST(user_key,item,istag_AUDIO['trackartist'],keep_tagorites_advanced_track_artist,lookupTopicTrack + '_artist')

### End Track #####################################################################################

### Album/Book #########################################################################################

    #Albums for music
    if ('ParentId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'album_info')

        istag_AUDIO['album'][album_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,album_item_info)

        #istag_AUDIO['albumartist']=get_istag_ARTIST(user_key,album_item_info,istag_AUDIO['albumartist'],keep_tagorites_advanced_album_artist,lookupTopicAlbum + '_artist')
    elif ('AlbumId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['AlbumId'],'album_info')

        istag_AUDIO['album'][album_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,album_item_info)

        #istag_AUDIO['albumartist']=get_istag_ARTIST(user_key,album_item_info,istag_AUDIO['albumartist'],keep_tagorites_advanced_album_artist,lookupTopicAlbum + '_artist')

### End Album/Book #####################################################################################

### Library ########################################################################################

    #Library
    if ('ParentId' in album_item_info):
        audiolibrary_item_info = get_ADDITIONAL_itemInfo(user_key,album_item_info['ParentId'],'library_info')

        istag_AUDIO['audiolibrary'][audiolibrary_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,audiolibrary_item_info)

### End Library #####################################################################################

    for istagkey in istag_AUDIO:
        for istagID in istag_AUDIO[istagkey]:
            if (istag_AUDIO[istagkey][istagID]):
                if (GLOBAL_DEBUG):
                    print_byType("\nAudio/AudioBook " + str(item['Id']) + " is tagged.",False)
                return(True)

    if (GLOBAL_DEBUG):
        print_byType("\nAudio/AudioBook " + str(item['Id']) + " is NOT tagged.",False)

    return(False)


#determine if genres for audiobook track, book, or audio book library are tagged
def get_isAUDIOBOOK_Tagged(item,user_key,usertags):
    return get_isAUDIO_Tagged(item,user_key,usertags,)


#Determine if genre is favorited
def get_isGENRE_Fav(user_key,item,isfav_ITEMgenre,keep_favorites_advanced,lookupTopic):

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

    if (('GenreItems' in item) and (does_index_exist(item['GenreItems'],0))):
        #Check if bitmask for favorites by item genre is enabled
        if (keep_favorites_advanced):
            #Check if bitmask for any or first item genre is enabled
            if (keep_favorites_advanced == 1):
                    genre_item_info = get_ADDITIONAL_itemInfo(user_key,item['GenreItems'][0]['Id'],lookupTopic)
                    #Check if genre's favorite value already exists in dictionary
                    if not genre_item_info['Id'] in isfav_ITEMgenre:
                        #Store if first genre is marked as favorite
                        isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (genre_item_info['UserData']['IsFavorite']):
                            #Store if the genre is marked as a favorite
                            isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']
            else:
                for genre_item in range(len(item['GenreItems'])):
                    genre_item_info = get_ADDITIONAL_itemInfo(user_key,item['GenreItems'][genre_item]['Id'],lookupTopic + '_any')
                    #Check if genre's favorite value already exists in dictionary
                    if not genre_item_info['Id'] in isfav_ITEMgenre:
                        #Store if any genre is marked as a favorite
                        isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (genre_item_info['UserData']['IsFavorite']):
                            #Store if the genre is marked as a favorite
                            isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']

    if (GLOBAL_DEBUG):
        print_byType("\nFavorite Info For Item: " + str(item['Id']) + "\n" + convert2json(isfav_ITEMgenre),False)

    return(isfav_ITEMgenre)


#Determine if artist is favorited
def get_isARTIST_Fav(user_key,item,isfav_ITEMartist,keep_favorites_advanced,lookupTopic):

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

    if (('ArtistItems' in item) and (does_index_exist(item['ArtistItems'],0))):
        #Check if bitmask for favorites by artist is enabled
        if (keep_favorites_advanced):
            #Check if bitmask for any or first artist is enabled
            if (keep_favorites_advanced == 1):
                artist_item_info = get_ADDITIONAL_itemInfo(user_key,item['ArtistItems'][0]['Id'],lookupTopic + '_info')
                #Check if artist's favorite value already exists in dictionary
                if not artist_item_info['Id'] in isfav_ITEMartist:
                    #Store if first artist is marked as favorite
                    isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']
                else: #it already exists
                    #if the value is True save it anyway
                    if (artist_item_info['UserData']['IsFavorite']):
                        #Store if the artist is marked as a favorite
                        isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']
            else:
                for artist in range(len(item['ArtistItems'])):
                    artist_item_info = get_ADDITIONAL_itemInfo(user_key,item['ArtistItems'][artist]['Id'],lookupTopic + '_info_any')
                    #Check if artist's favorite value already exists in dictionary
                    if not artist_item_info['Id'] in isfav_ITEMartist:
                        #Store if any track artist is marked as a favorite
                        isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (artist_item_info['UserData']['IsFavorite']):
                            #Store if the artist is marked as a favorite
                            isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']

    if (GLOBAL_DEBUG):
        print_byType("\nFavorite Info For Item: " + str(item['Id']) + "\n" + convert2json(isfav_ITEMartist),False)

    return(isfav_ITEMartist)


#Determine if artist is favorited
def get_isSTUDIONETWORK_Fav(user_key,item,isfav_ITEMstdo_ntwk,keep_favorites_advanced,lookupTopic):

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

    if (('Studios' in  item) and (does_index_exist(item['Studios'],0))):
        #Check if bitmask for favorites by item genre is enabled
        if (keep_favorites_advanced):
            #Check if bitmask for any or first item genre is enabled
            if (keep_favorites_advanced == 1):
                #Get studio network's item info
                studionetwork_item_info = get_ADDITIONAL_itemInfo(user_key,item['Studios'][0]['Id'],'studio_network_info')
                #Check if studio-network's favorite value already exists in dictionary
                if not studionetwork_item_info['Id'] in isfav_ITEMstdo_ntwk:
                    if (('UserData' in studionetwork_item_info) and ('IsFavorite' in studionetwork_item_info['UserData'])):
                        #Store if the studio network is marked as a favorite
                        isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']
                else: #it already exists
                    #if the value is True save it anyway
                    if (studionetwork_item_info['UserData']['IsFavorite']):
                        #Store if the studio network is marked as a favorite
                        isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']

            else:
                for studios in range(len(item['Studios'])):
                    #Get studio network's item info
                    studionetwork_item_info = get_ADDITIONAL_itemInfo(user_key,item['Studios'][studios]['Id'],'studio_network_info')
                    #Check if studio network's favorite value already exists in dictionary
                    if not studionetwork_item_info['Id'] in isfav_ITEMstdo_ntwk:
                        if (('UserData' in studionetwork_item_info) and ('IsFavorite' in studionetwork_item_info['UserData'])):
                            #Store if the studio network is marked as a favorite
                            isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (studionetwork_item_info['UserData']['IsFavorite']):
                            #Store if the studio network is marked as a favorite
                            isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']

    elif ('SeriesStudio' in item):
        #Check if bitmask for favorites by item genre is enabled
        if (keep_favorites_advanced):
            #Get series studio network's item info
            studionetwork_item_info = get_STUDIO_itemInfo(user_key,item['SeriesStudio'])
            #Check if series studio network's favorite value already exists in dictionary
            if not studionetwork_item_info['Id'] in isfav_ITEMstdo_ntwk:
                if (('UserData' in studionetwork_item_info) and ('IsFavorite' in studionetwork_item_info['UserData'])):
                    #Store if the series studio network is marked as a favorite
                    isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']
            else: #it already exists
                #if the value is True save it anyway
                if (studionetwork_item_info['UserData']['IsFavorite']):
                    #Store if the series studio network is marked as a favorite
                    isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']

    if (GLOBAL_DEBUG):
        print_byType("\nFavorite Info For Item: " + str(item['Id']) + "\n" + convert2json(isfav_ITEMstdo_ntwk),False)

    return(isfav_ITEMstdo_ntwk)


#determine if genres for movie or library are set to favorite
def get_isMOVIE_AdvancedFav(item,user_key):

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

    keep_favorites_advanced_movie_genre=cfg.keep_favorites_advanced_movie_genre
    keep_favorites_advanced_movie_library_genre=cfg.keep_favorites_advanced_movie_library_genre
    #define empty dictionary for favorited Movies
    isfav_MOVIE={'movie':{},'movielibrary':{},'moviegenre':{},'movielibrarygenre':{}}

### Movie #######################################################################################

    if ('Id' in item):

        isfav_MOVIE['moviegenre']=get_isGENRE_Fav(user_key,item,isfav_MOVIE['moviegenre'],keep_favorites_advanced_movie_genre,'movie_genre')

### End Movie ###################################################################################

### Movie Library #######################################################################################

    if ('ParentId' in item):
        movielibrary_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'movie_library_info')

        isfav_MOVIE['movielibrarygenre']=get_isGENRE_Fav(user_key,movielibrary_item_info,isfav_MOVIE['movielibrarygenre'],keep_favorites_advanced_movie_library_genre,'movie_library_genre')

### End Movie Library ###################################################################################

    for isfavkey in isfav_MOVIE:
        for isfavID in isfav_MOVIE[isfavkey]:
            if (isfav_MOVIE[isfavkey][isfavID]):
                if (GLOBAL_DEBUG):
                    print_byType("\nMovie Item " + str(item['Id']) + " is favorited.",False)
                return(True)

    if (GLOBAL_DEBUG):
        print_byType("\nMovie " + str(item['Id']) + " is NOT favorited.",False)

    return(False)


#determine if genres for episode, season, series, or studio-network are set to favorite
def get_isEPISODE_AdvancedFav(item,user_key):

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

    keep_favorites_advanced_episode_genre=cfg.keep_favorites_advanced_episode_genre
    keep_favorites_advanced_season_genre=cfg.keep_favorites_advanced_season_genre
    keep_favorites_advanced_series_genre=cfg.keep_favorites_advanced_series_genre
    keep_favorites_advanced_tv_library_genre=cfg.keep_favorites_advanced_tv_library_genre
    keep_favorites_advanced_tv_studio_network=cfg.keep_favorites_advanced_tv_studio_network
    keep_favorites_advanced_tv_studio_network_genre=cfg.keep_favorites_advanced_tv_studio_network_genre
    #define empty dictionary for favorited TV Series, Seasons, Episodes, and Channels/Networks
    isfav_EPISODE={'episode':{},'season':{},'series':{},'tvlibrary':{},'episodegenre':{},'seasongenre':{},'seriesgenre':{},'tvlibrarygenre':{},'seriesstudionetwork':{},'seriesstudionetworkgenre':{}}

### Episode #######################################################################################

    if ('Id' in item):

        isfav_EPISODE['episodegenre']=get_isGENRE_Fav(user_key,item,isfav_EPISODE['episodegenre'],keep_favorites_advanced_episode_genre,'episode_genre')

### End Episode ###################################################################################

### Season ########################################################################################

    if ('SeasonId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeasonId'],'season_info')

        isfav_EPISODE['seasongenre']=get_isGENRE_Fav(user_key,season_item_info,isfav_EPISODE['seasongenre'],keep_favorites_advanced_season_genre,'season_genre')

    elif ('ParentId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'season_info')

        isfav_EPISODE['seasongenre']=get_isGENRE_Fav(user_key,season_item_info,isfav_EPISODE['seasongenre'],keep_favorites_advanced_season_genre,'season_genre')

### End Season ####################################################################################

### Series ########################################################################################

    if ('SeriesId' in item):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeriesId'],'series_info')

        isfav_EPISODE['seriesgenre']=get_isGENRE_Fav(user_key,series_item_info,isfav_EPISODE['seriesgenre'],keep_favorites_advanced_series_genre,'series_genre')

        isfav_EPISODE['seriesstudionetwork']=get_isSTUDIONETWORK_Fav(user_key,series_item_info,isfav_EPISODE['seriesstudionetwork'],keep_favorites_advanced_tv_studio_network,'studio_network')

    elif ('SeriesId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeriesId'],'series_info')

        isfav_EPISODE['seriesgenre']=get_isGENRE_Fav(user_key,series_item_info,isfav_EPISODE['seriesgenre'],keep_favorites_advanced_series_genre,'series_genre')

        isfav_EPISODE['seriesstudionetwork']=get_isSTUDIONETWORK_Fav(user_key,series_item_info,isfav_EPISODE['seriesstudionetwork'],keep_favorites_advanced_tv_studio_network,'studio_network')

    elif ('ParentId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['ParentId'],'series_info')

        isfav_EPISODE['seriesgenre']=get_isGENRE_Fav(user_key,series_item_info,isfav_EPISODE['seriesgenre'],keep_favorites_advanced_series_genre,'series_genre')

        isfav_EPISODE['seriesstudionetwork']=get_isSTUDIONETWORK_Fav(user_key,series_item_info,isfav_EPISODE['seriesstudionetwork'],keep_favorites_advanced_tv_studio_network,'studio_network')

### End Series ####################################################################################

### TV Library ########################################################################################

    if ('ParentId' in series_item_info):
        tvlibrary_item_info = get_ADDITIONAL_itemInfo(user_key,series_item_info['ParentId'],'tv_library_info')

        isfav_EPISODE['tvlibrarygenre']=get_isGENRE_Fav(user_key,tvlibrary_item_info,isfav_EPISODE['tvlibrarygenre'],keep_favorites_advanced_tv_library_genre,'tv_library_genre')

### End TV Library ####################################################################################

### Studio Network #######################################################################################

    if (('Studios' in series_item_info) and (does_index_exist(series_item_info['Studios'],0))):
        #Get studio network's item info
        tvstudionetwork_item_info = get_ADDITIONAL_itemInfo(user_key,series_item_info['Studios'][0]['Id'],'studio_network_info')

        isfav_EPISODE['seriesstudionetworkgenre']=get_isGENRE_Fav(user_key,tvstudionetwork_item_info,isfav_EPISODE['seriesstudionetworkgenre'],keep_favorites_advanced_tv_studio_network_genre,'studio_network_genre')

    elif ('SeriesStudio' in series_item_info):
        #Get series studio network's item info
        tvstudionetwork_item_info = get_STUDIO_itemInfo(user_key,series_item_info['SeriesStudio'])

        isfav_EPISODE['seriesstudionetworkgenre']=get_isGENRE_Fav(user_key,tvstudionetwork_item_info,isfav_EPISODE['seriesstudionetworkgenre'],keep_favorites_advanced_tv_studio_network_genre,'studio_network_genre')

### End Studio Network ###################################################################################

    for isfavkey in isfav_EPISODE:
        for isfavID in isfav_EPISODE[isfavkey]:
            if (isfav_EPISODE[isfavkey][isfavID]):
                if (GLOBAL_DEBUG):
                    print_byType("\nEpisode " + str(item['Id']) + " is favorited.",False)
                return(True)

    if (GLOBAL_DEBUG):
        print_byType("\nEpisode " + str(item['Id']) + " is NOT favorited.",False)

    return(False)


#determine if genres for music track, album, or artist are set to favorite
def get_isAUDIO_AdvancedFav(item,user_key,itemType):

    #DEBUG log formatting
    if (GLOBAL_DEBUG):
        print_byType("\n",False)

    if (itemType == 'Audio'):
        lookupTopicTrack='track'
        lookupTopicAlbum='album'
        lookupTopicLibrary='music_library'

        keep_favorites_advanced_track_genre=cfg.keep_favorites_advanced_track_genre
        keep_favorites_advanced_album_genre=cfg.keep_favorites_advanced_album_genre
        keep_favorites_advanced_music_library_genre=cfg.keep_favorites_advanced_music_library_genre

        keep_favorites_advanced_track_artist=cfg.keep_favorites_advanced_track_artist
        keep_favorites_advanced_album_artist=cfg.keep_favorites_advanced_album_artist
    elif (itemType == 'AudioBook'):
        lookupTopicTrack='audiobook'
        lookupTopicAlbum='book'
        lookupTopicLibrary='audio_book_library'

        keep_favorites_advanced_track_genre=cfg.keep_favorites_advanced_audio_book_track_genre
        keep_favorites_advanced_album_genre=cfg.keep_favorites_advanced_audio_book_genre
        keep_favorites_advanced_music_library_genre=cfg.keep_favorites_advanced_audio_book_library_genre

        keep_favorites_advanced_track_artist=cfg.keep_favorites_advanced_audio_book_track_author
        keep_favorites_advanced_album_artist=cfg.keep_favorites_advanced_audio_book_author
    else:
        raise ValueError('ValueError: Unknown itemType passed into get_isAUDIO_AdvancedFav')

    #define empty dictionary for favorited Tracks, Albums, Artists
    isfav_AUDIO={'track':{},'album':{},'artist':{},'composer':{},'audiolibrary':{},'trackgenre':{},'albumgenre':{},'trackartist':{},'albumartist':{},'audiolibraryartist':{},'composergenre':{},'audiolibrarygenre':{}}

### Track #########################################################################################

    if ('Id' in item):

        isfav_AUDIO['trackgenre']=get_isGENRE_Fav(user_key,item,isfav_AUDIO['trackgenre'],keep_favorites_advanced_track_genre,lookupTopicTrack + '_genre')

        isfav_AUDIO['trackartist']=get_isARTIST_Fav(user_key,item,isfav_AUDIO['trackartist'],keep_favorites_advanced_track_artist,lookupTopicTrack + '_artist')

### End Track #####################################################################################

### Album/Book #########################################################################################

    #Albums for music
    if ('ParentId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'album_info')

        isfav_AUDIO['albumgenre']=get_isGENRE_Fav(user_key,album_item_info,isfav_AUDIO['albumgenre'],keep_favorites_advanced_album_genre,lookupTopicAlbum + '_genre')

        isfav_AUDIO['albumartist']=get_isARTIST_Fav(user_key,album_item_info,isfav_AUDIO['albumartist'],keep_favorites_advanced_album_artist,lookupTopicAlbum + '_artist')
    elif ('AlbumId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['AlbumId'],'album_info')

        isfav_AUDIO['albumgenre']=get_isGENRE_Fav(user_key,album_item_info,isfav_AUDIO['albumgenre'],keep_favorites_advanced_album_genre,lookupTopicAlbum + '_genre')

        isfav_AUDIO['albumartist']=get_isARTIST_Fav(user_key,album_item_info,isfav_AUDIO['albumartist'],keep_favorites_advanced_album_artist,lookupTopicAlbum + '_artist')

### End Album/Book #####################################################################################

### Library ########################################################################################

    #Library
    if ('ParentId' in album_item_info):
        audiolibrary_item_info = get_ADDITIONAL_itemInfo(user_key,album_item_info['ParentId'],'library_info')

        isfav_AUDIO['audiolibrarygenre']=get_isGENRE_Fav(user_key,audiolibrary_item_info,isfav_AUDIO['audiolibrarygenre'],keep_favorites_advanced_music_library_genre,lookupTopicLibrary + '_genre')

### End Library #####################################################################################

    for isfavkey in isfav_AUDIO:
        for isfavID in isfav_AUDIO[isfavkey]:
            if (isfav_AUDIO[isfavkey][isfavID]):
                if (GLOBAL_DEBUG):
                    if (itemType == 'Audio'):
                        print_byType("\nEpisode " + str(item['Id']) + " is favorited.",False)
                    elif (itemType == 'AudioBook'):
                        print_byType("\nEpisode " + str(item['Id']) + " is favorited.",False)
                    else:
                        print_byType("\nUnknown Audio Type " + str(item['Id']) + " is favorited.",False)
                return(True)

    if (GLOBAL_DEBUG):
        if (itemType == 'Audio'):
            print_byType("\nEpisode " + str(item['Id']) + " is NOT favorited.",False)
        elif (itemType == 'AudioBook'):
            print_byType("\nEpisode " + str(item['Id']) + " is NOT favorited.",False)
        else:
            print_byType("\nUnknown Audio Type " + str(item['Id']) + " is NOT favorited.",False)

    return(False)


#determine if genres for audiobok track, book, or author are set to favorite
def get_isAUDIOBOOK_AdvancedFav(item,user_key,itemType):
    return get_isAUDIO_AdvancedFav(item,user_key,itemType)


#get series item info from episode
def get_SERIES_itemInfo(episode,user_key):

    series_item_info={}

### Series ########################################################################################

    if ('SeriesId' in episode):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,episode['SeriesId'],'series_info')

    elif ('SeasonId' in episode):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,episode['SeasonId'],'season_info')

        if ('SeriesId' in season_item_info):
            series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['SeriesId'],'series_info')

        elif ('ParentId' in season_item_info):
            series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['ParentId'],'series_info')

    elif ('ParentId' in episode):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,episode['ParentId'],'season_info')

        if ('SeriesId' in season_item_info):
            series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['SeriesId'],'series_info')

        elif ('ParentId' in season_item_info):
            series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['ParentId'],'series_info')

### End Series ####################################################################################

    return series_item_info


#Handle favorites across multiple users
def get_isfav_ByMultiUser(userkey, isfav_byUserId, deleteItems):
    deleteIndexes=[]

    #compare favorited items across users
    #remove from deleteItems list if configured to keep media item when any user has it set as a favorite
    for userId in userkey:
        for usersItemId in isfav_byUserId[userId]:
            #remove all occurance of this items Id from deleteItems if favorited
            if (isfav_byUserId[userId][usersItemId]):
                for delItems in range(len(deleteItems)):
                    if (usersItemId == deleteItems[delItems]['Id']):
                        deleteIndexes.append(delItems)

    #converting to a set and then back to a list removes duplicates
    deleteIndexes=list(set(deleteIndexes))

    #sort indexes needed to remove items from deletion that we want to keep
    deleteIndexes.sort()

    #reverse the order to not worry about shifting indexes when removing items from deleteItems list
    deleteIndexes.reverse()

    #remove favorited items we want to keep
    for favItem in deleteIndexes:
        try:
           deleteItems.pop(favItem)
        except IndexError as err:
           print_byType("\n" + str(err),False)
           print_byType("\n" + convert2json(favItem),False)
           print_byType("\n" + convert2json(deleteIndexes),False)
           print_byType("\n" + convert2json(deleteItems),False)
           exit(0)

    deleteIndexes=[]

    #find duplicates
    for item0 in range(len(deleteItems)):
        for item1 in range(len(deleteItems)):
            if (item0 < item1):
               if (deleteItems[item0]['Id'] == deleteItems[item1]['Id']):
                   deleteIndexes.append(item1)

    #converting to a set and then back to a list removes duplicates
    deleteIndexes=list(set(deleteIndexes))

    #sort indexes needed to remove items from deletion that we want to keep
    deleteIndexes.sort()

    #reverse the order so not worry about shifting indexes when removing items from deleteItems list
    deleteIndexes.reverse()

    #remove duplicates
    for favItem in deleteIndexes:
        try:
            deleteItems.pop(favItem)
        except IndexError as err:
            print(str(err))
            print(favItem)
            print(deleteIndexes)
            print2json(deleteItems)
            exit(0)

    return(deleteItems)


# Determine episodes to be removed from deletion list to keep the mininum/minimum played episode numbers
def get_minEpisodesToKeep(episodeCounts_byUserId,deleteItems):

    user_keys = json.loads(cfg.user_keys)
    minimum_number_episodes = cfg.minimum_number_episodes
    minimum_number_played_episodes = cfg.minimum_number_played_episodes
    minimum_number_episodes_behavior = cfg.minimum_number_episodes_behavior
    minimum_number_episodes_behavior_modified = minimum_number_episodes_behavior.casefold().replace(' ','')

    episodes_toBeDeletedOrRemain={}
    episodeTracker={}
    min_num_episode_behavior = 0
    deleteIndexes=[]
    username_userid_match = False

    #Define different behavior types
    behaviorTypes={
                'username':1,
                'userid':2,
                'maxplayed':3,
                'maxplayedmaxplayed':3,
                'minplayed':4,
                'minplayedminplayed':4,
                'maxunplayed':5,
                'maxunplayedmaxunplayed':5,
                'minunplayed':6,
                'minunplayedminunplayed':6,
                'maxplayedmaxunplayed':7,
                'minplayedminunplayed':8,
                'maxplayedminunplayed':9,
                'minplayedmaxunplayed':10,
                'minunplayedminplayed':11,
                'minunplayedmaxunplayed':12,
                'minunplayedmaxplayed':13,
                'minplayedmaxplayed':14,
                'maxunplayedminunplayed':15,
                'maxunplayedminplayed':16,
                'maxunplayedmaxplayed':17,
                'maxplayedminplayed':18,
                'defaultbehavior':8
                }
    #Put behavior type keys into a list
    behaviorTypesKeys_List=list(behaviorTypes.keys())

    #when minimum_number_episodes it must be > minimum_number_played_episodes
    if (minimum_number_played_episodes > minimum_number_episodes):
        if not (minimum_number_episodes == 0):
            minimum_number_episodes = minimum_number_played_episodes

    #Build a dictionary to track episode information for each seriesId by userId
    #loop thru userIds
    for userId in episodeCounts_byUserId:
        #loop thru list of items to be deleted
        for episodeItem in deleteItems:
            #verify media item is an episode
            if (episodeItem['Type'] == 'Episode'):
                #check if the seriesId associated to the episode is was tracked for this user
                if (episodeItem['SeriesId'] in episodeCounts_byUserId[userId]):
                    #if seriesId has not already processed; add it so it can be
                    if not (episodeItem['SeriesId'] in episodes_toBeDeletedOrRemain):
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']]={}
                    #if userId has not already been processed; add it so it can be
                    if not (userId in episodes_toBeDeletedOrRemain[episodeItem['SeriesId']]):
                        #gather information needed to determine how many played and unplayed episodes may be deleted
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]=defaultdict(dict)
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['PlayedToBeDeleted'] = 0
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedToBeDeleted'] = 0
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['TotalEpisodeCount'] = episodeCounts_byUserId[userId][episodeItem['SeriesId']]['TotalEpisodeCount']
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['PlayedEpisodeCount'] = episodeCounts_byUserId[userId][episodeItem['SeriesId']]['PlayedEpisodeCount']
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedEpisodeCount'] = episodeCounts_byUserId[userId][episodeItem['SeriesId']]['UnplayedEpisodeCount']
                    #increment for played or unplayed episode counts that may be deleted
                    if (get_ADDITIONAL_itemInfo(userId,episodeItem['Id'],'finding minEpisodesToKeep() play state')['UserData']['Played']):
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['PlayedToBeDeleted'] += 1
                    else:
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedToBeDeleted'] += 1
                else:
                    #manually build any missing season and episode information for user's who did meet the filter criteria
                    series_info = get_SERIES_itemInfo(episodeItem,userId)
                    #if seriesId has not already processed; add it so it can be
                    if not (series_info['Id'] in episodes_toBeDeletedOrRemain):
                        episodes_toBeDeletedOrRemain[series_info['Id']]={}
                    #if userId has not already been processed; add it so it can be
                    if not (userId in episodes_toBeDeletedOrRemain[episodeItem['SeriesId']]):
                        #gather information needed to determine how many played and unplayed episodes may be deleted
                        episodes_toBeDeletedOrRemain[series_info['Id']][userId]=defaultdict(dict)
                        episodes_toBeDeletedOrRemain[series_info['Id']][userId]['PlayedToBeDeleted'] = 0
                        episodes_toBeDeletedOrRemain[series_info['Id']][userId]['UnplayedToBeDeleted'] = 0
                        RecursiveItemCount=int(series_info['RecursiveItemCount'])
                        UnplayedItemCount=int(series_info['UserData']['UnplayedItemCount'])
                        PlayedEpisodeCount=RecursiveItemCount - UnplayedItemCount
                        episodes_toBeDeletedOrRemain[series_info['Id']][userId]['TotalEpisodeCount'] = RecursiveItemCount
                        episodes_toBeDeletedOrRemain[series_info['Id']][userId]['PlayedEpisodeCount'] = PlayedEpisodeCount
                        episodes_toBeDeletedOrRemain[series_info['Id']][userId]['UnplayedEpisodeCount'] = UnplayedItemCount
                    #increment for played or unplayed episode counts that may be deleted
                    if (get_ADDITIONAL_itemInfo(userId,episodeItem['Id'],'finding minEpisodesToKeep() play state')['UserData']['Played']):
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['PlayedToBeDeleted'] += 1
                    else:
                        episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedToBeDeleted'] += 1

    #loop thru seriesIds we stored in the loop above
    for seriesId in episodes_toBeDeletedOrRemain:
        #loop thru the userIds under each seriesId
        for userId in episodes_toBeDeletedOrRemain[seriesId]:
            #determine the number of played and unplayed episodes for this series that will remain specifically for this user
            episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] = episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedEpisodeCount'] - episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
            episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain'] = episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedEpisodeCount'] - episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted']

            #check if the number of remaining played episodes is less than or equal to the minimum_number_played_episodes
            if (episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] <= minimum_number_played_episodes):
                #get the number of played episodes we will need to meet the requested minimum_number_played_episodes
                episode_gap = minimum_number_played_episodes - episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain']
                #check if the needed number of played episodes to meet the request minimum_number_played_episodes is available for this user
                if (episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] >= episode_gap):
                    #we have enough to fill the gap; incresed number of played episodes to remain; decrease the number of played episodes to be deleted by the delta
                    episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] += episode_gap
                    episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] -= episode_gap
                #when there are not enough played episodes to meet the requested minimum_number_played_episodes
                else: #(episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] < episode_gap):
                    #take everything there is; to incresed number of played episodes to remain as much as possible and to decrease the number of played episodes to be deleted by the same amount
                    episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] += episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                    episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] -= episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']

                #determine the total number of remaining episodes both played and unplayed
                total_remaining = episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] + episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain']
                #check if total_remaining meets the requested minimum_number_episodes
                if (total_remaining <= minimum_number_episodes):
                    #determine the number of episodes needed to fill the gap
                    episode_gap = minimum_number_episodes - total_remaining
                    #check if the needed number of unplayed episodes to meet the request minimum_number_episodes is available for this user
                    if (episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] >= episode_gap):
                        #we have enough to fill the gap; incresed number of unplayed episodes to remain; decrease the number of unplayed episodes to be deleted by the delta
                        episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain'] += episode_gap
                        episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] -= episode_gap
                    #when there are not enough unplayed episodes to meet the requested minimum_number_episodes
                    else: #(episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] < episode_gap):
                        #take everything there is; to incresed number of unplayed episodes to remain as much as possible and to decrease the number of unplayed episodes to be deleted by the same amount
                        episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain'] += episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted']
                        episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] -= episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted']

                    #determine the total number of remaining episodes both played and unplayed
                    total_remaining = episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] + episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain']
                    #check if total_remaining meets the requested minimum_number_episodes
                    if (total_remaining < minimum_number_episodes):
                        #determine the number of episodes needed to fill the gap
                        episode_gap = minimum_number_episodes - total_remaining
                        #check if the needed number of played episodes to meet the request minimum_number_episodes is available for this user
                        if (episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] >= episode_gap):
                            #we have enough to fill the gap; incresed number of played episodes to remain; decrease the number of played episodes to be deleted by the delta
                            episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] += episode_gap
                            episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] -= episode_gap
                        #when there are not enough played episodes to meet the requested minimum_number_episodes
                        else: #(episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] >= episode_gap):
                            #take everything there is; to incresed number of played episodes to remain as much as possible and to decrease the number of played episodes to be deleted by the same amount
                            episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] += episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                            episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] -= episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']

    #loop thru each item in the list of items that may be deleted
    for deleteItem in deleteItems:
        #verify media item is an episode
        #if (episodeItem['Type'] == 'Episode'):
        if (deleteItem['Type'] == 'Episode'):
            #add serieid to episode tracker if it does not already exist
            if not (deleteItem['SeriesId'] in episodeTracker):
                episodeTracker[deleteItem['SeriesId']]={}
            #gather information needed to build grid to determine season/episode order of each episode
            if not (deleteItem['Id'] in episodeTracker[deleteItem['SeriesId']]):
                if not ('MaxSeason' in episodeTracker[deleteItem['SeriesId']]):
                    episodeTracker[deleteItem['SeriesId']]['MaxSeason'] = 0
                if not ('MaxEpisode' in episodeTracker[deleteItem['SeriesId']]):
                    episodeTracker[deleteItem['SeriesId']]['MaxEpisode'] = 0
                if (deleteItem['ParentIndexNumber'] > episodeTracker[deleteItem['SeriesId']]['MaxSeason']):
                    episodeTracker[deleteItem['SeriesId']]['MaxSeason'] = deleteItem['ParentIndexNumber']
                if (deleteItem['IndexNumber'] > episodeTracker[deleteItem['SeriesId']]['MaxEpisode']):
                    episodeTracker[deleteItem['SeriesId']]['MaxEpisode'] = deleteItem['IndexNumber']
                #create dictionary entry containg season and episode number for each episode
                episodeTracker[deleteItem['SeriesId']][deleteItem['Id']]=defaultdict(dict)
                episodeTracker[deleteItem['SeriesId']][deleteItem['Id']][deleteItem['ParentIndexNumber']]=deleteItem['IndexNumber']

    #loop thru each series in the episode tracker
    for seriesId in episodeTracker:
        #create an season x episode grid for each series
        episodeTracker[seriesId]['SeasonEpisodeGrid'] = [[''] * (episodeTracker[seriesId]['MaxEpisode'] + 1) for x in range(episodeTracker[seriesId]['MaxSeason'] + 1)]

        #loop thru each episode for the series
        for episodeId in episodeTracker[seriesId]:
            #ignore non-essential data
            if not ((episodeId == 'MaxSeason') or (episodeId == 'MaxEpisode') or (episodeId == 'SeasonEpisodeGrid')):
                #get the key for this entry which is the season number
                seasonNum=list(episodeTracker[seriesId][episodeId].keys())
                #user the season number and the value from the season number key (aka episode number) to save the episodeId in the correct grid position
                episodeTracker[seriesId]['SeasonEpisodeGrid'][seasonNum[0]][episodeTracker[seriesId][episodeId][seasonNum[0]]]=episodeId

    #check if minimum_number_episodes_behavior is equal to any of the behaviorType keys
    if (minimum_number_episodes_behavior_modified in behaviorTypesKeys_List):
        min_num_episode_behavior = behaviorTypes[minimum_number_episodes_behavior_modified]
    #check if minimum_number_episodes_behavior is a userName or userId
    else:
        #loop thru userNames:userIds
        for userInfo in user_keys:
            #check if match has already been made
            if (username_userid_match == False):
                #split userName and userId into a list
                userNames_userIds_List=userInfo.split(":")
                #make possible userName strings ot be compared case insensitive
                if (userNames_userIds_List[0].casefold() == minimum_number_episodes_behavior.casefold()):
                    #userName match found
                    min_num_episode_behavior = behaviorTypes['username']
                    username_userid_match=True
                #make possible userId strings ot be compared case insensitive
                if (userNames_userIds_List[1].casefold() == minimum_number_episodes_behavior.casefold()):
                    #userId match found
                    min_num_episode_behavior = behaviorTypes['userid']
                    username_userid_match=True
        #check if behavior set to userName or userId
        if (min_num_episode_behavior in range(behaviorTypes['username'],(behaviorTypes['userid']+1))):
            #loop thru each series
            for seriesId in episodes_toBeDeletedOrRemain:
                #determine played and unplayed numbers specifically for this user
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = userNames_userIds_List[1]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = userNames_userIds_List[1]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][userNames_userIds_List[1]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][userNames_userIds_List[1]]['UnplayedToBeDeleted']
            #make sure we got here without matching a userName or userId
            if (username_userid_match == False):
                #if we did; prep for using the default behavior
                min_num_episode_behavior = 0
        #check if we made it this far without a match; if we did use the default behavior
        if (min_num_episode_behavior == 0):
            min_num_episode_behavior = behaviorTypes['defaultbehavior']

    #otherwise check if the desired behavior falls within the max/min played/unplyed ranges
    if (min_num_episode_behavior in range(behaviorTypes['maxplayed'],(behaviorTypes['maxplayedminplayed']+1))):
        #create lists to keep track of the user with the min/max played/unplayed number of episodes (first user with min/max value wins)
        maxPlayed_ToBeDeleted=['',-1]
        minPlayed_ToBeDeleted=['',-1]
        maxUnplayed_ToBeDeleted=['',-1]
        minUnplayed_ToBeDeleted=['',-1]
        #loop thru each series
        for seriesId in episodes_toBeDeletedOrRemain:
            #loop thru each user
            for userId in episodes_toBeDeletedOrRemain[seriesId]:
                #store value if greater than last
                if (episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] > maxPlayed_ToBeDeleted[1]):
                    maxPlayed_ToBeDeleted[1]=episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                    maxPlayed_ToBeDeleted[0]=userId

                    #initialize minimum value as max
                    if (minPlayed_ToBeDeleted[1] == -1):
                        minPlayed_ToBeDeleted[1]=episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                        minPlayed_ToBeDeleted[0]=userId

                #store value if greater than last
                if (episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] > maxUnplayed_ToBeDeleted[1]):
                    maxUnplayed_ToBeDeleted[1]=episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted']
                    maxUnplayed_ToBeDeleted[0]=userId

                    #initialize minimum value as max
                    if (minUnplayed_ToBeDeleted[1] == -1):
                        minUnplayed_ToBeDeleted[1]=episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted']
                        minUnplayed_ToBeDeleted[0]=userId

                #store value if less than last
                if (episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] < minPlayed_ToBeDeleted[1]):
                    minPlayed_ToBeDeleted[1]=episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                    minPlayed_ToBeDeleted[0]=userId

                #store value if less than last
                if (episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] < minUnplayed_ToBeDeleted[1]):
                    minUnplayed_ToBeDeleted[1]=episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted']
                    minUnplayed_ToBeDeleted[0]=userId

            #check for desired behaviorType; assign min/max played/unplayed valuse for each series depending on behaviorType
            if (min_num_episode_behavior == behaviorTypes['maxplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = maxPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = maxPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['minplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = minPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = minPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['maxunplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = maxUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = maxUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['minunplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = minUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = minUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['maxplayedmaxunplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = maxPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = maxUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['minplayedminunplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = minPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = minUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['maxplayedminunplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = maxPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = minUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['minplayedmaxunplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = minPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = maxUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['minunplayedminplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = minUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = minPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['minunplayedmaxunplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = minUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = maxUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['minunplayedmaxplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = minUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = maxPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['minplayedmaxplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = minPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = maxPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['maxunplayedminunplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = maxUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = minUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['maxunplayedminplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = maxUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = minPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['maxunplayedmaxplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = maxUnplayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = maxPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]]['UnplayedToBeDeleted']
            elif (min_num_episode_behavior == behaviorTypes['maxplayedminplayed']):
                episodeTracker[seriesId]['PlayedToBeDeleted_Id'] = maxPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['UnplayedToBeDeleted_Id'] = minPlayed_ToBeDeleted[0]
                episodeTracker[seriesId]['PlayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]]['PlayedToBeDeleted']
                episodeTracker[seriesId]['UnplayedToBeDeleted'] = episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]]['UnplayedToBeDeleted']

    #loop thru each series
    for seriesId in episodeTracker:
        #initialize loop check controls
        PlayedToBeDeleted_LoopControl=0
        UnplayedToBeDeleted_LoopControl=0

        #initialize list of episodes to be kept for each series
        if not ('TargetedEpisodeIds' in episodeTracker[seriesId]):
            episodeTracker[seriesId]['TargetedEpisodeIds']=[]

        #check if the number of played episodes to be deleted is greater than zero
        if (episodeTracker[seriesId]['PlayedToBeDeleted'] > 0):
            #loop thru seasons of season/episode grid
            for seasonNum in range(len(episodeTracker[seriesId]['SeasonEpisodeGrid'])):
                #loop thru episodes of season/episode grid
                for episodeNum in range(len(episodeTracker[seriesId]['SeasonEpisodeGrid'][seasonNum])):
                    #check if enough episodes have been removed to exhaust the number of played episodes to be deleted
                    if not (PlayedToBeDeleted_LoopControl >= episodeTracker[seriesId]['PlayedToBeDeleted']):
                        episodeId = episodeTracker[seriesId]['SeasonEpisodeGrid'][seasonNum][episodeNum]
                        #skip empty grid positions
                        if not (episodeId ==  ''):
                            #get played status for specified episodeId
                            if (get_ADDITIONAL_itemInfo(episodeTracker[seriesId]['PlayedToBeDeleted_Id'],episodeId,'filtering episode tracker grid for played item')['UserData']['Played']):
                                #add to list of episodes to be kept; increment tracker
                                episodeTracker[seriesId]['TargetedEpisodeIds'].append(episodeId)
                                PlayedToBeDeleted_LoopControl += 1

        #check if the number of unplayed episodes to be deleted is greater than zero
        if (episodeTracker[seriesId]['UnplayedToBeDeleted'] > 0):
            #loop thru seasons of season/episode grid
            for seasonNum in range(len(episodeTracker[seriesId]['SeasonEpisodeGrid'])):
                #loop thru episodes of season/episode grid
                for episodeNum in range(len(episodeTracker[seriesId]['SeasonEpisodeGrid'][seasonNum])):
                    #check if enough episodes have been removed to exhaust the number of played episodes to be deleted
                    if not (UnplayedToBeDeleted_LoopControl >= episodeTracker[seriesId]['UnplayedToBeDeleted']):
                        episodeId = episodeTracker[seriesId]['SeasonEpisodeGrid'][seasonNum][episodeNum]
                        #skip empty grid positions
                        if not (episodeId ==  ''):
                            #get played status for specified episodeId
                            if not (get_ADDITIONAL_itemInfo(episodeTracker[seriesId]['UnplayedToBeDeleted_Id'],episodeId,'filtering episode tracker grid for unplayed item')['UserData']['Played']):
                                #add to list of episodes to be kept; increment tracker
                                episodeTracker[seriesId]['TargetedEpisodeIds'].append(episodeId)
                                UnplayedToBeDeleted_LoopControl += 1

    #loop thru each series
    for seriesId in episodeTracker:
        #loop thru each item that may be deleted
        for delete_Items in deleteItems:
            #verify media item is an episode
            if (episodeItem['Type'] == 'Episode'):
                #loop thru each episode in the series
                for episodeId in episodeTracker[seriesId]['TargetedEpisodeIds']:
                    #check if episodeId matches and is to be deleted
                    if (episodeId == delete_Items['Id']):
                        deleteIndexes.append(deleteItems.index(delete_Items))

    #loop thru list of episodes that may be deleted
    for deleteItemIndex in reversed(range(len(deleteItems))):
        #verify media item is an episode
        if (deleteItems[deleteItemIndex]['Type'] == 'Episode'):
            #check if item does not match what was stored above and then remove it from the list of items to be deleted
            if not (deleteItemIndex in deleteIndexes):
                #remove episode from delete list
                deleteItems.pop(deleteItemIndex)

    return(deleteItems)


#Handle whitelists across multiple users by ID
def get_iswhitelist_ByMultiUser(whitelists, deleteItems):
    all_whitelists=set()
    deleteIndexes=[]

    #build whitelist dictionary
    for whitelist in whitelists:
        #read and split paths to compare to
        whitelist_split=whitelist.split(',')
        #add whitelist paths to set
        for wlist in whitelist_split:
            if not (wlist == ''):
                all_whitelists.add(wlist)

    #loop thru all whitelists and items to be deleted
    #remove item if it matches a whitelisted path
    for delIndex in range(len(deleteItems)):
        for whitelist in all_whitelists:
            delItemIsWhitelisted, delItemWhitelistedValue=get_isItemMatching(deleteItems[delIndex]['Id'], whitelist)
            if (delItemIsWhitelisted):
                deleteIndexes.append(delIndex)

    #converting to a set and then back to a list removes duplicates
    deleteIndexes=list(set(deleteIndexes))

    #sort indexes needed to remove items from deletion that we want to keep
    deleteIndexes.sort()

    #reverse the order to not worry about shifting indexes when removing items from deleteItems list
    deleteIndexes.reverse()

    #remove favorited items we want to keep
    for wlItem in deleteIndexes:
        try:
           deleteItems.pop(wlItem)
        except IndexError as err:
           print_byType("\n" + str(err),False)
           print_byType("\n" + convert2json(wlItem),False)
           print_byType("\n" + convert2json(deleteIndexes),False)
           print_byType("\n" + convert2json(deleteItems),False)
           exit(0)

    return(deleteItems)


#Handle whitetags across multiple users by ID
def get_iswhitetagged_ByMultiUser(whitetags, deleteItems):
    return get_iswhitelist_ByMultiUser(whitetags, deleteItems)


#Determine if a blacktagged item has been watched by all monitored users
def get_isblacktagged_watchedByAllUsers(blacktagged_and_watched, deleteItems):

    removeItem_list=[]
    pos_tracker=[]
    #temp_deleteItems=deleteItems.copy()

    for userId in blacktagged_and_watched:
        for itemId in blacktagged_and_watched[userId]:
            if not (itemId in removeItem_list):
                if (blacktagged_and_watched[userId][itemId]):
                    all_users_watched=True
                    for sub_userId in blacktagged_and_watched:
                        if not (itemId in blacktagged_and_watched[sub_userId]):
                            all_users_watched=False
                    if not (all_users_watched):
                        removeItem_list.append(itemId)

    #converting to a set and then back to a list removes duplicates
    removeItem_list=list(set(removeItem_list))

    i=0
    for delItemPos in deleteItems:
        for remItemPos in removeItem_list:
            if (delItemPos['Id'] == remItemPos):
                pos_tracker.append(i)
        i+=1

    #converting to a set and then back to a list removes duplicates
    pos_tracker=list(set(pos_tracker))

    #reverse the order to not worry about shifting indexes when removing items from deleteItems list
    pos_tracker.reverse()

    #remove items we do not want to delete
    for delItem in pos_tracker:
        try:
           deleteItems.pop(delItem)
        except IndexError as err:
           print_byType("\n" + str(err),False)
           print_byType("\n" + convert2json(delItem),False)
           print_byType("\n" + convert2json(pos_tracker),False)
           print_byType("\n" + convert2json(deleteItems),False)
           exit(0)

    return (deleteItems)


#Determine if media item met the play count filter for all users
def get_isplaycount_MetByAllUsers(playcount_met, deleteItems):
    return get_isblacktagged_watchedByAllUsers(playcount_met, deleteItems)


# determine if media item has been played specified amount of times
def get_playedStatus(item,media_condition,filter_count_comparison,filter_count):

    item_play_count=item['UserData']['PlayCount']
    item_played=item['UserData']['Played']

    if (media_condition == 'created'):
        IsPlayed=get_isCreated_FilterValue(filter_count_comparison,filter_count)
    else:
        IsPlayed='True'

    item_matches_played_count_filter=False

    if (((IsPlayed == 'True') and item_played) or ((IsPlayed == 'False') and not item_played) or (IsPlayed == '')):
        if (filter_count_comparison == '>'):
            if (item_play_count > filter_count):
                #media item play count greater than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '<'):
            if (item_play_count < filter_count):
                #media item play count less than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '>='):
            if (item_play_count >= filter_count):
                #media item play count greater than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '<='):
            if (item_play_count <= filter_count):
                #media item play count less than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '=='):
            if (item_play_count == filter_count):
                #media item play count equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not >'):
            if (not (item_play_count > filter_count)):
                #media item play count not greater than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not <'):
            if (not (item_play_count < filter_count)):
                #media item play count not less than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not >='):
            if (not (item_play_count >= filter_count)):
                #media item play count not greater than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not <='):
            if (not (item_play_count <= filter_count)):
                #media item play count not less than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not =='):
            if (not (item_play_count == filter_count)):
                #media item play count not equal to specified value
                item_matches_played_count_filter=True

    if (GLOBAL_DEBUG):
        print_byType("\nDoes Media Item " + str(item['Id']) + " Meet The " + media_condition + " Count Filter?...",False)
        print_byType("\n" + str(item_play_count) + " " + filter_count_comparison + " " + str(filter_count) + " : " + str(item_matches_played_count_filter),False)

    return item_matches_played_count_filter


# determine if media item has been played specified amount of times
def get_createdStatus(item,media_condition,filter_count_comparison,filter_count):
    return get_playedStatus(item,media_condition,filter_count_comparison,filter_count)


#decide if this item is ok to be deleted; still has to meet other criteria
def get_deleteStatus(item_matches_played_count_filter,item_matches_played_condition_day_filter,item_matches_created_played_count_filter,item_matches_created_condition_day_filter,itemisfav_Local,itemisfav_Advanced,itemIsWhiteTagged,itemIsBlackTagged,itemIsWhiteListed_Local,itemIsWhiteListed_Remote):

    #when item is favorited or whitetagged do not allow it to be deleted
    if (itemisfav_Local or itemisfav_Advanced or itemIsWhiteTagged):
        okToDelete=False
    #when item is blacktagged allow it to be deleted
    elif (itemIsBlackTagged and ((item_matches_played_count_filter and item_matches_played_condition_day_filter) or (item_matches_created_played_count_filter and item_matches_created_condition_day_filter))):
        okToDelete=True
    #when item is whitelisted do not allow it to be deleted
    elif (itemIsWhiteListed_Local or itemIsWhiteListed_Remote):
        okToDelete=False
    #when item is blacklisted allow it to be deleted
    elif ((item_matches_played_count_filter and item_matches_played_condition_day_filter) or (item_matches_created_played_count_filter and item_matches_created_condition_day_filter)):
        okToDelete=True
    else: #do not allow item to be deleted
        okToDelete=False

    if (GLOBAL_DEBUG):
        print_byType("\nIs Media Item OK To Delete: " + str(okToDelete),False)
        print_byType("\nIs Media Item Favorited For This User: " + str(itemisfav_Local),False)
        print_byType("\nIs Media Item An Advanced Favorite: " + str(itemisfav_Advanced),False)
        print_byType("\nIs Media Item WhiteTagged: " + str(itemIsWhiteTagged),False)
        print_byType("\nIs Media Item BlackTagged: " + str(itemIsBlackTagged),False)
        print_byType("\nDoes Media Item Match The Play Count Filter: " + str(item_matches_played_count_filter),False)
        print_byType("\nDoes Media Item Meet Number Of Days Since Played: " + str(item_matches_played_condition_day_filter),False)
        print_byType("\nDoes Media Item Match The Created Played Count Filter: " + str(item_matches_created_played_count_filter),False)
        print_byType("\nDoes Media Item Meet Number Of Days Since Created-Played: " + str(item_matches_created_condition_day_filter),False)
        print_byType("\nIs Media Item WhiteListed For This User: " + str(itemIsWhiteListed_Local),False)
        print_byType("\nIs Media Item WhiteListed For Another User: " + str(itemIsWhiteListed_Remote),False)

    return okToDelete


#check if desired metadata exists
# if it does not populate it with unknown
def prepare_MOVIEoutput(item):

    if (GLOBAL_DEBUG):
        print_byType("\n\nPreparing Movie " + item['Id'] + " For Output",False)

    if not ('Type' in item):
        item['Type']='Movie'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Type'] Was Missing",False)
    if not ('Name' in item):
        item['Name']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Name'] Was Missing",False)
    if not ('Studios' in item):
        item['Studios']=[0]
        item['Studios'][0]={'Name':'Unknown'}
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Studios'] or item['Studios'][0] Was Missing",False)
    if not (does_index_exist(item['Studios'],0)):
        item['Studios']=[0]
        item['Studios'][0]={'Name':'Unknown'}
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Studios'][0] or item['Studios'][0]{'Name':'Unknown'} Was Missing",False)
    if not ('Name' in item['Studios'][0]):
        item['Studios'][0]={'Name':'Unknown'}
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Studios'][0]{'Name':'Unknown'} Was Missing",False)
    if ((item['UserData']['Played'] == True) and (item['UserData']['PlayCount'] >= 1)):
        if not ('LastPlayedDate' in item['UserData']):
            item['UserData']['LastPlayedDate']='1970-01-01T00:00:00.00Z'
            if (GLOBAL_DEBUG):
                print_byType("\nitem['UserData']['LastPlayedDate'] Was Missing",False)
    else:
        item['UserData']['LastPlayedDate']='Unplayed'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['UserData']['LastPlayedDate'] Was Missing",False)
    if not ('DateCreated' in item):
        item['DateCreated']='1970-01-01T00:00:00.00Z'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['DateCreated'] Was Missing",False)
    if not ('Id' in item):
        item['Id']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Id'] Was Missing",False)

    if (GLOBAL_DEBUG):
        print_byType("\nFinished Preparing Movie " + item['Id'] + " For Output",False)

    return item


#check if desired metadata exists
# if it does not populate it with unknown
def prepare_EPISODEoutput(item):

    if (GLOBAL_DEBUG):
        print_byType("\n\nPreparing Episode " + item['Id'] + " For Output",False)

    if not ('Type' in item):
        item['Type']='Episode'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Type'] Was Missing",False)
    if not ('SeriesName' in item):
        item['SeriesName']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['SeriesName'] Was Missing",False)
    if not ('ParentIndexNumber' in item):
        item['ParentIndexNumber']='??'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['ParentIndexNumber'] Was Missing",False)
    if not ('IndexNumber' in item):
        item['IndexNumber']='??'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['IndexNumber'] Was Missing",False)
    if not ('Name' in item):
        item['Name']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Name'] Was Missing",False)
    if not ('SeriesStudio' in item):
        item['SeriesStudio']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['SeriesStudio'] Was Missing",False)
    if ((item['UserData']['Played'] == True) and (item['UserData']['PlayCount'] >= 1)):
        if not ('LastPlayedDate' in item['UserData']):
            item['UserData']['LastPlayedDate']='1970-01-01T00:00:00.00Z'
            if (GLOBAL_DEBUG):
                print_byType("\nitem['UserData']['LastPlayedDate'] Was Missing",False)
    else:
        item['UserData']['LastPlayedDate']='Unplayed'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['UserData']['LastPlayedDate'] Was Missing",False)
    if not ('DateCreated' in item):
        item['DateCreated']='1970-01-01T00:00:00.00Z'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['DateCreated'] Was Missing",False)
    if not ('Id' in item):
        item['Id']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Id'] Was Missing",False)

    if (GLOBAL_DEBUG):
        print_byType("\nFinished Preparing Episode " + item['Id'] + " For Output",False)

    return item


#check if desired metadata exists
# if it does not populate it with unknown
def prepare_AUDIOoutput(item):

    if (GLOBAL_DEBUG):
        print_byType("\n\nPreparing Audio/AudioBook " + item['Id'] + " For Output",False)

    if not ('Type' in item):
        item['Type']='Episode'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Type'] Was Missing",False)
    if not ('IndexNumber' in item):
        item['IndexNumber']=999
        if (GLOBAL_DEBUG):
            print_byType("\nitem['IndexNumber'] Was Missing",False)
    if not ('Name' in item):
        item['Name']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Name'] Was Missing",False)
    if not ('Album' in item):
        item['Album']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Album'] Was Missing",False)
    if not ('Artist' in item):
        item['Artist']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Artist'] Was Missing",False)
    if not ('Studios' in item):
        item['Studios']=[{'Name':'Unknown'}]
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Studios'] Was Missing",False)
    if not (does_index_exist(item['Studios'],0)):
        item['Studios']=[{'Name':'Unknown'}]
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Studios']{'Name':'Unknown'} Was Missing",False)
    if ((item['UserData']['Played'] == True) and (item['UserData']['PlayCount'] >= 1)):
        if not ('LastPlayedDate' in item['UserData']):
            item['UserData']['LastPlayedDate']='1970-01-01T00:00:00.00Z'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['UserData']['LastPlayedDate'] Was Missing",False)
    else:
        item['UserData']['LastPlayedDate']='Unplayed'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['UserData']['LastPlayedDate'] Was Missing",False)
    if not ('DateCreated' in item):
        item['DateCreated']='1970-01-01T00:00:00.00Z'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['DateCreated'] Was Missing",False)
    if not ('Id' in item):
        item['Id']='Unknown'
        if (GLOBAL_DEBUG):
            print_byType("\nitem['Id'] Was Missing",False)

    if (GLOBAL_DEBUG):
        print_byType("\nFinished Preparing Audio/AudioBook " + item['Id'] + " For Output",False)

    return item


#check if desired metadata exists
# if it does not populate it with unknown
def prepare_AUDIOBOOKoutput(item):
    return prepare_AUDIOoutput(item)


#determine if the requested console output line should be shown or hidden
def print_byType(string_to_print,ok_to_print):
    if (ok_to_print):
        print(string_to_print)
    if (GLOBAL_DEBUG):
        save_file(string_to_print,GLOBAL_debugFileName,"a")


# get played, favorited, and tagged media items
# save media items ready to be deleted
# remove media items with exceptions (i.e. favorited, whitelisted, whitetagged, etc...)
def get_media_items():
    server_brand=cfg.server_brand
    server_url=cfg.server_url
    auth_key=cfg.auth_key
    api_query_attempts=cfg.api_query_attempts
    movie_played_days=cfg.movie_played_days
    movie_created_days=cfg.movie_created_days
    episode_played_days=cfg.episode_played_days
    episode_created_days=cfg.episode_created_days
    audio_played_days=cfg.audio_played_days
    audio_created_days=cfg.audio_created_days
    if (cfg.server_brand == 'jellyfin'):
        audiobook_played_days=cfg.audiobook_played_days
        audiobook_created_days=cfg.audiobook_created_days
    else:
        audiobook_played_days=-1
        audiobook_created_days=-1
    blacktags=cfg.blacktag
    whitetags=cfg.whitetag
    print_script_header=cfg.print_script_header
    print_warnings=cfg.print_warnings
    print_user_header=cfg.print_user_header
    print_movie_delete_info=cfg.print_movie_delete_info
    print_movie_keep_info=cfg.print_movie_keep_info
    print_episode_delete_info=cfg.print_episode_delete_info
    print_episode_keep_info=cfg.print_episode_keep_info
    print_audio_delete_info=cfg.print_audio_delete_info
    print_audio_keep_info=cfg.print_audio_keep_info
    if (cfg.server_brand == 'jellyfin'):
        print_audiobook_delete_info=cfg.print_audiobook_delete_info
        print_audiobook_keep_info=cfg.print_audiobook_keep_info
    else:
        print_audiobook_delete_info=False
        print_audiobook_keep_info=False

    #establish deletion date for played media items
    date_time_now=datetime.now(timezone.utc)

    if ((movie_played_days >= 0) or (movie_created_days >= 0)):
        #movie_played_days=cfg.movie_played_days
        movie_played_count_comparison=cfg.movie_played_count_comparison
        movie_created_played_count_comparison=cfg.movie_created_played_count_comparison
        movie_played_count=cfg.movie_played_count
        movie_created_played_count=cfg.movie_created_played_count
        multiuser_play_count_movie=cfg.multiuser_play_count_movie
        keep_favorites_movie=cfg.keep_favorites_movie
        multiuser_whitelist_movie=cfg.multiuser_whitelist_movie
        delete_blacktagged_movie=cfg.delete_blacktagged_movie
        #dictionary for episodes to keep to meet cfg.minimum_number_episodes
        keep_favorites_advanced_movie_genre=cfg.keep_favorites_advanced_movie_genre
        keep_favorites_advanced_movie_library_genre=cfg.keep_favorites_advanced_movie_library_genre
        cut_off_date_played_movie=date_time_now - timedelta(movie_played_days)
        cut_off_date_created_movie=date_time_now - timedelta(movie_created_days)
        #dictionary of favorited items by userId
        isfav_byUserId_Movie={}
        #dictionary of items meeting the play count filter by userId
        isMeeting_PlayCountFilter_Movie={}
        #dictionary of blacktagged items by userId
        isblacktag_and_watched_byUserId_Movie={}
        #whitelisted Id per media type according to media types metadata
        movie_whitelists=[]
        #blacktagged items per media type according to media types metadata
        movie_blacktaglists=[]
        #whitetagged items per media type according to media types metadata
        movie_whitetag_list=[]
    if ((episode_played_days >= 0) or (episode_created_days >= 0)):
        #episode_condition=cfg.episode_condition
        #episode_played_days=cfg.episode_played_days
        episode_played_count_comparison=cfg.episode_played_count_comparison
        episode_created_played_count_comparison=cfg.episode_created_played_count_comparison
        episode_played_count=cfg.episode_played_count
        episode_created_played_count=cfg.episode_created_played_count
        multiuser_play_count_episode=cfg.multiuser_play_count_episode
        keep_favorites_episode=cfg.keep_favorites_episode
        multiuser_whitelist_episode=cfg.multiuser_whitelist_episode
        delete_blacktagged_episode=cfg.delete_blacktagged_episode
        episodeCounts_byUserId={}
        minimum_number_episodes=cfg.minimum_number_episodes
        minimum_number_played_episodes=cfg.minimum_number_played_episodes
        keep_favorites_advanced_episode_genre=cfg.keep_favorites_advanced_episode_genre
        keep_favorites_advanced_season_genre=cfg.keep_favorites_advanced_season_genre
        keep_favorites_advanced_series_genre=cfg.keep_favorites_advanced_series_genre
        keep_favorites_advanced_tv_library_genre=cfg.keep_favorites_advanced_tv_library_genre
        keep_favorites_advanced_tv_studio_network=cfg.keep_favorites_advanced_tv_studio_network
        keep_favorites_advanced_tv_studio_network_genre=cfg.keep_favorites_advanced_tv_studio_network_genre
        cut_off_date_played_episode=date_time_now - timedelta(episode_played_days)
        cut_off_date_created_episode=date_time_now - timedelta(episode_created_days)
        #dictionary of favorited items by userId
        isfav_byUserId_Episode={}
        #dictionary of items meeting the play count filter by userId
        isMeeting_PlayCountFilter_Episode={}
        #dictionary of blacktagged items by userId
        isblacktag_and_watched_byUserId_Episode={}
        #whitelisted Id per media type according to media types metadata
        episode_whitelists=[]
        #blacktagged items per media type according to media types metadata
        episode_blacktaglists=[]
        #whitetagged items per media type according to media types metadata
        episode_whitetag_list=[]
    if ((audio_played_days >= 0) or (audio_created_days >= 0)):
        #audio_condition=cfg.audio_condition
        #audio_played_days=cfg.audio_played_days
        audio_played_count_comparison=cfg.audio_played_count_comparison
        audio_created_played_count_comparison=cfg.audio_created_played_count_comparison
        audio_played_count=cfg.audio_played_count
        audio_created_played_count=cfg.audio_created_played_count
        multiuser_play_count_audio=cfg.multiuser_play_count_audio
        keep_favorites_audio=cfg.keep_favorites_audio
        multiuser_whitelist_audio=cfg.multiuser_whitelist_audio
        delete_blacktagged_audio=cfg.delete_blacktagged_audio
        keep_favorites_advanced_track_genre=cfg.keep_favorites_advanced_track_genre
        keep_favorites_advanced_album_genre=cfg.keep_favorites_advanced_album_genre
        keep_favorites_advanced_music_library_genre=cfg.keep_favorites_advanced_music_library_genre
        keep_favorites_advanced_track_artist=cfg.keep_favorites_advanced_track_artist
        keep_favorites_advanced_album_artist=cfg.keep_favorites_advanced_album_artist
        cut_off_date_played_audio=date_time_now - timedelta(audio_played_days)
        cut_off_date_created_audio=date_time_now - timedelta(audio_created_days)
        #dictionary of favorited items by userId
        isfav_byUserId_Audio={}
        #dictionary of items meeting the play count filter by userId
        isMeeting_PlayCountFilter_Audio={}
        #dictionary of blacktagged items by userId
        isblacktag_and_watched_byUserId_Audio={}
        #whitelisted Id per media type according to media types metadata
        audio_whitelists=[]
        #blacktagged items per media type according to media types metadata
        audio_blacktaglists=[]
        #whitetagged items per media type according to media types metadata
        audio_whitetag_list=[]
    if ((audiobook_played_days >= 0) or (audiobook_created_days >= 0)):
        #audiobook_condition=cfg.audiobook_condition
        #audiobook_played_days=cfg.audiobook_played_days
        audiobook_played_count_comparison=cfg.audiobook_played_count_comparison
        audiobook_created_played_count_comparison=cfg.audiobook_created_played_count_comparison
        audiobook_played_count=cfg.audiobook_played_count
        audiobook_created_played_count=cfg.audiobook_created_played_count
        multiuser_play_count_audiobook=cfg.multiuser_play_count_audiobook
        keep_favorites_audiobook=cfg.keep_favorites_audiobook
        multiuser_whitelist_audiobook=cfg.multiuser_whitelist_audiobook
        delete_blacktagged_audiobook=cfg.delete_blacktagged_audiobook
        keep_favorites_advanced_audio_book_track_genre=cfg.keep_favorites_advanced_audio_book_track_genre
        keep_favorites_advanced_audio_book_genre=cfg.keep_favorites_advanced_audio_book_genre
        keep_favorites_advanced_audio_book_library_genre=cfg.keep_favorites_advanced_audio_book_library_genre
        keep_favorites_advanced_audio_book_track_author=cfg.keep_favorites_advanced_audio_book_track_author
        keep_favorites_advanced_audio_book_author=cfg.keep_favorites_advanced_audio_book_author
        cut_off_date_played_audiobook=date_time_now - timedelta(audiobook_played_days)
        cut_off_date_created_audiobook=date_time_now - timedelta(audiobook_created_days)
        #dictionary of favorited items by userId
        isfav_byUserId_AudioBook={}
        #dictionary of items meeting the play count filter by userId
        isMeeting_PlayCountFilter_AudioBook={}
        #dictionary of blacktagged items by userId
        isblacktag_and_watched_byUserId_AudioBook={}
        #whitelisted Id per media type according to media types metadata
        audiobook_whitelists=[]
        #blacktagged items per media type according to media types metadata
        audiobook_blacktaglists=[]
        #whitetagged items per media type according to media types metadata
        audiobook_whitetag_list=[]

    if (GLOBAL_DEBUG):
        print_script_header=True
        print_warnings=True
        print_user_header=True
        print_movie_delete_info=True
        print_movie_keep_info=True
        print_episode_delete_info=True
        print_episode_keep_info=True
        print_audio_delete_info=True
        print_audio_keep_info=True
        print_audiobook_delete_info=True
        print_audiobook_keep_info=True

    print_common_delete_keep_info=(print_movie_delete_info or print_movie_keep_info or print_episode_delete_info or print_episode_keep_info or
                                    print_audio_delete_info or print_audio_keep_info or print_audiobook_delete_info or print_audiobook_keep_info)

    #Get list of all played items
    if (GLOBAL_DEBUG):
        #Double newline for debug log formatting
        print_byType('\n\n',False)
    print_byType('-----------------------------------------------------------',print_script_header)
    if (GLOBAL_DEBUG):
        print_byType('\n',False)
    print_byType('Start...',print_script_header)
    if (GLOBAL_DEBUG):
        print_byType('\n',False)
    print_byType('Cleaning media for server at: ' + server_url,print_script_header)
    if (GLOBAL_DEBUG):
        print_byType('\n',False)
    print_byType('-----------------------------------------------------------',print_script_header)
    if (GLOBAL_DEBUG):
        print_byType('\n',False)
    print_byType('',print_script_header)

    all_media_disabled=False

    if (
       (movie_played_days == -1) and
       (episode_played_days == -1) and
       (audio_played_days == -1) and
       ((hasattr(cfg, 'audiobook_played_days') and (audiobook_played_days == -1)) or (not hasattr(cfg, 'audiobook_played_days'))) and
       (movie_created_days == -1) and
       (episode_created_days == -1) and
       (audio_created_days == -1) and
       ((hasattr(cfg, 'audiobook_created_days') and (audiobook_created_days == -1)) or (not hasattr(cfg, 'audiobook_created_days')))
       ):
        print_byType('* ATTENTION!!!                                            *',print_warnings)
        print_byType('* No media types are being monitored.                     *',print_warnings)
        print_byType('* Open the mumc_config.py file in a text editor.          *',print_warnings)
        print_byType('* Set at least one media type to >=0.                     *',print_warnings)
        print_byType('*                                                         *',print_warnings)
        print_byType('* movie_played_days=-1                                    *',print_warnings)
        print_byType('* episode_played_days=-1                                  *',print_warnings)
        print_byType('* audio_played_days=-1                                    *',print_warnings)
        if (server_brand == 'jellyfin'):
            print_byType('* audiobook_played_days=-1                            *',print_warnings)
        print_byType('*                                                         *',print_warnings)
        print_byType('* movie_created_days=-1                                   *',print_warnings)
        print_byType('* episode_created_days=-1                                 *',print_warnings)
        print_byType('* audio_created_days=-1                                   *',print_warnings)
        if (server_brand == 'jellyfin'):
            print_byType('* audiobook_created_days=-1                           *',print_warnings)
        print_byType('-----------------------------------------------------------',print_warnings)
        all_media_disabled=True

    #list of items to be deleted
    deleteItems=[]

    #Build the library data from the data structures stored in the configuration file
    bluser_keys_json_verify,bluser_names_json_verify,user_bllib_keys_json,user_bllib_collectiontype_json,user_bllib_netpath_json,user_bllib_path_json=user_lib_builder(cfg.user_bl_libs)

    #Build the library data from the data structures stored in the configuration file
    wluser_keys_json_verify,wluser_names_json_verify,user_wllib_keys_json,user_wllib_collectiontype_json,user_wllib_netpath_json,user_wllib_path_json=user_lib_builder(cfg.user_wl_libs)

    #verify userIds are in same order for both blacklist and whitelist libraries
    if (bluser_keys_json_verify == wluser_keys_json_verify):
        user_keys_json = bluser_keys_json_verify
    else:
        if (GLOBAL_DEBUG):
            print_byType('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both',False)
        raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both')

    #verify userNames are in same order for both blacklist and whitelist libraries
    if (not (bluser_names_json_verify == wluser_names_json_verify)):
        if (GLOBAL_DEBUG):
            print_byType('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both',False)
        raise RuntimeError('\nUSERID_ERROR: cfg.user_bl_libs or cfg.user_wl_libs has been modified in mumc_config.py; userIds need to be in the same order for both')

    for user_key in user_keys_json:

        if ((movie_played_days >= 0) or (movie_created_days >= 0)):
            #define dictionary user_key to store media item favorite states by userId and itemId
            isfav_byUserId_Movie[user_key]={}
            #define dictionary user key to story media items meeting the play count filter by userId and itemId
            isMeeting_PlayCountFilter_Movie[user_key]={}
            #dictionary of blacktagged items by userId
            isblacktag_and_watched_byUserId_Movie[user_key]={}
        if ((episode_played_days >= 0) or (episode_created_days >= 0)):
            #define dictionary user_key to store media item favorite states by userId and itemId
            isfav_byUserId_Episode[user_key]={}
            #define dictionary user key to story media items meeting the play count filter by userId and itemId
            isMeeting_PlayCountFilter_Episode[user_key]={}
            #dictionary of blacktagged items by userId
            isblacktag_and_watched_byUserId_Episode[user_key]={}
            episodeCounts_byUserId[user_key]=defaultdict(dict)
        if ((audio_played_days >= 0) or (audio_created_days >= 0)):
            #define dictionary user_key to store media item favorite states by userId and itemId
            isfav_byUserId_Audio[user_key]={}
            #define dictionary user key to story media items meeting the play count filter by userId and itemId
            isMeeting_PlayCountFilter_Audio[user_key]={}
            #dictionary of blacktagged items by userId
            isblacktag_and_watched_byUserId_Audio[user_key]={}
        if ((audiobook_played_days >= 0) or (audiobook_created_days >= 0)):
            #define dictionary user_key to store media item favorite states by userId and itemId
            isfav_byUserId_AudioBook[user_key]={}
            #define dictionary user key to story media items meeting the play count filter by userId and itemId
            isMeeting_PlayCountFilter_AudioBook[user_key]={}
            #dictionary of blacktagged items by userId
            isblacktag_and_watched_byUserId_AudioBook[user_key]={}

    currentPosition=0

    for user_key in user_keys_json:
        url=server_url + '/Users/' + user_key  + '/?api_key=' + auth_key

        user_data=requestURL(url, GLOBAL_DEBUG, 'current_user', api_query_attempts)

        if (GLOBAL_DEBUG):
            print_byType('\n',False)
        print_byType('',print_user_header)
        if (GLOBAL_DEBUG):
            print_byType('\n',False)
        print_byType('-----------------------------------------------------------',print_user_header)
        if (GLOBAL_DEBUG):
            print_byType('\n',False)
        print_byType('Get List Of Media For:',print_user_header)
        if (GLOBAL_DEBUG):
            print_byType('\n',False)
        print_byType(user_data['Name'] + ' - ' + user_data['Id'],print_user_header)
        if (GLOBAL_DEBUG):
            print_byType('\n',False)
        print_byType('-----------------------------------------------------------',print_user_header)

        user_bllib_keys_json_lensplit=user_bllib_keys_json[currentPosition].split(',')
        user_wllib_keys_json_lensplit=user_wllib_keys_json[currentPosition].split(',')
        user_bllib_netpath_json_lensplit=user_bllib_netpath_json[currentPosition].split(',')
        user_wllib_netpath_json_lensplit=user_wllib_netpath_json[currentPosition].split(',')
        user_bllib_path_json_lensplit=user_bllib_path_json[currentPosition].split(',')
        user_wllib_path_json_lensplit=user_wllib_path_json[currentPosition].split(',')

        #make all list attributes the same length
        while not (len(user_bllib_keys_json_lensplit) == len(user_wllib_keys_json_lensplit)):
            if (len(user_bllib_keys_json_lensplit) > len(user_wllib_keys_json_lensplit)):
                user_wllib_keys_json_lensplit.append('')
                user_wllib_netpath_json_lensplit.append('')
                user_wllib_path_json_lensplit.append('')
            elif (len(user_bllib_keys_json_lensplit) < len(user_wllib_keys_json_lensplit)):
                user_bllib_keys_json_lensplit.append('')
                user_bllib_netpath_json_lensplit.append('')
                user_bllib_path_json_lensplit.append('')

        media_found=False

############# Movies #############

        if ((movie_played_days >= 0) or (movie_created_days >= 0)):

            if (GLOBAL_DEBUG):
                print_byType("\n\nProcessing MOVIE Items For UserId: " + str(user_key),False)

            user_processed_itemsId=set()

            currentSubPosition=0

            for LibraryID_BlkLst,LibraryID_WhtLst,LibraryNetPath_BlkLst,LibraryNetPath_WhtLst,LibraryPath_BlkLst,LibraryPath_WhtLst in zip(user_bllib_keys_json_lensplit,user_wllib_keys_json_lensplit,user_bllib_netpath_json_lensplit,user_wllib_netpath_json_lensplit,user_bllib_path_json_lensplit,user_wllib_path_json_lensplit):

                #Initialize api_query_handler() variables for watched media items in blacklists
                StartIndex_Blacklist=0
                TotalItems_Blacklist=1
                QueryLimit_Blacklist=1
                QueriesRemaining_Blacklist=True
                APIDebugMsg_Blacklist='movie_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for watched media items in blacklists
                    IncludeItemTypes_Blacklist='Movie'
                    FieldsState_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                    SortBy_Blacklist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Blacklist='Ascending'
                    EnableUserData_Blacklist='True'
                    Recursive_Blacklist='True'
                    EnableImages_Blacklist='False'
                    CollapseBoxSetItems_Blacklist='False'
                    if (movie_played_days >= 0):
                        IsPlayed_Blacklist=get_isPlayed_FilterValue(movie_played_count_comparison,movie_played_count)
                    else:
                        IsPlayed_Blacklist='disable'
                    if (movie_created_days >= 0):
                        IsCreated_Blacklist=get_isCreated_FilterValue(movie_created_played_count_comparison,movie_created_played_count)
                    else:
                        IsCreated_Blacklist='disable'
                    IsPlayedState_Blacklist=get_isPlayedCreated_FilterValue(IsPlayed_Blacklist,IsCreated_Blacklist)

                #Initialize api_query_handler() variables for Favorited from Blacklist media items
                StartIndex_Favorited_From_Blacklist=0
                TotalItems_Favorited_From_Blacklist=1
                QueryLimit_Favorited_From_Blacklist=1
                QueriesRemaining_Favorited_From_Blacklist=True
                APIDebugMsg_Favorited_From_Blacklist='movie_Favorited_From_Blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for Favorited_From_Blacklist media items
                    IncludeItemTypes_Favorited_From_Blacklist='Movie,BoxSet,CollectionFolder'
                    FieldsState_Favorited_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                    SortBy_Favorited_From_Blacklist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Favorited_From_Blacklist='Ascending'
                    EnableUserData_Favorited_From_Blacklist='True'
                    Recursive_Favorited_From_Blacklist='True'
                    EnableImages_Favorited_From_Blacklist='False'
                    CollapseBoxSetItems_Favorited_From_Blacklist='False'
                    IsFavorite_From_Blacklist='True'

                #Initialize api_query_handler() variables for Favorited from Whitelist media items
                StartIndex_Favorited_From_Whitelist=0
                TotalItems_Favorited_From_Whitelist=1
                QueryLimit_Favorited_From_Whitelist=1
                QueriesRemaining_Favorited_From_Whitelist=True
                APIDebugMsg_Favorited_From_Whitelist='movie_Favorited_From_Whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for Favorited_From_Whitelist media items
                    IncludeItemTypes_Favorited_From_Whitelist='Movie,BoxSet,CollectionFolder'
                    FieldsState_Favorited_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                    SortBy_Favorited_From_Whitelist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Favorited_From_Whitelist='Ascending'
                    EnableUserData_Favorited_From_Whitelist='True'
                    Recursive_Favorited_From_Whitelist='True'
                    EnableImages_Favorited_From_Whitelist='False'
                    CollapseBoxSetItems_Favorited_From_Whitelist='False'
                    IsFavorite_From_Whitelist='True'

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged_From_BlackList=0
                TotalItems_BlackTagged_From_BlackList=1
                QueryLimit_BlackTagged_From_BlackList=1
                QueriesRemaining_BlackTagged_From_BlackList=True
                APIDebugMsg_BlackTagged_From_BlackList='movie_blacktagged_from_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for blacktagged media items from blacklist
                    IncludeItemTypes_BlackTagged_From_BlackList='Movie,BoxSet,CollectionFolder'
                    FieldsState_BlackTagged_From_BlackList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                    SortBy_BlackTagged_From_BlackList='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_BlackTagged_From_BlackList='Ascending'
                    EnableUserData_Blacktagged_From_BlackList='True'
                    Recursive_Blacktagged_From_BlackList='True'
                    EnableImages_Blacktagged_From_BlackList='False'
                    CollapseBoxSetItems_Blacktagged_From_BlackList='False'
                    #Encode blacktags so they are url acceptable
                    BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged_From_WhiteList=0
                TotalItems_BlackTagged_From_WhiteList=1
                QueryLimit_BlackTagged_From_WhiteList=1
                QueriesRemaining_BlackTagged_From_WhiteList=True
                APIDebugMsg_BlackTagged_From_WhiteList='movie_blacktagged_from_whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for blacktagged media items from whitelist
                    IncludeItemTypes_BlackTagged_From_WhiteList='Movie,BoxSet,CollectionFolder'
                    FieldsState_BlackTagged_From_WhiteList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                    SortBy_BlackTagged_From_WhiteList='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_BlackTagged_From_WhiteList='Ascending'
                    EnableUserData_Blacktagged_From_WhiteList='True'
                    Recursive_Blacktagged_From_WhiteList='True'
                    EnableImages_Blacktagged_From_WhiteList='False'
                    CollapseBoxSetItems_Blacktagged_From_WhiteList='False'
                    #Encode blacktags so they are url acceptable
                    BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged_From_Blacklist=0
                TotalItems_WhiteTagged_From_Blacklist=1
                QueryLimit_WhiteTagged_From_Blacklist=1
                QueriesRemaining_WhiteTagged_From_Blacklist=True
                APIDebugMsg_WhiteTagged_From_Blacklist='movie_whitetagged_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for whitetagged media items
                    IncludeItemTypes_WhiteTagged_From_Blacklist='Movie,BoxSet,CollectionFolder'
                    FieldsState_WhiteTagged_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                    SortBy_WhiteTagged_From_Blacklist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_WhiteTagged_From_Blacklist='Ascending'
                    EnableUserData_Whitetagged_From_Blacklist='True'
                    Recursive_Whitetagged_From_Blacklist='True'
                    EnableImages_Whitetagged_From_Blacklist='False'
                    CollapseBoxSetItems_Whitetagged_From_Blacklist='False'
                    #Encode whitetags so they are url acceptable
                    WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged_From_Whitelist=0
                TotalItems_WhiteTagged_From_Whitelist=1
                QueryLimit_WhiteTagged_From_Whitelist=1
                QueriesRemaining_WhiteTagged_From_Whitelist=True
                APIDebugMsg_WhiteTagged_From_Whitelist='movie_whitetagged_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for whitetagged media items
                    IncludeItemTypes_WhiteTagged_From_Whitelist='Movie,BoxSet,CollectionFolder'
                    FieldsState_WhiteTagged_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                    SortBy_WhiteTagged_From_Whitelist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_WhiteTagged_From_Whitelist='Ascending'
                    EnableUserData_Whitetagged_From_Whitelist='True'
                    Recursive_Whitetagged_From_Whitelist='True'
                    EnableImages_Whitetagged_From_Whitelist='False'
                    CollapseBoxSetItems_Whitetagged_From_Whitelist='False'
                    #Encode whitetags so they are url acceptable
                    WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                QueryItemsRemaining_All=True

                while (QueryItemsRemaining_All):

                    if not (LibraryID_BlkLst == ''):
                        #Built query for watched items in blacklists
                        apiQuery_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Blacklist +
                        '&StartIndex=' + str(StartIndex_Blacklist) + '&Limit=' + str(QueryLimit_Blacklist) + '&IsPlayed=' + IsPlayedState_Blacklist +
                        '&Fields=' + FieldsState_Blacklist + '&Recursive=' + Recursive_Blacklist + '&SortBy=' + SortBy_Blacklist + '&SortOrder=' + SortOrder_Blacklist +
                        '&EnableImages=' + EnableImages_Blacklist + '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacklist + '&EnableUserData=' + EnableUserData_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        data_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,QueriesRemaining_Blacklist=api_query_handler(apiQuery_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,APIDebugMsg_Blacklist)
                    else:
                        #When no media items are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Blacklist=0
                        QueriesRemaining_Blacklist=False
                        if (GLOBAL_DEBUG):
                            print_byType("\n\nNo watched media items are blacklisted",False)

                    if not (LibraryID_BlkLst == ''):
                        #Built query for Favorited from Blacklist media items
                        apiQuery_Favorited_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Blacklist +
                        '&StartIndex=' + str(StartIndex_Favorited_From_Blacklist) + '&Limit=' + str(QueryLimit_Favorited_From_Blacklist) + '&Fields=' + FieldsState_Favorited_From_Blacklist +
                        '&Recursive=' + Recursive_Favorited_From_Blacklist + '&SortBy=' + SortBy_Favorited_From_Blacklist + '&SortOrder=' + SortOrder_Favorited_From_Blacklist + '&EnableImages=' + EnableImages_Favorited_From_Blacklist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Blacklist + '&IsFavorite=' + IsFavorite_From_Blacklist + '&EnableUserData=' + EnableUserData_Favorited_From_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for Favorited from Blacklist media items
                        data_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,QueriesRemaining_Favorited_From_Blacklist=api_query_handler(apiQuery_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,APIDebugMsg_Favorited_From_Blacklist)
                    else:
                        #When no media items are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Favorited_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Favorited_From_Blacklist=0
                        QueriesRemaining_Favorited_From_Blacklist=False
                        if (GLOBAL_DEBUG):
                            print_byType("\n\nNo favorited media items are blacklisted",False)

                    if not (LibraryID_WhtLst == ''):
                        #Built query for Favorited From Whitelist media items
                        apiQuery_Favorited_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Whitelist +
                        '&StartIndex=' + str(StartIndex_Favorited_From_Whitelist) + '&Limit=' + str(QueryLimit_Favorited_From_Whitelist) + '&Fields=' + FieldsState_Favorited_From_Whitelist +
                        '&Recursive=' + Recursive_Favorited_From_Whitelist + '&SortBy=' + SortBy_Favorited_From_Whitelist + '&SortOrder=' + SortOrder_Favorited_From_Whitelist + '&EnableImages=' + EnableImages_Favorited_From_Whitelist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Whitelist + '&IsFavorite=' + IsFavorite_From_Whitelist + '&EnableUserData=' + EnableUserData_Favorited_From_Whitelist + '&api_key=' + auth_key)

                        #Send the API query for for Favorited from Whitelist media items
                        data_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,QueriesRemaining_Favorited_From_Whitelist=api_query_handler(apiQuery_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,APIDebugMsg_Favorited_From_Whitelist)
                    else:
                        #When no media items are whitelisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
                        data_Favorited_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Favorited_From_Whitelist=0
                        QueriesRemaining_Favorited_From_Whitelist=False
                        if (GLOBAL_DEBUG):
                            print_byType("\n\nNo favorited media items are whitelisted",False)

                    #Check if blacktag or blacklist are not an empty strings
                    if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                        #Built query for blacktagged from blacklist media items
                        apiQuery_BlackTagged_From_BlackList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_BlackList +
                        '&StartIndex=' + str(StartIndex_BlackTagged_From_BlackList) + '&Limit=' + str(QueryLimit_BlackTagged_From_BlackList) + '&Fields=' + FieldsState_BlackTagged_From_BlackList +
                        '&Recursive=' + Recursive_Blacktagged_From_BlackList + '&SortBy=' + SortBy_BlackTagged_From_BlackList + '&SortOrder=' + SortOrder_BlackTagged_From_BlackList + '&EnableImages=' + EnableImages_Blacktagged_From_BlackList +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_BlackList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_BlackList + '&api_key=' + auth_key)

                        #Send the API query for for blacktagged from blacklist media items
                        data_Blacktagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,QueriesRemaining_BlackTagged_From_BlackList=api_query_handler(apiQuery_BlackTagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,APIDebugMsg_BlackTagged_From_BlackList)
                    else: #((BlackTags_Tagged == '') or (LibraryID_BlkLst == ''))
                        data_Blacktagged_From_BlackList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_BlackTagged_From_BlackList=0
                        QueriesRemaining_BlackTagged_From_BlackList=False
                        if (GLOBAL_DEBUG):
                            print_byType("\n\nNo blacktagged media items are blacklisted",False)

                    #Check if blacktag or whitelist are not an empty strings
                    if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                        #Built query for blacktagged from whitelist media items
                        apiQuery_BlackTagged_From_WhiteList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_WhiteList +
                        '&StartIndex=' + str(StartIndex_BlackTagged_From_WhiteList) + '&Limit=' + str(QueryLimit_BlackTagged_From_WhiteList) + '&Fields=' + FieldsState_BlackTagged_From_WhiteList +
                        '&Recursive=' + Recursive_Blacktagged_From_WhiteList + '&SortBy=' + SortBy_BlackTagged_From_WhiteList + '&SortOrder=' + SortOrder_BlackTagged_From_WhiteList + '&EnableImages=' + EnableImages_Blacktagged_From_WhiteList +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_WhiteList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_WhiteList + '&api_key=' + auth_key)

                        #Send the API query for for blacktagged from whitelist media items
                        data_Blacktagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,QueriesRemaining_BlackTagged_From_WhiteList=api_query_handler(apiQuery_BlackTagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,APIDebugMsg_BlackTagged_From_WhiteList)
                    else: #((BlackTags_Tagged == '') or (LibraryID_WhtLst == ''))
                        data_Blacktagged_From_WhiteList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_BlackTagged_From_WhiteList=0
                        QueriesRemaining_BlackTagged_From_WhiteList=False
                        if (GLOBAL_DEBUG):
                            print_byType("\n\nNo blacktagged media items are whitelisted",False)

                    #Check if whitetag or blacklist are not an empty strings
                    if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                        #Built query for whitetagged from Blacklist media items
                        apiQuery_WhiteTagged_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Blacklist +
                        '&StartIndex=' + str(StartIndex_WhiteTagged_From_Blacklist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Blacklist) + '&Fields=' + FieldsState_WhiteTagged_From_Blacklist +
                        '&Recursive=' + Recursive_Whitetagged_From_Blacklist + '&SortBy=' + SortBy_WhiteTagged_From_Blacklist + '&SortOrder=' + SortOrder_WhiteTagged_From_Blacklist + '&EnableImages=' + EnableImages_Whitetagged_From_Blacklist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Blacklist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for whitetagged from Blacklist= media items
                        data_Whitetagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,QueriesRemaining_WhiteTagged_From_Blacklist=api_query_handler(apiQuery_WhiteTagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,APIDebugMsg_WhiteTagged_From_Blacklist)
                    else: #(WhiteTags_Tagged_From_Blacklist == '')
                        data_Whitetagged_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_WhiteTagged_From_Blacklist=0
                        QueriesRemaining_WhiteTagged_From_Blacklist=False
                        if (GLOBAL_DEBUG):
                            print_byType("\n\nNo whitetagged media items are blacklisted",False)

                    #Check if whitetag or whitelist are not an empty strings
                    if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                        #Built query for whitetagged_From_Whitelist= media items
                        apiQuery_WhiteTagged_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Whitelist +
                        '&StartIndex=' + str(StartIndex_WhiteTagged_From_Whitelist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Whitelist) + '&Fields=' + FieldsState_WhiteTagged_From_Whitelist +
                        '&Recursive=' + Recursive_Whitetagged_From_Whitelist + '&SortBy=' + SortBy_WhiteTagged_From_Whitelist + '&SortOrder=' + SortOrder_WhiteTagged_From_Whitelist + '&EnableImages=' + EnableImages_Whitetagged_From_Whitelist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Whitelist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Whitelist + '&api_key=' + auth_key)

                        #Send the API query for for whitetagged_From_Whitelist= media items
                        data_Whitetagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,QueriesRemaining_WhiteTagged_From_Whitelist=api_query_handler(apiQuery_WhiteTagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,APIDebugMsg_WhiteTagged_From_Whitelist)
                    else: #(WhiteTags_Tagged == '')
                        data_Whitetagged_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_WhiteTagged_From_Whitelist=0
                        QueriesRemaining_WhiteTagged_From_Whitelist=False
                        if (GLOBAL_DEBUG):
                            print_byType("\n\nNo whitetagged media items are whitelisted",False)

                    #Define reasoning for lookup
                    APIDebugMsg_Favorited_From_Blacklist_Child='favorited_From_Blacklist_from_blacklist_child'
                    data_Favorited_From_Blacklist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Blacklist,movie_played_count_comparison,movie_played_count,movie_created_played_count_comparison,movie_created_played_count,APIDebugMsg_Favorited_From_Blacklist_Child,movie_played_days,movie_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Favorited_From_Whitelist_Child='favorited_From_Whitelist_from_whitelist_child'
                    data_Favorited_From_Whitelist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Whitelist,movie_played_count_comparison,movie_played_count,movie_created_played_count_comparison,movie_created_played_count,APIDebugMsg_Favorited_From_Whitelist_Child,movie_played_days,movie_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_From_BlackList_Child='blacktag_child_from_blacklist_child'
                    data_Blacktagged_From_BlackList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_BlackList,blacktags,movie_played_count_comparison,movie_played_count,movie_created_played_count_comparison,movie_created_played_count,APIDebugMsg_Blacktag_From_BlackList_Child,movie_played_days,movie_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_From_WhiteList_Child='blacktag_child_from_whitelist_child'
                    data_Blacktagged_From_WhiteList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_WhiteList,blacktags,movie_played_count_comparison,movie_played_count,movie_created_played_count_comparison,movie_created_played_count,APIDebugMsg_Blacktag_From_WhiteList_Child,movie_played_days,movie_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_From_Blacklist_Child='whitetag_child_from_blacklist_child'
                    data_Whitetagged_From_Blacklist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Blacklist,whitetags,movie_played_count_comparison,movie_played_count,movie_created_played_count_comparison,movie_created_played_count,APIDebugMsg_Whitetag_From_Blacklist_Child,movie_played_days,movie_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_From_Whitelist_Child='whitetag_child_from_blacklist_child'
                    data_Whitetagged_From_Whitelist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Whitelist,whitetags,movie_played_count_comparison,movie_played_count,movie_created_played_count_comparison,movie_created_played_count,APIDebugMsg_Whitetag_From_Whitelist_Child,movie_played_days,movie_created_days)

                    #Combine dictionaries into list of dictionaries
                    #Order here is important
                    data_list=[data_Favorited_From_Whitelist, #0
                               data_Favorited_From_Whitelist_Children, #1
                               data_Whitetagged_From_Whitelist, #2
                               data_Whitetagged_From_Whitelist_Children, #3
                               data_Blacktagged_From_WhiteList, #4
                               data_Blacktagged_From_WhiteList_Children, #5
                               data_Favorited_From_Blacklist, #6
                               data_Favorited_From_Blacklist_Children, #7
                               data_Whitetagged_From_Blacklist, #8
                               data_Whitetagged_From_Blacklist_Children, #9
                               data_Blacktagged_From_BlackList, #10
                               data_Blacktagged_From_BlackList_Children, #11
                               data_Blacklist] #12

                    #Order here is important (must match above)
                    data_from_favorited_queries=[0,1,6,7]
                    data_from_whitetag_queries=[2,3,8,9]
                    data_from_blacktag_queries=[4,5,10,11]
                    data_from_whitelist_queries=[0,1,2,3,4,5]
                    #data_from_blacklist_queries=[6,7,8,9,10,11,12]

                    #Determine if we are done processing queries or if there are still queries to be sent
                    QueryItemsRemaining_All=(QueriesRemaining_Favorited_From_Blacklist |
                                             QueriesRemaining_Favorited_From_Whitelist |
                                             QueriesRemaining_WhiteTagged_From_Blacklist |
                                             QueriesRemaining_WhiteTagged_From_Whitelist |
                                             QueriesRemaining_BlackTagged_From_BlackList |
                                             QueriesRemaining_BlackTagged_From_WhiteList |
                                             QueriesRemaining_Blacklist)

                    #track where we are in the data_list
                    data_list_pos=0

                    #Determine if media item is to be deleted or kept
                    #Loop thru each dictionary in data_list[#]
                    for data in data_list:

                        #Loop thru each dictionary[item]
                        for item in data['Items']:

                            #Check if item was already processed for this user
                            if not (item['Id'] in user_processed_itemsId):

                                if (GLOBAL_DEBUG):
                                    #Double newline for DEBUG log formatting
                                    print_byType("\n\nInspecting Media Item: " + str(item['Id']),False)

                                media_found=True

                                itemIsMonitored=False
                                if (item['Type'] == 'Movie'):
                                    for mediasource in item['MediaSources']:
                                        itemIsMonitored=get_isItemMonitored(mediasource)

                                #find media item is ready to delete
                                if (itemIsMonitored):

                                    if (GLOBAL_DEBUG):
                                        print_byType("\nProcessing Movie Item: " + str(item['Id']),False)

                                    #establish played cutoff date for media item
                                    if ((movie_played_days >= 0) and ('UserData' in item) and ('LastPlayedDate' in item['UserData'])):
                                        if ((cut_off_date_played_movie) > (parse(item['UserData']['LastPlayedDate']))):
                                            item_matches_played_condition_day_filter=True
                                        else:
                                            item_matches_played_condition_day_filter=False
                                    else:
                                        item_matches_played_condition_day_filter=False

                                    #establish created cutoff date for media item
                                    if ((movie_created_days >= 0) and ('DateCreated' in item)):
                                        if (cut_off_date_created_movie > parse(item['DateCreated'])):
                                            item_matches_created_condition_day_filter=True
                                        else:
                                            item_matches_created_condition_day_filter=False
                                    else:
                                        item_matches_created_condition_day_filter=False

                                    itemisfav_MOVIE_Local=False
                                    #Get if media item is set as favorite
                                    if (data_list_pos in data_from_favorited_queries):
                                        itemisfav_MOVIE_Local=True
                                    elif ((keep_favorites_movie) and ('UserData' in item) and ('IsFavorite' in item['UserData']) and (item['UserData']['IsFavorite'])):
                                        itemisfav_MOVIE_Local=True

                                    itemisfav_MOVIE_Advanced=False
                                    if ((keep_favorites_movie) and (keep_favorites_advanced_movie_genre or keep_favorites_advanced_movie_library_genre)):
                                        itemisfav_MOVIE_Advanced=get_isMOVIE_AdvancedFav(item,user_key)

                                    itemisfav_MOVIE_Display=False
                                    if (itemisfav_MOVIE_Local or itemisfav_MOVIE_Advanced):
                                        itemisfav_MOVIE_Display=True

                                    #Store media item's favorite state when multiple users are monitored and we want to keep media items based on any user favoriting the media item
                                    if ((keep_favorites_movie == 2) and (itemisfav_MOVIE_Local or itemisfav_MOVIE_Advanced)):
                                        isfav_byUserId_Movie[user_key][item['Id']]=True

                                    itemIsWhiteTagged=False
                                    if (data_list_pos in data_from_whitetag_queries):
                                        itemIsWhiteTagged=True
                                        movie_whitetag_list.append(item['Id'])
                                    elif not (whitetags == ''):
                                        if (get_isMOVIE_Tagged(item,user_key,whitetags)):
                                            itemIsWhiteTagged=True
                                            movie_whitetag_list.append(item['Id'])

                                    itemIsBlackTagged=False
                                    if (data_list_pos in data_from_blacktag_queries):
                                        itemIsBlackTagged=True
                                        movie_blacktaglists.append(item['Id'])
                                    elif not (blacktags == ''):
                                        if (get_isMOVIE_Tagged(item,user_key,blacktags)):
                                            itemIsBlackTagged=True
                                            movie_blacktaglists.append(item['Id'])

                                    itemIsWhiteListed_Display=False
                                    #check if we are at a whitelist queried data_list_pos
                                    if (data_list_pos in data_from_whitelist_queries):
                                        itemIsWhiteListed_Local,itemIsWhiteListed_Remote=get_isItemWhitelisted(LibraryID_WhtLst,LibraryNetPath_WhtLst,LibraryPath_WhtLst,currentPosition,
                                                                                                               user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json)

                                        #Display True if media item is locally or remotely whitelisted
                                        itemIsWhiteListed_Display=(itemIsWhiteListed_Local or itemIsWhiteListed_Remote)

                                        #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                        if ((itemIsWhiteListed_Local) and (multiuser_whitelist_movie == 0)):
                                            movie_whitelists.append(item['Id'])
                                    else: #check if we are at a blacklist queried data_list_pos
                                        itemIsWhiteListed_Local,itemIsWhiteListed_Remote=get_isItemWhitelisted(LibraryID_BlkLst,LibraryNetPath_BlkLst,LibraryPath_BlkLst,currentPosition,
                                                                                                               user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json)
 
                                        #Display True if media item is locally or remotely whitelisted
                                        itemIsWhiteListed_Display=(itemIsWhiteListed_Local or itemIsWhiteListed_Remote)

                                        #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                        if ((itemIsWhiteListed_Local) and (multiuser_whitelist_movie == 0)):
                                            movie_whitelists.append(item['Id'])

                                    #Decide if media item meets the played count filter criteria
                                    if (('UserData' in item) and ('PlayCount' in item['UserData'])):
                                        item_matches_played_count_filter=get_playedStatus(item,'played',movie_played_count_comparison,movie_played_count)
                                    else:
                                        #itemPlayedStateIsDeletable=False
                                        item_matches_played_count_filter=False

                                    if ((multiuser_play_count_movie == 1) and (item_matches_played_count_filter)):
                                        isMeeting_PlayCountFilter_Movie[user_key][item['Id']]=True

                                    #Decide if media item meets the created count filter criteria
                                    if (('DateCreated' in item)):
                                        item_matches_created_played_count_filter=get_createdStatus(item,'created',movie_created_played_count_comparison,movie_created_played_count)
                                    else:
                                        #itemPlayedStateIsDeletable=False
                                        item_matches_created_played_count_filter=False

                                    #Decide how to handle the fav_local, fav_adv, whitetag, blacktag, whitelist_local, and whitelist_remote flags
                                    itemIsOKToDelete=get_deleteStatus(item_matches_played_count_filter,item_matches_played_condition_day_filter,item_matches_created_played_count_filter,item_matches_created_condition_day_filter,itemisfav_MOVIE_Local,itemisfav_MOVIE_Advanced,itemIsWhiteTagged,itemIsBlackTagged,itemIsWhiteListed_Local,itemIsWhiteListed_Remote)

                                    if ((delete_blacktagged_movie == 1) and itemIsBlackTagged and itemIsOKToDelete):
                                        isblacktag_and_watched_byUserId_Movie[user_key][item['Id']]=True

                                    if ('Played' in item['UserData']):

                                        try:
                                            #Fill in the blanks
                                            item=prepare_MOVIEoutput(item)

                                            item_output_details=(item['Type'] + ' - ' + item['Name'] + ' - ' + item['Studios'][0]['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) +
                                                        ' - Play Count: ' + str(item['UserData']['PlayCount']) + ' - ' + get_days_since_created(item['DateCreated']) + ' - Favorite: ' + str(itemisfav_MOVIE_Display) +
                                                        ' - WhiteTag: ' + str(itemIsWhiteTagged) + ' - BlackTag: ' + str(itemIsBlackTagged) + ' - Whitelisted: ' + str(itemIsWhiteListed_Display) + ' - ' +
                                                        item['Type'] + 'ID: ' + item['Id'])
                                        except (KeyError, IndexError):
                                            item_output_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                                            if (GLOBAL_DEBUG):
                                                print_byType('\nError encountered - Movie: \nitem: ' + str(item) + '\nitem' + str(item),False)

                                        if (itemIsOKToDelete):
                                            if (GLOBAL_DEBUG):
                                                print_movie_delete_info=True
                                                print_byType("\n\n",False)
                                            print_byType(':*[DELETE] - ' + item_output_details,print_movie_delete_info)
                                            deleteItems.append(item)
                                        else:
                                            if (GLOBAL_DEBUG):
                                                print_movie_delete_info=True
                                                print_byType("\n\n",False)
                                            print_byType(':[KEEPING] - ' + item_output_details,print_movie_keep_info)

                                        if (GLOBAL_DEBUG):
                                            #Spacing for debug file
                                            print_byType("\n",False)

                                #Add media item Id to tracking list so it is not processed more than once
                                user_processed_itemsId.add(item['Id'])

                        data_list_pos += 1

                currentSubPosition += 1

############# Episodes #############

        if ((episode_played_days >= 0) or (episode_created_days >= 0)):

            if (GLOBAL_DEBUG):
                print_byType("\n\nProcessing EPISODE Items For UserId: " + str(user_key),False)

            user_processed_itemsId=set()

            currentSubPosition=0

            for LibraryID_BlkLst,LibraryID_WhtLst,LibraryNetPath_BlkLst,LibraryNetPath_WhtLst,LibraryPath_BlkLst,LibraryPath_WhtLst in zip(user_bllib_keys_json_lensplit,user_wllib_keys_json_lensplit,user_bllib_netpath_json_lensplit,user_wllib_netpath_json_lensplit,user_bllib_path_json_lensplit,user_wllib_path_json_lensplit):

                #Initialize api_query_handler() variables for watched media items in blacklists
                StartIndex_Blacklist=0
                TotalItems_Blacklist=1
                QueryLimit_Blacklist=1
                QueriesRemaining_Blacklist=True
                APIDebugMsg_Blacklist='episode_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for watched media items in blacklists
                    IncludeItemTypes_Blacklist='Episode'
                    FieldsState_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                    SortBy_Blacklist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Blacklist='Ascending'
                    EnableUserData_Blacklist='True'
                    Recursive_Blacklist='True'
                    EnableImages_Blacklist='False'
                    CollapseBoxSetItems_Blacklist='False'
                    if(episode_played_days >= 0):
                        IsPlayed_Blacklist=get_isPlayed_FilterValue(episode_played_count_comparison,episode_played_count)
                    else:
                        IsPlayed_Blacklist='disable'
                    if(episode_created_days >= 0):
                        IsCreated_Blacklist=get_isCreated_FilterValue(episode_created_played_count_comparison,episode_created_played_count)
                    else:
                        IsCreated_Blacklist='disable'
                    IsPlayedState_Blacklist=get_isPlayedCreated_FilterValue(IsPlayed_Blacklist,IsCreated_Blacklist)

                #Initialize api_query_handler() variables for Favorited from Blacklist media items
                StartIndex_Favorited_From_Blacklist=0
                TotalItems_Favorited_From_Blacklist=1
                QueryLimit_Favorited_From_Blacklist=1
                QueriesRemaining_Favorited_From_Blacklist=True
                APIDebugMsg_Favorited_From_Blacklist='episode_Favorited_From_Blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for Favorited_From_Blacklist media items
                    IncludeItemTypes_Favorited_From_Blacklist='Episode,Season,Series,CollectionFolder'
                    FieldsState_Favorited_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                    SortBy_Favorited_From_Blacklist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Favorited_From_Blacklist='Ascending'
                    EnableUserData_Favorited_From_Blacklist='True'
                    Recursive_Favorited_From_Blacklist='True'
                    EnableImages_Favorited_From_Blacklist='False'
                    CollapseBoxSetItems_Favorited_From_Blacklist='False'
                    IsFavorite_From_Blacklist='True'

                #Initialize api_query_handler() variables for Favorited from Whitelist media items
                StartIndex_Favorited_From_Whitelist=0
                TotalItems_Favorited_From_Whitelist=1
                QueryLimit_Favorited_From_Whitelist=1
                QueriesRemaining_Favorited_From_Whitelist=True
                APIDebugMsg_Favorited_From_Whitelist='episode_Favorited_From_Whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for Favorited_From_Whitelist media items
                    IncludeItemTypes_Favorited_From_Whitelist='Episode,Season,Series,CollectionFolder'
                    FieldsState_Favorited_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                    SortBy_Favorited_From_Whitelist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Favorited_From_Whitelist='Ascending'
                    EnableUserData_Favorited_From_Whitelist='True'
                    Recursive_Favorited_From_Whitelist='True'
                    EnableImages_Favorited_From_Whitelist='False'
                    CollapseBoxSetItems_Favorited_From_Whitelist='False'
                    IsFavorite_From_Whitelist='True'

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged_From_BlackList=0
                TotalItems_BlackTagged_From_BlackList=1
                QueryLimit_BlackTagged_From_BlackList=1
                QueriesRemaining_BlackTagged_From_BlackList=True
                APIDebugMsg_BlackTagged_From_BlackList='episode_blacktagged_from_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for blacktagged media items from blacklist
                    IncludeItemTypes_BlackTagged_From_BlackList='Episode,Season,Series,CollectionFolder'
                    FieldsState_BlackTagged_From_BlackList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                    SortBy_BlackTagged_From_BlackList='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_BlackTagged_From_BlackList='Ascending'
                    EnableUserData_Blacktagged_From_BlackList='True'
                    Recursive_Blacktagged_From_BlackList='True'
                    EnableImages_Blacktagged_From_BlackList='False'
                    CollapseBoxSetItems_Blacktagged_From_BlackList='False'
                    #Encode blacktags so they are url acceptable
                    BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged_From_WhiteList=0
                TotalItems_BlackTagged_From_WhiteList=1
                QueryLimit_BlackTagged_From_WhiteList=1
                QueriesRemaining_BlackTagged_From_WhiteList=True
                APIDebugMsg_BlackTagged_From_WhiteList='episode_blacktagged_from_whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for blacktagged media items from whitelist
                    IncludeItemTypes_BlackTagged_From_WhiteList='Episode,Season,Series,CollectionFolder'
                    FieldsState_BlackTagged_From_WhiteList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                    SortBy_BlackTagged_From_WhiteList='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_BlackTagged_From_WhiteList='Ascending'
                    EnableUserData_Blacktagged_From_WhiteList='True'
                    Recursive_Blacktagged_From_WhiteList='True'
                    EnableImages_Blacktagged_From_WhiteList='False'
                    CollapseBoxSetItems_Blacktagged_From_WhiteList='False'
                    #Encode blacktags so they are url acceptable
                    BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged_From_Blacklist=0
                TotalItems_WhiteTagged_From_Blacklist=1
                QueryLimit_WhiteTagged_From_Blacklist=1
                QueriesRemaining_WhiteTagged_From_Blacklist=True
                APIDebugMsg_WhiteTagged_From_Blacklist='episode_whitetagged_from_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for whitetagged media items
                    IncludeItemTypes_WhiteTagged_From_Blacklist='Episode,Season,Series,CollectionFolder'
                    FieldsState_WhiteTagged_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                    SortBy_WhiteTagged_From_Blacklist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_WhiteTagged_From_Blacklist='Ascending'
                    EnableUserData_Whitetagged_From_Blacklist='True'
                    Recursive_Whitetagged_From_Blacklist='True'
                    EnableImages_Whitetagged_From_Blacklist='False'
                    CollapseBoxSetItems_Whitetagged_From_Blacklist='False'
                    #Encode whitetags so they are url acceptable
                    WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged_From_Whitelist=0
                TotalItems_WhiteTagged_From_Whitelist=1
                QueryLimit_WhiteTagged_From_Whitelist=1
                QueriesRemaining_WhiteTagged_From_Whitelist=True
                APIDebugMsg_WhiteTagged_From_Whitelist='episode_whitetagged_from_whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for whitetagged media items
                    IncludeItemTypes_WhiteTagged_From_Whitelist='Episode,Season,Series,CollectionFolder'
                    FieldsState_WhiteTagged_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                    SortBy_WhiteTagged_From_Whitelist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_WhiteTagged_From_Whitelist='Ascending'
                    EnableUserData_Whitetagged_From_Whitelist='True'
                    Recursive_Whitetagged_From_Whitelist='True'
                    EnableImages_Whitetagged_From_Whitelist='False'
                    CollapseBoxSetItems_Whitetagged_From_Whitelist='False'
                    #Encode whitetags so they are url acceptable
                    WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                QueryItemsRemaining_All=True

                while (QueryItemsRemaining_All):

                    if not (LibraryID_BlkLst == ''):
                        #Built query for watched items in blacklists
                        apiQuery_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Blacklist +
                        '&StartIndex=' + str(StartIndex_Blacklist) + '&Limit=' + str(QueryLimit_Blacklist) + '&IsPlayed=' + IsPlayedState_Blacklist +
                        '&Fields=' + FieldsState_Blacklist + '&Recursive=' + Recursive_Blacklist + '&SortBy=' + SortBy_Blacklist + '&SortOrder=' + SortOrder_Blacklist +
                        '&EnableImages=' + EnableImages_Blacklist + '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacklist + '&EnableUserData=' + EnableUserData_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        data_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,QueriesRemaining_Blacklist=api_query_handler(apiQuery_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,APIDebugMsg_Blacklist)
                    else:
                        #When no media items are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Blacklist=0
                        QueriesRemaining_Blacklist=False

                    if not (LibraryID_BlkLst == ''):
                        #Built query for Favorited from Blacklist media items
                        apiQuery_Favorited_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Blacklist +
                        '&StartIndex=' + str(StartIndex_Favorited_From_Blacklist) + '&Limit=' + str(QueryLimit_Favorited_From_Blacklist) + '&Fields=' + FieldsState_Favorited_From_Blacklist +
                        '&Recursive=' + Recursive_Favorited_From_Blacklist + '&SortBy=' + SortBy_Favorited_From_Blacklist + '&SortOrder=' + SortOrder_Favorited_From_Blacklist + '&EnableImages=' + EnableImages_Favorited_From_Blacklist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Blacklist + '&IsFavorite=' + IsFavorite_From_Blacklist + '&EnableUserData=' + EnableUserData_Favorited_From_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for Favorited from Blacklist media items
                        data_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,QueriesRemaining_Favorited_From_Blacklist=api_query_handler(apiQuery_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,APIDebugMsg_Favorited_From_Blacklist)
                    else:
                        #When no media items are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Favorited_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Favorited_From_Blacklist=0
                        QueriesRemaining_Favorited_From_Blacklist=False

                    if not (LibraryID_WhtLst == ''):
                        #Built query for Favorited From Whitelist media items
                        apiQuery_Favorited_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Whitelist +
                        '&StartIndex=' + str(StartIndex_Favorited_From_Whitelist) + '&Limit=' + str(QueryLimit_Favorited_From_Whitelist) + '&Fields=' + FieldsState_Favorited_From_Whitelist +
                        '&Recursive=' + Recursive_Favorited_From_Whitelist + '&SortBy=' + SortBy_Favorited_From_Whitelist + '&SortOrder=' + SortOrder_Favorited_From_Whitelist + '&EnableImages=' + EnableImages_Favorited_From_Whitelist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Whitelist + '&IsFavorite=' + IsFavorite_From_Whitelist + '&EnableUserData=' + EnableUserData_Favorited_From_Whitelist + '&api_key=' + auth_key)

                        #Send the API query for for Favorited from Whitelist media items
                        data_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,QueriesRemaining_Favorited_From_Whitelist=api_query_handler(apiQuery_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,APIDebugMsg_Favorited_From_Whitelist)
                    else:
                        #When no media items are whitelisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
                        data_Favorited_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Favorited_From_Whitelist=0
                        QueriesRemaining_Favorited_From_Whitelist=False

                    #Check if blacktag or blacklist are not an empty strings
                    if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                        #Built query for blacktagged from blacklist media items
                        apiQuery_BlackTagged_From_BlackList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_BlackList +
                        '&StartIndex=' + str(StartIndex_BlackTagged_From_BlackList) + '&Limit=' + str(QueryLimit_BlackTagged_From_BlackList) + '&Fields=' + FieldsState_BlackTagged_From_BlackList +
                        '&Recursive=' + Recursive_Blacktagged_From_BlackList + '&SortBy=' + SortBy_BlackTagged_From_BlackList + '&SortOrder=' + SortOrder_BlackTagged_From_BlackList + '&EnableImages=' + EnableImages_Blacktagged_From_BlackList +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_BlackList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_BlackList + '&api_key=' + auth_key)

                        #Send the API query for for blacktagged from blacklist media items
                        data_Blacktagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,QueriesRemaining_BlackTagged_From_BlackList=api_query_handler(apiQuery_BlackTagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,APIDebugMsg_BlackTagged_From_BlackList)
                    else: #((BlackTags_Tagged == '') or (LibraryID_BlkLst == ''))
                        data_Blacktagged_From_BlackList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_BlackTagged_From_BlackList=0
                        QueriesRemaining_BlackTagged_From_BlackList=False

                    #Check if blacktag or whitelist are not an empty strings
                    if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                        #Built query for blacktagged from whitelist media items
                        apiQuery_BlackTagged_From_WhiteList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_WhiteList +
                        '&StartIndex=' + str(StartIndex_BlackTagged_From_WhiteList) + '&Limit=' + str(QueryLimit_BlackTagged_From_WhiteList) + '&Fields=' + FieldsState_BlackTagged_From_WhiteList +
                        '&Recursive=' + Recursive_Blacktagged_From_WhiteList + '&SortBy=' + SortBy_BlackTagged_From_WhiteList + '&SortOrder=' + SortOrder_BlackTagged_From_WhiteList + '&EnableImages=' + EnableImages_Blacktagged_From_WhiteList +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_WhiteList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_WhiteList + '&api_key=' + auth_key)

                        #Send the API query for for blacktagged from whitelist media items
                        data_Blacktagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,QueriesRemaining_BlackTagged_From_WhiteList=api_query_handler(apiQuery_BlackTagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,APIDebugMsg_BlackTagged_From_WhiteList)
                    else: #((BlackTags_Tagged == '') or (LibraryID_WhtLst == ''))
                        data_Blacktagged_From_WhiteList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_BlackTagged_From_WhiteList=0
                        QueriesRemaining_BlackTagged_From_WhiteList=False

                    #Check if whitetag or blacklist are not an empty strings
                    if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                        #Built query for whitetagged from Blacklist media items
                        apiQuery_WhiteTagged_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Blacklist +
                        '&StartIndex=' + str(StartIndex_WhiteTagged_From_Blacklist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Blacklist) + '&Fields=' + FieldsState_WhiteTagged_From_Blacklist +
                        '&Recursive=' + Recursive_Whitetagged_From_Blacklist + '&SortBy=' + SortBy_WhiteTagged_From_Blacklist + '&SortOrder=' + SortOrder_WhiteTagged_From_Blacklist + '&EnableImages=' + EnableImages_Whitetagged_From_Blacklist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Blacklist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for whitetagged from Blacklist= media items
                        data_Whitetagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,QueriesRemaining_WhiteTagged_From_Blacklist=api_query_handler(apiQuery_WhiteTagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,APIDebugMsg_WhiteTagged_From_Blacklist)
                    else: #(WhiteTags_Tagged_From_Blacklist == '')
                        data_Whitetagged_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_WhiteTagged_From_Blacklist=0
                        QueriesRemaining_WhiteTagged_From_Blacklist=False

                    #Check if whitetag or whitelist are not an empty strings
                    if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                        #Built query for whitetagged_From_Whitelist= media items
                        apiQuery_WhiteTagged_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Whitelist +
                        '&StartIndex=' + str(StartIndex_WhiteTagged_From_Whitelist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Whitelist) + '&Fields=' + FieldsState_WhiteTagged_From_Whitelist +
                        '&Recursive=' + Recursive_Whitetagged_From_Whitelist + '&SortBy=' + SortBy_WhiteTagged_From_Whitelist + '&SortOrder=' + SortOrder_WhiteTagged_From_Whitelist + '&EnableImages=' + EnableImages_Whitetagged_From_Whitelist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Whitelist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Whitelist + '&api_key=' + auth_key)

                        #Send the API query for for whitetagged_From_Whitelist= media items
                        data_Whitetagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,QueriesRemaining_WhiteTagged_From_Whitelist=api_query_handler(apiQuery_WhiteTagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,APIDebugMsg_WhiteTagged_From_Whitelist)
                    else: #(WhiteTags_Tagged == '')
                        data_Whitetagged_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_WhiteTagged_From_Whitelist=0
                        QueriesRemaining_WhiteTagged_From_Whitelist=False

                    #Define reasoning for lookup
                    APIDebugMsg_Favorited_From_Blacklist_Child='favorited_From_Blacklist_from_blacklist_child'
                    data_Favorited_From_Blacklist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Blacklist,episode_played_count_comparison,episode_played_count,episode_created_played_count_comparison,episode_created_played_count,APIDebugMsg_Favorited_From_Blacklist_Child,episode_played_days,episode_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Favorited_From_Whitelist_Child='favorited_From_Whitelist_from_whitelist_child'
                    data_Favorited_From_Whitelist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Whitelist,episode_played_count_comparison,episode_played_count,episode_created_played_count_comparison,episode_created_played_count,APIDebugMsg_Favorited_From_Whitelist_Child,episode_played_days,episode_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_From_BlackList_Child='blacktag_child_from_blacklist_child'
                    data_Blacktagged_From_BlackList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_BlackList,blacktags,episode_played_count_comparison,episode_played_count,episode_created_played_count_comparison,episode_created_played_count,APIDebugMsg_Blacktag_From_BlackList_Child,episode_played_days,episode_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_From_WhiteList_Child='blacktag_child_from_whitelist_child'
                    data_Blacktagged_From_WhiteList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_WhiteList,blacktags,episode_played_count_comparison,episode_played_count,episode_created_played_count_comparison,episode_created_played_count,APIDebugMsg_Blacktag_From_WhiteList_Child,episode_played_days,episode_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_From_Blacklist_Child='whitetag_child_from_blacklist_child'
                    data_Whitetagged_From_Blacklist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Blacklist,whitetags,episode_played_count_comparison,episode_played_count,episode_created_played_count_comparison,episode_created_played_count,APIDebugMsg_Whitetag_From_Blacklist_Child,episode_played_days,episode_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_From_Whitelist_Child='whitetag_child_from_blacklist_child'
                    data_Whitetagged_From_Whitelist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Whitelist,whitetags,episode_played_count_comparison,episode_played_count,episode_created_played_count_comparison,episode_created_played_count,APIDebugMsg_Whitetag_From_Whitelist_Child,episode_played_days,episode_created_days)

                    #Combine dictionaries into list of dictionaries
                    #Order here is important
                    data_list=[data_Favorited_From_Whitelist, #0
                               data_Favorited_From_Whitelist_Children, #1
                               data_Whitetagged_From_Whitelist, #2
                               data_Whitetagged_From_Whitelist_Children, #3
                               data_Blacktagged_From_WhiteList, #4
                               data_Blacktagged_From_WhiteList_Children, #5
                               data_Favorited_From_Blacklist, #6
                               data_Favorited_From_Blacklist_Children, #7
                               data_Whitetagged_From_Blacklist, #8
                               data_Whitetagged_From_Blacklist_Children, #9
                               data_Blacktagged_From_BlackList, #10
                               data_Blacktagged_From_BlackList_Children, #11
                               data_Blacklist] #12

                    #Order here is important (must match above)
                    data_from_favorited_queries=[0,1,6,7]
                    data_from_whitetag_queries=[2,3,8,9]
                    data_from_blacktag_queries=[4,5,10,11]
                    data_from_whitelist_queries=[0,1,2,3,4,5]
                    #data_from_blacklist_queries=[6,7,8,9,10,11,12]

                    #Determine if we are done processing queries or if there are still queries to be sent
                    QueryItemsRemaining_All=(QueriesRemaining_Favorited_From_Blacklist |
                                             QueriesRemaining_Favorited_From_Whitelist |
                                             QueriesRemaining_WhiteTagged_From_Blacklist |
                                             QueriesRemaining_WhiteTagged_From_Whitelist |
                                             QueriesRemaining_BlackTagged_From_BlackList |
                                             QueriesRemaining_BlackTagged_From_WhiteList |
                                             QueriesRemaining_Blacklist)

                    #track where we are in the data_list
                    data_list_pos=0

                    #Determine if media item is to be deleted or kept
                    #Loop thru each dictionary in data_list[#]
                    for data in data_list:

                        #Loop thru each dictionary[item]
                        for item in data['Items']:

                            #Check if item was already processed for this user
                            if not (item['Id'] in user_processed_itemsId):

                                if (GLOBAL_DEBUG):
                                    #Double newline for DEBUG log formatting
                                    print_byType("\n\nInspecting Media Item: " + str(item['Id']),False)

                                media_found=True

                                itemIsMonitored=False
                                if (item['Type'] == 'Episode'):
                                    for mediasource in item['MediaSources']:
                                        itemIsMonitored=get_isItemMonitored(mediasource)

                                #find media item is ready to delete
                                if (itemIsMonitored):

                                    if (GLOBAL_DEBUG):
                                        print_byType("\nProcessing Episode Item: " + str(item['Id']),False)

                                    #establish played cutoff date for media item
                                    if ((episode_played_days >= 0) and ('UserData' in item) and ('LastPlayedDate' in item['UserData'])):
                                        if ((cut_off_date_played_episode) > (parse(item['UserData']['LastPlayedDate']))):
                                            item_matches_played_condition_day_filter=True
                                        else:
                                            item_matches_played_condition_day_filter=False
                                    else:
                                        item_matches_played_condition_day_filter=False

                                    #establish created cutoff date for media item
                                    if ((episode_created_days >= 0) and ('DateCreated' in item)):
                                        if (cut_off_date_created_episode > parse(item['DateCreated'])):
                                            item_matches_created_condition_day_filter=True
                                        else:
                                            item_matches_created_condition_day_filter=False
                                    else:
                                        item_matches_created_condition_day_filter=False

                                    itemisfav_EPISODE_Local=False
                                    #Get if media item is set as favorite
                                    if (data_list_pos in data_from_favorited_queries):
                                        itemisfav_EPISODE_Local=True
                                    elif ((keep_favorites_episode) and ('UserData'in item) and ('IsFavorite' in item['UserData']) and (item['UserData']['IsFavorite'])):
                                        itemisfav_EPISODE_Local=True

                                    itemisfav_EPISODE_Advanced=False
                                    if ((keep_favorites_episode) and (keep_favorites_advanced_episode_genre or keep_favorites_advanced_season_genre or
                                       keep_favorites_advanced_series_genre or keep_favorites_advanced_tv_library_genre or
                                       keep_favorites_advanced_tv_studio_network or keep_favorites_advanced_tv_studio_network_genre)):
                                        itemisfav_EPISODE_Advanced=get_isEPISODE_AdvancedFav(item,user_key)

                                    itemisfav_EPISODE_Display=False
                                    if (itemisfav_EPISODE_Local or itemisfav_EPISODE_Advanced):
                                        itemisfav_EPISODE_Display=True

                                    #Store media item's favorite state when multiple users are monitored and we want to keep media items based on any user favoriting the media item
                                    if ((keep_favorites_episode == 2) and (itemisfav_EPISODE_Local or itemisfav_EPISODE_Advanced)):
                                        isfav_byUserId_Episode[user_key][item['Id']]=True

                                    itemIsWhiteTagged=False
                                    if (data_list_pos in data_from_whitetag_queries):
                                        itemIsWhiteTagged=True
                                        episode_whitetag_list.append(item['Id'])
                                    elif not (whitetags == ''):
                                        if (get_isEPISODE_Tagged(item,user_key,whitetags)):
                                            itemIsWhiteTagged=True
                                            episode_whitetag_list.append(item['Id'])

                                    itemIsBlackTagged=False
                                    if (data_list_pos in data_from_blacktag_queries):
                                        itemIsBlackTagged=True
                                        episode_blacktaglists.append(item['Id'])
                                    elif not (blacktags == ''):
                                        if (get_isEPISODE_Tagged(item,user_key,blacktags)):
                                            itemIsBlackTagged=True
                                            episode_blacktaglists.append(item['Id'])

                                    itemIsWhiteListed_Display=False
                                    #check if we are at a whitelist queried data_list_pos
                                    if (data_list_pos in data_from_whitelist_queries):
                                        itemIsWhiteListed_Local,itemIsWhiteListed_Remote=get_isItemWhitelisted(LibraryID_WhtLst,LibraryNetPath_WhtLst,LibraryPath_WhtLst,currentPosition,
                                                                                                               user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json)

                                        #Display True if media item is locally or remotely whitelisted
                                        itemIsWhiteListed_Display=(itemIsWhiteListed_Local or itemIsWhiteListed_Remote)

                                        #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                        if ((itemIsWhiteListed_Local) and (multiuser_whitelist_episode == 0)):
                                            episode_whitelists.append(item['Id'])
                                    else: #check if we are at a blacklist queried data_list_pos
                                        itemIsWhiteListed_Local,itemIsWhiteListed_Remote=get_isItemWhitelisted(LibraryID_BlkLst,LibraryNetPath_BlkLst,LibraryPath_BlkLst,currentPosition,
                                                                                                               user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json)

                                        #Display True if media item is locally or remotely whitelisted
                                        itemIsWhiteListed_Display=(itemIsWhiteListed_Local or itemIsWhiteListed_Remote)

                                        #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                        if ((itemIsWhiteListed_Local) and (multiuser_whitelist_episode == 0)):
                                            episode_whitelists.append(item['Id'])

                                    #Decide if media item meets the played count filter criteria
                                    if (('UserData' in item) and ('PlayCount' in item['UserData'])):
                                        item_matches_played_count_filter=get_playedStatus(item,'played',episode_played_count_comparison,episode_played_count)
                                    else:
                                        #itemPlayedStateIsDeletable=False
                                        item_matches_played_count_filter=False

                                    if ((multiuser_play_count_episode == 1) and (item_matches_played_count_filter)):
                                        isMeeting_PlayCountFilter_Episode[user_key][item['Id']]=True

                                    #Decide if media item meets the created count filter criteria
                                    if (('DateCreated' in item)):
                                        item_matches_created_played_count_filter=get_createdStatus(item,'created',episode_created_played_count_comparison,episode_created_played_count)
                                    else:
                                        #itemPlayedStateIsDeletable=False
                                        item_matches_created_played_count_filter=False

                                    #Decide how to handle the fav_local, fav_adv, whitetag, blacktag, whitelist_local, and whitelist_remote flags
                                    itemIsOKToDelete=get_deleteStatus(item_matches_played_count_filter,item_matches_played_condition_day_filter,item_matches_created_played_count_filter,item_matches_created_condition_day_filter,itemisfav_EPISODE_Local,itemisfav_EPISODE_Advanced,itemIsWhiteTagged,itemIsBlackTagged,itemIsWhiteListed_Local,itemIsWhiteListed_Remote)

                                    if ((delete_blacktagged_episode == 1) and itemIsBlackTagged and itemIsOKToDelete):
                                        isblacktag_and_watched_byUserId_Episode[user_key][item['Id']]=True

                                    if (minimum_number_episodes or minimum_number_played_episodes):
                                        #Get seriesId and compare it to what the episode thinks its seriesId is
                                        series_info = get_SERIES_itemInfo(item,user_key)
                                        if ((not ('SeriesId' in item)) or (not (item['SeriesId'] == series_info['Id']))):
                                            if (series_info):
                                                item['SeriesId']=series_info['Id']

                                        if not (item['SeriesId'] in episodeCounts_byUserId[user_key]):
                                            RecursiveItemCount=int(series_info['RecursiveItemCount'])
                                            UnplayedItemCount=int(series_info['UserData']['UnplayedItemCount'])
                                            PlayedEpisodeCount=RecursiveItemCount - UnplayedItemCount

                                        if not ('TotalEpisodeCount' in episodeCounts_byUserId[user_key][item['SeriesId']]):
                                            episodeCounts_byUserId[user_key][item['SeriesId']]['TotalEpisodeCount']=RecursiveItemCount
                                        if not ('UnplayedEpisodeCount' in episodeCounts_byUserId[user_key][item['SeriesId']]):
                                            episodeCounts_byUserId[user_key][item['SeriesId']]['UnplayedEpisodeCount']=UnplayedItemCount
                                        if not ('PlayedEpisodeCount' in episodeCounts_byUserId[user_key][item['SeriesId']]):
                                            episodeCounts_byUserId[user_key][item['SeriesId']]['PlayedEpisodeCount']=PlayedEpisodeCount

                                    if ('Played' in item['UserData']):

                                        try:
                                            #Fill in the blanks
                                            item=prepare_EPISODEoutput(item)

                                            item_output_details=(item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'],item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['SeriesStudio'] +
                                                        ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - Play Count: ' + str(item['UserData']['PlayCount']) + ' - ' + get_days_since_created(item['DateCreated']) +
                                                        ' - Favorite: ' + str(itemisfav_EPISODE_Display) + ' - WhiteTag: ' + str(itemIsWhiteTagged) + ' - BlackTag: ' + str(itemIsBlackTagged) + ' - Whitelisted: ' + str(itemIsWhiteListed_Display) +
                                                        ' - ' + item['Type'] + 'ID: ' + item['Id'])
                                        except (KeyError, IndexError):
                                            item_output_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                                            if (GLOBAL_DEBUG):
                                                print_byType('\nError encountered - Episode: \nitem: ' + str(item) + '\nitem' + str(item),False)

                                        if (itemIsOKToDelete):
                                            if (GLOBAL_DEBUG):
                                                print_episode_delete_info=True
                                                print_byType("\n\n",False)
                                            print_byType(':*[DELETE] - ' + item_output_details,print_episode_delete_info)
                                            deleteItems.append(item)
                                        else:
                                            if (GLOBAL_DEBUG):
                                                print_episode_delete_info=True
                                                print_byType("\n\n",False)
                                            print_byType(':[KEEPING] - ' + item_output_details,print_episode_keep_info)

                                        if (GLOBAL_DEBUG):
                                            #Spacing for debug file
                                            print_byType("\n",False)

                                #Add media item Id to tracking list so it is not processed more than once
                                user_processed_itemsId.add(item['Id'])

                        data_list_pos += 1

                currentSubPosition += 1

############# Audio #############

        if ((audio_played_days >= 0) or (audio_created_days >= 0)):

            if (GLOBAL_DEBUG):
                print_byType("\n\nProcessing AUDIO Items For UserId: " + str(user_key),False)

            user_processed_itemsId=set()

            currentSubPosition=0

            for LibraryID_BlkLst,LibraryID_WhtLst,LibraryNetPath_BlkLst,LibraryNetPath_WhtLst,LibraryPath_BlkLst,LibraryPath_WhtLst in zip(user_bllib_keys_json_lensplit,user_wllib_keys_json_lensplit,user_bllib_netpath_json_lensplit,user_wllib_netpath_json_lensplit,user_bllib_path_json_lensplit,user_wllib_path_json_lensplit):

                #Initialize api_query_handler() variables for watched media items in blacklists
                StartIndex_Blacklist=0
                TotalItems_Blacklist=1
                QueryLimit_Blacklist=1
                QueriesRemaining_Blacklist=True
                APIDebugMsg_Blacklist='audio_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for watched media items in blacklists
                    IncludeItemTypes_Blacklist='Audio'
                    FieldsState_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_Blacklist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Blacklist='Ascending'
                    EnableUserData_Blacklist='True'
                    Recursive_Blacklist='True'
                    EnableImages_Blacklist='False'
                    CollapseBoxSetItems_Blacklist='False'
                    if(audio_played_days >= 0):
                        IsPlayed_Blacklist=get_isPlayed_FilterValue(audio_played_count_comparison,audio_played_count)
                    else:
                        IsPlayed_Blacklist='disable'
                    if(audio_created_days >= 0):
                        IsCreated_Blacklist=get_isCreated_FilterValue(audio_created_played_count_comparison,audio_created_played_count)
                    else:
                        IsCreated_Blacklist='disable'
                    IsPlayedState_Blacklist=get_isPlayedCreated_FilterValue(IsPlayed_Blacklist,IsCreated_Blacklist)

                #Initialize api_query_handler() variables for Favorited from Blacklist media items
                StartIndex_Favorited_From_Blacklist=0
                TotalItems_Favorited_From_Blacklist=1
                QueryLimit_Favorited_From_Blacklist=1
                QueriesRemaining_Favorited_From_Blacklist=True
                APIDebugMsg_Favorited_From_Blacklist='audio_Favorited_From_Blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for Favorited_From_Blacklist media items
                    IncludeItemTypes_Favorited_From_Blacklist='Audio,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_Favorited_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_Favorited_From_Blacklist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Favorited_From_Blacklist='Ascending'
                    EnableUserData_Favorited_From_Blacklist='True'
                    Recursive_Favorited_From_Blacklist='True'
                    EnableImages_Favorited_From_Blacklist='False'
                    CollapseBoxSetItems_Favorited_From_Blacklist='False'
                    IsFavorite_From_Blacklist='True'

                #Initialize api_query_handler() variables for Favorited from Whitelist media items
                StartIndex_Favorited_From_Whitelist=0
                TotalItems_Favorited_From_Whitelist=1
                QueryLimit_Favorited_From_Whitelist=1
                QueriesRemaining_Favorited_From_Whitelist=True
                APIDebugMsg_Favorited_From_Whitelist='audio_Favorited_From_Whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for Favorited_From_Whitelist media items
                    IncludeItemTypes_Favorited_From_Whitelist='Audio,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_Favorited_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_Favorited_From_Whitelist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Favorited_From_Whitelist='Ascending'
                    EnableUserData_Favorited_From_Whitelist='True'
                    Recursive_Favorited_From_Whitelist='True'
                    EnableImages_Favorited_From_Whitelist='False'
                    CollapseBoxSetItems_Favorited_From_Whitelist='False'
                    IsFavorite_From_Whitelist='True'

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged_From_BlackList=0
                TotalItems_BlackTagged_From_BlackList=1
                QueryLimit_BlackTagged_From_BlackList=1
                QueriesRemaining_BlackTagged_From_BlackList=True
                APIDebugMsg_BlackTagged_From_BlackList='audio_blacktagged_from_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for blacktagged media items from blacklist
                    IncludeItemTypes_BlackTagged_From_BlackList='Audio,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_BlackTagged_From_BlackList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_BlackTagged_From_BlackList='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_BlackTagged_From_BlackList='Ascending'
                    EnableUserData_Blacktagged_From_BlackList='True'
                    Recursive_Blacktagged_From_BlackList='True'
                    EnableImages_Blacktagged_From_BlackList='False'
                    CollapseBoxSetItems_Blacktagged_From_BlackList='False'
                    #Encode blacktags so they are url acceptable
                    BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged_From_WhiteList=0
                TotalItems_BlackTagged_From_WhiteList=1
                QueryLimit_BlackTagged_From_WhiteList=1
                QueriesRemaining_BlackTagged_From_WhiteList=True
                APIDebugMsg_BlackTagged_From_WhiteList='audio_blacktagged_from_whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for blacktagged media items from whitelist
                    IncludeItemTypes_BlackTagged_From_WhiteList='Audio,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_BlackTagged_From_WhiteList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_BlackTagged_From_WhiteList='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_BlackTagged_From_WhiteList='Ascending'
                    EnableUserData_Blacktagged_From_WhiteList='True'
                    Recursive_Blacktagged_From_WhiteList='True'
                    EnableImages_Blacktagged_From_WhiteList='False'
                    CollapseBoxSetItems_Blacktagged_From_WhiteList='False'
                    #Encode blacktags so they are url acceptable
                    BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged_From_Blacklist=0
                TotalItems_WhiteTagged_From_Blacklist=1
                QueryLimit_WhiteTagged_From_Blacklist=1
                QueriesRemaining_WhiteTagged_From_Blacklist=True
                APIDebugMsg_WhiteTagged_From_Blacklist='audio_whitetagged_from_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for whitetagged media items
                    IncludeItemTypes_WhiteTagged_From_Blacklist='Audio,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_WhiteTagged_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_WhiteTagged_From_Blacklist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_WhiteTagged_From_Blacklist='Ascending'
                    EnableUserData_Whitetagged_From_Blacklist='True'
                    Recursive_Whitetagged_From_Blacklist='True'
                    EnableImages_Whitetagged_From_Blacklist='False'
                    CollapseBoxSetItems_Whitetagged_From_Blacklist='False'
                    #Encode whitetags so they are url acceptable
                    WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged_From_Whitelist=0
                TotalItems_WhiteTagged_From_Whitelist=1
                QueryLimit_WhiteTagged_From_Whitelist=1
                QueriesRemaining_WhiteTagged_From_Whitelist=True
                APIDebugMsg_WhiteTagged_From_Whitelist='audio_whitetagged_from_whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for whitetagged media items
                    IncludeItemTypes_WhiteTagged_From_Whitelist='Audio,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_WhiteTagged_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_WhiteTagged_From_Whitelist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_WhiteTagged_From_Whitelist='Ascending'
                    EnableUserData_Whitetagged_From_Whitelist='True'
                    Recursive_Whitetagged_From_Whitelist='True'
                    EnableImages_Whitetagged_From_Whitelist='False'
                    CollapseBoxSetItems_Whitetagged_From_Whitelist='False'
                    #Encode whitetags so they are url acceptable
                    WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                QueryItemsRemaining_All=True

                while (QueryItemsRemaining_All):

                    if not (LibraryID_BlkLst == ''):
                        #Built query for watched items in blacklists
                        apiQuery_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Blacklist +
                        '&StartIndex=' + str(StartIndex_Blacklist) + '&Limit=' + str(QueryLimit_Blacklist) + '&IsPlayed=' + IsPlayedState_Blacklist +
                        '&Fields=' + FieldsState_Blacklist + '&Recursive=' + Recursive_Blacklist + '&SortBy=' + SortBy_Blacklist + '&SortOrder=' + SortOrder_Blacklist +
                        '&EnableImages=' + EnableImages_Blacklist + '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacklist + '&EnableUserData=' + EnableUserData_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        data_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,QueriesRemaining_Blacklist=api_query_handler(apiQuery_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,APIDebugMsg_Blacklist)
                    else:
                        #When no media items are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Blacklist=0
                        QueriesRemaining_Blacklist=False

                    if not (LibraryID_BlkLst == ''):
                        #Built query for Favorited from Blacklist media items
                        apiQuery_Favorited_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Blacklist +
                        '&StartIndex=' + str(StartIndex_Favorited_From_Blacklist) + '&Limit=' + str(QueryLimit_Favorited_From_Blacklist) + '&Fields=' + FieldsState_Favorited_From_Blacklist +
                        '&Recursive=' + Recursive_Favorited_From_Blacklist + '&SortBy=' + SortBy_Favorited_From_Blacklist + '&SortOrder=' + SortOrder_Favorited_From_Blacklist + '&EnableImages=' + EnableImages_Favorited_From_Blacklist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Blacklist + '&IsFavorite=' + IsFavorite_From_Blacklist + '&EnableUserData=' + EnableUserData_Favorited_From_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for Favorited from Blacklist media items
                        data_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,QueriesRemaining_Favorited_From_Blacklist=api_query_handler(apiQuery_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,APIDebugMsg_Favorited_From_Blacklist)
                    else:
                        #When no media items are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Favorited_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Favorited_From_Blacklist=0
                        QueriesRemaining_Favorited_From_Blacklist=False

                    if not (LibraryID_WhtLst == ''):
                        #Built query for Favorited From Whitelist media items
                        apiQuery_Favorited_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Whitelist +
                        '&StartIndex=' + str(StartIndex_Favorited_From_Whitelist) + '&Limit=' + str(QueryLimit_Favorited_From_Whitelist) + '&Fields=' + FieldsState_Favorited_From_Whitelist +
                        '&Recursive=' + Recursive_Favorited_From_Whitelist + '&SortBy=' + SortBy_Favorited_From_Whitelist + '&SortOrder=' + SortOrder_Favorited_From_Whitelist + '&EnableImages=' + EnableImages_Favorited_From_Whitelist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Whitelist + '&IsFavorite=' + IsFavorite_From_Whitelist + '&EnableUserData=' + EnableUserData_Favorited_From_Whitelist + '&api_key=' + auth_key)

                        #Send the API query for for Favorited from Whitelist media items
                        data_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,QueriesRemaining_Favorited_From_Whitelist=api_query_handler(apiQuery_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,APIDebugMsg_Favorited_From_Whitelist)
                    else:
                        #When no media items are whitelisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
                        data_Favorited_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Favorited_From_Whitelist=0
                        QueriesRemaining_Favorited_From_Whitelist=False

                    #Check if blacktag or blacklist are not an empty strings
                    if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                        #Built query for blacktagged from blacklist media items
                        apiQuery_BlackTagged_From_BlackList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_BlackList +
                        '&StartIndex=' + str(StartIndex_BlackTagged_From_BlackList) + '&Limit=' + str(QueryLimit_BlackTagged_From_BlackList) + '&Fields=' + FieldsState_BlackTagged_From_BlackList +
                        '&Recursive=' + Recursive_Blacktagged_From_BlackList + '&SortBy=' + SortBy_BlackTagged_From_BlackList + '&SortOrder=' + SortOrder_BlackTagged_From_BlackList + '&EnableImages=' + EnableImages_Blacktagged_From_BlackList +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_BlackList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_BlackList + '&api_key=' + auth_key)

                        #Send the API query for for blacktagged from blacklist media items
                        data_Blacktagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,QueriesRemaining_BlackTagged_From_BlackList=api_query_handler(apiQuery_BlackTagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,APIDebugMsg_BlackTagged_From_BlackList)
                    else: #((BlackTags_Tagged == '') or (LibraryID_BlkLst == ''))
                        data_Blacktagged_From_BlackList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_BlackTagged_From_BlackList=0
                        QueriesRemaining_BlackTagged_From_BlackList=False

                    #Check if blacktag or whitelist are not an empty strings
                    if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                        #Built query for blacktagged from whitelist media items
                        apiQuery_BlackTagged_From_WhiteList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_WhiteList +
                        '&StartIndex=' + str(StartIndex_BlackTagged_From_WhiteList) + '&Limit=' + str(QueryLimit_BlackTagged_From_WhiteList) + '&Fields=' + FieldsState_BlackTagged_From_WhiteList +
                        '&Recursive=' + Recursive_Blacktagged_From_WhiteList + '&SortBy=' + SortBy_BlackTagged_From_WhiteList + '&SortOrder=' + SortOrder_BlackTagged_From_WhiteList + '&EnableImages=' + EnableImages_Blacktagged_From_WhiteList +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_WhiteList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_WhiteList + '&api_key=' + auth_key)

                        #Send the API query for for blacktagged from whitelist media items
                        data_Blacktagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,QueriesRemaining_BlackTagged_From_WhiteList=api_query_handler(apiQuery_BlackTagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,APIDebugMsg_BlackTagged_From_WhiteList)
                    else: #((BlackTags_Tagged == '') or (LibraryID_WhtLst == ''))
                        data_Blacktagged_From_WhiteList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_BlackTagged_From_WhiteList=0
                        QueriesRemaining_BlackTagged_From_WhiteList=False

                    #Check if whitetag or blacklist are not an empty strings
                    if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                        #Built query for whitetagged from Blacklist media items
                        apiQuery_WhiteTagged_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Blacklist +
                        '&StartIndex=' + str(StartIndex_WhiteTagged_From_Blacklist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Blacklist) + '&Fields=' + FieldsState_WhiteTagged_From_Blacklist +
                        '&Recursive=' + Recursive_Whitetagged_From_Blacklist + '&SortBy=' + SortBy_WhiteTagged_From_Blacklist + '&SortOrder=' + SortOrder_WhiteTagged_From_Blacklist + '&EnableImages=' + EnableImages_Whitetagged_From_Blacklist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Blacklist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for whitetagged from Blacklist= media items
                        data_Whitetagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,QueriesRemaining_WhiteTagged_From_Blacklist=api_query_handler(apiQuery_WhiteTagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,APIDebugMsg_WhiteTagged_From_Blacklist)
                    else: #(WhiteTags_Tagged_From_Blacklist == '')
                        data_Whitetagged_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_WhiteTagged_From_Blacklist=0
                        QueriesRemaining_WhiteTagged_From_Blacklist=False

                    #Check if whitetag or whitelist are not an empty strings
                    if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                        #Built query for whitetagged_From_Whitelist= media items
                        apiQuery_WhiteTagged_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Whitelist +
                        '&StartIndex=' + str(StartIndex_WhiteTagged_From_Whitelist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Whitelist) + '&Fields=' + FieldsState_WhiteTagged_From_Whitelist +
                        '&Recursive=' + Recursive_Whitetagged_From_Whitelist + '&SortBy=' + SortBy_WhiteTagged_From_Whitelist + '&SortOrder=' + SortOrder_WhiteTagged_From_Whitelist + '&EnableImages=' + EnableImages_Whitetagged_From_Whitelist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Whitelist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Whitelist + '&api_key=' + auth_key)

                        #Send the API query for for whitetagged_From_Whitelist= media items
                        data_Whitetagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,QueriesRemaining_WhiteTagged_From_Whitelist=api_query_handler(apiQuery_WhiteTagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,APIDebugMsg_WhiteTagged_From_Whitelist)
                    else: #(WhiteTags_Tagged == '')
                        data_Whitetagged_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_WhiteTagged_From_Whitelist=0
                        QueriesRemaining_WhiteTagged_From_Whitelist=False

                    #Define reasoning for lookup
                    APIDebugMsg_Favorited_From_Blacklist_Child='favorited_From_Blacklist_from_blacklist_child'
                    data_Favorited_From_Blacklist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Blacklist,audio_played_count_comparison,audio_played_count,audio_created_played_count_comparison,audio_created_played_count,APIDebugMsg_Favorited_From_Blacklist_Child,audio_played_days,audio_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Favorited_From_Whitelist_Child='favorited_From_Whitelist_from_whitelist_child'
                    data_Favorited_From_Whitelist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Whitelist,audio_played_count_comparison,audio_played_count,audio_created_played_count_comparison,audio_created_played_count,APIDebugMsg_Favorited_From_Whitelist_Child,audio_played_days,audio_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_From_BlackList_Child='blacktag_child_from_blacklist_child'
                    data_Blacktagged_From_BlackList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_BlackList,blacktags,audio_played_count_comparison,audio_played_count,audio_created_played_count_comparison,audio_created_played_count,APIDebugMsg_Blacktag_From_BlackList_Child,audio_played_days,audio_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_From_WhiteList_Child='blacktag_child_from_whitelist_child'
                    data_Blacktagged_From_WhiteList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_WhiteList,blacktags,audio_played_count_comparison,audio_played_count,audio_created_played_count_comparison,audio_created_played_count,APIDebugMsg_Blacktag_From_WhiteList_Child,audio_played_days,audio_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_From_Blacklist_Child='whitetag_child_from_blacklist_child'
                    data_Whitetagged_From_Blacklist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Blacklist,whitetags,audio_played_count_comparison,audio_played_count,audio_created_played_count_comparison,audio_created_played_count,APIDebugMsg_Whitetag_From_Blacklist_Child,audio_played_days,audio_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_From_Whitelist_Child='whitetag_child_from_blacklist_child'
                    data_Whitetagged_From_Whitelist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Whitelist,whitetags,audio_played_count_comparison,audio_played_count,audio_created_played_count_comparison,audio_created_played_count,APIDebugMsg_Whitetag_From_Whitelist_Child,audio_played_days,audio_created_days)

                    #Combine dictionaries into list of dictionaries
                    #Order here is important
                    data_list=[data_Favorited_From_Whitelist, #0
                               data_Favorited_From_Whitelist_Children, #1
                               data_Whitetagged_From_Whitelist, #2
                               data_Whitetagged_From_Whitelist_Children, #3
                               data_Blacktagged_From_WhiteList, #4
                               data_Blacktagged_From_WhiteList_Children, #5
                               data_Favorited_From_Blacklist, #6
                               data_Favorited_From_Blacklist_Children, #7
                               data_Whitetagged_From_Blacklist, #8
                               data_Whitetagged_From_Blacklist_Children, #9
                               data_Blacktagged_From_BlackList, #10
                               data_Blacktagged_From_BlackList_Children, #11
                               data_Blacklist] #12

                    #Order here is important (must match above)
                    data_from_favorited_queries=[0,1,6,7]
                    data_from_whitetag_queries=[2,3,8,9]
                    data_from_blacktag_queries=[4,5,10,11]
                    data_from_whitelist_queries=[0,1,2,3,4,5]
                    #data_from_blacklist_queries=[6,7,8,9,10,11,12]

                    #Determine if we are done processing queries or if there are still queries to be sent
                    QueryItemsRemaining_All=(QueriesRemaining_Favorited_From_Blacklist |
                                             QueriesRemaining_Favorited_From_Whitelist |
                                             QueriesRemaining_WhiteTagged_From_Blacklist |
                                             QueriesRemaining_WhiteTagged_From_Whitelist |
                                             QueriesRemaining_BlackTagged_From_BlackList |
                                             QueriesRemaining_BlackTagged_From_WhiteList |
                                             QueriesRemaining_Blacklist)

                    #track where we are in the data_list
                    data_list_pos=0

                    #Determine if media item is to be deleted or kept
                    #Loop thru each dictionary in data_list[#]
                    for data in data_list:

                        #Loop thru each dictionary[item]
                        for item in data['Items']:

                            #Check if item was already processed for this user
                            if not (item['Id'] in user_processed_itemsId):

                                if (GLOBAL_DEBUG):
                                    #Double newline for DEBUG log formatting
                                    print_byType("\n\nInspecting Media Item: " + str(item['Id']),False)

                                media_found=True

                                itemIsMonitored=False
                                if (item['Type'] == 'Audio'):
                                    for mediasource in item['MediaSources']:
                                        itemIsMonitored=get_isItemMonitored(mediasource)

                                #find media item is ready to delete
                                if (itemIsMonitored):

                                    if (GLOBAL_DEBUG):
                                        print_byType("\nProcessing Audio Item: " + str(item['Id']),False)

                                    #establish played cutoff date for media item
                                    if ((audio_played_days >= 0) and ('UserData' in item) and ('LastPlayedDate' in item['UserData'])):
                                        if ((cut_off_date_played_audio) > (parse(item['UserData']['LastPlayedDate']))):
                                            item_matches_played_condition_day_filter=True
                                        else:
                                            item_matches_played_condition_day_filter=False
                                    else:
                                        item_matches_played_condition_day_filter=False

                                    #establish created cutoff date for media item
                                    if ((audio_created_days >= 0) and ('DateCreated' in item)):
                                        if (cut_off_date_created_audio > parse(item['DateCreated'])):
                                            item_matches_created_condition_day_filter=True
                                        else:
                                            item_matches_created_condition_day_filter=False
                                    else:
                                        item_matches_created_condition_day_filter=False

                                    itemisfav_AUDIO_Local=False
                                    #Get if media item is set as favorite
                                    if (data_list_pos in data_from_favorited_queries):
                                        itemisfav_AUDIO_Local=True
                                    elif ((keep_favorites_audio) and ('UserData' in item) and ('IsFavorite' in item['UserData']) and (item['UserData']['IsFavorite'])):
                                        itemisfav_AUDIO_Local=True

                                    itemisfav_AUDIO_Advanced=False
                                    if ((keep_favorites_audio) and (keep_favorites_advanced_track_genre or keep_favorites_advanced_album_genre or
                                        keep_favorites_advanced_music_library_genre or keep_favorites_advanced_track_artist or
                                        keep_favorites_advanced_album_artist)):
                                        itemisfav_AUDIO_Advanced=get_isAUDIO_AdvancedFav(item,user_key,'Audio')

                                    itemisfav_AUDIO_Display=False
                                    if (itemisfav_AUDIO_Local or itemisfav_AUDIO_Advanced):
                                        itemisfav_AUDIO_Display=True

                                    #Store media item's favorite state when multiple users are monitored and we want to keep media items based on any user favoriting the media item
                                    if ((keep_favorites_audio == 2) and (itemisfav_AUDIO_Local or itemisfav_AUDIO_Advanced)):
                                        isfav_byUserId_Audio[user_key][item['Id']]=True

                                    itemIsWhiteTagged=False
                                    if (data_list_pos in data_from_whitetag_queries):
                                        itemIsWhiteTagged=True
                                        audio_whitetag_list.append(item['Id'])
                                    elif not (whitetags == ''):
                                        if (get_isAUDIO_Tagged(item,user_key,whitetags)):
                                            itemIsWhiteTagged=True
                                            audio_whitetag_list.append(item['Id'])

                                    itemIsBlackTagged=False
                                    if (data_list_pos in data_from_blacktag_queries):
                                        itemIsBlackTagged=True
                                        audio_blacktaglists.append(item['Id'])
                                    elif not (blacktags == ''):
                                        if (get_isAUDIO_Tagged(item,user_key,blacktags)):
                                            itemIsBlackTagged=True
                                            audio_blacktaglists.append(item['Id'])

                                    itemIsWhiteListed_Display=False
                                    #check if we are at a whitelist queried data_list_pos
                                    if (data_list_pos in data_from_whitelist_queries):
                                        itemIsWhiteListed_Local,itemIsWhiteListed_Remote=get_isItemWhitelisted(LibraryID_WhtLst,LibraryNetPath_WhtLst,LibraryPath_WhtLst,currentPosition,
                                                                                                               user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json)

                                        #Display True if media item is locally or remotely whitelisted
                                        itemIsWhiteListed_Display=(itemIsWhiteListed_Local or itemIsWhiteListed_Remote)

                                        #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                        if ((itemIsWhiteListed_Local) and (multiuser_whitelist_audio == 0)):
                                            audio_whitelists.append(item['Id'])
                                    else: #check if we are at a blacklist queried data_list_pos
                                        itemIsWhiteListed_Local,itemIsWhiteListed_Remote=get_isItemWhitelisted(LibraryID_BlkLst,LibraryNetPath_BlkLst,LibraryPath_BlkLst,currentPosition,
                                                                                                               user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json)

                                        #Display True if media item is locally or remotely whitelisted
                                        itemIsWhiteListed_Display=(itemIsWhiteListed_Local or itemIsWhiteListed_Remote)

                                        #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                        if ((itemIsWhiteListed_Local) and (multiuser_whitelist_audio == 0)):
                                            audio_whitelists.append(item['Id'])

                                    #Decide if media item meets the played count filter criteria
                                    if (('UserData' in item) and ('PlayCount' in item['UserData'])):
                                        item_matches_played_count_filter=get_playedStatus(item,'played',audio_played_count_comparison,audio_played_count)
                                    else:
                                        #itemPlayedStateIsDeletable=False
                                        item_matches_played_count_filter=False

                                    if ((multiuser_play_count_audio == 1) and (item_matches_played_count_filter)):
                                        isMeeting_PlayCountFilter_Audio[user_key][item['Id']]=True

                                    #Decide if media item meets the created count filter criteria
                                    if (('DateCreated' in item)):
                                        item_matches_created_played_count_filter=get_createdStatus(item,'created',audio_created_played_count_comparison,audio_created_played_count)
                                    else:
                                        #itemPlayedStateIsDeletable=False
                                        item_matches_created_played_count_filter=False

                                    #Decide how to handle the fav_local, fav_adv, whitetag, blacktag, whitelist_local, and whitelist_remote flags
                                    itemIsOKToDelete=get_deleteStatus(item_matches_played_count_filter,item_matches_played_condition_day_filter,item_matches_created_played_count_filter,item_matches_created_condition_day_filter,itemisfav_AUDIO_Local,itemisfav_AUDIO_Advanced,itemIsWhiteTagged,itemIsBlackTagged,itemIsWhiteListed_Local,itemIsWhiteListed_Remote)

                                    if ((delete_blacktagged_audio == 1) and itemIsBlackTagged and itemIsOKToDelete):
                                        isblacktag_and_watched_byUserId_Audio[user_key][item['Id']]=True

                                    if ('Played' in item['UserData']):

                                        try:
                                            #Fill in the blanks
                                            item=prepare_AUDIOoutput(item)

                                            item_output_details=(item['Type'] + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Album: ' + item['Album'] + ' - Artist: ' + item['Artists'][0] +
                                                          ' - Record Label: ' + item['Studios'][0]['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) +
                                                          ' - Play Count: ' + str(item['UserData']['PlayCount']) + ' - ' + get_days_since_created(item['DateCreated']) + ' - Favorite: ' + str(itemisfav_AUDIO_Display) +
                                                          ' - WhiteTag: ' + str(itemIsWhiteTagged) + ' - BlackTag: ' + str(itemIsBlackTagged) + ' - Whitelisted: ' + str(itemIsWhiteListed_Display) +
                                                          ' - ' + item['Type'] + 'ID: ' + item['Id'])
                                        except (KeyError, IndexError):
                                            item_output_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                                            if (GLOBAL_DEBUG):
                                                print_byType('\nError encountered - Audio: \nitem: ' + str(item) + '\nitem' + str(item),False)

                                        if (itemIsOKToDelete):
                                            if (GLOBAL_DEBUG):
                                                print_audio_delete_info=True
                                                print_byType("\n\n",False)
                                            print_byType(':*[DELETE] - ' + item_output_details,print_audio_delete_info)
                                            deleteItems.append(item)
                                        else:
                                            if (GLOBAL_DEBUG):
                                                print_audio_delete_info=True
                                                print_byType("\n\n",False)
                                            print_byType(':[KEEPING] - ' + item_output_details,print_audio_keep_info)

                                        if (GLOBAL_DEBUG):
                                            #Spacing for debug file
                                            print_byType("\n",False)

                                #Add media item Id to tracking list so it is not processed more than once
                                user_processed_itemsId.add(item['Id'])

                        data_list_pos += 1

                currentSubPosition += 1

############# AudioBook#############

        #audioBook meida type only applies to jellyfin
        #Jellyfin sets audio books to a media type of audioBook
        #Emby sets audio books to a media type of audio (see audio section)
        if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0))):

            if (GLOBAL_DEBUG):
                print_byType("\n\nProcessing AUDIOBOOK Items For UserId: " + str(user_key),False)

            user_processed_itemsId=set()

            currentSubPosition=0

            for LibraryID_BlkLst,LibraryID_WhtLst,LibraryNetPath_BlkLst,LibraryNetPath_WhtLst,LibraryPath_BlkLst,LibraryPath_WhtLst in zip(user_bllib_keys_json_lensplit,user_wllib_keys_json_lensplit,user_bllib_netpath_json_lensplit,user_wllib_netpath_json_lensplit,user_bllib_path_json_lensplit,user_wllib_path_json_lensplit):

                #Initialize api_query_handler() variables for watched media items in blacklists
                StartIndex_Blacklist=0
                TotalItems_Blacklist=1
                QueryLimit_Blacklist=1
                QueriesRemaining_Blacklist=True
                APIDebugMsg_Blacklist='audiobook_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for watched media items in blacklists
                    IncludeItemTypes_Blacklist='Audio'
                    FieldsState_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_Blacklist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Blacklist='Ascending'
                    EnableUserData_Blacklist='True'
                    Recursive_Blacklist='True'
                    EnableImages_Blacklist='False'
                    CollapseBoxSetItems_Blacklist='False'
                    if(audiobook_played_days >= 0):
                        IsPlayed_Blacklist=get_isPlayed_FilterValue(audiobook_played_count_comparison,audiobook_played_count)
                    else:
                        IsPlayed_Blacklist='disable'
                    if(audiobook_created_days >= 0):
                        IsCreated_Blacklist=get_isCreated_FilterValue(audiobook_created_played_count_comparison,audiobook_created_played_count)
                    else:
                        IsCreated_Blacklist='disable'
                    IsPlayedState_Blacklist=get_isPlayedCreated_FilterValue(IsPlayed_Blacklist,IsCreated_Blacklist)

                #Initialize api_query_handler() variables for Favorited from Blacklist media items
                StartIndex_Favorited_From_Blacklist=0
                TotalItems_Favorited_From_Blacklist=1
                QueryLimit_Favorited_From_Blacklist=1
                QueriesRemaining_Favorited_From_Blacklist=True
                APIDebugMsg_Favorited_From_Blacklist='audiobook_Favorited_From_Blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for Favorited_From_Blacklist media items
                    IncludeItemTypes_Favorited_From_Blacklist='Audio,Book,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_Favorited_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_Favorited_From_Blacklist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Favorited_From_Blacklist='Ascending'
                    EnableUserData_Favorited_From_Blacklist='True'
                    Recursive_Favorited_From_Blacklist='True'
                    EnableImages_Favorited_From_Blacklist='False'
                    CollapseBoxSetItems_Favorited_From_Blacklist='False'
                    IsFavorite_From_Blacklist='True'

                #Initialize api_query_handler() variables for Favorited from Whitelist media items
                StartIndex_Favorited_From_Whitelist=0
                TotalItems_Favorited_From_Whitelist=1
                QueryLimit_Favorited_From_Whitelist=1
                QueriesRemaining_Favorited_From_Whitelist=True
                APIDebugMsg_Favorited_From_Whitelist='audiobook_Favorited_From_Whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for Favorited_From_Whitelist media items
                    IncludeItemTypes_Favorited_From_Whitelist='Audio,Book,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_Favorited_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_Favorited_From_Whitelist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Favorited_From_Whitelist='Ascending'
                    EnableUserData_Favorited_From_Whitelist='True'
                    Recursive_Favorited_From_Whitelist='True'
                    EnableImages_Favorited_From_Whitelist='False'
                    CollapseBoxSetItems_Favorited_From_Whitelist='False'
                    IsFavorite_From_Whitelist='True'

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged_From_BlackList=0
                TotalItems_BlackTagged_From_BlackList=1
                QueryLimit_BlackTagged_From_BlackList=1
                QueriesRemaining_BlackTagged_From_BlackList=True
                APIDebugMsg_BlackTagged_From_BlackList='audiobook_blacktagged_from_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for blacktagged media items from blacklist
                    IncludeItemTypes_BlackTagged_From_BlackList='Audio,Book,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_BlackTagged_From_BlackList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_BlackTagged_From_BlackList='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_BlackTagged_From_BlackList='Ascending'
                    EnableUserData_Blacktagged_From_BlackList='True'
                    Recursive_Blacktagged_From_BlackList='True'
                    EnableImages_Blacktagged_From_BlackList='False'
                    CollapseBoxSetItems_Blacktagged_From_BlackList='False'
                    #Encode blacktags so they are url acceptable
                    BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged_From_WhiteList=0
                TotalItems_BlackTagged_From_WhiteList=1
                QueryLimit_BlackTagged_From_WhiteList=1
                QueriesRemaining_BlackTagged_From_WhiteList=True
                APIDebugMsg_BlackTagged_From_WhiteList='audiobook_blacktagged_from_whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for blacktagged media items from whitelist
                    IncludeItemTypes_BlackTagged_From_WhiteList='Audio,Book,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_BlackTagged_From_WhiteList='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_BlackTagged_From_WhiteList='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_BlackTagged_From_WhiteList='Ascending'
                    EnableUserData_Blacktagged_From_WhiteList='True'
                    Recursive_Blacktagged_From_WhiteList='True'
                    EnableImages_Blacktagged_From_WhiteList='False'
                    CollapseBoxSetItems_Blacktagged_From_WhiteList='False'
                    #Encode blacktags so they are url acceptable
                    BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged_From_Blacklist=0
                TotalItems_WhiteTagged_From_Blacklist=1
                QueryLimit_WhiteTagged_From_Blacklist=1
                QueriesRemaining_WhiteTagged_From_Blacklist=True
                APIDebugMsg_WhiteTagged_From_Blacklist='audiobook_whitetagged_from_blacklist_media_items'

                if not (LibraryID_BlkLst == ''):
                    #Build query for whitetagged media items
                    IncludeItemTypes_WhiteTagged_From_Blacklist='Audio,Book,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_WhiteTagged_From_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_WhiteTagged_From_Blacklist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_WhiteTagged_From_Blacklist='Ascending'
                    EnableUserData_Whitetagged_From_Blacklist='True'
                    Recursive_Whitetagged_From_Blacklist='True'
                    EnableImages_Whitetagged_From_Blacklist='False'
                    CollapseBoxSetItems_Whitetagged_From_Blacklist='False'
                    #Encode whitetags so they are url acceptable
                    WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged_From_Whitelist=0
                TotalItems_WhiteTagged_From_Whitelist=1
                QueryLimit_WhiteTagged_From_Whitelist=1
                QueriesRemaining_WhiteTagged_From_Whitelist=True
                APIDebugMsg_WhiteTagged_From_Whitelist='audiobook_whitetagged_from_whitelist_media_items'

                if not (LibraryID_WhtLst == ''):
                    #Build query for whitetagged media items
                    IncludeItemTypes_WhiteTagged_From_Whitelist='Audio,Book,MusicAlbum,Playlist,CollectionFolder'
                    FieldsState_WhiteTagged_From_Whitelist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_WhiteTagged_From_Whitelist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_WhiteTagged_From_Whitelist='Ascending'
                    EnableUserData_Whitetagged_From_Whitelist='True'
                    Recursive_Whitetagged_From_Whitelist='True'
                    EnableImages_Whitetagged_From_Whitelist='False'
                    CollapseBoxSetItems_Whitetagged_From_Whitelist='False'
                    #Encode whitetags so they are url acceptable
                    WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                QueryItemsRemaining_All=True

                while (QueryItemsRemaining_All):

                    if not (LibraryID_BlkLst == ''):
                        #Built query for watched items in blacklists
                        apiQuery_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Blacklist +
                        '&StartIndex=' + str(StartIndex_Blacklist) + '&Limit=' + str(QueryLimit_Blacklist) + '&IsPlayed=' + IsPlayedState_Blacklist +
                        '&Fields=' + FieldsState_Blacklist + '&Recursive=' + Recursive_Blacklist + '&SortBy=' + SortBy_Blacklist + '&SortOrder=' + SortOrder_Blacklist +
                        '&EnableImages=' + EnableImages_Blacklist + '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacklist + '&EnableUserData=' + EnableUserData_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        data_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,QueriesRemaining_Blacklist=api_query_handler(apiQuery_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,APIDebugMsg_Blacklist)
                    else:
                        #When no media items are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Blacklist=0
                        QueriesRemaining_Blacklist=False

                    if not (LibraryID_BlkLst == ''):
                        #Built query for Favorited from Blacklist media items
                        apiQuery_Favorited_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Blacklist +
                        '&StartIndex=' + str(StartIndex_Favorited_From_Blacklist) + '&Limit=' + str(QueryLimit_Favorited_From_Blacklist) + '&Fields=' + FieldsState_Favorited_From_Blacklist +
                        '&Recursive=' + Recursive_Favorited_From_Blacklist + '&SortBy=' + SortBy_Favorited_From_Blacklist + '&SortOrder=' + SortOrder_Favorited_From_Blacklist + '&EnableImages=' + EnableImages_Favorited_From_Blacklist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Blacklist + '&IsFavorite=' + IsFavorite_From_Blacklist + '&EnableUserData=' + EnableUserData_Favorited_From_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for Favorited from Blacklist media items
                        data_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,QueriesRemaining_Favorited_From_Blacklist=api_query_handler(apiQuery_Favorited_From_Blacklist,StartIndex_Favorited_From_Blacklist,TotalItems_Favorited_From_Blacklist,QueryLimit_Favorited_From_Blacklist,APIDebugMsg_Favorited_From_Blacklist)
                    else:
                        #When no media items are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Favorited_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Favorited_From_Blacklist=0
                        QueriesRemaining_Favorited_From_Blacklist=False

                    if not (LibraryID_WhtLst == ''):
                        #Built query for Favorited From Whitelist media items
                        apiQuery_Favorited_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_Favorited_From_Whitelist +
                        '&StartIndex=' + str(StartIndex_Favorited_From_Whitelist) + '&Limit=' + str(QueryLimit_Favorited_From_Whitelist) + '&Fields=' + FieldsState_Favorited_From_Whitelist +
                        '&Recursive=' + Recursive_Favorited_From_Whitelist + '&SortBy=' + SortBy_Favorited_From_Whitelist + '&SortOrder=' + SortOrder_Favorited_From_Whitelist + '&EnableImages=' + EnableImages_Favorited_From_Whitelist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited_From_Whitelist + '&IsFavorite=' + IsFavorite_From_Whitelist + '&EnableUserData=' + EnableUserData_Favorited_From_Whitelist + '&api_key=' + auth_key)

                        #Send the API query for for Favorited from Whitelist media items
                        data_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,QueriesRemaining_Favorited_From_Whitelist=api_query_handler(apiQuery_Favorited_From_Whitelist,StartIndex_Favorited_From_Whitelist,TotalItems_Favorited_From_Whitelist,QueryLimit_Favorited_From_Whitelist,APIDebugMsg_Favorited_From_Whitelist)
                    else:
                        #When no media items are whitelisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty whitelist string '' to the whitelist libraries later on
                        data_Favorited_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_Favorited_From_Whitelist=0
                        QueriesRemaining_Favorited_From_Whitelist=False

                    #Check if blacktag or blacklist are not an empty strings
                    if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                        #Built query for blacktagged from blacklist media items
                        apiQuery_BlackTagged_From_BlackList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_BlackList +
                        '&StartIndex=' + str(StartIndex_BlackTagged_From_BlackList) + '&Limit=' + str(QueryLimit_BlackTagged_From_BlackList) + '&Fields=' + FieldsState_BlackTagged_From_BlackList +
                        '&Recursive=' + Recursive_Blacktagged_From_BlackList + '&SortBy=' + SortBy_BlackTagged_From_BlackList + '&SortOrder=' + SortOrder_BlackTagged_From_BlackList + '&EnableImages=' + EnableImages_Blacktagged_From_BlackList +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_BlackList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_BlackList + '&api_key=' + auth_key)

                        #Send the API query for for blacktagged from blacklist media items
                        data_Blacktagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,QueriesRemaining_BlackTagged_From_BlackList=api_query_handler(apiQuery_BlackTagged_From_BlackList,StartIndex_BlackTagged_From_BlackList,TotalItems_BlackTagged_From_BlackList,QueryLimit_BlackTagged_From_BlackList,APIDebugMsg_BlackTagged_From_BlackList)
                    else: #((BlackTags_Tagged == '') or (LibraryID_BlkLst == ''))
                        data_Blacktagged_From_BlackList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_BlackTagged_From_BlackList=0
                        QueriesRemaining_BlackTagged_From_BlackList=False

                    #Check if blacktag or whitelist are not an empty strings
                    if (( not (BlackTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                        #Built query for blacktagged from whitelist media items
                        apiQuery_BlackTagged_From_WhiteList=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_BlackTagged_From_WhiteList +
                        '&StartIndex=' + str(StartIndex_BlackTagged_From_WhiteList) + '&Limit=' + str(QueryLimit_BlackTagged_From_WhiteList) + '&Fields=' + FieldsState_BlackTagged_From_WhiteList +
                        '&Recursive=' + Recursive_Blacktagged_From_WhiteList + '&SortBy=' + SortBy_BlackTagged_From_WhiteList + '&SortOrder=' + SortOrder_BlackTagged_From_WhiteList + '&EnableImages=' + EnableImages_Blacktagged_From_WhiteList +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged_From_WhiteList + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged_From_WhiteList + '&api_key=' + auth_key)

                        #Send the API query for for blacktagged from whitelist media items
                        data_Blacktagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,QueriesRemaining_BlackTagged_From_WhiteList=api_query_handler(apiQuery_BlackTagged_From_WhiteList,StartIndex_BlackTagged_From_WhiteList,TotalItems_BlackTagged_From_WhiteList,QueryLimit_BlackTagged_From_WhiteList,APIDebugMsg_BlackTagged_From_WhiteList)
                    else: #((BlackTags_Tagged == '') or (LibraryID_WhtLst == ''))
                        data_Blacktagged_From_WhiteList={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_BlackTagged_From_WhiteList=0
                        QueriesRemaining_BlackTagged_From_WhiteList=False

                    #Check if whitetag or blacklist are not an empty strings
                    if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_BlkLst == ''))):
                        #Built query for whitetagged from Blacklist media items
                        apiQuery_WhiteTagged_From_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_BlkLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Blacklist +
                        '&StartIndex=' + str(StartIndex_WhiteTagged_From_Blacklist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Blacklist) + '&Fields=' + FieldsState_WhiteTagged_From_Blacklist +
                        '&Recursive=' + Recursive_Whitetagged_From_Blacklist + '&SortBy=' + SortBy_WhiteTagged_From_Blacklist + '&SortOrder=' + SortOrder_WhiteTagged_From_Blacklist + '&EnableImages=' + EnableImages_Whitetagged_From_Blacklist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Blacklist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for whitetagged from Blacklist= media items
                        data_Whitetagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,QueriesRemaining_WhiteTagged_From_Blacklist=api_query_handler(apiQuery_WhiteTagged_From_Blacklist,StartIndex_WhiteTagged_From_Blacklist,TotalItems_WhiteTagged_From_Blacklist,QueryLimit_WhiteTagged_From_Blacklist,APIDebugMsg_WhiteTagged_From_Blacklist)
                    else: #(WhiteTags_Tagged_From_Blacklist == '')
                        data_Whitetagged_From_Blacklist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_WhiteTagged_From_Blacklist=0
                        QueriesRemaining_WhiteTagged_From_Blacklist=False

                    #Check if whitetag or whitelist are not an empty strings
                    if (( not (WhiteTags_Tagged == '')) and ( not (LibraryID_WhtLst == ''))):
                        #Built query for whitetagged_From_Whitelist= media items
                        apiQuery_WhiteTagged_From_Whitelist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID_WhtLst + '&IncludeItemTypes=' + IncludeItemTypes_WhiteTagged_From_Whitelist +
                        '&StartIndex=' + str(StartIndex_WhiteTagged_From_Whitelist) + '&Limit=' + str(QueryLimit_WhiteTagged_From_Whitelist) + '&Fields=' + FieldsState_WhiteTagged_From_Whitelist +
                        '&Recursive=' + Recursive_Whitetagged_From_Whitelist + '&SortBy=' + SortBy_WhiteTagged_From_Whitelist + '&SortOrder=' + SortOrder_WhiteTagged_From_Whitelist + '&EnableImages=' + EnableImages_Whitetagged_From_Whitelist +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged_From_Whitelist + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged_From_Whitelist + '&api_key=' + auth_key)

                        #Send the API query for for whitetagged_From_Whitelist= media items
                        data_Whitetagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,QueriesRemaining_WhiteTagged_From_Whitelist=api_query_handler(apiQuery_WhiteTagged_From_Whitelist,StartIndex_WhiteTagged_From_Whitelist,TotalItems_WhiteTagged_From_Whitelist,QueryLimit_WhiteTagged_From_Whitelist,APIDebugMsg_WhiteTagged_From_Whitelist)
                    else: #(WhiteTags_Tagged == '')
                        data_Whitetagged_From_Whitelist={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit_WhiteTagged_From_Whitelist=0
                        QueriesRemaining_WhiteTagged_From_Whitelist=False

                    #Define reasoning for lookup
                    APIDebugMsg_Favorited_From_Blacklist_Child='favorited_From_Blacklist_from_blacklist_child'
                    data_Favorited_From_Blacklist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Blacklist,audiobook_played_count_comparison,audiobook_played_count,audiobook_created_played_count_comparison,audiobook_created_played_count,APIDebugMsg_Favorited_From_Blacklist_Child,audiobook_played_days,audiobook_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Favorited_From_Whitelist_Child='favorited_From_Whitelist_from_whitelist_child'
                    data_Favorited_From_Whitelist_Children=getChildren_favoritedMediaItems(user_key,data_Favorited_From_Whitelist,audiobook_played_count_comparison,audiobook_played_count,audiobook_created_played_count_comparison,audiobook_created_played_count,APIDebugMsg_Favorited_From_Whitelist_Child,audiobook_played_days,audiobook_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_From_BlackList_Child='blacktag_child_from_blacklist_child'
                    data_Blacktagged_From_BlackList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_BlackList,blacktags,audiobook_played_count_comparison,audiobook_played_count,audiobook_created_played_count_comparison,audiobook_created_played_count,APIDebugMsg_Blacktag_From_BlackList_Child,audiobook_played_days,audiobook_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_From_WhiteList_Child='blacktag_child_from_whitelist_child'
                    data_Blacktagged_From_WhiteList_Children=getChildren_taggedMediaItems(user_key,data_Blacktagged_From_WhiteList,blacktags,audiobook_played_count_comparison,audiobook_played_count,audiobook_created_played_count_comparison,audiobook_created_played_count,APIDebugMsg_Blacktag_From_WhiteList_Child,audiobook_played_days,audiobook_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_From_Blacklist_Child='whitetag_child_from_blacklist_child'
                    data_Whitetagged_From_Blacklist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Blacklist,whitetags,audiobook_played_count_comparison,audiobook_played_count,audiobook_created_played_count_comparison,audiobook_created_played_count,APIDebugMsg_Whitetag_From_Blacklist_Child,audiobook_played_days,audiobook_created_days)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_From_Whitelist_Child='whitetag_child_from_blacklist_child'
                    data_Whitetagged_From_Whitelist_Children=getChildren_taggedMediaItems(user_key,data_Whitetagged_From_Whitelist,whitetags,audiobook_played_count_comparison,audiobook_played_count,audiobook_created_played_count_comparison,audiobook_created_played_count,APIDebugMsg_Whitetag_From_Whitelist_Child,audiobook_played_days,audiobook_created_days)

                    #Combine dictionaries into list of dictionaries
                    #Order here is important
                    data_list=[data_Favorited_From_Whitelist, #0
                               data_Favorited_From_Whitelist_Children, #1
                               data_Whitetagged_From_Whitelist, #2
                               data_Whitetagged_From_Whitelist_Children, #3
                               data_Blacktagged_From_WhiteList, #4
                               data_Blacktagged_From_WhiteList_Children, #5
                               data_Favorited_From_Blacklist, #6
                               data_Favorited_From_Blacklist_Children, #7
                               data_Whitetagged_From_Blacklist, #8
                               data_Whitetagged_From_Blacklist_Children, #9
                               data_Blacktagged_From_BlackList, #10
                               data_Blacktagged_From_BlackList_Children, #11
                               data_Blacklist] #12

                    #Order here is important (must match above)
                    data_from_favorited_queries=[0,1,6,7]
                    data_from_whitetag_queries=[2,3,8,9]
                    data_from_blacktag_queries=[4,5,10,11]
                    data_from_whitelist_queries=[0,1,2,3,4,5]
                    #data_from_blacklist_queries=[6,7,8,9,10,11,12]

                    #Determine if we are done processing queries or if there are still queries to be sent
                    QueryItemsRemaining_All=(QueriesRemaining_Favorited_From_Blacklist |
                                             QueriesRemaining_Favorited_From_Whitelist |
                                             QueriesRemaining_WhiteTagged_From_Blacklist |
                                             QueriesRemaining_WhiteTagged_From_Whitelist |
                                             QueriesRemaining_BlackTagged_From_BlackList |
                                             QueriesRemaining_BlackTagged_From_WhiteList |
                                             QueriesRemaining_Blacklist)

                    #track where we are in the data_list
                    data_list_pos=0

                    #Determine if media item is to be deleted or kept
                    #Loop thru each dictionary in data_list[#]
                    for data in data_list:

                        #Loop thru each dictionary[item]
                        for item in data['Items']:

                            #Check if item was already processed for this user
                            if not (item['Id'] in user_processed_itemsId):

                                if (GLOBAL_DEBUG):
                                    #Double newline for DEBUG log formatting
                                    print_byType("\n\nInspecting Media Item: " + str(item['Id']),False)

                                media_found=True

                                itemIsMonitored=False
                                if (item['Type'] == 'Audio'):
                                    for mediasource in item['MediaSources']:
                                        itemIsMonitored=get_isItemMonitored(mediasource)

                                #find media item is ready to delete
                                if (itemIsMonitored):

                                    if (GLOBAL_DEBUG):
                                        print_byType("\nProcessing AudioBook Item: " + str(item['Id']),False)

                                    #establish played cutoff date for media item
                                    if ((audiobook_played_days >= 0) and ('UserData' in item) and ('LastPlayedDate' in item['UserData'])):
                                        if ((cut_off_date_played_audiobook) > (parse(item['UserData']['LastPlayedDate']))):
                                            item_matches_played_condition_day_filter=True
                                        else:
                                            item_matches_played_condition_day_filter=False
                                    else:
                                        item_matches_played_condition_day_filter=False

                                    #establish created cutoff date for media item
                                    if ((audiobook_created_days >= 0) and ('DateCreated' in item)):
                                        if (cut_off_date_created_audiobook > parse(item['DateCreated'])):
                                            item_matches_created_condition_day_filter=True
                                        else:
                                            item_matches_created_condition_day_filter=False
                                    else:
                                        item_matches_created_condition_day_filter=False

                                    itemisfav_AUDIOBOOK_Local=False
                                    #Get if media item is set as favorite
                                    if (data_list_pos in data_from_favorited_queries):
                                        itemisfav_AUDIOBOOK_Local=True
                                    elif ((keep_favorites_audiobook) and ('UserData' in item) and ('IsFavorite' in item['UserData']) and (item['UserData']['IsFavorite'])):
                                        itemisfav_AUDIOBOOK_Local=True

                                    itemisfav_AUDIOBOOK_Advanced=False
                                    if ((keep_favorites_audiobook) and (keep_favorites_advanced_audio_book_track_genre or keep_favorites_advanced_audio_book_genre or
                                        keep_favorites_advanced_audio_book_library_genre or keep_favorites_advanced_audio_book_track_author or
                                        keep_favorites_advanced_audio_book_author)):
                                        itemisfav_AUDIOBOOK_Advanced=get_isAUDIOBOOK_AdvancedFav(item,user_key,'AudioBook')

                                    itemisfav_AUDIOBOOK_Display=False
                                    if (itemisfav_AUDIOBOOK_Local or itemisfav_AUDIOBOOK_Advanced):
                                        itemisfav_AUDIOBOOK_Display=True

                                    #Store media item's favorite state when multiple users are monitored and we want to keep media items based on any user favoriting the media item
                                    if ((keep_favorites_audiobook == 2) and (itemisfav_AUDIOBOOK_Local or itemisfav_AUDIOBOOK_Advanced)):
                                        isfav_byUserId_AudioBook[user_key][item['Id']]=True

                                    itemIsWhiteTagged=False
                                    if (data_list_pos in data_from_whitetag_queries):
                                        itemIsWhiteTagged=True
                                        audiobook_whitetag_list.append(item['Id'])
                                    elif not (whitetags == ''):
                                        if (get_isAUDIOBOOK_Tagged(item,user_key,whitetags)):
                                            itemIsWhiteTagged=True
                                            audiobook_whitetag_list.append(item['Id'])

                                    itemIsBlackTagged=False
                                    if (data_list_pos in data_from_blacktag_queries):
                                        itemIsBlackTagged=True
                                        audiobook_blacktaglists.append(item['Id'])
                                    elif not (blacktags == ''):
                                        if (get_isAUDIOBOOK_Tagged(item,user_key,blacktags)):
                                            itemIsBlackTagged=True
                                            audiobook_blacktaglists.append(item['Id'])

                                    itemIsWhiteListed_Display=False
                                    #check if we are at a whitelist queried data_list_pos
                                    if (data_list_pos in data_from_whitelist_queries):
                                        itemIsWhiteListed_Local,itemIsWhiteListed_Remote=get_isItemWhitelisted(LibraryID_WhtLst,LibraryNetPath_WhtLst,LibraryPath_WhtLst,currentPosition,
                                                                                                               user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json)

                                        #Display True if media item is locally or remotely whitelisted
                                        itemIsWhiteListed_Display=(itemIsWhiteListed_Local or itemIsWhiteListed_Remote)

                                        #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                        if ((itemIsWhiteListed_Local) and (multiuser_whitelist_audiobook == 0)):
                                            audiobook_whitelists.append(item['Id'])
                                    else: #check if we are at a blacklist queried data_list_pos
                                        itemIsWhiteListed_Local,itemIsWhiteListed_Remote=get_isItemWhitelisted(LibraryID_BlkLst,LibraryNetPath_BlkLst,LibraryPath_BlkLst,currentPosition,
                                                                                                               user_wllib_keys_json,user_wllib_netpath_json,user_wllib_path_json)

                                        #Display True if media item is locally or remotely whitelisted
                                        itemIsWhiteListed_Display=(itemIsWhiteListed_Local or itemIsWhiteListed_Remote)

                                        #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                        if ((itemIsWhiteListed_Local) and (multiuser_whitelist_audiobook == 0)):
                                            audiobook_whitelists.append(item['Id'])

                                    #Decide if media item meets the played count filter criteria
                                    if (('UserData' in item) and ('PlayCount' in item['UserData'])):
                                        item_matches_played_count_filter=get_playedStatus(item,'played',audiobook_played_count_comparison,audiobook_played_count)
                                    else:
                                        #itemPlayedStateIsDeletable=False
                                        item_matches_played_count_filter=False

                                    if ((multiuser_play_count_audiobook == 1) and (item_matches_played_count_filter)):
                                        isMeeting_PlayCountFilter_AudioBook[user_key][item['Id']]=True

                                    #Decide if media item meets the created count filter criteria
                                    if (('DateCreated' in item)):
                                        item_matches_created_played_count_filter=get_createdStatus(item,'created',audiobook_created_played_count_comparison,audiobook_created_played_count)
                                    else:
                                        #itemPlayedStateIsDeletable=False
                                        item_matches_created_played_count_filter=False

                                    #Decide how to handle the fav_local, fav_adv, whitetag, blacktag, whitelist_local, and whitelist_remote flags
                                    itemIsOKToDelete=get_deleteStatus(item_matches_played_count_filter,item_matches_played_condition_day_filter,item_matches_created_played_count_filter,item_matches_created_condition_day_filter,itemisfav_AUDIOBOOK_Local,itemisfav_AUDIOBOOK_Advanced,itemIsWhiteTagged,itemIsBlackTagged,itemIsWhiteListed_Local,itemIsWhiteListed_Remote)

                                    if ((delete_blacktagged_audiobook == 1) and itemIsBlackTagged and itemIsOKToDelete):
                                        isblacktag_and_watched_byUserId_AudioBook[user_key][item['Id']]=True

                                    if ('Played' in item['UserData']):

                                        try:
                                            #Fill in the blanks
                                            item=prepare_AUDIOBOOKoutput(item)

                                            item_output_details=(item['Type'] + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Book: ' + item['Album'] + ' - Author: ' + item['Artists'][0] +
                                                          ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - Play Count: ' + str(item['UserData']['PlayCount']) +
                                                          ' - ' + get_days_since_created(item['DateCreated']) + ' - Favorite: ' + str(itemisfav_AUDIOBOOK_Display) + ' - WhiteTag: ' + str(itemIsWhiteTagged) +
                                                          ' - BlackTag: ' + str(itemIsBlackTagged) + ' - Whitelisted: ' + str(itemIsWhiteListed_Display) + ' - ' + item['Type'] + 'ID: ' + item['Id'])
                                        except (KeyError, IndexError):
                                            item_output_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                                            if (GLOBAL_DEBUG):
                                                print_byType('\nError encountered - AudioBook: \nitem: ' + str(item) + '\nitem' + str(item),False)

                                        if (itemIsOKToDelete):
                                            if (GLOBAL_DEBUG):
                                                print_audiobook_delete_info=True
                                                print_byType("\n\n",False)
                                            print_byType(':*[DELETE] - ' + item_output_details,print_audiobook_delete_info)
                                            deleteItems.append(item)
                                        else:
                                            if (GLOBAL_DEBUG):
                                                print_audiobook_delete_info=True
                                                print_byType("\n\n",False)
                                            print_byType(':[KEEPING] - ' + item_output_details,print_audiobook_keep_info)

                                        if (GLOBAL_DEBUG):
                                            #Spacing for debug file
                                            print_byType("\n",False)

                                #Add media item Id to tracking list so it is not processed more than once
                                user_processed_itemsId.add(item['Id'])

                        data_list_pos += 1

                currentSubPosition += 1


############# End Media Types #############

        if not (all_media_disabled):
            if not (media_found):
                if (GLOBAL_DEBUG):
                    print_warnings=True
                    print_byType("\n",False)
                print_byType('[NO PLAYED, WHITELISTED, OR TAGGED MEDIA ITEMS]',print_warnings)

        if (GLOBAL_DEBUG):
            print_common_delete_keep_info=True
            print_byType("\n",False)
        print_byType('-----------------------------------------------------------',print_common_delete_keep_info)
        currentPosition+=1

    if (GLOBAL_DEBUG):
        print_byType("\nPOST PROCESSING STARTED\n",False)
        print_byType("\nList Of Possible Media Items To Be Deleted: " + str(len(deleteItems)),False)
        print_byType("\n" + convert2json(deleteItems),False)

    #When multiple users and keep_favorite_xyz==2 Determine media items to keep and remove them from deletion list
    #When not multiple users this will just clean up the deletion list
    if (((movie_played_days >= 0) or (movie_created_days >= 0)) and (keep_favorites_movie == 2)):
        deleteItems=get_isfav_ByMultiUser(user_keys_json, isfav_byUserId_Movie, deleteItems)
    if (((episode_played_days >= 0) or (episode_created_days >= 0)) and (keep_favorites_episode == 2)):
        deleteItems=get_isfav_ByMultiUser(user_keys_json, isfav_byUserId_Episode, deleteItems)
    if (((audio_played_days >= 0) or (audio_created_days >= 0)) and (keep_favorites_audio == 2)):
        deleteItems=get_isfav_ByMultiUser(user_keys_json, isfav_byUserId_Audio, deleteItems)
    if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (movie_created_days >= 0)) and (keep_favorites_audiobook == 2)):
        deleteItems=get_isfav_ByMultiUser(user_keys_json, isfav_byUserId_AudioBook, deleteItems)

    if (GLOBAL_DEBUG):
        print_byType('\n-----------------------------------------------------------',False)
        print_byType("\n",False)
        if ((movie_played_days >= 0) or (movie_created_days >= 0)):
            print_byType('\nisfav_MOVIE: ',False)
            print_byType("\n" + convert2json(isfav_byUserId_Movie),False)
            print_byType("\n",False)
        if ((episode_played_days >= 0) or (episode_created_days >= 0)):
            print_byType('\nisfav_EPISODE: ',False)
            print_byType("\n" + convert2json(isfav_byUserId_Episode),False)
            print_byType("\n",False)
        if ((audio_played_days >= 0) or (audio_created_days >= 0)):
            print_byType('\nisfav_AUDIO: ',False)
            print_byType("\n" + convert2json(isfav_byUserId_Audio),False)
            print_byType("\n",False)
        if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0))):
            print_byType('\nisfav_AUDIOBOOK: ',False)
            print_byType("\n" + convert2json(isfav_byUserId_AudioBook),False)
            print_byType("\n",False)

    #When whitetagged; Determine media items to keep and remove them from deletion list
    if (not (whitetags == '')):
        if ((movie_played_days >= 0) or (movie_created_days >= 0)):
            deleteItems=get_iswhitetagged_ByMultiUser(movie_whitetag_list, deleteItems)
        if ((episode_played_days >= 0) or (episode_created_days >= 0)):
            deleteItems=get_iswhitetagged_ByMultiUser(episode_whitetag_list, deleteItems)
        if ((audio_played_days >= 0) or (audio_created_days >= 0)):
            deleteItems=get_iswhitetagged_ByMultiUser(audio_whitetag_list, deleteItems)
        if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0))):
            deleteItems=get_iswhitetagged_ByMultiUser(audiobook_whitetag_list, deleteItems)

    if (GLOBAL_DEBUG):
        print_byType('\n-----------------------------------------------------------',False)
        print_byType("\n",False)
        if ((movie_played_days >= 0) or (movie_created_days >= 0)):
            print_byType('\niswhitetag_MOVIE: ',False)
            print_byType("\n" + convert2json(movie_whitetag_list),False)
            print_byType("\n",False)
        if ((episode_played_days >= 0) or (episode_created_days >= 0)):
            print_byType('\niswhitetag_EPISODE: ',False)
            print_byType("\n" + convert2json(episode_whitetag_list),False)
            print_byType("\n",False)
        if ((audio_played_days >= 0) or (audio_created_days >= 0)):
            print_byType('iswhitetag_AUDIO: ',False)
            print_byType(convert2json(audio_whitetag_list),False)
            print_byType('',False)
        if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0))):
            print_byType('\niswhitetag_AUDIOBOOK: ',False)
            print_byType("\n" + convert2json(audiobook_whitetag_list),False)
            print_byType("\n",False)

    #When multiple users and multiuser_whitelist_xyz==0 Determine media items to keep and remove them from deletion list
    if (((movie_played_days >= 0) or (movie_created_days >= 0)) and (multiuser_whitelist_movie == 0)):
        deleteItems=get_iswhitelist_ByMultiUser(movie_whitelists, deleteItems)
    if (((episode_played_days >= 0) or (episode_created_days >= 0)) and (multiuser_whitelist_episode == 0)):
        deleteItems=get_iswhitelist_ByMultiUser(episode_whitelists, deleteItems)
    if (((audio_played_days >= 0) or (audio_created_days >= 0)) and (multiuser_whitelist_audio == 0)):
        deleteItems=get_iswhitelist_ByMultiUser(audio_whitelists, deleteItems)
    if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0)) and (multiuser_whitelist_audiobook == 0)):
        deleteItems=get_iswhitelist_ByMultiUser(audiobook_whitelists, deleteItems)

    if (GLOBAL_DEBUG):
        print_byType('\n-----------------------------------------------------------',False)
        print_byType("\n",False)
        if ((movie_played_days >= 0) or (movie_created_days >= 0)):
            print_byType('\niswhitelist_MOVIE: ',False)
            print_byType(convert2json(movie_whitelists),False)
            print_byType("\n",False)
        if ((episode_played_days >= 0) or (episode_created_days >= 0)):
            print_byType('\niswhitelist_EPISODE: ',False)
            print_byType(convert2json(episode_whitelists),False)
            print_byType("\n",False)
        if ((audio_played_days >= 0) or (audio_created_days >= 0)):
            print_byType('\niswhitelist_AUDIO: ',False)
            print_byType(convert2json(audio_whitelists),False)
            print_byType("\n",False)
        if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0))):
            print_byType('\niswhitelist_AUDIOBOOK: ',False)
            print_byType("\n" + convert2json(audiobook_whitelists),False)
            print_byType("\n",False)

    #When blacktagged; Determine media items to remove them from deletion list depending on cfg.delete_blacktagged_*
    if (((movie_played_days >= 0) or (movie_created_days >= 0)) and (delete_blacktagged_movie == 1)):
        deleteItems=get_isblacktagged_watchedByAllUsers(isblacktag_and_watched_byUserId_Movie, deleteItems)
    if (((episode_played_days >= 0) or (episode_created_days >= 0)) and (delete_blacktagged_episode == 1)):
        deleteItems=get_isblacktagged_watchedByAllUsers(isblacktag_and_watched_byUserId_Episode, deleteItems)
    if (((audio_played_days >= 0) or (audio_created_days >= 0)) and (delete_blacktagged_audio == 1)):
        deleteItems=get_isblacktagged_watchedByAllUsers(isblacktag_and_watched_byUserId_Audio, deleteItems)
    if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0)) and (delete_blacktagged_audiobook == 1)):
        deleteItems=get_isblacktagged_watchedByAllUsers(isblacktag_and_watched_byUserId_AudioBook, deleteItems)

    if (GLOBAL_DEBUG):
        print_byType('\n-----------------------------------------------------------',False)
        print_byType("\n",False)
        if ((movie_played_days >= 0) or (movie_created_days >= 0)):
            print_byType('\nisblacktag_Played_MOVIE: ',False)
            print_byType("\n" + convert2json(isblacktag_and_watched_byUserId_Movie),False)
            print_byType("\n",False)
        if ((episode_played_days >= 0) or (episode_created_days >= 0)):
            print_byType('\nisblacktag_Played_EPISODE: ',False)
            print_byType("\n" + convert2json(isblacktag_and_watched_byUserId_Episode),False)
            print_byType("\n",False)
        if ((audio_played_days >= 0) or (audio_created_days >= 0)):
            print_byType('\nisblacktag_Played_AUDIO: ',False)
            print_byType("\n" + convert2json(isblacktag_and_watched_byUserId_Audio),False)
            print_byType("\n",False)
        if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0))):
            print_byType('\nisblacktag_Played_AUDIOBOOK: ',False)
            print_byType("\n" + convert2json(isblacktag_and_watched_byUserId_AudioBook),False)
            print_byType("\n",False)

    #When filtered; Determine media items to remove them from deletion list depending on cfg.multiuser_play_count_*
    if (((movie_played_days >= 0) or (movie_created_days >= 0)) and (multiuser_play_count_movie == 1)):
        deleteItems=get_isplaycount_MetByAllUsers(isMeeting_PlayCountFilter_Movie, deleteItems)
    if (((episode_played_days >= 0) or (episode_created_days >= 0)) and (multiuser_play_count_episode == 1)):
        deleteItems=get_isplaycount_MetByAllUsers(isMeeting_PlayCountFilter_Episode, deleteItems)
    if (((audio_played_days >= 0) or (audio_created_days >= 0)) and (multiuser_play_count_audio == 1)):
        deleteItems=get_isplaycount_MetByAllUsers(isMeeting_PlayCountFilter_Audio, deleteItems)
    if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0)) and (multiuser_play_count_audiobook == 1)):
        deleteItems=get_isplaycount_MetByAllUsers(isMeeting_PlayCountFilter_AudioBook, deleteItems)

    if (GLOBAL_DEBUG):
        print_byType('\n-----------------------------------------------------------',False)
        print_byType("\n",False)
        if ((movie_played_days >= 0) or (movie_created_days >= 0)):
            print_byType('\nisplaycountmet_MOVIE: ',False)
            print_byType("\n" + convert2json(isMeeting_PlayCountFilter_Movie),False)
            print_byType("\n",False)
        if ((episode_played_days >= 0) or (episode_created_days >= 0)):
            print_byType('\nisplaycountmet_EPISODE: ',False)
            print_byType("\n" + convert2json(isMeeting_PlayCountFilter_Episode),False)
            print_byType("\n",False)
        if ((audio_played_days >= 0) or (audio_created_days >= 0)):
            print_byType('\nisplaycountmet_AUDIO: ',False)
            print_byType("\n" + convert2json(isMeeting_PlayCountFilter_Audio),False)
            print_byType("\n",False)
        if ((server_brand == 'jellyfin') and ((audiobook_played_days >= 0) or (audiobook_created_days >= 0))):
            print_byType('\nisplaycountmet_AUDIOBOOK: ',False)
            print_byType("\n" + convert2json(isMeeting_PlayCountFilter_AudioBook),False)
            print_byType("\n",False)

    #When enabled; Keep a minimum number of episodes
    if (((episode_played_days >= 0) or (episode_created_days >= 0)) and ((minimum_number_episodes >= 1) or (minimum_number_played_episodes >= 1))):
        #Remove episode from deletion list to meet miniumum number of remaining episodes in a series
        deleteItems=get_minEpisodesToKeep(episodeCounts_byUserId, deleteItems)

    if (GLOBAL_DEBUG):
        print_byType('-----------------------------------------------------------',False)
        print_byType('',False)
        if (((episode_played_days >= 0) or (episode_created_days >= 0)) and ((minimum_number_episodes >= 1) or (minimum_number_played_episodes >= 1))):
            print_byType('\nepisodeCounts_byUserId: ',False)
            print_byType("\n" + convert2json(episodeCounts_byUserId),False)
            print_byType("\n",False)

    if (GLOBAL_DEBUG):
        print_byType("\nPOST PROCESSING FINISHED\n",False)
        print_byType("\nFinalized List Of Items To Be Deleted: " + str(len(deleteItems)),False)
        print_byType("\n" + convert2json(deleteItems),False)

    if (GLOBAL_DEBUG):
        print_common_delete_keep_info=True
    print_byType('\n',print_common_delete_keep_info)
    return(deleteItems)


#api call to delete items
def delete_media_item(itemID):

    #build API delete request for specified media item
    url=cfg.server_url + '/Items/' + itemID + '?api_key=' + cfg.auth_key

    req = request.Request(url,method='DELETE')

    if (GLOBAL_DEBUG):
        print_byType("\nSending Delete Request For: " + itemID,False)
        print_byType("\nURL:\n" + url,False)
        print_byType("\nRequest:\n" + str(req),False)

    #check if in dry-run mode
    #if REMOVE_FILES='False'; exit this function
    if not (cfg.REMOVE_FILES):
        return
    #else REMOVE_FILES='True'; send request to Emby/Jellyfin to delete specified media item
    else:
        try:
            request.urlopen(req)
        except Exception:
            print_byType('\ngeneric exception: ' + str(traceback.format_exc()),True)
        return


#list and delete items past played threshold
def output_itemsToDelete(deleteItems):

    print_summary_header=cfg.print_summary_header
    print_movie_summary=cfg.print_movie_summary
    print_episode_summary=cfg.print_episode_summary
    print_audio_summary=cfg.print_audio_summary
    if (cfg.server_brand == 'jellyfin'):
        print_audiobook_summary=cfg.print_audiobook_summary
    else:
        print_audiobook_summary=False

    if (GLOBAL_DEBUG):
        print_summary_header=True
        print_movie_summary=True
        print_episode_summary=True
        print_audio_summary=True
        if (cfg.server_brand == 'jellyfin'):
            print_audiobook_summary=True
        else:
            print_audiobook_summary=False

    print_common_summary = (print_movie_summary or print_episode_summary or print_audio_summary or print_audiobook_summary)

    #List items to be deleted
    print_byType('-----------------------------------------------------------',print_summary_header)
    print_byType('Summary Of Deleted Media:',print_summary_header)
    if not bool(cfg.REMOVE_FILES):
        print_byType('* Trial Run Mode',print_summary_header)
        print_byType('* REMOVE_FILES=\'False\'',print_summary_header)
        print_byType('* No Media Deleted',print_summary_header)
        print_byType('* Items = ' + str(len(deleteItems)),print_summary_header)
        print_byType('-----------------------------------------------------------',print_summary_header)
        print_byType('* To delete media open mumc_config.py in a text editor:',print_summary_header)
        print_byType('*    Set REMOVE_FILES=\'True\'',print_summary_header)
        print_byType('-----------------------------------------------------------',(print_summary_header or print_common_summary))
    else:
        print_byType('* Items Deleted = ' + str(len(deleteItems)) + '    *',print_summary_header)
        print_byType('-----------------------------------------------------------',(print_summary_header or print_common_summary))

    if len(deleteItems) > 0:
        for item in deleteItems:
            if item['Type'] == 'Movie':
                item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                #Delete media item
                delete_media_item(item['Id'])
                #Print output for deleted media item
                print_byType(item_output_details,print_movie_summary)
            elif item['Type'] == 'Episode':
                try:
                    item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'],item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']
                except (KeyError, IndexError):
                    item_output_details='[DELETED]   ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if (GLOBAL_DEBUG):
                        print_byType('Error encountered - Delete Episode: \n\n' + str(item),False)
                #Delete media item
                delete_media_item(item['Id'])
                #Print output for deleted media item
                print_byType(item_output_details,print_episode_summary)
            elif item['Type'] == 'Audio':
                item_output_details='[DELETED]     ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                #Delete media item
                delete_media_item(item['Id'])
                #Print output for deleted media item
                print_byType(item_output_details,print_audio_summary)
            elif item['Type'] == 'AudioBook':
                item_output_details='[DELETED] ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                #Delete media item
                delete_media_item(item['Id'])
                #Print output for deleted media item
                print_byType(item_output_details,print_audiobook_summary)
            else: # item['Type'] == 'Unknown':
                pass
    else:
        print_byType('[NO ITEMS TO DELETE]',print_common_summary)

    print_byType('-----------------------------------------------------------',print_common_summary)
    print_byType('\n',print_common_summary)
    print_byType('-----------------------------------------------------------',print_common_summary)
    print_byType('Done.',print_common_summary)
    print_byType('-----------------------------------------------------------',print_common_summary)
    print_byType('',print_common_summary)


#Check blacklist and whitelist config variables are as expected
def cfgCheck_forLibraries(check_list, userid_check_list, username_check_list, config_var_name):

    error_found_in_mumc_config_py=''

    for check_irt in check_list:
        #Check if userid exists
        if ('userid' in check_irt):
            #Set user tracker to zero
            user_found=0
            #Check user from user_keys is also a user in this blacklist/whitelist
            for user_check in userid_check_list:
                if (user_check in check_irt['userid']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' userid ' + check_irt['userid'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' userid ' + check_irt['userid'] + ' is seen more than once\n'
            #Check userid is string
            if not (isinstance(check_irt['userid'], str)):
                error_found_in_mumc_config_py+='TypeError: In ' + config_var_name + ' the userid is not a string for at least one user\n'
            else:
                #Check userid is 32 character long alphanumeric
                if not (
                    (check_irt['userid'].isalnum()) and
                    (len(check_irt['userid']) == 32)
                ):
                    error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' + at least one userid is not a 32-character alphanumeric string\n'
        else:
            error_found_in_mumc_config_py+='NameError: In ' + config_var_name + ' the userid key is missing for at least one user\n'


        #Check if username exists
        if ('username' in check_irt):
            #Set user tracker to zero
            user_found=0
            #Check user from user_name is also a user in this blacklist/whitelist
            for user_check in username_check_list:
                if (user_check in check_irt['username']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' username ' + check_irt['username'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' username ' + check_irt['username'] + ' is seen more than once\n'
            #Check username is string
            if not (isinstance(check_irt['username'], str)):
                error_found_in_mumc_config_py+='TypeError: In ' + config_var_name + ' the username is not a string for at least one user\n'
        else:
            error_found_in_mumc_config_py+='NameError: In ' + config_var_name + ' the username is missing for at least one user\n'


        #Check if length is >2; which means a userid, username, and at least one library are stored
        if (len(check_irt) > 2):
            #Get number of elements
            for num_elements in check_irt:
                #Ignore userid and username
                if (((not (num_elements == 'userid')) and (not (num_elements == 'username'))) and (int(num_elements) >= 0)):
                    #Set library key trackers to zero
                    libid_found=0
                    collectiontype_found=0
                    networkpath_found=0
                    path_found=0
                    #Check if this num_element exists before proceeding
                    if (num_elements in check_irt):
                        for libinfo in check_irt[num_elements]:
                            if (libinfo == 'libid'):
                                libid_found += 1
                                #Check libid is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_mumc_config_py+='TypeError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the libid for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check libid is 32 character long alphanumeric
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].isalnum()) and
                                        (len(check_irt[str(num_elements)][libinfo]) == 32)
                                    ):
                                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the libid for library with key' + num_elements + ' is not a 32 character alphanumeric string\n'
                            elif (libinfo == 'collectiontype'):
                                collectiontype_found += 1
                                #Check collectiontype is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_mumc_config_py+='TypeError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the collectiontype for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check collectiontype is all alpha characters
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].isalpha())
                                    ):
                                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the collectiontype for library with key' + num_elements + ' is not a 32 character alphanumeric string\n'
                                    else:
                                        #TODO verify we only see specific collection types (i.e. tvshows, movies, music, books, etc...)
                                        pass
                            elif (libinfo == 'networkpath'):
                                networkpath_found += 1
                                #Check networkpath is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_mumc_config_py+='TypeError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the networkpath for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check networkpath has no backslashes
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].find('\\') < 0)
                                    ):
                                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' user ' + check_irt['userid'] + ' the networkpath for library with key' + num_elements + ' cannot have any forward slashes \'\\\'\n'
                            elif (libinfo == 'path'):
                                path_found += 1
                                #Check path is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_mumc_config_py+='TypeError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the path for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check path has no backslashes
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].find('\\') < 0)
                                    ):
                                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the path for library with key' + num_elements + ' cannot have any backslashes \'\\\'\n'
                        if (libid_found == 0):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key libid is missing\n'
                        if (libid_found > 1):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key libid is seen more than once\n'
                        if (collectiontype_found == 0):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key collectiontype is missing\n'
                        if (collectiontype_found > 1):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key collectiontype is seen more than once\n'
                        if (networkpath_found == 0):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key networkpath is missing\n'
                        if (networkpath_found > 1):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key networkpath is seen more than once\n'
                        if (path_found == 0):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key path is missing\n'
                        if (path_found > 1):
                            error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key path is seen more than once\n'
                    else:
                        error_found_in_mumc_config_py+='ValueError: In ' + config_var_name + ' user ' + check_irt['userid'] + ' key'+ str(num_elements) +' does not exist\n'
    return(error_found_in_mumc_config_py)


#Check select config variables are as expected
def cfgCheck():

    if hasattr(cfg, 'server_brand'):
        server_brand=cfg.server_brand
    else:
        server_brand='invalid'
    error_found_in_mumc_config_py=''
    #Todo: find clean way to put cfg.variable_names in a dict/list/etc... and use the dict/list/etc... to call the varibles by name in a for loop
    if (GLOBAL_DEBUG):
        #Double newline for debug log formatting
        print_byType("\n\nserver_brand='" + server_brand + "'",False)

#######################################################################################################

    if hasattr(cfg, 'user_keys'):
        check=cfg.user_keys
        check_list=json.loads(check)
        if (GLOBAL_DEBUG):
            print_byType("\nuser_keys=" + convert2json(check_list),False)
        check_user_keys_length=len(check_list)
        username_check_list=[]
        userid_check_list=[]
        for user_info in check_list:
            username_check_list.append(user_info.split(':',1)[0])
            userid_check_list.append(user_info.split(':',1)[1])
            for check_irt in userid_check_list:
                if (
                    not ((type(check_irt) is str) and
                    (len(check_irt) == 32) and
                    (str(check_irt).isalnum()))
                ):
                    error_found_in_mumc_config_py+='ValueError: user_keys must be a single list with a dictionary entry for each monitored UserName:UserId\' each user key must be a 32-character alphanumeric string\n'
    else:
        error_found_in_mumc_config_py+='NameError: The user_keys variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'movie_played_days'):
        check=cfg.movie_played_days
        if (GLOBAL_DEBUG):
            print_byType("\nmovie_played_days=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: movie_played_days must be an integer; valid range -1 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The movie_played_days variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'episode_played_days'):
        check=cfg.episode_played_days
        if (GLOBAL_DEBUG):
            print_byType("\nepisode_played_days=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: episode_played_days must be an integer; valid range -1 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The episode_played_days variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'audio_played_days'):
        check=cfg.audio_played_days
        if (GLOBAL_DEBUG):
            print_byType("\naudio_played_days=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: audio_played_days must be an integer; valid range -1 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The audio_played_days variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'audiobook_played_days'):
            check=cfg.audiobook_played_days
            if (GLOBAL_DEBUG):
                print_byType("\naudiobook_played_days=" + str(check),False)
            if (
                not ((type(check) is int) and
                (check >= -1) and
                (check <= 730500))
            ):
                error_found_in_mumc_config_py+='ValueError: audiobook_played_days must be an integer; valid range -1 thru 730500\n'
        else:
            error_found_in_mumc_config_py+='NameError: The audiobook_played_days variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'movie_created_days'):
        check=cfg.movie_created_days
        if (GLOBAL_DEBUG):
            print_byType("\nmovie_created_days=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: movie_created_days must be an integer; valid range -1 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The movie_created_days variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'episode_created_days'):
        check=cfg.episode_created_days
        if (GLOBAL_DEBUG):
            print_byType("\nepisode_created_days=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: episode_created_days must be an integer; valid range -1 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The episode_created_days variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'audio_created_days'):
        check=cfg.audio_created_days
        if (GLOBAL_DEBUG):
            print_byType("\naudio_created_days=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: audio_created_days must be an integer; valid range -1 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The audio_created_days variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'audiobook_created_days'):
            check=cfg.audiobook_created_days
            if (GLOBAL_DEBUG):
                print_byType("\naudiobook_created_days=" + str(check),False)
            if (
                not ((type(check) is int) and
                (check >= -1) and
                (check <= 730500))
            ):
                error_found_in_mumc_config_py+='ValueError: audiobook_created_days must be an integer; valid range -1 thru 730500\n'
        else:
            error_found_in_mumc_config_py+='NameError: The audiobook_created_days variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'movie_played_count_comparison'):
        check=cfg.movie_played_count_comparison
        if (GLOBAL_DEBUG):
            print_byType("\nmovie_played_count_comparison='" + str(check) + "'",False)
        if (
            not ((type(check) is str) and
            ((check == '>') or (check == '<') or
            (check == '>=') or (check == '<=') or
            (check == '==') or
            (check == 'not >') or (check == 'not <') or
            (check == 'not >=') or (check == 'not <=') or
            (check == 'not ==')))
        ):
            error_found_in_mumc_config_py+='ValueError: movie_played_count_comparison must be string; any \'nots\' must be all lower case; valid values \'>\', \'<\', \'>=\', \'<=\, \'==\', \'not >\', \'not <\', \'not >=\', \'not <=\', and \'not ==\'\n'
    else:
        error_found_in_mumc_config_py+='NameError: The movie_played_count_comparison variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'episode_played_count_comparison'):
        check=cfg.episode_played_count_comparison
        if (GLOBAL_DEBUG):
            print_byType("\nepisode_played_count_comparison='" + str(check) + "'",False)
        if (
            not ((type(check) is str) and
            ((check == '>') or (check == '<') or
            (check == '>=') or (check == '<=') or
            (check == '==') or
            (check == 'not >') or (check == 'not <') or
            (check == 'not >=') or (check == 'not <=') or
            (check == 'not ==')))
        ):
            error_found_in_mumc_config_py+='ValueError: episode_played_count_comparison must be string; any \'nots\' must be all lower case; valid values \'>\', \'<\', \'>=\', \'<=\, \'==\', \'not >\', \'not <\', \'not >=\', \'not <=\', and \'not ==\'\n'
    else:
        error_found_in_mumc_config_py+='NameError: The episode_played_count_comparison variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'audio_played_count_comparison'):
        check=cfg.audio_played_count_comparison
        if (GLOBAL_DEBUG):
            print_byType("\naudio_played_count_comparison='" + str(check) + "'",False)
        if (
            not ((type(check) is str) and
            ((check == '>') or (check == '<') or
            (check == '>=') or (check == '<=') or
            (check == '==') or
            (check == 'not >') or (check == 'not <') or
            (check == 'not >=') or (check == 'not <=') or
            (check == 'not ==')))
        ):
            error_found_in_mumc_config_py+='ValueError: audio_played_count_comparison must be string; any \'nots\' must be all lower case; valid values \'>\', \'<\', \'>=\', \'<=\, \'==\', \'not >\', \'not <\', \'not >=\', \'not <=\', and \'not ==\'\n'
    else:
        error_found_in_mumc_config_py+='NameError: The audio_played_count_comparison variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'audiobook_played_count_comparison'):
            check=cfg.audiobook_played_count_comparison
            if (GLOBAL_DEBUG):
                print_byType("\naudiobook_played_count_comparison='" + str(check) + "'",False)
            if (
                not ((type(check) is str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=') or
                (check == 'not ==')))
            ):
                error_found_in_mumc_config_py+='ValueError: audiobook_played_count_comparison must be string; any \'nots\' must be all lower case; valid values \'>\', \'<\', \'>=\', \'<=\, \'==\', \'not >\', \'not <\', \'not >=\', \'not <=\', and \'not ==\'\n'
        else:
            error_found_in_mumc_config_py+='NameError: The audiobook_played_count_comparison variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'movie_created_played_count_comparison'):
        check=cfg.movie_created_played_count_comparison
        if (GLOBAL_DEBUG):
            print_byType("\nmovie_created_played_count_comparison='" + str(check) + "'",False)
        if (
            not ((type(check) is str) and
            ((check == '>') or (check == '<') or
            (check == '>=') or (check == '<=') or
            (check == '==') or
            (check == 'not >') or (check == 'not <') or
            (check == 'not >=') or (check == 'not <=') or
            (check == 'not ==')))
        ):
            error_found_in_mumc_config_py+='ValueError: movie_created_played_count_comparison must be string; any \'nots\' must be all lower case; valid values \'>\', \'<\', \'>=\', \'<=\, \'==\', \'not >\', \'not <\', \'not >=\', \'not <=\', and \'not ==\'\n'
    else:
        error_found_in_mumc_config_py+='NameError: The movie_created_played_count_comparison variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'episode_created_played_count_comparison'):
        check=cfg.episode_created_played_count_comparison
        if (GLOBAL_DEBUG):
            print_byType("\nepisode_created_played_count_comparison='" + str(check) + "'",False)
        if (
            not ((type(check) is str) and
            ((check == '>') or (check == '<') or
            (check == '>=') or (check == '<=') or
            (check == '==') or
            (check == 'not >') or (check == 'not <') or
            (check == 'not >=') or (check == 'not <=') or
            (check == 'not ==')))
        ):
            error_found_in_mumc_config_py+='ValueError: episode_created_played_count_comparison must be string; any \'nots\' must be all lower case; valid values \'>\', \'<\', \'>=\', \'<=\, \'==\', \'not >\', \'not <\', \'not >=\', \'not <=\', and \'not ==\'\n'
    else:
        error_found_in_mumc_config_py+='NameError: The episode_created_played_count_comparison variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'audio_created_played_count_comparison'):
        check=cfg.audio_created_played_count_comparison
        if (GLOBAL_DEBUG):
            print_byType("\naudio_created_played_count_comparison='" + str(check) + "'",False)
        if (
            not ((type(check) is str) and
            ((check == '>') or (check == '<') or
            (check == '>=') or (check == '<=') or
            (check == '==') or
            (check == 'not >') or (check == 'not <') or
            (check == 'not >=') or (check == 'not <=') or
            (check == 'not ==')))
        ):
            error_found_in_mumc_config_py+='ValueError: audio_created_played_count_comparison must be string; any \'nots\' must be all lower case; valid values \'>\', \'<\', \'>=\', \'<=\, \'==\', \'not >\', \'not <\', \'not >=\', \'not <=\', and \'not ==\'\n'
    else:
        error_found_in_mumc_config_py+='NameError: The audio_created_played_count_comparison variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'audiobook_created_played_count_comparison'):
            check=cfg.audiobook_created_played_count_comparison
            if (GLOBAL_DEBUG):
                print_byType("\naudiobook_created_played_count_comparison='" + str(check) + "'",False)
            if (
                not ((type(check) is str) and
                ((check == '>') or (check == '<') or
                (check == '>=') or (check == '<=') or
                (check == '==') or
                (check == 'not >') or (check == 'not <') or
                (check == 'not >=') or (check == 'not <=') or
                (check == 'not ==')))
            ):
                error_found_in_mumc_config_py+='ValueError: audiobook_created_played_count_comparison must be string; any \'nots\' must be all lower case; valid values \'>\', \'<\', \'>=\', \'<=\, \'==\', \'not >\', \'not <\', \'not >=\', \'not <=\', and \'not ==\'\n'
        else:
            error_found_in_mumc_config_py+='NameError: The audiobook_created_played_count_comparison variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'movie_played_count'):
        check=cfg.movie_played_count
        if (GLOBAL_DEBUG):
            print_byType("\nmovie_played_count=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: movie_played_count must be an integer; valid range 0 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The movie_played_count variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'episode_played_count'):
        check=cfg.episode_played_count
        if (GLOBAL_DEBUG):
            print_byType("\nepisode_played_count=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: episode_played_count must be an integer; valid range 0 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The episode_played_count variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'audio_played_count'):
        check=cfg.audio_played_count
        if (GLOBAL_DEBUG):
            print_byType("\naudio_played_count=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: audio_played_count must be an integer; valid range 0 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The audio_played_count variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'audiobook_played_count'):
            check=cfg.audiobook_played_count
            if (GLOBAL_DEBUG):
                print_byType("\naudiobook_played_count=" + str(check),False)
            if (
                not ((type(check) is int) and
                (check >= 0) and
                (check <= 730500))
            ):
                error_found_in_mumc_config_py+='ValueError: audiobook_played_count must be an integer; valid range 0 thru 730500\n'
        else:
            error_found_in_mumc_config_py+='NameError: The audiobook_played_count variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'movie_created_played_count'):
        check=cfg.movie_created_played_count
        if (GLOBAL_DEBUG):
            print_byType("\nmovie_created_played_count=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: movie_created_played_count must be an integer; valid range 0 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The movie_created_played_count variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'episode_created_played_count'):
        check=cfg.episode_created_played_count
        if (GLOBAL_DEBUG):
            print_byType("\nepisode_created_played_count=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: episode_created_played_count must be an integer; valid range 0 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The episode_created_played_count variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'audio_created_played_count'):
        check=cfg.audio_created_played_count
        if (GLOBAL_DEBUG):
            print_byType("\naudio_created_played_count=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: audio_created_played_count must be an integer; valid range 0 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The audio_created_played_count variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'audiobook_created_played_count'):
            check=cfg.audiobook_created_played_count
            if (GLOBAL_DEBUG):
                print_byType("\naudiobook_created_played_count=" + str(check),False)
            if (
                not ((type(check) is int) and
                (check >= 0) and
                (check <= 730500))
            ):
                error_found_in_mumc_config_py+='ValueError: audiobook_created_played_count must be an integer; valid range 0 thru 730500\n'
        else:
            error_found_in_mumc_config_py+='NameError: The audiobook_created_played_count variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'multiuser_play_count_movie'):
        check=cfg.multiuser_play_count_movie
        if (GLOBAL_DEBUG):
            print_byType("\nmultiuser_play_count_movie=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_mumc_config_py+='ValueError: multiuser_play_count_movie must be an integer; valid values 0 and 1\n'
    else:
        error_found_in_mumc_config_py+='NameError: The multiuser_play_count_movie variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'multiuser_play_count_episode'):
        check=cfg.multiuser_play_count_episode
        if (GLOBAL_DEBUG):
            print_byType("\nmultiuser_play_count_episode=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_mumc_config_py+='ValueError: multiuser_play_count_episode must be an integer; valid values 0 and 1\n'
    else:
        error_found_in_mumc_config_py+='NameError: The multiuser_play_count_episode variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'multiuser_play_count_audio'):
        check=cfg.multiuser_play_count_audio
        if (GLOBAL_DEBUG):
            print_byType("\nmultiuser_play_count_audio=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_mumc_config_py+='ValueError: multiuser_play_count_audio must be an integer; valid values 0 and 1\n'
    else:
        error_found_in_mumc_config_py+='NameError: The multiuser_play_count_audio variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'multiuser_play_count_audiobook'):
            check=cfg.multiuser_play_count_audiobook
            if (GLOBAL_DEBUG):
                print_byType("\nmultiuser_play_count_audiobook=" + str(check),False)
            if (
                not ((type(check) is int) and
                (check >= 0) and
                (check <= 1))
            ):
                error_found_in_mumc_config_py+='ValueError: multiuser_play_count_audiobook must be an integer; valid values 0 and 1\n'
        else:
            error_found_in_mumc_config_py+='NameError: The multiuser_play_count_audiobook variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'keep_favorites_movie'):
        check=cfg.keep_favorites_movie
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_movie=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_movie must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_movie variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_episode'):
        check=cfg.keep_favorites_episode
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_episode=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_episode must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_episode variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_audio'):
        check=cfg.keep_favorites_audio
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_audio=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_audio must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_audio variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'keep_favorites_audiobook'):
            check=cfg.keep_favorites_audiobook
            if (GLOBAL_DEBUG):
                print_byType("\nkeep_favorites_audiobook=" + str(check),False)
            if (
                not ((type(check) is int) and
                (check >= 0) and
                (check <= 2))
            ):
                error_found_in_mumc_config_py+='ValueError: keep_favorites_audiobook must be an integer; valid range 0 thru 2\n'
        else:
            error_found_in_mumc_config_py+='NameError: The keep_favorites_audiobook variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'multiuser_whitelist_movie'):
        check=cfg.multiuser_whitelist_movie
        if (GLOBAL_DEBUG):
            print_byType("\nmultiuser_whitelist_movie=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_mumc_config_py+='ValueError: multiuser_whitelist_movie must be an integer;valid values 0 and 1\n'
    else:
        error_found_in_mumc_config_py+='NameError: The multiuser_whitelist_movie variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'multiuser_whitelist_episode'):
        check=cfg.multiuser_whitelist_episode
        if (GLOBAL_DEBUG):
            print_byType("\nmultiuser_whitelist_episode=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_mumc_config_py+='ValueError: multiuser_whitelist_episode must be an integer;valid values 0 and 1\n'
    else:
        error_found_in_mumc_config_py+='NameError: The multiuser_whitelist_episode variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'multiuser_whitelist_audio'):
        check=cfg.multiuser_whitelist_audio
        if (GLOBAL_DEBUG):
            print_byType("\nmultiuser_whitelist_audio=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_mumc_config_py+='ValueError: multiuser_whitelist_audio must be an integer;valid values 0 and 1\n'
    else:
        error_found_in_mumc_config_py+='NameError: The multiuser_whitelist_audio variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'multiuser_whitelist_audiobook'):
            check=cfg.multiuser_whitelist_audiobook
            if (GLOBAL_DEBUG):
                print_byType("\nmultiuser_whitelist_audiobook=" + str(check),False)
            if (
                not ((type(check) is int) and
                (check >= 0) and
                (check <= 1))
            ):
                error_found_in_mumc_config_py+='ValueError: multiuser_whitelist_audiobook must be an integer;valid values 0 and 1\n'
        else:
            error_found_in_mumc_config_py+='NameError: The multiuser_whitelist_audiobook variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'blacktag'):
        check=cfg.blacktag
        if (GLOBAL_DEBUG):
            print_byType("\nblacktag='" + str(check) + "'",False)
        if not (
            (type(check) is str) and
            (check.find('\\') < 0)
        ):
            error_found_in_mumc_config_py+='ValueError: Blacktag(s) must be a single string with a comma separating multiple tag names; backlash \'\\\' not allowed\n'
    else:
        error_found_in_mumc_config_py+='NameError: The blacktag variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'delete_blacktagged_movie'):
        check=cfg.delete_blacktagged_movie
        if (GLOBAL_DEBUG):
            print_byType("\ndelete_blacktagged_movie=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_mumc_config_py+='ValueError: delete_blacktagged_movie must be an integer;valid values 0 and 1\n'
    else:
        error_found_in_mumc_config_py+='NameError: The delete_blacktagged_movie variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'delete_blacktagged_episode'):
        check=cfg.delete_blacktagged_episode
        if (GLOBAL_DEBUG):
            print_byType("\ndelete_blacktagged_episode=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_mumc_config_py+='ValueError: delete_blacktagged_episode must be an integer;valid values 0 and 1\n'
    else:
        error_found_in_mumc_config_py+='NameError: The delete_blacktagged_episode variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'delete_blacktagged_audio'):
        check=cfg.delete_blacktagged_audio
        if (GLOBAL_DEBUG):
            print_byType("\ndelete_blacktagged_audio=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_mumc_config_py+='ValueError: delete_blacktagged_audio must be an integer;valid values 0 and 1\n'
    else:
        error_found_in_mumc_config_py+='NameError: The delete_blacktagged_audio variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'delete_blacktagged_audiobook'):
            check=cfg.delete_blacktagged_audiobook
            if (GLOBAL_DEBUG):
                print_byType("\ndelete_blacktagged_audiobook=" + str(check),False)
            if (
                not ((type(check) is int) and
                (check >= 0) and
                (check <= 1))
            ):
                error_found_in_mumc_config_py+='ValueError: delete_blacktagged_audiobook must be an integer;valid values 0 and 1\n'
        else:
            error_found_in_mumc_config_py+='NameError: The delete_blacktagged_audiobook variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'whitetag'):
        check=cfg.whitetag
        if (GLOBAL_DEBUG):
            print_byType("\nwhitetag='" + str(check) + "'",False)
        if not (
            (type(check) is str) and
            (check.find('\\') < 0)
        ):
            error_found_in_mumc_config_py+='ValueError: Whitetag(s) must be a single string with a comma separating multiple tag names; backlash \'\\\' not allowed\n'
    else:
        error_found_in_mumc_config_py+='NameError: The whitetag variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'minimum_number_episodes'):
        check=cfg.minimum_number_episodes
        if (GLOBAL_DEBUG):
            print_byType("\nminimum_number_episodes=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: minimum_number_episodes must be an integer; valid range 0 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The minimum_number_episodes variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'minimum_number_played_episodes'):
        check=cfg.minimum_number_played_episodes
        if (GLOBAL_DEBUG):
            print_byType("\nminimum_number_played_episodes=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 730500))
        ):
            error_found_in_mumc_config_py+='ValueError: minimum_number_played_episodes must be an integer; valid range 0 thru 730500\n'
    else:
        error_found_in_mumc_config_py+='NameError: The minimum_number_played_episodes variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'minimum_number_episodes_behavior'):
        check=cfg.minimum_number_episodes_behavior
        if (GLOBAL_DEBUG):
            print_byType("\nminimum_number_episodes_behavior='" + str(check) + "'",False)
        check=check.casefold()
        usersname_usersid_match=False
        for usersname in username_check_list:
            if (check == usersname.casefold()):
                usersname_usersid_match=True
        for usersid in userid_check_list:
            if (check == usersid.casefold()):
                usersname_usersid_match=True
        if (usersname_usersid_match == False):
            check = check.replace(' ','')
        if (
            not ((type(check) is str) and
            ((usersname_usersid_match == True) or
            (check == 'maxplayed') or
            (check == 'maxplayedmaxplayed') or
            (check == 'minplayed') or
            (check == 'minplayedminplayed') or
            (check == 'maxunplayed') or
            (check == 'maxunplayedmaxunplayed') or
            (check == 'minunplayed') or
            (check == 'minunplayedminunplayed') or
            (check == 'maxplayedmaxunplayed') or
            (check == 'minplayedminunplayed') or
            (check == 'maxplayedminunplayed') or
            (check == 'minplayedmaxunplayed') or
            (check == 'minunplayedminplayed') or
            (check == 'minunplayedmaxunplayed') or
            (check == 'minunplayedmaxplayed') or
            (check == 'minplayedmaxplayed') or
            (check == 'maxunplayedminunplayed') or
            (check == 'maxunplayedminplayed') or
            (check == 'maxunplayedmaxplayed') or
            (check == 'maxplayedminplayed')))
        ):
            error_found_in_mumc_config_py+='ValueError: minimum_number_episodes_behavior must be a string; valid values \'User Name\', \'User Id\', and \'Min/Max Played/Unplayed\'\n'
    else:
        error_found_in_mumc_config_py+='NameError: The minimum_number_episodes_behavior variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'REMOVE_FILES'):
        check=cfg.REMOVE_FILES
        if (GLOBAL_DEBUG):
            print_byType("\nREMOVE_FILES='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: REMOVE_FILES must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The REMOVE_FILES variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'keep_favorites_advanced_movie_genre'):
        check=cfg.keep_favorites_advanced_movie_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_movie_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_movie_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_movie_genre variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_movie_library_genre'):
        check=cfg.keep_favorites_advanced_movie_library_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_movie_library_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_movie_library_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_movie_library_genre variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'keep_favorites_advanced_episode_genre'):
        check=cfg.keep_favorites_advanced_episode_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_episode_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_episode_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_episode_genre variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_season_genre'):
        check=cfg.keep_favorites_advanced_season_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_season_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_season_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_season_genre variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_series_genre'):
        check=cfg.keep_favorites_advanced_series_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_series_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_series_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_series_genre variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_tv_library_genre'):
        check=cfg.keep_favorites_advanced_tv_library_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_tv_library_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_tv_library_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_tv_library_genre variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_tv_studio_network'):
        check=cfg.keep_favorites_advanced_tv_studio_network
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_tv_studio_network=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_tv_studio_network must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_tv_studio_network variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_tv_studio_network_genre'):
        check=cfg.keep_favorites_advanced_tv_studio_network_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_tv_studio_network_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_tv_studio_network_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_tv_studio_network_genre variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'keep_favorites_advanced_track_genre'):
        check=cfg.keep_favorites_advanced_track_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_track_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_track_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_track_genre variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_album_genre'):
        check=cfg.keep_favorites_advanced_album_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_album_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_album_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_album_genre variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_music_library_genre'):
        check=cfg.keep_favorites_advanced_music_library_genre
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_music_library_genre=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_music_library_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_music_library_genre variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_track_artist'):
        check=cfg.keep_favorites_advanced_track_artist
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_track_artist=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_track_artist must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_track_artist variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_album_artist'):
        check=cfg.keep_favorites_advanced_album_artist
        if (GLOBAL_DEBUG):
            print_byType("\nkeep_favorites_advanced_album_artist=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_album_artist must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_album_artist variable is missing from mumc_config.py\n'

#######################################################################################################

    if (server_brand == 'jellyfin'):
            if hasattr(cfg, 'keep_favorites_advanced_audio_book_track_genre'):
                check=cfg.keep_favorites_advanced_audio_book_track_genre
                if (GLOBAL_DEBUG):
                    print_byType("\nkeep_favorites_advanced_audio_book_track_genre=" + str(check),False)
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_audio_book_track_genre must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_audio_book_track_genre variable is missing from mumc_config.py\n'

            if hasattr(cfg, 'keep_favorites_advanced_audio_book_genre'):
                check=cfg.keep_favorites_advanced_audio_book_genre
                if (GLOBAL_DEBUG):
                    print_byType("\nkeep_favorites_advanced_audio_book_track_genre=" + str(check),False)
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_audio_book_genre must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_audio_book_genre variable is missing from mumc_config.py\n'

            if hasattr(cfg, 'keep_favorites_advanced_audio_book_library_genre'):
                check=cfg.keep_favorites_advanced_audio_book_library_genre
                if (GLOBAL_DEBUG):
                    print_byType("\nkeep_favorites_advanced_audio_book_library_genre=" + str(check),False)
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_audio_book_library_genre must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_audio_book_library_genre variable is missing from mumc_config.py\n'

            if hasattr(cfg, 'keep_favorites_advanced_audio_book_track_author'):
                check=cfg.keep_favorites_advanced_audio_book_track_author
                if (GLOBAL_DEBUG):
                    print_byType("\nkeep_favorites_advanced_audio_book_track_author=" + str(check),False)
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_audio_book_track_author must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_audio_book_track_author variable is missing from mumc_config.py\n'

            if hasattr(cfg, 'keep_favorites_advanced_audio_book_author'):
                check=cfg.keep_favorites_advanced_audio_book_author
                if (GLOBAL_DEBUG):
                    print_byType("\nkeep_favorites_advanced_audio_book_author=" + str(check),False)
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_mumc_config_py+='ValueError: keep_favorites_advanced_audio_book_author must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_mumc_config_py+='NameError: The keep_favorites_advanced_audio_book_author variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'print_script_header'):
        check=cfg.print_script_header
        if (GLOBAL_DEBUG):
            print_byType("\nprint_script_header='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_script_header must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_script_header variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_warnings'):
        check=cfg.print_warnings
        if (GLOBAL_DEBUG):
            print_byType("\nprint_warnings='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_warnings must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_warnings variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_user_header'):
        check=cfg.print_user_header
        if (GLOBAL_DEBUG):
            print_byType("\nprint_user_header='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_user_header must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_user_header variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_movie_delete_info'):
        check=cfg.print_movie_delete_info
        if (GLOBAL_DEBUG):
            print_byType("\nprint_movie_delete_info='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_movie_delete_info must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_movie_delete_info variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_movie_keep_info'):
        check=cfg.print_movie_keep_info
        if (GLOBAL_DEBUG):
            print_byType("\nprint_movie_keep_info='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_movie_keep_info must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_movie_keep_info variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_episode_delete_info'):
        check=cfg.print_episode_delete_info
        if (GLOBAL_DEBUG):
            print_byType("\nprint_episode_delete_info='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_episode_delete_info must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_episode_delete_info variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_episode_keep_info'):
        check=cfg.print_episode_keep_info
        if (GLOBAL_DEBUG):
            print_byType("\nprint_episode_keep_info='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_episode_keep_info must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_episode_keep_info variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_audio_delete_info'):
        check=cfg.print_audio_delete_info
        if (GLOBAL_DEBUG):
            print_byType("\nprint_audio_delete_info='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_audio_delete_info must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_audio_delete_info variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_audio_keep_info'):
        check=cfg.print_audio_keep_info
        if (GLOBAL_DEBUG):
            print_byType("\nprint_audio_keep_info='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_audio_keep_info must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_audio_keep_info variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'print_audiobook_delete_info'):
            check=cfg.print_audiobook_delete_info
            if (GLOBAL_DEBUG):
                print_byType("\nprint_audiobook_delete_info='" + str(check) + "'",False)
            if (
                not ((type(check) is bool) and
                ((check == True) or
                (check == False)))
            ):
                error_found_in_mumc_config_py+='ValueError: print_audiobook_delete_info must be a boolean; valid values True and False\n'
        else:
            error_found_in_mumc_config_py+='NameError: The print_audiobook_delete_info variable is missing from mumc_config.py\n'

        if hasattr(cfg, 'print_audiobook_keep_info'):
            check=cfg.print_audiobook_keep_info
            if (GLOBAL_DEBUG):
                print_byType("\nprint_audiobook_keep_info='" + str(check) + "'",False)
            if (
                not ((type(check) is bool) and
                ((check == True) or
                (check == False)))
            ):
                error_found_in_mumc_config_py+='ValueError: print_audiobook_keep_info must be a boolean; valid values True and False\n'
        else:
            error_found_in_mumc_config_py+='NameError: The print_audiobook_keep_info variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_summary_header'):
        check=cfg.print_summary_header
        if (GLOBAL_DEBUG):
            print_byType("\nprint_summary_header='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_summary_header must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_summary_header variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_movie_summary'):
        check=cfg.print_movie_summary
        if (GLOBAL_DEBUG):
            print_byType("\nprint_movie_summary='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_movie_summary must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_movie_summary variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_episode_summary'):
        check=cfg.print_episode_summary
        if (GLOBAL_DEBUG):
            print_byType("\nprint_episode_summary='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_episode_summary must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_episode_summary variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'print_audio_summary'):
        check=cfg.print_audio_summary
        if (GLOBAL_DEBUG):
            print_byType("\nprint_audio_summary='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: print_audio_summary must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The print_audio_summary variable is missing from mumc_config.py\n'

    if (server_brand == 'jellyfin'):
        if hasattr(cfg, 'print_audiobook_summary'):
            check=cfg.print_audiobook_summary
            if (GLOBAL_DEBUG):
                print_byType("\nprint_audiobook_summary='" + str(check) + "'",False)
            if (
                not ((type(check) is bool) and
                ((check == True) or
                (check == False)))
            ):
                error_found_in_mumc_config_py+='ValueError: print_audiobook_summary must be a boolean; valid values True and False\n'
        else:
            error_found_in_mumc_config_py+='NameError: The print_audiobook_summary variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'UPDATE_CONFIG'):
        check=cfg.UPDATE_CONFIG
        if (GLOBAL_DEBUG):
            print_byType("\nUPDATE_CONFIG='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: UPDATE_CONFIG must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The UPDATE_CONFIG variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (GLOBAL_DEBUG):
            print_byType("\nserver_brand='" + str(check) + "'",False)
        if (
            not ((type(check) is str) and
            ((check == 'emby') or
            (check == 'jellyfin')))
        ):
            error_found_in_mumc_config_py+='ValueError: server_brand must be a string with a value of \'emby\' or \'jellyfin\'\n'
    else:
        error_found_in_mumc_config_py+='NameError: The server_brand variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'server_url'):
        check=cfg.server_url
        if (GLOBAL_DEBUG):
            print_byType("\nserver_url='" + str(check) + "'",False)
        if (
            not (type(check) is str)
        ):
            error_found_in_mumc_config_py+='ValueError: server_url must be a string\n'
    else:
        error_found_in_mumc_config_py+='NameError: The server_url variable is missing from mumc_config.py\n'

    if hasattr(cfg, 'auth_key'):
        check=cfg.auth_key
        if (GLOBAL_DEBUG):
            print_byType("\nauth_key='" + str(check) + "'",False)
        if (
            not ((type(check) is str) and
            (len(check) == 32) and
            (str(check).isalnum()))
        ):
            error_found_in_mumc_config_py+='ValueError: auth_key must be a 32-character alphanumeric string\n'
    else:
        error_found_in_mumc_config_py+='NameError: The auth_key variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'library_setup_behavior'):
        check=cfg.library_setup_behavior
        if (GLOBAL_DEBUG):
            print_byType("\nlibrary_setup_behavior='" + str(check) + "'",False)
        if (
            not (type(check) is str) and
            ((check == 'blacklist') or (check == 'whitelist'))
        ):
            error_found_in_mumc_config_py+='ValueError: library_setup_behavior must be a string; valid values \'blacklist\' or \'whitelist\'\n'
    else:
        error_found_in_mumc_config_py+='NameError: The library_setup_behavior variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'library_matching_behavior'):
        check=cfg.library_matching_behavior
        if (GLOBAL_DEBUG):
            print_byType("\nlibrary_matching_behavior='" + str(check) + "'",False)
        if (
            not (type(check) is str) and
            ((check == 'byId') or (check == 'byPath') or (check == 'byNetworkPath'))
        ):
            error_found_in_mumc_config_py+='ValueError: library_matching_behavior must be a string; valid values \'byId\' or \'byPath\' or \'byNetworkPath\'; I, P, and/or N must be uppercase letters\n'
    else:
        error_found_in_mumc_config_py+='NameError: The library_matching_behavior variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'user_bl_libs'):
        check=cfg.user_bl_libs
        check_list=json.loads(check)
        if (GLOBAL_DEBUG):
            print_byType("\nuser_bl_libs=" + convert2json(check_list),False)
        check_user_bllibs_length=len(check_list)
        #Check number of users matches the number of blacklist entries
        if not (check_user_bllibs_length == check_user_keys_length):
            error_found_in_mumc_config_py+='ValueError: Number of configured users does not match the number of configured blacklists\n'
        else:
            error_found_in_mumc_config_py+=cfgCheck_forLibraries(check_list, userid_check_list, username_check_list, 'user_bl_libs')

#######################################################################################################

    if hasattr(cfg, 'user_wl_libs'):
        check=cfg.user_wl_libs
        check_list=json.loads(check)
        if (GLOBAL_DEBUG):
            print_byType("\nuser_wl_libs=" + convert2json(check_list),False)
        check_user_wllibs_length=len(check_list)
        #Check number of users matches the number of whitelist entries
        if not (check_user_wllibs_length == check_user_keys_length):
            error_found_in_mumc_config_py+='ValueError: Number of configured users does not match the number of configured whitelists\n'
        else:
            error_found_in_mumc_config_py+=cfgCheck_forLibraries(check_list, userid_check_list, username_check_list, 'user_wl_libs')

#######################################################################################################

    if hasattr(cfg, 'api_query_attempts'):
        check=cfg.api_query_attempts
        if (GLOBAL_DEBUG):
            print_byType("\napi_query_attempts=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 16))
        ):
            error_found_in_mumc_config_py+='ValueError: api_query_attempts must be an integer; valid range 0 thru 16\n'
    else:
        error_found_in_mumc_config_py+='NameError: The api_query_attempts variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'api_query_item_limit'):
        check=cfg.api_query_item_limit
        if (GLOBAL_DEBUG):
            print_byType("\napi_query_item_limit=" + str(check),False)
        if (
            not ((type(check) is int) and
            (check >= 1) and
            (check <= 10000))
        ):
            error_found_in_mumc_config_py+='ValueError: api_query_item_limit must be an integer; valid range 0 thru 10000\n'
    else:
        error_found_in_mumc_config_py+='NameError: The api_query_item_limit variable is missing from mumc_config.py\n'

#######################################################################################################

    if hasattr(cfg, 'DEBUG'):
        check=cfg.DEBUG
        if (GLOBAL_DEBUG):
            print_byType("\nDEBUG='" + str(check) + "'",False)
        if (
            not ((type(check) is bool) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_mumc_config_py+='ValueError: DEBUG must be a boolean; valid values True and False\n'
    else:
        error_found_in_mumc_config_py+='NameError: The DEBUG variable is missing from mumc_config.py\n'

#######################################################################################################

    #Bring all errors found to users attention
    if not (error_found_in_mumc_config_py == ''):
        if (GLOBAL_DEBUG):
            print_byType("\n" + error_found_in_mumc_config_py,GLOBAL_debugFileName,False)
        raise RuntimeError('\n' + error_found_in_mumc_config_py)

#######################################################################################################


############# START OF SCRIPT #############

#Declare global variables
GLOBAL_configFileName='mumc_config.py'
GLOBAL_debugFileName='mumc_DEBUG.log'

#get current working directory
cwd = os.getcwd()
#change to script's directory
script_dir=change_working_directory(cwd)
#remove old DEBUG if it exists
if os.path.exists(GLOBAL_debugFileName):
    os.remove(GLOBAL_debugFileName)
#change back to original working directory
os.chdir(cwd)

try:
    #try importing the mumc_config.py file
    #if mumc_config.py file does not exsit go to except and create one
    import mumc_config as cfg

    #try assigning the DEBUG variable from mumc_config.py file
    #if DEBUG does not exsit go to except and completely rebuild the mumc_config.py file
    GLOBAL_DEBUG=cfg.DEBUG
    #removing DEBUG from mumc_config.py file will allow the configuration to be reset

    print_script_header=cfg.print_script_header

    if (GLOBAL_DEBUG):
        print_script_header=True

    print_byType('-----------------------------------------------------------',print_script_header)
    if (GLOBAL_DEBUG):
        print_byType('\n',False)
    print_byType('',print_script_header)
    if (GLOBAL_DEBUG):
        print_byType('\n',False)
    print_byType('-----------------------------------------------------------',print_script_header)
    if (GLOBAL_DEBUG):
        print_byType('\n',False)
    print_byType('Script Version: ' + get_script_version(),print_script_header)

#the exception
except (AttributeError, ModuleNotFoundError):
    GLOBAL_DEBUG=False
    #GLOBAL_DEBUG=True

    #we are here because the mumc_config.py file does not exist
    #this is either the first time the script is running or mumc_config.py file was deleted
    #when this happens create a new mumc_config.py file
    #another possible reason we are here...
    #the above attempt to set GLOBAL_DEBUG=cfg.DEBUG failed likely because DEBUG is missing from the mumc_config.py file
    #when this happens create a new mumc_config.py file
    update_config = False
    build_configuration_file(None,update_config)

    #exit gracefully after setup
    exit(0)

#check config values are what we expect them to be
cfgCheck()

#check if user wants to update the existing config file
if (cfg.UPDATE_CONFIG):
    #check if user intentionally wants to update the config but does not have the script_behavor variable in their config
    edit_configuration_file(cfg,cfg.UPDATE_CONFIG)

    #exit gracefully after conifig update
    exit(0)

#now we can get media items that are ready to be deleted;
deleteItems=get_media_items()

#show and delete media items
output_itemsToDelete(deleteItems)

############# END OF SCRIPT #############
