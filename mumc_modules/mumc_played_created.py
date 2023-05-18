#!/usr/bin/env python3
from dateutil.parser import parse
from mumc_modules.mumc_output import appendTo_DEBUG_log


#Get isPlayed state for API filtering
def get_isPlayed_FilterValue(the_dict,filter_played_count_comparison,filter_played_count):

    if (filter_played_count_comparison == '>'):
        #Play counts 1 thru 730500
        isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == '<'):
        if ((filter_played_count == 0) or (filter_played_count == 1)):
            #Play counts 0 and 1
            isPlayed_Filter_Value='False'
        else:
            #Play counts 0 thru 730499
            isPlayed_Filter_Value=''
    elif (filter_played_count_comparison == '>='):
        if (filter_played_count == 0):
            #Play counts 0 thru 730500
            isPlayed_Filter_Value=''
        else:
            #Play counts 1 thru 730500
            isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == '<='):
        if (filter_played_count == 0):
            #Play count 0
            isPlayed_Filter_Value='False'
        else:
            #Play counts 0 thru 730500
            isPlayed_Filter_Value=''
    elif (filter_played_count_comparison == '=='):
        if (filter_played_count == 0):
            #Play count 0
            isPlayed_Filter_Value='False'
        else:
            #Play count 1 thru 730500
            isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == 'not >'):
        if ((filter_played_count == 0) or (filter_played_count == 1)):
            #Play count 0
            isPlayed_Filter_Value='False'
        else:
            #Play count 1 thru 730499
            isPlayed_Filter_Value=''
    elif (filter_played_count_comparison == 'not <'):
        #Play counts 1 thru 730500
        isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == 'not >='):
        if ((filter_played_count == 0) or (filter_played_count == 1)):
            #Play count 0
            isPlayed_Filter_Value='False'
        else:
            #Play count 1 thru 730499
            isPlayed_Filter_Value=''
    elif (filter_played_count_comparison == 'not <='):
        #Play count 1 thru 730500
        isPlayed_Filter_Value='True'
    elif (filter_played_count_comparison == 'not =='):
        if (filter_played_count == 0):
            #Play count 1 thru 730500
            isPlayed_Filter_Value='True'
        else:
            #Play count 0 thru 730500
            isPlayed_Filter_Value=''
    else:
        #Play count comparison unknown
        isPlayed_Filter_Value=''

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nIsPlayed IsCreated Filter Value: " + isPlayed_Filter_Value,2,the_dict)

    return isPlayed_Filter_Value


#Get isPlayed state for API filtering
def get_isCreated_FilterValue(the_dict,filter_created_played_count_comparison,filter_created_played_count):
    return get_isPlayed_FilterValue(the_dict,filter_created_played_count_comparison,filter_created_played_count)


# Combine isPlayed value with isCreated-Played value
def get_isPlayedCreated_FilterValue(the_dict,played_days,created_days,filter_played_count_comparison,filter_played_count,filter_created_played_count_comparison,filter_created_played_count):

    if (played_days >= 0):
        isPlayed_Filter_Value=get_isPlayed_FilterValue(the_dict,filter_played_count_comparison,filter_played_count)
    else:
        isPlayed_Filter_Value='disabled'

    if (created_days >= 0):
        isCreated_Filter_Value=get_isCreated_FilterValue(the_dict,filter_created_played_count_comparison,filter_created_played_count)
    else:
        isCreated_Filter_Value='disabled'

    if ((isPlayed_Filter_Value == 'False') and (isCreated_Filter_Value == 'False')):
        return isPlayed_Filter_Value
    elif ((isPlayed_Filter_Value == 'True') and (isCreated_Filter_Value == 'True')):
        return isPlayed_Filter_Value
    elif ((isPlayed_Filter_Value == 'disabled') and ((isCreated_Filter_Value == 'False') or (isCreated_Filter_Value == 'True'))):
        return isCreated_Filter_Value
    elif (((isPlayed_Filter_Value == 'False') or (isPlayed_Filter_Value == 'True')) and (isCreated_Filter_Value == 'disabled')):
        return isPlayed_Filter_Value
    else:
        return ''


