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

    print()
    print(envar)
    print(the_cfg['argv'])
    print()


#environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': '4d119a6a129f', 'C': '/usr/src/app/config', 'SERVER_BRAND': 'EMBYFIN', 'SU': 'https://embyfin.com', 'ADMIN_USERNAME': 'you-and_me', 'AP': '  abc  123  zyx  987  ', 'SERVER_AUTH_KEY': 'some  hex  value', 'SAI': '\\\\ some\\\\ other\\\\ hex\\\\ value\\\\', 'TZ': 'America/New_York', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.11.11', 'PYTHON_SHA256': '2a9920c7a0cd236de33644ed980a13cbbc21058bfdc528febb6081575ed73be3', 'HOME': '/root'})
#['./mumc.py', '-d']
#['./mumc.py', '-d', '/usr/src/app/config', 'EMBYFIN', 'https://embyfin.com', 'you-and_me', 'abc123zyx987', 'somehexvalue', '\\\\some\\\\other\\\\hex\\\\value\\\\']

#environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'e288cad6ec98', 'SERVER_AUTH_KEY': 'some  hex  value', 'SAI': 'some other hex value', 'TZ': 'America/New_York', 'C': '/usr/src/app/config', 'SERVER_BRAND': 'EMBYFIN', 'SU': 'https://embyfin.com', 'ADMIN_USERNAME': 'you-and_me', 'AP': '  abc  123  zyx  987  ', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.11.11', 'PYTHON_SHA256': '2a9920c7a0cd236de33644ed980a13cbbc21058bfdc528febb6081575ed73be3', 'HOME': '/root'})
#['./mumc.py', '-d']
#['./mumc.py', '-d', '/usr/src/app/config', 'EMBYFIN', 'https://embyfin.com', 'you-and_me', 'abc123zyx987', 'somehexvalue', 'someotherhexvalue']

#environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': '45938294e2ef', 'CONFIG': '/usr/src/app/config', 'ADMIN_PASSWORD': '  abc  123  zyx  987  ', 'TZ': 'America/New_York', 'SERVER_BRAND': 'EMBYFIN', 'SERVER_ADMIN_ID': 'some other hex value', 'SERVER_URL': 'https://embyfin.com', 'SERVER_AUTH_KEY': 'some  hex  value', 'ADMIN_USERNAME': 'you-and_me', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.11.11', 'PYTHON_SHA256': '2a9920c7a0cd236de33644ed980a13cbbc21058bfdc528febb6081575ed73be3', 'HOME': '/root'})
#['./mumc.py', '-d']
#['./mumc.py', '-d']

#environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': '7aa5285f6318', 'SERVER_URL': 'https://embyfin.com', 'SERVER_ADMIN_ID': 'some other hex value', 'ATTRS': 'false', 'SERVER_AUTH_KEY': 'some  hex  value', 'SERVER_BRAND': 'EMBYFIN', 'TZ': 'America/New_York', 'ADMIN_USERNAME': 'you-and_me', 'CONFIG': '/usr/src/app/config', 'CONTAINER': 'true', 'ADMIN_PASSWORD': '  abc  123  zyx  987  ', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.11.11', 'PYTHON_SHA256': '2a9920c7a0cd236de33644ed980a13cbbc21058bfdc528febb6081575ed73be3', 'HOME': '/root'})
#['./mumc.py', '-d']
#['./mumc.py', '-d']

#environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': '6ee9f3fba24f', 'CONFIG': '/usr/src/app/config', 'SERVER_URL': 'https://embyfin.com', 'SERVER_BRAND': 'EMBYFIN', 'SERVER_AUTH_KEY': 'some  hex  value', 'ATTRS': 'False', 'SERVER_ADMIN_ID': 'some other hex value', 'TZ': 'America/New_York', 'CONTAINER': 'true', 'ADMIN_USERNAME': 'you-and_me', 'ADMIN_PASSWORD': '  abc  123  zyx  987  ', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.11.11', 'PYTHON_SHA256': '2a9920c7a0cd236de33644ed980a13cbbc21058bfdc528febb6081575ed73be3', 'HOME': '/root'})
#['./mumc.py', '-d']
#['./mumc.py', '-d']

    #need to parse to take into account all the ways people can enter/format these commands/environmental variables

    #save container environmental variables
    #save environmental variable - ATTRS,ATTRIBUTES
    if (not (envar.get('ATTRS') == None)):
        the_cfg['argv'].append('-attrs')
        the_cfg['argv'].append(envar['ATTRS'])
    if (not (envar.get('ATTRIBUTES') == None)):
        the_cfg['argv'].append('-attributes')
        the_cfg['argv'].append(envar['ATTRIBUTES'])

    #save environmental variable - CONFIG
    if (not (envar.get('CONFIG') == None)):
        the_cfg['argv'].append('-config')
        the_cfg['argv'].append(envar['CONFIG'])

    #save environmental variable - SERVER_BRAND
    if (not (envar.get('SERVER_BRAND') == None)):
        the_cfg['argv'].append('-server_brand')
        the_cfg['argv'].append(envar['SERVER_BRAND'])

    #save environmental variable - SERVER_URL
    if (not (envar.get('SERVER_URL') == None)):
        the_cfg['argv'].append('-server_url')
        the_cfg['argv'].append(envar['SERVER_URL'])

    #save environmental variable - ADMIN_USERNAME
    if (not (envar.get('ADMIN_USERNAME') == None)):
        the_cfg['argv'].append('-admin_username')
        the_cfg['argv'].append(envar['ADMIN_USERNAME'])

    #save environmental variable - ADMIN_PASSWORD
    if (not (envar.get('ADMIN_PASSWORD') == None)):
        the_cfg['argv'].append('-admin_password')
        the_cfg['argv'].append(envar['ADMIN_PASSWORD'])

    #save environmental variable - SERVER_AUTH_KEY
    if (not (envar.get('SERVER_AUTH_KEY') == None)):
        the_cfg['argv'].append('-server_auth_key')
        the_cfg['argv'].append(envar['SERVER_AUTH_KEY'])

    #save environmental variable - SERVER_ADMIN_ID
    if (not (envar.get('SERVER_ADMIN_ID') == None)):
        the_cfg['argv'].append('-server_admin_id')
        the_cfg['argv'].append(envar['SERVER_ADMIN_ID'])

    #save environmental variable - LIST_BEHAVIOR
    #save environmental variable - MATCHING_BEHAVIOR
    #save environmental variable - MONITOR_DISABLED_USERS
    #save environmental variable - RADARR_URL
    #save environmental variable - RADARR_API
    #save environmental variable - SONARR_URL
    #save environmental variable - SONARR_API
    #save environmental variable - LIDARR_URL
    #save environmental variable - LIDARR_API
    #save environmental variable - READARR_URL
    #save environmental variable - READARR_API

    print()
    print(the_cfg['argv'])
    print()
    exit(0)

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