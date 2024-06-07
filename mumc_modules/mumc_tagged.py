import urllib.parse as urlparse
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_played_created import get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue
from mumc_modules.mumc_url import api_query_handler,build_request_message
from mumc_modules.mumc_compare_items import get_isItemMatching,does_index_exist,keys_exist
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo,get_STUDIO_itemInfo
from mumc_modules.mumc_output import appendTo_DEBUG_log


def list_to_urlparsed_string(the_list):
    tag_string=''
    for xltag in the_list:
        if (tag_string == ''):
            tag_string=str(xltag)
        else:
            tag_string+='|' + str(xltag)

    return urlparse.quote(tag_string)


def get_isItemTagged(usertags,tagged_items,item,the_dict):
    itemIsTagged=False

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    #Emby and jellyfin store tags differently
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        #Check if media item is tagged
        if ((not (usertags == '')) and ('TagItems' in item)):
            #Check if media item is tagged
            taglist=set()
            #Loop thru tags; store them for comparison to the media item
            for tagpos in range(len(item['TagItems'])):
                taglist.add(item['TagItems'][tagpos]['Name'])
            #Check if any of the media items tags match the tags in the config file
            itemIsTagged,itemTaggedValue=get_isItemMatching(usertags,taglist,the_dict)
            #Save media item's tags state
            if (itemIsTagged):
                tagged_items.append(item['Id'])
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('\nEmby tagged item with Id ' + str(item['Id']) + ' has tag named: ' + str(itemTaggedValue),2,the_dict)
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
            itemIsTagged,itemTaggedValue=get_isItemMatching(usertags,taglist,the_dict)
            #Save media item's usertags state
            if (itemIsTagged):
                tagged_items.append(item['Id'])
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log('\nJellyfin tagged item with Id ' + str(item['Id']) + ' has tag named: ' + str(itemTaggedValue),2,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\nIs Media Item ' + str(item['Id']) + ' Tagged: ' + str(itemIsTagged),2,the_dict)

    #parenthesis intentionally omitted to return tagged_items as a set
    return itemIsTagged,tagged_items


#Get children of tagged parents
def getChildren_taggedMediaItems(suffix_str,user_info,var_dict,the_dict):

    data_dict={}
    data_Tagged=var_dict['data_' + suffix_str]
    user_tags=var_dict['blacktags']
    data_dict['APIDebugMsg_']='Find_' + var_dict['APIDebugMsg_Child_Of_' + suffix_str]
    server_url=the_dict['admin_settings']['server']['url']
    #auth_key=the_dict['admin_settings']['server']['auth_key']
    child_dict={}
    child_list=[]
    child_itemId_isTagged=[]
    data_dict['StartIndex_']=0

    if (user_tags):
        insert_tagName=user_tags[0]
    else:
        insert_tagName=''

    #Loop thru items returned as tagged
    for data in data_Tagged['Items']:

        #Verify media item is a parent (not a child like an episode, movie, or audio)
        if ((data['IsFolder'] == True) or (data['Type'] == 'Book')):

            user_processed_itemsId=set()

            #Initialize api_query_handler() variables for child media items
            data_dict['StartIndex_']=0
            data_dict['TotalItems_']=1
            data_dict['QueryLimit_']=1
            data_dict['QueriesRemaining_']=True

            if not (data['Id'] == ''):
                #Build query for child media items; check is not Movie, Episode, or Audio
                if not ((data['Type'] == 'Movie') and (data['Type'] == 'Episode') and (data['Type'] == 'Audio')):
                    #include all item types; filter applied in first API calls for each media type in get_mediaItems()
                    IncludeItemTypes=''
                    FieldsState='Id,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,UserData'
                    if (isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
                        SortBy='SeriesSortName'
                    else:
                        SortBy='SeriesName'
                    SortBy=SortBy + ',AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                    SortOrder='Ascending'
                    Recursive='True'
                    EnableImages='False'
                    CollapseBoxSetItems='False'
                    IsPlayedState=get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(the_dict,var_dict)

                    while (data_dict['QueriesRemaining_']):

                        if not (data['Id'] == ''):
                            #Built query for child media items
                            url=(server_url + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + data['Id'] + '&IncludeItemTypes=' + IncludeItemTypes +
                            '&StartIndex=' + str(data_dict['StartIndex_']) + '&Limit=' + str(data_dict['QueryLimit_']) + '&IsPlayed=' + IsPlayedState +
                            '&Fields=' + FieldsState + '&Recursive=' + Recursive + '&SortBy=' + SortBy + '&SortOrder=' + SortOrder +
                            '&CollapseBoxSet' + CollapseBoxSetItems + '&EnableImages=' + EnableImages)

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

                        #Loop thru the returned child items
                        for child_item in data_dict['data_']['Items']:
                            child_itemIsTagged=False
                            #Check if child item has already been processed
                            if not (child_item['Id'] in user_processed_itemsId):
                                if (does_index_exist(data['TagItems'],0,the_dict)) and (keys_exist(data['TagItems'][0],'Name')):
                                    insert_tagName=data['TagItems'][0]['Name']
                                    #Emby and jellyfin store tags differently
                                    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
                                        #Does 'TagItems' exist
                                        if not ('TagItems' in child_item):
                                            #if it does not; add desired tag to metadata
                                            #child_item['TagItems']=[{'Name':insert_tagName,'Id':insert_tagId}]
                                            child_item['TagItems']=[{'Name':data['TagItems'][0]['Name'],'Id':data['TagItems'][0]['Id']}]
                                        #Does 'TagItems'[] exist
                                        elif not (does_index_exist(child_item['TagItems'],0,the_dict)):
                                            #if it does not; add desired tag to metadata
                                            #child_item['TagItems']=[{'Name':insert_tagName,'Id':insert_tagId}]
                                            child_item['TagItems']=[{'Name':data['TagItems'][0]['Name'],'Id':data['TagItems'][0]['Id']}]
                                        else: #Tag already exists
                                            #Determine if the existing tags are any of the tags we are looking for
                                            child_itemIsTagged,child_itemId_isTagged=get_isItemTagged(user_tags,child_itemId_isTagged,child_item,the_dict)
                                            #If existing tags are not ones we are lookign for then insert desired tag
                                            if not (child_itemIsTagged):
                                                #child_item['TagItems'].append({'Name':insert_tagName,'Id':insert_tagId})
                                                child_item['TagItems']=[{'Name':data['TagItems'][0]['Name'],'Id':data['TagItems'][0]['Id']}]
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

    child_dict['Items']=child_list
    child_dict['TotalRecordCount']=len(child_list)
    child_dict['StartIndex']=data_dict['StartIndex_']

    #Return child dictionary
    return child_dict


#determine if movie or library are tagged
def get_isMOVIE_Tagged(the_dict,item,user_info,usertags):

    tagged_items=[]

    #define empty dictionary for tagged Movies
    istag_MOVIE={'movie':{},'movielibrary':{}}

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Movie #######################################################################################

        if ('Id' in item):
            istag_MOVIE['movie'][item['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,item,the_dict)

### End Movie ###################################################################################

### Movie Library #######################################################################################

        if ('ParentId' in item):
            movielibrary_item_info = get_ADDITIONAL_itemInfo(user_info,item['ParentId'],'movie_library_info',the_dict)
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
def get_isEPISODE_Tagged(the_dict,item,user_info,usertags):

    tagged_items=[]

    #define empty dictionary for tagorited TV Series, Seasons, Episodes, and Channels/Networks
    istag_EPISODE={'episode':{},'season':{},'series':{},'tvlibrary':{},'seriesstudionetwork':{}}

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Episode #######################################################################################

        if ('Id' in item):
            istag_EPISODE['episode'][item['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,item,the_dict)

### End Episode ###################################################################################

### Season ########################################################################################

        if ('SeasonId' in item):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,item['SeasonId'],'season_info',the_dict)
        elif ('ParentId' in item):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,item['ParentId'],'season_info',the_dict)
        else:
            season_item_info=None

        if (not (season_item_info == None)):
            istag_EPISODE['season'][season_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,season_item_info,the_dict)

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
                istag_EPISODE['series'][series_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,series_item_info,the_dict)

### End Series ####################################################################################

### TV Library ########################################################################################

                if ('ParentId' in series_item_info):
                    tvlibrary_item_info = get_ADDITIONAL_itemInfo(user_info,series_item_info['ParentId'],'tv_library_info',the_dict)
                else:
                    tvlibrary_item_info=None

                if (not (tvlibrary_item_info == None)):
                    istag_EPISODE['tvlibrary'][tvlibrary_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,tvlibrary_item_info,the_dict)

### End TV Library ####################################################################################

### Studio Network #######################################################################################

                if (('Studios' in series_item_info) and does_index_exist(series_item_info['Studios'],0,the_dict)):
                    #Get studio network's item info
                    tvstudionetwork_item_info = get_ADDITIONAL_itemInfo(user_info,series_item_info['Studios'][0]['Id'],'studio_network_info',the_dict)
                elif ('SeriesStudio' in series_item_info):
                    #Get series studio network's item info
                    tvstudionetwork_item_info = get_STUDIO_itemInfo(series_item_info['SeriesStudio'],the_dict,the_dict)
                else:
                    tvstudionetwork_item_info=None

                if (not (tvstudionetwork_item_info == None)):
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
def get_isAUDIO_Tagged(the_dict,item,user_info,usertags):

    tagged_items=[]

    #define empty dictionary for tagorited Tracks, Albums, Artists
    istag_AUDIO={'track':{},'album':{},'audiolibrary':{}}

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n",1,the_dict)

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Track #########################################################################################

        if ('Id' in item):
            istag_AUDIO['track'][item['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,item,the_dict)

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
            istag_AUDIO['album'][album_item_info['Id']],tagged_items=get_isItemTagged(usertags,tagged_items,album_item_info,the_dict)

### End Album/Book #####################################################################################

### Library ########################################################################################

            #Library
            if ('ParentId' in album_item_info):
                audiolibrary_item_info = get_ADDITIONAL_itemInfo(user_info,album_item_info['ParentId'],'library_info',the_dict)
            else:
                audiolibrary_item_info=None

            if (not (audiolibrary_item_info == None)):
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
def get_isAUDIOBOOK_Tagged(the_dict,item,user_info,usertags):
    return get_isAUDIO_Tagged(the_dict,item,user_info,usertags)