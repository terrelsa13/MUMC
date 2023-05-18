#!/usr/bin/env python3
from mumc_modules.mumc_trakt_fix import modify_lastPlayedDate
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_compare_items import does_index_exist


#check if desired metadata exists
# if it does not populate it with unknown
def prepare_MOVIEoutput(the_dict,item,user_key,movie_set_missing_last_played_date):

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nPreparing Movie " + item['Id'] + " For Output",2,the_dict)

    if not ('Type' in item):
        item['Type']='Movie'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Type'] Was Missing",3,the_dict)
    if not ('Name' in item):
        item['Name']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Name'] Was Missing",3,the_dict)
    if not ('Studios' in item):
        item['Studios']=[0]
        item['Studios'][0]={'Name':'Unknown'}
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Studios'] or item['Studios'][0] Was Missing",3,the_dict)
    if not (does_index_exist(item['Studios'],0,the_dict)):
        item['Studios']=[0]
        item['Studios'][0]={'Name':'Unknown'}
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Studios'][0] or item['Studios'][0]{'Name':'Unknown'} Was Missing",3,the_dict)
    if not ('Name' in item['Studios'][0]):
        item['Studios'][0]={'Name':'Unknown'}
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Studios'][0]{'Name':'Unknown'} Was Missing",3,the_dict)
    if ((item['UserData']['Played'] == True) and (item['UserData']['PlayCount'] >= 1)):
        if not ('LastPlayedDate' in item['UserData']):
            if (movie_set_missing_last_played_date):
                modify_lastPlayedDate(item,user_key,the_dict)
            else:
                item['UserData']['LastPlayedDate']='1970-01-01T00:00:00.00Z'
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nitem['UserData']['LastPlayedDate'] Was Missing",3,the_dict)
    else:
        item['UserData']['LastPlayedDate']='Unplayed'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['UserData']['LastPlayedDate'] Was Missing",3,the_dict)
    if not ('DateCreated' in item):
        item['DateCreated']='1970-01-01T00:00:00.00Z'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['DateCreated'] Was Missing",3,the_dict)
    if not ('Id' in item):
        item['Id']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Id'] Was Missing",3,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nFinished Preparing Movie " + item['Id'] + " For Output",2,the_dict)

    return item


#check if desired metadata exists
# if it does not populate it with unknown
def prepare_EPISODEoutput(the_dict,item,user_key,episode_set_missing_last_played_date):

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n\nPreparing Episode " + item['Id'] + " For Output",2,the_dict)

    if not ('Type' in item):
        item['Type']='Episode'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Type'] Was Missing",3,the_dict)
    if not ('SeriesName' in item):
        item['SeriesName']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['SeriesName'] Was Missing",3,the_dict)
    if not ('ParentIndexNumber' in item):
        item['ParentIndexNumber']='??'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['ParentIndexNumber'] Was Missing",3,the_dict)
    if not ('IndexNumber' in item):
        item['IndexNumber']='??'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['IndexNumber'] Was Missing",3,the_dict)
    if not ('Name' in item):
        item['Name']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Name'] Was Missing",3,the_dict)
    if not ('SeriesStudio' in item):
        item['SeriesStudio']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['SeriesStudio'] Was Missing",3,the_dict)
    if ((item['UserData']['Played'] == True) and (item['UserData']['PlayCount'] >= 1)):
        if not ('LastPlayedDate' in item['UserData']):
            if (episode_set_missing_last_played_date == 1):
                modify_lastPlayedDate(item,user_key,the_dict)
            else:
                item['UserData']['LastPlayedDate']='1970-01-01T00:00:00.00Z'
            if (the_dict['DEBUG']):
                appendTo_DEBUG_log("\nitem['UserData']['LastPlayedDate'] Was Missing",3,the_dict)
    else:
        item['UserData']['LastPlayedDate']='Unplayed'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['UserData']['LastPlayedDate'] Was Missing",3,the_dict)
    if not ('DateCreated' in item):
        item['DateCreated']='1970-01-01T00:00:00.00Z'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['DateCreated'] Was Missing",3,the_dict)
    if not ('Id' in item):
        item['Id']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Id'] Was Missing",3,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nFinished Preparing Episode " + item['Id'] + " For Output",2,the_dict)

    return item


