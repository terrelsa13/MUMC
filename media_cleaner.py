#!/usr/bin/env python3

import urllib.request as request
import json, urllib
import traceback
import hashlib
import time
import uuid
import sys
import os
from dateutil.parser import parse
from collections import defaultdict
from datetime import datetime,date,timedelta,timezone
from media_cleaner_config_defaults import get_default_config_values


def convert2json(rawjson):
    #return a formatted string of the python JSON object
    ezjson = json.dumps(rawjson, sort_keys=False, indent=4)
    return(ezjson)


def print2json(rawjson):
    #create a formatted string of the python JSON object
    ezjson = convert2json(rawjson)
    print(ezjson)


#Check if json key exists
def does_key_exist(item, keyvalue):
    try:
        exists = item[keyvalue]
    except KeyError:
        return(False)
    return(True)


#Check if json index exists
def does_index_exist(item, indexvalue):
    try:
        exists = item[indexvalue]
    except IndexError:
        return(False)
    return(True)


#Check if json key and index exist
def does_key_index_exist(item, keyvalue, indexvalue):
    return(does_key_exist(item, keyvalue) and does_index_exist(item[keyvalue], indexvalue))


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
    print('Plain text password used to grab authentication key; password not stored in config file.')
    password=input('Enter admin password: ')
    return(password)


#Blacklisting or Whitelisting?
def get_setup_behavior(script_behavior):
    defaultbehavior='blacklist'
    valid_behavior=False
    while (valid_behavior == False):
        print('Decide how the script will use the libraries chosen for each user.')
        print('0 - blacklist - Media items in the libraries you choose will be allowed to be deleted.')
        print('1 - whitelist - Media items in the libraries you choose will NOT be allowed to be deleted.')
        if (script_behavior == 'blacklist'):
            print('')
            print('Script previously setup using \'0 - ' + script_behavior + '\'.')
        elif (script_behavior == 'whitelist'):
            print('')
            print('Script previously setup using \'1 - ' + script_behavior + '\'.')
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


#Get not played ages for media types?
def get_played_age(mediaType):
    defaultage=get_default_config_values('played_age_' + mediaType)
    valid_age=False
    while (valid_age == False):
        print('Choose the number of days to wait before deleting played ' + mediaType + ' media items')
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
                        print('\nInvalid ' + mediaType + ' age. Try again.\n')
                else:
                    print('\nInvalid ' + mediaType + ' age. Try again.\n')
            except:
                print('\nInvalid ' + mediaType + ' age. Try again.\n')


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
def get_auth_key(server_url, username, password, server_brand):
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

    headers = {xAuth : 'Emby UserId="' + username  + '", Client="media_cleaner.py", Device="Multi-User Media Cleaner", DeviceId="MUMC", Version="2.0.5 Beta", Token=""', 'Content-Type' : 'application/json'}

    req = request.Request(url=server_url + '/Users/AuthenticateByName', data=DATA, method='POST', headers=headers)

    #preConfigDebug = True
    preConfigDebug = False

    #api call
    data=requestURL(req, preConfigDebug, 'get_auth_key', 3)

    return(data['AccessToken'])


#API call to get all user accounts
#Choose account(s) this script will use to delete played media
#Choosen account(s) do NOT need to have "Allow Media Deletion From" enabled in the UI
def get_users_and_libraries(server_url, auth_key, script_behavior, updateConfig):
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

    user_keys_json=''
    user_wl_libs_json=''
    user_bl_libs_json=''

    #Check if not running for the first time
    if (updateConfig):
        #load user_keys to json
        user_keys_json=json.loads(cfg.user_keys)
        #load user_wl_libs to json
        user_wl_libs_json=json.loads(cfg.user_wl_libs)
        #load user_bl_libs to json
        user_bl_libs_json=json.loads(cfg.user_bl_libs)

        #get number of user_keys
        userkey_count=len(user_keys_json)
        #get number of user_keys
        user_wllibs_count=len(user_wl_libs_json)
        #get number of user_keys
        user_bllibs_count=len(user_bl_libs_json)

        if (userkey_count != user_wllibs_count):
            raise ValueError('\nValueError: Number of entries in user_key and number of entries in user_bl_libs does NOT match')
        elif(userkey_count != user_bllibs_count):
            raise ValueError('\nValueError: Number of entries in user_key and number of entries in user_wl_libs does NOT match')

        i=0
        #Pre-populate the existing userkeys and libraries so only new users are shown will all displayed user info
        for rerun_userkey in user_keys_json:
            userId_set.add(rerun_userkey)
            if (rerun_userkey == user_wl_libs_json[i]['userid']):
                userId_wllib_dict[rerun_userkey]=user_wl_libs_json[i]
            else:
                raise ValueError('\nValueError: Order of user_keys and user_bl libs are not in the same order.')
            if (rerun_userkey == user_wl_libs_json[i]['userid']):
                userId_bllib_dict[rerun_userkey]=user_bl_libs_json[i]
            else:
                raise ValueError('\nValueError: Order of user_keys and user_wl libs are not in the same order.')
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
    while (stop_loop == False):
        i=0
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
        else:
            single_user=True
            for user in data:
                userId_dict[i]=user['Id']

        print('')

        if ((i == 0) and (single_user == True)):
            user_number='0'
        elif ((i >= 1) and (one_user_selected == False)):
            user_number=input('Select one user at a time.\nEnter number of the user to monitor: ')
            print('')
        else: #((i >= 1) and (one_user_selected == True)):
            print('Monitoring multiple users is possible.')
            print('When multiple users are selected; the user with the oldest last played time will determine if media can be deleted.')
            user_number=input('Select one user at a time.\nEnter number of the next user to monitor; leave blank when finished: ')
            print('')

        try:
            if ((user_number == '0') and (single_user == True)):
                stop_loop=True
                one_user_selected=True
                user_number_int=int(user_number)
                userId_set.add(userId_dict[user_number_int])

                if (script_behavior == 'blacklist'):
                    message='Enter number of the library folder to blacklist (aka monitor) for the selected user.\nMedia in blacklisted library folder(s) will be monitored for deletion.'
                    userId_wllib_dict[userId_dict[user_number_int]],userId_bllib_dict[userId_dict[user_number_int]]=list_library_folders(server_url, auth_key, message, data[user_number_int]['Policy'], data[user_number_int]['Id'], user_number_int, False)
                else: #(script_behavior == 'whitelist'):
                    message='Enter number of the library folder to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                    userId_bllib_dict[userId_dict[user_number_int]],userId_wllib_dict[userId_dict[user_number_int]]=list_library_folders(server_url, auth_key, message, data[user_number_int]['Policy'], data[user_number_int]['Id'], user_number_int, False)

            elif ((user_number == '') and (not (len(userId_set) == 0))):
                stop_loop=True
                print('')
            elif ((user_number == '') and (len(userId_set) == 0)):
                print('\nMust select at least one user. Try again.\n')
            elif not (user_number == ''):
                user_number_float=float(user_number)
                if ((user_number_float % 1) == 0):
                    user_number_int=int(user_number_float)
                if ((user_number_int >= 0) and (user_number_int < i)):
                    one_user_selected=True
                    userId_set.add(userId_dict[user_number_int])

                    if (script_behavior == 'blacklist'):
                        message='Enter number of the library folder to blacklist (aka monitor) for the selected user.\nMedia in blacklisted library folder(s) will be monitored for deletion.'
                        userId_wllib_dict[userId_dict[user_number_int]],userId_bllib_dict[userId_dict[user_number_int]]=list_library_folders(server_url, auth_key, message, data[user_number_int]['Policy'], data[user_number_int]['Id'], user_number_int, False)
                    else: #(script_behavior == 'whitelist'):
                        message='Enter number of the library folder to whitelist (aka ignore) for the selcted user.\nMedia in whitelisted library folder(s) will be excluded from deletion.'
                        userId_bllib_dict[userId_dict[user_number_int]],userId_wllib_dict[userId_dict[user_number_int]]=list_library_folders(server_url, auth_key, message, data[user_number_int]['Policy'], data[user_number_int]['Id'], user_number_int, False)

                    if (len(userId_set) >= i):
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


#api call to get library folders
#then choose which folders to whitelist
def list_library_folders(server_url, auth_key, infotext, user_policy, user_id, user_number, mandatory):
    #get all library paths

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
    libraryPath_set=set()
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

    if not (user_policy['EnableAllFolders']):
        for okFolders in range(len(user_policy['EnabledFolders'])):
            enabledFolderIds_set.add(user_policy['EnabledFolders'][okFolders])
    #if not (user_policy['EnableAllChannels']):
        #for okChannels in range(len(user_policy['EnabledChannels'])):
            #enabledFolderIds_set.add(user_policy['EnabledChannels'][okChannels])

    i=0
    # Get all media libraries for the not chosen script behavior
    for libFolder in data_folders:
        if (('ItemId' in libFolder) and ('CollectionType' in libFolder) and ((enabledFolderIds_set == set()) or (libFolder['ItemId'] in enabledFolderIds_set))):
            for subLibPath in range(len(libFolder['LibraryOptions']['PathInfos'])):
                if not ('userid' in not_library_dict):
                    not_library_dict['userid']=user_id
                not_library_dict[i]['libid']=libFolder['ItemId']
                not_library_dict[i]['collectiontype']=libFolder['CollectionType']
                if (('NetworkPath' in libFolder['LibraryOptions']['PathInfos'][subLibPath])):
                    not_library_dict[i]['networkpath']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath']
                else:
                    not_library_dict[i]['networkpath']=''
                if (('Path' in libFolder['LibraryOptions']['PathInfos'][subLibPath])):
                    not_library_dict[i]['path']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path']
                else:
                    not_library_dict[i]['path']=''
                i += 1

    #for libChannel in data_channels:
        #if (('Id' in libChannel) and ('Type' in libChannel) and ((enabledFolderIds_set == set()) or (libChannel['Id'] in enabledFolderIds_set))):
            #if not ('userid' in not_library_dict):
                #not_library_dict['userid']=user_id
            #not_library_dict[i]['libid']=libChannel['Id']
            #not_library_dict[i]['collectiontype']=libChannel['Type']
            #not_library_dict[i]['networkpath']=''
            #not_library_dict[i]['path']=''
            #i += 1

    stop_loop=False
    first_run=True
    while (stop_loop == False):
        j=0
        for libFolder in data_folders:
            if (('ItemId' in libFolder) and ('CollectionType' in libFolder) and ((enabledFolderIds_set == set()) or (libFolder['ItemId'] in enabledFolderIds_set))):
                for subLibPath in range(len(libFolder['LibraryOptions']['PathInfos'])):
                    if (('NetworkPath' in libFolder['LibraryOptions']['PathInfos'][subLibPath]) and ('Path' in libFolder['LibraryOptions']['PathInfos'][subLibPath])):
                        if not (libFolder['ItemId'] in libraryPath_set):
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' + libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path'] + ' - (' + libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath'] +') - LibId: ' + libFolder['ItemId'])
                        else:
                            #show blank entry
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' )
                        if not ('userid' in libraryTemp_dict):
                            libraryTemp_dict['userid']=user_id
                        libraryTemp_dict[j]['libid']=libFolder['ItemId']
                        libraryTemp_dict[j]['collectiontype']=libFolder['CollectionType']
                        libraryTemp_dict[j]['networkpath']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath']
                        libraryTemp_dict[j]['path']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path']
                    elif ('NetworkPath' in libFolder['LibraryOptions']['PathInfos'][subLibPath]):
                        if not (libFolder['ItemId'] in libraryPath_set):
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' + libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath'] + ' - LibId: ' + libFolder['ItemId'])
                        else:
                            #show blank entry
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' )
                        if not ('userid' in libraryTemp_dict):
                            libraryTemp_dict['userid']=user_id
                        libraryTemp_dict[j]['libid']=libFolder['ItemId']
                        libraryTemp_dict[j]['collectiontype']=libFolder['CollectionType']
                        libraryTemp_dict[j]['networkpath']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['NetworkPath']
                        libraryTemp_dict[j]['path']=''
                    else: #('Path' in libFolder['LibraryOptions']['PathInfos'][subLibPath]):
                        if not(libFolder['ItemId'] in libraryPath_set):
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' + libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path'] + ' - LibId: ' + libFolder['ItemId'])
                        else:
                            #show blank entry
                            print(str(j) + ' - ' + libFolder['Name'] + ' - ' )
                        if not ('userid' in libraryTemp_dict):
                            libraryTemp_dict['userid']=user_id
                        libraryTemp_dict[j]['libid']=libFolder['ItemId']
                        libraryTemp_dict[j]['collectiontype']=libFolder['CollectionType']
                        libraryTemp_dict[j]['networkpath']=''
                        libraryTemp_dict[j]['path']=libFolder['LibraryOptions']['PathInfos'][subLibPath]['Path']
                    j += 1

        #for libChannel in data_channels:
            #if (('Id' in libChannel) and ('Type' in libChannel) and ((enabledFolderIds_set == set()) or (libChannel['Id'] in enabledFolderIds_set))):
                #if not (libChannel['Id'] in libraryPath_set):
                    #print(str(j) + ' - ' + libChannel['Name'] + ' - ' + libChannel['Type'] + ' - LibId: ' + libChannel['Id'])
                #else:
                    #show blank entry
                    #print(str(j) + ' - ' + libChannel['Name'] + ' - ' )
                #if not ('userid' in libraryTemp_dict):
                    #libraryTemp_dict['userid']=user_id
                #libraryTemp_dict[j]['libid']=libChannel['Id']
                #libraryTemp_dict[j]['collectiontype']=libChannel['Type']
                #libraryTemp_dict[j]['networkpath']=''
                #libraryTemp_dict[j]['path']=''
            #j += 1

        print('')

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
                if ((input_path_number == '') and (len(libraryPath_set) == 0) and (mandatory)):
                    print('\nMust select at least one library to monitor for this user. Try again.\n')
                elif (input_path_number == ''):
                    #Add valid library selecitons to the library dicitonary
                    if not ('userid' in library_dict):
                        library_dict['userid']=libraryTemp_dict['userid']
                    stop_loop=True
                    print('')
                else:
                    path_number_float=float(input_path_number)
                    if ((path_number_float % 1) == 0):
                        path_number_int=int(path_number_float)
                        if ((path_number_int >= 0) and (path_number_int < i)):
                            #Add valid library selecitons to the library dicitonary
                            if not ('userid' in library_dict):
                                library_dict['userid']=libraryTemp_dict['userid']
                            library_dict[path_number_int]['libid']=libraryTemp_dict[path_number_int]['libid']
                            library_dict[path_number_int]['collectiontype']=libraryTemp_dict[path_number_int]['collectiontype']
                            library_dict[path_number_int]['networkpath']=libraryTemp_dict[path_number_int]['networkpath']
                            library_dict[path_number_int]['path']=libraryTemp_dict[path_number_int]['path']

                            #Remove valid library selecitons to the not_library dicitonary
                            if (path_number_int in not_library_dict):
                                not_library_dict.pop(path_number_int)

                            # Add library ID/Path to chosen list type behavior
                            if not (library_dict[path_number_int].get('libid') == ''):
                                libraryPath_set.add(library_dict[path_number_int]['libid'])
                            elif not (library_dict[path_number_int].get('networkpath') == ''):
                                libraryPath_set.add(library_dict[path_number_int]['networkpath'])
                            else: #not (library_dict[path_number_int].get('path') == ''):
                                libraryPath_set.add(library_dict[path_number_int]['path'])

                            if (len(libraryPath_set) >= j):
                                stop_loop=True
                            else:
                                stop_loop=False
                            print('')

                            #DEBUG
                            #print('selected library folders')
                            #print(libraryPath_set)
                        else:
                            print('\nIgnoring Out Of Range Value: ' + input_path_number + '\n')
                    else:
                        print('\nIgnoring Decimal Value: ' + input_path_number + '\n')
            except:
                print('\nIgnoring Non-Whole Number Value: ' + input_path_number + '\n')

    # This should never happen
    if ((len(library_dict) > 1) and (len(not_library_dict) > 1)):
        for entry in library_dict:
            if not (entry == 'userid'):
                library_dict[entry]['path']=parse_library_Paths(library_dict[entry].get('path'))
                library_dict[entry]['networkpath']=parse_library_Paths(library_dict[entry].get('networkpath'))
        for entry in not_library_dict:
            if not (entry == 'userid'):
                not_library_dict[entry]['path']=parse_library_Paths(not_library_dict[entry].get('path'))
                not_library_dict[entry]['networkpath']=parse_library_Paths(not_library_dict[entry].get('networkpath'))
        #libraries for blacklist and whitelist
        return(not_library_dict,library_dict)
    elif ((len(library_dict) == 1) and (len(not_library_dict) > 1)):
        for entry in not_library_dict:
            if not (entry == 'userid'):
                not_library_dict[entry]['path']=parse_library_Paths(not_library_dict[entry].get('path'))
                not_library_dict[entry]['networkpath']=parse_library_Paths(not_library_dict[entry].get('networkpath'))
        #libraries for blacklist and whitelist
        return(not_library_dict,library_dict)
    elif ((len(library_dict) > 1) and (len(not_library_dict) == 1)):
        for entry in library_dict:
            if not (entry == 'userid'):
                library_dict[entry]['path']=parse_library_Paths(library_dict[entry].get('path'))
                library_dict[entry]['networkpath']=parse_library_Paths(library_dict[entry].get('networkpath'))
        #libraries for blacklist and whitelist
        return(not_library_dict,library_dict)
    else: #((len(library_dict) == 0) and (len(not_library_dict) == 0)):
        #This should never happen
        #empty libraries for blacklist and whitelist
        return(not_library_dict,library_dict)


#Parse library Paths
def parse_library_Paths(libPath_str):
    libPath_str=libPath_str.replace('\\','/')
    return(libPath_str)


