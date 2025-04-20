import copy
from mumc_modules.mumc_user_queries import get_all_users_from_media_server
from mumc_modules.mumc_blacklist_whitelist import get_unpreferred_listing_type


#user data class for builder
class user_library_data:

    def __init__(self,user_id='',user_name='',whitelist=[],blacklist=[]):
        self.user_id=user_id
        self.user_name=user_name
        self.whitelist=whitelist
        self.blacklist=blacklist

    def __str__(self):
        return f"UserId: {self.user_id} - Name: {self.user_name} - Whitelist: {self.whitelist} - Blacklist: {self.blacklist}"


#user data class for builder
class user_data(user_library_data):

    def __init__(self,user_id='',user_name='',whitelist=[],blacklist=[],enableAllFolders=False,enabledFolders=[],excludedSubFolders=[],selected=False):
        user_library_data.__init__(self,user_id,user_name,whitelist,blacklist)
        self.enableAllFolders=enableAllFolders
        self.enabledFolders=enabledFolders
        self.excludedSubFolders=excludedSubFolders
        self.selected=selected

    def __str__(self):
        #initialize user selected to false
        self.selected=False

        #loop thru whitelist libraries
        for thisLib in self.whitelist:
            #check if any libraries selected
            if (thisLib.selected):
                #set user selectoin to true if any libraries are selected
                self.selected=True
                break
        #loop thru blacklist libraries
        for thisLib in self.blacklist:
            #check if any libraries selected
            if (thisLib.selected):
                #set user selectoin to true if any libraries are selected
                self.selected=True
                break

        #check if user is selected
        if (self.selected):
            return f"Name: {self.user_name} -"
        else: #(not (self.selected)):
            return f"Name: {self.user_name} - UserId: {self.user_id}"

    def display(self):
        return f"UserId: {self.user_id} - Name: {self.user_name} - Whitelist: {self.whitelist} - Blacklist: {self.blacklist} - AccessToAllFolders: {self.enableAllFolders} - EnabledFolders: {self.enabledFolders} - ExcludedSubfolders: {self.excludedSubFolders} - Selected: {self.selected}"
 
    def userObjectToYAML(self,preferred_listing_type):
        #delcare dictionary and top level keys
        userDataLibDataDict={}
        userDataLibDataDict['user_id']=self.user_id
        userDataLibDataDict['user_name']=self.user_name
        userDataLibDataDict['whitelist']=[]
        userDataLibDataDict['blacklist']=[]

        #get unpreferred listing type
        unpreferred_listing_type=get_unpreferred_listing_type(preferred_listing_type)

        #loop thru user's whitelist libraries
        for thisLib in self.whitelist:
            #delcare sub-dictionary and its top level keys
            libDict={}
            libDict['lib_id']=thisLib.lib_id
            libDict['lib_name']=thisLib.name
            libDict['collection_type']=thisLib.collection_type
            libDict['path']=thisLib.path
            libDict['network_path']=thisLib.network_path
            libDict['subfolder_id']=thisLib.subfolder_id
            libDict['lib_enabled']=thisLib.lib_enabled
            #check if lib is selected
            if (thisLib.selected):
                #when lib selected append to the preferred_listing_type
                userDataLibDataDict[preferred_listing_type].append(libDict)
            else:
                #when lib NOT selected append to the unpreferred_listing_type
                userDataLibDataDict[unpreferred_listing_type].append(libDict)

        #loop thru user's blacklist libraries
        for thisLib in self.blacklist:
            #delcare sub-dictionary and its top level keys
            libDict={}
            libDict['lib_id']=thisLib.lib_id
            libDict['lib_name']=thisLib.name
            libDict['collection_type']=thisLib.collection_type
            libDict['path']=thisLib.path
            libDict['network_path']=thisLib.network_path
            libDict['subfolder_id']=thisLib.subfolder_id
            libDict['lib_enabled']=thisLib.lib_enabled
            #check if lib is selected
            if (thisLib.selected):
                #when lib selected append to the preferred_listing_type
                userDataLibDataDict[preferred_listing_type].append(libDict)
            else:
                #when lib NOT selected append to the unpreferred_listing_type
                userDataLibDataDict[unpreferred_listing_type].append(libDict)

        return userDataLibDataDict

 