#check if desired metadata exists
# if it does not populate it with unknown
def prepare_AUDIOoutput(the_dict,item,user_key,audio_set_missing_last_played_date,mediaType):

    if (mediaType == "audio"):
        audio_set_missing_last_played_date=audio_set_missing_last_played_date
    else:
        audio_set_missing_last_played_date=0

    if ((isJellyfinServer(the_dict['server_brand'])) and (mediaType == "audiobook")):
        audiobook_set_missing_last_played_date=audio_set_missing_last_played_date
    else:
        audiobook_set_missing_last_played_date=0

    if (the_dict['DEBUG']):
        if (mediaType == "audio"):
            appendTo_DEBUG_log("\n\nPreparing Audio " + item['Id'] + " For Output",2,the_dict)
        elif (mediaType == "audiobook"):
            appendTo_DEBUG_log("\n\nPreparing AudioBook " + item['Id'] + " For Output",2,the_dict)

    if not ('Type' in item):
        item['Type']='Audio'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Type'] Was Missing",3,the_dict)
    if not ('ParentIndexNumber' in item):
        item['ParentIndexNumber']=999
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['ParentIndexNumber'] Was Missing",3,the_dict)
    if not ('IndexNumber' in item):
        item['IndexNumber']=999
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['IndexNumber'] Was Missing",3,the_dict)
    if not ('Name' in item):
        item['Name']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Name'] Was Missing",3,the_dict)
    if not ('Album' in item):
        item['Album']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Album'] Was Missing",3,the_dict)
    if not ('Artists' in item):
        item['Artists']=['Unknown']
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Artists'] Was Missing",3,the_dict)
    if not (does_index_exist(item['Artists'],0,the_dict)):
        item['Artists']=['Unknown']
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Artists'][0] Was Missing",3,the_dict)
    if not ('AlbumArtist' in item):
        item['AlbumArtist']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['AlbumArtist'] Was Missing",3,the_dict)
    if not (does_index_exist(item['AlbumArtist'],0,the_dict)):
        item['AlbumArtist']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['AlbumArtist'] Was Missing",3,the_dict)
    if not ('Studios' in item):
        item['Studios']=[{'Name':'Unknown'}]
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Studios'] Was Missing",3,the_dict)
    if not (does_index_exist(item['Studios'],0,the_dict)):
        item['Studios']=[{'Name':'Unknown'}]
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Studios']{'Name':'Unknown'} Was Missing",3,the_dict)
    if ((item['UserData']['Played'] == True) and (item['UserData']['PlayCount'] >= 1)):
        if not ('LastPlayedDate' in item['UserData']):
            if (((mediaType == "audio") and (audio_set_missing_last_played_date == 1)) or
               ((isJellyfinServer(the_dict['server_brand'])) and (mediaType == "audiobook") and (audiobook_set_missing_last_played_date == 1))):
                modify_lastPlayedDate(item,user_key,the_dict)
            else:
                item['UserData']['LastPlayedDate']='1970-01-01T00:00:00.00Z'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['UserData']['LastPlayedDate'] Was Missing",3,the_dict)
    else:
        item['UserData']['LastPlayedDate']='Unplayed'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['UserData']['LastPlayedDate'] Was Missing",3,the_dict)
    if not ('DateCreated' in item):
        item['DateCreated']='1970-01-01T00:00:00.00Z'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['DateCreated'] Was Missing",3,the_dict)
    if not ('Id' in item):
        item['Id']='Unknown'
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nitem['Id'] Was Missing",3,the_dict)
    if not ('PremiereDate' in item):
        item['PremiereDate']='1970-01-01T00:00:00.00Z'
    if not ('ProductionYear' in item):
        item['ProductionYear']='1970-01-01T00:00:00.00Z'

    if (the_dict['DEBUG']):
        if (mediaType == "audio"):
            appendTo_DEBUG_log("\nFinished Preparing Audio " + item['Id'] + " For Output",2,the_dict)
        elif (mediaType == "audiobook"):
            appendTo_DEBUG_log("\nFinished Preparing AudioBook " + item['Id'] + " For Output",2,the_dict)

    return item


#check if desired metadata exists
# if it does not populate it with unknown
def prepare_AUDIOBOOKoutput(the_dict,item,user_key,audiobook_set_missing_last_played_date,mediaType):
    return prepare_AUDIOoutput(item,user_key,audiobook_set_missing_last_played_date,mediaType)