from mumc_modules.mumc_output import appendTo_DEBUG_log


#get season and episode numbers; pad with zeros to make them equal lengths
def format_season_or_episode_index(IndexNumber):

    #convert index number to string
    index_num_str = str(IndexNumber)

    #Add leading zero to single digit index
    if (len(index_num_str) == 1):
        index_num_str = '0' + index_num_str

    return(index_num_str)


#get season and episode numbers; pad with zeros to make them equal lengths
def get_season_episode(ParentIndexNumber,IndexNumber,the_dict):

    season_num_str=format_season_or_episode_index(ParentIndexNumber)
    episode_num_str=format_season_or_episode_index(IndexNumber)

    #Pad the season number or episode number with zeros until they are the same length
    while not (len(season_num_str) == len(episode_num_str)):
        #pad episode number when season number is longer
        if (len(episode_num_str) < len(season_num_str)):
            episode_num_str = '0' + episode_num_str
        #pad season number when episode number is longer
        elif (len(episode_num_str) > len(season_num_str)):
            season_num_str = '0' + season_num_str

    #Format the season and episode into something easily readable (i.e. s01.e23)
    formatted_season_episode = 's' + season_num_str + '.e' + episode_num_str

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\nSeason # is: ' + str(ParentIndexNumber),2,the_dict)
        appendTo_DEBUG_log('\nEpisode # is: ' + str(IndexNumber),2,the_dict)
        appendTo_DEBUG_log('\nPadded Season #: ' + season_num_str,2,the_dict)
        appendTo_DEBUG_log('\nPadded Episode #: ' + episode_num_str,2,the_dict)
        appendTo_DEBUG_log('\nFormatted season#.episode# is: ' + str(formatted_season_episode),2,the_dict)

    return(formatted_season_episode)


#get disk and track numbers; pad with zeros to make them equal lengths
def get_disk_track(ParentIndexNumber,IndexNumber,the_dict):
    return get_season_episode(ParentIndexNumber,IndexNumber,the_dict).replace('s', 'd', 1).replace('e', 't', 1)