#get user input needed to build the media_cleaner_config.py file
def generate_config(cfg,updateConfig):

    if not (updateConfig):
        print('-----------------------------------------------------------')
        server_brand=get_brand()

        print('-----------------------------------------------------------')
        server=get_url()
        print('-----------------------------------------------------------')
        port=get_port()
        print('-----------------------------------------------------------')
        server_base=get_base(server_brand)
        if (len(port)):
            server_url=server + ':' + port + '/' + server_base
        else:
            server_url=server + '/' + server_base
        print('-----------------------------------------------------------')

        username=get_admin_username()
        print('-----------------------------------------------------------')
        password=get_admin_password()
        print('-----------------------------------------------------------')
        auth_key=get_auth_key(server_url, username, password, server_brand)

        script_behavior=get_setup_behavior(None)
        print('-----------------------------------------------------------')

        #Initialize for compare with other tag to prevent using the same tag in both blacktag and whitetag
        blacktag=''
        whitetag=''

        blacktag=get_tag_name('blacktag',whitetag)
        print('-----------------------------------------------------------')

        whitetag=get_tag_name('whitetag',blacktag)
        print('-----------------------------------------------------------')

        user_keys_and_bllibs, user_keys_and_wllibs=get_users_and_libraries(server_url, auth_key, script_behavior, updateConfig)
        print('-----------------------------------------------------------')


        played_age_movie = get_played_age('movie')
        print('-----------------------------------------------------------')
        played_age_episode = get_played_age('episode')
        print('-----------------------------------------------------------')
        played_age_audio = get_played_age('audio')
        if (server_brand == 'jellyfin'):
            print('-----------------------------------------------------------')
            played_age_audiobook = get_played_age('audiobook')

        #set REMOVE_FILES
        REMOVE_FILES=False

    else: #Prepare to run the config editor
        print('-----------------------------------------------------------')
        script_behavior=get_setup_behavior(cfg.script_behavior)
        print('-----------------------------------------------------------')
        user_keys_and_bllibs, user_keys_and_wllibs=get_users_and_libraries(cfg.server_url, cfg.auth_key, script_behavior, updateConfig)

    userkeys_bllibs_list=[]
    userbllibs_list=[]
    userkeys_wllibs_list=[]
    userwllibs_list=[]

    for userkey, userbllib in user_keys_and_bllibs.items():
        userkeys_bllibs_list.append(userkey)
        userbllibs_list.append(userbllib)

    for userkey, userwllib in user_keys_and_wllibs.items():
        userkeys_wllibs_list.append(userkey)
        userwllibs_list.append(userwllib)

    if (userkeys_bllibs_list == userkeys_wllibs_list):
        user_keys=json.dumps(userkeys_bllibs_list)
        #user_keys=json.dumps(userkeys_wllibs_list) #Only need to dump userkeys once
        user_bl_libs=json.dumps(userbllibs_list)
        user_wl_libs=json.dumps(userwllibs_list)
    else:
        raise ValueError('Error! User key values do not match.')

    print('-----------------------------------------------------------')

    config_file=''
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Delete media type once it has been played # days ago\n"
    config_file += "#   0-730500 - number of days to wait before deleting played media\n"
    config_file += "#  -1 - to disable managing specified media type\n"
    config_file += "# (-1 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "played_age_movie=" + str(played_age_movie) + "\n"
        config_file += "played_age_episode=" + str(played_age_episode) + "\n"
        config_file += "played_age_audio=" + str(played_age_audio) + "\n"
        if (server_brand == 'jellyfin'):
            config_file += "played_age_audiobook=" + str(played_age_audiobook) + "\n"
    elif (updateConfig):
        config_file += "played_age_movie=" + str(cfg.played_age_movie) + "\n"
        config_file += "played_age_episode=" + str(cfg.played_age_episode) + "\n"
        config_file += "played_age_audio=" + str(cfg.played_age_audio) + "\n"
        if (cfg.server_brand == 'jellyfin'):
            config_file += "played_age_audiobook=" + str(cfg.played_age_audiobook) + "\n"
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
        if (cfg.server_brand == 'jellyfin'):
            config_file += "keep_favorites_audiobook=" + str(cfg.keep_favorites_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide how whitelists with multiple users behave\n"
    config_file += "#  0 - do not delete media item when ALL monitored users have the parent library whitelisted\n"
    config_file += "#  1 - do not delete media item when ANY monitored users have the parent library whitelisted\n"
    config_file += "# (1 : default)\n"
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
        if (cfg.server_brand == 'jellyfin'):
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
        config_file += "keep_favorites_advanced_music_library_artist=" + str(get_default_config_values('keep_favorites_advanced_music_library_artist')) + "\n"
    elif (updateConfig):
        config_file += "keep_favorites_advanced_track_genre=" + str(cfg.keep_favorites_advanced_track_genre) + "\n"
        config_file += "keep_favorites_advanced_album_genre=" + str(cfg.keep_favorites_advanced_album_genre) + "\n"
        config_file += "keep_favorites_advanced_music_library_genre=" + str(cfg.keep_favorites_advanced_music_library_genre) + "\n"
        config_file += "keep_favorites_advanced_track_artist=" + str(cfg.keep_favorites_advanced_track_artist) + "\n"
        config_file += "keep_favorites_advanced_album_artist=" + str(cfg.keep_favorites_advanced_album_artist) + "\n"
        config_file += "keep_favorites_advanced_music_library_artist=" + str(cfg.keep_favorites_advanced_music_library_artist) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    if ((( not (updateConfig)) and (server_brand == 'jellyfin')) or
         (updateConfig) and (hasattr(cfg, 'server_brand') and (cfg.server_brand == 'jellyfin'))):
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
            config_file += "keep_favorites_advanced_audio_book_library_author=" + str(get_default_config_values('keep_favorites_advanced_audio_book_library_author')) + "\n"
        elif (updateConfig):
            config_file += "keep_favorites_advanced_audio_book_track_genre=" + str(cfg.keep_favorites_advanced_audio_book_track_genre) + "\n"
            config_file += "keep_favorites_advanced_audio_book_genre=" + str(cfg.keep_favorites_advanced_audio_book_genre) + "\n"
            config_file += "keep_favorites_advanced_audio_book_library_genre=" + str(cfg.keep_favorites_advanced_audio_book_library_genre) + "\n"
            config_file += "keep_favorites_advanced_audio_book_track_author=" + str(cfg.keep_favorites_advanced_audio_book_track_author) + "\n"
            config_file += "keep_favorites_advanced_audio_book_author=" + str(cfg.keep_favorites_advanced_audio_book_author) + "\n"
            config_file += "keep_favorites_advanced_audio_book_library_author=" + str(cfg.keep_favorites_advanced_audio_book_library_author) + "\n"
        #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Set to True to add new users or edit existing users\n"
    config_file += "# Must be a boolean True or False value\n"
    config_file += "#  False - Operate normally\n"
    config_file += "#  True  - Enable configuration editor mode; will NOT delete media items\n"
    config_file += "#           Resets REMOVE_FILES=False\n"
    config_file += "# (False : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "UPDATE_CONFIG=False\n"
    elif (updateConfig):
        config_file += "UPDATE_CONFIG='" + str(cfg.UPDATE_CONFIG) + "'\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# CAUTION!!!   CAUTION!!!   CAUTION!!!   CAUTION!!!   CAUTION!!!\n"
    config_file += "# Do NOT enable any max_age_xyz options unless you know what you are doing\n"
    config_file += "# Use at your own risk; You alone are responsible for your actions\n"
    config_file += "# Enabling any of these options with a low value WILL DELETE THE ENTIRE LIBRARY\n"
    config_file += "# Delete media type if its creation date is x days ago; played state is ignored; value must be greater than or equal to the corresponding played_age_xyz\n"
    config_file += "#   0-730500 - number of days to wait before deleting \"old\" media\n"
    config_file += "#  -1 - to disable managing max age of specified media type\n"
    config_file += "# (-1 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "max_age_movie=-1\n"
        config_file += "max_age_episode=-1\n"
        config_file += "max_age_audio=-1\n"
        if (server_brand == 'jellyfin'):
            config_file += "max_age_audiobook=-1\n"
    elif (updateConfig):
        config_file += "max_age_movie=" + str(cfg.max_age_movie) + "\n"
        config_file += "max_age_episode=" + str(cfg.max_age_episode) + "\n"
        config_file += "max_age_audio=" + str(cfg.max_age_audio) + "\n"
        if ((cfg.server_brand == 'jellyfin') and (hasattr(cfg, 'max_age_audiobook'))):
            config_file += "max_age_audiobook=" + str(cfg.max_age_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide if max age media set as a favorite should be deleted\n"
    config_file += "#  0 - ok to delete max age media items set as a favorite\n"
    config_file += "#  1 - do not delete max age media items when set as a favorite\n"
    config_file += "# (1 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "max_keep_favorites_movie=1\n"
        config_file += "max_keep_favorites_episode=1\n"
        config_file += "max_keep_favorites_audio=1\n"
        if (server_brand == 'jellyfin'):
            config_file += "max_keep_favorites_audiobook=1\n"
    elif (updateConfig):
        config_file += "max_keep_favorites_movie=" + str(cfg.max_keep_favorites_movie) + "\n"
        config_file += "max_keep_favorites_episode=" + str(cfg.max_keep_favorites_episode) + "\n"
        config_file += "max_keep_favorites_audio=" + str(cfg.max_keep_favorites_audio) + "\n"
        if ((cfg.server_brand == 'jellyfin') and (hasattr(cfg, 'max_keep_favorites_audiobook'))):
            config_file += "max_keep_favorites_audiobook=" + str(cfg.max_keep_favorites_audiobook) + "\n"
    #config_file += "#----------------------------------------------------------#\n"
    config_file += "\n"
    config_file += "#------------DO NOT MODIFY BELOW---------------------------#\n"
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
    config_file += "#  Also know as an Access Token\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "auth_key='" + auth_key + "'\n"
    elif (updateConfig):
        config_file += "auth_key='" + cfg.auth_key + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Decide how the script will use the libraries chosen for each user.\n"
    config_file += "#  0 - blacklist - Media items in the libraries you choose will be allowed to be deleted.\n"
    config_file += "#  1 - whitelist - Media items in the libraries you choose will NOT be allowed to be deleted.\n"
    config_file += "# (blacklist : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "script_behavior='" + script_behavior + "'\n"
    elif (updateConfig):
        config_file += "script_behavior='" + cfg.script_behavior + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# User key(s) of monitored account(s); chosen during setup\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "user_keys='" + user_keys + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Blacklisted libraries with corresponding user keys(s)\n"
    config_file += "# These libraries are monitored for media items to delete; chosen during setup\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "user_bl_libs='" + user_bl_libs + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# Whitelisted libraries with corresponding user keys(s)\n"
    config_file += "# These libraries are NOT actively monitored for media items to delete; chosen during setup\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "user_wl_libs='" + user_wl_libs + "'\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# API query attempts; number of times to retry an API request\n"
    config_file += "#  delay between initial attempt and the first retry is 1 second\n"
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
    config_file += "# API query item limit; large libraries sometimes cannot return all of the media metadata items in a single API call\n"
    config_file += "#  This is especially true when using the max_age_xyz options; which requires every item of the specified media type send its metadata\n"
    config_file += "#  1-10000 - number of media metadata items the server will return for each API call for media item metadata; ALL queried items will be processed regardless of this value\n"
    config_file += "#  (50 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "api_query_item_limit=50\n"
    elif (updateConfig):
        config_file += "api_query_item_limit=" + str(cfg.api_query_item_limit) + "\n"
    config_file += "\n"
    config_file += "#----------------------------------------------------------#\n"
    config_file += "# 0 - Debug messages disabled\n"
    config_file += "# 1 - Debug messages enabled\n"
    config_file += "# (0 : default)\n"
    config_file += "#----------------------------------------------------------#\n"
    if not (updateConfig):
        config_file += "DEBUG=0\n"
    elif (updateConfig):
        config_file += "DEBUG=" + str(cfg.DEBUG) + "\n"

    #Create config file next to the script even when cwd (Current Working Directory) is not the same
    cwd = os.getcwd()
    script_dir = os.path.dirname(__file__)
    if (script_dir == ''):
        #script must have been run from the cwd
        #set script_dir to cwd (aka this directory) to prevent error when attempting to change to '' (aka a blank directory)
        script_dir=cwd
    os.chdir(script_dir)
    f = open("media_cleaner_config.py", "w")
    f.write(config_file)
    f.close()
    os.chdir(cwd)

    if not (updateConfig):
        try:

            if ((played_age_movie == -1) and
                (played_age_episode == -1) and
                (played_age_audio == -1) and
                #((hasattr(cfg, 'played_age_audiobook') and (cfg.played_age_audiobook == -1)) or (not hasattr(cfg, 'played_age_audiobook')))):
                (((server_brand == 'jellyfin') and (played_age_audiobook == -1)) or (server_brand == 'emby'))):
                    print('\n\n-----------------------------------------------------------')
                    print('Config file is not setup to find played media.')
                    print('-----------------------------------------------------------')
                    print('To find played media open media_cleaner_config.py in a text editor:')
                    print('    Set \'played_age_movie\' to zero or a positive number')
                    print('    Set \'played_age_episode\' to zero or a positive number')
                    print('    Set \'played_age_audio\' to zero or a positive number')
                    if (server_brand == 'jellyfin'):
                        print('    Set \'played_age_audiobook\' to zero or a positive number')
            if (REMOVE_FILES == 0):
                print('-----------------------------------------------------------')
                print('Config file is not setup to delete played media.')
                print('Config file is in dry run mode to prevent deleting media.')
                print('-----------------------------------------------------------')
                print('To delete media open media_cleaner_config.py in a text editor:')
                print('    Set REMOVE_FILES=\'TRUE\' in media_cleaner_config.py')
            print('-----------------------------------------------------------')
            print('Edit the media_cleaner_config.py file and try running again.')
            print('-----------------------------------------------------------')

        #the exception
        except (AttributeError, ModuleNotFoundError):
            #something went wrong
            #media_cleaner_config.py should have been created by now
            #we are here because the media_cleaner_config.py file does not exist
            #this is either the first time the script is running or media_cleaner_config.py file was deleted

            raise RuntimeError('\nConfigError: Cannot find or open media_cleaner_config.py')

            #exit gracefully
            exit(0)


#Get count of days since last played
def get_days_since_played(date_last_played):

    if not (date_last_played == 'Unknown'):

        #Get current time
        date_time_now = datetime.utcnow()

        #Keep the year, month, day, hour, minute, and seconds
        #split date_last_played after seconds
        try:
            split_date_micro_tz = date_last_played.split(".")
            date_time_last_played = datetime.strptime(date_last_played, '%Y-%m-%dT%H:%M:%S.' + split_date_micro_tz[1])
        except (ValueError):
            date_time_last_played = 'unknown date time format'

        if bool(cfg.DEBUG):
            #DEBUG
            print(date_time_last_played)

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
    else:
        days_since_played=date_last_played

    return(days_since_played)


#Get count of days since last created
def get_days_since_created(date_last_created):
    return(get_days_since_played(date_last_created).replace('Played', 'Created', 1))


#get season and episode numbers
def get_season_episode(season_number, episode_number):
    season_num = str(season_number)
    season_num_len=len(str(season_number))

    episode_num = str(episode_number)
    episode_num_len=len(str(episode_num))

    #at the least; print season.episode with 2-digits zero padded
    #if season or episode has more than 2-digits print x-digits zero padded
    if (season_num_len <= 2) and (episode_num_len <= 2):
        season_num = season_num.zfill(2)
        episode_num = episode_num.zfill(2)
    elif (season_num_len >= episode_num_len):
        season_num = season_num.zfill(season_num_len)
        episode_num = episode_num.zfill(season_num_len)
    else: #(season_num_len < episode_num_len):
        season_num = season_num.zfill(episode_num_len)
        episode_num = episode_num.zfill(episode_num_len)

    season_episode = 's' + season_num + '.e' + episode_num
    return(season_episode)


#Limit the amount of data returned for a single API call
def api_query_handler(url,StartIndex,TotalItems,QueryLimit,APIDebugMsg):

    data=requestURL(url, cfg.DEBUG, APIDebugMsg, cfg.api_query_attempts)

    TotalItems = data['TotalRecordCount']
    StartIndex = StartIndex + QueryLimit
    QueryLimit = cfg.api_query_item_limit
    if ((StartIndex + QueryLimit) >= (TotalItems)):
        QueryLimit = TotalItems - StartIndex

    QueryItemsRemaining=False
    if (QueryLimit > 0):
        QueryItemsRemaining=True

    return(data,StartIndex,TotalItems,QueryLimit,QueryItemsRemaining)


#send url request
def requestURL(url, debugBool, debugMessage, retries):

    if bool(debugBool):
        #DEBUG
        print(debugMessage + ' - url')
        print(url)

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
                        if bool(debugBool):
                            #DEBUG
                            print(debugMessage + ' - data')
                            print2json(data)
                        #return(data)
                    except Exception as err:
                        if (err.msg == 'Unauthorized'):
                            print('\n' + str(err))
                            raise RuntimeError('\nUser Not Authorized To Access Library')
                        else:
                            time.sleep(delay)
                            #delay value doubles each time the same API request is resent
                            delay += delay
                            if (delay >= (2**retryAttempts)):
                                print('An error occured, a maximum of ' + str(retryAttempts) + ' attempts met, and no data retrieved from the \"' + debugMessage + '\" lookup.')
                                return(err)
                else:
                    getdata = False
                    print('An error occurred while attempting to retrieve data from the API.')
                    return('Attempt to get data at: ' + debugMessage + '. Server responded with code: ' + str(response.getcode()))
        except Exception as err:
            if (err.msg == 'Unauthorized'):
                print('\n' + str(err))
                raise RuntimeError('\nUser Not Authorized To Access Library')
            else:
                time.sleep(delay)
                #delay value doubles each time the same API request is resent
                delay += delay
                if (delay >= (2**retryAttempts)):
                    print('An error occured, a maximum of ' + str(retryAttempts) + ' attempts met, and no data retrieved from the \"' + debugMessage + '\" lookup.')
                    return(err)
    return(data)


#Get the favorited children of specified favorited parents
def getChildren_favoriteMetaData(user_key,data_Favorited):
    server_url=cfg.server_url
    auth_key=cfg.auth_key
    child_list=[]
    child_list_Id=[]

    for data in data_Favorited['Items']:

        #if ((data['Type'] == 'Season') or (data['Type'] == 'Series') or (data['Type'] == 'CollectionFolder')):
        if ((data['IsFolder'] == True) or (data['Type'] == 'Book')):

            user_processed_itemsId_list=set()

            #Initialize api_query_handler() variables for watched child media items
            StartIndex=0
            TotalItems=1
            QueryLimit=1
            QueriesRemaining=True
            APIDebugMsg='find_children_of_favortied_media_data'

            if not (data['Id'] == ''):
                #Build query for watched child media items; check is not Movie, Episode, or Audio
                if not ((data['Type'] == 'Movie') and (data['Type'] == 'Episode') and (data['Type'] == 'Audio')):
                    #include all item types; filter applied in firt API calls for each media type in get_items()
                    IncludeItemTypes=''
                    FieldsState='Id,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,UserData'
                    SortBy='SeriesName,AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                    SortOrder='Ascending'
                    Recursive='True'
                    EnableImages='False'
                    CollapseBoxSetItems='False'
                    if (cfg.max_age_movie >= 0):
                        IsPlayedState=''
                    else:
                        IsPlayedState='True'

                    while (QueriesRemaining):

                        if not (data['Id'] == ''):
                            #Built query for watched items in s
                            apiQuery=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + data['Id'] + '&IncludeItemTypes=' + IncludeItemTypes +
                            '&StartIndex=' + str(StartIndex) + '&Limit=' + str(QueryLimit) + '&IsPlayed=' + IsPlayedState + '&Fields=' + FieldsState +
                            '&CollapseBoxSetItems=' + CollapseBoxSetItems + '&Recursive=' + Recursive + '&SortBy=' + SortBy + '&SortOrder=' + SortOrder + '&EnableImages=' + EnableImages + '&api_key=' + auth_key)
                        else:
                            #When no libraries are ed; simulate an empty query being returned
                            #this will prevent trying to compare to an empty  string '' to the whitelist libraries later on
                            data={'Items':[],'TotalRecordCount':0}
                            QueryLimit=0

                        #Send the API query for for watched media items in blacklists
                        children_data,StartIndex,TotalItems,QueryLimit,QueriesRemaining=api_query_handler(apiQuery,StartIndex,TotalItems,QueryLimit,APIDebugMsg)

                        for child_item in children_data['Items']:
                            child_itemTag=''
                            child_itemIsFavorited=False
                            if not (child_item['Id'] in user_processed_itemsId_list):
                                #Check if media item has any favs
                                if not (does_key_exist(child_item,'UserData')):
                                    #if it does not; add fav to metadata
                                    child_item['UserData']={'IsFavorite':True}
                                elif not (does_key_exist(child_item['UserData'],'IsFavorite')):
                                    #if it does not; add fav to metadata
                                    child_item['UserData']['IsFavorite']=True
                                #if child_item is not already a fav; update this temp metadata so it is a fav
                                elif not (child_item['UserData']['IsFavorite']):
                                    child_item['UserData']['IsFavorite']=True

                                #assign fav to metad
                                child_list.append(child_item)
                                user_processed_itemsId_list.add(child_item['Id'])

    #Return dictionary of child items along with TotalRecordCount
    return({'Items':child_list,'TotalRecordCount':len(child_list)})


#Get watched children of parents
def getChildren_tagMetaData(user_key,data_Tagged,user_tags,tag_Type):
    server_url=cfg.server_url
    auth_key=cfg.auth_key
    parent_tag=[]
    child_list=[]
    child_list_Id=[]
    insert_tagName=user_tags.split(',')[0]
    insert_tagId=uuid.uuid4().int

    for data in data_Tagged['Items']:

        #if ((data['Type'] == 'Season') or (data['Type'] == 'Series') or (data['Type'] == 'CollectionFolder')):
        if ((data['IsFolder'] == True) or (data['Type'] == 'Book')):

            user_processed_itemsId_list=set()

            #Initialize api_query_handler() variables for watched child media items
            StartIndex=0
            TotalItems=1
            QueryLimit=1
            QueriesRemaining=True
            APIDebugMsg='find_children_' + tag_Type + 'ged_media_data'

            if not (data['Id'] == ''):
                #Build query for watched child media items; check is not Movie, Episode, or Audio
                if not ((data['Type'] == 'Movie') and (data['Type'] == 'Episode') and (data['Type'] == 'Audio')):
                    #include all item types; filter applied in firt API calls for each media type in get_items()
                    IncludeItemTypes=''
                    FieldsState='Id,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,UserData'
                    SortBy='SeriesName,AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                    SortOrder='Ascending'
                    Recursive='True'
                    EnableImages='False'
                    CollapseBoxSetItems='False'
                    if (cfg.max_age_movie >= 0):
                        IsPlayedState=''
                    else:
                        IsPlayedState='True'

                    while (QueriesRemaining):

                        if not (data['Id'] == ''):
                            #Built query for watched items in s
                            apiQuery=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + data['Id'] + '&IncludeItemTypes=' + IncludeItemTypes +
                            '&StartIndex=' + str(StartIndex) + '&Limit=' + str(QueryLimit) + '&IsPlayed=' + IsPlayedState +
                            '&Fields=' + FieldsState + '&Recursive=' + Recursive + '&SortBy=' + SortBy + '&SortOrder=' + SortOrder +
                            '&EnableImages=' + EnableImages + '&api_key=' + auth_key)
                        else:
                            #When no libraries are ed; simulate an empty query being returned
                            #this will prevent trying to compare to an empty  string '' to the whitelist libraries later on
                            data={'Items':[],'TotalRecordCount':0}
                            QueryLimit=0

                        #Send the API query for for watched media items in blacklists
                        children_data,StartIndex,TotalItems,QueryLimit,QueriesRemaining=api_query_handler(apiQuery,StartIndex,TotalItems,QueryLimit,APIDebugMsg)

                        for child_item in children_data['Items']:
                            child_itemTag=''
                            child_itemIsTagged=False
                            if not (child_item['Id'] in user_processed_itemsId_list):
                                if (cfg.server_brand == 'emby'):
                                    #Does 'TagItems' exist
                                    if not (does_key_exist(child_item,'TagItems')):
                                        #if it does not; add desired tag to metadata
                                        child_item['TagItems']=[{'Name':insert_tagName,'Id':insert_tagId}]
                                    #Does 'TagItems'[] exist
                                    elif not (does_index_exist(child_item['TagItems'],0)):
                                        #if it does not; add desired tag to metadata
                                        child_item['TagItems']=[{'Name':insert_tagName,'Id':insert_tagId}]
                                    else: #Tag already exists
                                        #Determine if the existing tags are any of the tags we are looking for
                                        child_list_Id,child_itemIsTagged=get_isItemTagged(user_tags,child_list_Id,child_item,user_key,tag_Type)
                                        #If existing tags are not ones we are lookign for then insert desired tag
                                        if not (child_itemIsTagged):
                                            child_item['TagItems'].append({'Name':insert_tagName,'Id':insert_tagId})
                                else: #(cfg.server_brand == 'jellyfin')
                                    #Does 'TagItems' exist
                                    if not (does_key_exist(child_item,'Tag')):
                                        #if it does not; add desired tag to metadata
                                        child_item['Tags']=[insert_tagName]
                                    #Does 'Tags'[] exist
                                    elif (child_item['Tags'] == []):
                                        #if it does not; add desired tag to metadata
                                        child_item['Tags'].append(insert_tagName)
                                    else:
                                        #Determine if the existing tags are any of the tags we are looking for
                                        child_list_Id,child_itemIsTagged=get_isItemTagged(user_tags,child_list_Id,child_item,user_key,tag_Type)
                                        #If existing tags are not ones we are lookign for then insert desired tag
                                        if not (child_itemIsTagged):
                                            child_item['Tags'].append(insert_tagName)
                                #keep track of tagged child items
                                child_list.append(child_item)
                                user_processed_itemsId_list.add(child_item['Id'])

    #Return dictionary of child items along with TotalRecordCount
    return({'Items':child_list,'TotalRecordCount':len(child_list)})


