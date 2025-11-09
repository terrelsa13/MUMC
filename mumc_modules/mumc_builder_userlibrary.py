from mumc_modules.mumc_server_type import isEmbyServer
from mumc_modules.mumc_builder_library import get_all_libraries,get_list_of_libraries_to_show,enumerate_libraries_to_be_shown,show_libraries,get_multiple_library_selection,select_all_user_libraries,unselect_all_user_libraries,auto_select_libraries_to_show
#from mumc_modules.mumc_builder_user import get_all_users,clean_all_users,clean_all_user_libraries,update_all_user_libraries,show_users,show_users,get_single_user_selection,get_multiple_user_selection,auto_select_all_users,toggle_selected_user_libraries,on_off_all_selected_user_libraries,remove_users_without_valid_libraries
from mumc_modules.mumc_builder_user import get_all_users,clean_all_users,clean_all_user_libraries,update_all_user_libraries,show_users,show_users,get_single_user_selection,get_multiple_user_selection,auto_select_all_users,toggle_selected_user_libraries,remove_users_without_valid_libraries


#build users and libraries
def build_users_and_libraries(the_dict):

    ##########################################################################################################
    ######Data Collection#####################################################################################
    ##########################################################################################################

    #set preferred_listing_type
    preferred_listing_type=the_dict['preferred_listing_type']

    #check if emby or jellyfin
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        the_dict['isEmby']=True
        the_dict['isJellyfin']=False
        #set libraryId key for emby
        the_dict['libraryId']='Guid'
    else:
        the_dict['isEmby']=False
        the_dict['isJellyfin=']=True
        #set libraryId key for jellyfin
        the_dict['libraryId']='ItemId'

    #get all libraries from server
    all_libraries=get_all_libraries(the_dict)

    #get all users from server
    all_users=get_all_users(the_dict)

    #remove any already existing users that no longer exist on the server; populate libraries of existing users
    all_users=clean_all_users(the_dict['admin_settings']['users'],all_users)

    #remove any existing user libraries that no longer exist; remove libraries the user does NOT have permission to access
    all_users=clean_all_user_libraries(preferred_listing_type,all_libraries,all_users)

    #update users with "new" libraries they have permission to access
    all_users=update_all_user_libraries(preferred_listing_type,all_libraries,all_users)

    #remove users that do not have any libraries (or any valid libraries)
    all_users=remove_users_without_valid_libraries(all_users)

    ##########################################################################################################
    ##########################################################################################################
    #set user_library_selection
    user_library_selection=the_dict['user_library_selection']
    ##########################################################################################################
    ##########################################################################################################
    # 0 - Select users and libraries.
    #     Select libraries to be whitelisted/blacklisted for selected users.
    # 1 - Select users only.
    #     Selected users will have all libraries whitelisted/blacklisted according to their access policy.
    # 2 - Select libraries only.
    #     Selected libraries will be whitelisted/blacklisted for all users according to their access policy.
    # 3 - Select nothing.
    #     All libraries will be whitelisted/blacklisted for all users according to their access policy.
    ##########################################################################################################
    ##########################################################################################################

    #declare variables to run while loops
    user_loop_active=True
    library_loop_active=True

    ##########################################################################################################
    ######User Selection######################################################################################
    ##########################################################################################################

    #loop until finished
    while (user_loop_active):

        #select one user
        if (user_library_selection == 0):
            #print user info to console
            show_users(all_users)

            #select one user; clean the selection; check selection is valid; return list with selection
            user_selection=get_single_user_selection(all_users)

            #if no user selected set loop to inactive
            if (user_selection == []):
                #stop user loop
                user_loop_active=False
            else:
                #start library loop
                library_loop_active=True

        #select one or more users
        elif (user_library_selection == 1):
            #print user info to console
            show_users(all_users)

            #select one user; clean the selection; check selection is valid; return list with selection
            user_selection=get_multiple_user_selection(all_users)

            #if no user selected set loop to inactive
            if (user_selection == []):
                #stop loop
                user_loop_active=False
            else:
                #start library loop
                library_loop_active=True

        #auto select all users
        elif ((user_library_selection == 2) or (user_library_selection == 3)):
            #auto select all users; return list with selection
            user_selection=auto_select_all_users(all_users)

            if (user_library_selection == 2):
                #unselect all user libraries before show_libraries(); this will show all as unselected
                all_users=unselect_all_user_libraries(all_users)
            else:
                #select all user libraries
                all_users=select_all_user_libraries(all_users)

        ##########################################################################################################
        ######Library Selection###################################################################################
        ##########################################################################################################

        #check if loop is active
        if (user_loop_active):

            #loop until finished
            while(library_loop_active):

                #show and select one or more libraries for one user or multiple users
                if ((user_library_selection == 0) or (user_library_selection == 2)):
                    #build list of libraries to be shown on the console
                    libraries_to_show=get_list_of_libraries_to_show(preferred_listing_type,all_users,user_selection)

                    #enumerate each library selection to align with it's position in the list
                    libraries_to_show=enumerate_libraries_to_be_shown(libraries_to_show)

                    #print library info to console
                    show_libraries(libraries_to_show)

                    #select one or more libraries; clean the selection; check selection is valid; return list with selection
                    library_selection=get_multiple_library_selection(preferred_listing_type,libraries_to_show,user_library_selection)

                    #toggle if library is considered selected or unselected
                    all_users=toggle_selected_user_libraries(preferred_listing_type,all_users,user_selection,libraries_to_show,library_selection)

                    #if no library selected set loop to inactive
                    if (library_selection == []):
                        #stop loop
                        library_loop_active=False
                        #check if selecting one or more libraries for multiple users
                        if (user_library_selection == 2):
                            #stop loop
                            user_loop_active=False
                            
                #auto select all libraries
                elif ((user_library_selection == 1) or (user_library_selection == 3)):
                    #build list of libraries to be shown on the console
                    libraries_to_show=get_list_of_libraries_to_show(preferred_listing_type,all_users,user_selection)

                    #auto select all libraries; return list with selection
                    library_selection=auto_select_libraries_to_show(libraries_to_show)

                    if (user_library_selection == 1):
                        #toggle if library is considered selected or unselected
                        all_users=toggle_selected_user_libraries(preferred_listing_type,all_users,user_selection,libraries_to_show,library_selection)

                    #stop loop
                    library_loop_active=False

                    #check if auto selecting both users and libraries
                    if (user_library_selection == 3):
                        #stop loop
                        user_loop_active=False

    ##########################################################################################################
    ######Data To YAML########################################################################################
    ##########################################################################################################

    #declare list to return
    user_and_library_list=[]
    #save user and library selections
    for thisUser in all_users:
        #check if user is selected
        if (thisUser.selected):
            #add new user and library entry to list
            user_and_library_list.append(thisUser.userObjectToYAML(preferred_listing_type))

    return user_and_library_list