from mumc_modules.mumc_played_created import get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue
from mumc_modules.mumc_url import api_query_handler,build_request_message
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo,get_STUDIO_itemInfo
from mumc_modules.mumc_compare_items import does_index_exist
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json


#Get children of favorited parents
def getChildren_favoritedMediaItems(suffix_str,user_info,var_dict,the_dict):

    data_dict={}
    data_Favorited=var_dict['data_Favorited_' + suffix_str]
    data_dict['APIDebugMsg_']='Find ' + var_dict['APIDebugMsg_Child_Of_Favorited_Item_' + suffix_str]
    server_url=the_dict['admin_settings']['server']['url']
    child_dict={}
    data_dict['StartIndex_']=0
    data_dict['data_']={'Items':[]}

    #Loop thru items returned as favorited
    for data in data_Favorited['Items']:

        #Verify media item is a parent (not a child like an episode, movie, or audio)
        if ((data['IsFolder'] == True) or (data['Type'] == 'Book')):

            #Initialize api_query_handler() variables for watched child media items
            data_dict['StartIndex_']=0
            data_dict['TotalItems_']=1
            data_dict['QueryLimit_']=1
            data_dict['QueriesRemaining_']=True

            if (not (data['Id'] == '')):
                #Build query for child media items
                #include all item types; filter applied in first API calls for each media type in get_mediaItems()
                IncludeItemTypes=''
                FieldsState='Id,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,UserData'
                SortBy='SeriesSortName,AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                SortOrder='Ascending'
                Recursive='True'
                EnableImages='False'
                CollapseBoxSetItems='False'
                IsPlayedState=get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(the_dict,var_dict)

                while (data_dict['QueriesRemaining_']):

                    if (not (data['Id'] == '')):
                        #Built query for child meida items

                        url=(server_url + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + data['Id'] + '&IncludeItemTypes=' + IncludeItemTypes +
                        '&StartIndex=' + str(data_dict['StartIndex_']) + '&Limit=' + str(data_dict['QueryLimit_']) + '&IsPlayed=' + IsPlayedState + '&Fields=' + FieldsState +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems + '&Recursive=' + Recursive + '&SortBy=' + SortBy + '&SortOrder=' + SortOrder + '&EnableImages=' + EnableImages)

                        data_dict['apiQuery_']=build_request_message(url,the_dict)

                        #Send the API query for for watched media items in blacklists
                        data_dict.update(api_query_handler('',data_dict,the_dict))
                    else:
                        #When no media items are returned; simulate an empty query being returned
                        #this will prevent trying to compare to an empty string '' to the whitelist libraries later on
                        data_dict['data_']={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        data_dict['QueryLimit_']=0
                        data_dict['QueriesRemaining_']=False
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log("\n\nNo " + data_dict['APIDebugMsg_'] + " media items found",2,the_dict)

                    #save favorites to child items
                    for child_item in data_dict['data_']['Items']:
                        if ((child_item['Type'].casefold() == 'movie') or (child_item['Type'].casefold() == 'episode') or (child_item['Type'].casefold() == 'audio') or (child_item['Type'].casefold() == 'audiobook')):
                            if (not ('UserData' in child_item)):
                                child_item['UserData']={}
                                child_item['UserData']['IsFavorite']=True
                            else: #(('IsFavorite' in child_item['UserData']) or (not ('IsFavorite' in child_item['UserData']))):
                                child_item['UserData']['IsFavorite']=True

    child_dict['Items']=data_dict['data_']['Items']
    child_dict['TotalRecordCount']=len(data_dict['data_']['Items'])
    child_dict['StartIndex']=data_dict['StartIndex_']

    #Return dictionary of child items along with TotalRecordCount
    return child_dict


#Determine if genre is favorited
def get_isGENRE_Fav(user_info,item,isfav_ITEMgenre,favorites_advanced,lookupTopic,the_dict):

    if (('GenreItems' in item) and (does_index_exist(item['GenreItems'],0))):
        #Check if bitmask for favorites by item genre is enabled
        if (favorites_advanced):
            #Check if bitmask for any or first item genre is enabled
            if (favorites_advanced == 1):
                    genre_item_info = get_ADDITIONAL_itemInfo(user_info,item['GenreItems'][0]['Id'],lookupTopic,the_dict)
                    #Check if genre's favorite value already exists in dictionary
                    if not genre_item_info['Id'] in isfav_ITEMgenre:
                        #Store if first genre is marked as favorite
                        isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (genre_item_info['UserData']['IsFavorite']):
                            #Store if the genre is marked as a favorite
                            isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']
            else:
                for genre_item in range(len(item['GenreItems'])):
                    genre_item_info = get_ADDITIONAL_itemInfo(user_info,item['GenreItems'][genre_item]['Id'],lookupTopic + '_any',the_dict)
                    #Check if genre's favorite value already exists in dictionary
                    if not genre_item_info['Id'] in isfav_ITEMgenre:
                        #Store if any genre is marked as a favorite
                        isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (genre_item_info['UserData']['IsFavorite']):
                            #Store if the genre is marked as a favorite
                            isfav_ITEMgenre[genre_item_info['Id']] = genre_item_info['UserData']['IsFavorite']

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nFavorite Info For Item: " + str(item['Id']) + "\n" + convert2json(isfav_ITEMgenre),2,the_dict)

    return(isfav_ITEMgenre)


#Determine if artist is favorited
def get_isARTIST_Fav(user_info,item,isfav_ITEMartist,favorites_advanced,lookupTopic,the_dict):

    if (('ArtistItems' in item) and (does_index_exist(item['ArtistItems'],0))):
        #Check if bitmask for favorites by artist is enabled
        if (favorites_advanced):
            #Check if bitmask for any or first artist is enabled
            if (favorites_advanced == 1):
                artist_item_info = get_ADDITIONAL_itemInfo(user_info,item['ArtistItems'][0]['Id'],lookupTopic + '_info',the_dict)
                #Check if artist's favorite value already exists in dictionary
                if not artist_item_info['Id'] in isfav_ITEMartist:
                    #Store if first artist is marked as favorite
                    isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']
                else: #it already exists
                    #if the value is True save it anyway
                    if (artist_item_info['UserData']['IsFavorite']):
                        #Store if the artist is marked as a favorite
                        isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']
            else:
                for artist in range(len(item['ArtistItems'])):
                    artist_item_info = get_ADDITIONAL_itemInfo(user_info,item['ArtistItems'][artist]['Id'],lookupTopic + '_info_any',the_dict)
                    #Check if artist's favorite value already exists in dictionary
                    if not artist_item_info['Id'] in isfav_ITEMartist:
                        #Store if any track artist is marked as a favorite
                        isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (artist_item_info['UserData']['IsFavorite']):
                            #Store if the artist is marked as a favorite
                            isfav_ITEMartist[artist_item_info['Id']] = artist_item_info['UserData']['IsFavorite']

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nFavorite Info For Item: " + str(item['Id']) + "\n" + convert2json(isfav_ITEMartist),2,the_dict)

    return(isfav_ITEMartist)


#Determine if artist is favorited
def get_isSTUDIONETWORK_Fav(user_info,item,isfav_ITEMstdo_ntwk,favorites_advanced,lookupTopic,the_dict):

    if (('Studios' in  item) and (does_index_exist(item['Studios'],0))):
        #Check if bitmask for favorites by item genre is enabled
        if (favorites_advanced):
            #Check if bitmask for any or first item genre is enabled
            if (favorites_advanced == 1):
                #Get studio network's item info
                studionetwork_item_info = get_ADDITIONAL_itemInfo(user_info,item['Studios'][0]['Id'],'studio_network_info',the_dict)
                #Check if studio-network's favorite value already exists in dictionary
                if not studionetwork_item_info['Id'] in isfav_ITEMstdo_ntwk:
                    if (('UserData' in studionetwork_item_info) and ('IsFavorite' in studionetwork_item_info['UserData'])):
                        #Store if the studio network is marked as a favorite
                        isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']
                else: #it already exists
                    #if the value is True save it anyway
                    if (studionetwork_item_info['UserData']['IsFavorite']):
                        #Store if the studio network is marked as a favorite
                        isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']

            else:
                for studios in range(len(item['Studios'])):
                    #Get studio network's item info
                    studionetwork_item_info = get_ADDITIONAL_itemInfo(user_info,item['Studios'][studios]['Id'],'studio_network_info',the_dict)
                    #Check if studio network's favorite value already exists in dictionary
                    if not studionetwork_item_info['Id'] in isfav_ITEMstdo_ntwk:
                        if (('UserData' in studionetwork_item_info) and ('IsFavorite' in studionetwork_item_info['UserData'])):
                            #Store if the studio network is marked as a favorite
                            isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']
                    else: #it already exists
                        #if the value is True save it anyway
                        if (studionetwork_item_info['UserData']['IsFavorite']):
                            #Store if the studio network is marked as a favorite
                            isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']

    elif ('SeriesStudio' in item):
        #Check if bitmask for favorites by item genre is enabled
        if (favorites_advanced):
            #Get series studio network's item info
            studionetwork_item_info = get_STUDIO_itemInfo(item['SeriesStudio'],the_dict,the_dict)
            #Check if series studio network's favorite value already exists in dictionary
            if not studionetwork_item_info['Id'] in isfav_ITEMstdo_ntwk:
                if (('UserData' in studionetwork_item_info) and ('IsFavorite' in studionetwork_item_info['UserData'])):
                    #Store if the series studio network is marked as a favorite
                    isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']
            else: #it already exists
                #if the value is True save it anyway
                if (studionetwork_item_info['UserData']['IsFavorite']):
                    #Store if the series studio network is marked as a favorite
                    isfav_ITEMstdo_ntwk[studionetwork_item_info['Id']] = studionetwork_item_info['UserData']['IsFavorite']

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nFavorite Info For Item: " + str(item['Id']) + "\n" + convert2json(isfav_ITEMstdo_ntwk),2,the_dict)

    return(isfav_ITEMstdo_ntwk)


#determine if movie set to favorite
def get_isMOVIE_Fav(the_dict,item,user_info):

    user_info=user_info

    isfav_MOVIE={'movie':{}}

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Movie #######################################################################################

        if (('UserData'in item) and ('IsFavorite' in item['UserData'])):
            isfav_MOVIE['movie'][item['Id']]=item['UserData']['IsFavorite']

### End Movie ###################################################################################

    for isfavkey in isfav_MOVIE:
        for isfavID in isfav_MOVIE[isfavkey]:
            if (isfav_MOVIE[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n\nMovie Item " + str(item['Id']) + " is favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nMovie " + str(item['Id']) + " is NOT favorited.",2,the_dict)

    return(False)


#determine if genres for movie or library are set to favorite
def get_isMOVIE_AdvancedFav(the_dict,item,user_info,var_dict):

    advFav_media=var_dict['advFav_media']

    #define empty dictionary for favorited Movies
    isfav_MOVIE={'movielibrary':{},'moviegenre':{},'movielibrarygenre':{}}

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Movie #######################################################################################

        if ('Id' in item):

            if ((not (item['Id'] in isfav_MOVIE['moviegenre'])) or (isfav_MOVIE['moviegenre'][item['Id']] == False)):
                isfav_MOVIE['moviegenre']=get_isGENRE_Fav(user_info,item,isfav_MOVIE['moviegenre'],advFav_media['genre'],'movie_genre',the_dict)

### End Movie ###################################################################################

### Movie Library #######################################################################################

        if ('ParentId' in item):
            movielibrary_item_info = get_ADDITIONAL_itemInfo(user_info,item['ParentId'],'movie_library_info',the_dict)

            if ((not (movielibrary_item_info['Id'] in isfav_MOVIE['movielibrarygenre'])) or (isfav_MOVIE['movielibrarygenre'][movielibrary_item_info['Id']] == False)):
                isfav_MOVIE['movielibrarygenre']=get_isGENRE_Fav(user_info,movielibrary_item_info,isfav_MOVIE['movielibrarygenre'],advFav_media['library_genre'],'movie_library_genre',the_dict)

### End Movie Library ###################################################################################

    for isfavkey in isfav_MOVIE:
        for isfavID in isfav_MOVIE[isfavkey]:
            if (isfav_MOVIE[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n\nMovie Item " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nMovie " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)

    return(False)


#determine if episode, season, or series are set to favorite
def get_isEPISODE_Fav(the_dict,item,user_info):

    isfav_EPISODE={'episode':{},'season':{},'series':{}}

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Episode #######################################################################################

        if (('UserData'in item) and ('IsFavorite' in item['UserData'])):
            isfav_EPISODE['episode'][item['Id']]=item['UserData']['IsFavorite']

### End Episode ###################################################################################

### Season ########################################################################################

        if ('SeasonId' in item):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,item['SeasonId'],'season_info',the_dict)
        elif ('ParentId' in item):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,item['ParentId'],'season_info',the_dict)
        else:
            season_item_info=None

        if (not (season_item_info == None)):
            if ((not (season_item_info['Id'] in isfav_EPISODE['season'])) or (isfav_EPISODE['season'][season_item_info['Id']] == False)):
                isfav_EPISODE['season'][season_item_info['Id']]=season_item_info['UserData']['IsFavorite']

### End Season ####################################################################################

### Series ########################################################################################

            if ('SeriesId' in item):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,item['SeriesId'],'series_info',the_dict)
            elif ('SeriesId' in season_item_info):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,season_item_info['SeriesId'],'series_info',the_dict)
            elif ('ParentId' in season_item_info):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,season_item_info['ParentId'],'series_info',the_dict)
            else:
                series_item_info=None

            if (not (series_item_info == None)):
                if ((not (series_item_info['Id'] in isfav_EPISODE['season'])) or (isfav_EPISODE['season'][series_item_info['Id']] == False)):
                    isfav_EPISODE['series'][series_item_info['Id']]=series_item_info['UserData']['IsFavorite']

