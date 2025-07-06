import urllib.parse as urlparse
from mumc_modules.mumc_url import requestURL,build_emby_jellyfin_request_message,build_radarr_request_message,build_sonarr_request_message


#get additional item info needed to make a decision about a media item
def get_ADDITIONAL_itemInfo(user_info,itemId,lookupTopic,the_dict):
    #Get additonal item information

    url=the_dict['admin_settings']['server']['url'] + '/Users/' + user_info['user_id']  + '/Items/' + str(itemId) + '?enableImages=False&enableUserData=True&Fields=ParentId,Genres,Tags,RecursiveItemCount,ChildCount,Type,ProviderIds'

    req=build_emby_jellyfin_request_message(url,the_dict)

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], lookupTopic + '_for_' + str(itemId), the_dict['admin_settings']['api_controls']['attempts'])

    return itemInfo


#get additional channel/network/studio info needed to determine if item is favorite
def get_STUDIO_itemInfo(studioNetworkName,the_dict):
    #Encode studio name
    studio_network=urlparse.quote(studioNetworkName)

    #Get studio item information
    url=the_dict['admin_settings']['server']['url'] + '/Studios/' + studio_network + '&enableImages=False&enableUserData=True'
    
    req=build_emby_jellyfin_request_message(url,the_dict)

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'studio_network_info_for_' + str(studioNetworkName), the_dict['api_query_attempts'])

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


#lookup movie item info from radarr using IMDB Id
def lookup_MOVIE_radarrInfo_IMdBId(radarrIMdbId,arrInfo,the_dict):

    url=arrInfo['url'] + '/api/v3/movie/lookup/imdb?imdbId=' + str(radarrIMdbId)

    req=build_radarr_request_message(url=url,arrInfo=arrInfo)

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'lookup_info_for_movie_with_tmdbId: ' + str(radarrIMdbId), the_dict['admin_settings']['api_controls']['attempts'], False)

    return itemInfo


#get movie item info from radarr using TMDB Id
def get_MOVIE_radarrInfo_TMdBId(radarrTMdbId,arrInfo,the_dict):

    url=arrInfo['url'] + '/api/v3/movie?tmdbId=' + str(radarrTMdbId)

    req=build_radarr_request_message(url=url,arrInfo=arrInfo)

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'get_info_for_movie_with_tmdbId: ' + str(radarrTMdbId), the_dict['admin_settings']['api_controls']['attempts'], False)

    return itemInfo


#put movie item info into radarr using Radarr Id
def put_MOVIE_radarrInfo_radarrId(radarrId,movieData,arrInfo,the_dict):

    url=arrInfo['url'] + '/api/v3/movie/' + str(radarrId)

    req=build_radarr_request_message(url=url,arrInfo=arrInfo,data=movieData,method='PUT')

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'set_info_for_movie_with_radarrId: ' + str(radarrId), the_dict['admin_settings']['api_controls']['attempts'])

    return itemInfo


##put movie item info into radarr using TMDB Id
#def put_MOVIE_radarrInfo_TMdBId(radarrTMdbId,movieData,arrInfo,the_dict):

    #url=arrInfo['url'] + '/api/v3/movie?tmdbId=' + str(radarrTMdbId)

    #req=build_radarr_request_message(url=url,arrInfo=arrInfo,data=movieData,method='PUT')

    #itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'set_info_for_movie_with_tmdbId: ' + str(radarrTMdbId), the_dict['admin_settings']['api_controls']['attempts'])

    #return itemInfo


#remove movie from radarr using Radarr Id
def remove_MOVIE_radarr_radarrId(radarrId,arrInfo,the_dict):

    url=arrInfo['url'] + '/api/v3/movie/' + str(radarrId) + '?deleteFiles=false&addImportExclusion=false'

    req=build_radarr_request_message(url=url,arrInfo=arrInfo,accept='*/*',contentType='*/*',method='DELETE')

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'remove_movie_with_radarrId: ' + str(radarrId) + ' from_Radarr', the_dict['admin_settings']['api_controls']['attempts'], False)

    return itemInfo


#get series item info from IMDB Id
def lookup_SERIES_sonarrInfo_IMdbId(seriesIMdBId,arrInfo,the_dict):

    url=arrInfo['url'] + '/api/v3/series/lookup?term=imdb:' + str(seriesIMdBId)

    req=build_sonarr_request_message(url=url,arrInfo=arrInfo)

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'lookup_info_for_series_with_tmdbid' + str(seriesIMdBId), the_dict['admin_settings']['api_controls']['attempts'],False)

    return itemInfo


#get series item info from TVDB Id
def get_SERIES_sonarrInfo_TVdbId(seriesTVdBId,arrInfo,the_dict):

    url=arrInfo['url'] + '/api/v3/series?tvdbId=' + str(seriesTVdBId)

    req=build_sonarr_request_message(url=url,arrInfo=arrInfo)

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'get_info_for_movie_with_tvdbid' + str(seriesTVdBId), the_dict['admin_settings']['api_controls']['attempts'],False)

    return itemInfo


#get series item info from Sonarr Id
def get_SERIES_sonarrInfo_sonarrId(sonarrId,arrInfo,the_dict):

    url=arrInfo['url'] + '/api/v3/series/' + str(sonarrId)

    req=build_sonarr_request_message(url=url,arrInfo=arrInfo)

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'get_info_for_movie_with_sonarrid' + str(sonarrId), the_dict['admin_settings']['api_controls']['attempts'],False)

    return itemInfo


#post series item info to sonarr
def put_SERIES_sonarrInfo_sonarrId(sonarrId,arrInfo,seriesData,the_dict):

    url=arrInfo['url'] + '/api/v3/series'

    req=build_sonarr_request_message(url=url,arrInfo=arrInfo,data=seriesData,method='PUT')

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'set_info_for_series_with_sonarrId: ' + str(sonarrId), the_dict['admin_settings']['api_controls']['attempts'])

    return itemInfo


#remove series from sonar
def remove_SERIES_sonarr(sonarrId,arrInfo,the_dict):

    url=arrInfo['url'] + '/api/v3/series/' + str(sonarrId) + '?deleteFiles=false&addImportExclusion=false'

    req=build_sonarr_request_message(url=url,arrInfo=arrInfo,accept='*/*',contentType='*/*',method='DELETE')

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'remove_series_with_sonarrId: ' + str(sonarrId) + ' from_Sonarr', the_dict['admin_settings']['api_controls']['attempts'],False)

    return itemInfo


#set sonarr episode monitor status
def put_EPISODE_sonarrInfo_sonarrId(sonarrItemId,arrInfo,the_dict,monitored_status=False):

    monitorData_dict={}
    monitorData_dict['episodeIds']=[int(sonarrItemId)]
    monitorData_dict['monitored']=monitored_status

    url=arrInfo['url'] + '/api/v3/episode/monitor?includeImages=false'

    req=build_sonarr_request_message(url=url,arrInfo=arrInfo,accept='*/*',data=monitorData_dict,method='PUT')

    itemInfo=requestURL(the_dict, req, the_dict['DEBUG'], 'set_episodeId_' + str(monitorData_dict['episodeIds']) + '_monitor_status_to_' + str(monitorData_dict['monitored']), the_dict['admin_settings']['api_controls']['attempts'])

    return itemInfo