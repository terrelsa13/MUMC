#!/usr/bin/env python3
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_played_created import get_isPlayedCreated_FilterValue,get_playedCreatedDays_playedCreatedCounts
from mumc_modules.mumc_url import api_query_handler
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo,get_STUDIO_itemInfo
from mumc_modules.mumc_compare_items import does_index_exist
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json


#Get children of favorited parents
def getChildren_favoritedMediaItems(user_key,data_Favorited,filter_played_count_comparison,filter_played_count,filter_created_played_count_comparison,filter_created_played_count,APIDebugMsg,played_days,created_days,the_dict):
    server_url=the_dict['server_url']
    auth_key=the_dict['auth_key']
    child_list=[]
    StartIndex=0

    #Loop thru items returned as favorited
    for data in data_Favorited['Items']:

        #Verify media item is a parent (not a child like an episode, movie, or audio)
        if ((data['IsFolder'] == True) or (data['Type'] == 'Book')):

            user_processed_itemsId=set()

            #Initialize api_query_handler() variables for watched child media items
            StartIndex=0
            TotalItems=1
            QueryLimit=1
            QueriesRemaining=True

            if not (data['Id'] == ''):
                #Build query for child media items
                #include all item types; filter applied in first API calls for each media type in get_media_items()
                IncludeItemTypes=''
                FieldsState='Id,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,UserData'
                if (isJellyfinServer(the_dict['server_brand'])):
                    SortBy='SeriesSortName'
                else:
                    SortBy='SeriesName'
                SortBy=SortBy + ',AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                SortOrder='Ascending'
                Recursive='True'
                EnableImages='False'
                CollapseBoxSetItems='False'
                IsPlayedState=get_isPlayedCreated_FilterValue(the_dict,played_days,created_days,filter_played_count_comparison,filter_played_count,filter_created_played_count_comparison,filter_created_played_count)

                while (QueriesRemaining):

                    if not (data['Id'] == ''):
                        #Built query for child meida items
                        apiQuery=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + data['Id'] + '&IncludeItemTypes=' + IncludeItemTypes +
                        '&StartIndex=' + str(StartIndex) + '&Limit=' + str(QueryLimit) + '&IsPlayed=' + IsPlayedState + '&Fields=' + FieldsState +
                        '&CollapseBoxSetItems=' + CollapseBoxSetItems + '&Recursive=' + Recursive + '&SortBy=' + SortBy + '&SortOrder=' + SortOrder + '&EnableImages=' + EnableImages + '&api_key=' + auth_key)

                        #Send the API query for for watched media items in blacklists
                        children_data,StartIndex,TotalItems,QueryLimit,QueriesRemaining=api_query_handler(apiQuery,StartIndex,TotalItems,QueryLimit,APIDebugMsg,the_dict)
                    else:
                        #When no media items are returned; simulate an empty query being returned
                        #this will prevent trying to compare to an empty string '' to the whitelist libraries later on
                        children_data={'Items':[],'TotalRecordCount':0,'StartIndex':0}
                        QueryLimit=0
                        QueriesRemaining=False
                        if (the_dict['DEBUG']):
                            appendTo_DEBUG_log("\n\nNo " + APIDebugMsg + " media items found",2,the_dict)
                            

                    #Loop thru the returned child items
                    for child_item in children_data['Items']:
                        #Check if child item has already been processed
                        if not (child_item['Id'] in user_processed_itemsId):
                            #Check if media item has any favs
                            if not ('UserData' in child_item):
                                #if it does not; add fav to metadata
                                child_item['UserData']={'IsFavorite':True}
                            elif not ('IsFavorite' in child_item['UserData']):
                                #if it does not; add fav to metadata
                                child_item['UserData']['IsFavorite']=True
                            #if child_item is not already a fav; update this temp metadata so it is a fav
                            elif not (child_item['UserData']['IsFavorite']):
                                child_item['UserData']['IsFavorite']=True

                            #assign fav to metadata
                            child_list.append(child_item)
                            user_processed_itemsId.add(child_item['Id'])

                            if (the_dict['DEBUG']):
                                appendTo_DEBUG_log('\nChild item with Id: ' + str(child_item['Id']) + ' marked as favorite',2,the_dict)

    #Return dictionary of child items along with TotalRecordCount
    return({'Items':child_list,'TotalRecordCount':len(child_list),'StartIndex':StartIndex})


