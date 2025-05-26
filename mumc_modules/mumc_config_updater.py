from mumc_modules.mumc_output import save_yaml_config
from mumc_modules.mumc_compare_items import keys_exist,keys_exist_return_value


def userLib_configurationUpdater(the_dict):

    for userInfo in the_dict['admin_settings']['users']:
        whitelist_libId_List=[]
        blacklist_libId_List=[]
        whitelist_pos_List=[]
        blacklist_pos_List=[]
        userIndex = the_dict['admin_settings']['users'].index(userInfo)
        for libInfo in the_dict['admin_settings']['users'][userIndex]['whitelist']:
            libIndex=the_dict['admin_settings']['users'][userIndex]['whitelist'].index(libInfo)
            whitelist_libId_List.append(the_dict['admin_settings']['users'][userIndex]['whitelist'][libIndex]['lib_id'])
        for libInfo in the_dict['admin_settings']['users'][userIndex]['blacklist']:
            libIndex=the_dict['admin_settings']['users'][userIndex]['blacklist'].index(libInfo)
            blacklist_libId_List.append(the_dict['admin_settings']['users'][userIndex]['blacklist'][libIndex]['lib_id'])

        whitelist_libId_List.reverse()
        for libInfo in whitelist_libId_List:
            libIndex=whitelist_libId_List.index(libInfo)
            if (whitelist_libId_List.count(whitelist_libId_List[libIndex]) > 1):
                whitelist_libId_List[libIndex]=None
        whitelist_libId_List.reverse()

        blacklist_libId_List.reverse()
        for libInfo in blacklist_libId_List:
            libIndex=blacklist_libId_List.index(libInfo)
            if (blacklist_libId_List.count(blacklist_libId_List[libIndex]) > 1):
                blacklist_libId_List[libIndex]=None
        blacklist_libId_List.reverse()

        for libId in whitelist_libId_List:
            if (libId == None):
                libIndex=whitelist_libId_List.index(libId)
                whitelist_pos_List.append(libIndex)
                whitelist_libId_List[libIndex]=0

        for libId in blacklist_libId_List:
            if (libId == None):
                libIndex=blacklist_libId_List.index(libId)
                blacklist_pos_List.append(libIndex)
                blacklist_libId_List[libIndex]=0

        for libIndex in reversed(whitelist_pos_List):
            the_dict['admin_settings']['users'][userIndex]['whitelist'].pop(libIndex)

        for libIndex in reversed(blacklist_pos_List):
            the_dict['admin_settings']['users'][userIndex]['blacklist'].pop(libIndex)

    return the_dict['admin_settings']['users']


