#!/usr/bin/env python3
import multiprocessing
from pathlib import Path
from datetime import datetime
from mumc_modules.mumc_init import initialize_mumc,getIsAnyMediaEnabled,override_consoleOutputs_onDEBUG
from mumc_modules.mumc_parse_options import parse_command_line_options
from mumc_modules.mumc_config_import import importConfig
from mumc_modules.mumc_config_check import cfgCheckLegacy
from mumc_modules.mumc_config_builder import edit_configuration_file,buildUserLibraries
from mumc_modules.mumc_post_process import postProcessing,init_postProcessing
from mumc_modules.mumc_console_info import print_informational_header,print_starting_header,print_and_delete_items,print_cache_stats,print_footer_information,print_all_media_disabled,cache_data_to_debug
from mumc_modules.mumc_get_media import getMedia
from mumc_modules.mumc_sort import sortDeleteLists
from mumc_modules.mumc_output import get_current_directory,delete_debug_log
from mumc_modules.mumc_yaml_check import cfgCheckYAML


def main():
    #inital dictionary setup
    init_dict=initialize_mumc(get_current_directory(),Path(__file__).parent)

    #remove old DEBUG if it exists
    delete_debug_log(init_dict)

    #parse command line options
    cmdopt_dict=parse_command_line_options(init_dict)

    #import config file
    cfg,init_dict=importConfig(init_dict,cmdopt_dict)

    #get and check config values are what we expect them to be
    cfgCheckYAML(cfg,init_dict)
    #config_dict=cfgCheckLegacy(cfg,init_dict)

    #merge config_dict and init_dict
    cfg.update(init_dict)

    #update cache variables with values specified in the config file
    cfg['cached_data'].updateCacheVariables(cfg)

    #check if user wants to update the existing config file
    if (cfg['advanced_settings']['UPDATE_CONFIG']):
        #check if user intentionally wants to update the config
        edit_configuration_file(cfg)
        #exit gracefully after updating config
        exit(0)

    #output details about script, Emby/Jellying, and server
    print_informational_header(cfg_dict)

    #when debug is enabled force all console outputs
    cfg_dict=override_consoleOutputs_onDEBUG(cfg_dict)

    #output the starting header
    print_starting_header(cfg_dict)

    #before running the main part of the script, determine if at least one media type is enabled to be monitored
    cfg_dict=getIsAnyMediaEnabled(cfg_dict)

    #check if at least one media type is enabled ot be monitored
    #if not; print message to console
    #if it is; proceed and process media items
    if (config_dict['all_media_disabled']):
        #output message letting user know none of the media is enabled to be monitored
        print_all_media_disabled(config_dict)
    else:
        #build the user libraries from config data
        config_dict=buildUserLibraries(config_dict)

        #prepare for the main event; return dictionaries of media items per monitored user
        movie_dict,episode_dict,audio_dict,audiobook_dict=getMedia(config_dict)

        #prepare for post processing; return list of media items to be deleted
        deleteItems_dict=init_postProcessing(movie_dict,episode_dict,audio_dict,audiobook_dict,config_dict)

        #sort lists of items to be deleted into a single list
        deleteItems=sortDeleteLists(deleteItems_dict['movie'],deleteItems_dict['episode'],deleteItems_dict['audio'],deleteItems_dict['audiobook'])
        #deleteItems=sortDeleteLists(deleteItems_movie,deleteItems_episode,deleteItems_audio,deleteItems_audiobook)

        #output to console the items to be deleted; then delete media items
        print_and_delete_items(deleteItems,config_dict)

    #show cache stats
    print_cache_stats(config_dict)

    if (config_dict['DEBUG'] == 255):
        #show cache data (only when DEBUG=255; yes tihs is a "secret" DEBUG level)
        cache_data_to_debug(config_dict)

    #show footer info
    print_footer_information(config_dict)

    #clear cache
    config_dict['cached_data'].wipeCache()


############# START OF SCRIPT #############

if __name__ == "__main__":
    main()

############# END OF SCRIPT #############

exit(0)
