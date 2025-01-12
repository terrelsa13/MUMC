import urllib.parse as urlparse
from mumc_modules.mumc_url import requestURL,build_emby_jellyfin_request_message,build_radarr_request_message,build_sonarr_request_message


#get additional item info needed to make a decision about a media item
def get_ADDITIONAL_itemInfo(user_info,itemId,lookupTopic,the_dict):
    #Get additonal item information

    url=the_dict['admin_settings']['server']['url'] + '/Users/' + user_info['user_id']  + '/Items/' + str(itemId) + '?enableImages=False&enableUserData=True&Fields=ParentId,Genres,Tags,RecursiveItemCount,ChildCount,Type,ProviderIds'

    req=build_emby_jellyfin_request_message(url,the_dict)

    itemInfo=requestURL(req, the_dict['DEBUG'], lookupTopic + '_for_' + str(itemId), the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    return itemInfo


#get additional channel/network/studio info needed to determine if item is favorite
def get_STUDIO_itemInfo(studioNetworkName,the_dict):
    #Encode studio name
    studio_network=urlparse.quote(studioNetworkName)

    #Get studio item information
    url=the_dict['admin_settings']['server']['url'] + '/Studios/' + studio_network + '&enableImages=False&enableUserData=True'
    
    req=build_emby_jellyfin_request_message(url,the_dict)

    itemInfo=requestURL(req, the_dict['DEBUG'], 'studio_network_info_for_' + str(studioNetworkName), the_dict['api_query_attempts'], the_dict)

    return itemInfo


#get series item info from episode
def get_SERIES_itemInfo(episode,user_info,the_dict):

    series_item_info={}

    if (('mumc' in episode) and ('lib_id' in episode['mumc']) and (episode['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Series ########################################################################################

        if ('SeriesId' in episode):
            series_item_info = get_ADDITIONAL_itemInfo(user_info,episode['SeriesId'],'series_info',the_dict)

        elif ('SeasonId' in episode):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,episode['SeasonId'],'season_info',the_dict)

            if ('SeriesId' in season_item_info):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,season_item_info['SeriesId'],'series_info',the_dict)

            elif ('ParentId' in season_item_info):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,season_item_info['ParentId'],'series_info',the_dict)

        elif ('ParentId' in episode):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,episode['ParentId'],'season_info',the_dict)

            if ('SeriesId' in season_item_info):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,season_item_info['SeriesId'],'series_info',the_dict)

            elif ('ParentId' in season_item_info):
                series_item_info = get_ADDITIONAL_itemInfo(user_info,season_item_info['ParentId'],'series_info',the_dict)

### End Series ####################################################################################

    return series_item_info


#get movie item info from radarr
def get_MOVIE_radarrInfo(radarrTMdbId,the_dict):

    url=the_dict['admin_settings']['media_managers']['radarr']['url'] + '/api/v3/movie?tmdbId=' + str(radarrTMdbId)

    req=build_radarr_request_message(url,the_dict)

    itemInfo=requestURL(req, the_dict['DEBUG'], 'get_info_for_movie_with_tmdbid: ' + str(radarrTMdbId), the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    return itemInfo


#put moive item info to radarr
def put_MOVIE_radarrInfo(radarrTMdbId,movieData,the_dict):

    url=the_dict['admin_settings']['media_managers']['radarr']['url'] + '/api/v3/movie?tmdbId=' + str(radarrTMdbId)

    req=build_radarr_request_message(url,the_dict,data=movieData,method='PUT')

    itemInfo=requestURL(req, the_dict['DEBUG'], 'set_info_for_movie_with_tmdbid: ' + str(radarrTMdbId), the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    return itemInfo


#remove movie from radarr
def remove_MOVIE_radarr(radarrId,the_dict):

    url=the_dict['admin_settings']['media_managers']['radarr']['url'] + '/api/v3/movie/' + str(radarrId) + '?deleteFiles=false&addImportExclusion=false'

    req=build_radarr_request_message(url,the_dict,accept='*/*',contentType='*/*',method='DELETE')

    itemInfo=requestURL(req, the_dict['DEBUG'], 'remove_movie_with_radarrId: ' + str(radarrId) + ' from_Radarr', the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    return itemInfo


#get series item info from sonarr
def get_SERIES_sonarrInfo(seriesTVdBId,postproc_dict,the_dict):

    url=postproc_dict['admin_settings']['media_managers']['sonarr']['url'] + '/api/v3/series?tvdbId=' + str(seriesTVdBId) + '&includeSeasonImages=false'

    req=build_sonarr_request_message(url,the_dict)

    itemInfo=requestURL(req, the_dict['DEBUG'], 'get_sonarr_series_info_for_' + str(seriesTVdBId), the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    return itemInfo


#post series item info to sonarr
def put_SERIES_sonarrInfo(sonarrTVdbId,seriesData,the_dict):

    url=the_dict['admin_settings']['media_managers']['sonarr']['url'] + '/api/v3/series'

    req=build_sonarr_request_message(url,the_dict,data=seriesData,method='PUT')

    itemInfo=requestURL(req, the_dict['DEBUG'], 'set_info_for_series_with_tvdbId: ' + str(sonarrTVdbId), the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    return itemInfo


#remove series from sonar
def remove_SERIES_sonarr(sonarrId,the_dict):

    url=the_dict['admin_settings']['media_managers']['sonarr']['url'] + '/api/v3/series/' + str(sonarrId) + '?deleteFiles=false&addImportExclusion=false'

    req=build_sonarr_request_message(url,the_dict,accept='*/*',contentType='*/*',method='DELETE')

    itemInfo=requestURL(req, the_dict['DEBUG'], 'remove_series_with_sonarrId: ' + str(sonarrId) + ' from_Sonarr', the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    return itemInfo


#set sonarr episode monitor status
def update_EPISODE_sonarrMonitorStatus(sonarrItemId,the_dict,monitored_status=False):

    monitorData_dict={}
    monitorData_dict['episodeIds']=[int(sonarrItemId)]
    monitorData_dict['monitored']=monitored_status

    url=the_dict['admin_settings']['media_managers']['sonarr']['url'] + '/api/v3/episode/monitor?includeImages=false'

    req=build_sonarr_request_message(url,the_dict,accept='*/*',data=monitorData_dict,method='PUT')

    itemInfo=requestURL(req, the_dict['DEBUG'], 'set_episodeId_' + str(monitorData_dict['episodeIds']) + '_monitor_status_to_' + str(monitorData_dict['monitored']), the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    return itemInfo