#Determine if genre is favorited
def get_isGENRE_Fav(user_key,item,isfav_ITEMgenre,favorites_advanced,lookupTopic,the_dict):

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    if (('GenreItems' in item) and (does_index_exist(item['GenreItems'],0,the_dict))):
        #Check if bitmask for favorites by item genre is enabled
        if (favorites_advanced):
            #Check if bitmask for any or first item genre is enabled
            if (favorites_advanced == 1):
                    genre_item_info = get_ADDITIONAL_itemInfo(user_key,item['GenreItems'][0]['Id'],lookupTopic,the_dict)
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
                    genre_item_info = get_ADDITIONAL_itemInfo(user_key,item['GenreItems'][genre_item]['Id'],lookupTopic + '_any',the_dict)
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
        appendTo_DEBUG_log("\nFavorite Info For Item: " + str(item['Id']) + "\n" + convert2json(isfav_ITEMgenre),2,the_dict)

    return(isfav_ITEMgenre)


#Determine if artist is favorited
def get_isARTIST_Fav(user_key,item,isfav_ITEMartist,favorites_advanced,lookupTopic,the_dict):

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    if (('ArtistItems' in item) and (does_index_exist(item['ArtistItems'],0,the_dict))):
        #Check if bitmask for favorites by artist is enabled
        if (favorites_advanced):
            #Check if bitmask for any or first artist is enabled
            if (favorites_advanced == 1):
                artist_item_info = get_ADDITIONAL_itemInfo(user_key,item['ArtistItems'][0]['Id'],lookupTopic + '_info',the_dict)
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
                    artist_item_info = get_ADDITIONAL_itemInfo(user_key,item['ArtistItems'][artist]['Id'],lookupTopic + '_info_any',the_dict)
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
        appendTo_DEBUG_log("\nFavorite Info For Item: " + str(item['Id']) + "\n" + convert2json(isfav_ITEMartist),2,the_dict)

    return(isfav_ITEMartist)


#Determine if artist is favorited
def get_isSTUDIONETWORK_Fav(user_key,item,isfav_ITEMstdo_ntwk,favorites_advanced,lookupTopic,the_dict):

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    if (('Studios' in  item) and (does_index_exist(item['Studios'],0,the_dict))):
        #Check if bitmask for favorites by item genre is enabled
        if (favorites_advanced):
            #Check if bitmask for any or first item genre is enabled
            if (favorites_advanced == 1):
                #Get studio network's item info
                studionetwork_item_info = get_ADDITIONAL_itemInfo(user_key,item['Studios'][0]['Id'],'studio_network_info',the_dict)
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
                    studionetwork_item_info = get_ADDITIONAL_itemInfo(user_key,item['Studios'][studios]['Id'],'studio_network_info',the_dict)
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
        appendTo_DEBUG_log("\nFavorite Info For Item: " + str(item['Id']) + "\n" + convert2json(isfav_ITEMstdo_ntwk),2,the_dict)

    return(isfav_ITEMstdo_ntwk)


#determine if movie set to favorite
def get_isMOVIE_Fav(the_dict,item,user_key):

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    user_key=user_key

    isfav_MOVIE={'movie':{}}

### Movie #######################################################################################

    if (('UserData'in item) and ('IsFavorite' in item['UserData'])):
        isfav_MOVIE['movie'][item['Id']]=item['UserData']['IsFavorite']

