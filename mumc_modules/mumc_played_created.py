from dateutil.parser import parse
from mumc_modules.mumc_output import appendTo_DEBUG_log


#Get isPlayed state for API filtering
def get_isPlayed_FilterValue(the_dict,filter_played_count_comparison,filter_played_count):

    if (filter_played_count_comparison == '>'):
        #Play counts 1 thru 730500
        isPlayed_Filter_Value='playedOnly'
    elif (filter_played_count_comparison == '<'):
        if ((filter_played_count == 0) or (filter_played_count == 1)):
            #Play counts 0 and 1
            isPlayed_Filter_Value='unplayedOnly'
        else:
            #Play counts 2 thru 730499
            isPlayed_Filter_Value='playedAndUnplayed'
    elif (filter_played_count_comparison == '>='):
        if (filter_played_count == 0):
            #Play count 0
            isPlayed_Filter_Value='playedAndUnplayed'
        else:
            #Play counts 1 thru 730500
            isPlayed_Filter_Value='playedOnly'
    elif (filter_played_count_comparison == '<='):
        if (filter_played_count == 0):
            #Play count 0
            isPlayed_Filter_Value='unplayedOnly'
        else:
            #Play counts 1 thru 730500
            isPlayed_Filter_Value='playedAndUnplayed'
    elif (filter_played_count_comparison == '=='):
        if (filter_played_count == 0):
            #Play count 0
            isPlayed_Filter_Value='unplayedOnly'
        else:
            #Play count 1 thru 730500
            isPlayed_Filter_Value='playedOnly'
    elif (filter_played_count_comparison == 'not >'):
        if ((filter_played_count == 0) or (filter_played_count == 1)):
            #Play count 0 thru 1
            isPlayed_Filter_Value='unplayedOnly'
        else:
            #Play count 2 thru 730499
            isPlayed_Filter_Value='playedAndUnplayed'
    elif (filter_played_count_comparison == 'not <'):
        #Play counts 1 thru 730500
        isPlayed_Filter_Value='playedOnly'
    elif (filter_played_count_comparison == 'not >='):
        if ((filter_played_count == 0) or (filter_played_count == 1)):
            #Play count 0
            isPlayed_Filter_Value='unplayedOnly'
        else:
            #Play count 1 thru 730499
            isPlayed_Filter_Value='playedAndUnplayed'
    elif (filter_played_count_comparison == 'not <='):
        #Play count 1 thru 730500
        isPlayed_Filter_Value='playedOnly'
    elif (filter_played_count_comparison == 'not =='):
        if (filter_played_count == 0):
            #Play count 1 thru 730500
            isPlayed_Filter_Value='playedOnly'
        else:
            #Play count 0 thru 730500
            isPlayed_Filter_Value='playedAndUnplayed'
    else:
        #Play count comparison unknown
        isPlayed_Filter_Value='playedAndUnplayed'

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("IsPlayed IsCreated Filter Value: '" + isPlayed_Filter_Value + "'\n",2,the_dict)

    return isPlayed_Filter_Value


#Get isPlayed state for API filtering
def get_isCreatedPlayed_FilterValue(the_dict,filter_created_played_count_comparison,filter_created_played_count):
    return get_isPlayed_FilterValue(the_dict,filter_created_played_count_comparison,filter_created_played_count)


# Combine isPlayed value with isCreated-Played value to determine if the API query should
 # filter for played, unplayed, or neither (aka played and unplayed)
def get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(the_dict,var_dict):

    played_days=int(var_dict['media_played_days'])
    created_days=int(var_dict['media_created_days'])

    filter_played_count_comparison=var_dict['media_played_count_comparison']
    filter_created_played_count_comparison=var_dict['media_created_played_count_comparison']

    if (isinstance(var_dict['media_played_count'],int)):
        filter_played_count=int(var_dict['media_played_count'])
    if (isinstance(var_dict['media_created_played_count'],int)):
        filter_created_played_count=int(var_dict['media_created_played_count'])

    if (played_days >= 0):
        isPlayed_Filter_Value=get_isPlayed_FilterValue(the_dict,filter_played_count_comparison,filter_played_count)
    else:
        isPlayed_Filter_Value='disabled'

    if (created_days >= 0):
        isCreated_Filter_Value=get_isCreatedPlayed_FilterValue(the_dict,filter_created_played_count_comparison,filter_created_played_count)
    else:
        isCreated_Filter_Value='disabled'

    if ((isPlayed_Filter_Value == 'unplayedOnly') and (isCreated_Filter_Value == 'unplayedOnly')):
        return 'False'
    elif ((isPlayed_Filter_Value == 'playedOnly') and (isCreated_Filter_Value == 'playedOnly')):
        return 'True'
    elif ((isPlayed_Filter_Value == 'disabled') and (isCreated_Filter_Value == 'unplayedOnly')):
        return 'False'
    elif ((isPlayed_Filter_Value == 'disabled') and (isCreated_Filter_Value == 'playedOnly')):
        return 'True'
    elif ((isPlayed_Filter_Value == 'unplayedOnly') and (isCreated_Filter_Value == 'disabled')):
        return 'False'
    elif ((isPlayed_Filter_Value == 'playedOnly') and (isCreated_Filter_Value == 'disabled')):
        return 'True'
    elif ((isPlayed_Filter_Value == 'disabled') and (isCreated_Filter_Value == 'disabled')):
        return 'disabled'
    else:
        return ''


