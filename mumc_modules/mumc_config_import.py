#!/usr/bin/env python3
import importlib
from sys import path
from mumc_modules.mumc_config_build import build_configuration_file
from mumc_modules.mumc_output import print_byType
from mumc_modules.mumc_console_info import defaultHelper


def importConfig(init_dict,cmdopt_dict):
    try:
        #Attempt to import the alternate config file as cfg
        #Check for the .py extension and no spaces or periods in the module name
        if (cmdopt_dict['altConfigInfo']):
            #Insert alternate config to path at the top of the path list so it can be search and imported first
            #We want the alternate config path to be searched first incase the the alternate config is also named mumc_config.py
            #Searching the alternate config path first will allow the alternate config file to be found first
            if (not(cmdopt_dict['altConfigInfo'] in path)):
                path.insert(0,cmdopt_dict['altConfigPath'])
            #Cannot do a direct import using a variable; use the importlib.import_module instead
            #Also cannot import the whole path; add the path to path then import by filename
            cfg = importlib.import_module(cmdopt_dict['altConfigFileNoExt'],cmdopt_dict['altConfigInfo'])
        else:
            #try importing the mumc_config.py file
            #if mumc_config.py file does not exist go to except and create one
            import mumc_config as cfg

        #try assigning the DEBUG variable from mumc_config.py file
        #if DEBUG does not exsit go to except and rebuild the mumc_config.py file
        init_dict['DEBUG']=cfg.DEBUG
        #removing DEBUG from mumc_config.py file will allow the configuration to be reset

        #try assigning the server_brand variable from mumc_config.py file
        #if server_brand does not exsit go to except and rebuild the mumc_config.py file
        init_dict['server_brand']=cfg.server_brand.lower()
        #removing DEBUG from mumc_config.py file will allow the configuration to be reset
    except (AttributeError, ModuleNotFoundError):
        if (cmdopt_dict['containerized'] or cmdopt_dict['altConfigInfo']):
            print_byType('',True,init_dict)
            print_byType('Config file missing \'DEBUG\' and/or \'server_brand\' variables',True,init_dict)
            print_byType('',True,init_dict)
            print_byType('Either add missing config variables or rebuild the config by running: /path/to/python /path/to/mumc.py',True,init_dict)
            print_byType('',True,init_dict)
            defaultHelper(init_dict)
            exit(0)
        else:
            #tell user config found; but missing DEBUG or server_brand options
            #the_dict={}
            init_dict['DEBUG']=0
            init_dict['UPDATE_CONFIG']=False
            build_configuration_file(None,init_dict)
            #exit gracefully
            exit(0)

    return cfg