def get_all_users(the_dict):
    allUsersList=[]

    #check if disabled users should be monitored
    if (the_dict['admin_settings']['behavior']['users']['monitor_disabled']):
        #send query to server for both enabled and disabled users
        usersList=get_all_users_from_media_server(the_dict)
    else:
        #send query to server for only enabled
        usersList=get_all_users_from_media_server(the_dict,False)

    #loop thru list of all users
    for userInfo in usersList:
        #check if server is emby or jellyfin
        if (the_dict['isEmby']):
            #save user data; emby allows subfolder specific user permissions
            allUsersList.append(user_data(user_id=userInfo['Id'],user_name=userInfo['Name'],whitelist=[],blacklist=[],enableAllFolders=userInfo['Policy']['EnableAllFolders'],enabledFolders=userInfo['Policy']['EnabledFolders'],excludedSubFolders=userInfo['Policy']['ExcludedSubFolders']))
        else:
            #save user data; jellyfin does NOT allow subfolder specific user permissions
            allUsersList.append(user_data(user_id=userInfo['Id'],user_name=userInfo['Name'],whitelist=[],blacklist=[],enableAllFolders=userInfo['Policy']['EnableAllFolders'],enabledFolders=userInfo['Policy']['EnabledFolders'],excludedSubFolders=[]))

    return allUsersList


#remove any already existing users that no longer exist on the server
def clean_all_users(existingUsers,allUsersList):
    #loop thru list of existing users
    for existingUser in existingUsers:
        #loop thru list of all users
        for thisUser in allUsersList:
            #check if userIds match
            #existing userIds that are never matched; are pruned here
            if (existingUser['user_id'] == thisUser.user_id):
                #existing user found transfer whitelist
                thisUser.whitelist=existingUser['whitelist']
                #existing user found transfer blacklist
                thisUser.blacklist=existingUser['blacklist']
                #existing users are selected
                thisUser.selected=True

    return allUsersList


#check if user has access to this library and/or subfolder
def does_user_have_access_to_this_lib_folder(thisUser,thisAllLib):

    #check if user has access to all libraries/subfolders
    if (thisUser.enableAllFolders):
        does_user_have_access=True
    #determine which specific libraries/subfolders a user has access to
    else:
        #check if this lib_id is enabled for this user
        if (str(thisAllLib.lib_id) in thisUser.enabledFolders):
            #check if this subfolder_id is excluded for this user
            if ((str(thisAllLib.lib_id) + '_' + str(thisAllLib.subfolder_id)) in thisUser.excludedSubFolders):
                does_user_have_access=False
            #subfolder_id is included for this user
            else:
                does_user_have_access=True
        #lib_id is disabled for this user
        else:
            does_user_have_access=False

    return does_user_have_access


