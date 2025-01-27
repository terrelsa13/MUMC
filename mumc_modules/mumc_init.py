from datetime import datetime,timezone
from sys import argv,path
from os import environ as envar
from mumc_modules.mumc_paths_files import add_to_PATH
from mumc_modules.mumc_cache import cached_data_handler
from mumc_modules.mumc_console_attributes import console_text_attributes
from mumc_modules.mumc_server_type import isEmbyServer,isJellyfinServer
from mumc_modules.mumc_compare_items import keys_exist_return_value
from mumc_modules.mumc_versions import get_min_config_version,get_script_version
from mumc_modules.mumc_tagged import get_isFilterStatementTag
from sys import exit

def initialize_mumc(cwd,mumc_path):

    the_cfg={}

    #Set dictionary variables
    the_cfg['app_name_short']='MUMC'
    the_cfg['app_name_long']='Multi-User Media Cleaner'
    the_cfg['DEBUG']=0
    the_cfg['version']=get_script_version()
    the_cfg['script_version']=get_script_version()
    the_cfg['min_config_version']=get_min_config_version()
    the_cfg['client_name']='mumc.py'
    the_cfg['config_file_path']=None
    the_cfg['config_file_name']=None
    the_cfg['config_file_name_py']='mumc_config.py'
    the_cfg['config_file_name_yaml']='mumc_config.yaml'
    the_cfg['config_file_name_yml']='mumc_config.yml'
    the_cfg['config_file_name_no_ext']='mumc_config'
    the_cfg['debug_file_name']='mumc_DEBUG.log'
    the_cfg['date_time_now']=datetime.now()
    the_cfg['date_time_now_tz_utc']=datetime.now(timezone.utc)
    the_cfg['date_time_utc_now']=the_cfg['date_time_now_tz_utc'].replace(tzinfo=None)

    #save current working directory
    the_cfg['cwd']=cwd
    if (not(str(cwd) in path)):
        add_to_PATH(cwd,0)

    #save ../config/mumc_config.yaml directory
    the_cfg['mumc_path_config_dir']=mumc_path / 'config'
    if (not(str(mumc_path / 'config') in path)):
        add_to_PATH(mumc_path / 'config',1)

    #save ../mumc_config.yaml directory
    the_cfg['mumc_path']=mumc_path
    if (not(str(mumc_path) in path)):
        add_to_PATH(mumc_path,1)

    #save command line arguments
    the_cfg['argv']=argv
    print(argv)
    print()
    #save environmental variables
    the_cfg['envar']=envar
    print(envar)
    print()

    the_cfg['console_separator']='----------------------------------------------------------------------------------------'
    the_cfg['console_separator_']='----------------------------------------------------------------------------------------\n'
    the_cfg['_console_separator']='\n----------------------------------------------------------------------------------------'
    the_cfg['_console_separator_']='\n----------------------------------------------------------------------------------------\n'

    the_cfg['cache_size']=4#MB initial default value
    the_cfg['bytes_in_megabytes']=1000000 #1048576 bytes is 1 mebibyte
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

    the_dict['all_media_disabled']=True
    server_brand=isJellyfinServer(the_dict['admin_settings']['server']['brand'])

    #the_dict['filter_tag_played_days']=False
    #the_dict['filter_tag_created_days']=False

    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_statements','movie','played','condition_days')) == None)):
        if (check >= 0):
            the_dict['all_media_disabled']=False
            return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_statements','movie','created','condition_days')) == None)):
        if (check >= 0):
            the_dict['all_media_disabled']=False
            return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_statements','episode','played','condition_days')) == None)):
        if (check >= 0):
            the_dict['all_media_disabled']=False
            return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_statements','episode','created','condition_days')) == None)):
        if (check >= 0):
            the_dict['all_media_disabled']=False
            return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_statements','audio','played','condition_days')) == None)):
        if (check >= 0):
            the_dict['all_media_disabled']=False
            return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_statements','audio','created','condition_days')) == None)):
        if (check >= 0):
            the_dict['all_media_disabled']=False
            return the_dict
    if(server_brand):
        if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_statements','audiobook','played','condition_days')) == None)):
            if (check >= 0):
                the_dict['all_media_disabled']=False
                return the_dict
        if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_statements','audiobook','created','condition_days')) == None)):
            if (check >= 0):
                the_dict['all_media_disabled']=False
                return the_dict

    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_tags','movie','whitetags')) == None)):
        for filterTag in check:
            if (not ((filterStatementTag:=get_isFilterStatementTag(filterTag)) == False)):
                if (filterStatementTag[1] >= 0):
                    the_dict['all_media_disabled']=False
                    return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_tags','movie','blacktags')) == None)):
        for filterTag in check:
            if (not ((filterStatementTag:=get_isFilterStatementTag(filterTag)) == False)):
                if (filterStatementTag[1] >= 0):
                    the_dict['all_media_disabled']=False
                    return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_tags','episode','whitetags')) == None)):
        for filterTag in check:
            if (not ((filterStatementTag:=get_isFilterStatementTag(filterTag)) == False)):
                if (filterStatementTag[1] >= 0):
                    the_dict['all_media_disabled']=False
                    return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_tags','episode','blacktags')) == None)):
        for filterTag in check:
            if (not ((filterStatementTag:=get_isFilterStatementTag(filterTag)) == False)):
                if (filterStatementTag[1] >= 0):
                    the_dict['all_media_disabled']=False
                    return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_tags','audio','whitetags')) == None)):
        for filterTag in check:
            if (not ((filterStatementTag:=get_isFilterStatementTag(filterTag)) == False)):
                if (filterStatementTag[1] >= 0):
                    the_dict['all_media_disabled']=False
                    return the_dict
    if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_tags','audio','blacktags')) == None)):
        for filterTag in check:
            if (not ((filterStatementTag:=get_isFilterStatementTag(filterTag)) == False)):
                if (filterStatementTag[1] >= 0):
                    the_dict['all_media_disabled']=False
                    return the_dict
    if(server_brand):
        if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_tags','audiobook','whitetags')) == None)):
            for filterTag in check:
                if (not ((filterStatementTag:=get_isFilterStatementTag(filterTag)) == False)):
                    if (filterStatementTag[1] >= 0):
                        the_dict['all_media_disabled']=False
                        return the_dict
        if (not ((check:=keys_exist_return_value(the_dict,'basic_settings','filter_tags','audiobook','blacktags')) == None)):
            for filterTag in check:
                if (not ((filterStatementTag:=get_isFilterStatementTag(filterTag)) == False)):
                    if (filterStatementTag[1] >= 0):
                        the_dict['all_media_disabled']=False
                        return the_dict

    for mediaType in ('movie','episode','audio','audiobook'):
        if (not ((isEmbyServer(the_dict['admin_settings']['server']['brand'])) and (mediaType == 'audiobook'))):
            #remove whitespace(s) from the beginning and end of each tag
            #whitetags_global = [tagstr for tagstr in the_dict['advanced_settings']['whitetags'] if tagstr.strip()]
            #blacktags_global = [tagstr for tagstr in the_dict['advanced_settings']['blacktags'] if tagstr.strip()]
            #whitetags_media_specific = [tagstr for tagstr in the_dict['advanced_settings']['behavioral_statements'][mediaType]['whitetagged']['tags'] if tagstr.strip()]
            #blacktags_media_specific = [tagstr for tagstr in the_dict['advanced_settings']['behavioral_statements'][mediaType]['blacktagged']['tags'] if tagstr.strip()]
            whitetags_global = [tagstr for tagstr in the_dict['advanced_settings']['whitetags']['global'] if tagstr.strip()]
            blacktags_global = [tagstr for tagstr in the_dict['advanced_settings']['blacktags']['global'] if tagstr.strip()]
            whitetags_media_specific = [tagstr for tagstr in the_dict['advanced_settings']['whitetags'][mediaType] if tagstr.strip()]
            blacktags_media_specific = [tagstr for tagstr in the_dict['advanced_settings']['blacktags'][mediaType] if tagstr.strip()]
            #combine tags and remove any duplicates
            the_dict['whitetags']=list(set(whitetags_global + whitetags_media_specific))
            the_dict['blacktags']=list(set(blacktags_global + blacktags_media_specific))

            for this_tag in the_dict['whitetags']:
                if (not ((this_filter_tag_list:=get_isFilterStatementTag(this_tag)) == False)):
                    #if (this_tag.startswith('played')):
                        #tagType='played'
                    #elif (this_tag.startswith('created')):
                        #tagType='created'
                    #if (this_filter_tag_list['media_' + tagType + '_days'] >= 0):
                    if (this_filter_tag_list[1] >= 0):
                        the_dict['all_media_disabled']=False
                        return the_dict

            for this_tag in the_dict['blacktags']:
                if (not ((this_filter_tag_list:=get_isFilterStatementTag(this_tag)) == False)):
                    #if (this_tag.startswith('played')):
                        #tagType='played'
                    #elif (this_tag.startswith('created')):
                        #tagType='created'
                    #if (this_filter_tag_list['media_' + tagType + '_days'] >= 0):
                    if (this_filter_tag_list[1] >= 0):
                        the_dict['all_media_disabled']=False
                        return the_dict

    return the_dict


#force console outputs when DEBUG enabled
def override_consoleOutputs_onDEBUG(the_dict):

    #enable all output for all other DEBUG
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