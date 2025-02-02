from mumc_modules.mumc_url import requestURL,build_emby_jellyfin_request_message


#API call to get single user account
def get_single_user(userId,the_dict):

    url=the_dict['admin_settings']['server']['url'] + '/Users/' + str(userId)

    req=build_emby_jellyfin_request_message(url,the_dict)

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    data_single_user=requestURL(req, preConfigDebug, 'get_single_user_info_for_' + str(userId), 3, the_dict)

    return data_single_user


#API call to get all user accounts
def get_all_users(the_dict):

    url=the_dict['admin_settings']['server']['url'] + '/Users'
    
    req=build_emby_jellyfin_request_message(url,the_dict)

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    data_all_users=requestURL(req, preConfigDebug, 'get_all_user_info', 3, the_dict)

    return data_all_users