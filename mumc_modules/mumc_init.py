#!/usr/bin/env python3
from datetime import datetime,timezone
from sys import argv,path
from mumc_modules.mumc_output import add_to_PATH
from mumc_modules.mumc_cache import cached_data_handler
from mumc_modules.mumc_console_attributes import console_text_attributes
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_compare_items import keys_exist
from mumc_modules.mumc_versions import get_min_config_version,get_script_version


def initialize_mumc(cwd,mumc_path):

    the_cfg={}

    #Set dictionary variables
    the_cfg['DEBUG']=0
    the_cfg['version']=get_script_version()
    the_cfg['script_version']=get_script_version()
    the_cfg['min_config_version']=get_min_config_version()
    the_cfg['config_file_name']='mumc_config.py'
    the_cfg['config_file_name_yaml']='mumc_config.yaml'
    the_cfg['config_file_name_no_ext']='mumc_config'
    the_cfg['debug_file_name']='mumc_DEBUG.log'
    the_cfg['date_time_now']=datetime.now()
    the_cfg['date_time_utc_now']=datetime.utcnow()
    the_cfg['date_time_now_tz_utc']=datetime.now(timezone.utc)

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

    the_cfg['console_separator']='----------------------------------------------------------------------------------------'
    the_cfg['console_separator_']='----------------------------------------------------------------------------------------\n'
    the_cfg['_console_separator']='\n----------------------------------------------------------------------------------------'
    the_cfg['_console_separator_']='\n----------------------------------------------------------------------------------------\n'

    the_cfg['cache_size']=16#MB initial default value
    the_cfg['bytes_in_megabytes']=1048576
    the_cfg['fallback_behavior']='LRU' #initial default value
    the_cfg['minimum_age']=200 #initial default value
    the_cfg['cached_data']=cached_data_handler(the_cfg)
    the_cfg['text_attrs']=console_text_attributes()
    the_cfg['formatting']={}
    the_cfg['formatting']['font']={}
    the_cfg['formatting']['font']['color']=''
    the_cfg['formatting']['font']['style']=''
    the_cfg['formatting']['background']={}
    the_cfg['formatting']['background']['color']=''

    return the_cfg


def getIsAnyMediaEnabled(the_dict):
    audiobook_played_exists=keys_exist(the_dict['basic_settings']['filter_statements'],'audiobook','played','condition_days')
    audiobook_created_exists=keys_exist(the_dict['basic_settings']['filter_statements'],'audiobook','created','condition_days')

    if (
        (the_dict['basic_settings']['filter_statements']['movie']['played']['condition_days'] == -1) and
        (the_dict['basic_settings']['filter_statements']['episode']['played']['condition_days'] == -1) and
        (the_dict['basic_settings']['filter_statements']['audio']['played']['condition_days'] == -1) and
        ((audiobook_played_exists and (the_dict['basic_settings']['filter_statements']['audiobook']['played']['condition_days'] == -1)) or (not audiobook_played_exists)) and
        (the_dict['basic_settings']['filter_statements']['movie']['created']['condition_days'] == -1) and
        (the_dict['basic_settings']['filter_statements']['episode']['created']['condition_days'] == -1) and
        (the_dict['basic_settings']['filter_statements']['audio']['created']['condition_days'] == -1) and
        ((audiobook_created_exists and (the_dict['basic_settings']['filter_statements']['audiobook']['created']['condition_days'] == -1)) or (not audiobook_created_exists))
       ):
        the_dict['all_media_disabled']=True
    else:
        the_dict['all_media_disabled']=False

    return the_dict


#force console outputs when DEBUG enabled
def override_consoleOutputs_onDEBUG(the_dict):

    if (the_dict['DEBUG']):
        the_dict['advanced_settings']['console_controls']['headers']['script']['show']=True
        the_dict['advanced_settings']['console_controls']['headers']['user']['show']=True
        the_dict['advanced_settings']['console_controls']['headers']['summary']['show']=True
        the_dict['advanced_settings']['console_controls']['footers']['script']['show']=True
        the_dict['advanced_settings']['console_controls']['warnings']['script']['show']=True
        the_dict['advanced_settings']['console_controls']['movie']['delete']['show']=True
        the_dict['advanced_settings']['console_controls']['movie']['keep']['show']=True
        the_dict['advanced_settings']['console_controls']['movie']['post_processing']['show']=True
        the_dict['advanced_settings']['console_controls']['movie']['summary']['show']=True
        the_dict['advanced_settings']['console_controls']['episode']['delete']['show']=True
        the_dict['advanced_settings']['console_controls']['episode']['keep']['show']=True
        the_dict['advanced_settings']['console_controls']['episode']['post_processing']['show']=True
        the_dict['advanced_settings']['console_controls']['episode']['summary']['show']=True
        the_dict['advanced_settings']['console_controls']['audio']['delete']['show']=True
        the_dict['advanced_settings']['console_controls']['audio']['keep']['show']=True
        the_dict['advanced_settings']['console_controls']['audio']['post_processing']['show']=True
        the_dict['advanced_settings']['console_controls']['audio']['summary']['show']=True
        if(isJellyfinServer(the_dict['admin_settings']['server']['brand'])):
            the_dict['advanced_settings']['console_controls']['audiobook']['delete']['show']=True
            the_dict['advanced_settings']['console_controls']['audiobook']['keep']['show']=True
            the_dict['advanced_settings']['console_controls']['audiobook']['post_processing']['show']=True
            the_dict['advanced_settings']['console_controls']['audiobook']['summary']['show']=True

    return the_dict