#get additional item info needed to make a decision about a media item
def get_additional_item_info(user_key,itemId,lookupTopic):
    server_url=cfg.server_url
    auth_key=cfg.auth_key

    #Get additonal item information
    url=(server_url + '/Users/' + user_key  + '/Items/' + str(itemId) +
        '?enableImages=False&enableUserData=True&Fields=ParentId,Genres,Tags&api_key=' + auth_key)

    if bool(cfg.DEBUG):
        #DEBUG
        print('-----------------------------------------------------------')
        print(url)

    itemInfo=requestURL(url, cfg.DEBUG, lookupTopic, cfg.api_query_attempts)

    return(itemInfo)


#get additional channel/network/studio info needed to determine if item is favorite
def get_studio_item_info(user_key,studioNetworkName):
    server_url=cfg.server_url
    auth_key=cfg.auth_key
    #Encode studio name
    studio_network=urllib.parse.quote(studioNetworkName)

    #Get studio item information
    #url=server_url + '/Studios/' + studio_network + '?userId=' + user_key + '&enableImages=False&api_key=' + auth_key
    url=server_url + '/Studios/' + studio_network + '&enableImages=False&enableUserData=True&api_key=' + auth_key

    if bool(cfg.DEBUG):
        #DEBUG
        print('-----------------------------------------------------------')
        print(url)

    itemInfo=requestURL(url, cfg.DEBUG, 'studio_network_info', cfg.api_query_attempts)

    return(itemInfo)


#Determine if item can be monitored
def get_isItemMonitored(mediasource):
    if (does_key_exist(mediasource, 'Type') and does_key_exist(mediasource, 'Size')):
        if ((mediasource['Type'] == 'Placeholder') and (mediasource['Size'] == 0)):
            itemIsMonitored=False
        else:
            itemIsMonitored=True
    elif (does_key_exist(mediasource, 'Type')):
        if (mediasource['Type'] == 'Placeholder'):
            itemIsMonitored=False
        else:
            itemIsMonitored=True
    elif (does_key_exist(mediasource, 'Size')):
        if (mediasource['Size'] == 0):
            itemIsMonitored=False
        else:
            itemIsMonitored=True
    else:
        itemIsMonitored=False

    return(itemIsMonitored)


#Get the watched children of specified tagged parents
def get_isItemTagged(usertags,tagged_items,item,user_key,tagtype):
    itemIsTagged=False
    itemIsTagged=False

    if (cfg.server_brand == 'emby'):
        #Check if media item is tagged
        if ((not (usertags == '')) and (does_key_exist(item,'TagItems'))):
            #Check if media item is tagged
            taglist=set()
            for tagpos in range(len(item['TagItems'])):
                taglist.add(item['TagItems'][tagpos]['Name'])
            itemIsTagged, itemTaggedValue=get_isItemMatching(usertags, ','.join(map(str, taglist)))
            #Save media item's tags state
            if (itemIsTagged):
                tagged_items.append(item['Id'])
                if bool(cfg.DEBUG):
                    istag_byUserId[user_key][item['Id']] = itemIsTagged
    else:
        #Jellyfin tags
        #Check if media item is tagged
        if ((not (usertags == '')) and (does_key_exist(item,'Tags'))):
            #Check if media item is tagged
            taglist=set()
            for tagpos in range(len(item['Tags'])):
                taglist.add(item['Tags'][tagpos])
            itemIsTagged, itemTaggedValue=get_isItemMatching(usertags, ','.join(map(str, taglist)))
            #Save media item's usertags state
            if (itemIsTagged):
                tagged_items.append(item['Id'])
                if bool(cfg.DEBUG):
                    istag_byUserId[user_key][item['Id']] = itemIsTagged

    #parenthesis intentionally omitted to return tagged_items as a set
    return tagged_items,itemIsTagged


#Determine if there is a matching item
def get_isItemMatching(item_one, item_two):

    #for Ids in Microsoft Windows, replace backslashes in Ids with forward slash
    item_one = item_one.replace('\\','/')
    item_two = item_two.replace('\\','/')

    #read and split Ids to compare to
    item_one_split=item_one.split(',')
    item_two_split=item_two.split(',')

    matching_item=''
    items_match=False
    #determine if media Id matches one of the other Ids
    for single_item_one in item_one_split:
        if not (single_item_one == ''):
            for single_item_two in item_two_split:
                if not (single_item_two == ''):
                    if (single_item_one == single_item_two):
                        items_match=True

                        if bool(cfg.DEBUG):
                            #DEBUG
                            print('media item id to library id comparison')
                            print(item_one + ' : ' + single_item_one)

                        return(items_match, single_item_one)

    return(items_match, matching_item)


#Determine if genre is favorited
def get_isfav_GENRE(user_key,item,isfav_ITEMgenre,keep_favorites_advanced,lookupTopic):

    if (does_key_index_exist(item, 'GenreItems', 0)):
        #Check if bitmask for favorites by item genre is enabled
        if (keep_favorites_advanced):
            #Check if bitmask for any or first item genre is enabled
            if (keep_favorites_advanced == 1):
                    genre_item_info = get_additional_item_info(user_key,item['GenreItems'][0]['Id'],lookupTopic)
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
                    genre_item_info = get_additional_item_info(user_key,item['GenreItems'][genre_item]['Id'],lookupTopic + '_any')
                    #Check if genre's favorite value already exists in dictionary
                    if not genre_item_info['Id'] in isfav_ITEMgenre:
                        #Store if any genre is marked as a favorite
                        isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (genre_item_info['UserData']['IsFavorite']):
                            #Store if the genre is marked as a favorite
                            isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']

    return(isfav_ITEMgenre)


#Determine if artist is favorited
def get_isfav_ARTIST(user_key,item,isfav_ITEMartist,keep_favorites_advanced,lookupTopic):

    if (does_key_index_exist(item, 'ArtistItems', 0)):
        #Check if bitmask for favorites by artist is enabled
        if (keep_favorites_advanced):
            #Check if bitmask for any or first artist is enabled
            if (keep_favorites_advanced == 1):
                artist_item_info = get_additional_item_info(user_key,item['ArtistItems'][0]['Id'],lookupTopic + '_info')
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
                    artist_item_info = get_additional_item_info(user_key,item['ArtistItems'][artist]['Id'],lookupTopic + '_info_any')
                    #Check if artist's favorite value already exists in dictionary
                    if not artist_item_info['Id'] in isfav_ITEMartist:
                        #Store if any track artist is marked as a favorite
                        isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (artist_item_info['UserData']['IsFavorite']):
                            #Store if the artist is marked as a favorite
                            isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']

    return(isfav_ITEMartist)


#Determine if artist is favorited
def get_isfav_STUDIONETWORK(user_key,item,isfav_ITEMstdo_ntwk,keep_favorites_advanced,lookupTopic):

    if (does_key_index_exist(item, 'Studios', 0)):
        #Check if bitmask for favorites by item genre is enabled
        if (keep_favorites_advanced):
            #Check if bitmask for any or first item genre is enabled
            if (keep_favorites_advanced == 1):
                #Get studio network's item info
                studionetwork_item_info = get_additional_item_info(user_key,item['Studios'][0]['Id'],'studio_network_info')
                #Check if studio-network's favorite value already exists in dictionary
                if not studionetwork_item_info['Id'] in isfav_ITEMstdo_ntwk:
                    if (does_key_index_exist(studionetwork_item_info,'UserData','IsFavorite')):
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
                    studionetwork_item_info = get_additional_item_info(user_key,item['Studios'][studios]['Id'],'studio_network_info')
                    #Check if studio network's favorite value already exists in dictionary
                    if not studionetwork_item_info['Id'] in isfav_ITEMstdo_ntwk:
                        if (does_key_index_exist(studionetwork_item_info,'UserData','IsFavorite')):
                            #Store if the studio network is marked as a favorite
                            isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (studionetwork_item_info['UserData']['IsFavorite']):
                            #Store if the studio network is marked as a favorite
                            isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']

    elif (does_key_exist(item, 'SeriesStudio')):
        #Check if bitmask for favorites by item genre is enabled
        if (keep_favorites_advanced):
            #Get series studio network's item info
            studionetwork_item_info = get_studio_item_info(user_key,item['SeriesStudio'])
            #Check if series studio network's favorite value already exists in dictionary
            if not studionetwork_item_info['Id'] in isfav_ITEMstdo_ntwk:
                if (does_key_index_exist(studionetwork_item_info,'UserData','IsFavorite')):
                    #Store if the series studio network is marked as a favorite
                    isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']
            else: #it already exists
                #if the value is True save it anyway
                if (studionetwork_item_info['UserData']['IsFavorite']):
                    #Store if the series studio network is marked as a favorite
                    isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']

    return(isfav_ITEMstdo_ntwk)


#determine if genres for movie or library are set to favorite
def get_isfav_MOVIE_ADVANCED(item,user_key):

    keep_favorites_advanced_movie_genre=cfg.keep_favorites_advanced_movie_genre
    keep_favorites_advanced_movie_library_genre=cfg.keep_favorites_advanced_movie_library_genre
    #define empty dictionary for favorited Movies
    isfav_MOVIE={'movie':{},'movielibrary':{},'moviegenre':{},'movielibrarygenre':{}}

### Movie #######################################################################################

    if (does_key_exist(item, 'Id')):

        isfav_MOVIE['moviegenre']=get_isfav_GENRE(user_key,item,isfav_MOVIE['moviegenre'],keep_favorites_advanced_movie_genre,'movie_genre')

### End Movie ###################################################################################

### Movie Library #######################################################################################

    if (does_key_exist(item, 'ParentId')):
        movielibrary_item_info = get_additional_item_info(user_key,item['ParentId'],'movie_library_info')

        isfav_MOVIE['movielibrarygenre']=get_isfav_GENRE(user_key,movielibrary_item_info,isfav_MOVIE['movielibrarygenre'],keep_favorites_advanced_movie_library_genre,'movie_library_genre')

### End Movie Library ###################################################################################

    for isfavkey in isfav_MOVIE:
        for isfavID in isfav_MOVIE[isfavkey]:
            if (isfav_MOVIE[isfavkey][isfavID]):
                return(True)
                
    return(False)


#determine if genres for episode, season, series, or studio-network are set to favorite
def get_isfav_EPISODE_ADVANCED(item,user_key):

    keep_favorites_advanced_episode_genre=cfg.keep_favorites_advanced_episode_genre
    keep_favorites_advanced_season_genre=cfg.keep_favorites_advanced_season_genre
    keep_favorites_advanced_series_genre=cfg.keep_favorites_advanced_series_genre
    keep_favorites_advanced_tv_library_genre=cfg.keep_favorites_advanced_tv_library_genre
    keep_favorites_advanced_tv_studio_network=cfg.keep_favorites_advanced_tv_studio_network
    keep_favorites_advanced_tv_studio_network_genre=cfg.keep_favorites_advanced_tv_studio_network_genre
    #define empty dictionary for favorited TV Series, Seasons, Episodes, and Channels/Networks
    isfav_EPISODE={'episode':{},'season':{},'series':{},'tvlibrary':{},'episodegenre':{},'seasongenre':{},'seriesgenre':{},'tvlibrarygenre':{},'seriesstudionetwork':{},'seriesstudionetworkgenre':{}}

### Episode #######################################################################################

    if (does_key_exist(item, 'Id')):

        isfav_EPISODE['episodegenre']=get_isfav_GENRE(user_key,item,isfav_EPISODE['episodegenre'],keep_favorites_advanced_episode_genre,'episode_genre')

### End Episode ###################################################################################

### Season ########################################################################################

    if (does_key_exist(item, 'SeasonId')):
        season_item_info = get_additional_item_info(user_key,item['SeasonId'],'season_info')

        isfav_EPISODE['seasongenre']=get_isfav_GENRE(user_key,season_item_info,isfav_EPISODE['seasongenre'],keep_favorites_advanced_season_genre,'season_genre')

    elif (does_key_exist(item, 'ParentId')):
        season_item_info = get_additional_item_info(user_key,item['ParentId'],'season_info')

        isfav_EPISODE['seasongenre']=get_isfav_GENRE(user_key,season_item_info,isfav_EPISODE['seasongenre'],keep_favorites_advanced_season_genre,'season_genre')

### End Season ####################################################################################

### Series ########################################################################################

    if (does_key_exist(item, 'SeriesId')):
        series_item_info = get_additional_item_info(user_key,item['SeriesId'],'series_info')

        isfav_EPISODE['seriesgenre']=get_isfav_GENRE(user_key,series_item_info,isfav_EPISODE['seriesgenre'],keep_favorites_advanced_series_genre,'series_genre')

        isfav_EPISODE['seriesstudionetwork']=get_isfav_STUDIONETWORK(user_key,series_item_info,isfav_EPISODE['seriesstudionetwork'],keep_favorites_advanced_tv_studio_network,'studio_network')

    elif (does_key_exist(season_item_info, 'SeriesId')):
        series_item_info = get_additional_item_info(user_key,item['SeriesId'],'series_info')

        isfav_EPISODE['seriesgenre']=get_isfav_GENRE(user_key,series_item_info,isfav_EPISODE['seriesgenre'],keep_favorites_advanced_series_genre,'series_genre')

        isfav_EPISODE['seriesstudionetwork']=get_isfav_STUDIONETWORK(user_key,series_item_info,isfav_EPISODE['seriesstudionetwork'],keep_favorites_advanced_tv_studio_network,'studio_network')

    elif (does_key_exist(item, 'ParentId')):
        series_item_info = get_additional_item_info(user_key,season_item_info['ParentId'],'series_info')

        isfav_EPISODE['seriesgenre']=get_isfav_GENRE(user_key,series_item_info,isfav_EPISODE['seriesgenre'],keep_favorites_advanced_series_genre,'series_genre')

        isfav_EPISODE['seriesstudionetwork']=get_isfav_STUDIONETWORK(user_key,series_item_info,isfav_EPISODE['seriesstudionetwork'],keep_favorites_advanced_tv_studio_network,'studio_network')

    elif (does_key_exist(season_item_info, 'ParentId')):
        series_item_info = get_additional_item_info(user_key,season_item_info['ParentId'],'series_info')

        isfav_EPISODE['seriesgenre']=get_isfav_GENRE(user_key,series_item_info,isfav_EPISODE['seriesgenre'],keep_favorites_advanced_series_genre,'series_genre')

        isfav_EPISODE['seriesstudionetwork']=get_isfav_STUDIONETWORK(user_key,series_item_info,isfav_EPISODE['seriesstudionetwork'],keep_favorites_advanced_tv_studio_network,'studio_network')

### End Series ####################################################################################

### TV Library ########################################################################################

    if (does_key_exist(series_item_info, 'ParentId')):
        tvlibrary_item_info = get_additional_item_info(user_key,series_item_info['ParentId'],'tv_library_info')

        isfav_EPISODE['tvlibrarygenre']=get_isfav_GENRE(user_key,tvlibrary_item_info,isfav_EPISODE['tvlibrarygenre'],keep_favorites_advanced_tv_library_genre,'tv_library_genre')

### End TV Library ####################################################################################

### Studio Network #######################################################################################

    if (does_key_index_exist(series_item_info, 'Studios', 0)):
        #Get studio network's item info
        tvstudionetwork_item_info = get_additional_item_info(user_key,series_item_info['Studios'][0]['Id'],'studio_network_info')

        isfav_EPISODE['seriesstudionetworkgenre']=get_isfav_GENRE(user_key,tvstudionetwork_item_info,isfav_EPISODE['seriesstudionetworkgenre'],keep_favorites_advanced_tv_studio_network_genre,'studio_network_genre')

    elif (does_key_exist(series_item_info, 'SeriesStudio')):
        #Get series studio network's item info
        tvstudionetwork_item_info = get_studio_item_info(user_key,series_item_info['SeriesStudio'])

        isfav_EPISODE['seriesstudionetworkgenre']=get_isfav_GENRE(user_key,tvstudionetwork_item_info,isfav_EPISODE['seriesstudionetworkgenre'],keep_favorites_advanced_tv_studio_network_genre,'studio_network_genre')

### End Studio Network ###################################################################################

    for isfavkey in isfav_EPISODE:
        for isfavID in isfav_EPISODE[isfavkey]:
            if (isfav_EPISODE[isfavkey][isfavID]):
                return(True)

    return(False)


#determine if genres for music track, album, or artist are set to favorite
def get_isfav_AUDIO_ADVANCED(item,user_key,itemType):

    if (itemType == 'Audio'):
        lookupTopicTrack='track'
        lookupTopicAlbum='album'
        lookupTopicArtist='artist'
        lookupTopicLibrary='music_library'

        keep_favorites_advanced_track_genre=cfg.keep_favorites_advanced_track_genre
        keep_favorites_advanced_album_genre=cfg.keep_favorites_advanced_album_genre
        keep_favorites_advanced_music_library_genre=cfg.keep_favorites_advanced_music_library_genre

        keep_favorites_advanced_track_artist=cfg.keep_favorites_advanced_track_artist
        keep_favorites_advanced_album_artist=cfg.keep_favorites_advanced_album_artist
        keep_favorites_advanced_music_library_artist=cfg.keep_favorites_advanced_music_library_artist
    elif (itemType == 'AudioBook'):
        lookupTopicTrack='audiobook'
        lookupTopicAlbum='book'
        lookupTopicArtist='author'
        lookupTopicLibrary='audio_book_library'

        keep_favorites_advanced_track_genre=cfg.keep_favorites_advanced_audio_book_track_genre
        keep_favorites_advanced_album_genre=cfg.keep_favorites_advanced_audio_book_genre
        keep_favorites_advanced_music_library_genre=cfg.keep_favorites_advanced_audio_book_library_genre

        keep_favorites_advanced_track_artist=cfg.keep_favorites_advanced_audio_book_track_author
        keep_favorites_advanced_album_artist=cfg.keep_favorites_advanced_audio_book_author
        keep_favorites_advanced_music_library_artist=cfg.keep_favorites_advanced_audio_book_library_author
    else:
        raise ValueError('ValueError: Unknown itemType passed into get_isfav_AUDIO_ADVANCED')

    #define empty dictionary for favorited Tracks, Albums, Artists
    isfav_AUDIO={'track':{},'album':{},'artist':{},'composer':{},'audiolibrary':{},'trackgenre':{},'albumgenre':{},'trackartist':{},'albumartist':{},'audiolibraryartist':{},'composergenre':{},'audiolibrarygenre':{}}

### Track #########################################################################################

    if (does_key_exist(item, 'Id')):

        isfav_AUDIO['trackgenre']=get_isfav_GENRE(user_key,item,isfav_AUDIO['trackgenre'],keep_favorites_advanced_track_genre,lookupTopicTrack + '_genre')

        isfav_AUDIO['trackartist']=get_isfav_ARTIST(user_key,item,isfav_AUDIO['trackartist'],keep_favorites_advanced_track_artist,lookupTopicTrack + '_artist')

