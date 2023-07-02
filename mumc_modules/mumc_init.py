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

    the_dict={}

    #Set dictionary variables
    the_dict['DEBUG']=0
    the_dict['config_file_name']='mumc_config.py'
    the_dict['config_file_name_yaml']='mumc_config.yaml'
    the_dict['config_file_name_no_ext']='mumc_config'
    the_dict['debug_file_name']='mumc_DEBUG.log'
    the_dict['date_time_now']=datetime.now()
    the_dict['date_time_utc_now']=datetime.utcnow()
    the_dict['date_time_now_tz_utc']=datetime.now(timezone.utc)
    #the_dict['all_media_disabled']=False

    #get current working directory
    the_dict['cwd']=cwd
    if (not(str(cwd) in path)):
        add_to_PATH(cwd,0)

    #get mumc.py directory
    the_dict['mumc_path']=mumc_path
    if (not(str(mumc_path) in path)):
        add_to_PATH(mumc_path)

    #get command line arguments
    the_dict['argv']=argv

    the_dict['console_separator']='-----------------------------------------------------------'
    the_dict['console_separator_']='-----------------------------------------------------------\n'
    the_dict['_console_separator']='\n-----------------------------------------------------------'
    the_dict['_console_separator_']='\n-----------------------------------------------------------\n'

    the_dict['bytes_in_megabytes']=1048576
    the_dict['cached_data']=cached_data_handler(the_dict)
    the_dict['text_attrs']=console_text_attributes()

    return the_dict


def getIsAnyMediaEnabled(the_dict):
    if (
        (the_dict['played_filter_movie'][0] == -1) and
        (the_dict['played_filter_episode'][0] == -1) and
        (the_dict['played_filter_audio'][0] == -1) and
        ((('played_filter_audiobook' in the_dict) and (does_index_exist(the_dict['played_filter_audiobook'],0)) and (the_dict['played_filter_audiobook'][0] == -1)) or (not ('played_filter_audiobook' in the_dict))) and
        (the_dict['created_filter_movie'][0] == -1) and
        (the_dict['created_filter_episode'][0] == -1) and
        (the_dict['created_filter_audio'][0] == -1) and
        ((('created_filter_audiobook' in the_dict) and (does_index_exist(the_dict['created_filter_audiobook'],0)) and (the_dict['created_filter_audiobook'][0] == -1)) or (not ('created_filter_audiobook' in the_dict)))
        ):
        the_dict['all_media_disabled']=True
    else:
        the_dict['all_media_disabled']=False
    return the_dict


#force console outputs when DEBUG enabled
def override_consoleOutputs_onDEBUG(the_dict):

    if (the_dict['DEBUG']):
        the_dict['print_script_header']=True
        the_dict['print_script_warning']=True
        the_dict['print_user_header']=True
        the_dict['print_movie_delete_info']=True
        the_dict['print_movie_keep_info']=True
        the_dict['print_episode_delete_info']=True
        the_dict['print_episode_keep_info']=True
        the_dict['print_audio_delete_info']=True
        the_dict['print_audio_keep_info']=True
        if(isJellyfinServer(the_dict['server_brand'])):
            the_dict['print_audiobook_delete_info']=True
            the_dict['print_audiobook_keep_info']=True
        the_dict['print_movie_post_processing_info']=True
        the_dict['print_episode_post_processing_info']=True
        the_dict['print_audio_post_processing_info']=True
        if(isJellyfinServer(the_dict['server_brand'])):
            the_dict['print_audiobook_post_processing_info']=True
        the_dict['print_summary_header']=True
        the_dict['print_movie_summary']=True
        the_dict['print_episode_summary']=True
        the_dict['print_audio_summary']=True
        if(isJellyfinServer(the_dict['server_brand'])):
            the_dict['print_audiobook_summary']=True
        the_dict['print_script_footer']=True

    return the_dict