### End Series ####################################################################################

    for isfavkey in isfav_EPISODE:
        for isfavID in isfav_EPISODE[isfavkey]:
            if (isfav_EPISODE[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is NOT favorited.",2,the_dict)

    return(False)


#determine if genres for episode, season, series, or studio-network are set to favorite
def get_isEPISODE_AdvancedFav(the_dict,item,user_info,var_dict):

    advFav_media=var_dict['advFav_media']

    #define empty dictionary for favorited TV Series, Seasons, Episodes, and Channels/Networks
    isfav_EPISODE={'tvlibrary':{},'episodegenre':{},'seasongenre':{},'seriesgenre':{},'tvlibrarygenre':{},'seriesstudionetwork':{},'seriesstudionetworkgenre':{}}

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Episode #######################################################################################

        if ('Id' in item):

            if ((not (item['Id'] in isfav_EPISODE['episodegenre'])) or (isfav_EPISODE['episodegenre'][item['Id']] == False)):
                isfav_EPISODE['episodegenre']=get_isGENRE_Fav(user_info,item,isfav_EPISODE['episodegenre'],advFav_media['genre'],'episode_genre',the_dict)

### End Episode ###################################################################################

### Season ########################################################################################

        if ('SeasonId' in item):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,item['SeasonId'],'season_info',the_dict)
        elif ('ParentId' in item):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,item['ParentId'],'season_info',the_dict)
        else:
            season_item_info=None

        if (not (season_item_info == None)):
            if ((not (season_item_info['Id'] in isfav_EPISODE['seasongenre'])) or (isfav_EPISODE['seasongenre'][season_item_info['Id']] == False)):
                isfav_EPISODE['seasongenre']=get_isGENRE_Fav(user_info,season_item_info,isfav_EPISODE['seasongenre'],advFav_media['season_genre'],'season_genre',the_dict)

