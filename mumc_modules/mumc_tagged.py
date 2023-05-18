#!/usr/bin/env python3
import uuid
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_played_created import get_isPlayedCreated_FilterValue
from mumc_modules.mumc_url import api_query_handler
from mumc_modules.mumc_compare_items import get_isItemMatching_doesItemStartWith,does_index_exist
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo,get_STUDIO_itemInfo
from mumc_modules.mumc_output import appendTo_DEBUG_log


def get_isItemTagged(usertags,tagged_items,item,the_dict):
    itemIsTagged=False

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    #Emby and jellyfin store tags differently
    if (isEmbyServer(the_dict['server_brand'])):
        #Check if media item is tagged
        if ((not (usertags == '')) and ('TagItems' in item)):
            #Check if media item is tagged
            taglist=set()
            #Loop thru tags; store them for comparison to the media item
            for tagpos in range(len(item['TagItems'])):
                taglist.add(item['TagItems'][tagpos]['Name'])
            #Check if any of the media items tags match the tags in the config file
            itemIsTagged,itemTaggedValue=get_isItemMatching_doesItemStartWith(usertags, ','.join(map(str, taglist)),the_dict)
            #Save media item's tags state
            if (itemIsTagged):
                tagged_items.append(item['Id'])
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('\nItem with Id ' + str(item['Id']) + 'has tag named ' + str(itemTaggedValue),2,the_dict)
    #Emby and jellyfin store tags differently
    else: #(isJellyfinServer(the_dict['server_brand']))
        #Jellyfin tags
        #Check if media item is tagged
        if ((not (usertags == '')) and ('Tags' in item)):
            #Check if media item is tagged
            taglist=set()
            #Loop thru tags; store them for comparison to the media item
            for tagpos in range(len(item['Tags'])):
                taglist.add(item['Tags'][tagpos])
            #Check if any of the media items tags match the tags in the config file
            itemIsTagged,itemTaggedValue=get_isItemMatching_doesItemStartWith(usertags, ','.join(map(str, taglist)),the_dict)
            #Save media item's usertags state
            if (itemIsTagged):
                tagged_items.append(item['Id'])
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('\nItem with Id ' + str(item['Id']) + 'has tag named: ' + str(itemTaggedValue),2,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\nIs Media Item ' + str(item['Id']) + ' Tagged: ' + str(itemIsTagged),2,the_dict)

    #parenthesis intentionally omitted to return tagged_items as a set
    return itemIsTagged,tagged_items


#Get children of tagged parents
def getChildren_taggedMediaItems(user_key,data_Tagged,user_tags,filter_played_count_comparison,filter_played_count,filter_created_played_count_comparison,filter_created_played_count,tag_Type,played_days,created_days,the_dict):
    server_url=the_dict['server_url']
    auth_key=the_dict['auth_key']
    #parent_tag=[]
    child_list=[]
    child_itemId_isTagged=[]
    StartIndex=0
    insert_tagName=user_tags.split(',')[0]
    insert_tagId=uuid.uuid4().int

    #Loop thru items returned as tagged
    for data in data_Tagged['Items']:

        #Verify media item is a parent (not a child like an episode, movie, or audio)
        if ((data['IsFolder'] == True) or (data['Type'] == 'Book')):

            user_processed_itemsId=set()

            #Initialize api_query_handler() variables for child media items
            StartIndex=0
            TotalItems=1
            QueryLimit=1
            QueriesRemaining=True
            APIDebugMsg='find_children_' + tag_Type + '_media_items'

            if not (data['Id'] == ''):
                #Build query for child media items; check is not Movie, Episode, or Audio
                if not ((data['Type'] == 'Movie') and (data['Type'] == 'Episode') and (data['Type'] == 'Audio')):
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
                            #Built query for child media items
                            apiQuery=(server_url + '/Users/' + user_key  + '/Items?ParentID=' + data['Id'] + '&IncludeItemTypes=' + IncludeItemTypes +
                            '&StartIndex=' + str(StartIndex) + '&Limit=' + str(QueryLimit) + '&IsPlayed=' + IsPlayedState +
                            '&Fields=' + FieldsState + '&Recursive=' + Recursive + '&SortBy=' + SortBy + '&SortOrder=' + SortOrder +
                            '&CollapseBoxSet' + CollapseBoxSetItems + '&EnableImages=' + EnableImages + '&api_key=' + auth_key)

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
                            child_itemIsTagged=False
                            #Check if child item has already been processed
                            if not (child_item['Id'] in user_processed_itemsId):
                                #Emby and jellyfin store tags differently
                                if (isEmbyServer(the_dict['server_brand'])):
                                    #Does 'TagItems' exist
                                    if not ('TagItems' in child_item):
                                        #if it does not; add desired tag to metadata
                                        child_item['TagItems']=[{'Name':insert_tagName,'Id':insert_tagId}]
                                    #Does 'TagItems'[] exist
                                    elif not (does_index_exist(child_item['TagItems'],0,the_dict)):
                                        #if it does not; add desired tag to metadata
                                        child_item['TagItems']=[{'Name':insert_tagName,'Id':insert_tagId}]
                                    else: #Tag already exists
                                        #Determine if the existing tags are any of the tags we are looking for
                                        child_itemIsTagged,child_itemId_isTagged=get_isItemTagged(user_tags,child_itemId_isTagged,child_item,the_dict)
                                        #If existing tags are not ones we are lookign for then insert desired tag
                                        if not (child_itemIsTagged):
                                            child_item['TagItems'].append({'Name':insert_tagName,'Id':insert_tagId})
                                #Emby and jellyfin store tags differently
                                else: #(isJellyfinServer())
                                    #Does 'TagItems' exist
                                    if not ('Tag' in child_item):
                                        #if it does not; add desired tag to metadata
                                        child_item['Tags']=[insert_tagName]
                                    #Does 'Tags'[] exist
                                    elif (child_item['Tags'] == []):
                                        #if it does not; add desired tag to metadata
                                        child_item['Tags'].append(insert_tagName)
                                    else:
                                        #Determine if the existing tags are any of the tags we are looking for
                                        child_itemIsTagged,child_itemId_isTagged=get_isItemTagged(user_tags,child_itemId_isTagged,child_item,the_dict)
                                        #If existing tags are not ones we are looking for then insert desired tag
                                        if not (child_itemIsTagged):
                                            child_item['Tags'].append(insert_tagName)
                                #keep track of tagged child items
                                child_list.append(child_item)
                                user_processed_itemsId.add(child_item['Id'])

                                if (the_dict['DEBUG']):
                                    appendTo_DEBUG_log('\nChild item with Id: ' + str(child_item['Id']) + ' tagged with tag named: ' + str(insert_tagName),2,the_dict)

    #Return dictionary of child items along with TotalRecordCount
    return({'Items':child_list,'TotalRecordCount':len(child_list),'StartIndex':StartIndex})


#determine if movie or library are tagged
def get_isMOVIE_Tagged(the_dict,item,user_key,usertags):

    tagged_items=[]

    #define empty dictionary for tagged Movies
    istag_MOVIE={'movie':{},'movielibrary':{}}

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

### Movie #######################################################################################

    if ('Id' in item):
        istag_MOVIE['movie'][item['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,item,the_dict)

### End Movie ###################################################################################

### Movie Library #######################################################################################

    if ('ParentId' in item):
        movielibrary_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'movie_library_info',the_dict)
        istag_MOVIE['movielibrary'][movielibrary_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,movielibrary_item_info,the_dict)

### End Movie Library ###################################################################################

    for istagkey in istag_MOVIE:
        for istagID in istag_MOVIE[istagkey]:
            if (istag_MOVIE[istagkey][istagID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nMovie " + str(item['Id']) + " is tagged.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nMovie " + str(item['Id']) + " is NOT tagged.",2,the_dict)

    return(False)


#determine if episode, season, series, or studio-network are tagged
def get_isEPISODE_Tagged(the_dict,item,user_key,usertags):

    tagged_items=[]

    #define empty dictionary for tagorited TV Series, Seasons, Episodes, and Channels/Networks
    istag_EPISODE={'episode':{},'season':{},'series':{},'tvlibrary':{},'seriesstudionetwork':{}}

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

### Episode #######################################################################################

    if ('Id' in item):
        istag_EPISODE['episode'][item['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,item,the_dict)

### End Episode ###################################################################################

### Season ########################################################################################

    if ('SeasonId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeasonId'],'season_info',the_dict)
    elif ('ParentId' in item):
        season_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'season_info',the_dict)

    istag_EPISODE['season'][season_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,season_item_info,the_dict)

### End Season ####################################################################################

### Series ########################################################################################

    if ('SeriesId' in item):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,item['SeriesId'],'series_info',the_dict)
    elif ('SeriesId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['SeriesId'],'series_info',the_dict)
    elif ('ParentId' in season_item_info):
        series_item_info = get_ADDITIONAL_itemInfo(user_key,season_item_info['ParentId'],'series_info',the_dict)

    istag_EPISODE['series'][series_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,series_item_info,the_dict)

### End Series ####################################################################################

### TV Library ########################################################################################

    if ('ParentId' in series_item_info):
        tvlibrary_item_info = get_ADDITIONAL_itemInfo(user_key,series_item_info['ParentId'],'tv_library_info',the_dict)

    istag_EPISODE['tvlibrary'][tvlibrary_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,tvlibrary_item_info,the_dict)

### End TV Library ####################################################################################

### Studio Network #######################################################################################

    if (('Studios' in series_item_info) and does_index_exist(series_item_info['Studios'],0,the_dict)):
        #Get studio network's item info
        tvstudionetwork_item_info = get_ADDITIONAL_itemInfo(user_key,series_item_info['Studios'][0]['Id'],'studio_network_info',the_dict)
    elif ('SeriesStudio' in series_item_info):
        #Get series studio network's item info
        tvstudionetwork_item_info = get_STUDIO_itemInfo(series_item_info['SeriesStudio'],the_dict,the_dict)

    istag_EPISODE['seriesstudionetwork'][tvstudionetwork_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,tvstudionetwork_item_info,the_dict)

### End Studio Network ###################################################################################

    for istagkey in istag_EPISODE:
        for istagID in istag_EPISODE[istagkey]:
            if (istag_EPISODE[istagkey][istagID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is tagged.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nEpisode " + str(item['Id']) + " is NOT tagged.",2,the_dict)

    return(False)

#determine if genres for music track, album, or music library are tagged
def get_isAUDIO_Tagged(the_dict,item,user_key,usertags):

    tagged_items=[]

    #define empty dictionary for tagorited Tracks, Albums, Artists
    istag_AUDIO={'track':{},'album':{},'audiolibrary':{}}

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

### Track #########################################################################################

    tagged_items=[]

    if ('Id' in item):
        istag_AUDIO['track'][item['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,item,the_dict)

### End Track #####################################################################################

### Album/Book #########################################################################################

    #Albums for music
    if ('ParentId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['ParentId'],'album_info',the_dict)
    elif ('AlbumId' in item):
        album_item_info = get_ADDITIONAL_itemInfo(user_key,item['AlbumId'],'album_info',the_dict)

    istag_AUDIO['album'][album_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,album_item_info,the_dict)

### End Album/Book #####################################################################################

### Library ########################################################################################

    #Library
    if ('ParentId' in album_item_info):
        audiolibrary_item_info = get_ADDITIONAL_itemInfo(user_key,album_item_info['ParentId'],'library_info',the_dict)

    istag_AUDIO['audiolibrary'][audiolibrary_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,audiolibrary_item_info,the_dict)

### End Library #####################################################################################

    for istagkey in istag_AUDIO:
        for istagID in istag_AUDIO[istagkey]:
            if (istag_AUDIO[istagkey][istagID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\nAudio/AudioBook " + str(item['Id']) + " is tagged.",2,the_dict)
                return(True)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nAudio/AudioBook " + str(item['Id']) + " is NOT tagged.",2,the_dict)

    return(False)


#determine if genres for audiobook track, book, or audio book library are tagged
def get_isAUDIOBOOK_Tagged(the_dict,item,user_key,usertags):
    return get_isAUDIO_Tagged(the_dict,item,user_key,usertags)