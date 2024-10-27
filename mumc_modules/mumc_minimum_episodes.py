from collections import defaultdict
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_item_info import get_ADDITIONAL_itemInfo,get_SERIES_itemInfo


#Minimum episodes and minimum played episodes control
class minEpisodesToKeep_data_handler:
    #Initialize and define minEpisodesToKeep variables
    def __init__(self,postproc_dict,the_dict):
        self.the_dict=the_dict
        self.postproc_dict=postproc_dict
        self.episodeCounts_byUserId=postproc_dict['mediaCounts_byUserId']
        self.deleteItems=postproc_dict['deleteItems']
        self.deleteItems_Tracker=postproc_dict['deleteItems_Tracker']

        self.users_info = self.postproc_dict['enabled_users']
        self.minimum_number_episodes = self.postproc_dict['minimum_number_episodes']
        self.minimum_number_played_episodes = self.postproc_dict['minimum_number_played_episodes']
        self.minimum_number_episodes_behavior = self.postproc_dict['minimum_number_episodes_behavior']

        self.minimum_number_episodes_behavior_modified = self.minimum_number_episodes_behavior.casefold().replace(' ','')

        self.episodes_toBeDeletedOrRemain={}
        self.episodeTracker={}
        self.min_num_episode_behavior = 0
        self.username_userid_match = False

        self.episodesToKeepIds = []

        #Define dictionary of different behavior types
        self.behaviorTypes={
                    'username':1,
                    'userid':2,
                    'maxplayed':3,
                    'maxplayedmaxplayed':3,
                    'minplayed':4,
                    'minplayedminplayed':4,
                    'maxunplayed':5,
                    'maxunplayedmaxunplayed':5,
                    'minunplayed':6,
                    'minunplayedminunplayed':6,
                    'maxplayedmaxunplayed':7,
                    'minplayedminunplayed':8,
                    'maxplayedminunplayed':9,
                    'minplayedmaxunplayed':10,
                    'minunplayedminplayed':11,
                    'minunplayedmaxunplayed':12,
                    'minunplayedmaxplayed':13,
                    'minplayedmaxplayed':14,
                    'maxunplayedminunplayed':15,
                    'maxunplayedminplayed':16,
                    'maxunplayedmaxplayed':17,
                    'maxplayedminplayed':18,
                    'defaultbehavior':8
                    }
        #Put behavior type keys into a list
        self.behaviorTypesKeys_List=list(self.behaviorTypes.keys())

        #minimum_number_episodes must be > minimum_number_played_episodes
        if (self.minimum_number_played_episodes > self.minimum_number_episodes):
            if (not (self.minimum_number_episodes == 0)):
                self.minimum_number_episodes = self.minimum_number_played_episodes


    #Build a dictionary to track episode information for each seriesId by userId
    def trackEpisodes_byUserId(self):
        #loop thru userIds
        for userId in self.episodeCounts_byUserId:
            for user_info_entry in self.users_info:
                if (userId == user_info_entry['user_id']):
                    user_info=user_info_entry
                    break
            #loop thru list of items to be deleted
            for episodeItem in self.deleteItems:
                #verify media item is an episode
                if (episodeItem['Type'] == 'Episode'):
                    #check if the seriesId associated to the episode was tracked during during get_mediaItems() for this user
                    if (episodeItem['SeriesId'] in self.episodeCounts_byUserId[userId]):
                        #if seriesId has not already processed; add it so it can be
                        if (not (episodeItem['SeriesId'] in self.episodes_toBeDeletedOrRemain)):
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']]={}
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']]['SeriesName'] = self.episodeCounts_byUserId[userId][episodeItem['SeriesId']]['SeriesName']
                        #if userId has not already been processed; add it so it can be
                        if (not (userId in self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']])):
                            #gather information needed to determine how many played and unplayed episodes may be deleted
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]={}
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['PlayedToBeDeleted'] = 0
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedToBeDeleted'] = 0
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['TotalEpisodeCount'] = self.episodeCounts_byUserId[userId][episodeItem['SeriesId']]['TotalEpisodeCount']
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['PlayedEpisodeCount'] = self.episodeCounts_byUserId[userId][episodeItem['SeriesId']]['PlayedEpisodeCount']
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedEpisodeCount'] = self.episodeCounts_byUserId[userId][episodeItem['SeriesId']]['UnplayedEpisodeCount']

                        if (('mumc' in episodeItem) and ('lib_id' in episodeItem['mumc']) and (episodeItem['mumc']['lib_id'] in self.the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):
                            #increment for played or unplayed episode counts that may be deleted
                            if (get_ADDITIONAL_itemInfo(user_info,episodeItem['Id'],'finding minEpisodesToKeep() play state',self.the_dict)['UserData']['Played']):
                                self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['PlayedToBeDeleted'] += 1
                            else:
                                self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedToBeDeleted'] += 1
                        else:
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedToBeDeleted'] += 1
                    else:
                        if (episodeItem['mumc']['lib_id'] in self.the_dict['byUserId_accessibleLibraries'][userId]):
                            #manually build any missing season and episode information for user's who did not meet the filter criteria
                            series_info = get_SERIES_itemInfo(episodeItem,user_info,self.the_dict)
                        else:
                            for this_user_id in self.the_dict['byUserId_accessibleLibraries']:
                                if (episodeItem['mumc']['lib_id'] in self.the_dict['byUserId_accessibleLibraries'][this_user_id]):
                                    break
                            for found_user_info in self.users_info:
                                if (this_user_id == found_user_info['user_id']):
                                    #manually build any missing season and episode information for user's who did meet the filter criteria
                                    series_info = get_SERIES_itemInfo(episodeItem,found_user_info,self.the_dict)
                                    break

                            series_info['UserData']['PlayedPercentage']=None
                            series_info['UserData']['UnplayedItemCount']=series_info['RecursiveItemCount']
                            series_info['UserData']['PlaybackPositionTicks']=None
                            series_info['UserData']['PlayCount']=None
                            series_info['UserData']['IsFavorite']=None
                            series_info['UserData']['Played']=None
                            series_info['UserData']['Key']=None

                        #if seriesId has not already processed; add it so it can be
                        if (not (series_info['Id'] in self.episodes_toBeDeletedOrRemain)):
                            self.episodes_toBeDeletedOrRemain[series_info['Id']]={}
                            self.episodes_toBeDeletedOrRemain[series_info['Id']]['SeriesName'] = self.episodeCounts_byUserId[userId][series_info['Id']]['SeriesName']
                        #if userId has not already been processed; add it so it can be
                        if (not (userId in self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']])):
                            #gather information needed to determine how many played and unplayed episodes may be deleted
                            self.episodes_toBeDeletedOrRemain[series_info['Id']][userId]={}
                            self.episodes_toBeDeletedOrRemain[series_info['Id']][userId]['PlayedToBeDeleted'] = 0
                            self.episodes_toBeDeletedOrRemain[series_info['Id']][userId]['UnplayedToBeDeleted'] = 0
                            RecursiveItemCount=int(series_info['RecursiveItemCount'])
                            UnplayedItemCount=int(series_info['UserData']['UnplayedItemCount'])
                            PlayedEpisodeCount=RecursiveItemCount - UnplayedItemCount
                            self.episodes_toBeDeletedOrRemain[series_info['Id']][userId]['TotalEpisodeCount'] = RecursiveItemCount
                            self.episodes_toBeDeletedOrRemain[series_info['Id']][userId]['PlayedEpisodeCount'] = PlayedEpisodeCount
                            self.episodes_toBeDeletedOrRemain[series_info['Id']][userId]['UnplayedEpisodeCount'] = UnplayedItemCount

                        if (('mumc' in episodeItem) and ('lib_id' in episodeItem['mumc']) and (episodeItem['mumc']['lib_id'] in self.the_dict['byUserId_accessibleLibraries'][user_info['user_id']])):
                            #increment for played or unplayed episode counts that may be deleted
                            if (get_ADDITIONAL_itemInfo(user_info,episodeItem['Id'],'finding minEpisodesToKeep() play state',self.the_dict)['UserData']['Played']):
                                self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['PlayedToBeDeleted'] += 1
                            else:
                                self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedToBeDeleted'] += 1
                        else:
                            self.episodes_toBeDeletedOrRemain[episodeItem['SeriesId']][userId]['UnplayedToBeDeleted'] += 1


    #loop thru seriesIds we stored in the loop above and determine the number of played to remain and unplayed ot remain for each series under each user
    def determine_playedUnplayedToRemain(self):
        for seriesId in self.episodes_toBeDeletedOrRemain:
            #loop thru the userIds under each seriesId
            for userId in self.episodes_toBeDeletedOrRemain[seriesId]:
                #ignore if this value
                if (not (userId == 'SeriesName')):
                    #determine the number of played and unplayed episodes for this series that will remain specifically for this user
                    self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] = self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedEpisodeCount'] - self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                    self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain'] = self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedEpisodeCount'] - self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted']

                    #check if the number of remaining played episodes is less than or equal to the minimum_number_played_episodes
                    if (self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] <= self.minimum_number_played_episodes):
                        #get the number of played episodes we will need to meet the requested minimum_number_played_episodes
                        episode_gap = self.minimum_number_played_episodes - self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain']
                        #check if the needed number of played episodes to meet the requested minimum_number_played_episodes is available for this user
                        if (self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] >= episode_gap):
                            #we have enough to fill the gap; increase the number of played episodes to remain; decrease the number of played episodes to be deleted by the delta
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] += episode_gap
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] -= episode_gap
                        #when there are not enough played episodes to meet the requested minimum_number_played_episodes
                        else: #(episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] < episode_gap):
                            #take everything there is; to increase the number of played episodes to remain as much as possible and to decrease the number of played episodes to be deleted by the same amount
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] += self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                            #episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] -= episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] = 0

                    #determine the total number of remaining episodes both played and unplayed
                    total_remaining = self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] + self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain']
                    #check if total_remaining meets the requested minimum_number_episodes
                    if (total_remaining <= self.minimum_number_episodes):
                        #determine the number of episodes needed to fill the gap
                        episode_gap = self.minimum_number_episodes - total_remaining
                        #check if the needed number of unplayed episodes to meet the request minimum_number_episodes is available for this user
                        if (self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] >= episode_gap):
                            #we have enough to fill the gap; increase the number of unplayed episodes to remain; decrease the number of unplayed episodes to be deleted by the delta
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain'] += episode_gap
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] -= episode_gap
                        #when there are not enough unplayed episodes to meet the requested minimum_number_episodes
                        else: #(episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] < episode_gap):
                            #take everything there is; increase the number of unplayed episodes to remain as much as possible and decrease the number of unplayed episodes to be deleted by the same amount
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain'] += self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted']
                            #episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] -= episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted']
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToBeDeleted'] = 0

                    #determine the total number of remaining episodes both played and unplayed
                    total_remaining = self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] + self.episodes_toBeDeletedOrRemain[seriesId][userId]['UnplayedToRemain']
                    #check if total_remaining meets the requested minimum_number_episodes
                    if (total_remaining < self.minimum_number_episodes):
                        #determine the number of episodes needed to fill the gap
                        episode_gap = self.minimum_number_episodes - total_remaining
                        #check if the needed number of played episodes to meet the request minimum_number_episodes is available for this user
                        if (self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] >= episode_gap):
                            #we have enough to fill the gap; increase the number of played episodes to remain; decrease the number of played episodes to be deleted by the delta
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] += episode_gap
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] -= episode_gap
                        #when there are not enough played episodes to meet the requested minimum_number_episodes
                        else: #(episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] >= episode_gap):
                            #take everything there is; increase number of played episodes to remain as much as possible and decrease the number of played episodes to be deleted by the same amount
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToRemain'] += self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                            #episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] -= episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted']
                            self.episodes_toBeDeletedOrRemain[seriesId][userId]['PlayedToBeDeleted'] = 0


    #loop thru each item in the list of items that may be deleted
    def buildSeason_byEpisodeGrid(self):
        for deleteItem in self.deleteItems:
            #verify media item is an episode
            if (deleteItem['Type'] == 'Episode'):
                #add seriesid to episode tracker if it does not already exist
                if (not (deleteItem['SeriesId'] in self.episodeTracker)):
                    self.episodeTracker[deleteItem['SeriesId']]={}
                #gather information needed to build grid to determine season and episode order of each series
                if (not (deleteItem['Id'] in self.episodeTracker[deleteItem['SeriesId']])):
                    if (not ('SeriesName' in self.episodeTracker[deleteItem['SeriesId']])):
                        self.episodeTracker[deleteItem['SeriesId']]['SeriesName'] = self.episodes_toBeDeletedOrRemain[deleteItem['SeriesId']]['SeriesName']
                    if (not ('MaxSeason' in self.episodeTracker[deleteItem['SeriesId']])):
                        self.episodeTracker[deleteItem['SeriesId']]['MaxSeason'] = 0
                    if (not ('MaxEpisode' in self.episodeTracker[deleteItem['SeriesId']])):
                        self.episodeTracker[deleteItem['SeriesId']]['MaxEpisode'] = 0

                    if (self.the_dict['DEBUG']):
                        #Check if string or integer
                        if (isinstance(deleteItem['Id'],str)):
                            appendTo_DEBUG_log('\n\ndeleteItem[\'Id\'] : Is String',3,self.the_dict)
                        elif (isinstance(deleteItem['Id'],int)):
                            appendTo_DEBUG_log('\n\ndeleteItem[\'Id\'] : Is Integer',3,self.the_dict)
                        appendTo_DEBUG_log('\n\ndeleteItem[\'Id\'] = ' + str(deleteItem['Id']),3,self.the_dict)

                        #Check if string or integer
                        if (isinstance(deleteItem['ParentIndexNumber'],str)):
                            appendTo_DEBUG_log('\ndeleteItem[\'ParentIndexNumber\'] : Is String',3,self.the_dict)
                            try:
                                deleteItem['ParentIndexNumber'] = int(deleteItem['ParentIndexNumber'])
                                appendTo_DEBUG_log('\ndeleteItem[\'ParentIndexNumber\'] Converted : Is Now Integer',3,self.the_dict)
                            except:
                                appendTo_DEBUG_log('\ndeleteItem[\'ParentIndexNumber\'] Not Coverted : Skipping This Item',3,self.the_dict)
                        elif (isinstance(deleteItem['ParentIndexNumber'],int)):
                            appendTo_DEBUG_log('\ndeleteItem[\'ParentIndexNumber\'] : Is Integer',3,self.the_dict)
                        appendTo_DEBUG_log('\ndeleteItem[\'ParentIndexNumber\'] = ' + str(deleteItem['ParentIndexNumber']),3,self.the_dict)

                        #Check if string or integer
                        if (isinstance(deleteItem['SeriesId'],str)):
                            appendTo_DEBUG_log('\ndeleteItem[\'SeriesId\'] : Is String',3,self.the_dict)
                        elif (isinstance(deleteItem['SeriesId'],int)):
                            appendTo_DEBUG_log('\ndeleteItem[\'SeriesId\'] : Is Integer',3,self.the_dict)
                        appendTo_DEBUG_log('\ndeleteItem[\'SeriesId\'] = ' + str(deleteItem['SeriesId']),3,self.the_dict)

                        #Check if string or integer
                        if (isinstance(self.episodeTracker[deleteItem['SeriesId']]['MaxSeason'],str)):
                            appendTo_DEBUG_log('\nepisodeTracker[deleteItem[\'SeriesId\']][\'MaxSeason\'] : Is String',3,self.the_dict)
                        elif (isinstance(self.episodeTracker[deleteItem['SeriesId']]['MaxSeason'],int)):
                            appendTo_DEBUG_log('\nepisodeTracker[deleteItem[\'SeriesId\']][\'MaxSeason\'] : Is Integer',3,self.the_dict)
                        appendTo_DEBUG_log('\nepisodeTracker[deleteItem[\'SeriesId\']][\'MaxSeason\'] = ' + str(self.episodeTracker[deleteItem['SeriesId']]['MaxSeason']),3,self.the_dict)

                    try:
                        #Check if string or integer
                        if (isinstance(deleteItem['ParentIndexNumber'],str)):
                            deleteItem['ParentIndexNumber'] = int(deleteItem['ParentIndexNumber'])
                        if (deleteItem['ParentIndexNumber'] > self.episodeTracker[deleteItem['SeriesId']]['MaxSeason']):
                            self.episodeTracker[deleteItem['SeriesId']]['MaxSeason'] = deleteItem['ParentIndexNumber']

                        #Check if string or integer
                        if (isinstance(deleteItem['IndexNumber'],str)):
                            deleteItem['IndexNumber'] = int(deleteItem['IndexNumber'])
                        if (deleteItem['IndexNumber'] > self.episodeTracker[deleteItem['SeriesId']]['MaxEpisode']):
                            self.episodeTracker[deleteItem['SeriesId']]['MaxEpisode'] = deleteItem['IndexNumber']

                        #create dictionary entry containg season and episode number for each episode
                        self.episodeTracker[deleteItem['SeriesId']][deleteItem['Id']]=defaultdict(dict)
                        self.episodeTracker[deleteItem['SeriesId']][deleteItem['Id']][deleteItem['ParentIndexNumber']]=deleteItem['IndexNumber']
                    except:
                        appendTo_DEBUG_log('\nItem[\'Id\'] : ' + str(deleteItem['Id']) + ' Skipped likley due to ParentIndexNumber ' + str(deleteItem['ParentIndexNumber']) + ' Not Being An Integer.',3,self.the_dict)
                        appendTo_DEBUG_log('\nItem[\'Id\'] : ' + str(deleteItem['Id']) + ' Skipped likley due to IndexNumber ' + str(deleteItem['IndexNumber']) + ' Not Being An Integer.',3,self.the_dict)

        #loop thru each series in the episode tracker and build a season x episode grid
        for seriesId in self.episodeTracker:
            #create an season x episode grid for each series
            self.episodeTracker[seriesId]['SeasonEpisodeGrid'] = [[''] * (self.episodeTracker[seriesId]['MaxEpisode'] + 1) for _ in range(self.episodeTracker[seriesId]['MaxSeason'] + 1)]

            #loop thru each episode for the series
            for episodeId in self.episodeTracker[seriesId]:
                #ignore non-essential data
                if (not ((episodeId == 'SeriesName') or (episodeId == 'MaxSeason') or (episodeId == 'MaxEpisode') or (episodeId == 'SeasonEpisodeGrid'))):
                    #get the key for this entry, which is the season number as the first element of a list
                    seasonNum=list(self.episodeTracker[seriesId][episodeId].keys())[0]
                    #use the season number and the value from the season number key (aka episode number) to save the episodeId in the correct grid position
                    self.episodeTracker[seriesId]['SeasonEpisodeGrid'][seasonNum][self.episodeTracker[seriesId][episodeId][seasonNum]]=episodeId


    #check if minimum_number_episodes_behavior is equal to any of the behaviorType keys
    def determine_minimumEpisodeBehavioralType(self):
        if (self.minimum_number_episodes_behavior_modified in self.behaviorTypesKeys_List):
            self.min_num_episode_behavior = self.behaviorTypes[self.minimum_number_episodes_behavior_modified]
        #check if minimum_number_episodes_behavior is a userName or userId
        else:
            #loop thru userNames:userIds
            for userInfo in self.users_info:
                #check if match has already been made
                if (self.username_userid_match == False):
                    #split userName and userId into a list
                    userName=userInfo['user_name']
                    userId=userInfo['user_id']
                    #make possible userName strings to be compared case insensitive
                    if (userName.casefold() == self.minimum_number_episodes_behavior.casefold()):
                        #userName match found
                        self.min_num_episode_behavior = self.behaviorTypes['username']
                        break
                    #make possible userId strings to be compared case insensitive
                    if (userId.casefold() == self.minimum_number_episodes_behavior.casefold()):
                        #userId match found
                        self.min_num_episode_behavior = self.behaviorTypes['userid']
                        break
            #check if behavior set to userName or userId
            if (self.min_num_episode_behavior in range(self.behaviorTypes['username'],(self.behaviorTypes['userid']+1))):
                #loop thru each series
                for seriesId in self.episodes_toBeDeletedOrRemain:
                    #determine played and unplayed numbers specifically for this user
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = userInfo
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = userInfo
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][userInfo['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][userInfo['user_id']]['UnplayedToBeDeleted']
                #make sure we got here without matching a userName or userId
                if (self.username_userid_match == False):
                    #if we did; prep for using the default behavior
                    self.min_num_episode_behavior = 0
            #check if we made it this far without a match; if we did use the default behavior
            if (self.min_num_episode_behavior == 0):
                self.min_num_episode_behavior = self.behaviorTypes['defaultbehavior']


    #check if the desired behavior falls within the max/min played/unplayed ranges
    def calc_userSpecificBehavioralTypeData(self):
        if (self.min_num_episode_behavior in range(self.behaviorTypes['maxplayed'],(self.behaviorTypes['maxplayedminplayed']+1))):
            #create lists to keep track of the user with the min/max played/unplayed number of episodes (first user with min/max value wins)
            maxPlayed_ToBeDeleted=['',-1]
            minPlayed_ToBeDeleted=['',-1]
            maxUnplayed_ToBeDeleted=['',-1]
            minUnplayed_ToBeDeleted=['',-1]
            #loop thru each series
            for seriesId in self.episodes_toBeDeletedOrRemain:
                #loop thru each user
                for userId in self.episodes_toBeDeletedOrRemain[seriesId]:
                    user_enabled = False
                    if (not (userId == 'SeriesName')):
                        for users_info in self.postproc_dict['enabled_users']:
                            if (userId == users_info['user_id']):
                                #user_info=users_info
                                user_enabled = True
                                break
                        if (user_enabled):
                            #store value if greater than last
                            if (self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['PlayedToBeDeleted'] > maxPlayed_ToBeDeleted[1]):
                                maxPlayed_ToBeDeleted[1]=self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['PlayedToBeDeleted']
                                maxPlayed_ToBeDeleted[0]=users_info

                                #initialize minimum value as max
                                if (minPlayed_ToBeDeleted[1] == -1):
                                    minPlayed_ToBeDeleted[1]=self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['PlayedToBeDeleted']
                                    minPlayed_ToBeDeleted[0]=users_info

                            #store value if greater than last
                            if (self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['UnplayedToBeDeleted'] > maxUnplayed_ToBeDeleted[1]):
                                maxUnplayed_ToBeDeleted[1]=self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['UnplayedToBeDeleted']
                                maxUnplayed_ToBeDeleted[0]=users_info

                                #initialize minimum value as max
                                if (minUnplayed_ToBeDeleted[1] == -1):
                                    minUnplayed_ToBeDeleted[1]=self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['UnplayedToBeDeleted']
                                    minUnplayed_ToBeDeleted[0]=users_info

                            #store value if less than last
                            if (self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['PlayedToBeDeleted'] < minPlayed_ToBeDeleted[1]):
                                minPlayed_ToBeDeleted[1]=self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['PlayedToBeDeleted']
                                minPlayed_ToBeDeleted[0]=users_info

                            #store value if less than last
                            if (self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['UnplayedToBeDeleted'] < minUnplayed_ToBeDeleted[1]):
                                minUnplayed_ToBeDeleted[1]=self.episodes_toBeDeletedOrRemain[seriesId][users_info['user_id']]['UnplayedToBeDeleted']
                                minUnplayed_ToBeDeleted[0]=users_info

                #check for desired behaviorType; assign min/max played/unplayed values for each series depending on behaviorType
                if (self.min_num_episode_behavior == self.behaviorTypes['maxplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = maxPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = maxPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['minplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = minPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = minPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['maxunplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = maxUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = maxUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['minunplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = minUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = minUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['maxplayedmaxunplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = maxPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = maxUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['minplayedminunplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = minPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = minUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['maxplayedminunplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = maxPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = minUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['minplayedmaxunplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = minPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = maxUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['minunplayedminplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = minUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = minPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['minunplayedmaxunplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = minUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = maxUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['minunplayedmaxplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = minUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = maxPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['minplayedmaxplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = minPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = maxPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['maxunplayedminunplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = maxUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = minUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minUnplayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['maxunplayedminplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = maxUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = minPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['maxunplayedmaxplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = maxUnplayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = maxPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxUnplayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']
                elif (self.min_num_episode_behavior == self.behaviorTypes['maxplayedminplayed']):
                    self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'] = maxPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'] = minPlayed_ToBeDeleted[0]
                    self.episodeTracker[seriesId]['PlayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][maxPlayed_ToBeDeleted[0]['user_id']]['PlayedToBeDeleted']
                    self.episodeTracker[seriesId]['UnplayedToBeDeleted'] = self.episodes_toBeDeletedOrRemain[seriesId][minPlayed_ToBeDeleted[0]['user_id']]['UnplayedToBeDeleted']


    def find_playedEpisodesToKeep(self):
        #loop thru each series
        for seriesId in self.episodeTracker:
            #manually set seasonNumIndex from the season x episode grid because episodeTracker[seriesId]['SeasonEpisodeGrid'].index(seasonNumIndex) returns false positives when more than one season index is full of ''
            seasonNumIndex = 0
            #loop thru each season in the season x episode grid
            for _ in self.episodeTracker[seriesId]['SeasonEpisodeGrid']:
                #loop thru each episode position in the season x episode grid
                for episodeId in self.episodeTracker[seriesId]['SeasonEpisodeGrid'][seasonNumIndex]:
                    #check if episode is not populated for this position of the season x episode grid
                    if (not (episodeId == '')):
                        #check if episodeId is in the list of items to be deleted
                        if (episodeId in self.deleteItems_Tracker):
                            #get the index of this episodeId from deleteItems_Tracker
                            episode_index=self.deleteItems_Tracker.index(episodeId)
                            #verify this index matches the same episode and position in deleteItems list
                            if (episodeId == self.deleteItems[episode_index]['Id']):
                                #veriy this use has access to the library this episode is in
                                if (self.deleteItems[episode_index]['mumc']['lib_id'] in self.the_dict['byUserId_accessibleLibraries'][self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo']['user_id']]):
                                    #get played status for specified episodeId
                                    played_status=get_ADDITIONAL_itemInfo(self.episodeTracker[seriesId]['PlayedToBeDeleted_UserInfo'],episodeId,'filtering episode tracker grid for played item',self.the_dict)
                                    #verify info was returned and episode is played
                                    if ((not (played_status == False)) and played_status['UserData']['Played']):
                                        #are the expected number of played episodes to be deleted > 0
                                        if (self.episodeTracker[seriesId]['PlayedToBeDeleted'] > 0):
                                            #decrement the expected number of played episodes to be deleted by 1
                                            self.episodeTracker[seriesId]['PlayedToBeDeleted'] -= 1
                                        else: #verify the expected number of played episodes to be deleted is == 0
                                            #check if episodeId is already in the list of episodeIds to be kept
                                            if (not (episodeId in self.episodesToKeepIds)):
                                                #add this episodeId to the list of episodeIds to be removed from the delete list later
                                                self.episodesToKeepIds.append(episodeId)
                seasonNumIndex += 1    


    def find_unplayedEpisodesToKeep(self):
        #loop thru each series
        for seriesId in self.episodeTracker:
            #manually set seasonNumIndex from the season x episode grid because episodeTracker[seriesId]['SeasonEpisodeGrid'].index(seasonNumIndex) returns false positives when more than one season index is full of ''
            seasonNumIndex = 0
            #loop thru each season in the season x episode grid
            for _ in self.episodeTracker[seriesId]['SeasonEpisodeGrid']:
                #loop thru each episode position in the season x episode grid
                for episodeId in self.episodeTracker[seriesId]['SeasonEpisodeGrid'][seasonNumIndex]:
                    #check if episode is not populated for this position of the season x episode grid
                    if (not (episodeId == '')):
                        #check if episodeId is in the list of items to be deleted
                        if (episodeId in self.deleteItems_Tracker):
                            #get the index of this episodeId from deleteItems_Tracker
                            episode_index=self.deleteItems_Tracker.index(episodeId)
                            #verify this index matches the same episode and position in deleteItems list
                            if (episodeId == self.deleteItems[episode_index]['Id']):
                                #veriy this use has access to the library this episode is in
                                if (self.deleteItems[episode_index]['mumc']['lib_id'] in self.the_dict['byUserId_accessibleLibraries'][self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo']['user_id']]):
                                    #get unplayed status for specified episodeId
                                    unplayed_status=get_ADDITIONAL_itemInfo(self.episodeTracker[seriesId]['UnplayedToBeDeleted_UserInfo'],episodeId,'filtering episode tracker grid for unplayed item',self.the_dict)
                                    #verify info was returned and episode is unplayed
                                    if ((not (unplayed_status == False)) and (not unplayed_status['UserData']['Played'])):
                                        #are the expected number of unplayed episodes to be deleted > 0
                                        if (self.episodeTracker[seriesId]['UnplayedToBeDeleted'] > 0):
                                            #decrement the expected number of unplayed episodes to be deleted by 1
                                            self.episodeTracker[seriesId]['UnplayedToBeDeleted'] -= 1
                                        else: #verify the expected number of unplayed episodes to be deleted is == 0
                                            #check if episodeId is already in the list of episodeIds to be kept
                                            if (not (episodeId in self.episodesToKeepIds)):
                                                #add this episodeId to the list of episodeIds to be removed from the delete list later
                                                self.episodesToKeepIds.append(episodeId)
                seasonNumIndex += 1


    def remove_episodesToKeepFromDeleteList(self,postproc_dict):
        #loop thru each series
        for episodeId in self.episodesToKeepIds:
            #loop while the number of instances of episodeId in the deleteItems_Tracker is > 0
            while self.deleteItems_Tracker.count(episodeId):
                #remove this episodeId from the deleteItems list
                self.deleteItems.pop(self.deleteItems_Tracker.index(episodeId))
                #remove this episodeId from the deleteItems_Tracker list
                self.deleteItems_Tracker.remove(episodeId)

        #update with the modifed deleteItems list
        postproc_dict['deleteItems']=self.deleteItems
        #update with the modifed deleteItems_Tracker list
        postproc_dict['deleteItems_Tracker']=self.deleteItems_Tracker

        return postproc_dict