def getTag_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(tag_type,the_dict,var_dict,prev_isPlayed_isUnplayed):
    for this_tag in var_dict[tag_type + '_filter_statements']:
        #todo get item tags
        this_tag_dict=var_dict[tag_type + '_filter_statements'][this_tag]
        if (this_tag.startswith('played')):
            #played_days=this_tag['media_played_days']
            this_tag_dict['media_created_days']=-1
            #cut_off_date_played=this_tag_dict['cut_off_date_played_media']
            this_tag_dict['cut_off_date_created_media']=None
            #played_count_comparison=this_tag_dict['media_played_count_comparison']
            #played_count=this_tag_dict['media_played_count']
            this_tag_dict['media_created_played_count_comparison']=None
            this_tag_dict['media_created_played_count']=None
        elif (this_tag.startswith('created')):
            this_tag_dict['media_played_days']=-1
            #created_days=this_tag_dict['media_created_days']
            this_tag_dict['cut_off_date_played_media']=None
            #cut_off_date_created=this_tag_dict['cut_off_date_created_media']
            this_tag_dict['media_played_count_comparison']=None
            this_tag_dict['media_played_count']=None
            #created_played_count_comparison=this_tag_dict['media_created_played_count_comparison']
            #created_played_count=this_tag_dict['media_created_played_count']

        isPlayed_isUnplayed=get_isPlayed_isUnplayed_isPlayedAndUnplayed_QueryValue(the_dict,this_tag_dict)

        if ((prev_isPlayed_isUnplayed == 'disabled') and (isPlayed_isUnplayed == 'disabled')):
            prev_isPlayed_isUnplayed='disabled'
        elif ((prev_isPlayed_isUnplayed == 'disabled') and (isPlayed_isUnplayed == 'True')):
            prev_isPlayed_isUnplayed='True'
        elif ((prev_isPlayed_isUnplayed == 'disabled') and (isPlayed_isUnplayed == 'False')):
            prev_isPlayed_isUnplayed='False'
        elif ((prev_isPlayed_isUnplayed == 'disabled') and (isPlayed_isUnplayed == '')):
            prev_isPlayed_isUnplayed=''

        elif ((prev_isPlayed_isUnplayed == 'True') and (isPlayed_isUnplayed == 'disabled')):
            prev_isPlayed_isUnplayed='True'
        elif ((prev_isPlayed_isUnplayed == 'True') and (isPlayed_isUnplayed == 'True')):
            prev_isPlayed_isUnplayed='True'
        elif ((prev_isPlayed_isUnplayed == 'True') and (isPlayed_isUnplayed == 'False')):
            prev_isPlayed_isUnplayed=''
        elif ((prev_isPlayed_isUnplayed == 'True') and (isPlayed_isUnplayed == '')):
            prev_isPlayed_isUnplayed=''

        elif ((prev_isPlayed_isUnplayed == 'False') and (isPlayed_isUnplayed == 'disabled')):
            prev_isPlayed_isUnplayed='False'
        elif ((prev_isPlayed_isUnplayed == 'False') and (isPlayed_isUnplayed == 'True')):
            prev_isPlayed_isUnplayed=''
        elif ((prev_isPlayed_isUnplayed == 'False') and (isPlayed_isUnplayed == 'False')):
            prev_isPlayed_isUnplayed='False'
        elif ((prev_isPlayed_isUnplayed == 'False') and (isPlayed_isUnplayed == '')):
            prev_isPlayed_isUnplayed=''

        elif ((prev_isPlayed_isUnplayed == '') and (isPlayed_isUnplayed == 'disabled')):
            prev_isPlayed_isUnplayed=''
        elif ((prev_isPlayed_isUnplayed == '') and (isPlayed_isUnplayed == 'True')):
            prev_isPlayed_isUnplayed=''
        elif ((prev_isPlayed_isUnplayed == '') and (isPlayed_isUnplayed == 'False')):
            prev_isPlayed_isUnplayed=''
        elif ((prev_isPlayed_isUnplayed == '') and (isPlayed_isUnplayed == '')):
            prev_isPlayed_isUnplayed=''

    return prev_isPlayed_isUnplayed


