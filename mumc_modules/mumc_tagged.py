import urllib.parse as urlparse
from mumc_modules.mumc_server_type import isEmbyServer
from mumc_modules.mumc_played_created import get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue
from mumc_modules.mumc_url import api_query_handler,build_request_message
from mumc_modules.mumc_compare_items import get_isItemMatching,does_index_exist
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


def get_isItemTagged(usertags,matched_tags,item,the_dict):
    #itemIsTagged=False
    itemIsTagged={}
    itemIsTagged['any_match']=False
    itemIsTagged['all_match']=False
    itemIsTagged['match_state']=[]
    itemIsTagged['match_value']=[]

    #Emby and jellyfin store tags differently
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        tagData='TagItems'
    else:
        tagData='Tags'

    #Check if media item is tagged
    if ((not (usertags == '')) and (tagData in item)):
        #Check if media item is tagged
        tag_list=[]
        #Loop thru tags; store them for comparison to the media item
        if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
            for tagpos in range(len(item[tagData])):
                tag_list.append(item[tagData][tagpos]['Name'])
        else:
            for tagpos in range(len(item[tagData])):
                tag_list.append(item[tagData][tagpos])
        #Check if any of the media items tags match the tags in the config file

        #Check if any of the media items tags match the tags in the config file
        itemIsTagged=get_isItemMatching(usertags,tag_list,the_dict)

        #Save media item's tags state
        if (itemIsTagged['any_match']):
            #matched_tags.append(item['Id'])
            matched_tags.extend(match for match in itemIsTagged['match_value'] if (not (match == None)))
            matched_tags=list(set(matched_tags))

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log('\n\nTagged item with Id ' + str(item['Id']) + ' has tag named: ' + str(itemIsTagged['match_value']),2,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\nIs Media Item ' + str(item['Id']) + ' Tagged: ' + str(itemIsTagged['any_match']),2,the_dict)

    #parenthesis intentionally omitted to return matched_tags as a set
    return itemIsTagged['any_match'],matched_tags


#add tags to media_item
def removeTags_From_mediaItem(item,the_dict):

    #Emby and jellyfin store tags differently
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        tagData='TagItems'
    else:
        tagData='Tags'

    #Blank the list to remove existing tags
    item[tagData]=[]

    return item


#add tags to media_item
def addTags_To_mediaItem(matched_tags,child_item,the_dict):

    #Emby and jellyfin store tags differently
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        tagData='TagItems'
    else:
        tagData='Tags'

    #Check if media item is tagged
    if (not (tagData in child_item)):
        child_item[tagData]=[]

    #Emby and jellyfin store tags differently
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        for thisTag in matched_tags:
            thisTag_dict={'Name':thisTag}
            child_item[tagData].append(thisTag_dict)
    else:
        for thisTag in matched_tags:
            child_item[tagData].append(thisTag)

    #child_item[tagData]+=parent_item[tagData]
    #child_item[tagData].extend(parent_item[tagData])

    return child_item


def getList_Of_thisItemsTags(item,the_dict):

    #Emby and jellyfin store tags differently
    if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
        tagData='TagItems'
    else:
        tagData='Tags'

    matched_tags=[]

    for this_tag in item[tagData]:
        if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
            matched_tags.append(this_tag['Name'])
        else:
            matched_tags.append(this_tag)

    return matched_tags


#Get children of tagged parents
def getChildren_taggedMediaItems(suffix_str,user_info,var_dict,the_dict):

    data_dict={}
    data_Tagged=var_dict['data_' + suffix_str]
    data_dict['APIDebugMsg_']='Find_' + var_dict['APIDebugMsg_Child_Of_' + suffix_str]
    server_url=the_dict['admin_settings']['server']['url']
    child_dict={}
    data_dict['StartIndex_']=0
    data_dict['data_']={'Items':[]}

    if ('blacktagged' in suffix_str.casefold()):
        tagType='blacktags'
    elif ('whitetagged' in suffix_str.casefold()):
        tagType='whitetags'
    else:
        raise ValueError('Unknown tagging type; not blacktags and not whitetags.\n\tUnknown value is:' + str(tagType))

    #Loop thru items returned as tagged
    for data in data_Tagged['Items']:

        #Verify media item is a parent (not a child like an episode, movie, or audio)
        if ((data['IsFolder'] == True) or (data['Type'] == 'Book')):

            #Initialize api_query_handler() variables for child media items
            data_dict['StartIndex_']=0
            data_dict['TotalItems_']=1
            data_dict['QueryLimit_']=1
            data_dict['QueriesRemaining_']=True

            if (not (data['Id'] == '')):
                #Build query for child media items; SortOrdercheck is not Movie, Episode, or Audio
                if (not ((data['Type'].casefold() == 'movie') and (data['Type'].casefold() == 'episode') and (data['Type'].casefold() == 'audio'))):
                    #include all item types; filter applied in first API calls for each media type in get_mediaItems()
                    IncludeItemTypes=''
                    FieldsState='Id,Path,Tags,MediaSources,DateCreated,Genres,Studios,SeriesStudio,UserData'
                    SortBy='SeriesSortName,AlbumArtist,ParentIndexNumber,IndexNumber,Name'
                    SortOrder='Ascending'
                    Recursive='True'
                    EnableImages='False'
                    CollapseBoxSetItems='False'
                    #IsPlayedState=get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(the_dict,var_dict)

                    while (data_dict['QueriesRemaining_']):

                        if (not (data['Id'] == '')):
                            #Built query for child media items
                            url=(server_url + '/Users/' + user_info['user_id']  + '/Items?ParentID=' + data['Id'] + '&IncludeItemTypes=' + IncludeItemTypes +
                            #'&StartIndex=' + str(data_dict['StartIndex_']) + '&Limit=' + str(data_dict['QueryLimit_']) + '&IsPlayed=' + IsPlayedState +
                            '&StartIndex=' + str(data_dict['StartIndex_']) + '&Limit=' + str(data_dict['QueryLimit_']) +
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

                        #get tags for child items
                        for child_item in data_dict['data_']['Items']:

                            if ((child_item['Type'].casefold() == 'movie') or (child_item['Type'].casefold() == 'episode') or
                                (child_item['Type'].casefold() == 'audio') or (child_item['Type'].casefold() == 'audiobook')):

                                #if ('whitelist' in suffix_str.casefold()):
                                    #libType='whitelist'
                                #else: #('blacklist' in suffix_str.casefold()):
                                    #libType='blacklist'

                                #Save lib_id for each media item; needed during post processing
                                #child_item['mumc']={}
                                #child_item['mumc']['lib_id']=var_dict['this_' + libType + '_lib']['lib_id']
                                #child_item['mumc']['path']=var_dict['this_' + libType + '_lib']['path']
                                #child_item['mumc']['network_path']=var_dict['this_' + libType + '_lib']['network_path']

                            #if (child_item['Type'].casefold() == 'movie'):
                                #childIsTagged,matched_tags=get_isMOVIE_Tagged(the_dict,child_item,user_info,var_dict[tagType])
                            #elif (child_item['Type'].casefold() == 'episode'):
                                #childIsTagged,matched_tags=get_isEPISODE_Tagged(the_dict,child_item,user_info,var_dict[tagType])
                            #elif (child_item['Type'].casefold() == 'audio'):
                                #childIsTagged,matched_tags=get_isAUDIO_Tagged(the_dict,child_item,user_info,var_dict[tagType])
                            #elif (child_item['Type'].casefold() == 'audiobook'):
                                #childIsTagged,matched_tags=get_isAUDIOBOOK_Tagged(the_dict,child_item,user_info,var_dict[tagType])
                            #else:
                                #childIsTagged=False

                            #if (childIsTagged):
                                #remove all tags from media_item
                                #child_item=removeTags_From_mediaItem(child_item,the_dict)
                                #add matching tags to media_item
                                #child_item=addTags_To_mediaItem(matched_tags,child_item,the_dict)

                                #Emby and jellyfin store tags differently
                                #if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
                                    #tagData='TagItems'
                                #else:
                                    #tagData='Tags'

                                #matched_tags=[]

                                #for this_tag in data[tagData]:
                                    #if (isEmbyServer(the_dict['admin_settings']['server']['brand'])):
                                        #matched_tags.append(this_tag['Name'])
                                    #else:
                                        #matched_tags.append(this_tag)

                                #child_item[tagData]=list(set(child_item[tagData] + data[tagData]))
                                child_item=addTags_To_mediaItem(getList_Of_thisItemsTags(data,the_dict),child_item,the_dict)

    child_dict['Items']=data_dict['data_']['Items']
    child_dict['TotalRecordCount']=len(data_dict['data_']['Items'])
    child_dict['StartIndex']=data_dict['StartIndex_']

    return child_dict


#Get if tag is formatted as a filter statement tag
def get_isFilterStatementTag(this_tag):

    isFilterStatementTag=False
    split_this_tag=this_tag.split(':')
    filterStatementTag={}

    try:
        if (((len(split_this_tag) == 4) and ((split_this_tag[0] == 'played') or (split_this_tag[0] == 'created'))) or
            ((len(split_this_tag) == 5) and (split_this_tag[0] == 'created'))):

            if ((int(split_this_tag[1]) >= -1) and (int(split_this_tag[1]) <= 730500)):
                split_this_tag[1]=int(split_this_tag[1])

                if ((split_this_tag[2] == '>') or (split_this_tag[2] == '<') or
                    (split_this_tag[2] == '>=') or (split_this_tag[2] == '<=') or
                    (split_this_tag[2] == '==') or (split_this_tag[2] == 'not >') or
                    (split_this_tag[2] == 'not <') or (split_this_tag[2] == 'not >=') or
                    (split_this_tag[2] == 'not <=') or (split_this_tag[2] == 'not ==')):

                    if ((int(split_this_tag[3]) >= 0) and (int(split_this_tag[3]) <= 730500)):
                        split_this_tag[3]=int(split_this_tag[3])

                        if (split_this_tag[0] == 'created'):
                            if (does_index_exist(split_this_tag,4)):
                                if (split_this_tag[4].casefold() == 'true'):
                                    split_this_tag[4]=True
                                    isFilterStatementTag=True
                                elif(split_this_tag[4].casefold() == 'false'):
                                    split_this_tag[4]=False
                                    isFilterStatementTag=True
                                else:
                                    raise ValueError('Filter statement tag \'' + str(this_tag + '\' has an invalid value for behavior_control; valid values are true and false.'))
                            else:
                                split_this_tag.append(True) #default behavioral_control value
                                isFilterStatementTag=True
                        else:
                            isFilterStatementTag=True
    except:
        isFilterStatementTag=False

    if (isFilterStatementTag):

        #filterStatementTag['filter_type']=split_this_tag[0]

        #if (filterStatementTag['filter_type'] == 'played'):
        if (split_this_tag[0] == 'played'):
            filterStatementTag['media_played_days']=split_this_tag[1]
            filterStatementTag['media_played_count_comparison']=split_this_tag[2]
            filterStatementTag['media_played_count']=split_this_tag[3]
        else:
            filterStatementTag['media_created_days']=split_this_tag[1]
            filterStatementTag['media_created_played_count_comparison']=split_this_tag[2]
            filterStatementTag['media_created_played_count']=split_this_tag[3]
            filterStatementTag['behavioral_control']=split_this_tag[4]

        return filterStatementTag
    else:
        return False


#determine if movie or library are tagged
def get_isMOVIE_Tagged(the_dict,item,user_info,usertags):

    matched_tags=[]

    #define empty dictionary for tagged Movies
    istag_MOVIE={'movie':{},'movielibrary':{}}

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Movie #######################################################################################

        if ('Id' in item):
            istag_MOVIE['movie'][item['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,item,the_dict)
            #these tags are already part of the media_item; no need to add them again
            matched_tags.clear()

### End Movie ###################################################################################

### Movie Library #######################################################################################

        if ('ParentId' in item):
            movielibrary_item_info = get_ADDITIONAL_itemInfo(user_info,item['ParentId'],'movie_library_info',the_dict)
            istag_MOVIE['movielibrary'][movielibrary_item_info['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,movielibrary_item_info,the_dict)

### End Movie Library ###################################################################################

    for istagkey in istag_MOVIE:
        for istagID in istag_MOVIE[istagkey]:
            if (istag_MOVIE[istagkey][istagID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n\nMovie " + str(item['Id']) + " is tagged.",2,the_dict)
                return True,matched_tags

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nMovie " + str(item['Id']) + " is NOT tagged.",2,the_dict)

    return False,matched_tags


#determine if episode, season, series, or studio-network are tagged
def get_isEPISODE_Tagged(the_dict,item,user_info,usertags):

    matched_tags=[]

    #define empty dictionary for tagorited TV Series, Seasons, Episodes, and Channels/Networks
    istag_EPISODE={'episode':{},'season':{},'series':{},'tvlibrary':{},'seriesstudionetwork':{}}

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Episode #######################################################################################

        if ('Id' in item):
            istag_EPISODE['episode'][item['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,item,the_dict)
            #these tags are already part of the media_item; no need to add them again
            matched_tags.clear()

### End Episode ###################################################################################

### Season ########################################################################################

        if ('SeasonId' in item):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,item['SeasonId'],'season_info',the_dict)
        elif ('ParentId' in item):
            season_item_info = get_ADDITIONAL_itemInfo(user_info,item['ParentId'],'season_info',the_dict)
        else:
            season_item_info=None

        if (not (season_item_info == None)):
            istag_EPISODE['season'][season_item_info['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,season_item_info,the_dict)

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
                istag_EPISODE['series'][series_item_info['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,series_item_info,the_dict)

### End Series ####################################################################################

### TV Library ########################################################################################

                if ('ParentId' in series_item_info):
                    tvlibrary_item_info = get_ADDITIONAL_itemInfo(user_info,series_item_info['ParentId'],'tv_library_info',the_dict)
                else:
                    tvlibrary_item_info=None

                if (not (tvlibrary_item_info == None)):
                    istag_EPISODE['tvlibrary'][tvlibrary_item_info['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,tvlibrary_item_info,the_dict)

### End TV Library ####################################################################################

### Studio Network #######################################################################################

                if (('Studios' in series_item_info) and does_index_exist(series_item_info['Studios'],0)):
                    #Get studio network's item info
                    tvstudionetwork_item_info = get_ADDITIONAL_itemInfo(user_info,series_item_info['Studios'][0]['Id'],'studio_network_info',the_dict)
                elif ('SeriesStudio' in series_item_info):
                    #Get series studio network's item info
                    tvstudionetwork_item_info = get_STUDIO_itemInfo(series_item_info['SeriesStudio'],the_dict,the_dict)
                else:
                    tvstudionetwork_item_info=None

                if (not (tvstudionetwork_item_info == None)):
                    istag_EPISODE['seriesstudionetwork'][tvstudionetwork_item_info['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,tvstudionetwork_item_info,the_dict)

### End Studio Network ###################################################################################

    for istagkey in istag_EPISODE:
        for istagID in istag_EPISODE[istagkey]:
            if (istag_EPISODE[istagkey][istagID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is tagged.",2,the_dict)
                return True,matched_tags

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nEpisode " + str(item['Id']) + " is NOT tagged.",2,the_dict)

    return False,matched_tags

#determine if genres for music track, album, or music library are tagged
def get_isAUDIO_Tagged(the_dict,item,user_info,usertags):

    matched_tags=[]

    #define empty dictionary for tagorited Tracks, Albums, Artists
    istag_AUDIO={'track':{},'album':{},'audiolibrary':{}}

    if (('mumc' in item) and ('lib_id' in item['mumc']) and (item['mumc']['lib_id'] in the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):

### Track #########################################################################################

        if ('Id' in item):
            istag_AUDIO['track'][item['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,item,the_dict)
            #these tags are already part of the media_item; no need to add them again
            matched_tags.clear()

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
            istag_AUDIO['album'][album_item_info['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,album_item_info,the_dict)

### End Album/Book #####################################################################################

### Library ########################################################################################

            #Library
            if ('ParentId' in album_item_info):
                audiolibrary_item_info = get_ADDITIONAL_itemInfo(user_info,album_item_info['ParentId'],'library_info',the_dict)
            else:
                audiolibrary_item_info=None

            if (not (audiolibrary_item_info == None)):
                istag_AUDIO['audiolibrary'][audiolibrary_item_info['Id']],matched_tags=get_isItemTagged(usertags,matched_tags,audiolibrary_item_info,the_dict)

### End Library #####################################################################################

    for istagkey in istag_AUDIO:
        for istagID in istag_AUDIO[istagkey]:
            if (istag_AUDIO[istagkey][istagID]):
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log("\n\nAudio/AudioBook " + str(item['Id']) + " is tagged.",2,the_dict)
                return True,matched_tags

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nAudio/AudioBook " + str(item['Id']) + " is NOT tagged.",2,the_dict)

    return False,matched_tags


#determine if genres for audiobook track, book, or audio book library are tagged
def get_isAUDIOBOOK_Tagged(the_dict,item,user_info,usertags):
    return get_isAUDIO_Tagged(the_dict,item,user_info,usertags)