#remove any existing user libraries not in all_libraries; or any libraries the user does not have permission to access
def clean_all_user_libraries(preferred_listing_type,all_libraries,all_users):
    #loop thru all_users
    for thisUser in all_users:

        #check which listing type was selected
        if (preferred_listing_type == 'whitelist'):
            #whitelisting selected
            thisUserPreferredListType=thisUser.whitelist
            #blacklisting not selected
            thisUserUnpreferredListType=thisUser.blacklist
        else:
            #blacklisting selected
            thisUserPreferredListType=thisUser.blacklist
            #whitelisting not selected
            thisUserUnpreferredListType=thisUser.whitelist

        #loop thru the specific user's selected library listing type
        for thisUserLib in reversed(thisUserPreferredListType):
            #loop thru all_libraries
            for thisAllLib in all_libraries:
                #check if lib_id and subfolder_id match for the specific user's library entry and the library entry from all_libraries (because jellyfin does not have subfolder_ids, path has to be used for comparison)
                if ((thisUserLib['lib_id'] == thisAllLib.lib_id) and (thisUserLib['subfolder_id'] == thisAllLib.subfolder_id) and (thisUserLib['path'] == thisAllLib.path)):
                    #check if user has access to this library folder
                    if (does_user_have_access_to_this_lib_folder(thisUser,thisAllLib)):
                        #create temp copy
                        temp_thisAllLib=copy.copy(thisAllLib)
                        #libraries/subfolders in the preferred listing type are selected
                        temp_thisAllLib.selected=True
                        #store lib_enabled state for existing library
                        temp_thisAllLib.lib_enabled=thisUserLib['lib_enabled']
                        #copy the matching entry from all_libraries to overwrite the existing library
                        thisUserPreferredListType[thisUserPreferredListType.index(thisUserLib)]=copy.copy(temp_thisAllLib)
                        break
            else:
                #library folder no longer exists or user does not have permissoin to access the library folder
                #either way; remove this library from the user
                thisUserPreferredListType.remove(thisUserLib)

        #loop thru the specific user's selected library listing type
        for thisUserLib in reversed(thisUserUnpreferredListType):
            #loop thru all_libraries
            for thisAllLib in all_libraries:
                #check if lib_id and subfolder_id match for the specific user's library entry and the library entry from all_libraries (because jellyfin does not have subfolder_ids, path has to be used for comparison)
                if ((thisUserLib['lib_id'] == thisAllLib.lib_id) and (thisUserLib['subfolder_id'] == thisAllLib.subfolder_id) and (thisUserLib['path'] == thisAllLib.path)):
                    #check if user has access to this library folder
                    if (does_user_have_access_to_this_lib_folder(thisUser,thisAllLib)):
                        #create temp copy
                        temp_thisAllLib=copy.copy(thisAllLib)
                        #store lib_enabled state for existing library
                        temp_thisAllLib.lib_enabled=thisUserLib['lib_enabled']
                        #copy the matching entry from all_libraries to overwrite the existing library
                        thisUserUnpreferredListType[thisUserUnpreferredListType.index(thisUserLib)]=copy.copy(temp_thisAllLib)
                        break
            else:
                #library folder no longer exists or user does not have permissoin to access the library folder
                #either way; remove this library from the user
                thisUserUnpreferredListType.remove(thisUserLib)

    return all_users


#update users with "new" libraries they have permission to access
def update_all_user_libraries(preferred_listing_type,all_libraries,all_users):
    #loop thru all_users
    for thisUser in all_users:
        #check which listing type was selected
        if (preferred_listing_type == 'whitelist'):
            #whitelisting selected
            thisUserPreferredListType=thisUser.whitelist
            #blacklisting not selected
            thisUserUnpreferredListType=thisUser.blacklist
        else:
            #blacklisting selected
            thisUserPreferredListType=thisUser.blacklist
            #whitelisting not selected
            thisUserUnpreferredListType=thisUser.whitelist

        #declare a list for this user's already populated blacklist and whitelist libraries
        user_lib_id_subfolder_id_list=[]

        #loop thru all preferred listing type libraries
        for thisUserLib in thisUserPreferredListType:
            user_lib_id_subfolder_id_list.append(str(thisUserLib.lib_id) + '_' + str(thisUserLib.subfolder_id))
        #loop thru all unpreferred listing type libraries
        for thisUserLib in thisUserUnpreferredListType:
            user_lib_id_subfolder_id_list.append(str(thisUserLib.lib_id) + '_' + str(thisUserLib.subfolder_id))

        #loop thru all libraries
        for thisAllLib in all_libraries:
            #verify this lib_id and subfolder_id are NOT already in this user's blacklist or whitelist
            if (not ((str(thisAllLib.lib_id) + '_' + str(thisAllLib.subfolder_id)) in user_lib_id_subfolder_id_list)):
                #check if user has access to this library folder
                if (does_user_have_access_to_this_lib_folder(thisUser,thisAllLib)):
                    #create temp copy
                    temp_thisAllLib=copy.copy(thisAllLib)
                    #set lib_enabled state for new libraries
                    temp_thisAllLib.lib_enabled=True
                    #copy the matching entry from all_libraries to overwrite the existing library
                    thisUserUnpreferredListType.append(copy.copy(temp_thisAllLib))

    return all_users