### End Movie ###################################################################################

    for isfavkey in isfav_MOVIE:
        for isfavID in isfav_MOVIE[isfavkey]:
            if (isfav_MOVIE[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nMovie Item " + str(item['Id']) + " is favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nMovie " + str(item['Id']) + " is NOT favorited.",2,the_dict)

    return(False)


#determine if genres for movie or library are set to favorite
def get_isMOVIE_AdvancedFav(the_dict,item,user_key,favorited_advanced_movie_genre,favorited_advanced_movie_library_genre):

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    #define empty dictionary for favorited Movies
    isfav_MOVIE={'movielibrary':{},'moviegenre':{},'movielibrarygenre':{}}

### Movie #######################################################################################

    if ('Id' in item):

        if ((not (item['Id'] in isfav_MOVIE['moviegenre'])) or (isfav_MOVIE['moviegenre'][item['Id']] == False)):
            isfav_MOVIE['moviegenre']=get_isGENRE_Fav(user_key,item,isfav_MOVIE['moviegenre'],favorited_advanced_movie_genre,'movie_genre',the_dict)

### End Movie ###################################################################################

### Movie Library #######################################################################################

    if ('ParentId' in item):
        movielibrary_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'movie_library_info',the_dict)

        if ((not (movielibrary_item_info['Id'] in isfav_MOVIE['movielibrarygenre'])) or (isfav_MOVIE['movielibrarygenre'][movielibrary_item_info['Id']] == False)):
            isfav_MOVIE['movielibrarygenre']=get_isGENRE_Fav(user_key,movielibrary_item_info,isfav_MOVIE['movielibrarygenre'],favorited_advanced_movie_library_genre,'movie_library_genre',the_dict)

### End Movie Library ###################################################################################

    for isfavkey in isfav_MOVIE:
        for isfavID in isfav_MOVIE[isfavkey]:
            if (isfav_MOVIE[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nMovie Item " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nMovie " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)

    return(False)


#determine if episode, season, or series are set to favorite
def get_isEPISODE_Fav(the_dict,item,user_key):

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    isfav_EPISODE={'episode':{},'season':{},'series':{}}

### Episode #######################################################################################

    if (('UserData'in item) and ('IsFavorite' in item['UserData'])):
        isfav_EPISODE['episode'][item['Id']]=item['UserData']['IsFavorite']

### End Episode ###################################################################################

### Season ########################################################################################

    if ('SeasonId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeasonId'],'season_info',the_dict)
    elif ('ParentId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'season_info',the_dict)

    if ((not (season_item_info['Id'] in isfav_EPISODE['season'])) or (isfav_EPISODE['season'][season_item_info['Id']] == False)):
        isfav_EPISODE['season'][season_item_info['Id']]=season_item_info['UserData']['IsFavorite']

### End Season ####################################################################################

### Series ########################################################################################

    if ('SeriesId' in item):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeriesId'],'series_info',the_dict)
    elif ('SeriesId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['SeriesId'],'series_info',the_dict)
    elif ('ParentId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['ParentId'],'series_info',the_dict)

    if ((not (series_item_info['Id'] in isfav_EPISODE['season'])) or (isfav_EPISODE['season'][series_item_info['Id']] == False)):
        isfav_EPISODE['series'][series_item_info['Id']]=series_item_info['UserData']['IsFavorite']

### End Series ####################################################################################

    for isfavkey in isfav_EPISODE:
        for isfavID in isfav_EPISODE[isfavkey]:
            if (isfav_EPISODE[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is NOT favorited.",2,the_dict)

    return(False)


#determine if genres for episode, season, series, or studio-network are set to favorite
def get_isEPISODE_AdvancedFav(the_dict,item,user_key,favorited_advanced_episode_genre,favorited_advanced_season_genre,favorited_advanced_series_genre,
                              favorited_advanced_tv_library_genre,favorited_advanced_tv_studio_network,favorited_advanced_tv_studio_network_genre):

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    #define empty dictionary for favorited TV Series, Seasons, Episodes, and Channels/Networks
    isfav_EPISODE={'tvlibrary':{},'episodegenre':{},'seasongenre':{},'seriesgenre':{},'tvlibrarygenre':{},'seriesstudionetwork':{},'seriesstudionetworkgenre':{}}

### Episode #######################################################################################

    if ('Id' in item):

        if ((not (item['Id'] in isfav_EPISODE['episodegenre'])) or (isfav_EPISODE['episodegenre'][item['Id']] == False)):
            isfav_EPISODE['episodegenre']=get_isGENRE_Fav(user_key,item,isfav_EPISODE['episodegenre'],favorited_advanced_episode_genre,'episode_genre',the_dict)

### End Episode ###################################################################################

### Season ########################################################################################

    if ('SeasonId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeasonId'],'season_info',the_dict)
    elif ('ParentId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'season_info',the_dict)

    if ((not (season_item_info['Id'] in isfav_EPISODE['seasongenre'])) or (isfav_EPISODE['seasongenre'][season_item_info['Id']] == False)):
        isfav_EPISODE['seasongenre']=get_isGENRE_Fav(user_key,season_item_info,isfav_EPISODE['seasongenre'],favorited_advanced_season_genre,'season_genre',the_dict)

### End Season ####################################################################################

### Series ########################################################################################

    if ('SeriesId' in item):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeriesId'],'series_info',the_dict)
    elif ('SeriesId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['SeriesId'],'series_info',the_dict)
    elif ('ParentId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['ParentId'],'series_info',the_dict)

    if ((not (series_item_info['Id'] in isfav_EPISODE['seriesgenre'])) or (isfav_EPISODE['seriesgenre'][series_item_info['Id']] == False)):
        isfav_EPISODE['seriesgenre']=get_isGENRE_Fav(user_key,series_item_info,isfav_EPISODE['seriesgenre'],favorited_advanced_series_genre,'series_genre',the_dict)

    if ((not (series_item_info['Id'] in isfav_EPISODE['seriesstudionetwork'])) or (isfav_EPISODE['seriesstudionetwork'][series_item_info['Id']] == False)):
        isfav_EPISODE['seriesstudionetwork']=get_isSTUDIONETWORK_Fav(user_key,series_item_info,isfav_EPISODE['seriesstudionetwork'],favorited_advanced_tv_studio_network,'studio_network',the_dict)

### End Series ####################################################################################

### TV Library ########################################################################################

    if ('ParentId' in series_item_info):
        tvlibrary_item_info = get_ADDITIONAL_itemInfo(user_key,series_item_info['ParentId'],'tv_library_info',the_dict)

    if ((not (tvlibrary_item_info['Id'] in isfav_EPISODE['tvlibrarygenre'])) or (isfav_EPISODE['tvlibrarygenre'][tvlibrary_item_info['Id']] == False)):
        isfav_EPISODE['tvlibrarygenre']=get_isGENRE_Fav(user_key,tvlibrary_item_info,isfav_EPISODE['tvlibrarygenre'],favorited_advanced_tv_library_genre,'tv_library_genre',the_dict)

### End TV Library ####################################################################################

### Studio Network #######################################################################################

    if (('Studios' in series_item_info) and (does_index_exist(series_item_info['Studios'],0,the_dict))):
        #Get studio network's item info
        tvstudionetwork_item_info = get_ADDITIONAL_itemInfo(user_key,series_item_info['Studios'][0]['Id'],'studio_network_info',the_dict)
    elif ('SeriesStudio' in series_item_info):
        #Get series studio network's item info
        tvstudionetwork_item_info = get_STUDIO_itemInfo(series_item_info['SeriesStudio'],the_dict)

    if ((not (tvstudionetwork_item_info['Id'] in isfav_EPISODE['seriesstudionetworkgenre'])) or (isfav_EPISODE['seriesstudionetworkgenre'][tvstudionetwork_item_info['Id']] == False)):
        isfav_EPISODE['seriesstudionetworkgenre']=get_isGENRE_Fav(user_key,tvstudionetwork_item_info,isfav_EPISODE['seriesstudionetworkgenre'],favorited_advanced_tv_studio_network_genre,'studio_network_genre',the_dict)

### End Studio Network ###################################################################################

    for isfavkey in isfav_EPISODE:
        for isfavID in isfav_EPISODE[isfavkey]:
            if (isfav_EPISODE[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)

    return(False)


#determine if music track or album are set to favorite
def get_isAUDIO_Fav(the_dict,item,user_key,itemType):

    if (itemType == 'Audio'):
        lookupTopicAlbum='album'
    elif (itemType == 'AudioBook'):
        lookupTopicAlbum='book'
    else:
        raise ValueError('ValueError: Unknown itemType passed into get_isAUDIO_AdvancedFav')

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    #define empty dictionary for favorited Tracks and Albums
    isfav_AUDIO={'track':{},'album':{}}

### Track #########################################################################################

    if (('UserData'in item) and ('IsFavorite' in item['UserData']) and ()):
        isfav_AUDIO['track'][item['Id']]=item['UserData']['IsFavorite']

### End Track #####################################################################################

### Album/Book #########################################################################################

    #Albums for music
    if ('ParentId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],lookupTopicAlbum + '_info',the_dict)
    elif ('AlbumId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['AlbumId'],lookupTopicAlbum + '_info',the_dict)

    if ((not (album_item_info['Id'] in isfav_AUDIO['album'])) or (isfav_AUDIO['album'][album_item_info['Id']] == False)):
        isfav_AUDIO['album'][album_item_info['Id']]=album_item_info['UserData']['IsFavorite']

### End Album/Book #####################################################################################

    for isfavkey in isfav_AUDIO:
        for isfavID in isfav_AUDIO[isfavkey]:
            if (isfav_AUDIO[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    if (itemType == 'Audio'):
                        appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is favorited.",2,the_dict)
                    elif (itemType == 'AudioBook'):
                        appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is favorited.",2,the_dict)
                    else:
                        appendTo_DEBUG_log("\nUnknown Audio Type " + str(item['Id']) + " is favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        if (itemType == 'Audio'):
            appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is NOT favorited.",2,the_dict)
        elif (itemType == 'AudioBook'):
            appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is NOT favorited.",2,the_dict)
        else:
            appendTo_DEBUG_log("\nUnknown Audio Type " + str(item['Id']) + " is NOT favorited.",2,the_dict)

    return(False)


#determine if genres for music track, album, or artist are set to favorite
def get_isAUDIO_AdvancedFav(the_dict,item,user_key,itemType,favorited_advanced_track_genre,favorited_advanced_album_genre,
                            favorited_advanced_music_library_genre,favorited_advanced_track_artist,favorited_advanced_album_artist,favorited_advanced_album_library_artist=0):

    if (itemType == 'Audio'):
        lookupTopicTrack='track'
        lookupTopicAlbum='album'
        lookupTopicLibrary='music_library'
    elif (itemType == 'AudioBook'):
        lookupTopicTrack='audiobook'
        lookupTopicAlbum='book'
        lookupTopicLibrary='audiobook_library'
    else:
        raise ValueError('ValueError: Unknown itemType passed into get_isAUDIO_AdvancedFav')

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    #define empty dictionary for favorited Tracks, Albums, Artists
    isfav_AUDIO={'track':{},'album':{},'artist':{},'composer':{},'audiolibrary':{},'trackgenre':{},'albumgenre':{},'trackartist':{},'albumartist':{},'audiolibraryartist':{},'composergenre':{},'audiolibrarygenre':{}}

### Track #########################################################################################

    if ('Id' in item):

        if ((not (item['Id'] in isfav_AUDIO['trackgenre'])) or (isfav_AUDIO['trackgenre'][item['Id']] == False)):
            isfav_AUDIO['trackgenre']=get_isGENRE_Fav(user_key,item,isfav_AUDIO['trackgenre'],favorited_advanced_track_genre,lookupTopicTrack + '_genre',the_dict)

        if ((not (item['Id'] in isfav_AUDIO['trackartist'])) or (isfav_AUDIO['trackartist'][item['Id']] == False)):
            isfav_AUDIO['trackartist']=get_isARTIST_Fav(user_key,item,isfav_AUDIO['trackartist'],favorited_advanced_track_artist,lookupTopicTrack + '_artist',the_dict)

### End Track #####################################################################################

### Album/Book #########################################################################################

    #Albums for music
    if ('ParentId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'album_info',the_dict)
    elif ('AlbumId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['AlbumId'],'album_info',the_dict)

    if ((not (album_item_info['Id'] in isfav_AUDIO['albumgenre'])) or (isfav_AUDIO['albumgenre'][album_item_info['Id']] == False)):
        isfav_AUDIO['albumgenre']=get_isGENRE_Fav(user_key,album_item_info,isfav_AUDIO['albumgenre'],favorited_advanced_album_genre,lookupTopicAlbum + '_genre',the_dict)

    if ((not (album_item_info['Id'] in isfav_AUDIO['albumartist'])) or (isfav_AUDIO['albumartist'][album_item_info['Id']] == False)):
        isfav_AUDIO['albumartist']=get_isARTIST_Fav(user_key,album_item_info,isfav_AUDIO['albumartist'],favorited_advanced_album_artist,lookupTopicAlbum + '_artist',the_dict)

    if ((not (album_item_info['Id'] in isfav_AUDIO['libraryartist'])) or (isfav_AUDIO['libraryartist'][album_item_info['Id']] == False)):
        isfav_AUDIO['libraryartist']=get_isARTIST_Fav(user_key,album_item_info,isfav_AUDIO['libraryartist'],favorited_advanced_album_library_artist,lookupTopicAlbum + '_library_artist',the_dict)

### End Album/Book #####################################################################################

### Library ########################################################################################

    #Library
    if ('ParentId' in album_item_info):
        audiolibrary_item_info = get_ADDITIONAL_itemInfo(user_key,album_item_info['ParentId'],'library_info',the_dict)

        if ((not (audiolibrary_item_info['Id'] in isfav_AUDIO['audiolibrarygenre'])) or (isfav_AUDIO['audiolibrarygenre'][audiolibrary_item_info['Id']] == False)):
            isfav_AUDIO['audiolibrarygenre']=get_isGENRE_Fav(user_key,audiolibrary_item_info,isfav_AUDIO['audiolibrarygenre'],favorited_advanced_music_library_genre,lookupTopicLibrary + '_genre',the_dict)

### End Library #####################################################################################

    for isfavkey in isfav_AUDIO:
        for isfavID in isfav_AUDIO[isfavkey]:
            if (isfav_AUDIO[isfavkey][isfavID]):
                if (the_dict['DEBUG']):
                    if (itemType == 'Audio'):
                        appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                    elif (itemType == 'AudioBook'):
                        appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                    else:
                        appendTo_DEBUG_log("\nUnknown Audio Type " + str(item['Id']) + " is advanced favorited.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        if (itemType == 'Audio'):
            appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)
        elif (itemType == 'AudioBook'):
            appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)
        else:
            appendTo_DEBUG_log("\nUnknown Audio Type " + str(item['Id']) + " is NOT advanced favorited.",2,the_dict)

    return(False)


#determine if audiobook track or book are set to favorite
def get_isAUDIOBOOK_Fav(the_dict,item,user_key,itemType):
    return get_isAUDIO_Fav(the_dict,item,user_key,itemType)


#determine if genres for audiobook track, book, or author are set to favorite
def get_isAUDIOBOOK_AdvancedFav(the_dict,item,user_key,itemType,favorited_advanced_audiobook_track_genre,favorited_advanced_audiobook_genre,
                                favorited_advanced_audiobook_library_genre,favorited_advanced_audiobook_track_author,favorited_advanced_audiobook_author,favorited_advanced_audiobook_library_author):
    return get_isAUDIO_AdvancedFav(the_dict,item,user_key,itemType,favorited_advanced_audiobook_track_genre,favorited_advanced_audiobook_genre,
                                   favorited_advanced_audiobook_library_genre,favorited_advanced_audiobook_track_author,favorited_advanced_audiobook_author,favorited_advanced_audiobook_library_author)


#Because we are not searching directly for non-favorited items; cleanup needs to happen to help the behavioral patterns make sense
#def favorites_playedPatternCleanup(itemsDictionary,itemsExtraDictionary,media_played_days,media_created_days,cut_off_date_played_media,cut_off_date_created_media,media_played_count_comparison,media_played_count,media_created_played_count_comparison,media_created_played_count,favorited_behavior_media,advFav0,advFav1,advFav2=0,advFav3=0,advFav4=0,advFav5=0):
def favorites_playedPatternCleanup(the_dict,itemsDictionary,itemsExtraDictionary,postproc_dict):
    userId_tracker=[]
    itemId_tracker=[]

    favorited_behavior_media=postproc_dict['favorited_behavior_media']
    advFav0=postproc_dict['advFav0_media']
    advFav1=postproc_dict['advFav1_media']
    advFav2=postproc_dict['advFav2_media']
    advFav3=postproc_dict['advFav3_media']
    advFav4=postproc_dict['advFav4_media']
    advFav5=postproc_dict['advFav5_media']

    for userId in itemsDictionary:
        userId_tracker.append(userId)

    for userId in itemsDictionary:
        for itemId in itemsDictionary[userId]:
            if not (itemId in itemId_tracker):
                itemId_tracker.append(itemId)
                for subUserId in userId_tracker:
                    if (not(userId == subUserId)):
                        if (not(itemId in itemsDictionary[subUserId])):

                            item=get_ADDITIONAL_itemInfo(subUserId,itemId,'favorites_playedPatternCleanup',the_dict)

                            itemsDictionary[subUserId][itemId]=item

                            itemIsFav=False
                            itemIsAdvFav=False
                            if (item['Type'].casefold() == 'movie'):
                                itemIsFav=get_isMOVIE_Fav(the_dict,item,subUserId)
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nMovie is favorite: " + str(itemIsFav),3,the_dict)
                                if ((favorited_behavior_media[3] >= 0) and (advFav0 or advFav1)):
                                    itemIsAdvFav=get_isMOVIE_AdvancedFav(the_dict,item,subUserId,advFav0,advFav1)
                                    if (the_dict['DEBUG']):
                                        appendTo_DEBUG_log("\nadvFav0: " + str(advFav0),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav1: " + str(advFav1),3,the_dict)
                            elif (item['Type'].casefold() == 'episode'):
                                itemIsFav=get_isEPISODE_Fav(the_dict,item,subUserId)
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nEpisode is favorite: " + str(itemIsFav),3,the_dict)
                                if ((favorited_behavior_media[3] >= 0) and (advFav0 or advFav1 or advFav2 or advFav3 or advFav4 or advFav5)):
                                    itemIsAdvFav=get_isEPISODE_AdvancedFav(the_dict,item,subUserId,advFav0,advFav1,advFav2,advFav3,advFav4,advFav5)
                                    if (the_dict['DEBUG']):
                                        appendTo_DEBUG_log("\nadvFav0: " + str(advFav0),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav1: " + str(advFav1),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav2: " + str(advFav2),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav3: " + str(advFav3),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav4: " + str(advFav4),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav5: " + str(advFav5),3,the_dict)
                            elif (item['Type'].casefold() == 'audio'):
                                itemIsFav=get_isAUDIO_Fav(the_dict,item,subUserId,'Audio')
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nAudio is favorite: " + str(itemIsFav),3,the_dict)
                                if ((favorited_behavior_media[3] >= 0) and (advFav0 or advFav1 or advFav2 or advFav3 or advFav4)):
                                    itemIsAdvFav=get_isAUDIO_AdvancedFav(the_dict,item,subUserId,'Audio',advFav0,advFav1,advFav2,advFav3,advFav4)
                                    if (the_dict['DEBUG']):
                                        appendTo_DEBUG_log("\nadvFav0: " + str(advFav0),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav1: " + str(advFav1),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav2: " + str(advFav2),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav3: " + str(advFav3),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav4: " + str(advFav4),3,the_dict)
                            elif (item['Type'].casefold() == 'audiobook'):
                                itemIsFav=get_isAUDIOBOOK_Fav(the_dict,item,subUserId,'AudioBook')
                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log("\nAudioBook is favorite: " + str(itemIsFav),3,the_dict)
                                if ((favorited_behavior_media[3] >= 0) and (advFav0 or advFav1 or advFav2 or advFav3 or advFav4 or advFav5)):
                                    itemIsAdvFav=get_isAUDIOBOOK_AdvancedFav(the_dict,item,subUserId,'AudioBook',advFav0,advFav1,advFav2,advFav3,advFav4,advFav5)
                                    if (the_dict['DEBUG']):
                                        appendTo_DEBUG_log("\nadvFav0: " + str(advFav0),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav1: " + str(advFav1),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav2: " + str(advFav2),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav3: " + str(advFav3),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav4: " + str(advFav4),3,the_dict)
                                        appendTo_DEBUG_log("\nadvFav5: " + str(advFav5),3,the_dict)

                            if (itemIsFav or itemIsAdvFav):
                                itemsExtraDictionary[subUserId][itemId]['IsMeetingAction']=True
                            else:
                                #itemsExtraDictionary[subUserId][itemId]['IsMeetingAction']=None
                                itemsExtraDictionary[subUserId][itemId]['IsMeetingAction']=False

                            mediaItemAdditionalInfo=get_ADDITIONAL_itemInfo(subUserId,itemId,'playedPatternCleanup',the_dict)
                            itemIsPlayed,itemPlayedCount,item_matches_played_days_filter,item_matches_created_days_filter,item_matches_played_count_filter,item_matches_created_played_count_filter=get_playedCreatedDays_playedCreatedCounts(the_dict,mediaItemAdditionalInfo,itemsExtraDictionary[subUserId][itemId]['PlayedDays'],itemsExtraDictionary[subUserId][itemId]['CreatedDays'],itemsExtraDictionary[subUserId][itemId]['CutOffDatePlayed'],itemsExtraDictionary[subUserId][itemId]['CutOffDateCreated'],itemsExtraDictionary[subUserId][itemId]['PlayedCountComparison'],itemsExtraDictionary[subUserId][itemId]['PlayedCount'],itemsExtraDictionary[subUserId][itemId]['CreatedPlayedCountComparison'],itemsExtraDictionary[subUserId][itemId]['CreatedPlayedCount'])
                            #if (not (item_matches_played_days_filter == None)):
                                #itemsExtraDictionary[subUserId][itemId]['IsMeetingPlayedFilter']=(item_matches_played_days_filter and item_matches_played_count_filter)
                            #else:
                                #itemsExtraDictionary[subUserId][itemId]['IsMeetingPlayedFilter']=None
                            itemsExtraDictionary[subUserId][itemId]['itemIsPlayed']=itemIsPlayed
                            itemsExtraDictionary[subUserId][itemId]['itemPlayedCount']=itemPlayedCount
                            itemsExtraDictionary[subUserId][itemId]['item_matches_played_days_filter']=item_matches_played_days_filter #meeting played X days ago?
                            itemsExtraDictionary[subUserId][itemId]['item_matches_created_days_filter']=item_matches_created_days_filter #meeting created X days ago?
                            itemsExtraDictionary[subUserId][itemId]['item_matches_played_count_filter']=item_matches_played_count_filter #played X number of times?
                            itemsExtraDictionary[subUserId][itemId]['item_matches_created_played_count_filter']=item_matches_created_played_count_filter #created-played X number of times?
                            itemsExtraDictionary[subUserId][itemId]['IsMeetingPlayedFilter']=(item_matches_played_days_filter and item_matches_played_count_filter) #meeting complete played_filter_*?
                            itemsExtraDictionary[subUserId][itemId]['IsMeetingCreatedPlayedFilter']=(item_matches_created_days_filter and item_matches_created_played_count_filter) #meeting complete created_filter_*?
                            if (the_dict['DEBUG']):
                                appendTo_DEBUG_log("\itemIsPlayed: " + str(itemsExtraDictionary[subUserId][itemId]['itemIsPlayed']),3,the_dict)
                                appendTo_DEBUG_log("\itemPlayedCount: " + str(itemsExtraDictionary[subUserId][itemId]['itemPlayedCount']),3,the_dict)
                                appendTo_DEBUG_log("\item_matches_played_days_filter: " + str(itemsExtraDictionary[subUserId][itemId]['item_matches_played_days_filter']),3,the_dict)
                                appendTo_DEBUG_log("\item_matches_created_days_filter: " + str(itemsExtraDictionary[subUserId][itemId]['item_matches_created_days_filter']),3,the_dict)
                                appendTo_DEBUG_log("\item_matches_played_count_filter: " + str(itemsExtraDictionary[subUserId][itemId]['item_matches_played_count_filter']),3,the_dict)
                                appendTo_DEBUG_log("\item_matches_created_played_count_filter: " + str(itemsExtraDictionary[subUserId][itemId]['item_matches_created_played_count_filter']),3,the_dict)
                                appendTo_DEBUG_log("\IsMeetingPlayedFilter: " + str(itemsExtraDictionary[subUserId][itemId]['IsMeetingPlayedFilter']),3,the_dict)
                                appendTo_DEBUG_log("\IsMeetingCreatedPlayedFilter: " + str(itemsExtraDictionary[subUserId][itemId]['IsMeetingCreatedPlayedFilter']),3,the_dict)

    return itemsDictionary,itemsExtraDictionary