# determine if media item has been played specified amount of times
def get_playedStatus(the_dict,item,media_condition,filter_count_comparison,filter_count,itemPlayedCount,itemIsPlayed):

    if (media_condition == 'created'):
        IsPlayedStatus=get_isCreatedPlayed_FilterValue(the_dict,filter_count_comparison,filter_count)
    else:
        IsPlayedStatus='playedOnly'

    item_matches_played_count_filter=False

    if ((not (itemPlayedCount == None)) and (((IsPlayedStatus == 'playedOnly') and itemIsPlayed) or ((IsPlayedStatus == 'unplayedOnly') and (not itemIsPlayed)) or (IsPlayedStatus == 'playedAndUnplayed'))):
        if (filter_count_comparison == '>'):
            if (itemPlayedCount > filter_count):
                #media item play count greater than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '<'):
            if (itemPlayedCount < filter_count):
                #media item play count less than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '>='):
            if (itemPlayedCount >= filter_count):
                #media item play count greater than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '<='):
            if (itemPlayedCount <= filter_count):
                #media item play count less than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == '=='):
            if (itemPlayedCount == filter_count):
                #media item play count equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not >'):
            if (not (itemPlayedCount > filter_count)):
                #media item play count not greater than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not <'):
            if (not (itemPlayedCount < filter_count)):
                #media item play count not less than specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not >='):
            if (not (itemPlayedCount >= filter_count)):
                #media item play count not greater than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not <='):
            if (not (itemPlayedCount <= filter_count)):
                #media item play count not less than or equal to specified value
                item_matches_played_count_filter=True
        elif (filter_count_comparison == 'not =='):
            if (not (itemPlayedCount == filter_count)):
                #media item play count not equal to specified value
                item_matches_played_count_filter=True

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\nDoes Media Item " + str(item['Id']) + " Meet The " + media_condition + " Count Filter?...",2,the_dict)
            if (((IsPlayedStatus == 'playedOnly') and itemIsPlayed) or ((IsPlayedStatus == 'unplayedOnly') and not itemIsPlayed) or (IsPlayedStatus == 'playedAndUnplayed')):
                appendTo_DEBUG_log("\n" + str(itemPlayedCount) + " " + str(filter_count_comparison) + " " + str(filter_count) + " : " + str(item_matches_played_count_filter) + "\n",2,the_dict,)
            else:
                appendTo_DEBUG_log("\n" + str(itemPlayedCount) + " " + str(filter_count_comparison) + " " + str(filter_count) + " : " + "N/A Unplayed\n",2,the_dict,)

    return item_matches_played_count_filter


# determine if media item has been played specified amount of times
def get_createdPlayedStatus(the_dict,item,media_condition,filter_count_comparison,filter_count,itemPlayedCount,itemIsPlayed):
    return get_playedStatus(the_dict,item,media_condition,filter_count_comparison,filter_count,itemPlayedCount,itemIsPlayed)


# get played status of media item
def get_isItemPlayed(item):
    #'Played' is set to 'True' when the 'PlayedPercentage' for the media_item is >= the 'Max Resume Percent' set in the GUI
     #The default 'Max Resume Percent' in the GUI is '90%'

    '''
    UserData	
        PlayedPercentage: 66.8771217639365
        PlaybackPositionTicks: 4744958540
        PlayCount: 2
        IsFavorite: false
        LastPlayedDate: "2024-06-03T22:45:40.0000000Z"
        Played: false
    '''

    itemIsPlayed=False

    if ('UserData' in item):
        if ('Played' in item['UserData']) and (item['UserData']['Played']):
            itemIsPlayed=item['UserData']['Played']

    return itemIsPlayed


def get_isItemMeetingDaysFilter(date_string,cut_off_date):

    item_meets_day_count=False

    if (not (date_string == 'Unplayed')):
        if ((cut_off_date) > (parse(date_string))):
            #media item meets the played/created days count
            item_meets_day_count=True

    return item_meets_day_count