#clean and covert selection string to list
def clean_selection_convert_selection_to_list(selection_str):
    #check if at least one selection, check if selection is all commas
    if ((len(selection_str) > 0) and (len(selection_str) == selection_str.count(','))):
        #all commas will become []; append an invalid value to force a retry
        selection_str='retry'

    #check if at least one selection, check if selection is all commas
    if ((len(selection_str) > 0) and (len(selection_str) == selection_str.count(' '))):
        #all spaces will become []; append an invalid value to force a retry
        selection_str='retry'

    #replace spaces with commas (assuming people will use spaces because the space bar is bigger and easier to push)
    selection_no_spaces=selection_str.replace(' ',',')
    #convert string to list
    selection_list=selection_no_spaces.split(',')
    #remove blanks
    while ('' in selection_list):
        selection_list.remove('')
    #remove duplicate strings
    selection_list=list(set(selection_list))
    #sort alphabetically
    selection_list.sort()

    return selection_list


#check if all selections are valid
def are_valid_inputs_selected(selection_list,selection_limit):
    #loop thru all selections
    for thisSelection in selection_list:
        try:
            ##check if selection converts to a complex number
            #if (isinstance(thisSelection,complex)):
                ##selection is NOT valid
                #valid_selection=False
                #break
            ##check if selection converts to a float
            #elif (isinstance(thisSelection,float)):
                ##selection is NOT valid
                #valid_selection=False
                #break
            #check if selection converts to an integer
            if (isinstance(int(thisSelection),int)):
                #check if integer is less than zero; check if integer is greater than limit; check if string is '-0'
                if ((int(thisSelection) < 0) or (int(thisSelection) > selection_limit) or (thisSelection == '-0')):
                    #selection is NOT valid
                    valid_selection=False
                    break
                else:
                    #convert string of int into actual int
                    selection_list[selection_list.index(thisSelection)]=int(thisSelection)
            #selection is NOT numeric value
            else:
                #selection is NOT valid
                valid_selection=False
                break
        except:
            #selection is NOT valid
            valid_selection=False
            break
    else:
        #all selections are valid
        valid_selection=True

    return valid_selection


#print user info to console
def show_users(all_users):
    #print blank line
    print()
    #loop thru all users
    for thisAllUser in all_users:
        #print user info for each user to console
        print(str(all_users.index(thisAllUser)) + ' - ' + str(thisAllUser))


#select one user
def get_single_user_selection(all_users):
    print()

    #loop until finished selecting users
    loop_active=True

    #loop until user is finished
    while (loop_active):
        #show message on console; wait for input
        user_selection_str = input('Select one user at a time.\nEnter number of user to monitor; leave blank when finished: ')

        #check if any commas; this implies multiple users selected
        if (user_selection_str.find(',') >= 0):
            #something resembling a multiple selection; append an invalid value to force a retry
            user_selection_str='retry'

        #scrub and normalize selection
        selected_user_list=clean_selection_convert_selection_to_list(user_selection_str)

        #check if no selection was made
        if (selected_user_list == []):
            #loop thru all users
            for thisAllUser in all_users:
                if (thisAllUser.selected):
                    #at least one user selected; ok to exit selection loop
                    loop_active=False
                    break
            else:
                #no users selected; NOT ok to exit selection loop
                print('\nMust select at least one user. Try again.')
                #print user info to console
                show_users(all_users)
                print()
        #check if single user was selected; verify selection is valid
        elif ((len(selected_user_list) == 1) and (are_valid_inputs_selected(selected_user_list,len(all_users) - 1))):
            #at least one user selected; ok to exit selection loop
            loop_active=False
        else:
            #invalid selection; NOT ok to exit selection loop
            print('\nInvalid selection. Try again.')
            #print user info to console
            show_users(all_users)
            print()

    print('\n----------------------------------------------------------------------------------------')

    return selected_user_list


