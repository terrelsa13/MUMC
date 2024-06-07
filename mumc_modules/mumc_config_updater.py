from mumc_modules.mumc_paths import save_yaml_config
from mumc_modules.mumc_compare_items import keys_exist,keys_exist_return_value

#TBD
def yaml_configurationUpdater(the_dict,orig_dict={}):
    config_data={}
    
    if (orig_dict=={}):
        config_data['version']=the_dict['version']
        try:
            config_data['basic_settings']=the_dict['basic_settings']
        except:
            pass
        try:
            config_data['advanced_settings']=the_dict['advanced_settings']
            if (not ((check:=keys_exist_return_value(the_dict,'advanced_settings','REMOVE_FILES')) == None)):
                if (check):
                    config_data['advanced_settings']['REMOVE_FILES']=False
        except:
            pass
        config_data['admin_settings']=the_dict['admin_settings']
        try:
            config_data['DEBUG']=the_dict['DEBUG']
        except:
            config_data['DEBUG']=0
    else:
        config_data['version']=orig_dict['version']
        try:
            config_data['basic_settings']=orig_dict['basic_settings']
        except:
            pass
        try:
            config_data['advanced_settings']=orig_dict['advanced_settings']
            if (not ((check:=keys_exist_return_value(orig_dict,'advanced_settings','REMOVE_FILES')) == None)):
                if (check):
                    config_data['advanced_settings']['REMOVE_FILES']=False
        except:
            pass
        config_data['admin_settings']={}
        try:
            try:
                #check if default value was NOT selected during updating
                if (the_dict['admin_settings']['behavior']['list'] == 'whitelist'):
                    orig_dict['admin_settings']['behavior']['list']='whitelist'
                else:
                    #check if keys already exist in 
                    if (keys_exist(orig_dict,'admin_settings','behavior','list')):
                        orig_dict['admin_settings']['behavior']['list']=the_dict['admin_settings']['behavior']['list']

                #before saving; reorder some keys for consistency
                orig_dict['admin_settings']['behavior']['list']=orig_dict['admin_settings']['behavior'].pop('list')
            except:
                pass

            try:
                #check if default value was NOT selected during updating
                if (the_dict['admin_settings']['behavior']['matching'] == 'byPath'):
                    orig_dict['admin_settings']['behavior']['matching']='byPath'
                elif (the_dict['admin_settings']['behavior']['matching'] == 'byNetworkPath'):
                    orig_dict['admin_settings']['behavior']['matching']='byNetworkPath'
                else:
                    if (keys_exist(orig_dict,'admin_settings','behavior','matching')):
                        orig_dict['admin_settings']['behavior']['matching']=the_dict['admin_settings']['behavior']['matching']

                #before saving; reorder some keys for consistency
                orig_dict['admin_settings']['behavior']['matching']=orig_dict['admin_settings']['behavior'].pop('matching')
            except:
                pass

            try:
                #check if default value was NOT selected during updating
                if (the_dict['admin_settings']['behavior']['users']['monitor_disabled'] == False):
                    orig_dict['admin_settings']['behavior']['users']['monitor_disabled']=False
                else:
                    if (keys_exist(orig_dict,'admin_settings','behavior','users')):
                        orig_dict['admin_settings']['behavior']['users']={}
                        #if (keys_exist(orig_dict,'admin_settings','behavior','users','monitor_disabled')):
                        orig_dict['admin_settings']['behavior']['users']['monitor_disabled']=the_dict['admin_settings']['behavior']['users']['monitor_disabled']
                        #else:
                            #orig_dict['admin_settings']['behavior']['users']['monitor_disabled']=the_dict['admin_settings']['behavior']['users']['monitor_disabled']

                #before saving; reorder some keys for consistency
                orig_dict['admin_settings']['behavior']['users']=orig_dict['admin_settings']['behavior'].pop('users')
            except:
                pass

            config_data['admin_settings']['behavior']=orig_dict['admin_settings']['behavior']
        except:
            pass
        config_data['admin_settings']['server']=orig_dict['admin_settings']['server']
        config_data['admin_settings']['users']=the_dict['admin_settings']['users']
        try:
            config_data['admin_settings']['api_controls']=orig_dict['admin_settings']['api_controls']
        except:
            pass
        try:
            config_data['admin_settings']['cache']=orig_dict['admin_settings']['cache']
        except:
            pass
        try:
            config_data['DEBUG']=the_dict['DEBUG']
        except:
            config_data['DEBUG']=0

    #save yaml config file
    save_yaml_config(config_data,the_dict['mumc_path'] / the_dict['config_file_name_yaml'])