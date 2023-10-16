#!/usr/bin/env python3
from mumc_modules.mumc_output import save_yaml_config


#TBD
def yaml_configurationUpdater(the_dict):
    config_data={}
    config_data['version']=the_dict['version']
    config_data['basic_settings']=the_dict['basic_settings']
    config_data['advanced_settings']=the_dict['advanced_settings']
    config_data['admin_settings']=the_dict['admin_settings']
    config_data['DEBUG']=the_dict['DEBUG']

    #save yaml config file
    save_yaml_config(config_data,the_dict['mumc_path'] / the_dict['config_file_name_yaml'])

    #return