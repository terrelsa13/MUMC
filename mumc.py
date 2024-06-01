#!/usr/bin/env python3
import copy
import sys
from pathlib import Path
from mumc_modules.mumc_init import initialize_mumc,getIsAnyMediaEnabled,override_consoleOutputs_onDEBUG
from mumc_modules.mumc_parse_options import parse_command_line_options
from mumc_modules.mumc_config_import import importConfig
from mumc_modules.mumc_config_builder import edit_configuration_file
from mumc_modules.mumc_post_process import init_postProcessing
from mumc_modules.mumc_console_info import print_informational_header,print_starting_header,print_and_delete_items,print_cache_stats,print_footer_information,print_all_media_disabled,cache_data_to_debug
from mumc_modules.mumc_get_media import init_getMedia
from mumc_modules.mumc_sort import sortDeleteLists
from mumc_modules.mumc_paths import get_current_directory,delete_debug_log
from mumc_modules.mumc_yaml_check import cfgCheckYAML,pre_cfgCheckYAML
from mumc_modules.mumc_folder_cleanup import season_series_folder_cleanup
from mumc_modules.mumc_config_default import create_default_config,merge_configuration

def MUMC():
    #inital dictionary setup
    init_dict=initialize_mumc(get_current_directory(),Path(__file__).parent)

    #remove old DEBUG if it exists
    delete_debug_log(init_dict)

    #parse command line options
    cmdopt_dict=parse_command_line_options(init_dict)

    #import config file
    cfg,init_dict=importConfig(init_dict,cmdopt_dict)

    #remember original config for when user wants to update existing config file
    cfg_orig=copy.deepcopy(cfg)

    pre_cfgCheckYAML(cfg)

    #create default config file
    default_config=create_default_config(cfg['admin_settings']['server']['brand'])

    #copy over path info for use later
    default_config['mumc_path']=init_dict['mumc_path']
    default_config['debug_file_name']=init_dict['debug_file_name']

    #merge user config into default config
    cfg=merge_configuration(default_config,cfg)

    #delete unused variable
    del default_config

    #get and check config values are what we expect them to be
    cfg,init_dict=cfgCheckYAML(cfg,init_dict)

    #merge cfg and init_dict; goal is to preserve cfg's structure
    init_dict.update(copy.deepcopy(cfg))
    cfg=copy.deepcopy(init_dict)

    #delete unused variable
    del init_dict

    #update cache variables with values specified in the config file
    cfg['cached_data'].updateCacheVariables(cfg)

    #check if user wants to update the existing config file
    if ((cfg['advanced_settings']['UPDATE_CONFIG']) or (cmdopt_dict['configUpdater'])):
        #check if user intentionally wants to update the config
        edit_configuration_file(cfg,cfg_orig)

        if (cfg['DEBUG']):
            #show cache stats
            print_cache_stats(cfg)

        if (cfg['DEBUG'] == 255):
            #show cache data (only when DEBUG=255; yes tihs is a "secret" DEBUG level)
            cache_data_to_debug(cfg)

        #delete unused variables
        del cmdopt_dict
        del cfg_orig

        #exit gracefully after updating config
        sys.exit(0)
    else:
        #delete unused variables
        del cmdopt_dict
        del cfg_orig

    #output details about script, Emby/Jellyfin, and server
    print_informational_header(cfg)

    #when debug is enabled force all console outputs
    cfg=override_consoleOutputs_onDEBUG(cfg)

    #output the starting header
    print_starting_header(cfg)

    #before running the main part of the script, determine if at least one media type is enabled to be monitored
    cfg=getIsAnyMediaEnabled(cfg)

    #check if at least one media type is enabled ot be monitored
    #if not; print message to console
    #if it is; proceed and process media items
    if (cfg['all_media_disabled']):
        #output message letting user know none of the media is enabled to be monitored
        print_all_media_disabled(cfg)
        deleteItems=[]
    else:
        #prepare for the main event; return dictionaries of media items per monitored user
        cfg=init_getMedia(cfg)

        #prepare for post processing; return list of media items to be deleted
        deleteItems_dict=init_postProcessing(cfg)

        #sort lists of items to be deleted into a single list
        deleteItems=sortDeleteLists(deleteItems_dict)

        del deleteItems_dict

        #output to console the items to be deleted; then delete media items
        print_and_delete_items(deleteItems,cfg)

    #cleanup empty season and series folders
    season_series_folder_cleanup(deleteItems,cfg)
    
    #delete unused variable
    del deleteItems

    if (cfg['DEBUG']):
        #show cache stats
        print_cache_stats(cfg)

    if (cfg['DEBUG'] == 255):
        #show cache data (only when DEBUG=255; yes tihs is a "secret" DEBUG level)
        cache_data_to_debug(cfg)

    #show footer info
    print_footer_information(cfg)

    #clear cache
    cfg['cached_data'].wipeCache()

    #delete unused variable
    del cfg


############# START OF SCRIPT #############

if (__name__ == "__main__"):
    MUMC()

sys.exit(0)

############# END OF SCRIPT #############