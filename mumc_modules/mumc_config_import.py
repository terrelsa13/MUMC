#!/usr/bin/env python3
import importlib
import yaml
from mumc_modules.mumc_config_check import cfgCheckLegacy
from mumc_modules.mumc_config_builder import build_configuration_file
from mumc_modules.mumc_output import print_byType,getFileExtension,add_to_PATH,doesFileExist
from mumc_modules.mumc_console_info import default_helper_menu,concat_to_console_strings_list,print_failed_to_load_config
from mumc_modules.mumc_config_convert import convert_legacyConfigToYAML


#removing any of the test variables from mumc_config.yaml will cause script to rebuild a new config.yaml
def assignVarTest(init_dict,cfg):
    #try assigning the below variables from the mumc_config.yaml file
    #if any do not exist go to except and rebuild the mumc_config.yaml file
    init_dict['config_version']=cfg['version']
    init_dict['server_brand']=cfg['admin_settings']['server']['brand'].lower()
    init_dict['DEBUG']=cfg['DEBUG']

    return init_dict


def importConfig(init_dict,cmdopt_dict):
    try:
        #Attempt to import the alternate config file as cfg
        #Check for the .py extension and no spaces or periods in the module name
        if (cmdopt_dict['altConfigInfo']):
            #Insert alternate config to path at the top of the path list so it can be searched and imported first
            #We want the alternate config path to be searched first incase the the alternate config is also named mumc_config.py
            #Searching the alternate config path first will allow the alternate config file to be found first
            add_to_PATH(cmdopt_dict['altConfigPath'],0)

            #check if yaml config
            if ((getFileExtension(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt']) == '.yaml') or
               (getFileExtension(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt']) == '.yml')):
                with open(cmdopt_dict['altConfigPath'] / 'mumc_config.yaml', 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)
            #check if legacy config
            else: #if (getFileExtension(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt']) == '.py'):
                #Cannot do a direct import using a variable; use the importlib.import_module instead
                #Also cannot import the whole path; add the path to path then import by filename
                cfg = importlib.import_module(cmdopt_dict['altConfigFileNoExt'],cmdopt_dict['altConfigInfo'])

                #run a config check on the legacy mumc_config.py before converting to mumc_config.yaml
                legacy_dict=cfgCheckLegacy(cfg,init_dict)
                legacy_dict=legacy_dict

                #function to convert legacy config to mumc_config.yaml
                convert_legacyConfigToYAML(cfg,cmdopt_dict['altConfigPath'],cmdopt_dict['altConfigFileNoExt'])

                with open(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileNoExt'] + '.yaml', 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)

            #make sure a few of the necessary config variables are there
            init_dict=assignVarTest(init_dict,cfg)

        else:
            if (doesFileExist(init_dict['mumc_path'] / init_dict['config_file_name'])):
                #try importing the mumc_config.py file
                #if mumc_config.py file does not exist go to except and create one
                with open(init_dict['mumc_path'] / init_dict['config_file_name_yaml'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)
            else:
                #try importing the mumc_config.yaml file
                #if mumc_config.yaml file does not exist go to except and create one
                import mumc_config as cfg

                #run a config check on the legacy mumc_config.py before converting to mumc_config.yaml
                legacy_dict=cfgCheckLegacy(cfg,init_dict)
                legacy_dict=legacy_dict

                #convert legacy mumc_config.py to mumc_config.yaml
                convert_legacyConfigToYAML(cfg,init_dict['mumc_path'],init_dict['config_file_name_no_ext'])

                with open(init_dict['mumc_path'] / init_dict['config_file_name_yaml'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)

            #make sure a few of the necessary config variables are there
            init_dict=assignVarTest(init_dict,cfg)

    except (AttributeError, ModuleNotFoundError):
        if (cmdopt_dict['containerized'] or cmdopt_dict['altConfigInfo']):
            print_failed_to_load_config(init_dict)
            default_helper_menu(init_dict)
            #exit gracefully
            exit(0)
        else:
            #tell user config found; but missing DEBUG or server_brand options
            init_dict['DEBUG']=0
            init_dict['UPDATE_CONFIG']=False
            build_configuration_file(None,init_dict)
            #exit gracefully
            exit(0)

    return cfg,init_dict