### End Track #####################################################################################

### Album/Book #########################################################################################

    #Albums for music
    if (does_key_exist(item, 'ParentId')):
        album_item_info = get_additional_item_info(user_key,item['ParentId'],'album_info')

        isfav_AUDIO['albumgenre']=get_isfav_GENRE(user_key,album_item_info,isfav_AUDIO['albumgenre'],keep_favorites_advanced_album_genre,lookupTopicLibrary + '_genre')

        isfav_AUDIO['albumartist']=get_isfav_ARTIST(user_key,album_item_info,isfav_AUDIO['albumartist'],keep_favorites_advanced_album_artist,lookupTopicLibrary + '_artist')
    elif (does_key_exist(item, 'AlbumId')):
        album_item_info = get_additional_item_info(user_key,item['AlbumId'],'album_info')

        isfav_AUDIO['albumgenre']=get_isfav_GENRE(user_key,album_item_info,isfav_AUDIO['albumgenre'],keep_favorites_advanced_album_genre,lookupTopicLibrary + '_genre')

        isfav_AUDIO['albumartist']=get_isfav_ARTIST(user_key,album_item_info,isfav_AUDIO['albumartist'],keep_favorites_advanced_album_artist,lookupTopicLibrary + '_artist')

### End Album/Book #####################################################################################

### Library ########################################################################################

    #Library
    if (does_key_exist(album_item_info, 'ParentId')):
        audiolibrary_item_info = get_additional_item_info(user_key,album_item_info['ParentId'],'library_info')

        isfav_AUDIO['audiolibrarygenre']=get_isfav_GENRE(user_key,audiolibrary_item_info,isfav_AUDIO['audiolibrarygenre'],keep_favorites_advanced_music_library_genre,lookupTopicLibrary + '_genre')

### End Library #####################################################################################

    for isfavkey in isfav_AUDIO:
        for isfavID in isfav_AUDIO[isfavkey]:
            if (isfav_AUDIO[isfavkey][isfavID]):
                return(True)

    return(False)


#determine if genres for audiobok track, book, or author are set to favorite
def get_isfav_AUDIOBOOK_ADVANCED(item,user_key,itemType):
    return get_isfav_AUDIO_ADVANCED(item,user_key,itemType)


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
           print(str(err))
           print(favItem)
           print(deleteIndexes)
           print2json(deleteItems)
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


#Handle whitelists across multiple users by ID
def get_iswhitelist_ByMultiUser(userkeys, whitelists, deleteItems):
    all_whitelists=set()
    deleteIndexes=[]

    #len_userkeys=len(userkeys)
    len_deleteItems=len(deleteItems)

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
           print(str(err))
           print(wlItem)
           print(deleteIndexes)
           print2json(deleteItems)
           exit(0)

    return(deleteItems)


#Handle whitetags across multiple users by ID
def get_iswhitetagged_ByMultiUser(userkeys, whitetags, deleteItems):
    return get_iswhitelist_ByMultiUser(userkeys, whitetags, deleteItems)


#check and populate unknown movie output data
def prep_movieOutput(item):

    if not (does_key_exist(item,'Type')):
        item['Type']='Movie'
    if not (does_key_exist(item,'Name')):
        item['Name']='Unknown'
    if not (does_key_exist(item,'Studios')):
        item['Studios']=[0]
        item['Studios'][0]={'Name':'Unknown'}
    if not (does_key_exist(item['Studios'],0)):
        item['Studios']=[0]
        item['Studios'][0]={'Name':'Unknown'}
    if not (does_key_exist(item['Studios'][0],'Name')):
        item['Studios'][0]={'Name':'Unknown'}
    #if not (does_key_exist(item,'SeriesStudio')):
        #item['SeriesStudio']='Unknown'
        #tbd
    if ((item['UserData']['Played'] == True) and (item['UserData']['PlayCount'] >= 1)):
        if not (does_key_exist(item['UserData'],'LastPlayedDate')):
            item['UserData']['LastPlayedDate']='1970-01-01T00:00:00.00Z'
    else:
        if not (does_key_exist(item['UserData'],'LastPlayedDate')):
            item['UserData']['LastPlayedDate']='Unknown'
    if not (does_key_exist(item,'DateCreated')):
        item['DateCreated']='1970-01-01T00:00:00.00Z'
    if not (does_key_exist(item,'Id')):
        item['item']='Unknown'

    return item


#check and populate unknown episode output data
def prep_episodeOutput(item):

    if not (does_key_exist(item,'Type')):
        item['Type']='Episode'
    if not (does_key_exist(item,'SeriesName')):
        item['SeriesName']='Unknown'
    if not (does_key_exist(item,'ParentIndexNumber')):
        item['ParentIndexNumber']=999
    if not (does_key_exist(item,'IndexNumber')):
        item['IndexNumber']=999
    if not (does_key_exist(item,'Name')):
        item['Name']='Unknown'
    if not (does_key_exist(item,'SeriesStudio')):
        item['SeriesStudio']='Unknown'
    if ((item['UserData']['Played'] == True) and (item['UserData']['PlayCount'] >= 1)):
        if not (does_key_exist(item['UserData'],'LastPlayedDate')):
            item['UserData']['LastPlayedDate']='1970-01-01T00:00:00.00Z'
    else:
        if not (does_key_exist(item['UserData'],'LastPlayedDate')):
            item['UserData']['LastPlayedDate']='Unknown'
    if not (does_key_exist(item,'DateCreated')):
        item['DateCreated']='1970-01-01T00:00:00.00Z'
    if not (does_key_exist(item,'Id')):
        item['item']='Unknown'

    return item


#check and populate unknown audio and audiobook output data
def prep_audioOutput(item):

    if not (does_key_exist(item,'Type')):
        item['Type']='Episode'
    if not (does_key_exist(item,'IndexNumber')):
        item['IndexNumber']=999
    if not (does_key_exist(item,'Name')):
        item['Name']='Unknown'
    if not (does_key_exist(item,'Album')):
        item['Album']='Unknown'
    if not (does_key_exist(item,'Artist')):
        item['Artist']='Unknown'
    if not (does_key_exist(item,'Studios')):
        item['Studios']=[{'Name':'Unknown'}]
    if not (does_index_exist(item['Studios'],0)):
        item['Studios']=[{'Name':'Unknown'}]
    if ((item['UserData']['Played'] == True) and (item['UserData']['PlayCount'] >= 1)):
        if not (does_key_exist(item['UserData'],'LastPlayedDate')):
            item['UserData']['LastPlayedDate']='1970-01-01T00:00:00.00Z'
    else:
        if not (does_key_exist(item['UserData'],'LastPlayedDate')):
            item['UserData']['LastPlayedDate']='Unknown'
    if not (does_key_exist(item,'DateCreated')):
        item['DateCreated']='1970-01-01T00:00:00.00Z'
    if not (does_key_exist(item,'Id')):
        item['item']='Unknown'

    return item


#Unpack library data structure from config
def user_lib_builder(lib_json):
    built_userid=[]
    built_libid=[]
    built_collectiontype=[]
    built_networkpath=[]
    built_path=[]
    datapos=0

    for currentPos in lib_json:
        libid_append=''
        collectiontype_append=''
        networkpath_append=''
        path_append=''
        for slots in currentPos:
            if (slots == 'userid'):
                built_userid.append(currentPos[slots])
            else:
                for slotLibData in currentPos[slots]:
                    if (slotLibData == 'libid'):
                        if (libid_append == ''):
                            libid_append=currentPos[slots][slotLibData]
                        else:
                            if not (currentPos[slots][slotLibData] == ''):
                                libid_append=libid_append + ',' + currentPos[slots][slotLibData]
                            else:
                                libid_append=libid_append + ',\'\''
                    elif (slotLibData == 'collectiontype'):
                        if (collectiontype_append == ''):
                            collectiontype_append=currentPos[slots][slotLibData]
                        else:
                            if not (currentPos[slots][slotLibData] == ''):
                                collectiontype_append=collectiontype_append + ',' + currentPos[slots][slotLibData]
                            else:
                                collectiontype_append=collectiontype_append + ',\'\''
                    elif (slotLibData == 'networkpath'):
                        if (networkpath_append == ''):
                            networkpath_append=currentPos[slots][slotLibData]
                        else:
                            if not (currentPos[slots][slotLibData] == ''):
                                networkpath_append=networkpath_append + ',' + currentPos[slots][slotLibData]
                            else:
                                networkpath_append=networkpath_append + ',\'\''
                    elif (slotLibData == 'path'):
                        if (path_append == ''):
                            path_append=currentPos[slots][slotLibData]
                        else:
                            if not (currentPos[slots][slotLibData] == ''):
                                path_append=path_append + ',' + currentPos[slots][slotLibData]
                            else:
                                path_append=path_append + ',\'\''
        built_libid.insert(datapos,libid_append)
        built_collectiontype.insert(datapos,collectiontype_append)
        built_networkpath.insert(datapos,networkpath_append)
        built_path.insert(datapos,path_append)
        datapos+=1
    return(built_libid,built_collectiontype,built_networkpath,built_path)


#get played media items; track media items ready to be deleted
def get_items():
    server_url=cfg.server_url
    auth_key=cfg.auth_key
    
    #Get list of all played items
    print('')
    print('-----------------------------------------------------------')
    print('Start...')
    print('Cleaning media for server at: ' + server_url)
    print('-----------------------------------------------------------')
    print('')

    all_media_disabled=False

    if (
       (cfg.played_age_movie == -1) and
       (cfg.played_age_episode == -1) and
       (cfg.played_age_audio == -1) and
       ((hasattr(cfg, 'played_age_audiobook') and (cfg.played_age_audiobook == -1)) or (not hasattr(cfg, 'played_age_audiobook'))) and
       (cfg.max_age_movie == -1) and
       (cfg.max_age_episode == -1) and
       (cfg.max_age_audio == -1) and
       ((hasattr(cfg, 'max_age_audiobook') and (cfg.max_age_audiobook == -1)) or (not hasattr(cfg, 'max_age_audiobook')))
       ):
        print('* ATTENTION!!!                                            *')
        print('* No media types are being monitored.                     *')
        print('* Open the media_cleaner_config.py file in a text editor. *')
        print('* Set at least one media type to >=0.                     *')
        print('*                                                         *')
        print('* played_age_movie=-1                                     *')
        print('* played_age_episode=-1                                   *')
        print('* played_age_audio=-1                                     *')
        if (cfg.server_brand == 'jellyfin'):
            print('* played_age_audiobook=-1                             *')
        print('-----------------------------------------------------------')
        all_media_disabled=True

    #list of items to be deleted
    deleteItems=[]
    #dictionary of favorited items by userId
    isfav_byUserId_Movie={}
    isfav_byUserId_Episode={}
    isfav_byUserId_Audio={}
    if (cfg.server_brand == 'jellyfin'):
        isfav_byUserId_AudioBook={}
    #whitelisted Id per media type according to media types metadata
    movie_whitelists=set()
    episode_whitelists=set()
    audio_whitelists=set()
    if (cfg.server_brand == 'jellyfin'):
        audiobook_whitelists=set()

    #blacktagged items per media type according to media types metadata
    movie_blacktaglists=[]
    episode_blacktaglists=[]
    audio_blacktaglists=[]
    if (cfg.server_brand == 'jellyfin'):
        audiobook_blacktaglists=[]

    #whitetagged items per media type according to media types metadata
    movie_whitetaglists=[]
    episode_whitetaglists=[]
    audio_whitetaglists=[]
    if (cfg.server_brand == 'jellyfin'):
        audiobook_whitetaglists=[]

    if bool(cfg.DEBUG):
        #dictionary of whitelisted items by userId
        #iswhitelist_byUserId={}
        iswhitelist_byUserId[user_key]={}
        #dictionary of blacktagged items by userId
        #isblacktag_byUserId={}
        isblacktag_byUserId[user_key]={}
        #dictionary of whitetagged items by userId
        #iswhitetag_byUserId={}
        iswhitetag_byUserId[user_key]={}

    #load user_keys to json
    user_keys_json=json.loads(cfg.user_keys)
    #load user_bl_libs to json
    user_bllib_json=json.loads(cfg.user_bl_libs)
    #load_user_wl_libs to json
    user_wllib_json=json.loads(cfg.user_wl_libs)

    #Build the library data from the data structures stored in the configuration file
    user_bllib_keys_json,user_bllib_collectiontype_json,user_bllib_netpath_json,user_bllib_path_json=user_lib_builder(json.loads(cfg.user_bl_libs))
    #Build the library data from the data structures stored in the configuration file
    user_wllib_keys_json,user_wllib_collectiontype_json,user_wllib_netpath_json,user_wllib_path_json=user_lib_builder(json.loads(cfg.user_wl_libs))

    #Get blacktags
    blacktags=cfg.blacktag
    #Get whitetags
    whitetags=cfg.whitetag

    #establish deletion date for played media items
    cut_off_date_movie=datetime.now(timezone.utc) - timedelta(cfg.played_age_movie)
    cut_off_date_episode=datetime.now(timezone.utc) - timedelta(cfg.played_age_episode)
    cut_off_date_audio=datetime.now(timezone.utc) - timedelta(cfg.played_age_audio)
    if ((cfg.server_brand == 'jellyfin') and hasattr(cfg, 'played_age_audiobook')):
        cut_off_date_audiobook=datetime.now(timezone.utc) - timedelta(cfg.played_age_audiobook)

    for user_key in user_keys_json:
        #define dictionary user_key to store media item favorite states by userId and itemId
        isfav_byUserId_Movie[user_key]={}
        isfav_byUserId_Episode[user_key]={}
        isfav_byUserId_Audio[user_key]={}
        if (cfg.server_brand == 'jellyfin'):
            isfav_byUserId_AudioBook[user_key]={}

    currentPosition=0

    for user_key in user_keys_json:
        url=server_url + '/Users/' + user_key  + '/?api_key=' + auth_key

        if bool(cfg.DEBUG):
            #DEBUG
            print(url)

        user_data=requestURL(url, cfg.DEBUG, 'current_user', cfg.api_query_attempts)

        print('')
        print('-----------------------------------------------------------')
        print('Get List Of Media For:')
        print(user_data['Name'] + ' - ' + user_data['Id'])
        print('-----------------------------------------------------------')

        media_found=False