#get played days and counts; get created days and counts
def get_playedDays_createdPlayedDays_playedCounts_createdPlayedCounts(the_dict,item,var_dict):

    played_days=var_dict['media_played_days']
    created_days=var_dict['media_created_days']
    cut_off_date_played=var_dict['cut_off_date_played_media']
    cut_off_date_created=var_dict['cut_off_date_created_media']
    played_count_comparison=var_dict['media_played_count_comparison']
    played_count=var_dict['media_played_count']
    created_played_count_comparison=var_dict['media_created_played_count_comparison']
    created_played_count=var_dict['media_created_played_count']

    item_matches_played_days_filter=False
    item_matches_created_days_filter=False
    itemPlayedCount=0
    item_matches_played_count_filter=False
    item_matches_created_played_count_filter=False
    return_dict={}

    itemIsPlayed=get_isItemPlayed(item)

    if (itemIsPlayed):
        #establish if media item meets the played cutoff date and is played
        if ((played_days >= 0) and ('UserData' in item) and ('LastPlayedDate' in item['UserData'])):
            #was media item last played long enough ago?
            item_matches_played_days_filter=get_isItemMeetingDaysFilter(item['UserData']['LastPlayedDate'],cut_off_date_played)

        #establish if media item meets the created cutoff date and is played
        if ((created_days >= 0) and ('DateCreated' in item)):
            #was media item created long enough ago?
            item_matches_created_days_filter=get_isItemMeetingDaysFilter(item['DateCreated'],cut_off_date_created)

        if (((played_days >= 0) or (created_days >= 0)) and ('UserData' in item) and ('PlayCount' in item['UserData'])):
            itemPlayedCount=item['UserData']['PlayCount']

        #Decide if media item meets the played count filter criteria
        #and
        #Decide if media item meets the created played count filter criteria
        if (('UserData' in item) and ('PlayCount' in item['UserData'])):
            item_matches_played_count_filter=get_playedStatus(the_dict,item,'played',played_count_comparison,played_count,itemPlayedCount,itemIsPlayed)
            item_matches_created_played_count_filter=get_createdPlayedStatus(the_dict,item,'created',created_played_count_comparison,created_played_count,itemPlayedCount,itemIsPlayed)
    else:
        #establish if media item meets the created cutoff date and is played
        if ((created_days >= 0) and ('DateCreated' in item)):
            #was media item created long enough ago?
            item_matches_created_days_filter=get_isItemMeetingDaysFilter(item['DateCreated'],cut_off_date_created)

        if ((created_days >= 0) and ('UserData' in item) and ('PlayCount' in item['UserData'])):
            itemPlayedCount=item['UserData']['PlayCount']

        #Decide if media item meets the played count filter criteria
        #and
        #Decide if media item meets the created played count filter criteria
        if (('UserData' in item) and ('PlayCount' in item['UserData'])):
            item_matches_created_played_count_filter=get_createdPlayedStatus(the_dict,item,'created',created_played_count_comparison,created_played_count,itemPlayedCount,itemIsPlayed)

    return_dict['itemIsPlayed']=itemIsPlayed
    return_dict['itemPlayedCount']=itemPlayedCount
    return_dict['item_matches_played_days_filter']=item_matches_played_days_filter
    return_dict['item_matches_created_days_filter']=item_matches_created_days_filter
    return_dict['item_matches_played_count_filter']=item_matches_played_count_filter
    return_dict['item_matches_created_played_count_filter']=item_matches_created_played_count_filter

    return return_dict


def getTag_playedDays_createdPlayedDays_playedCounts_createdPlayedCounts(tag_type,the_dict,item,var_dict):

    played_created_dict={}

    #for this_tag in var_dict[tag_type + '_filter_statements']:
    for this_tag in var_dict['matched_filter_' + tag_type + 's']:
        #todo get item tags
        this_tag_dict=var_dict[tag_type + '_filter_statements'][this_tag]
        if (this_tag.startswith('played')):
            this_tag_dict['media_created_days']=-1
            this_tag_dict['cut_off_date_created_media']=None
            this_tag_dict['media_created_played_count_comparison']=None
            this_tag_dict['media_created_played_count']=None
            this_tag_dict['behavioral_control']=None
        elif (this_tag.startswith('created')):
            this_tag_dict['media_played_days']=-1
            this_tag_dict['cut_off_date_played_media']=None
            this_tag_dict['media_played_count_comparison']=None
            this_tag_dict['media_played_count']=None

        
        played_created_dict=get_playedDays_createdPlayedDays_playedCounts_createdPlayedCounts(the_dict,item,this_tag_dict)

        var_dict['matched_filter_' + tag_type + 's'][this_tag]['IsMeetingAction']=True
        var_dict['matched_filter_' + tag_type + 's'][this_tag]['IsMeetingPlayedFilter']=(played_created_dict['item_matches_played_days_filter'] and played_created_dict['item_matches_played_count_filter'])
        var_dict['matched_filter_' + tag_type + 's'][this_tag]['IsMeetingCreatedPlayedFilter']=(played_created_dict['item_matches_created_days_filter'] and played_created_dict['item_matches_created_played_count_filter'])

    return var_dict