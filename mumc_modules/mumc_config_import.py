#!/usr/bin/env python3
import importlib
import yaml
from mumc_modules.mumc_config_check import cfgCheckLegacy
from mumc_modules.mumc_config_builder import build_configuration_file
from mumc_modules.mumc_output import getFileExtension,add_to_PATH,doesFileExist
from mumc_modules.mumc_console_info import default_helper_menu,print_failed_to_load_config
from mumc_modules.mumc_config_convert import convert_legacyConfigToYAML


def importHasException(init_dict,cmdopt_dict):
    if (cmdopt_dict['containerized'] or cmdopt_dict['altConfigInfo']):
        print_failed_to_load_config(init_dict)
        default_helper_menu(init_dict)
        #exit gracefully
        exit(0)
    else:
        #config found; but missing DEBUG or server_brand options; automatically start to rebuild new config
        init_dict['DEBUG']=0
        init_dict['advanced_settings']={}
        init_dict['advanced_settings']['UPDATE_CONFIG']=False
        build_configuration_file(init_dict)
        #exit gracefully
        exit(0)


#verify specified variables are avaialbe in the config
def assignVarTest(init_dict,cmdopt_dict,cfg):
    try:
        #removing any of the test variables from mumc_config.yaml will cause script to rebuild a new config.yaml
        #try assigning the below variables from the mumc_config.yaml file
        #if any do not exist go to except and rebuild the mumc_config.yaml file
        #init_dict['admin_settings']['server']['brand']=cfg['admin_settings']['server']['brand'].casefold()
        init_dict['version']=cfg['version']
        init_dict['DEBUG']=cfg['DEBUG']

    except (AttributeError, ModuleNotFoundError, KeyError):
        importHasException(init_dict,cmdopt_dict)

    return init_dict


def importConfig(init_dict,cmdopt_dict):
    try:
        #Attempt to import the alternate config file as cfg
        #Check for the .py extension and no spaces or periods in the module name
        if (cmdopt_dict['altConfigInfo']):
            #Insert alternate config to path at the top of the path list so it can be searched and imported first
            #We want the alternate config path to be searched first incase the the alternate config is also named mumc_config.yaml
            #Searching the alternate config path first will allow the alternate config file to be found first
            add_to_PATH(cmdopt_dict['altConfigPath'],0)

            #check if yaml config
            if ((getFileExtension(cmdopt_dict['altConfigPath'] + '/' + cmdopt_dict['altConfigFileExt']) == '.yaml') or
               (getFileExtension(cmdopt_dict['altConfigPath'] + '/' + cmdopt_dict['altConfigFileExt']) == '.yml')):
                #open alternate yaml config
                with open(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)
            #check if legacy config
            else: #if (getFileExtension(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt']) == '.py'):
                #Cannot do a direct import using a variable; use the importlib.import_module instead
                #Also cannot import the whole path; add the path to path then import by filename
                cfg = importlib.import_module(cmdopt_dict['altConfigFileNoExt'],cmdopt_dict['altConfigInfo'])

                #run a config check on the legacy mumc_config.py before converting to mumc_config.yaml
                legacy_dict=cfgCheckLegacy(cfg,init_dict)
                #legacy_dict=legacy_dict

                #function to convert legacy config to mumc_config.yaml
                convert_legacyConfigToYAML(cfg,cmdopt_dict['altConfigPath'],cmdopt_dict['altConfigFileNoExt'])

                with open(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileNoExt'] + '.yaml', 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)

            #make sure a few of the necessary config variables are there
            init_dict=assignVarTest(init_dict,cmdopt_dict,cfg)

        else:
            if (doesFileExist(init_dict['mumc_path'] / init_dict['config_file_name_yaml'])):
                #try importing the mumc_config.yaml file
                #if mumc_config.yaml file does not exist try importing the legacy mumc_config.py file
                with open(init_dict['mumc_path'] / init_dict['config_file_name_yaml'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)
            else:
                #try importing the mumc_config.py file
                #if mumc_config.py file does not exist go to except and create one
                import mumc_config as cfg

                #run a config check on the legacy mumc_config.py before converting to mumc_config.yaml
                legacy_dict=cfgCheckLegacy(cfg,init_dict)
                #legacy_dict=legacy_dict

                #convert legacy mumc_config.py to mumc_config.yaml; output is mumc_config.yaml
                convert_legacyConfigToYAML(legacy_dict,init_dict['mumc_path'],init_dict['config_file_name_no_ext'])

                with open(init_dict['mumc_path'] / init_dict['config_file_name_yaml'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)

            #make sure a few of the necessary config variables are there
            init_dict=assignVarTest(init_dict,cmdopt_dict,cfg)

    except (AttributeError, ModuleNotFoundError, KeyError):
        importHasException(init_dict,cmdopt_dict)

    return cfg,init_dict