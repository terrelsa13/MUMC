from mumc_modules.mumc_output import appendTo_DEBUG_log


#get season and episode numbers; pad with zeros to make them equal lengths
def get_season_episode(ParentIndexNumber,IndexNumber,the_dict):

    #convert season number to string
    ParentIndexNumber_str = str(ParentIndexNumber)
    #convert episode number to string
    IndexNumber_str = str(IndexNumber)

    #Add leading zero to single digit seasons
    if (len(ParentIndexNumber_str) == 1):
        ParentIndexNumber_str = '0' + ParentIndexNumber_str

    #Add leading zero to single digit episodes
    if (len(IndexNumber_str) == 1):
        IndexNumber_str = '0' + IndexNumber_str

    #Pad the season number or episode number with zeros until they are the same length
    while (not (len(ParentIndexNumber_str) == len(IndexNumber_str))):

        #pad episode number when season number is longer
        if (len(IndexNumber_str) < len(ParentIndexNumber_str)):
            IndexNumber_str = '0' + IndexNumber_str
        #pad season number when episode number is longer
        elif (len(IndexNumber_str) > len(ParentIndexNumber_str)):
            ParentIndexNumber_str = '0' + ParentIndexNumber_str

    #Format the season and episode into something easily readable (i.e. s01.e23)
    formatted_season_episode = 's' + ParentIndexNumber_str + '.e' + IndexNumber_str

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\nSeason # is: ' + str(ParentIndexNumber),2,the_dict)
        appendTo_DEBUG_log('\nEpisode # is: ' + str(IndexNumber),2,the_dict)
        appendTo_DEBUG_log('\nPadded Season #: ' + ParentIndexNumber_str,2,the_dict)
        appendTo_DEBUG_log('\nPadded Episode #: ' + IndexNumber_str,2,the_dict)
        appendTo_DEBUG_log('\nFormatted season#.episode# is: ' + str(formatted_season_episode) + '\n',2,the_dict)

    return(formatted_season_episode)


#get disk and track numbers; pad with zeros to make them equal lengths
def get_disk_track(ParentIndexNumber,IndexNumber,the_dict):
    return get_season_episode(ParentIndexNumber,IndexNumber,the_dict).replace('s', 'd', 1).replace('e', 't', 1)