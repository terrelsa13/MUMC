import urllib.request as urlrequest
from mumc_modules.mumc_url import requestURL,build_request_message
from mumc_modules.mumc_server_type import isJellyfinServer


#API call to get all user accounts
def get_single_user(userId,the_dict):

    url=the_dict['admin_settings']['server']['url'] + '/Users/' + str(userId)

    req=build_request_message(url,the_dict)

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    data_all_users=requestURL(req, preConfigDebug, 'get_single_user_info_for_' + str(userId), 3, the_dict)

    return data_all_users


#API call to get all user accounts
def get_all_users(the_dict):

    url=the_dict['admin_settings']['server']['url'] + '/Users'

    '''
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        #the jellyfin endpoint is /Users
        url=the_dict['admin_settings']['server']['url'] + '/Users'
    else:
        #the emby endpoint is /Users/Query
        url=the_dict['admin_settings']['server']['url'] + '/Users/Query'
    '''
    
    req=build_request_message(url,the_dict)

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    data_all_users=requestURL(req, preConfigDebug, 'get_all_user_info', 3, the_dict)
    '''
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        #jellyfin returns a list of users
        data_all_users=requestURL(req, preConfigDebug, 'get_all_user_info', 3, the_dict)
    else:
        #emby returns a dictionary with a key called 'Items' with a list of users as the value
        data_all_users=requestURL(req, preConfigDebug, 'get_all_user_info', 3, the_dict)
        data_all_users=data_all_users['Items']
    '''

    return data_all_users