### End Season ####################################################################################

### Series ########################################################################################

            if ('SeriesId' in item):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,item['SeriesId'],'series_info',the_dict)
            elif ('SeriesId' in season_item_info):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,season_item_info['SeriesId'],'series_info',the_dict)
            elif ('ParentId' in season_item_info):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,season_item_info['ParentId'],'series_info',the_dict)
            else:
                series_item_info=None

            if (not (series_item_info == None)):
                if ((not (series_item_info['Id'] in isfav_EPISODE['seriesgenre'])) or (isfav_EPISODE['seriesgenre'][series_item_info['Id']] == False)):
                    isfav_EPISODE['seriesgenre']=get_isGENRE_Fav(user_info,series_item_info,isfav_EPISODE['seriesgenre'],advFav_media['series_genre'],'series_genre',the_dict)

                if ((not (series_item_info['Id'] in isfav_EPISODE['seriesstudionetwork'])) or (isfav_EPISODE['seriesstudionetwork'][series_item_info['Id']] == False)):
                    isfav_EPISODE['seriesstudionetwork']=get_isSTUDIONETWORK_Fav(user_info,series_item_info,isfav_EPISODE['seriesstudionetwork'],advFav_media['studio_network'],'series studio_network',the_dict)

### End Series ####################################################################################