############# Movies #############

        if ((cfg.played_age_movie >= 0) or (cfg.max_age_movie >= 0)):

            user_processed_itemsId_list=set()

            for LibraryID in user_bllib_keys_json[currentPosition].split(','):

                #Initialize api_query_handler() variables for watched media items in blacklists
                StartIndex_Blacklist=0
                TotalItems_Blacklist=1
                QueryLimit_Blacklist=1
                QueriesRemaining_Blacklist=True
                APIDebugMsg_Blacklist='movie_blacklist_media_data'

                if not (LibraryID == ''):
                    #Build query for watched media items in blacklists
                    IncludeItemTypes_Blacklist='Movie'
                    FieldsState_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                    SortBy_Blacklist='ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Blacklist='Ascending'
                    EnableUserData_Blacklist='True'
                    Recursive_Blacklist='True'
                    EnableImages_Blacklist='False'
                    CollapseBoxSetItems_Blacklist='False'
                    if (cfg.max_age_movie >= 0):
                        IsPlayedState_Blacklist=''
                    else:
                        IsPlayedState_Blacklist='True'

                #Initialize api_query_handler() variables for Favorited media items
                StartIndex_Favorited=0
                TotalItems_Favorited=1
                QueryLimit_Favorited=1
                QueriesRemaining_Favorited=True
                APIDebugMsg_Favorited='movie_Favorited_media_data'

                #Build query for Favorited media items
                IncludeItemTypes_Favorited='Movie,BoxSet,CollectionFolder'
                FieldsState_Favorited='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_Favorited='ParentIndexNumber,IndexNumber,Name'
                SortOrder_Favorited='Ascending'
                EnableUserData_Favorited='True'
                Recursive_Favorited='True'
                EnableImages_Favorited='False'
                CollapseBoxSetItems_Favorited='False'
                IsFavorite='True'

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged=0
                TotalItems_BlackTagged=1
                QueryLimit_BlackTagged=1
                QueriesRemaining_BlackTagged=True
                APIDebugMsg_BlackTagged='movie_favortied_media_data'

                #Build query for blacktagged media items
                IncludeItemTypes_BlackTagged='Movie,BoxSet,CollectionFolder'
                FieldsState_BlackTagged='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_BlackTagged='ParentIndexNumber,IndexNumber,Name'
                SortOrder_BlackTagged='Ascending'
                EnableUserData_Blacktagged='True'
                Recursive_Tagged_Blacktagged='True'
                EnableImages_Blacktagged='False'
                CollapseBoxSetItems_Blacktagged='False'
                #Encode blacktags so they are url acceptable
                BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged=0
                TotalItems_WhiteTagged=1
                QueryLimit_WhiteTagged=1
                QueriesRemaining_WhiteTagged=True
                APIDebugMsg_WhiteTagged='movie_favortied_media_data'

                #Build query for whitetagged media items
                IncludeItemTypes_WhiteTagged='Movie,BoxSet,CollectionFolder'
                FieldsState_WhiteTagged='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios'
                SortBy_WhiteTagged='ParentIndexNumber,IndexNumber,Name'
                SortOrder_WhiteTagged='Ascending'
                EnableUserData_Whitetagged='True'
                Recursive_Tagged_Whitetagged='True'
                EnableImages_Whitetagged='False'
                CollapseBoxSetItems_Whitetagged='False'
                #Encode whitetags so they are url acceptable
                WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                QueryItemsRemaining_All=True

                while (QueryItemsRemaining_All):

                    if not (LibraryID == ''):
                        #Built query for watched items in blacklists
                        apiQuery_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID + '&IncludeItemTypes=' + IncludeItemTypes_Blacklist +
                        '&StartIndex=' + str(StartIndex_Blacklist) + '&Limit=' + str(QueryLimit_Blacklist) + '&IsPlayed=' + IsPlayedState_Blacklist +
                        '&Fields=' + FieldsState_Blacklist + '&Recursive=' + Recursive_Blacklist + '&SortBy=' + SortBy_Blacklist + '&SortOrder=' + SortOrder_Blacklist +
                        '&EnableImages=' + EnableImages_Blacklist + '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacklist + '&EnableUserData=' + EnableUserData_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        data_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,QueriesRemaining_Blacklist=api_query_handler(apiQuery_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,APIDebugMsg_Blacklist)
                    else:
                        #When no libraries are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Blacklist={'Items':[],'TotalRecordCount':0}
                        QueryLimit_Blacklist=0
                        QueriesRemaining_Blacklist=False

                    #Built query for Favorited media items
                    apiQuery_Favorited=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID + '&IncludeItemTypes=' + IncludeItemTypes_Favorited +
                    '&StartIndex=' + str(StartIndex_Favorited) + '&Limit=' + str(QueryLimit_Favorited) + '&Fields=' + FieldsState_Favorited +
                    '&Recursive=' + Recursive_Favorited + '&SortBy=' + SortBy_Favorited + '&SortOrder=' + SortOrder_Favorited + '&EnableImages=' + EnableImages_Favorited +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited + '&IsFavorite=' + IsFavorite + '&EnableUserData=' + EnableUserData_Favorited + '&api_key=' + auth_key)

                    #Send the API query for for Favorited media items
                    data_Favorited,StartIndex_Favorited,TotalItems_Favorited,QueryLimit_Favorited,QueriesRemaining_Favorited=api_query_handler(apiQuery_Favorited,StartIndex_Favorited,TotalItems_Favorited,QueryLimit_Favorited,APIDebugMsg_Favorited)

                    #Built query for blacktagged media items
                    apiQuery_BlackTagged=(server_url + '/Users/' + user_key  + '/Items?IncludeItemTypes=' + IncludeItemTypes_BlackTagged +
                    '&StartIndex=' + str(StartIndex_BlackTagged) + '&Limit=' + str(QueryLimit_BlackTagged) + '&Fields=' + FieldsState_BlackTagged +
                    '&Recursive=' + Recursive_Tagged_Blacktagged + '&SortBy=' + SortBy_BlackTagged + '&SortOrder=' + SortOrder_BlackTagged + '&EnableImages=' + EnableImages_Blacktagged +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged + '&api_key=' + auth_key)

                    #Check if blacktag is not an empty string
                    if not (BlackTags_Tagged == ''):
                        #Send the API query for for blacktagged media items
                        data_Blacktagged,StartIndex_BlackTagged,TotalItems_BlackTagged,QueryLimit_BlackTagged,QueriesRemaining_BlackTagged=api_query_handler(apiQuery_BlackTagged,StartIndex_BlackTagged,TotalItems_BlackTagged,QueryLimit_BlackTagged,APIDebugMsg_BlackTagged)
                    else: #(BlackTags_Tagged == '')
                        data_Blacktagged={'Items':[],'TotalRecordCount':0}
                        QueryLimit_BlackTagged=0
                        QueriesRemaining_BlackTagged=False

                    #Built query for whitetagged media items
                    apiQuery_WhiteTagged=(server_url + '/Users/' + user_key  + '/Items?IncludeItemTypes=' + IncludeItemTypes_WhiteTagged +
                    '&StartIndex=' + str(StartIndex_WhiteTagged) + '&Limit=' + str(QueryLimit_WhiteTagged) + '&Fields=' + FieldsState_WhiteTagged +
                    '&Recursive=' + Recursive_Tagged_Whitetagged + '&SortBy=' + SortBy_WhiteTagged + '&SortOrder=' + SortOrder_WhiteTagged + '&EnableImages=' + EnableImages_Whitetagged +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged + '&api_key=' + auth_key)

                    #Check if whitetag is not an empty string
                    if not (WhiteTags_Tagged == ''):
                        #Send the API query for for whitetagged media items
                        data_Whitetagged,StartIndex_WhiteTagged,TotalItems_WhiteTagged,QueryLimit_WhiteTagged,QueriesRemaining_WhiteTagged=api_query_handler(apiQuery_WhiteTagged,StartIndex_WhiteTagged,TotalItems_WhiteTagged,QueryLimit_WhiteTagged,APIDebugMsg_WhiteTagged)
                    else: #(WhiteTags_Tagged == '')
                        data_Whitetagged={'Items':[],'TotalRecordCount':0}
                        QueryLimit_WhiteTagged=0
                        QueriesRemaining_WhiteTagged=False

                    #Define reasoning for lookup
                    APIDebugMsg_Favortied_Child='favortied child'
                    data_Favorited_Children=getChildren_favoriteMetaData(user_key,data_Favorited)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_Child='blacktag'
                    data_Blacktagged_Children=getChildren_tagMetaData(user_key,data_Blacktagged,cfg.blacktag,APIDebugMsg_Blacktag_Child)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_Child='whitetag'
                    data_Whitetagged_Children=getChildren_tagMetaData(user_key,data_Whitetagged,cfg.whitetag,APIDebugMsg_Whitetag_Child)
                    
                    #Combine dictionaries into list of dictionaries
                    #Order here is important [0-Fav,1-FavChid,2-Whitetag,3-WhitetagChild,4-BlackTag,5-BlacktagChild,6-Blacklist]
                    data_list=[data_Favorited,data_Favorited_Children,data_Whitetagged,data_Whitetagged_Children,data_Blacktagged,data_Blacktagged_Children,data_Blacklist]

                    #Combine remaining query items into list of dictionaries
                    QueryLimit_list=[QueryLimit_Blacklist,QueryLimit_Favorited,QueryLimit_BlackTagged]

                    #Determine if we are done processing queries or if there are still queries to be sent
                    QueryItemsRemaining_All=(QueriesRemaining_Blacklist | QueriesRemaining_Favorited | QueriesRemaining_BlackTagged | QueriesRemaining_WhiteTagged)

                    #Determine if media item is to be deleted or kept
                    #Loop thru each dictionary in data_list[#]
                    for data in data_list:

                        #Loop thru each dictionary[item]
                        for item in data['Items']:

                            #Check if item was already processed for this user
                            if not (item['Id'] in user_processed_itemsId_list):
                                user_processed_itemsId_list.add(item['Id'])

                                media_found=True

                                itemIsMonitored=False
                                if (item['Type'] == 'Movie'):
                                    for mediasource in item['MediaSources']:
                                        itemIsMonitored=get_isItemMonitored(mediasource)

                                #find media item is ready to delete
                                if (itemIsMonitored):

                                    #establish max cutoff date for media item
                                    if (cfg.max_age_movie >= 0):
                                        max_cut_off_date_movie=datetime.strptime(item['DateCreated'], '%Y-%m-%dT%H:%M:%S.' + item['DateCreated'].split(".")[1]) + timedelta(cfg.max_age_movie)
                                    else:
                                        max_cut_off_date_movie=date_time_now=datetime.utcnow() + timedelta(1)

                                    #Get if media item is set as favorite
                                    if ((does_key_exist(item,'UserData')) and (does_key_exist(item['UserData'],'IsFavorite')) and (item['UserData']['IsFavorite'])):
                                        itemisfav_MOVIE=True
                                    else:
                                        itemisfav_MOVIE=get_isfav_MOVIE_ADVANCED(item,user_key)

                                    #Store media item's favorite state when multiple users are monitored and we want to keep media items based on any user favoriting the media item
                                    if ((cfg.keep_favorites_movie == 2) and (itemisfav_MOVIE)):
                                        isfav_byUserId_Movie[user_key][item['Id']] = itemisfav_MOVIE

                                    itemIsWhiteListed=False
                                    itemIsWhiteListedTaggedNotWatched=False
                                    #Store media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                    if (cfg.multiuser_whitelist_movie == 1):
                                        #Get if media item is whitelisted
                                        for wllib_pos in range(len(user_wllib_keys_json)):
                                            if not (wllib_pos == currentPosition):
                                                itemIsWhiteListed, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                                                #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                                if (itemIsWhiteListed):
                                                    movie_whitelists.add(item['Id'])
                                                    if bool(cfg.DEBUG):
                                                        iswhitelist_byUserId[user_key][item['Id']] = itemIsWhiteListed
                                            else:
                                                #media item could be seen due to matching tag and not watched state
                                                itemIsWhiteListedTaggedNotWatched, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                                    else:
                                        #Get if media item is whitelisted
                                        for wllib_pos in range(len(user_wllib_keys_json)):
                                            if (wllib_pos == currentPosition):
                                                #media item could be seen due to matching tag and not watched state
                                                itemIsWhiteListedTaggedNotWatched, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])

                                    #Determine what to show based on whitelist outputs
                                    if ((itemIsWhiteListed == False) and (itemIsWhiteListedTaggedNotWatched == False)):
                                        displayIsWhiteListed=False
                                    elif ((itemIsWhiteListed == False) and (itemIsWhiteListedTaggedNotWatched == True)):
                                        displayIsWhiteListed=True
                                    elif ((itemIsWhiteListed == True) and (itemIsWhiteListedTaggedNotWatched == False)):
                                        displayIsWhiteListed=False
                                    elif ((itemIsWhiteListed == True) and (itemIsWhiteListedTaggedNotWatched == True)):
                                        displayIsWhiteListed=True

                                    #Override for when LibraryID == ''
                                    #This means all libraries are whitelisted for this user
                                    if (LibraryID == ''):
                                        displayIsWhiteListed=True

                                    movie_whitetaglists,itemIsWhiteTagged=get_isItemTagged(whitetags,movie_whitetaglists,item,user_key,'whitetag')

                                    itemIsBlackTagged=False
                                    #Skip blacktagging if already whitetagged
                                    if not (itemIsWhiteTagged):
                                        movie_blacktaglists,itemIsBlackTagged=get_isItemTagged(blacktags,movie_blacktaglists,item,user_key,'blacktag')

                                    if (does_key_exist(item['UserData'], 'Played')):

                                        if (
                                        ((cfg.played_age_movie >= 0) and
                                        (item['UserData']['PlayCount'] >= 1) and
                                        (cut_off_date_movie > parse(item['UserData']['LastPlayedDate'])) and
                                        (not bool(cfg.keep_favorites_movie) or (not itemisfav_MOVIE)) and 
                                        (not itemIsWhiteListed) and (not itemIsWhiteTagged))
                                        or
                                        ((cfg.max_age_movie >= 0) and
                                        (max_cut_off_date_movie <= datetime.utcnow()) and
                                        (((not bool(cfg.keep_favorites_movie)) or (not itemisfav_MOVIE)) and
                                        ((not bool(cfg.max_keep_favorites_movie)) or (not itemisfav_MOVIE))) and
                                        (not itemIsWhiteListed) and (not itemIsWhiteTagged))
                                        ):
                                            try:
                                                #Fill in the blanks
                                                item=prep_movieOutput(item)

                                                item_details=(item['Type'] + ' - ' + item['Name'] + ' - ' + item['Studios'][0]['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) +
                                                            ' - ' + get_days_since_created(item['DateCreated']) + ' - Favorite: ' + str(itemisfav_MOVIE) + ' - Whitelisted: ' + str(displayIsWhiteListed) +
                                                            ' - Tag Match: ' + str(itemIsBlackTagged or itemIsWhiteTagged) + ' - ' + item['Type'] + 'ID: ' + item['Id'])
                                            except (KeyError, IndexError):
                                                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                                                if bool(cfg.DEBUG):
                                                    #DEBUG
                                                    print('\nError encountered - Delete Movie: \nitem: ' + str(item) + '\nitem' + str(item))
                                            if (item['Type'] == 'Movie'):
                                                print(':*[DELETE] -     ' + item_details)
                                                deleteItems.append(item)
                                        else:
                                            try:
                                                #Fill in the blanks
                                                item=prep_movieOutput(item)

                                                item_details=(item['Type'] + ' - ' + item['Name'] + ' - ' + item['Studios'][0]['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) +
                                                            ' - ' + get_days_since_created(item['DateCreated']) + ' - Favorite: ' + str(itemisfav_MOVIE) + ' - Whitelisted: ' + str(displayIsWhiteListed) +
                                                            ' - Tag Match: ' + str(itemIsBlackTagged or itemIsWhiteTagged) + ' - ' + item['Type'] + 'ID: ' + item['Id'])
                                            except (KeyError, IndexError):
                                                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                                                if bool(cfg.DEBUG):
                                                    #DEBUG
                                                    print('\nError encountered - Keep Movie: \nitem: ' + str(item) + '\nitem' + str(item))
                                            if (item['Type'] == 'Movie'):
                                                print(':[KEEPING] -     ' + item_details)

############# Episodes #############

        if ((cfg.played_age_episode >= 0) or (cfg.max_age_episode >= 0)):

            user_processed_itemsId_list=set()

            for LibraryID in user_bllib_keys_json[currentPosition].split(','):

                #Initialize api_query_handler() variables for watched media items in blacklists
                StartIndex_Blacklist=0
                TotalItems_Blacklist=1
                QueryLimit_Blacklist=1
                QueriesRemaining_Blacklist=True
                APIDebugMsg_Blacklist='episode_blacklist_media_data'

                if not (LibraryID == ''):
                    #Build query for watched media items in blacklists
                    IncludeItemTypes_Blacklist='Episode'
                    FieldsState_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                    SortBy_Blacklist='SeriesName,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Blacklist='Ascending'
                    EnableUserData_Blacklist='True'
                    Recursive_Blacklist='True'
                    EnableImages_Blacklist='False'
                    if (cfg.max_age_episode >= 0):
                        IsPlayedState_Blacklist=''
                    else:
                        IsPlayedState_Blacklist='True'

                #Initialize api_query_handler() variables for Favorited media items
                StartIndex_Favorited=0
                TotalItems_Favorited=1
                QueryLimit_Favorited=1
                QueriesRemaining_Favorited=True
                APIDebugMsg_Favorited='episode_Favorited_media_data'

                #Build query for Favorited media items
                IncludeItemTypes_Favorited='Episode,Season,Series,CollectionFolder'
                FieldsState_Favorited='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                SortBy_Favorited='SeriesName,ParentIndexNumber,IndexNumber,Name'
                SortOrder_Favorited='Ascending'
                EnableUserData_Favorited='True'
                Recursive_Favorited='True'
                EnableImages_Favorited='False'
                IsFavorite='True'

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged=0
                TotalItems_BlackTagged=1
                QueryLimit_BlackTagged=1
                QueriesRemaining_BlackTagged=True
                APIDebugMsg_BlackTagged='episode_favortied_media_data'

                #Build query for tagged media items
                IncludeItemTypes_BlackTagged='Episode,Season,Series,CollectionFolder'
                FieldsState_BlackTagged='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                SortBy_BlackTagged='ParentIndexNumber,IndexNumber,Name'
                SortOrder_BlackTagged='Ascending'
                EnableUserData_Blacktagged='True'
                Recursive_Tagged_Blacktagged='True'
                EnableImages_Blacktagged='False'
                #Encode blacktags so they are url acceptable
                BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged=0
                TotalItems_WhiteTagged=1
                QueryLimit_WhiteTagged=1
                QueriesRemaining_WhiteTagged=True
                APIDebugMsg_WhiteTagged='episode_favortied_media_data'

                #Build query for tagged media items
                IncludeItemTypes_WhiteTagged='Episode,Season,Series,CollectionFolder'
                FieldsState_WhiteTagged='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,seriesStatus'
                SortBy_WhiteTagged='ParentIndexNumber,IndexNumber,Name'
                SortOrder_WhiteTagged='Ascending'
                EnableUserData_Whitetagged='True'
                Recursive_Tagged_Whitetagged='True'
                EnableImages_Whitetagged='False'
                #Encode whitetags so they are url acceptable
                WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                QueryItemsRemaining_All=True

                while (QueryItemsRemaining_All):

                    if not (LibraryID == ''):
                        #Built query for watched items in blacklists
                        apiQuery_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID + '&IncludeItemTypes=' + IncludeItemTypes_Blacklist +
                        '&StartIndex=' + str(StartIndex_Blacklist) + '&Limit=' + str(QueryLimit_Blacklist) + '&IsPlayed=' + IsPlayedState_Blacklist +
                        '&Fields=' + FieldsState_Blacklist + '&Recursive=' + Recursive_Blacklist + '&SortBy=' + SortBy_Blacklist + '&SortOrder=' + SortOrder_Blacklist +
                        '&EnableImages=' + EnableImages_Blacklist + '&EnableUserData=' + EnableUserData_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        data_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,QueriesRemaining_Blacklist=api_query_handler(apiQuery_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,APIDebugMsg_Blacklist)
                    else:
                        #When no libraries are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Blacklist={'Items':[],'TotalRecordCount':0}
                        QueryLimit_Blacklist=0
                        QueriesRemaining_Blacklist=False

                    #Built query for Favorited media items
                    apiQuery_Favorited=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID + '&IncludeItemTypes=' + IncludeItemTypes_Favorited +
                    '&StartIndex=' + str(StartIndex_Favorited) + '&Limit=' + str(QueryLimit_Favorited) + '&Fields=' + FieldsState_Favorited +
                    '&Recursive=' + Recursive_Favorited + '&SortBy=' + SortBy_Favorited + '&SortOrder=' + SortOrder_Favorited + '&EnableImages=' + EnableImages_Favorited +
                    '&IsFavorite=' + IsFavorite + '&EnableUserData=' + EnableUserData_Favorited + '&api_key=' + auth_key)

                    #Send the API query for for Favorited media items
                    data_Favorited,StartIndex_Favorited,TotalItems_Favorited,QueryLimit_Favorited,QueriesRemaining_Favorited=api_query_handler(apiQuery_Favorited,StartIndex_Favorited,TotalItems_Favorited,QueryLimit_Favorited,APIDebugMsg_Favorited)

                    #Built query for blacktagged media items
                    apiQuery_BlackTagged=(server_url + '/Users/' + user_key  + '/Items?IncludeItemTypes=' + IncludeItemTypes_BlackTagged +
                    '&StartIndex=' + str(StartIndex_BlackTagged) + '&Limit=' + str(QueryLimit_BlackTagged) + '&Fields=' + FieldsState_BlackTagged +
                    '&Recursive=' + Recursive_Tagged_Blacktagged + '&SortBy=' + SortBy_BlackTagged + '&SortOrder=' + SortOrder_BlackTagged + '&EnableImages=' + EnableImages_Blacktagged +
                    '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged + '&api_key=' + auth_key)

                    #Check if blacktag is not an empty string
                    if not (BlackTags_Tagged == ''):
                        #Send the API query for for blacktagged media items
                        data_Blacktagged,StartIndex_BlackTagged,TotalItems_BlackTagged,QueryLimit_BlackTagged,QueriesRemaining_BlackTagged=api_query_handler(apiQuery_BlackTagged,StartIndex_BlackTagged,TotalItems_BlackTagged,QueryLimit_BlackTagged,APIDebugMsg_BlackTagged)
                    else: #(BlackTags_Tagged == '')
                        data_Blacktagged={'Items':[],'TotalRecordCount':0}
                        QueryLimit_BlackTagged=0
                        QueriesRemaining_BlackTagged=False

                    #Built query for whitetagged media items
                    apiQuery_WhiteTagged=(server_url + '/Users/' + user_key  + '/Items?IncludeItemTypes=' + IncludeItemTypes_WhiteTagged +
                    '&StartIndex=' + str(StartIndex_WhiteTagged) + '&Limit=' + str(QueryLimit_WhiteTagged) + '&Fields=' + FieldsState_WhiteTagged +
                    '&Recursive=' + Recursive_Tagged_Whitetagged + '&SortBy=' + SortBy_WhiteTagged + '&SortOrder=' + SortOrder_WhiteTagged + '&EnableImages=' + EnableImages_Whitetagged +
                    '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged + '&api_key=' + auth_key)

                    #Check if whitetag is not an empty string
                    if not (WhiteTags_Tagged == ''):
                        #Send the API query for for whitetagged media items
                        data_Whitetagged,StartIndex_WhiteTagged,TotalItems_WhiteTagged,QueryLimit_WhiteTagged,QueriesRemaining_WhiteTagged=api_query_handler(apiQuery_WhiteTagged,StartIndex_WhiteTagged,TotalItems_WhiteTagged,QueryLimit_WhiteTagged,APIDebugMsg_WhiteTagged)
                    else: #(WhiteTags_Tagged == '')
                        data_Whitetagged={'Items':[],'TotalRecordCount':0}
                        QueryLimit_WhiteTagged=0
                        QueriesRemaining_WhiteTagged=False

                    #Define reasoning for lookup
                    APIDebugMsg_Favortied_Child='favortied child'
                    data_Favorited_Children=getChildren_favoriteMetaData(user_key,data_Favorited)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_Child='blacktag'
                    data_Blacktagged_Children=getChildren_tagMetaData(user_key,data_Blacktagged,cfg.blacktag,APIDebugMsg_Blacktag_Child)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_Child='whitetag'
                    data_Whitetagged_Children=getChildren_tagMetaData(user_key,data_Whitetagged,cfg.whitetag,APIDebugMsg_Whitetag_Child)
                    
                    #Combine dictionaries into list of dictionaries
                    #Order here is important [0-Fav,1-FavChid,2-Whitetag,3-WhitetagChild,4-BlackTag,5-BlacktagChild,6-Blacklist]
                    data_list=[data_Favorited,data_Favorited_Children,data_Whitetagged,data_Whitetagged_Children,data_Blacktagged,data_Blacktagged_Children,data_Blacklist]

                    #Combine remaining query items into list of dictionaries
                    QueryLimit_list=[QueryLimit_Blacklist,QueryLimit_Favorited,QueryLimit_BlackTagged]

                    #Determine if we are done processing queries or if there are still queries to be sent
                    QueryItemsRemaining_All=(QueriesRemaining_Blacklist | QueriesRemaining_Favorited | QueriesRemaining_BlackTagged | QueriesRemaining_WhiteTagged)

                    #Determine if media item is to be deleted or kept
                    #Loop thru each dictionary in data_list[#]
                    for data in data_list:

                        #Loop thru each dictionary[item]
                        for item in data['Items']: 

                            #Check if item was already processed for this user
                            if not (item['Id'] in user_processed_itemsId_list):
                                user_processed_itemsId_list.add(item['Id'])

                                media_found=True

                                itemIsMonitored=False
                                if (item['Type'] == 'Episode'):
                                    for mediasource in item['MediaSources']:
                                        itemIsMonitored=get_isItemMonitored(mediasource)

                                #find media item is ready to delete
                                if (itemIsMonitored):

                                    #establish max cutoff date for media item
                                    if (cfg.max_age_episode >= 0):
                                        max_cut_off_date_episode=datetime.strptime(item['DateCreated'], '%Y-%m-%dT%H:%M:%S.' + item['DateCreated'].split(".")[1]) + timedelta(cfg.max_age_episode)
                                    else:
                                        max_cut_off_date_episode=date_time_now=datetime.utcnow() + timedelta(1)

                                    #Get if media item is set as favorite
                                    if ((does_key_exist(item,'UserData')) and (does_key_exist(item['UserData'],'IsFavorite')) and (item['UserData']['IsFavorite'])):
                                        itemisfav_EPISODE=True
                                    else:
                                        itemisfav_EPISODE=get_isfav_EPISODE_ADVANCED(item,user_key)

                                    #Store media item's favorite state when multiple users are monitored and we want to keep media items based on any user favoriting the media item
                                    if ((cfg.keep_favorites_episode == 2) and (itemisfav_EPISODE)):
                                        isfav_byUserId_Episode[user_key][item['Id']] = itemisfav_EPISODE

                                    itemIsWhiteListed=False
                                    itemIsWhiteListedTaggedNotWatched=False
                                    #Store media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                    if (cfg.multiuser_whitelist_episode == 1):
                                        #Get if media item is whitelisted
                                        for wllib_pos in range(len(user_wllib_keys_json)):
                                            if not (wllib_pos == currentPosition):
                                                itemIsWhiteListed, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                                                #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                                if (itemIsWhiteListed):
                                                    episode_whitelists.add(item['Id'])
                                                    if bool(cfg.DEBUG):
                                                        iswhitelist_byUserId[user_key][item['Id']] = itemIsWhiteListed
                                            else:
                                                #media item could be seen due to matching tag and not watched state
                                                itemIsWhiteListedTaggedNotWatched, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                                    else:
                                        #Get if media item is whitelisted
                                        for wllib_pos in range(len(user_wllib_keys_json)):
                                            if (wllib_pos == currentPosition):
                                                #media item could be seen due to matching tag and not watched state
                                                itemIsWhiteListedTaggedNotWatched, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])

                                    #Determine what to show based on whitelist outputs
                                    if ((itemIsWhiteListed == False) and (itemIsWhiteListedTaggedNotWatched == False)):
                                        displayIsWhiteListed=False
                                    elif ((itemIsWhiteListed == False) and (itemIsWhiteListedTaggedNotWatched == True)):
                                        displayIsWhiteListed=True
                                    elif ((itemIsWhiteListed == True) and (itemIsWhiteListedTaggedNotWatched == False)):
                                        displayIsWhiteListed=False
                                    elif ((itemIsWhiteListed == True) and (itemIsWhiteListedTaggedNotWatched == True)):
                                        displayIsWhiteListed=True

                                    #Override for when LibraryID == ''
                                    #This means all libraries are whitelisted for this user
                                    if (LibraryID == ''):
                                        displayIsWhiteListed=True

                                    episode_whitetaglists,itemIsWhiteTagged=get_isItemTagged(whitetags,episode_whitetaglists,item,user_key,'whitetag')

                                    itemIsBlackTagged=False
                                    #Skip blacktagging if already whitetagged
                                    if not (itemIsWhiteTagged):
                                        episode_blacktaglists,itemIsBlackTagged=get_isItemTagged(blacktags,episode_blacktaglists,item,user_key,'blacktag')

                                    if (does_key_exist(item['UserData'], 'Played')):

                                        if (
                                        ((cfg.played_age_episode >= 0) and
                                        (item['UserData']['PlayCount'] >= 1) and
                                        (cut_off_date_episode > parse(item['UserData']['LastPlayedDate'])) and
                                        (not bool(cfg.keep_favorites_episode) or (not itemisfav_EPISODE)) and
                                        (not itemIsWhiteListed) and (not itemIsWhiteTagged))
                                        or
                                        ((cfg.max_age_episode >= 0) and
                                        (max_cut_off_date_episode <= datetime.utcnow()) and
                                        (((not bool(cfg.keep_favorites_episode)) or (not itemisfav_EPISODE)) and
                                        ((not bool(cfg.max_keep_favorites_episode)) or (not itemisfav_EPISODE))) and
                                        (not itemIsWhiteListed) and (not itemIsWhiteTagged))
                                        ):
                                            try:
                                                #Fill in the blanks
                                                item=prep_episodeOutput(item)

                                                item_details=(item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'], item['IndexNumber']) +
                                                            ' - ' + item['Name'] + ' - ' + item['SeriesStudio'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) +
                                                            ' - ' + get_days_since_created(item['DateCreated']) + ' - Favorite: ' + str(itemisfav_EPISODE) + ' - Whitelisted: ' + str(displayIsWhiteListed) +
                                                            ' - Tag Match: ' + str(itemIsBlackTagged or itemIsWhiteTagged) + ' - ' + item['Type'] + 'ID: ' + item['Id'])
                                            except (KeyError, IndexError):
                                                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                                                if bool(cfg.DEBUG):
                                                    #DEBUG
                                                    print('\nError encountered - Delete Episode: \nitem: ' + str(item) + '\nitem_info' + str(item_info))
                                            if (item['Type'] == 'Episode'):
                                                print(':*[DELETE] -   ' + item_details)
                                                deleteItems.append(item)
                                        else:
                                            try:
                                                #Fill in the blanks
                                                item=prep_episodeOutput(item)
                                                
                                                item_details=(item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'], item['IndexNumber']) +
                                                            ' - ' + item['Name'] + ' - ' + item['SeriesStudio'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) +
                                                            ' - ' + get_days_since_created(item['DateCreated']) + ' - Favorite: ' + str(itemisfav_EPISODE) + ' - Whitelisted: ' + str(displayIsWhiteListed) +
                                                            ' - Tag Match: ' + str(itemIsBlackTagged or itemIsWhiteTagged) + ' - ' + item['Type'] + 'ID: ' + item['Id'])
                                            except (KeyError, IndexError):
                                                item_details=item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                                                if bool(cfg.DEBUG):
                                                    #DEBUG
                                                    print('\nError encountered - Keep Episode: \nitem: ' + str(item) + '\nitem_info' + str(item_info))
                                            if (item['Type'] == 'Episode'):
                                                print(':[KEEPING] -   ' + item_details)

############# Audio #############

        if ((cfg.played_age_audio >= 0) or (cfg.max_age_audio >= 0)):

            user_processed_itemsId_list=set()

            for LibraryID in user_bllib_keys_json[currentPosition].split(','):

                #Initialize api_query_handler() variables for watched media items in blacklists
                StartIndex_Blacklist=0
                TotalItems_Blacklist=1
                QueryLimit_Blacklist=1
                QueriesRemaining_Blacklist=True
                APIDebugMsg_Blacklist='audio_blacklist_media_data'

                if not (LibraryID == ''):
                    #Build query for watched media items in blacklists
                    IncludeItemTypes_Blacklist='Audio'
                    FieldsState_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_Blacklist='AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Blacklist='Ascending'
                    EnableUserData_Blacklist='True'
                    Recursive_Blacklist='True'
                    EnableImages_Blacklist='False'
                    if (cfg.max_age_audio >= 0):
                        IsPlayedState_Blacklist=''
                    else:
                        IsPlayedState_Blacklist='True'

                #Initialize api_query_handler() variables for Favorited media items
                StartIndex_Favorited=0
                TotalItems_Favorited=1
                QueryLimit_Favorited=1
                QueriesRemaining_Favorited=True
                APIDebugMsg_Favorited='audio_Favorited_media_data'

                #Build query for Favorited media items
                IncludeItemTypes_Favorited='Audio,MusicAlbum,Playlist,CollectionFolder'
                FieldsState_Favorited='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                SortBy_Favorited='AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                SortOrder_Favorited='Ascending'
                EnableUserData_Favorited='True'
                Recursive_Favorited='True'
                EnableImages_Favorited='False'
                IsFavorite='True'

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged=0
                TotalItems_BlackTagged=1
                QueryLimit_BlackTagged=1
                QueriesRemaining_BlackTagged=True
                APIDebugMsg_BlackTagged='audio_favortied_media_data'

                #Build query for tagged media items
                IncludeItemTypes_BlackTagged='Audio,MusicAlbum,Playlist,CollectionFolder'
                FieldsState_BlackTagged='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                SortBy_BlackTagged='ParentIndexNumber,IndexNumber,Name'
                SortOrder_BlackTagged='Ascending'
                EnableUserData_Blacktagged='True'
                Recursive_Tagged_Blacktagged='True'
                EnableImages_Blacktagged='False'
                #Encode blacktags so they are url acceptable
                BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged=0
                TotalItems_WhiteTagged=1
                QueryLimit_WhiteTagged=1
                QueriesRemaining_WhiteTagged=True
                APIDebugMsg_WhiteTagged='audio_favortied_media_data'

                #Build query for tagged media items
                IncludeItemTypes_WhiteTagged='Audio,MusicAlbum,Playlist,CollectionFolder'
                FieldsState_WhiteTagged='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                SortBy_WhiteTagged='ParentIndexNumber,IndexNumber,Name'
                SortOrder_WhiteTagged='Ascending'
                EnableUserData_Whitetagged='True'
                Recursive_Tagged_Whitetagged='True'
                EnableImages_Whitetagged='False'
                #Encode whitetags so they are url acceptable
                WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                QueryItemsRemaining_All=True

                while (QueryItemsRemaining_All):

                    if not (LibraryID == ''):
                        #Built query for watched items in blacklists
                        apiQuery_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID + '&IncludeItemTypes=' + IncludeItemTypes_Blacklist +
                        '&StartIndex=' + str(StartIndex_Blacklist) + '&Limit=' + str(QueryLimit_Blacklist) + '&IsPlayed=' + IsPlayedState_Blacklist +
                        '&Fields=' + FieldsState_Blacklist + '&Recursive=' + Recursive_Blacklist + '&SortBy=' + SortBy_Blacklist + '&SortOrder=' + SortOrder_Blacklist +
                        '&EnableImages=' + EnableImages_Blacklist + '&EnableUserData=' + EnableUserData_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        data_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,QueriesRemaining_Blacklist=api_query_handler(apiQuery_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,APIDebugMsg_Blacklist)
                    else:
                        #When no libraries are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Blacklist={'Items':[],'TotalRecordCount':0}
                        QueryLimit_Blacklist=0
                        QueriesRemaining_Blacklist=False

                    #Built query for Favorited media items
                    apiQuery_Favorited=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID + '&IncludeItemTypes=' + IncludeItemTypes_Favorited +
                    '&StartIndex=' + str(StartIndex_Favorited) + '&Limit=' + str(QueryLimit_Favorited) + '&Fields=' + FieldsState_Favorited +
                    '&Recursive=' + Recursive_Favorited + '&SortBy=' + SortBy_Favorited + '&SortOrder=' + SortOrder_Favorited + '&EnableImages=' + EnableImages_Favorited +
                    '&IsFavorite=' + IsFavorite + '&EnableUserData=' + EnableUserData_Favorited + '&api_key=' + auth_key)

                    #Send the API query for for Favorited media items
                    data_Favorited,StartIndex_Favorited,TotalItems_Favorited,QueryLimit_Favorited,QueriesRemaining_Favorited=api_query_handler(apiQuery_Favorited,StartIndex_Favorited,TotalItems_Favorited,QueryLimit_Favorited,APIDebugMsg_Favorited)

                    #Built query for blacktagged media items
                    apiQuery_BlackTagged=(server_url + '/Users/' + user_key  + '/Items?IncludeItemTypes=' + IncludeItemTypes_BlackTagged +
                    '&StartIndex=' + str(StartIndex_BlackTagged) + '&Limit=' + str(QueryLimit_BlackTagged) + '&Fields=' + FieldsState_BlackTagged +
                    '&Recursive=' + Recursive_Tagged_Blacktagged + '&SortBy=' + SortBy_BlackTagged + '&SortOrder=' + SortOrder_BlackTagged + '&EnableImages=' + EnableImages_Blacktagged +
                    '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged + '&api_key=' + auth_key)

                    #Check if blacktag is not an empty string
                    if not (BlackTags_Tagged == ''):
                        #Send the API query for for blacktagged media items
                        data_Blacktagged,StartIndex_BlackTagged,TotalItems_BlackTagged,QueryLimit_BlackTagged,QueriesRemaining_BlackTagged=api_query_handler(apiQuery_BlackTagged,StartIndex_BlackTagged,TotalItems_BlackTagged,QueryLimit_BlackTagged,APIDebugMsg_BlackTagged)
                    else: #(BlackTags_Tagged == '')
                        data_Blacktagged={'Items':[],'TotalRecordCount':0}
                        QueryLimit_BlackTagged=0
                        QueriesRemaining_BlackTagged=False

                    #Built query for whitetagged media items
                    apiQuery_WhiteTagged=(server_url + '/Users/' + user_key  + '/Items?IncludeItemTypes=' + IncludeItemTypes_WhiteTagged +
                    '&StartIndex=' + str(StartIndex_WhiteTagged) + '&Limit=' + str(QueryLimit_WhiteTagged) + '&Fields=' + FieldsState_WhiteTagged +
                    '&Recursive=' + Recursive_Tagged_Whitetagged + '&SortBy=' + SortBy_WhiteTagged + '&SortOrder=' + SortOrder_WhiteTagged + '&EnableImages=' + EnableImages_Whitetagged +
                    '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged + '&api_key=' + auth_key)

                    #Check if whitetag is not an empty string
                    if not (WhiteTags_Tagged == ''):
                        #Send the API query for for whitetagged media items
                        data_Whitetagged,StartIndex_WhiteTagged,TotalItems_WhiteTagged,QueryLimit_WhiteTagged,QueriesRemaining_WhiteTagged=api_query_handler(apiQuery_WhiteTagged,StartIndex_WhiteTagged,TotalItems_WhiteTagged,QueryLimit_WhiteTagged,APIDebugMsg_WhiteTagged)
                    else: #(WhiteTags_Tagged == '')
                        data_Whitetagged={'Items':[],'TotalRecordCount':0}
                        QueryLimit_WhiteTagged=0
                        QueriesRemaining_WhiteTagged=False

                    #Define reasoning for lookup
                    APIDebugMsg_Favortied_Child='favortied child'
                    data_Favorited_Children=getChildren_favoriteMetaData(user_key,data_Favorited)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_Child='blacktag'
                    data_Blacktagged_Children=getChildren_tagMetaData(user_key,data_Blacktagged,cfg.blacktag,APIDebugMsg_Blacktag_Child)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_Child='whitetag'
                    data_Whitetagged_Children=getChildren_tagMetaData(user_key,data_Whitetagged,cfg.whitetag,APIDebugMsg_Whitetag_Child)
                    
                    #Combine dictionaries into list of dictionaries
                    #Order here is important [0-Fav,1-FavChid,2-Whitetag,3-WhitetagChild,4-BlackTag,5-BlacktagChild,6-Blacklist]
                    data_list=[data_Favorited,data_Favorited_Children,data_Whitetagged,data_Whitetagged_Children,data_Blacktagged,data_Blacktagged_Children,data_Blacklist]

                    #Combine remaining query items into list of dictionaries
                    QueryLimit_list=[QueryLimit_Blacklist,QueryLimit_Favorited,QueryLimit_BlackTagged]

                    #Determine if we are done processing queries or if there are still queries to be sent
                    QueryItemsRemaining_All=(QueriesRemaining_Blacklist | QueriesRemaining_Favorited | QueriesRemaining_BlackTagged | QueriesRemaining_WhiteTagged)

                    #Determine if media item is to be deleted or kept
                    #Loop thru each dictionary in data_list[#]
                    for data in data_list:

                        #Loop thru each dictionary[item]
                        for item in data['Items']: 

                            #Check if item was already processed for this user
                            if not (item['Id'] in user_processed_itemsId_list):
                                user_processed_itemsId_list.add(item['Id'])

                                media_found=True

                                itemIsMonitored=False
                                if (item['Type'] == 'Audio'):
                                    for mediasource in item['MediaSources']:
                                        itemIsMonitored=get_isItemMonitored(mediasource)

                                #find media item is ready to delete
                                if (itemIsMonitored):

                                    #establish max cutoff date for media item
                                    if (cfg.max_age_audio >= 0):
                                        max_cut_off_date_audio=datetime.strptime(item['DateCreated'], '%Y-%m-%dT%H:%M:%S.' + item['DateCreated'].split(".")[1]) + timedelta(cfg.max_age_audio)
                                    else:
                                        max_cut_off_date_audio=date_time_now=datetime.utcnow() + timedelta(1)

                                    #Get if media item is set as favorite
                                    if ((does_key_exist(item,'UserData')) and (does_key_exist(item['UserData'],'IsFavorite')) and (item['UserData']['IsFavorite'])):
                                        itemisfav_AUDIO=True
                                    else:
                                        itemisfav_AUDIO=get_isfav_AUDIO_ADVANCED(item,user_key,'Audio')

                                    #Store media item's favorite state when multiple users are monitored and we want to keep media items based on any user favoriting the media item
                                    if ((cfg.keep_favorites_audio == 2) and (itemisfav_AUDIO)):
                                        isfav_byUserId_Audio[user_key][item['Id']] = itemisfav_AUDIO

                                    itemIsWhiteListed=False
                                    itemIsWhiteListedTaggedNotWatched=False
                                    #Store media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                    if (cfg.multiuser_whitelist_audio == 1):
                                        #Get if media item is whitelisted
                                        for wllib_pos in range(len(user_wllib_keys_json)):
                                            if not (wllib_pos == currentPosition):
                                                itemIsWhiteListed, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                                                #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                                if (itemIsWhiteListed):
                                                    audio_whitelists.add(item['Id'])
                                                    if bool(cfg.DEBUG):
                                                        iswhitelist_byUserId[user_key][item['Id']] = itemIsWhiteListed
                                            else:
                                                #media item could be seen due to matching tag and not watched state
                                                itemIsWhiteListedTaggedNotWatched, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                                    else:
                                        #Get if media item is whitelisted
                                        for wllib_pos in range(len(user_wllib_keys_json)):
                                            if (wllib_pos == currentPosition):
                                                #media item could be seen due to matching tag and not watched state
                                                itemIsWhiteListedTaggedNotWatched, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])

                                    #Determine what to show based on whitelist outputs
                                    if ((itemIsWhiteListed == False) and (itemIsWhiteListedTaggedNotWatched == False)):
                                        displayIsWhiteListed=False
                                    elif ((itemIsWhiteListed == False) and (itemIsWhiteListedTaggedNotWatched == True)):
                                        displayIsWhiteListed=True
                                    elif ((itemIsWhiteListed == True) and (itemIsWhiteListedTaggedNotWatched == False)):
                                        displayIsWhiteListed=False
                                    elif ((itemIsWhiteListed == True) and (itemIsWhiteListedTaggedNotWatched == True)):
                                        displayIsWhiteListed=True

                                    #Override for when LibraryID == ''
                                    #This means all libraries are whitelisted for this user
                                    if (LibraryID == ''):
                                        displayIsWhiteListed=True

                                    audio_whitetaglists,itemIsWhiteTagged=get_isItemTagged(whitetags,audio_whitetaglists,item,user_key,'whitetag')

                                    itemIsBlackTagged=False
                                    #Skip blacktagging if already whitetagged
                                    if not (itemIsWhiteTagged):
                                        audio_blacktaglists,itemIsBlackTagged=get_isItemTagged(blacktags,audio_blacktaglists,item,user_key,'blacktag')

                                    if (does_key_exist(item['UserData'], 'Played')):

                                        if (
                                        ((cfg.played_age_audio >= 0) and
                                        (item['UserData']['PlayCount'] >= 1) and
                                        (cut_off_date_audio > parse(item['UserData']['LastPlayedDate'])) and
                                        (not bool(cfg.keep_favorites_audio) or (not itemisfav_AUDIO)) and
                                        (not itemIsWhiteListed) and (not itemIsWhiteTagged))
                                        or
                                        ((cfg.max_age_audio >= 0) and
                                        (max_cut_off_date_audio <= datetime.utcnow()) and
                                        (((not bool(cfg.keep_favorites_audio)) or (not itemisfav_AUDIO)) and
                                        ((not bool(cfg.max_keep_favorites_audio)) or (not itemisfav_AUDIO))) and
                                        (not itemIsWhiteListed) and (not itemIsWhiteTagged))
                                        ):
                                            try:
                                                #Fill in the blanks
                                                item=prep_audioOutput(item)

                                                item_details=(item['Type'] + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Album: ' + item['Album'] + ' - Artist: ' + item['Artists'][0] +
                                                            ' - Record Label: ' + item['Studios'][0]['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - ' + get_days_since_created(item['DateCreated']) +
                                                            ' - Favorite: ' + str(itemisfav_AUDIO) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - Tag Match: ' + str(itemIsBlackTagged or itemIsWhiteTagged) +
                                                            ' - TrackID: ' + item['Id'])
                                            except (KeyError, IndexError):
                                                item_details=item['Type'] + ' - Track: ' + item['Name'] + ' - ' + item['Id']
                                                if bool(cfg.DEBUG):
                                                    #DEBUG
                                                    print('\nError encountered - Delete Audio: \nitem: ' + str(item) + '\nitem' + str(item))
                                            print(':*[DELETE] -     ' + item_details)
                                            deleteItems.append(item)
                                        else:
                                            try:
                                                #Fill in the blanks
                                                item=prep_audioOutput(item)

                                                item_details=(item['Type'] + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Album: ' + item['Album'] + ' - Artist: ' + item['Artists'][0] +
                                                            ' - Record Label: ' + item['Studios'][0]['Name'] + ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - ' + get_days_since_created(item['DateCreated']) +
                                                            ' - Favorite: ' + str(itemisfav_AUDIO) + ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - Tag Match: ' + str(itemIsBlackTagged or itemIsWhiteTagged) +
                                                            ' - TrackID: ' + item['Id'])
                                            except (KeyError, IndexError):
                                                item_details=item['Type'] + ' - Track: ' + item['Name'] + ' - ' + item['Id']
                                                if bool(cfg.DEBUG):
                                                    #DEBUG
                                                    print('\nError encountered - Keep Audio: \nitem: ' + str(item) + '\nitem' + str(item))
                                            print(':[KEEPING] -     ' + item_details)

############# AudioBook#############

        #audioBook meida type only applies to jellyfin
        #Jellyfin sets audio books to a media type of audioBook
        #Emby sets audio books to a media type of audio (see audio section)
        if (
           ((cfg.server_brand == 'jellyfin') and
           hasattr(cfg, 'played_age_audiobook') and hasattr(cfg, 'max_age_audiobook')) and
           ((cfg.played_age_audiobook >= 0) or (cfg.max_age_audiobook >= 0))
           ):

            user_processed_itemsId_list=set()

            for LibraryID in user_bllib_keys_json[currentPosition].split(','):

                #Initialize api_query_handler() variables for watched media items in blacklists
                StartIndex_Blacklist=0
                TotalItems_Blacklist=1
                QueryLimit_Blacklist=1
                QueriesRemaining_Blacklist=True
                APIDebugMsg_Blacklist='audiobook_blacklist_media_data'

                if not (LibraryID == ''):
                    #Build query for watched media items in blacklists
                    IncludeItemTypes_Blacklist='Audio'
                    FieldsState_Blacklist='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                    SortBy_Blacklist='AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                    SortOrder_Blacklist='Ascending'
                    EnableUserData_Blacklist='True'
                    Recursive_Blacklist='True'
                    EnableImages_Blacklist='False'
                    if (cfg.max_age_audio >= 0):
                        IsPlayedState_Blacklist=''
                    else:
                        IsPlayedState_Blacklist='True'

                #Initialize api_query_handler() variables for Favorited media items
                StartIndex_Favorited=0
                TotalItems_Favorited=1
                QueryLimit_Favorited=1
                QueriesRemaining_Favorited=True
                APIDebugMsg_Favorited='audiobook_Favorited_media_data'

                #Build query for Favorited media items
                IncludeItemTypes_Favorited='Audio,Book,MusicAlbum,Playlist,CollectionFolder'
                FieldsState_Favorited='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                SortBy_Favorited='AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                SortOrder_Favorited='Ascending'
                EnableUserData_Favorited='True'
                Recursive_Favorited='True'
                EnableImages_Favorited='False'
                IsFavorite='True'

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_BlackTagged=0
                TotalItems_BlackTagged=1
                QueryLimit_BlackTagged=1
                QueriesRemaining_BlackTagged=True
                APIDebugMsg_BlackTagged='audiobook_favortied_media_data'

                #Build query for tagged media items
                IncludeItemTypes_BlackTagged='Audio,Book,MusicAlbum,Playlist,CollectionFolder'
                FieldsState_BlackTagged='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                SortBy_BlackTagged='ParentIndexNumber,IndexNumber,Name'
                SortOrder_BlackTagged='Ascending'
                EnableUserData_Blacktagged='True'
                Recursive_Tagged_Blacktagged='True'
                EnableImages_Blacktagged='False'
                #Encode blacktags so they are url acceptable
                BlackTags_Tagged=urllib.parse.quote(blacktags.replace(',','|'))

                #Initialize api_query_handler() variables for tagged media items
                StartIndex_WhiteTagged=0
                TotalItems_WhiteTagged=1
                QueryLimit_WhiteTagged=1
                QueriesRemaining_WhiteTagged=True
                APIDebugMsg_WhiteTagged='audiobook_favortied_media_data'

                #Build query for tagged media items
                IncludeItemTypes_WhiteTagged='Audio,MusicAlbum,Playlist,CollectionFolder'
                FieldsState_WhiteTagged='Id,ParentId,Path,Tags,MediaSources,DateCreated,Genres,Studios,ArtistItems,AlbumId,AlbumArtists'
                SortBy_WhiteTagged='ParentIndexNumber,IndexNumber,Name'
                SortOrder_WhiteTagged='Ascending'
                EnableUserData_Whitetagged='True'
                Recursive_Tagged_Whitetagged='True'
                EnableImages_Whitetagged='False'
                #Encode whitetags so they are url acceptable
                WhiteTags_Tagged=urllib.parse.quote(whitetags.replace(',','|'))

                QueryItemsRemaining_All=True

                while (QueryItemsRemaining_All):

                    if not (LibraryID == ''):
                        #Built query for watched items in blacklists
                        apiQuery_Blacklist=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID + '&IncludeItemTypes=' + IncludeItemTypes_Blacklist +
                        '&StartIndex=' + str(StartIndex_Blacklist) + '&Limit=' + str(QueryLimit_Blacklist) + '&IsPlayed=' + IsPlayedState_Blacklist +
                        '&Fields=' + FieldsState_Blacklist + '&Recursive=' + Recursive_Blacklist + '&SortBy=' + SortBy_Blacklist + '&SortOrder=' + SortOrder_Blacklist +
                        '&EnableImages=' + EnableImages_Blacklist + '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacklist + '&EnableUserData=' + EnableUserData_Blacklist + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        data_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,QueriesRemaining_Blacklist=api_query_handler(apiQuery_Blacklist,StartIndex_Blacklist,TotalItems_Blacklist,QueryLimit_Blacklist,APIDebugMsg_Blacklist)
                    else:
                        #When no libraries are blacklisted; simulate an empty query being returned
                        #this will prevent trying to compare to an empty blacklist string '' to the whitelist libraries later on
                        data_Blacklist={'Items':[],'TotalRecordCount':0}
                        QueryLimit_Blacklist=0
                        QueriesRemaining_Blacklist=False

                    #Built query for Favorited media items
                    apiQuery_Favorited=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + LibraryID + '&IncludeItemTypes=' + IncludeItemTypes_Favorited +
                    '&StartIndex=' + str(StartIndex_Favorited) + '&Limit=' + str(QueryLimit_Favorited) + '&Fields=' + FieldsState_Favorited +
                    '&Recursive=' + Recursive_Favorited + '&SortBy=' + SortBy_Favorited + '&SortOrder=' + SortOrder_Favorited + '&EnableImages=' + EnableImages_Favorited +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Favorited + '&IsFavorite=' + IsFavorite + '&EnableUserData=' + EnableUserData_Favorited + '&api_key=' + auth_key)

                    #Send the API query for for Favorited media items
                    data_Favorited,StartIndex_Favorited,TotalItems_Favorited,QueryLimit_Favorited,QueriesRemaining_Favorited=api_query_handler(apiQuery_Favorited,StartIndex_Favorited,TotalItems_Favorited,QueryLimit_Favorited,APIDebugMsg_Favorited)

                    #Built query for blacktagged media items
                    apiQuery_BlackTagged=(server_url + '/Users/' + user_key  + '/Items?IncludeItemTypes=' + IncludeItemTypes_BlackTagged +
                    '&StartIndex=' + str(StartIndex_BlackTagged) + '&Limit=' + str(QueryLimit_BlackTagged) + '&Fields=' + FieldsState_BlackTagged +
                    '&Recursive=' + Recursive_Tagged_Blacktagged + '&SortBy=' + SortBy_BlackTagged + '&SortOrder=' + SortOrder_BlackTagged + '&EnableImages=' + EnableImages_Blacktagged +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Blacktagged + '&Tags=' + BlackTags_Tagged + '&EnableUserData=' + EnableUserData_Blacktagged + '&api_key=' + auth_key)

                    #Check if blacktag is not an empty string
                    if not (BlackTags_Tagged == ''):
                        #Send the API query for for blacktagged media items
                        data_Blacktagged,StartIndex_BlackTagged,TotalItems_BlackTagged,QueryLimit_BlackTagged,QueriesRemaining_BlackTagged=api_query_handler(apiQuery_BlackTagged,StartIndex_BlackTagged,TotalItems_BlackTagged,QueryLimit_BlackTagged,APIDebugMsg_BlackTagged)
                    else: #(BlackTags_Tagged == '')
                        data_Blacktagged={'Items':[],'TotalRecordCount':0}
                        QueryLimit_BlackTagged=0
                        QueriesRemaining_BlackTagged=False

                    #Built query for whitetagged media items
                    apiQuery_WhiteTagged=(server_url + '/Users/' + user_key  + '/Items?IncludeItemTypes=' + IncludeItemTypes_WhiteTagged +
                    '&StartIndex=' + str(StartIndex_WhiteTagged) + '&Limit=' + str(QueryLimit_WhiteTagged) + '&Fields=' + FieldsState_WhiteTagged +
                    '&Recursive=' + Recursive_Tagged_Whitetagged + '&SortBy=' + SortBy_WhiteTagged + '&SortOrder=' + SortOrder_WhiteTagged + '&EnableImages=' + EnableImages_Whitetagged +
                    '&CollapseBoxSetItems=' + CollapseBoxSetItems_Whitetagged + '&Tags=' + WhiteTags_Tagged + '&EnableUserData=' + EnableUserData_Whitetagged + '&api_key=' + auth_key)

                    #Check if whitetag is not an empty string
                    if not (WhiteTags_Tagged == ''):
                        #Send the API query for for whitetagged media items
                        data_Whitetagged,StartIndex_WhiteTagged,TotalItems_WhiteTagged,QueryLimit_WhiteTagged,QueriesRemaining_WhiteTagged=api_query_handler(apiQuery_WhiteTagged,StartIndex_WhiteTagged,TotalItems_WhiteTagged,QueryLimit_WhiteTagged,APIDebugMsg_WhiteTagged)
                    else: #(WhiteTags_Tagged == '')
                        data_Whitetagged={'Items':[],'TotalRecordCount':0}
                        QueryLimit_WhiteTagged=0
                        QueriesRemaining_WhiteTagged=False

                    #Define reasoning for lookup
                    APIDebugMsg_Favortied_Child='favortied child'
                    data_Favorited_Children=getChildren_favoriteMetaData(user_key,data_Favorited)
                    #Define reasoning for lookup
                    APIDebugMsg_Blacktag_Child='blacktag'
                    data_Blacktagged_Children=getChildren_tagMetaData(user_key,data_Blacktagged,cfg.blacktag,APIDebugMsg_Blacktag_Child)
                    #Define reasoning for lookup
                    APIDebugMsg_Whitetag_Child='whitetag'
                    data_Whitetagged_Children=getChildren_tagMetaData(user_key,data_Whitetagged,cfg.whitetag,APIDebugMsg_Whitetag_Child)
                    
                    #Combine dictionaries into list of dictionaries
                    #Order here is important [0-Fav,1-FavChid,2-Whitetag,3-WhitetagChild,4-BlackTag,5-BlacktagChild,6-Blacklist]
                    data_list=[data_Favorited,data_Favorited_Children,data_Whitetagged,data_Whitetagged_Children,data_Blacktagged,data_Blacktagged_Children,data_Blacklist]

                    #Combine remaining query items into list of dictionaries
                    QueryLimit_list=[QueryLimit_Blacklist,QueryLimit_Favorited,QueryLimit_BlackTagged]

                    #Determine if we are done processing queries or if there are still queries to be sent
                    QueryItemsRemaining_All=(QueriesRemaining_Blacklist | QueriesRemaining_Favorited | QueriesRemaining_BlackTagged | QueriesRemaining_WhiteTagged)

                    #Determine if media item is to be deleted or kept
                    #Loop thru each dictionary in data_list[#]
                    for data in data_list:

                        #Loop thru each dictionary[item]
                        for item in data['Items']: 

                            #Check if item was already processed for this user
                            if not (item['Id'] in user_processed_itemsId_list):
                                user_processed_itemsId_list.add(item['Id'])

                                media_found=True

                                itemIsMonitored=False
                                if (item['Type'] == 'Audio'):
                                    for mediasource in item['MediaSources']:
                                        itemIsMonitored=get_isItemMonitored(mediasource)

                                #find media item is ready to delete
                                if (itemIsMonitored):

                                    #establish max cutoff date for media item
                                    if (cfg.max_age_audiobook >= 0):
                                        max_cut_off_date_audiobook=datetime.strptime(item['DateCreated'], '%Y-%m-%dT%H:%M:%S.' + item['DateCreated'].split(".")[1]) + timedelta(cfg.max_age_audiobook)
                                    else:
                                        max_cut_off_date_audiobook=date_time_now=datetime.utcnow() + timedelta(1)

                                    #Get if media item is set as favorite
                                    if ((does_key_exist(item,'UserData')) and (does_key_exist(item['UserData'],'IsFavorite')) and (item['UserData']['IsFavorite'])):
                                        itemisfav_AUDIOBOOK=True
                                    else:
                                        itemisfav_AUDIOBOOK=get_isfav_AUDIOBOOK_ADVANCED(item,user_key,'AudioBook')

                                    #Store media item's favorite state when multiple users are monitored and we want to keep media items based on any user favoriting the media item
                                    if ((cfg.keep_favorites_audiobook == 2) and (itemisfav_AUDIOBOOK)):
                                        isfav_byUserId_Audio[user_key][item['Id']] = itemisfav_AUDIOBOOK

                                    itemIsWhiteListed=False
                                    itemIsWhiteListedTaggedNotWatched=False
                                    #Store media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                    if (cfg.multiuser_whitelist_audiobook == 1):
                                        #Get if media item is whitelisted
                                        for wllib_pos in range(len(user_wllib_keys_json)):
                                            if not (wllib_pos == currentPosition):
                                                itemIsWhiteListed, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                                                #Save media item's whitelist state when multiple users are monitored and we want to keep media items based on any user whitelisting the parent library
                                                if (itemIsWhiteListed):
                                                    audiobook_whitelists.add(item['Id'])
                                                    if bool(cfg.DEBUG):
                                                        iswhitelist_byUserId[user_key][item['Id']] = itemIsWhiteListed
                                            else:
                                                #media item could be seen due to matching tag and not watched state
                                                itemIsWhiteListedTaggedNotWatched, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])
                                    else:
                                        #Get if media item is whitelisted
                                        for wllib_pos in range(len(user_wllib_keys_json)):
                                            if (wllib_pos == currentPosition):
                                                #media item could be seen due to matching tag and not watched state
                                                itemIsWhiteListedTaggedNotWatched, itemWhiteListedValue=get_isItemMatching(LibraryID, user_wllib_keys_json[wllib_pos])

                                    #Determine what to show based on whitelist outputs
                                    if ((itemIsWhiteListed == False) and (itemIsWhiteListedTaggedNotWatched == False)):
                                        displayIsWhiteListed=False
                                    elif ((itemIsWhiteListed == False) and (itemIsWhiteListedTaggedNotWatched == True)):
                                        displayIsWhiteListed=True
                                    elif ((itemIsWhiteListed == True) and (itemIsWhiteListedTaggedNotWatched == False)):
                                        displayIsWhiteListed=False
                                    elif ((itemIsWhiteListed == True) and (itemIsWhiteListedTaggedNotWatched == True)):
                                        displayIsWhiteListed=True

                                    #Override for when LibraryID == ''
                                    #This means all libraries are whitelisted for this user
                                    if (LibraryID == ''):
                                        displayIsWhiteListed=True

                                    audiobook_whitetaglists,itemIsWhiteTagged=get_isItemTagged(whitetags,audiobook_whitetaglists,item,user_key,'whitetag')

                                    itemIsBlackTagged=False
                                    #Skip blacktagging if already whitetagged
                                    if not (itemIsWhiteTagged):
                                        audiobook_blacktaglists,itemIsBlackTagged=get_isItemTagged(blacktags,audiobook_blacktaglists,item,user_key,'blacktag')

                                    if (does_key_exist(item['UserData'], 'Played')):

                                        if (
                                        ((cfg.played_age_audiobook >= 0) and
                                        (item['UserData']['PlayCount'] >= 1) and
                                        (cut_off_date_audiobook > parse(item['UserData']['LastPlayedDate'])) and
                                        (not bool(cfg.keep_favorites_audiobook) or (not itemisfav_AUDIOBOOK)) and
                                        (not itemIsWhiteListed) and (not itemIsWhiteTagged))
                                        or
                                        ((cfg.max_age_audiobook >= 0) and
                                        (max_cut_off_date_audiobook <= datetime.utcnow()) and
                                        (((not bool(cfg.keep_favorites_audiobook)) or (not itemisfav_AUDIOBOOK)) and
                                        ((not bool(cfg.max_keep_favorites_audiobook)) or (not itemisfav_AUDIOBOOK))) and
                                        (not itemIsWhiteListed) and (not itemIsWhiteTagged))
                                        ):
                                            try:
                                                #Fill in the blanks; same as audio
                                                item=prep_audioOutput(item)

                                                item_details=(item['Type'] + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Book: ' + item['Album'] + ' - Author: ' + item['Artists'][0] +
                                                            ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - ' + get_days_since_created(item['DateCreated']) + ' - Favorite: ' + str(itemisfav_AUDIOBOOK) +
                                                            ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - Tag Match: ' + str(itemIsBlackTagged or itemIsWhiteTagged) + ' - TrackID: ' + item['Id'])
                                            except (KeyError, IndexError):
                                                item_details=item['Type'] + ' - Track: ' + item['Name'] + ' - ' + item['Id']
                                                if bool(cfg.DEBUG):
                                                    #DEBUG
                                                    print('\nError encountered - Delete AudioBook: \nitem: ' + str(item) + '\nitem' + str(item))
                                            print(':*[DELETE] -     ' + item_details)
                                            deleteItems.append(item)
                                        else:
                                            try:
                                                #Fill in the blanks; same as audio
                                                item=prep_audioOutput(item)

                                                item_details=(item['Type'] + ' - Track #' + str(item['IndexNumber']) + ': ' + item['Name'] + ' - Book: ' + item['Album'] + ' - Author: ' + item['Artists'][0] +
                                                            ' - ' + get_days_since_played(item['UserData']['LastPlayedDate']) + ' - ' + get_days_since_created(item['DateCreated']) + ' - Favorite: ' + str(itemisfav_AUDIOBOOK) +
                                                            ' - Whitelisted: ' + str(itemIsWhiteListed) + ' - Tag Match: ' + str(itemIsBlackTagged or itemIsWhiteTagged) + ' - TrackID: ' + item['Id'])
                                            except (KeyError, IndexError):
                                                item_details=item['Type'] + ' - Track: ' + item['Name'] + ' - ' + item['Id']
                                                if bool(cfg.DEBUG):
                                                    #DEBUG
                                                    print('\nError encountered - Keep AudioBook: \nitem: ' + str(item) + '\nitem' + str(item))
                                            print(':[KEEPING] -     ' + item_details)

############# End Media Types #############

        if (not all_media_disabled):
            if not (media_found):
                print('[NO PLAYED ITEMS]')

        print('-----------------------------------------------------------')
        currentPosition+=1

    #When multiple users and keep_favorite_xyz==2 Determine media items to keep and remove them from deletion list
    #When not multiple users this will just clean up the deletion list
    deleteItems=get_isfav_ByMultiUser(user_keys_json, isfav_byUserId_Movie, deleteItems)
    deleteItems=get_isfav_ByMultiUser(user_keys_json, isfav_byUserId_Episode, deleteItems)
    deleteItems=get_isfav_ByMultiUser(user_keys_json, isfav_byUserId_Audio, deleteItems)
    if ((cfg.server_brand == 'jellyfin') and hasattr(cfg, 'multiuser_whitelist_audiobook')):
        deleteItems=get_isfav_ByMultiUser(user_keys_json, isfav_byUserId_AudioBook, deleteItems)

    #When multiple users and multiuser_whitelist_xyz==1 Determine media items to keep and remove them from deletion list
    deleteItems=get_iswhitelist_ByMultiUser(user_keys_json, list(movie_whitelists), deleteItems)
    deleteItems=get_iswhitelist_ByMultiUser(user_keys_json, list(episode_whitelists), deleteItems)
    deleteItems=get_iswhitelist_ByMultiUser(user_keys_json, list(audio_whitelists), deleteItems)
    if ((cfg.server_brand == 'jellyfin') and hasattr(cfg, 'multiuser_whitelist_audiobook')):
        deleteItems=get_iswhitelist_ByMultiUser(user_keys_json, list(audiobook_whitelists), deleteItems)

    #When whitetagged; Determine media items to keep and remove them from deletion list
    deleteItems=get_iswhitetagged_ByMultiUser(user_keys_json, movie_whitetaglists, deleteItems)
    deleteItems=get_iswhitetagged_ByMultiUser(user_keys_json, episode_whitetaglists, deleteItems)
    deleteItems=get_iswhitetagged_ByMultiUser(user_keys_json, audio_whitetaglists, deleteItems)
    if ((cfg.server_brand == 'jellyfin') and hasattr(cfg, 'multiuser_whitelist_audiobook')):
        deleteItems=get_iswhitetagged_ByMultiUser(user_keys_json, audiobook_whitetaglists, deleteItems)

    if bool(cfg.DEBUG):
        print('-----------------------------------------------------------')
        print('')
        print('isfav_MOVIE: ')
        print(isfav_MOVIE)
        print('')
        print('isfav_EPISODE: ')
        print(isfav_EPISODE)
        print('')
        print('isfav_AUDIO: ')
        print(isfav_AUDIO)
        print('')
        if ((cfg.server_brand == 'jellyfin') and hasattr(cfg, 'keep_favorites_audiobook')):
            print('isfav_AUDIOBOOK: ')
            print(isfav_AUDIOBOOK)
            print('')

    print('\n')
    return(deleteItems)


#list and delete items past played threshold
def list_delete_items(deleteItems):
    #List items to be deleted
    print('-----------------------------------------------------------')
    print('Summary Of Deleted Media:')
    if not bool(cfg.REMOVE_FILES):
        print('* Trial Run Mode       ')
        print('* REMOVE_FILES=\'TRUE\'')
        print('* No Media Deleted     ')
        print('* Items = ' + str(len(deleteItems)))
        print('-----------------------------------------------------------')
    else:
        print('* Items Deleted = ' + str(len(deleteItems)) + '    *')
        print('-----------------------------------------------------------')

    if len(deleteItems) > 0:
        for item in deleteItems:
            if item['Type'] == 'Movie':
                item_details='[DELETED]     ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'Episode':
                try:
                    item_details='[DELETED]   ' + item['Type'] + ' - ' + item['SeriesName'] + ' - ' + get_season_episode(item['ParentIndexNumber'], item['IndexNumber']) + ' - ' + item['Name'] + ' - ' + item['Id']
                except (KeyError, IndexError):
                    item_details='[DELETED]   ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
                    if bool(cfg.DEBUG):
                        #DEBUG
                        print('Error encountered - Delete Episode: \n\n' + str(item))
            elif item['Type'] == 'Audio':
                item_details='[DELETED]     ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            elif item['Type'] == 'AudioBook':
                item_details='[DELETED] ' + item['Type'] + ' - ' + item['Name'] + ' - ' + item['Id']
            else: # item['Type'] == 'Unknown':
                pass
            #Delete media item
            delete_item(item['Id'])
            print(item_details)
    else:
        print('[NO ITEMS TO DELETE]')

    print('-----------------------------------------------------------')
    print('\n')
    print('-----------------------------------------------------------')
    print('Done.')
    print('-----------------------------------------------------------')
    print('')


#api call to delete items
def delete_item(itemID):
    #build API delete request for specified media item
    url=cfg.server_url + '/Items/' + itemID + '?api_key=' + cfg.auth_key

    req = request.Request(url,method='DELETE')

    if bool(cfg.DEBUG):
        #DEBUG
        print(itemID)
        print(url)
        print(req)

    #check if in dry-run mode
    #if REMOVE_FILES='FALSE'; exit this function
    #else REMOVE_FILES='TRUE'; send request to Emby/Jellyfin to delete specified media item
    if not (cfg.REMOVE_FILES):
        return
    else:
        try:
            request.urlopen(req)
        except Exception:
            print('generic exception: ' + traceback.format_exc())
        return


#Check blacklist and whitelist config variables are as expected
def cfgCheck_forLibraries(check_list, user_check_list, config_var_name):

    error_found_in_media_cleaner_config_py=''

    for check_irt in check_list:
        #Check if userid exists
        if (does_key_exist(check_irt, 'userid')):
            #Set user tracker to zero
            user_found=0
            #Check user from user_keys is also a user in this blacklist/whitelist
            for user_check in user_check_list:
                if (user_check in check_irt['userid']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' user ' + check_irt['userid'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' user ' + check_irt['userid'] + ' is seen more than once\n'
            #Check userid is string
            if not (isinstance(check_irt['userid'], str)):
                error_found_in_media_cleaner_config_py+='TypeError: In ' + config_var_name + ' the userid is not a string for at least one user\n'
            else:
                #Check userid is 32 character long alphanumeric
                if not (
                    (check_irt['userid'].isalnum()) and
                    (len(check_irt['userid']) == 32)
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' + at least one userid is not a 32-character alphanumeric string\n'
        else:
            error_found_in_media_cleaner_config_py+='NameError: In ' + config_var_name + ' the userid key is missing for at least one user\n'
        #Check if length is >1; which means a userid and at least one library are stored
        if (len(check_irt) > 1):
            #Get number of elements
            for num_elements in check_irt:
                #First element is always userid; ignore element at position zero
                if ((not (num_elements == 'userid')) and (int(num_elements) > 0)):
                    #Set library key trackers to zero
                    libid_found=0
                    collectiontype_found=0
                    networkpath_found=0
                    path_found=0
                    #Check if this num_element exists before proceeding
                    if (does_key_exist(check_irt, num_elements)):
                        for libinfo in check_irt[num_elements]:
                            if (libinfo == 'libid'):
                                libid_found += 1
                                #Check libid is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_media_cleaner_config_py+='TypeError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the libid for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check libid is 32 character long alphanumeric
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].isalnum()) and
                                        (len(check_irt[str(num_elements)][libinfo]) == 32)
                                    ):
                                        error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the libid for library with key' + num_elements + ' is not a 32 character alphanumeric string\n'
                            elif (libinfo == 'collectiontype'):
                                collectiontype_found += 1
                                #Check collectiontype is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_media_cleaner_config_py+='TypeError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the collectiontype for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check collectiontype is all alpha characters
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].isalpha())
                                    ):
                                        error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the collectiontype for library with key' + num_elements + ' is not a 32 character alphanumeric string\n'
                                    else:
                                        #TODO verify we only see specific collection types (i.e. tvshows, movies, music, books, etc...)
                                        pass
                            elif (libinfo == 'networkpath'):
                                networkpath_found += 1
                                #Check networkpath is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_media_cleaner_config_py+='TypeError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the networkpath for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check networkpath has no backslashes
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].find('\\') < 0)
                                    ):
                                        error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' user ' + check_irt['userid'] + ' the networkpath for library with key' + num_elements + ' cannot have any forward slashes \'\\\'\n'
                            elif (libinfo == 'path'):
                                path_found += 1
                                #Check path is string
                                if not (isinstance(check_irt[str(num_elements)][libinfo], str)):
                                    error_found_in_media_cleaner_config_py+='TypeError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the path for library with key' + num_elements + ' is not a string\n'
                                else:
                                    #Check path has no backslashes
                                    if not (
                                        (check_irt[str(num_elements)][libinfo].find('\\') < 0)
                                    ):
                                        error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' the path for library with key' + num_elements + ' cannot have any backslashes \'\\\'\n'
                        if (libid_found == 0):
                            error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key libid is missing\n'
                        if (libid_found > 1):
                            error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key libid is seen more than once\n'
                        if (collectiontype_found == 0):
                            error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key collectiontype is missing\n'
                        if (collectiontype_found > 1):
                            error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key collectiontype is seen more than once\n'
                        if (networkpath_found == 0):
                            error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key networkpath is missing\n'
                        if (networkpath_found > 1):
                            error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key networkpath is seen more than once\n'
                        if (path_found == 0):
                            error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key path is missing\n'
                        if (path_found > 1):
                            error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' for user ' + check_irt['userid'] + ' key path is seen more than once\n'
                    else:
                        error_found_in_media_cleaner_config_py+='ValueError: In ' + config_var_name + ' user ' + check_irt['userid'] + ' key'+ str(num_elements) +' does not exist\n'
    return(error_found_in_media_cleaner_config_py)


