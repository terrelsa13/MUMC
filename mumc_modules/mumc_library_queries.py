from mumc_modules.mumc_url import requestURL,build_emby_jellyfin_request_message


#Request for libraries (i.e. movies, tvshows, audio, etc...)
def get_all_libraries(the_dict):
    #Request for libraries (i.e. movies, tvshows, audio, etc...)
    url=the_dict['admin_settings']['server']['url'] + '/Library/VirtualFolders'

    req=build_emby_jellyfin_request_message(url,the_dict)

    #preConfigDebug = 3
    preConfigDebug = 0

    #api calls
    data_all_folders = requestURL(the_dict, req, preConfigDebug, 'get_all_library_folders', 3)

    return data_all_folders


#Request for libraries (i.e. movies, tvshows, audio, etc...)
def get_all_library_subfolders(the_dict):
    #Request for libraries (i.e. movies, tvshows, audio, etc...)
    url=the_dict['admin_settings']['server']['url'] + '/Library/SelectableMediaFolders'

    req=build_emby_jellyfin_request_message(url,the_dict)

    #preConfigDebug = 3
    preConfigDebug = 0

    #api calls
    data_all_folders = requestURL(the_dict, req, preConfigDebug, 'get_all_library_subfolders', 3)

    return data_all_folders