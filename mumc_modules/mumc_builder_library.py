from mumc_modules.mumc_library_queries import get_all_libraries_from_media_server,get_all_library_subfolders
from mumc_modules.mumc_builder_user import clean_selection_convert_selection_to_list,are_valid_inputs_selected


#user library class for builder
class user_library:

    def __init__(self,lib_id='',collection_type='',path='',network_path='',subfolder_id='',lib_enabled=False):
        self.lib_id=lib_id
        self.collection_type=collection_type
        self.path=path
        self.network_path=network_path
        self.subfolder_id=subfolder_id
        self.lib_enabled=lib_enabled

    def __str__(self):
        if (self.collection_type == 'movies'):
            strAlignment="-----"
        elif (self.collection_type == 'tvshows'):
            strAlignment="----"
        elif ((self.collection_type == 'music') or (self.collection_type == 'books')):
            strAlignment="------"
        else: #(self.collection_type == 'audiobooks')
            strAlignment="-"
            
        return f"{self.collection_type} {strAlignment} Path: {self.path} - NetPath: {self.network_path} - LibId: {self.lib_id} - SubFolderId: {self.subfolder_id}"


#media library class for builder
class library_data(user_library):

    def __init__(self,lib_id='',collection_type='',path='',network_path='',subfolder_id=None,lib_enabled=False,name='',selected=False,selection=None):
        user_library.__init__(self,lib_id,collection_type,path,network_path,subfolder_id,lib_enabled)
        self.name=name
        self.selected=selected
        self.selection=selection

    def __str__(self):
        if (self.collection_type == 'movies'):
            strAlignment="-----"
        elif (self.collection_type == 'tvshows'):
            strAlignment="----"
        elif ((self.collection_type == 'music') or (self.collection_type == 'books')):
            strAlignment="------"
        else: #(self.collection_type == 'audiobooks')
            strAlignment="-"

        #check if user is selected
        if (self.selected):
            return f"{self.selection} - {self.collection_type} {strAlignment} Name: {self.name} - Path: {self.path} -"
        else: #(not (self.selected)):
            return f"{self.selection} - {self.collection_type} {strAlignment} Name: {self.name} - Path: {self.path} - NetPath: {self.network_path} - LibId: {self.lib_id} - SubFolderId: {self.subfolder_id}"

    def display(self):
        return f"LibId: {self.lib_id} - CollectionType: {self.collection_type} - Path: {self.path} - NetPath: {self.network_path} - SubFolderId: {self.subfolder_id} - LibEnabled: {self.lib_enabled} - Name: {self.name} - Selected: {self.selected} - Selection: {self.selection}"


#get and build all libraries
def get_all_libraries(the_dict):
    allLibrariesList=[]
    isEmby=the_dict['isEmby']
    libraryId=the_dict['libraryId']

    #get all libraries from media server
    virtualFolders=get_all_libraries_from_media_server(the_dict)

    #loop thru libraries
    for virtFolder in virtualFolders:
        #filter library results by collection type
        if ((virtFolder['CollectionType'] == 'movies') or
            (virtFolder['CollectionType'] == 'tvshows') or
            (virtFolder['CollectionType'] == 'music') or
            (virtFolder['CollectionType'] == 'audiobooks') or
            (virtFolder['CollectionType'] == 'books')):
            #loop thru subfolder paths within this library
            for pathInfo in virtFolder['LibraryOptions']['PathInfos']:
                #when emby; the subfolders need to be specifically handled
                if (isEmby):
                    #query server for subfolder specific information
                    libraryInfoSubfolderInfo=get_all_library_subfolders(the_dict)
                    #loop thru returned library information
                    for libraryInfo in libraryInfoSubfolderInfo:
                        #check if subfolder's parent library id matches virtual folder's id
                        if (libraryInfo[libraryId] == virtFolder[libraryId]):
                            #loop thru subfolders for this library
                            for subfolderInfo in libraryInfo['SubFolders']:
                                #check if subfolder's path matches subfolder path of the virtual folder
                                if (subfolderInfo['Path'] == pathInfo['Path']):
                                    #try saving the network path
                                    try:
                                        networkPath=pathInfo['NetworkPath']
                                    except:
                                        networkPath=None
                                    #create list of library (sub)folder information objects
                                    allLibrariesList.append(library_data(lib_id=virtFolder[libraryId],collection_type=virtFolder['CollectionType'],path=pathInfo['Path'],network_path=networkPath,subfolder_id=subfolderInfo['Id'],name=virtFolder['Name']))
                            break
                #when jellyfin; subfolders do not exist and cannot be specifically handled
                else:
                    #try saving the network path
                    try:
                        networkPath=pathInfo['NetworkPath']
                    except:
                        networkPath=None
                    #create list of library folder information objects
                    allLibrariesList.append(library_data(lib_id=virtFolder[libraryId],collection_type=virtFolder['CollectionType'],path=pathInfo['Path'],network_path=networkPath,name=virtFolder['Name']))

    return allLibrariesList


