import urllib.request as urlrequest
from mumc_modules.mumc_output import convert2json
from mumc_modules.mumc_url import requestURL
from mumc_modules.mumc_versions import get_script_version


#request access token (aka auth key aka API key) using the admin account credentials
def authenticate_user_by_name(admin_username,admin_password,the_dict):
    #login info
    values = {'Username' : admin_username, 'Pw' : admin_password}
    #DATA = urlparse.urlencode(values)
    #DATA = DATA.encode('ascii')
    DATA = convert2json(values)
    DATA = DATA.encode('utf-8')

    #works for both Emby and Jellyfin
    xAuth = 'Authorization'
    #assuming jellyfin will eventually change to this
    #if (isEmbyServer()):
        #xAuth = 'X-Emby-Authorization'
    #else #(isJellyfinServer()):
        #xAuth = 'X-Jellyfin-Authorization'

    headers = {xAuth : 'Emby UserId="' + admin_username  + '", Client="mumc.py", Device="' + the_dict['app_name_long'] + '", DeviceId="' + the_dict['app_name_short'] + '", Version="' + get_script_version() + '", Token=""', 'Content-Type' : 'application/json'}

    req = urlrequest.Request(url=the_dict['admin_settings']['server']['url'] + '/Users/AuthenticateByName', data=DATA, method='POST', headers=headers)

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    authenticated_user_data=requestURL(req, preConfigDebug, 'get_authentication_key', 4, the_dict)

    return(authenticated_user_data)


#request exisitng GUI auth keys
def get_labelled_authentication_keys(authenticated_user_data,the_dict):

    url=the_dict['admin_settings']['server']['url'] + '/Auth/Keys?api_key=' + authenticated_user_data['AccessToken']

    preConfigDebug = 3
    #preConfigDebug = 0

    #api call
    labelled_authentication_keys=requestURL(url, preConfigDebug, 'get_labelled_authentication_key', 4, the_dict)

    labelled_authentication_keys['request_url']=url

    return(labelled_authentication_keys)


#create GUI auth key for MUMC
def create_labelled_authentication_key(authenticated_user_data,the_dict):

    req = urlrequest.Request(url=the_dict['admin_settings']['server']['url'] + '/Auth/Keys?app=' + the_dict['app_name_short'] + '&api_key=' + authenticated_user_data['AccessToken'], method='POST')

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    requestURL(req, preConfigDebug, 'create_labelled_authentication_key', 4, the_dict)


#Find existing MUMC auth key
def get_MUMC_labelled_authentication_key(labelled_authentication_keys,the_dict):
    for item in labelled_authentication_keys['Items']:
        if (item['AppName'].casefold() == the_dict['app_name_short'].casefold()):
            return item['AccessToken']
    return False