# determine if media item has been played specified amount of times
def get_playedStatus(the_dict,item,media_condition,filter_count_comparison,filter_count):

    item_play_count=item['UserData']['PlayCount']
    item_played=item['UserData']['Played']

    if (media_condition == 'created'):
        IsPlayed=get_isCreated_FilterValue(the_dict,filter_count_comparison,filter_count)
    else:
        IsPlayed='True'

    item_matches_played_count_filter=False

    if (((IsPlayed == 'True') and item_played) or ((IsPlayed == 'False') and not item_played) or (IsPlayed == '')):
        if (filter_count_comparison == '>'):
            if (item_play_count > filter_count):
                #media item play count greater than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '<'):
            if (item_play_count < filter_count):
                #media item play count less than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '>='):
            if (item_play_count >= filter_count):
                #media item play count greater than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '<='):
            if (item_play_count <= filter_count):
                #media item play count less than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '=='):
            if (item_play_count == filter_count):
                #media item play count equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not >'):
            if (not (item_play_count > filter_count)):
                #media item play count not greater than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not <'):
            if (not (item_play_count < filter_count)):
                #media item play count not less than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not >='):
            if (not (item_play_count >= filter_count)):
                #media item play count not greater than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not <='):
            if (not (item_play_count <= filter_count)):
                #media item play count not less than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not =='):
            if (not (item_play_count == filter_count)):
                #media item play count not equal to specified value
                item_matches_played_count_filter=True

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nDoes Media Item " + str(item['Id']) + " Meet The " + media_condition + " Count Filter?...",2,the_dict)
        if (((IsPlayed == 'True') and item_played) or ((IsPlayed == 'False') and not item_played) or (IsPlayed == '')):
            appendTo_DEBUG_log("\n" + str(item_play_count) + " " + filter_count_comparison + " " + str(filter_count) + " : " + str(item_matches_played_count_filter),2,the_dict,)
        else:
            appendTo_DEBUG_log("\n" + str(item_play_count) + " " + filter_count_comparison + " " + str(filter_count) + " : " + "N/A Unplayed",2,the_dict,)

    return item_matches_played_count_filter


# determine if media item has been played specified amount of times
def get_createdPlayedStatus(the_dict,item,media_condition,filter_count_comparison,filter_count):
    return get_playedStatus(the_dict,item,media_condition,filter_count_comparison,filter_count)


#get played days and counts; get created days and counts
def get_playedCreatedDays_playedCreatedCounts(the_dict,item,played_days,created_days,cut_off_date_played,cut_off_date_created, played_count_comparison,played_count,created_played_count_comparison,created_played_count):

    #establish played cutoff date for media item
    if ((played_days >= 0) and ('UserData' in item) and ('LastPlayedDate' in item['UserData'])
        and ('Played' in item['UserData']) and (item['UserData']['Played'] == True)):
        if ((cut_off_date_played) > (parse(item['UserData']['LastPlayedDate']))):
            item_matches_played_days_filter=True
        else:
            item_matches_played_days_filter=False
    else:
        item_matches_played_days_filter=False

    #establish created cutoff date for media item
    if ((created_days >= 0) and ('DateCreated' in item)):
        if (cut_off_date_created > parse(item['DateCreated'])):
            item_matches_created_days_filter=True
        else:
            item_matches_created_days_filter=False
    else:
        item_matches_created_days_filter=False

    #Decide if media item meets the played count filter criteria
    #and
    #Decide if media item meets the created played count filter criteria
    if (('UserData' in item) and ('PlayCount' in item['UserData'])):
        item_matches_played_count_filter=get_playedStatus(the_dict,item,'played',played_count_comparison,played_count)
        item_matches_created_played_count_filter=get_createdPlayedStatus(the_dict,item,'created',created_played_count_comparison,created_played_count)
    else:
        item_matches_played_count_filter=False
        item_matches_created_played_count_filter=False

    return item_matches_played_days_filter,item_matches_created_days_filter,item_matches_played_count_filter,item_matches_created_played_count_filter