### TV Library ########################################################################################

                if ('ParentId' in series_item_info):
                    tvlibrary_item_info = get_ADDITIONAL_itemInfo(user_info,series_item_info['ParentId'],'tv_library_info',the_dict)
                else:
                    tvlibrary_item_info=None

                if (not (tvlibrary_item_info == None)):
                    if ((not (tvlibrary_item_info['Id'] in isfav_EPISODE['tvlibrarygenre'])) or (isfav_EPISODE['tvlibrarygenre'][tvlibrary_item_info['Id']] == False)):
                        isfav_EPISODE['tvlibrarygenre']=get_isGENRE_Fav(user_info,tvlibrary_item_info,isfav_EPISODE['tvlibrarygenre'],advFav_media['library_genre'],'tv_library_genre',the_dict)

### End TV Library ####################################################################################

### Studio Network #######################################################################################

                if (('Studios' in series_item_info) and (does_index_exist(series_item_info['Studios'],0))):
                    #Get studio network's item info
                    tvstudionetwork_item_info = get_ADDITIONAL_itemInfo(user_info,series_item_info['Studios'][0]['Id'],'studio_network_info',the_dict)
                elif ('SeriesStudio' in series_item_info):
                    #Get series studio network's item info
                    tvstudionetwork_item_info = get_STUDIO_itemInfo(series_item_info['SeriesStudio'],the_dict)
                else:
                    tvstudionetwork_item_info=None

                if (not (tvstudionetwork_item_info == None)):
                    if ((not (tvstudionetwork_item_info['Id'] in isfav_EPISODE['seriesstudionetworkgenre'])) or (isfav_EPISODE['seriesstudionetworkgenre'][tvstudionetwork_item_info['Id']] == False)):
                        isfav_EPISODE['seriesstudionetworkgenre']=get_isGENRE_Fav(user_info,tvstudionetwork_item_info,isfav_EPISODE['seriesstudionetworkgenre'],advFav_media['studio_network_genre'],'series_studio_network_genre',the_dict)

