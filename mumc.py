#!/usr/bin/env python3
import copy
import sys
from pathlib import Path
from mumc_modules.mumc_init import initialize_mumc,getIsAnyMediaEnabled,override_consoleOutputs_onDEBUG
from mumc_modules.mumc_parse_commands import parse_command_line_options
from mumc_modules.mumc_config_import import importConfig
from mumc_modules.mumc_config_builder import edit_configuration_file
from mumc_modules.mumc_post_process import init_postProcessing
from mumc_modules.mumc_console_info import print_informational_header,print_starting_header,print_cache_stats,print_footer_information,print_all_media_disabled,cache_data_to_debug,print_configuration_yaml,override_media_manager_enabled_states
from mumc_modules.mumc_get_media import init_getMedia
from mumc_modules.mumc_sort import sortDeleteLists
from mumc_modules.mumc_paths_files import get_current_directory,delete_debug_log
from mumc_modules.mumc_output import open_and_return_default_config
from mumc_modules.mumc_yaml_check import cfgCheckYAML,pre_cfgCheckYAML
#from mumc_modules.mumc_yaml_check import cfgCheckYAML
from mumc_modules.mumc_folder_cleanup import season_series_folder_cleanup
#from mumc_modules.mumc_config_merge import create_default_config,merge_configurations
from mumc_modules.mumc_config_merge import merge_configurations
from mumc_modules.mumc_get_folders import populate_config_with_subfolder_ids
from mumc_modules.mumc_delete import print_and_delete_items
from mumc_modules.mumc_data_checks import data_checker
#from memory_profiler import profile


#@profile
def MUMC():
    #inital dictionary setup
    init_dict=initialize_mumc(get_current_directory(),Path(__file__).parent)

    #parse command line options
    cmdopt_dict=parse_command_line_options(init_dict)
    init_dict['argv']=cmdopt_dict['argv']

    #import config file
    cfg,init_dict=importConfig(init_dict,cmdopt_dict)

    #get and pre-check user defined values are what we expect them to be
    pre_cfgCheckYAML(cfg,init_dict)

    #get and full check user defined config values are what we expect them to be
    userCfgChecker=data_checker(cfg,init_dict['DEBUG'])
    cfg=cfgCheckYAML(cfg,userCfgChecker)

    #after importing the config; remove old DEBUG if it exists
    delete_debug_log(init_dict)

    #look for missing subfolder Ids and add them
    cfg=populate_config_with_subfolder_ids(cfg,init_dict)

    #remember original config for when user wants to update existing config file
    cfg_orig=copy.deepcopy(cfg)

    #create default config file
    default_config=open_and_return_default_config()

    #copy over path info for use later
    default_config['mumc_path']=init_dict['mumc_path']
    default_config['debug_file_name']=init_dict['debug_file_name']

    #merge user config into default config
    cfg=merge_configurations(default_config,cfg)

    if (cfg['DEBUG']):
        #print config when DEBUG >= 1
        print_configuration_yaml(cfg,init_dict)

    #get and check user defined + default config values are what we expect them to be
    cfgChecker=data_checker(cfg,cfg['DEBUG'])
    cfg=cfgCheckYAML(cfg,cfgChecker)

    #merge cfg and init_dict; goal is to preserve cfg's structure
    init_dict.update(copy.deepcopy(cfg))
    cfg=copy.deepcopy(init_dict)

    #update cache variables with values specified in the config file
    cfg['cached_data'].updateCacheVariables(cfg)

    #check if user wants to update the existing config file
    #if ((cfg['advanced_settings']['UPDATE_CONFIG']) or (cmdopt_dict['configUpdater'])):
    if ((cfg['advanced_settings']['UPDATE_CONFIG']) or (('-config_updater' in cmdopt_dict['argv']) and (cmdopt_dict['argv']['-config_updater']))):
        #check if user intentionally wants to update the config
        edit_configuration_file(cfg,cfg_orig)

        if (cfg['DEBUG']):
            #show cache stats
            print_cache_stats(cfg)

        if (cfg['DEBUG'] == 255):
            #show cache data (only when DEBUG == 255
            cache_data_to_debug(cfg)

        #clear cache
        cfg['cached_data'].wipeCache()

        return

    #check for media_manager info; override if None or ''
    override_media_manager_enabled_states(cfg)

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

        #output to console the items to be deleted; then delete media items
        print_and_delete_items(deleteItems,cfg)

    #cleanup empty season and series folders
    season_series_folder_cleanup(deleteItems,cfg)

    if (cfg['DEBUG']):
        #show cache stats
        print_cache_stats(cfg)

    if (cfg['DEBUG'] == 255):
        #show cache data (only when DEBUG == 255)
        cache_data_to_debug(cfg)

    #show footer info
    print_footer_information(cfg)

    #clear cache
    cfg['cached_data'].wipeCache()

    return


############# START OF SCRIPT #############

if (__name__ == "__main__"):

    MUMC()

#Exit Gracefully
sys.exit(0)

############# END OF SCRIPT #############