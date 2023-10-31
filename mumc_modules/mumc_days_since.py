#!/usr/bin/env python3
from datetime import datetime
from mumc_modules.mumc_output import appendTo_DEBUG_log


#Get count of days since last played
def get_days_since_played(date_last_played,the_dict):

    if not ((date_last_played == 'Unplayed') or (date_last_played == 'Unknown')):

        #Get current time
        #date_time_now = datetime.utcnow()
        date_time_now=the_dict['date_time_utc_now']

        #Keep the year, month, day, hour, minute, and seconds
        #split date_last_played after seconds
        try:
            split_date_micro_tz = date_last_played.split(".")
            date_time_last_played = datetime.strptime(date_last_played, '%Y-%m-%dT%H:%M:%S.' + split_date_micro_tz[1])
        except (ValueError):
            date_time_last_played = 'unknown date time format'

        if not (date_time_last_played == 'unknown date time format'):
            date_time_delta = date_time_now - date_time_last_played
            s_date_time_delta = str(date_time_delta)
            days_since_played = s_date_time_delta.split(' day')[0]
            if ':' in days_since_played:
                days_since_played = 'Played <1 day ago'
            elif days_since_played == '1':
                days_since_played = 'Played ' + days_since_played + ' day ago'
            else:
                days_since_played = 'Played ' + days_since_played + ' days ago'
        else:
            days_since_played='0'

        if (the_dict['DEBUG']):
            #Double newline for DEBUG log formatting
            appendTo_DEBUG_log('\n\nCaptured UTC time is: ' + str(date_time_now),3,the_dict)
            appendTo_DEBUG_log('\nDate last played or date created is: ' + str(date_last_played),2,the_dict)
            appendTo_DEBUG_log('\nFormatted date last played or date created is: ' + str(date_time_last_played),3,the_dict)
            appendTo_DEBUG_log('\nMedia item was last \'' + days_since_played + '\'',2,the_dict)
    else:
        days_since_played=date_last_played

        if (the_dict['DEBUG']):
            appendTo_DEBUG_log('\nMedia item was played or created \'' + days_since_played + '\' day(s) ago',2,the_dict)

    return(days_since_played)


#Get count of days since last created
def get_days_since_created(date_last_created,the_dict):
    return(get_days_since_played(date_last_created,the_dict).replace('Played', 'Created', 1))


def convert_timeToString(byUserId_item):
    for userId in byUserId_item:
        if (not((userId == 'DynamicBehavior') or (userId == 'ActionControl') or (userId == 'ActionType') or (userId == 'MonitoredUsersAction') or
                (userId == 'MonitoredUsersMeetPlayedFilter') or (userId == 'ConfiguredBehavior'))):
            for itemId in byUserId_item[userId]:
                if ('CutOffDatePlayed' in byUserId_item[userId][itemId]):
                    byUserId_item[userId][itemId]['CutOffDatePlayed']=str(byUserId_item[userId][itemId]['CutOffDatePlayed'])
                if ('CutOffDateCreated' in byUserId_item[userId][itemId]):
                    byUserId_item[userId][itemId]['CutOffDateCreated']=str(byUserId_item[userId][itemId]['CutOffDateCreated'])

    return(byUserId_item)