### End Studio Network ###################################################################################

    for isfavkey in isfav_EPISODE:
        for isfavID in isfav_EPISODE[isfavkey]:
            if (isfav_EPISODE[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)

    return(False)


#determine if music track or album are set to favorite
def get_isAUDIO_Fav(the_dict,item,user_info,var_dict):

    itemType=var_dict['media_type_title']

    if (itemType == 'Audio'):
        lookupTopicAlbum='album'
    elif (itemType == 'AudioBook'):
        lookupTopicAlbum='book'
    else:
        raise ValueError('ValueError: Unknown itemType passed into get_isAUDIO_AdvancedFav')

    #define empty dictionary for favorited Tracks and Albums
    isfav_AUDIO={'track':{},'album':{}}

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Track #########################################################################################

        if (('UserData'in item) and ('IsFavorite' in item['UserData']) and ()):
            isfav_AUDIO['track'][item['Id']]=item['UserData']['IsFavorite']

### End Track #####################################################################################

### Album/Book #########################################################################################

        #Albums for music
        if ('ParentId' in item):
            album_item_info = get_ADDITIONAL_itemInfo(user_info,item['ParentId'],lookupTopicAlbum + '_info',the_dict)
        elif ('AlbumId' in item):
            album_item_info = get_ADDITIONAL_itemInfo(user_info,item['AlbumId'],lookupTopicAlbum + '_info',the_dict)
        else:
            album_item_info=None

        if (not (album_item_info == None)):
            if ((not (album_item_info['Id'] in isfav_AUDIO['album'])) or (isfav_AUDIO['album'][album_item_info['Id']] == False)):
                isfav_AUDIO['album'][album_item_info['Id']]=album_item_info['UserData']['IsFavorite']

### End Album/Book #####################################################################################

    for isfavkey in isfav_AUDIO:
        for isfavID in isfav_AUDIO[isfavkey]:
            if (isfav_AUDIO[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    if (itemType == 'Audio'):
                        appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is favorited.",2,the_dict)
                    elif (itemType == 'AudioBook'):
                        appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is favorited.",2,the_dict)
                    else:
                        appendTo_DEBUG_log("\n\nUnknown Audio Type " + str(item['Id']) + " is favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        if (itemType == 'Audio'):
            appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is NOT favorited.",2,the_dict)
        elif (itemType == 'AudioBook'):
            appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is NOT favorited.",2,the_dict)
        else:
            appendTo_DEBUG_log("\n\nUnknown Audio Type " + str(item['Id']) + " is NOT favorited.",2,the_dict)

    return(False)


#determine if genres for music track, album, or artist are set to favorite
def get_isAUDIO_AdvancedFav(the_dict,item,user_info,var_dict):

    itemType=var_dict['media_type_title']

    if (itemType == 'Audio'):
        lookupTopicTrack='track'
        lookupTopicAlbum='album'
        lookupTopicLibrary='music_library'
        favorited_advanced_track_genre=var_dict['advFav_media']['genre']
        favorited_advanced_album_genre=var_dict['advFav_media']['album_genre']
        favorited_advanced_music_library_genre=var_dict['advFav_media']['library_genre']
        favorited_advanced_track_artist=var_dict['advFav_media']['track_artist']
        favorited_advanced_album_library_artist=0
        favorited_advanced_album_artist=var_dict['advFav_media']['album_artist']
    elif (itemType == 'AudioBook'):
        lookupTopicTrack='audiobook'
        lookupTopicAlbum='book'
        lookupTopicLibrary='audiobook_library'
        favorited_advanced_track_genre=var_dict['advFav_media']['genre']
        favorited_advanced_album_genre=var_dict['advFav_media']['audiobook_genre']
        favorited_advanced_music_library_genre=var_dict['advFav_media']['library_genre']
        favorited_advanced_track_artist=var_dict['advFav_media']['track_author']
        favorited_advanced_album_library_artist=var_dict['advFav_media']['author']
        favorited_advanced_album_artist=var_dict['advFav_media']['library_author']
    else:
        raise ValueError('ValueError: Unknown itemType passed into get_isAUDIO_AdvancedFav')

    #define empty dictionary for favorited Tracks, Albums, Artists
    isfav_AUDIO={'track':{},'album':{},'artist':{},'composer':{},'audiolibrary':{},'trackgenre':{},'albumgenre':{},'trackartist':{},'albumartist':{},'audiolibraryartist':{},'composergenre':{},'audiolibrarygenre':{}}

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Track #########################################################################################

        if ('Id' in item):

            if ((not (item['Id'] in isfav_AUDIO['trackgenre'])) or (isfav_AUDIO['trackgenre'][item['Id']] == False)):
                isfav_AUDIO['trackgenre']=get_isGENRE_Fav(user_info,item,isfav_AUDIO['trackgenre'],favorited_advanced_track_genre,lookupTopicTrack + '_genre',the_dict)

            if ((not (item['Id'] in isfav_AUDIO['trackartist'])) or (isfav_AUDIO['trackartist'][item['Id']] == False)):
                isfav_AUDIO['trackartist']=get_isARTIST_Fav(user_info,item,isfav_AUDIO['trackartist'],favorited_advanced_track_artist,lookupTopicTrack + '_artist',the_dict)

### End Track #####################################################################################

### Album/Book #########################################################################################

        #Albums for music
        if ('ParentId' in item):
            album_item_info = get_ADDITIONAL_itemInfo(user_info,item['ParentId'],'album_info',the_dict)
        elif ('AlbumId' in item):
            album_item_info = get_ADDITIONAL_itemInfo(user_info,item['AlbumId'],'album_info',the_dict)
        else:
            album_item_info=None

        if (not (album_item_info == None)):
            if ((not (album_item_info['Id'] in isfav_AUDIO['albumgenre'])) or (isfav_AUDIO['albumgenre'][album_item_info['Id']] == False)):
                isfav_AUDIO['albumgenre']=get_isGENRE_Fav(user_info,album_item_info,isfav_AUDIO['albumgenre'],favorited_advanced_album_genre,lookupTopicAlbum + '_genre',the_dict)

            if ((not (album_item_info['Id'] in isfav_AUDIO['albumartist'])) or (isfav_AUDIO['albumartist'][album_item_info['Id']] == False)):
                isfav_AUDIO['albumartist']=get_isARTIST_Fav(user_info,album_item_info,isfav_AUDIO['albumartist'],favorited_advanced_album_artist,lookupTopicAlbum + '_artist',the_dict)

            if (itemType == 'AudioBook'):
                if ((not (album_item_info['Id'] in isfav_AUDIO['libraryartist'])) or (isfav_AUDIO['libraryartist'][album_item_info['Id']] == False)):
                    isfav_AUDIO['libraryartist']=get_isARTIST_Fav(user_info,album_item_info,isfav_AUDIO['libraryartist'],favorited_advanced_album_library_artist,lookupTopicAlbum + '_library_artist',the_dict)

### End Album/Book #####################################################################################

### Library ########################################################################################

            #Library
            if ('ParentId' in album_item_info):
                audiolibrary_item_info = get_ADDITIONAL_itemInfo(user_info,album_item_info['ParentId'],'library_info',the_dict)
            else:
                audiolibrary_item_info=None

            if (not (audiolibrary_item_info == None)):
                if ((not (audiolibrary_item_info['Id'] in isfav_AUDIO['audiolibrarygenre'])) or (isfav_AUDIO['audiolibrarygenre'][audiolibrary_item_info['Id']] == False)):
                    isfav_AUDIO['audiolibrarygenre']=get_isGENRE_Fav(user_info,audiolibrary_item_info,isfav_AUDIO['audiolibrarygenre'],favorited_advanced_music_library_genre,lookupTopicLibrary + '_genre',the_dict)

### End Library #####################################################################################

    for isfavkey in isfav_AUDIO:
        for isfavID in isfav_AUDIO[isfavkey]:
            if (isfav_AUDIO[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    if (itemType == 'Audio'):
                        appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                    elif (itemType == 'AudioBook'):
                        appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                    else:
                        appendTo_DEBUG_log("\n\nUnknown Audio Type " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        if (itemType == 'Audio'):
            appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)
        elif (itemType == 'AudioBook'):
            appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)
        else:
            appendTo_DEBUG_log("\n\nUnknown Audio Type " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)

    return(False)


#determine if audiobook track or book are set to favorite
def get_isAUDIOBOOK_Fav(the_dict,item,user_info,var_dict):
    return get_isAUDIO_Fav(the_dict,item,user_info,var_dict)


#determine if genres for audiobook track, book, or author are set to favorite
def get_isAUDIOBOOK_AdvancedFav(the_dict,item,user_info,var_dict):
    return get_isAUDIO_AdvancedFav(the_dict,item,user_info,var_dict)