from mumc_modules.mumc_url import requestURL,build_request_message


#request access token (aka auth key aka API key) using the admin account credentials
def authenticate_user_by_name(admin_username,admin_password,the_dict):
    #login info
    values = {'Username' : admin_username, 'Pw' : admin_password}

    url=the_dict['admin_settings']['server']['url'] + '/Users/AuthenticateByName'

    req=build_request_message(url,the_dict,data=values,method='POST',client='mumc_auth.py',device='Multi-User Media Cleaner Auth',deviceId='MUMC Auth')

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    authenticated_user_data=requestURL(req, preConfigDebug, 'authenticate_by_name', 4, the_dict)

    return(authenticated_user_data)


#request exisitng GUI auth keys
def get_labelled_authentication_keys(authenticated_user_data,the_dict):

    token=authenticated_user_data['AccessToken']

    url=the_dict['admin_settings']['server']['url'] + '/Auth/Keys'

    req=build_request_message(url,the_dict,token=token,client='mumc_auth.py',device='Multi-User Media Cleaner Auth',deviceId='MUMC Auth')

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    labelled_authentication_keys=requestURL(req, preConfigDebug, 'get_labelled_authentication_key', 4, the_dict)

    labelled_authentication_keys['request_url']=req

    return(labelled_authentication_keys)


#create GUI auth key for MUMC
def create_labelled_authentication_key(authenticated_user_data,the_dict):

    token=authenticated_user_data['AccessToken']

    url = the_dict['admin_settings']['server']['url'] + '/Auth/Keys?app=' + the_dict['app_name_short']
    
    req=build_request_message(url,the_dict,token=token,client='mumc_auth.py',device='Multi-User Media Cleaner Auth',deviceId='MUMC Auth',method='POST')

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    requestURL(req, preConfigDebug, 'create_labelled_authentication_key', 4, the_dict)


#delete GUI auth key for MUMC
def delete_labelled_authentication_key(key_to_delete,authenticated_user_data,the_dict):

    token=authenticated_user_data['AccessToken']

    url = the_dict['admin_settings']['server']['url'] + '/Auth/Keys/' + str(key_to_delete)
    
    req=build_request_message(url,the_dict,token=token,method='DELETE',client='mumc_auth.py',device='Multi-User Media Cleaner Auth',deviceId='MUMC Auth')

    #preConfigDebug = 3
    preConfigDebug = 0

    #api call
    requestURL(req, preConfigDebug, 'delete_labelled_authentication_key_' + str(key_to_delete), 4, the_dict)


#Find existing MUMC auth key
def get_MUMC_labelled_authentication_key(labelled_authentication_keys,the_dict):
    for item in labelled_authentication_keys['Items']:
        if (item['AppName'].casefold() == the_dict['app_name_short'].casefold()):
            return item['AccessToken']
    return False