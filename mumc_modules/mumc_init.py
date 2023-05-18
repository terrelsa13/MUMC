#!/usr/bin/env python3
from datetime import datetime,timezone
from sys import argv
from mumc_modules.mumc_output import get_current_directory
from mumc_modules.mumc_cache import cached_data_handler
from mumc_modules.mumc_compare_items import does_index_exist


def initialize_mumc():

    the_dict={}

    #Set dictionary variables
    the_dict['DEBUG']=0
    the_dict['config_file_name']='mumc_config.py'
    the_dict['debug_file_name']='mumc_DEBUG.log'
    the_dict['date_time_now']=datetime.now()
    the_dict['date_time_utc_now']=datetime.utcnow()
    the_dict['date_time_now_tz_utc']=datetime.now(timezone.utc)
    the_dict['all_media_disabled']=False
    #get current working directory
    the_dict['cwd']=get_current_directory()
    #get command line arguments
    the_dict['argv']=argv

    the_dict['bytes_in_megabytes']=1048576
    the_dict['cached_data']=cached_data_handler(the_dict)

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
    return the_dict


#force console outputs when DEBUG enabled
def override_consoleOutputs_onDEBUG(the_dict):
    if (the_dict['DEBUG']):
        the_dict['print_script_header']=True
        the_dict['print_warnings']=True
        the_dict['print_user_header']=True
        the_dict['print_movie_delete_info']=True
        the_dict['print_movie_keep_info']=True
        the_dict['print_episode_delete_info']=True
        the_dict['print_episode_keep_info']=True
        the_dict['print_audio_delete_info']=True
        the_dict['print_audio_keep_info']=True
        the_dict['print_audiobook_delete_info']=True
        the_dict['print_audiobook_keep_info']=True
        the_dict['print_summary_header']=True
        the_dict['print_movie_summary']=True
        the_dict['print_episode_summary']=True
        the_dict['print_audio_summary']=True
        the_dict['print_audiobook_summary']=True
        the_dict['print_script_footer']=True

    return the_dict