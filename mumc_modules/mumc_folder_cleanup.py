from mumc_modules.mumc_user_queries import get_all_users
from mumc_modules.mumc_console_info import print_and_delete_items
from mumc_modules.mumc_get_folders import init_empty_folder_query,empty_folder_query


def get_admin_user_id(the_dict):
    user_info={}
    user_all_libs_enabled_found=False
    userIds_list=[]
    libNums_list=[]
    if (the_dict['admin_settings']['server']['admin_id'] == None):
        data_all_users=get_all_users(the_dict)
        for user_info in data_all_users:
            if (user_info['Policy']['EnableAllFolders']):
                the_dict['admin_settings']['server']['admin_id']=user_info['Id']
                user_all_libs_enabled_found=True
                break
            else:
                userIds_list.append(user_info['Id'])
                libNums_list.append(len(user_info['Policy']['EnabledFolders']) - len(user_info['Policy']['ExcludedSubFolders']))

        if (user_all_libs_enabled_found == False):
            sorted_libNums_list=libNums_list.copy()
            sorted_libNums_list.sort(reverse=True)
            the_dict['admin_settings']['server']['admin_id']=userIds_list[libNums_list.index(sorted_libNums_list[0])]

    user_info['user_id']=the_dict['admin_settings']['server']['admin_id']

    return user_info

def get_empty_folders(folder_type,the_dict):
    var_dict={}
    var_dict['server_url']=the_dict['admin_settings']['server']['url']
    var_dict['media_type_lower']=folder_type.casefold()
    var_dict['media_type_upper']=folder_type.upper()
    var_dict['media_type_title']=folder_type.title()
    var_dict['server_brand']=the_dict['admin_settings']['server']['brand']
    var_dict['advanced_settings']={}
    var_dict['advanced_settings']['delete_empty_folders']={}
    var_dict['advanced_settings']['delete_empty_folders']['episode']={}
    var_dict['advanced_settings']['delete_empty_folders']['episode'][folder_type]=the_dict['advanced_settings']['delete_empty_folders']['episode'][folder_type]

    parentItems_Tracker=[]
    the_dict['parentDeleteItems']=[]
    if (not ('child_remaining' in the_dict)):
        the_dict['child_remaining']={}
    the_dict['pre_child_remaing']={}

    user_info=get_admin_user_id(the_dict)

    var_dict=init_empty_folder_query(var_dict)

    var_dict['QueryItemsRemaining_All']=True

    while (var_dict['QueryItemsRemaining_All']):
        var_dict=empty_folder_query(user_info,var_dict,the_dict)

        var_dict['QueryItemsRemaining_All']=var_dict['QueriesRemaining_Empty_Folder']

        for parentItem in var_dict['data_Empty_Folder']['Items']:
            try:
                seriesId=parentItem['SeriesId']
            except:
                seriesId=parentItem['ParentId']
            #When season look for parents with no children; add them to the delete list
            #When season/series and REMOVE_FILES is True look for parents with no children; add them to the delete list
            if (the_dict['advanced_settings']['REMOVE_FILES']):
                if (not (parentItem == None)):
                    if ('ChildCount' in parentItem):
                        if (int(parentItem['ChildCount']) == 0):
                            if (parentItem['Id'] in parentItems_Tracker):
                                parent_item_index=parentItems_Tracker.index(parentItem['Id'])
                                the_dict['parentDeleteItems'][parent_item_index]=parentItem
                            else:
                                parentItems_Tracker.append(parentItem['Id'])
                                the_dict['parentDeleteItems'].append(parentItem)
                            if (seriesId in the_dict['child_remaining']):
                                the_dict['child_remaining'][seriesId]+=1
                            else:
                                the_dict['child_remaining'][seriesId]=1
            #When season/series and REMOVE_FILES is False simulate looking for parents with no children; adding them to the delete list
            else:
                if (not (parentItem == None)):
                    if ('ChildCount' in parentItem):
                        if (not (parentItem['Id'] in parentItems_Tracker)):
                            parentItems_Tracker.append(parentItem['Id'])
                        if (parentItem['Id'] in the_dict['child_remaining']):
                            the_dict['child_remaining'][parentItem['Id']]=parentItem['ChildCount'] - the_dict['child_remaining'][parentItem['Id']]
                            if (the_dict['child_remaining'][parentItem['Id']] == 0):
                                the_dict['parentDeleteItems'].append(parentItem)
                                if (seriesId in the_dict['pre_child_remaing']):
                                    the_dict['pre_child_remaing'][seriesId]+=1
                                else:
                                    the_dict['pre_child_remaing'][seriesId]=1

    the_dict['child_remaining']=the_dict['pre_child_remaing']

    return the_dict


def track_episodes_when_REMOVE_FILES_false(deleteItems,the_dict):
    if (not (the_dict['advanced_settings']['REMOVE_FILES'])):
        the_dict['child_remaining']={}
        episodeTracker=[]
        for item in deleteItems:
            if (item['Type'] == 'Episode'):
                if (not (item['Id'] in episodeTracker)):
                    episodeTracker.append(item['Id'])
                    seasonId=None
                    try:
                        seasonId=item['SeasonId']
                    except:
                        seasonId=item['ParentId']
                    if (seasonId in the_dict['child_remaining']):
                        the_dict['child_remaining'][seasonId]+=1
                    else:
                        the_dict['child_remaining'][seasonId]=1

    return the_dict


def season_series_folder_cleanup(deleteItems,the_dict):

    the_dict=track_episodes_when_REMOVE_FILES_false(deleteItems,the_dict)

    #remove empty season folders
    if (the_dict['advanced_settings']['delete_empty_folders']['episode']['season']):
        the_dict=get_empty_folders('season',the_dict)

        print_and_delete_items(the_dict['parentDeleteItems'],the_dict,'Season Folders')

    #remove empty series folders
    if (the_dict['advanced_settings']['delete_empty_folders']['episode']['series']):
        the_dict=get_empty_folders('series',the_dict)

        print_and_delete_items(the_dict['parentDeleteItems'],the_dict,'Series Folders')