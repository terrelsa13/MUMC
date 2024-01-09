from mumc_modules.mumc_url import requestURL
from mumc_modules.mumc_server_type import isJellyfinServer


#API call to get all user accounts
def get_single_user(userId,the_dict):
    #Get single user
    req=(the_dict['admin_settings']['server']['url'] + '/Users/' + str(userId) + '?api_key=' + the_dict['admin_settings']['server']['auth_key'])

    #preConfigDebug = True
    preConfigDebug = False

    #api call
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        #jellyfin returns a list of users
        data_all_users=requestURL(req, preConfigDebug, 'get_users', 3, the_dict)
    else:
        #emby returns a dictionary with a key called 'Items' with a list of users as the value
        data_all_users=requestURL(req, preConfigDebug, 'get_users', 3, the_dict)
        data_all_users=data_all_users['Items']

    return data_all_users


#API call to get all user accounts
def get_all_users(the_dict):
    #Get all users
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        #the jellyfin endpoint is /Users
        req=(the_dict['admin_settings']['server']['url'] + '/Users?api_key=' + the_dict['admin_settings']['server']['auth_key'])
    else:
        #the emby endpoint is /Users/Query
        req=(the_dict['admin_settings']['server']['url'] + '/Users/Query?api_key=' + the_dict['admin_settings']['server']['auth_key'])

    #preConfigDebug = True
    preConfigDebug = False

    #api call
    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
        #jellyfin returns a list of users
        data_all_users=requestURL(req, preConfigDebug, 'get_users', 3, the_dict)
    else:
        #emby returns a dictionary with a key called 'Items' with a list of users as the value
        data_all_users=requestURL(req, preConfigDebug, 'get_users', 3, the_dict)
        data_all_users=data_all_users['Items']

    return data_all_users