#get and return list of libraries to be shown
def get_list_of_libraries_to_show(preferred_listing_type,all_users,user_selection):
    #declare list of libraries to show
    libraries_to_show=[]
    #declare list of libraries ids/subfolder ids
    library_tracker=[]

    #loop thru each user selection in the list
    for usrPos in user_selection:

        #check which listing type was selected
        if (preferred_listing_type == 'whitelist'):
            #whitelisting selected
            thisUserPreferredListType=all_users[usrPos].whitelist
            #blacklisting not selected
            thisUserUnpreferredListType=all_users[usrPos].blacklist
        else:
            #blacklisting selected
            thisUserPreferredListType=all_users[usrPos].blacklist
            #whitelisting not selected
            thisUserUnpreferredListType=all_users[usrPos].whitelist

        #loop thru each preferred listing type library
        for thisLib in thisUserPreferredListType:
            #check if library has already been added to libraries_to_show (because jellyfin does not have subfolder_ids, path has to be used for comparison)
            if (not ((str(thisLib.lib_id) + '_' + str(thisLib.subfolder_id) + '_' + str(thisLib.path)) in library_tracker)):
                #append library to list of libraries to be shown
                libraries_to_show.append(thisLib)
                #add library to library_tracker
                library_tracker.append(str(thisLib.lib_id) + '_' + str(thisLib.subfolder_id) + '_' + str(thisLib.path))

        #loop thru each unpreferred listing type library
        for thisLib in thisUserUnpreferredListType:
            #check if library has already been added to libraries_to_show (because jellyfin does not have subfolder_ids, path has to be used for comparison)
            if (not ((str(thisLib.lib_id) + '_' + str(thisLib.subfolder_id) + '_' + str(thisLib.path)) in library_tracker)):
                #append library to list of libraries to be shown
                libraries_to_show.append(thisLib)
                #add library to library_tracker
                library_tracker.append(str(thisLib.lib_id) + '_' + str(thisLib.subfolder_id) + '_' + str(thisLib.path))

    return libraries_to_show


#populate the selection number into each library
def enumerate_libraries_to_be_shown(libraries_to_show):
    #loop thru libraries to be shown
    for thisLib in libraries_to_show:
        #add selection number that alings with list index
        thisLib.selection=libraries_to_show.index(thisLib)

    return libraries_to_show


#print library info to console
def show_libraries(libraries_to_show):
    #print blank line
    print()
    #loop thru all libraries to be shown in the console
    for thisLib in libraries_to_show:
        #print library info to the console
        print(str(thisLib))


#select one library
def get_single_library_selection():
    #n/a - this function is not needed
    pass


#select one or more libraries
def get_multiple_library_selection(preferred_listing_type,libraries_to_show,user_library_selection):
    print()

    #declare variable to run while loop
    loop_active=True

    #loop until finished selecting libraries
    while (loop_active):
        #show message on console; wait for input
        library_selection_str = input('Select one or more libraries to be ' + str(preferred_listing_type) + 'ed.\n*Use a comma or space to separate multiple selections.\nLeave blank when finished: ')

        #scrub and normalize selection
        selected_library_list=clean_selection_convert_selection_to_list(library_selection_str)

        #check if no selection was made and user_library_select only requires selecting one or more libraries
        if ((selected_library_list == []) and (user_library_selection == 2)):
            #loop thru all libraries
            for thisLib in libraries_to_show:
                if (thisLib.selected):
                    #at least one library selected; ok to exit selection loop
                    loop_active=False
                    break
            else:
                #no libraries selected; NOT ok to exit selection loop
                print('\nMust select at least one library. Try again.')
                #print library info to console
                show_libraries(libraries_to_show)
                print()
        #check if single library was selected; verify selection is valid
        elif (are_valid_inputs_selected(selected_library_list,len(libraries_to_show) - 1)):
        #if (are_valid_inputs_selected(selected_library_list,len(libraries_to_show) - 1)):
            #at least one library selected; ok to exit selection loop
            loop_active=False
        else:
            #invalid selection; NOT ok to exit selection loop
            print('\nInvalid selection. Try again.')
            #print library info to console
            show_libraries(libraries_to_show)
            print()

    return selected_library_list


#set selected for all user libraries to True
def select_all_user_libraries(all_users,selected_value=True):
    #loop thru all users
    for thisUser in all_users:
        #loop thru whitelist libraries for this user
        for thisLib in thisUser.whitelist:
            #unselect this library
            thisLib.selected=selected_value
        #loop thru blacklist libraries for this user
        for thisLib in thisUser.blacklist:
            #unselecte this library
            thisLib.selected=selected_value


#set selected for all user libraries to False
def unselect_all_user_libraries(all_users,selected_value=False):
    select_all_user_libraries(all_users,selected_value)


#auto select all libraries
def auto_select_libraries_to_show(libraries_to_show):
    
    #covert range() into selected_user_list
    library_selection=list(range(0,len(libraries_to_show)))
    
    return library_selection