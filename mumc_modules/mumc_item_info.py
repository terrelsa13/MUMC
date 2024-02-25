import urllib.parse as urlparse
from mumc_modules.mumc_url import requestURL,build_request_message


#get additional item info needed to make a decision about a media item
def get_ADDITIONAL_itemInfo(user_info,itemId,lookupTopic,the_dict):
    #Get additonal item information

    url=the_dict['admin_settings']['server']['url'] + '/Users/' + user_info['user_id']  + '/Items/' + str(itemId) + '?enableImages=False&enableUserData=True&Fields=ParentId,Genres,Tags,RecursiveItemCount,ChildCount,Type'

    req=build_request_message(url,the_dict)

    itemInfo=requestURL(req, the_dict['DEBUG'], lookupTopic + '_for_' + str(itemId), the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    return itemInfo


#get additional channel/network/studio info needed to determine if item is favorite
def get_STUDIO_itemInfo(studioNetworkName,the_dict):
    #Encode studio name
    studio_network=urlparse.quote(studioNetworkName)

    #Get studio item information
    url=the_dict['admin_settings']['server']['url'] + '/Studios/' + studio_network + '&enableImages=False&enableUserData=True'
    
    req=build_request_message(url,the_dict)

    itemInfo=requestURL(req, the_dict['DEBUG'], 'studio_network_info_for_' + str(studioNetworkName), the_dict['api_query_attempts'], the_dict)

    return itemInfo


#get series item info from episode
def get_SERIES_itemInfo(episode,user_info,the_dict):

    series_item_info={}

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