

#Determine if server is Jellyfin
def isJellyfinServer(server_brand):
    if (server_brand.casefold() == 'jellyfin'):
        return True
    elif (server_brand.casefold() == 'emby'):
        return False
    else:
        raise ValueError('ConfigValueError: admin_settings > server > brand must be a string or is missing\n\tValid values are emby, jellyfin\n')


#Determine if server is Emby
def isEmbyServer(server_brand):
    return not isJellyfinServer(server_brand)