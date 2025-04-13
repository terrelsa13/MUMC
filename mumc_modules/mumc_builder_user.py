import copy
from mumc_modules.mumc_user_queries import get_all_users_from_media_server


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
        #check if user is selected
        if (self.selected):
            return f"Name: {self.user_name} -"
        else: #(not (self.selected)):
            return f"Name: {self.user_name} - UserId: {self.user_id}"

    def display(self):
        return f"UserId: {self.user_id} - Name: {self.user_name} - Whitelist: {self.whitelist} - Blacklist: {self.blacklist} - AccessToAllFolders: {self.enableAllFolders} - EnabledFolders: {self.enabledFolders} - ExcludedSubfolders: {self.excludedSubFolders} - Selected: {self.selected}"
 
 
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
            allUsersList.append(user_data(user_id=userInfo['Id'],user_name=userInfo['Name'],enableAllFolders=userInfo['Policy']['EnableAllFolders'],enabledFolders=userInfo['Policy']['EnabledFolders'],excludedSubFolders=userInfo['Policy']['ExcludedSubFolders']))
        else:
            #save user data; jellyfin does NOT allow subfolder specific user permissions
            allUsersList.append(user_data(user_id=userInfo['Id'],user_name=userInfo['Name'],enableAllFolders=userInfo['Policy']['EnableAllFolders'],enabledFolders=userInfo['Policy']['EnabledFolders']))

    return allUsersList


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
            if (str(thisAllLib.lib_id + '_' + thisAllLib.subfolder_id) in thisUser.excludedSubFolders):
                does_user_have_access=False
            #subfolder_id is included for this user
            else:
                does_user_have_access=True
        #lib_id is disabled for this user
        else:
            does_user_have_access=False

    return does_user_have_access


#remove any existing user libraries not in all_libraries; or any libraries the user does not have permission to access
def clean_all_user_libraries(the_dict,all_libraries,all_users):
    #loop thru all_users
    for thisUser in all_users:
        #check which listing type was selected
        if (the_dict['favored_listing_type'] == 'whitelist'):
            #whitelisting selected
            thisUserFavoredListType=thisUser.whitelist
            #blacklisting not selected
            thisUserUnfavoredListType=thisUser.blacklist
        else:
            #blacklisting selected
            thisUserFavoredListType=thisUser.blacklist
            #whitelisting not selected
            thisUserUnfavoredListType=thisUser.whitelist

        #loop thru the specific user's selected library listing type
        for thisUserLib in reversed(thisUserFavoredListType):
            #loop thru all_libraries
            for thisAllLib in all_libraries:
                #check if lib_id and subfolder_id match for the specific user's library entry and the library entry from all_libraries
                if ((thisUserLib['lib_id'] == thisAllLib.lib_id) and (thisUserLib['subfolder_id'] == thisAllLib.subfolder_id)):
                    #check if user has access to this library folder
                    if (does_user_have_access_to_this_lib_folder(thisUser,thisAllLib)):
                        #create temp copy
                        temp_thisAllLib=copy.copy(thisAllLib)
                        #libraries/subfolders in the favored listing type are selected
                        temp_thisAllLib.selected=True
                        #store lib_enabled state for existing library
                        temp_thisAllLib.lib_enabled=thisUserLib['lib_enabled']
                        #copy the matching entry from all_libraries to overwrite the existing library
                        thisUserFavoredListType[thisUserFavoredListType.index(thisUserLib)]=copy.copy(temp_thisAllLib)
                        break
            else:
                #library folder no longer exists or user does not have permissoin to access the library folder
                #either way; remove this library from the user
                thisUserFavoredListType.remove(thisUserLib)

        #loop thru the specific user's selected library listing type
        for thisUserLib in reversed(thisUserUnfavoredListType):
            #loop thru all_libraries
            for thisAllLib in all_libraries:
                #check if lib_id and subfolder_id match for the specific user's library entry and the library entry from all_libraries
                if ((thisUserLib['lib_id'] == thisAllLib.lib_id) and (thisUserLib['subfolder_id'] == thisAllLib.subfolder_id)):
                    #check if user has access to this library folder
                    if (does_user_have_access_to_this_lib_folder(thisUser,thisAllLib)):
                        #create temp copy
                        temp_thisAllLib=copy.copy(thisAllLib)
                        #store lib_enabled state for existing library
                        temp_thisAllLib.lib_enabled=thisUserLib['lib_enabled']
                        #copy the matching entry from all_libraries to overwrite the existing library
                        thisUserUnfavoredListType[thisUserUnfavoredListType.index(thisUserLib)]=copy.copy(temp_thisAllLib)
                        break
            else:
                #library folder no longer exists or user does not have permissoin to access the library folder
                #either way; remove this library from the user
                thisUserUnfavoredListType.remove(thisUserLib)

    return all_users


#update users with "new" libraries they have permission to access
def update_all_user_libraries(the_dict,all_libraries,all_users):
    #loop thru all_users
    for thisUser in all_users:
        #check which listing type was selected
        if (the_dict['favored_listing_type'] == 'whitelist'):
            #whitelisting selected
            thisUserFavoredListType=thisUser.whitelist
            #blacklisting not selected
            thisUserUnfavoredListType=thisUser.blacklist
        else:
            #blacklisting selected
            thisUserFavoredListType=thisUser.blacklist
            #whitelisting not selected
            thisUserUnfavoredListType=thisUser.whitelist

        #declare a list for this user's already populated blacklist and whitelist libraries
        user_lib_id_subfolder_id_list=[]

        #loop thru all favored listing type libraries
        for thisUserLib in thisUserFavoredListType:
            user_lib_id_subfolder_id_list.append(str(thisUserLib.lib_id + '_' + thisUserLib.subfolder_id))
        #loop thru all unfavored listing type libraries
        for thisUserLib in thisUserUnfavoredListType:
            user_lib_id_subfolder_id_list.append(str(thisUserLib.lib_id + '_' + thisUserLib.subfolder_id))

        #loop thru all libraries
        for thisAllLib in all_libraries:
            #verify this lib_id and subfolder_id are NOT already in this user's blacklist or whitelist
            if (not (str(thisAllLib.lib_id + '_' + thisAllLib.subfolder_id) in user_lib_id_subfolder_id_list)):
                #check if user has access to this library folder
                if (does_user_have_access_to_this_lib_folder(thisUser,thisAllLib)):
                    #create temp copy
                    temp_thisAllLib=copy.copy(thisAllLib)
                    #set lib_enabled state for new libraries
                    temp_thisAllLib.lib_enabled=True
                    #copy the matching entry from all_libraries to overwrite the existing library
                    thisUserUnfavoredListType.append(copy.copy(temp_thisAllLib))

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

    return selected_user_list


#auto select all users
def auto_select_all_users(all_users):
    
    #covert range() into selected_user_list
    selected_user_list=list(range(0,len(all_users)))
    
    return selected_user_list