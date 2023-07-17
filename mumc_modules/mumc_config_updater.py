#!/usr/bin/env python3
import yaml
import json
from sys import path
from mumc_modules.mumc_versions import get_script_version
from mumc_modules.mumc_output import get_current_directory

def yaml_configurationUpdater(cfg,the_dict):

    #Save the config file
    with open(the_dict['mumc_path'] / the_dict['config_file_name_yaml'],'w') as file:
        file.write('---\n')
        yaml.safe_dump(cfg,file,sort_keys=False)
        file.write('...')

    

    return