#select one or more users
def get_multiple_user_selection(all_users):
    print()

    #declare variable to run while loop
    loop_active=True

    #loop until finished selecting users
    while (loop_active):
        #show message on console; wait for input
        user_selection_str = input('Select one or more users.\n*Use a comma or space to separate multiple selections.\nLeave blank when finished: ')

        #scrub and normalize selection
        selected_user_list=clean_selection_convert_selection_to_list(user_selection_str)

        #check if no selection was made
        if (selected_user_list == []):
            #loop thru all users
            for thisAllUser in all_users:
                if (thisAllUser.selected):
                    #at least one user selected; ok to exit selection loop
                    loop_active=False
                    break
            else:
                #no users selected; NOT ok to exit selection loop
                print('\nMust select at least one user. Try again.')
                #print user info to console
                show_users(all_users)
                print()
        #check if single user was selected; verify selection is valid
        elif (are_valid_inputs_selected(selected_user_list,len(all_users) - 1)):
            #at least one user selected; ok to exit selection loop
            loop_active=False
        else:
            #invalid selection; NOT ok to exit selection loop
            print('\nInvalid selection. Try again.')
            #print user info to console
            show_users(all_users)
            print()

    print('\n----------------------------------------------------------------------------------------')

    return selected_user_list


#auto select all users
def auto_select_all_users(all_users):
    
    #covert range() into selected_user_list
    selected_user_list=list(range(0,len(all_users)))

    #loop thru all users
    for thisUser in all_users:
        #set this user to selected
        thisUser.selected=True
    
    return selected_user_list


#update user libraries select flag
def toggle_selected_user_libraries(preferred_listing_type,all_users,user_selection,libraries_to_show,library_selection):
    #loop thru user selection list
    for usrPos in user_selection:
        #check which listing type was selected
        if (preferred_listing_type == 'whitelist'):
            #whitelist preferred listing type; combine whitelist and blacklist
            userLibs=all_users[usrPos].whitelist + all_users[usrPos].blacklist
        else:
            #blacklist preferred listing type; combine blacklist and whitelist
            userLibs=all_users[usrPos].blacklist + all_users[usrPos].whitelist

        #loop thru this users libraries
        for thisUserLib in userLibs:
            #loop thru library selection list
            for thisLibSelection in library_selection:
                #check if the lib_id and subfolder_id from the user library entry and the selected library entry
                if ((thisUserLib.lib_id == libraries_to_show[thisLibSelection].lib_id) and (thisUserLib.subfolder_id == libraries_to_show[thisLibSelection].subfolder_id)):
                    #toggle selection
                    thisUserLib.selected=(not thisUserLib.selected)
                    break


#update user libraries select flag all to the same value
def on_off_all_selected_user_libraries(preferred_listing_type,all_users,user_selection,libraries_to_show,library_selection):
    #loop thru user selection list
    for usrPos in user_selection:
        #check which listing type was selected
        if (preferred_listing_type == 'whitelist'):
            #whitelist preferred listing type; combine whitelist and blacklist
            userLibs=all_users[usrPos].whitelist + all_users[usrPos].blacklist
        else:
            #blacklist preferred listing type; combine blacklist and whitelist
            userLibs=all_users[usrPos].blacklist + all_users[usrPos].whitelist

        #loop thru this users libraries
        for thisUserLib in userLibs:
            #loop thru library selection list
            for thisLibSelection in library_selection:
                #check if the lib_id and subfolder_id from the user library entry and the selected library entry
                if ((thisUserLib.lib_id == libraries_to_show[thisLibSelection].lib_id) and (thisUserLib.subfolder_id == libraries_to_show[thisLibSelection].subfolder_id)):
                    #toggle selection
                    thisUserLib.selected=(not all_users[usrPos].selected)
                    break