

#Determine if server is Jellyfin
def isJellyfinServer(server_brand):
    if (server_brand.casefold() == "jellyfin"):
        return True
    else:
        return False


#Determine if server is Emby
def isEmbyServer(server_brand):
    return not isJellyfinServer(server_brand)