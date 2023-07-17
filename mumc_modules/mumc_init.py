#!/usr/bin/env python3
import os
from datetime import datetime,timezone
from sys import argv,path
from pathlib import Path
from mumc_modules.mumc_output import add_to_PATH
from mumc_modules.mumc_cache import cached_data_handler
from mumc_modules.mumc_compare_items import does_index_exist
from mumc_modules.mumc_console_attributes import console_text_attributes
from mumc_modules.mumc_server_type import isJellyfinServer


def initialize_mumc(cwd,mumc_path):

    the_cfg={}

    #Set dictionary variables
    the_cfg['DEBUG']=0
    the_cfg['config_file_name']='mumc_config.py'
    the_cfg['config_file_name_yaml']='mumc_config.yaml'
    the_cfg['config_file_name_no_ext']='mumc_config'
    the_cfg['debug_file_name']='mumc_DEBUG.log'
    the_cfg['date_time_now']=datetime.now()
    the_cfg['date_time_utc_now']=datetime.utcnow()
    the_cfg['date_time_now_tz_utc']=datetime.now(timezone.utc)
    #the_cfg['all_media_disabled']=False

    #get current working directory
    the_cfg['cwd']=cwd
    if (not(str(cwd) in path)):
        add_to_PATH(cwd,0)

    #get mumc.py directory
    the_cfg['mumc_path']=mumc_path
    if (not(str(mumc_path) in path)):
        add_to_PATH(mumc_path)

    #get command line arguments
    the_cfg['argv']=argv

    the_cfg['console_separator']='-----------------------------------------------------------'
    the_cfg['console_separator_']='-----------------------------------------------------------\n'
    the_cfg['_console_separator']='\n-----------------------------------------------------------'
    the_cfg['_console_separator_']='\n-----------------------------------------------------------\n'

    the_cfg['cache_size']=16#MB initial default value
    the_cfg['bytes_in_megabytes']=1048576
    the_cfg['fallback_behavior']='LRU' #initial default value
    the_cfg['last_accessed_time']=200 #initial default value
    the_cfg['cached_data']=cached_data_handler(the_cfg)
    the_cfg['text_attrs']=console_text_attributes()

    return the_cfg


def getIsAnyMediaEnabled(the_cfg):
    if (
        (the_cfg['played_filter_movie'][0] == -1) and
        (the_cfg['played_filter_episode'][0] == -1) and
        (the_cfg['played_filter_audio'][0] == -1) and
        ((('played_filter_audiobook' in the_cfg) and (does_index_exist(the_cfg['played_filter_audiobook'],0)) and (the_cfg['played_filter_audiobook'][0] == -1)) or (not ('played_filter_audiobook' in the_cfg))) and
        (the_cfg['created_filter_movie'][0] == -1) and
        (the_cfg['created_filter_episode'][0] == -1) and
        (the_cfg['created_filter_audio'][0] == -1) and
        ((('created_filter_audiobook' in the_cfg) and (does_index_exist(the_cfg['created_filter_audiobook'],0)) and (the_cfg['created_filter_audiobook'][0] == -1)) or (not ('created_filter_audiobook' in the_cfg)))
        ):
        the_cfg['all_media_disabled']=True
    else:
        the_cfg['all_media_disabled']=False
    return the_cfg


#force console outputs when DEBUG enabled
def override_consoleOutputs_onDEBUG(the_cfg):

    if (the_cfg['DEBUG']):
        the_cfg['print_script_header']=True
        the_cfg['print_script_warning']=True
        the_cfg['print_user_header']=True
        the_cfg['print_movie_delete_info']=True
        the_cfg['print_movie_keep_info']=True
        the_cfg['print_episode_delete_info']=True
        the_cfg['print_episode_keep_info']=True
        the_cfg['print_audio_delete_info']=True
        the_cfg['print_audio_keep_info']=True
        if(isJellyfinServer(the_cfg['server_brand'])):
            the_cfg['print_audiobook_delete_info']=True
            the_cfg['print_audiobook_keep_info']=True
        the_cfg['print_movie_post_processing_info']=True
        the_cfg['print_episode_post_processing_info']=True
        the_cfg['print_audio_post_processing_info']=True
        if(isJellyfinServer(the_cfg['server_brand'])):
            the_cfg['print_audiobook_post_processing_info']=True
        the_cfg['print_summary_header']=True
        the_cfg['print_movie_summary']=True
        the_cfg['print_episode_summary']=True
        the_cfg['print_audio_summary']=True
        if(isJellyfinServer(the_cfg['server_brand'])):
            the_cfg['print_audiobook_summary']=True
        the_cfg['print_script_footer']=True

    return the_cfg