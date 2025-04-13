import copy
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_builder_library import get_all_libraries,get_list_of_libraries_to_show,enumerate_libraries_to_be_shown,show_libraries,get_multiple_library_selection
from mumc_modules.mumc_builder_user import get_all_users,clean_all_users,clean_all_user_libraries,update_all_user_libraries,show_users,show_users,get_single_user_selection,get_multiple_user_selection,auto_select_all_users


def build_users_and_libraries(the_dict):
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

    #remove any already existing users that no longer exist
    all_users=clean_all_users(the_dict['admin_settings']['users'],all_users)

    #remove any existing user libraries that no longer exist; remove libraries the user does NOT have permission to access
    all_users=clean_all_user_libraries(the_dict,all_libraries,all_users)

    #update users with "new" libraries they have permission to access
    all_users=update_all_user_libraries(the_dict,all_libraries,all_users)

    #declare variable to run while loop
    loop_active=True

    #loop until user is finished
    while (loop_active):

        ######User Selection######################

        #select one user
        if (the_dict['user_library_selection'] == 0):
            #print user info to console
            show_users(all_users)

            #select one user; clean the selection; check selection is valid; return list with selection
            user_selection=get_single_user_selection(all_users)

            #if no user selected set loop to inactive
            if (user_selection == []):
                #stop loop
                loop_active=False

        #select one or more users
        elif (the_dict['user_library_selection'] == 1):
            #print user info to console
            show_users(all_users)

            #select one user; clean the selection; check selection is valid; return list with selection
            user_selection=get_multiple_user_selection(all_users)

            #if no user selected set loop to inactive
            if (user_selection == []):
                #stop loop
                loop_active=False

        #auto select all users
        elif ((the_dict['user_library_selection'] == 2) or (the_dict['user_library_selection'] == 3)):
            #auto select all users; return list with selection
            user_selection=auto_select_all_users(all_users)

        ######Library Selection###################

        #check if loop is active
        if (loop_active):
            #show and select one or more libraries for one user
            if (the_dict['user_library_selection'] == 0):
                #build list of libraries to be shown on the console
                libraries_to_show=get_list_of_libraries_to_show(the_dict,all_users,user_selection)

                #enumerate each library selection to align with it's position in the list
                enumerate_libraries_to_be_shown(libraries_to_show)

                #print library info to console
                show_libraries(libraries_to_show)

                #select one or more libraries; clean the selection; check selection is valid; return list with selection
                library_selection=get_multiple_library_selection(libraries_to_show)
                
                pass

            #show and select one or more libraries for multiple users
            if (the_dict['user_library_selection'] == 2):
                pass

            #auto select all libraries
            elif ((the_dict['user_library_selection'] == 1) or (the_dict['user_library_selection'] == 3)):
                #check if auto selecting both users and libraries
                if (the_dict['user_library_selection'] == 3):
                    #stop loop
                    loop_active=False

    pass