def yaml_configurationUpdater(mem_dict,orig_dict={}):
    new_dict={}
    
    if (orig_dict=={}):
        new_dict['version']=mem_dict['version']
        try:
            new_dict['basic_settings']=mem_dict['basic_settings']
        except:
            pass
        try:
            new_dict['advanced_settings']=mem_dict['advanced_settings']
            if (not ((check:=keys_exist_return_value(mem_dict,'advanced_settings','REMOVE_FILES')) == None)):
                if (check):
                    new_dict['advanced_settings']['REMOVE_FILES']=False
        except:
            pass
        new_dict['admin_settings']=mem_dict['admin_settings']
        try:
            new_dict['DEBUG']=mem_dict['DEBUG']
        except:
            new_dict['DEBUG']=0
    else:
        new_dict['version']=orig_dict['version']
        try:
            new_dict['basic_settings']=orig_dict['basic_settings']
        except:
            pass
        try:
            new_dict['advanced_settings']=orig_dict['advanced_settings']
            if (not ((check:=keys_exist_return_value(orig_dict,'advanced_settings','REMOVE_FILES')) == None)):
                if (check):
                    new_dict['advanced_settings']['REMOVE_FILES']=False
        except:
            pass
        new_dict['admin_settings']={}
        try:
            try:
                #check if default value was NOT selected during updating
                if (mem_dict['admin_settings']['behavior']['list'] == 'whitelist'):
                    if (not (keys_exist(new_dict,'admin_settings','behavior'))):
                        new_dict['admin_settings']['behavior']={}
                    if (not (keys_exist(new_dict,'admin_settings','behavior','list'))):
                        new_dict['admin_settings']['behavior']['list']=None
                    new_dict['admin_settings']['behavior']['list']='whitelist'
                else:
                    #check if keys already exist in 
                    if (keys_exist(orig_dict,'admin_settings','behavior','list')):
                        if (not (keys_exist(new_dict,'admin_settings','behavior'))):
                            new_dict['admin_settings']['behavior']={}
                        if (not (keys_exist(new_dict,'admin_settings','behavior','list'))):
                            new_dict['admin_settings']['behavior']['list']=None
                        new_dict['admin_settings']['behavior']['list']=mem_dict['admin_settings']['behavior']['list']

                #before saving; reorder some keys for consistency
                new_dict['admin_settings']['behavior']['list']=new_dict['admin_settings']['behavior'].pop('list')
            except:
                pass

            try:
                #check if default value was NOT selected during updating
                if (mem_dict['admin_settings']['behavior']['matching'] == 'byPath'):
                    if (not (keys_exist(new_dict,'admin_settings','behavior'))):
                        new_dict['admin_settings']['behavior']={}
                    if (not (keys_exist(new_dict,'admin_settings','behavior','matching'))):
                        new_dict['admin_settings']['behavior']['matching']=None
                    new_dict['admin_settings']['behavior']['matching']='byPath'
                elif (mem_dict['admin_settings']['behavior']['matching'] == 'byNetworkPath'):
                    if (not (keys_exist(new_dict,'admin_settings','behavior'))):
                        new_dict['admin_settings']['behavior']={}
                    if (not (keys_exist(new_dict,'admin_settings','behavior','matching'))):
                        new_dict['admin_settings']['behavior']['matching']=None
                    new_dict['admin_settings']['behavior']['matching']='byNetworkPath'
                else:
                    #check if keys already exist in 
                    if (keys_exist(orig_dict,'admin_settings','behavior','matching')):
                        if (not (keys_exist(new_dict,'admin_settings','behavior'))):
                            new_dict['admin_settings']['behavior']={}
                        if (not (keys_exist(new_dict,'admin_settings','behavior','matching'))):
                            new_dict['admin_settings']['behavior']['matching']=None
                        new_dict['admin_settings']['behavior']['matching']=mem_dict['admin_settings']['behavior']['matching']

                #before saving; reorder some keys for consistency
                new_dict['admin_settings']['behavior']['matching']=new_dict['admin_settings']['behavior'].pop('matching')
            except:
                pass

            try:
                #check if default value was NOT selected during updating
                if (mem_dict['admin_settings']['behavior']['users']['monitor_disabled'] == False):
                    if (not (keys_exist(new_dict,'admin_settings','behavior'))):
                        new_dict['admin_settings']['behavior']={}
                    if (not (keys_exist(new_dict,'admin_settings','behavior','users'))):
                        new_dict['admin_settings']['behavior']['users']={}
                    if (not (keys_exist(new_dict,'admin_settings','behavior','users','monitor_disabled'))):
                        new_dict['admin_settings']['behavior']['users']['monitor_disabled']=None
                    new_dict['admin_settings']['behavior']['users']['monitor_disabled']=False
                else:
                    #check if keys already exist in 
                    if (keys_exist(orig_dict,'admin_settings','behavior','users','monitor_disabled')):
                        if (not (keys_exist(new_dict,'admin_settings','behavior'))):
                            new_dict['admin_settings']['behavior']={}
                        if (not (keys_exist(new_dict,'admin_settings','behavior','users'))):
                            new_dict['admin_settings']['behavior']['users']={}
                        if (not (keys_exist(new_dict,'admin_settings','behavior','users','monitor_disabled'))):
                            new_dict['admin_settings']['behavior']['users']['monitor_disabled']=None
                        new_dict['admin_settings']['behavior']['users']['monitor_disabled']=mem_dict['admin_settings']['behavior']['users']['monitor_disabled']

                #before saving; reorder some keys for consistency
                new_dict['admin_settings']['behavior']['users']=new_dict['admin_settings']['behavior'].pop('users')
            except:
                pass

            #new_dict['admin_settings']['behavior']=orig_dict['admin_settings']['behavior']
        except:
            pass
        new_dict['admin_settings']['server']=orig_dict['admin_settings']['server']

        new_dict['admin_settings']['users']=userLib_configurationUpdater(mem_dict)

        try:
            arr_in_orig_dict=False
            arr_in_mem_dict=False
            #check if media_managers in orig_dict['admin_settings']
            if ('media_managers' in orig_dict['admin_settings']):
                #check if radarr in orig_dict['admin_settings']['media_managers']
                if ('radarr' in orig_dict['admin_settings']['media_managers']):
                    #check if orig_dict['admin_settings']['media_managers']['radarr'] is an empty list
                    if (not (orig_dict['admin_settings']['media_managers']['radarr'] == [])):
                        #set orig_dict has values
                        arr_in_orig_dict=True
            #check if media_managers in mem_dict['admin_settings']
            if ('media_managers' in mem_dict['admin_settings']):
                #check if radarr in mem_dict['admin_settings']['media_managers']
                if ('radarr' in mem_dict['admin_settings']['media_managers']):
                    #check if mem_dict['admin_settings']['media_managers']['radarr'] is the default value
                    if (not (mem_dict['admin_settings']['media_managers']['radarr'] == [{'enabled':True,'url':'','api_key':''}])):
                        #set mem_dict has values
                        arr_in_mem_dict=True

            #check if orig_dict['admin_settings']['media_managers']['radarr'] or mem_dict['admin_settings']['media_managers']['radarr'] have values
            if (arr_in_orig_dict or arr_in_mem_dict):
                #check if media_managers in new_dict['admin_settings']
                if (not ('media_managers' in new_dict['admin_settings'])):
                    #add media_managers key
                    new_dict['admin_settings']['media_managers']={}
                #check if radarr in new_dict['admin_settings']['media_managers']
                if (not ('radarr' in new_dict['admin_settings']['media_managers'])):
                    #add radarr key
                    new_dict['admin_settings']['media_managers']['radarr']=[]
                #save mem_dict['admin_settings']['media_managers']['radarr'] values to new_dict['admin_settings']['media_managers']['radarr']
                new_dict['admin_settings']['media_managers']['radarr']=mem_dict['admin_settings']['media_managers']['radarr']
        except:
            pass

        try:
            arr_in_orig_dict=False
            arr_in_mem_dict=False
            #check if media_managers in orig_dict['admin_settings']
            if ('media_managers' in orig_dict['admin_settings']):
                #check if sonarr in orig_dict['admin_settings']['media_managers']
                if ('sonarr' in orig_dict['admin_settings']['media_managers']):
                    #check if orig_dict['admin_settings']['media_managers']['sonarr'] is an empty list
                    if (not (orig_dict['admin_settings']['media_managers']['sonarr'] == [])):
                        #set orig_dict has values
                        arr_in_orig_dict=True
            #check if media_managers in mem_dict['admin_settings']
            if ('media_managers' in mem_dict['admin_settings']):
                #check if sonarr in mem_dict['admin_settings']['media_managers']
                if ('sonarr' in mem_dict['admin_settings']['media_managers']):
                    #check if mem_dict['admin_settings']['media_managers']['sonarr'] is the default value
                    if (not (mem_dict['admin_settings']['media_managers']['sonarr'] == [{'enabled':True,'url':'','api_key':''}])):
                        #set mem_dict has values
                        arr_in_mem_dict=True

            #check if orig_dict['admin_settings']['media_managers']['sonarr'] or mem_dict['admin_settings']['media_managers']['sonarr'] have values
            if (arr_in_orig_dict or arr_in_mem_dict):
                #check if media_managers in new_dict['admin_settings']
                if (not ('media_managers' in new_dict['admin_settings'])):
                    #add media_managers key
                    new_dict['admin_settings']['media_managers']={}
                #check if sonarr in new_dict['admin_settings']['media_managers']
                if (not ('sonarr' in new_dict['admin_settings']['media_managers'])):
                    #add sonarr key
                    new_dict['admin_settings']['media_managers']['sonarr']=[]
                #save mem_dict['admin_settings']['media_managers']['sonarr'] values to new_dict['admin_settings']['media_managers']['sonarr']
                new_dict['admin_settings']['media_managers']['sonarr']=mem_dict['admin_settings']['media_managers']['sonarr']
        except:
            pass

        try:
            arr_in_orig_dict=False
            arr_in_mem_dict=False
            #check if media_managers in orig_dict['admin_settings']
            if ('media_managers' in orig_dict['admin_settings']):
                #check if lidarr in orig_dict['admin_settings']['media_managers']
                if ('lidarr' in orig_dict['admin_settings']['media_managers']):
                    #check if orig_dict['admin_settings']['media_managers']['lidarr'] is an empty list
                    if (not (orig_dict['admin_settings']['media_managers']['lidarr'] == [])):
                        #set orig_dict has values
                        arr_in_orig_dict=True
            #check if media_managers in mem_dict['admin_settings']
            if ('media_managers' in mem_dict['admin_settings']):
                #check if lidarr in mem_dict['admin_settings']['media_managers']
                if ('lidarr' in mem_dict['admin_settings']['media_managers']):
                    #check if mem_dict['admin_settings']['media_managers']['lidarr'] is the default value
                    if (not (mem_dict['admin_settings']['media_managers']['lidarr'] == [{'enabled':True,'url':'','api_key':''}])):
                        #set mem_dict has values
                        arr_in_mem_dict=True

            #check if orig_dict['admin_settings']['media_managers']['lidarr'] or mem_dict['admin_settings']['media_managers']['lidarr'] have values
            if (arr_in_orig_dict or arr_in_mem_dict):
                #check if media_managers in new_dict['admin_settings']
                if (not ('media_managers' in new_dict['admin_settings'])):
                    #add media_managers key
                    new_dict['admin_settings']['media_managers']={}
                #check if lidarr in new_dict['admin_settings']['media_managers']
                if (not ('lidarr' in new_dict['admin_settings']['media_managers'])):
                    #add lidarr key
                    new_dict['admin_settings']['media_managers']['lidarr']=[]
                #save mem_dict['admin_settings']['media_managers']['lidarr'] values to new_dict['admin_settings']['media_managers']['lidarr']
                new_dict['admin_settings']['media_managers']['lidarr']=mem_dict['admin_settings']['media_managers']['lidarr']
        except:
            pass

        try:
            arr_in_orig_dict=False
            arr_in_mem_dict=False
            #check if media_managers in orig_dict['admin_settings']
            if ('media_managers' in orig_dict['admin_settings']):
                #check if readarr in orig_dict['admin_settings']['media_managers']
                if ('readarr' in orig_dict['admin_settings']['media_managers']):
                    #check if orig_dict['admin_settings']['media_managers']['readarr'] is an empty list
                    if (not (orig_dict['admin_settings']['media_managers']['readarr'] == [])):
                        #set orig_dict has values
                        arr_in_orig_dict=True
            #check if media_managers in mem_dict['admin_settings']
            if ('media_managers' in mem_dict['admin_settings']):
                #check if readarr in mem_dict['admin_settings']['media_managers']
                if ('readarr' in mem_dict['admin_settings']['media_managers']):
                    #check if mem_dict['admin_settings']['media_managers']['readarr'] is the default value
                    if (not (mem_dict['admin_settings']['media_managers']['readarr'] == [{'enabled':True,'url':'','api_key':''}])):
                        #set mem_dict has values
                        arr_in_mem_dict=True

            #check if orig_dict['admin_settings']['media_managers']['readarr'] or mem_dict['admin_settings']['media_managers']['readarr'] have values
            if (arr_in_orig_dict or arr_in_mem_dict):
                #check if media_managers in new_dict['admin_settings']
                if (not ('media_managers' in new_dict['admin_settings'])):
                    #add media_managers key
                    new_dict['admin_settings']['media_managers']={}
                #check if readarr in new_dict['admin_settings']['media_managers']
                if (not ('readarr' in new_dict['admin_settings']['media_managers'])):
                    #add readarr key
                    new_dict['admin_settings']['media_managers']['readarr']=[]
                #save mem_dict['admin_settings']['media_managers']['readarr'] values to new_dict['admin_settings']['media_managers']['readarr']
                new_dict['admin_settings']['media_managers']['readarr']=mem_dict['admin_settings']['media_managers']['readarr']
        except:
            pass

        try:
            new_dict['admin_settings']['api_controls']=orig_dict['admin_settings']['api_controls']
        except:
            pass
        try:
            new_dict['admin_settings']['cache']=orig_dict['admin_settings']['cache']
        except:
            pass
        try:
            new_dict['DEBUG']=mem_dict['DEBUG']
        except:
            new_dict['DEBUG']=0

    #save yaml config file
    save_yaml_config(new_dict,mem_dict['config_file_path'] / mem_dict['config_file_name_yaml'])