#Check select config variables are as expected
def cfgCheck():

    errorfound=False
    error_found_in_media_cleaner_config_py=''
    #Todo: find clean way to put cfg.variable_names in a dict/list/etc... and use the dict/list/etc... to call the varibles by name in a for loop

    if hasattr(cfg, 'played_age_movie'):
        check=cfg.played_age_movie
        check_played_age_movie=check
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: played_age_movie must be an integer; valid range -1 thru 730500\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The played_age_movie variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'played_age_episode'):
        check=cfg.played_age_episode
        check_played_age_episode=check
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: played_age_episode must be an integer; valid range -1 thru 730500\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The played_age_episode variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'played_age_audio'):
        check=cfg.played_age_audio
        check_played_age_audio=check
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: played_age_audio must be an integer; valid range -1 thru 730500\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The played_age_audio variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'played_age_audiobook'):
                check=cfg.played_age_audiobook
                check_played_age_audiobook=check
                if (
                    not ((type(check) is int) and
                    (check >= -1) and
                    (check <= 730500))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: played_age_audiobook must be an integer; valid range -1 thru 730500\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The played_age_audiobook variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_movie'):
        check=cfg.keep_favorites_movie
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_movie must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_movie variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_episode'):
        check=cfg.keep_favorites_episode
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_episode must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_episode variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_audio'):
        check=cfg.keep_favorites_audio
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_audio must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_audio variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'keep_favorites_audiobook'):
                check=cfg.keep_favorites_audiobook
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_audiobook must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_audiobook variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_movie_genre'):
        check=cfg.keep_favorites_advanced_movie_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_movie_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_movie_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_movie_library_genre'):
        check=cfg.keep_favorites_advanced_movie_library_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_movie_library_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_movie_library_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_episode_genre'):
        check=cfg.keep_favorites_advanced_episode_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_episode_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_episode_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_season_genre'):
        check=cfg.keep_favorites_advanced_season_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_season_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_season_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_series_genre'):
        check=cfg.keep_favorites_advanced_series_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_series_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_series_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_tv_library_genre'):
        check=cfg.keep_favorites_advanced_tv_library_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_tv_library_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_tv_library_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_tv_studio_network'):
        check=cfg.keep_favorites_advanced_tv_studio_network
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_tv_studio_network must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_tv_studio_network variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_tv_studio_network_genre'):
        check=cfg.keep_favorites_advanced_tv_studio_network_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_tv_studio_network_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_tv_studio_network_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_track_genre'):
        check=cfg.keep_favorites_advanced_track_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_track_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_track_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_album_genre'):
        check=cfg.keep_favorites_advanced_album_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_album_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_album_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_music_library_genre'):
        check=cfg.keep_favorites_advanced_music_library_genre
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_music_library_genre must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_music_library_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_track_artist'):
        check=cfg.keep_favorites_advanced_track_artist
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_track_artist must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_track_artist variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_album_artist'):
        check=cfg.keep_favorites_advanced_album_artist
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_album_artist must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_album_artist variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'keep_favorites_advanced_music_library_artist'):
        check=cfg.keep_favorites_advanced_music_library_artist
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 2))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_music_library_artist must be an integer; valid range 0 thru 2\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_music_library_artist variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'keep_favorites_advanced_audio_book_track_genre'):
                check=cfg.keep_favorites_advanced_audio_book_track_genre
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_audio_book_track_genre must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_audio_book_track_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'keep_favorites_advanced_audio_book_genre'):
                check=cfg.keep_favorites_advanced_audio_book_genre
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_audio_book_genre must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_audio_book_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'keep_favorites_advanced_audio_book_library_genre'):
                check=cfg.keep_favorites_advanced_audio_book_library_genre
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_audio_book_library_genre must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_audio_book_library_genre variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'keep_favorites_advanced_audio_book_track_author'):
                check=cfg.keep_favorites_advanced_audio_book_track_author
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_audio_book_track_author must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_audio_book_track_author variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'keep_favorites_advanced_audio_book_author'):
                check=cfg.keep_favorites_advanced_audio_book_author
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_audio_book_author must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_audio_book_author variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'keep_favorites_advanced_audio_book_library_author'):
                check=cfg.keep_favorites_advanced_audio_book_library_author
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 2))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: keep_favorites_advanced_audio_book_library_author must be an integer; valid range 0 thru 2\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The keep_favorites_advanced_audio_book_library_author variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'multiuser_whitelist_episode'):
        check=cfg.multiuser_whitelist_episode
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: multiuser_whitelist_episode must be an integer; valid range 0 thru 1\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The multiuser_whitelist_episode variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'multiuser_whitelist_audio'):
        check=cfg.multiuser_whitelist_audio
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: multiuser_whitelist_audio must be an integer; valid range 0 thru 1\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The multiuser_whitelist_audio variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'multiuser_whitelist_audiobook'):
                check=cfg.multiuser_whitelist_audiobook
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 1))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: multiuser_whitelist_audiobook must be an integer; valid range 0 thru 1\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The multiuser_whitelist_audiobook variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'REMOVE_FILES'):
        check=cfg.REMOVE_FILES
        if (
            not ((type(check) is bool) and
            #(check.isupper()) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: REMOVE_FILES must be a boolean; valid values True and False\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The REMOVE_FILES variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'UPDATE_CONFIG'):
        check=cfg.UPDATE_CONFIG
        if (
            not ((type(check) is bool) and
            #(check.isupper()) and
            ((check == True) or
            (check == False)))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: UPDATE_CONFIG must be a boolean; valid values True and False\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The UPDATE_CONFIG variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'blacktag'):
        check=cfg.blacktag
        if not (
            (type(check) is str) and
            (check.find('\\') < 0)
        ):
            error_found_in_media_cleaner_config_py+='ValueError: Blacktag(s) must be a single string with a comma separating multiple tag names; backlash \'\\\' not allowed\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The blacktag variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'whitetag'):
        check=cfg.whitetag
        if not (
            (type(check) is str) and
            (check.find('\\') < 0)
        ):
            error_found_in_media_cleaner_config_py+='ValueError: Whitetag(s) must be a single string with a comma separating multiple tag names; backlash \'\\\' not allowed\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The whitetag variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'max_age_movie'):
        check=cfg.max_age_movie
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500) and
            (((check >= check_played_age_movie) and (check >= 0)) or
            (check == -1)))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: max_age_movie must be an integer greater than corresponding played_age_xyz; valid range -1 thru 730500\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The max_age_movie variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'max_age_episode'):
        check=cfg.max_age_episode
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500) and
            (((check >= check_played_age_episode) and (check >= 0)) or
            (check == -1)))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: max_age_episode must be an integer greater than corresponding played_age_xyz; valid range -1 thru 730500\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The max_age_episode variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'max_age_audio'):
        check=cfg.max_age_audio
        if (
            not ((type(check) is int) and
            (check >= -1) and
            (check <= 730500) and
            (((check >= check_played_age_audio) and (check >= 0)) or
            (check == -1)))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: max_age_audio must be an integer greater than corresponding played_age_xyz; valid range -1 thru 730500\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The max_age_audio variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'max_age_audiobook'):
                check=cfg.max_age_audiobook
                if (
                    not ((type(check) is int) and
                    (check >= -1) and
                    (check <= 730500) and
                    (((check >= check_played_age_audiobook) and (check >= 0)) or
                    (check == -1)))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: max_age_audiobook must be an integer greater than corresponding played_age_xyz; valid range -1 thru 730500\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The max_age_audiobook variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'max_keep_favorites_movie'):
        check=cfg.max_keep_favorites_movie
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: max_keep_favorites_movie must be an integer; valid range 0 thru 1\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The max_keep_favorites_movie variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'max_keep_favorites_episode'):
        check=cfg.max_keep_favorites_episode
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: max_keep_favorites_episode must be an integer; valid range 0 thru 1\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The max_keep_favorites_episode variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'max_keep_favorites_audio'):
        check=cfg.max_keep_favorites_audio
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: max_keep_favorites_audio must be an integer; valid range 0 thru 1\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The max_keep_favorites_audio variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (check == 'jellyfin'):
            if hasattr(cfg, 'max_keep_favorites_audiobook'):
                check=cfg.max_keep_favorites_audiobook
                if (
                    not ((type(check) is int) and
                    (check >= 0) and
                    (check <= 1))
                ):
                    error_found_in_media_cleaner_config_py+='ValueError: max_keep_favorites_audiobook must be an integer; valid range 0 thru 1\n'
            else:
                error_found_in_media_cleaner_config_py+='NameError: The max_keep_favorites_audiobook variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_brand'):
        check=cfg.server_brand
        if (
            not ((type(check) is str) and
            ((check == 'emby') or
            (check == 'jellyfin')))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: server_brand must be a string with a value of \'emby\' or \'jellyfin\'\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The server_brand variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'server_url'):
        check=cfg.server_url
        if (
            not (type(check) is str)
        ):
            error_found_in_media_cleaner_config_py+='ValueError: server_url must be a string\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The server_url variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'auth_key'):
        check=cfg.auth_key
        if (
            not ((type(check) is str) and
            (len(check) == 32) and
            (str(check).isalnum()))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: auth_key must be a 32-character alphanumeric string\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The auth_key variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'user_keys'):
        check=cfg.user_keys
        check_list=json.loads(check)
        user_check_list=check_list
        check_user_keys_length=len(check_list)
        for check_irt in check_list:
            if (
                not ((type(check_irt) is str) and
                (len(check_irt) == 32) and
                (str(check_irt).isalnum()))
            ):
                error_found_in_media_cleaner_config_py+='ValueError: user_keys must be a single list with a comma separating multiple users\' keys; each user key must be a 32-character alphanumeric string\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The user_keys variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'script_behavior'):
        check=cfg.script_behavior
        if (
            not (type(check) is str) and
            ((check == 'blacklist') or (check == 'whitelist'))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: script_behavior must be a string; valid values \'blacklist\' or \'whitelist\'\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The script_behavior variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'user_bl_libs'):
        check=cfg.user_bl_libs
        check_list=json.loads(check)
        check_user_bllibs_length=len(check_list)
        #Check number of users matches the number of blacklist entries
        if not (check_user_bllibs_length == check_user_keys_length):
            error_found_in_media_cleaner_config_py+='ValueError: Number of configured users does not match the number of configured blacklists\n'
        else:
            error_found_in_media_cleaner_config_py+=cfgCheck_forLibraries(check_list, user_check_list, 'user_bl_libs')

    if hasattr(cfg, 'user_wl_libs'):
        check=cfg.user_wl_libs
        check_list=json.loads(check)
        check_user_wllibs_length=len(check_list)
        #Check number of users matches the number of whitelist entries
        if not (check_user_wllibs_length == check_user_keys_length):
            error_found_in_media_cleaner_config_py+='ValueError: Number of configured users does not match the number of configured whitelists\n'
        else:
            error_found_in_media_cleaner_config_py+=cfgCheck_forLibraries(check_list, user_check_list, 'user_wl_libs')

    if hasattr(cfg, 'api_query_attempts'):
        check=cfg.api_query_attempts
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 16))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: api_query_attempts must be an integer; valid range 0 thru 16\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The api_query_attempts variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'api_query_item_limit'):
        check=cfg.api_query_item_limit
        if (
            not ((type(check) is int) and
            (check >= 1) and
            (check <= 10000))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: api_query_item_limit must be an integer; valid range 0 thru 10000\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The api_query_item_limit variable is missing from media_cleaner_config.py\n'

    if hasattr(cfg, 'DEBUG'):
        check=cfg.DEBUG
        if (
            not ((type(check) is int) and
            (check >= 0) and
            (check <= 1))
        ):
            error_found_in_media_cleaner_config_py+='ValueError: DEBUG must be an integer; valid values 0 and 1\n'
    else:
        error_found_in_media_cleaner_config_py+='NameError: The DEBUG variable is missing from media_cleaner_config.py\n'

    #Bring all errors found to users attention
    if (not error_found_in_media_cleaner_config_py == ''):
        raise RuntimeError('\n' + error_found_in_media_cleaner_config_py)


############# START OF SCRIPT #############

try:
    #try importing the media_cleaner_config.py file
    #if media_cleaner_config.py file does not exsit go to except and create one
    import media_cleaner_config as cfg

    #try assigning the DEBUG variable from media_cleaner_config.py file
    #if DEBUG does not exsit go to except and completely rebuild the media_cleaner_config.py file
    check=cfg.DEBUG
    #removing DEBUG from media_cleaner_config.py file will allow the configuration to be reset

    print('-----------------------------------------------------------')
    print ('\n')

#the exception
except (AttributeError, ModuleNotFoundError):
    #we are here because the media_cleaner_config.py file does not exist
    #this is either the first time the script is running or media_cleaner_config.py file was deleted
    #when this happens create a new media_cleaner_config.py file
    #another possible reason we are here...
    #the above attempt to set check=cfg.DEBUG failed likely because DEBUG is missing from the media_cleaner_config.py file
    #when this happens create a new media_cleaner_config.py file
    update_config = False
    generate_config(None,update_config)

    #exit gracefully after setup
    exit(0)

#check config values are what we expect them to be
cfgCheck()

#check if user wants to update the existing config file
if (hasattr(cfg, 'UPDATE_CONFIG') and (cfg.UPDATE_CONFIG)):
    #check if user intentionally wants to update the config but does not have the script_behavor variable in their config
    if (hasattr(cfg, 'script_behavior')):
        #we are here because we want to add new users to the media_cleaner_config.py file
        generate_config(cfg,cfg.UPDATE_CONFIG)
    else:
        raise NameError('Error! The script_behavior variable is missing from media_cleaner_config.py. It is needed to use the UPDATE_CONFIG functionality.')

    #exit gracefully after conifig update
    exit(0)

#now we can get media items that are ready to be deleted;
deleteItems=get_items()

#show and delete media items
list_delete_items(deleteItems)

############# END OF SCRIPT #############
