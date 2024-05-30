from mumc_modules.mumc_output import save_yaml_config
from mumc_modules.mumc_compare_items import keys_exist_return_value

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