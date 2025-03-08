import sys
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_config_skeleton import setYAMLConfigSkeleton
from mumc_modules.mumc_configuration_yaml import yaml_configurationLayout

def create_default_config(server_brand='emby'):

    default_config={}
    default_config['server_brand']=server_brand
    #create empty config yaml
    default_config=setYAMLConfigSkeleton(default_config)
    default_config['admin_settings']['server']['brand']='emby'
    #populate empty config yaml with default values
    default_config=yaml_configurationLayout(default_config,default_config['server_brand'])

    return default_config

def merge_configuration(cfg_default,cfg_file):

    error_found_in_mumc_config_yaml=''

    try:
        cfg_default['version']=cfg_file['version']
    except:
        error_found_in_mumc_config_yaml+='ConfigError: version is missing from the MUMC config file\n'

    try:
        cfg_file['advanced_settings']=cfg_file['advanced_settings']
    except:
        pass
        #error_found_in_mumc_config_yaml+='ConfigError: advanced_settings is missing from the MUMC config file\n'
    try:
        cfg_default['DEBUG']=cfg_file['DEBUG']
    except:
        cfg_default['DEBUG']=0

    try:
        server_brand=cfg_file['admin_settings']['server']['brand']
    except:
        server_brand='emby'

    try:
        cfg_default['basic_settings']['filter_statements']['movie']['played']['condition_days']=cfg_file['basic_settings']['filter_statements']['movie']['played']['condition_days']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['movie']['played']['count_equality']=cfg_file['basic_settings']['filter_statements']['movie']['played']['count_equality']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['movie']['played']['count']=cfg_file['basic_settings']['filter_statements']['movie']['played']['count']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['movie']['created']['condition_days']=cfg_file['basic_settings']['filter_statements']['movie']['created']['condition_days']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['movie']['created']['count_equality']=cfg_file['basic_settings']['filter_statements']['movie']['created']['count_equality']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['movie']['created']['count']=cfg_file['basic_settings']['filter_statements']['movie']['created']['count']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['movie']['created']['behavioral_control']=cfg_file['basic_settings']['filter_statements']['movie']['created']['behavioral_control']
    except:
        pass

    try:
        cfg_default['basic_settings']['filter_statements']['episode']['played']['condition_days']=cfg_file['basic_settings']['filter_statements']['episode']['played']['condition_days']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['episode']['played']['count_equality']=cfg_file['basic_settings']['filter_statements']['episode']['played']['count_equality']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['episode']['played']['count']=cfg_file['basic_settings']['filter_statements']['episode']['played']['count']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['episode']['created']['condition_days']=cfg_file['basic_settings']['filter_statements']['episode']['created']['condition_days']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['episode']['created']['count_equality']=cfg_file['basic_settings']['filter_statements']['episode']['created']['count_equality']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['episode']['created']['count']=cfg_file['basic_settings']['filter_statements']['episode']['created']['count']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['episode']['created']['behavioral_control']=cfg_file['basic_settings']['filter_statements']['episode']['created']['behavioral_control']
    except:
        pass

    try:
        cfg_default['basic_settings']['filter_statements']['audio']['played']['condition_days']=cfg_file['basic_settings']['filter_statements']['audio']['played']['condition_days']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['audio']['played']['count_equality']=cfg_file['basic_settings']['filter_statements']['audio']['played']['count_equality']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['audio']['played']['count']=cfg_file['basic_settings']['filter_statements']['audio']['played']['count']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['audio']['created']['condition_days']=cfg_file['basic_settings']['filter_statements']['audio']['created']['condition_days']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['audio']['created']['count_equality']=cfg_file['basic_settings']['filter_statements']['audio']['created']['count_equality']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['audio']['created']['count']=cfg_file['basic_settings']['filter_statements']['audio']['created']['count']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_statements']['audio']['created']['behavioral_control']=cfg_file['basic_settings']['filter_statements']['audio']['created']['behavioral_control']
    except:
        pass

    if (server_brand == 'jellyfin'):
        try:
            cfg_default['basic_settings']['filter_statements']['audiobook']['played']['condition_days']=cfg_file['basic_settings']['filter_statements']['audiobook']['played']['condition_days']
        except:
            pass
        try:
            cfg_default['basic_settings']['filter_statements']['audiobook']['played']['count_equality']=cfg_file['basic_settings']['filter_statements']['audiobook']['played']['count_equality']
        except:
            pass
        try:
            cfg_default['basic_settings']['filter_statements']['audiobook']['played']['count']=cfg_file['basic_settings']['filter_statements']['audiobook']['played']['count']
        except:
            pass
        try:
            cfg_default['basic_settings']['filter_statements']['audiobook']['created']['condition_days']=cfg_file['basic_settings']['filter_statements']['audiobook']['created']['condition_days']
        except:
            pass
        try:
            cfg_default['basic_settings']['filter_statements']['audiobook']['created']['count_equality']=cfg_file['basic_settings']['filter_statements']['audiobook']['created']['count_equality']
        except:
            pass
        try:
            cfg_default['basic_settings']['filter_statements']['audiobook']['created']['count']=cfg_file['basic_settings']['filter_statements']['audiobook']['created']['count']
        except:
            pass
        try:
            cfg_default['basic_settings']['filter_statements']['audiobook']['created']['behavioral_control']=cfg_file['basic_settings']['filter_statements']['audiobook']['created']['behavioral_control']
        except:
            pass

    try:
        cfg_default['basic_settings']['filter_tags']['movie']['whitetags']=cfg_file['basic_settings']['filter_tags']['movie']['whitetags']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_tags']['movie']['blacktags']=cfg_file['basic_settings']['filter_tags']['movie']['blacktags']
    except:
        pass

    try:
        cfg_default['basic_settings']['filter_tags']['episode']['whitetags']=cfg_file['basic_settings']['filter_tags']['episode']['whitetags']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_tags']['episode']['blacktags']=cfg_file['basic_settings']['filter_tags']['episode']['blacktags']
    except:
        pass

    try:
        cfg_default['basic_settings']['filter_tags']['audio']['whitetags']=cfg_file['basic_settings']['filter_tags']['audio']['whitetags']
    except:
        pass
    try:
        cfg_default['basic_settings']['filter_tags']['audio']['blacktags']=cfg_file['basic_settings']['filter_tags']['audio']['blacktags']
    except:
        pass

    if (server_brand == 'jellyfin'):
        try:
            cfg_default['basic_settings']['filter_tags']['audiobook']['whitetags']=cfg_file['basic_settings']['filter_tags']['audiobook']['whitetags']
        except:
            pass
        try:
            cfg_default['basic_settings']['filter_tags']['audiobook']['blacktags']=cfg_file['basic_settings']['filter_tags']['audiobook']['blacktags']
        except:
            pass

    try:
        cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['favorited']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['favorited'] & cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['whitetagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitetagged'] & cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['blacktagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacktagged'] & cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['whitelisted']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']
            except:
                pass
    try:
        cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['favorited']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['favorited'] & cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['whitetagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['whitetagged'] & cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['blacktagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacktagged'] & cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['blacklisted']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']
            except:
                pass

    try:
        cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['favorited']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['favorited'] & cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['whitetagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitetagged'] & cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['blacktagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacktagged'] & cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['whitelisted']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']
            except:
                pass
    try:
        cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['favorited']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['favorited'] & cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['whitetagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['whitetagged'] & cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['blacktagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacktagged'] & cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['blacklisted']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']
            except:
                pass

    try:
        cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['favorited']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['favorited'] & cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['whitetagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitetagged'] & cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['blacktagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacktagged'] & cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['whitelisted']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']
            except:
                pass
    try:
        cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['favorited']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['favorited'] & cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['whitetagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['whitetagged'] & cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['blacktagged']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacktagged'] & cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']
        except:
            pass
    try:
        cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']
    except:
        try:
            cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['blacklisted']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']
            except:
                pass

    if (server_brand == 'jellyfin'):
        try:
            cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['favorited']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['favorited'] & cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']
            except:
                pass
        try:
            cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['whitetagged']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitetagged'] & cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']
            except:
                pass
        try:
            cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['blacktagged']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacktagged'] & cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']
            except:
                pass
        try:
            cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['whitelisted']
            except:
                try:
                    cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']
                except:
                    pass
        try:
            cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['favorited']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['favorited']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['favorited'] & cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']
            except:
                pass
        try:
            cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['whitetagged']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['whitetagged']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitetagged'] & cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']
            except:
                pass
        try:
            cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['blacktagged']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['blacktagged']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacktagged'] & cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']
            except:
                pass
        try:
            cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']
        except:
            try:
                cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['blacklisted']
            except:
                try:
                    cfg_default['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']=cfg_file['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']
                except:
                    pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['favorited']['action']=cfg_file['advanced_settings']['behavioral_statements']['movie']['favorited']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['favorited']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['favorited']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['favorited']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['favorited']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['favorited']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['movie']['favorited']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['genre']=cfg_file['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['genre']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['library_genre']=cfg_file['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['library_genre']
    except:
        pass
    
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitetagged']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitetagged']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitetagged']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitetagged']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']
    except:
        pass
    #try:
        #cfg_default['advanced_settings']['behavioral_statements']['movie']['whitetagged']['tags']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitetagged']['tags']
    #except:
        #pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacktagged']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacktagged']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacktagged']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacktagged']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']
    except:
        pass
    #try:
        #cfg_default['advanced_settings']['behavioral_statements']['movie']['blacktagged']['tags']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacktagged']['tags']
    #except:
        #pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitelisted']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitelisted']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitelisted']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitelisted']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']
    except:
        pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacklisted']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacklisted']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacklisted']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacklisted']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']
    except:
        pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['action']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['genre']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['genre']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['season_genre']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['season_genre']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['series_genre']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['series_genre']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['library_genre']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['library_genre']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network_genre']=cfg_file['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network_genre']
    except:
        pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitetagged']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitetagged']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitetagged']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitetagged']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']
    except:
        pass
    #try:
        #cfg_default['advanced_settings']['behavioral_statements']['episode']['whitetagged']['tags']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitetagged']['tags']
    #except:
        #pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacktagged']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacktagged']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacktagged']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacktagged']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']
    except:
        pass
    #try:
        #cfg_default['advanced_settings']['behavioral_statements']['episode']['blacktagged']['tags']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacktagged']['tags']
    #except:
        #pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitelisted']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitelisted']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitelisted']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitelisted']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']
    except:
        pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacklisted']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacklisted']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacklisted']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacklisted']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']
    except:
        pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['action']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['genre']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['genre']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_genre']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_genre']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['library_genre']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['library_genre']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['track_artist']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['track_artist']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_artist']=cfg_file['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_artist']
    except:
        pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitetagged']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitetagged']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitetagged']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitetagged']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']
    except:
        pass
    #try:
        #cfg_default['advanced_settings']['behavioral_statements']['audio']['whitetagged']['tags']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitetagged']['tags']
    #except:
        #pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacktagged']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacktagged']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacktagged']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacktagged']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']
    except:
        pass
    #try:
        #cfg_default['advanced_settings']['behavioral_statements']['audio']['blacktagged']['tags']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacktagged']['tags']
    #except:
        #pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitelisted']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitelisted']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitelisted']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitelisted']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']
    except:
        pass

    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacklisted']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacklisted']['user_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacklisted']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacklisted']['played_conditional']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action_control']
    except:
        pass
    try:
        cfg_default['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']
    except:
        pass

    if (server_brand == 'jellyfin'):
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['user_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['played_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action_control']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['genre']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['genre']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['audiobook_genre']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['audiobook_genre']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_genre']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_genre']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['track_author']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['track_author']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['author']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['author']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_author']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_author']
        except:
            pass

        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['user_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['played_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action_control']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']
        except:
            pass
        #try:
            #cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['tags']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['tags']
        #except:
            #pass

        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['user_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['played_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action_control']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']
        except:
            pass
        #try:
            #cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['tags']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['tags']
        #except:
            #pass

        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['user_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['played_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action_control']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']
        except:
            pass

        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['user_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['user_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['played_conditional']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['played_conditional']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action_control']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action_control']
        except:
            pass
        try:
            cfg_default['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']
        except:
            pass

    try:
        cfg_default['advanced_settings']['behavioral_tags']['movie']=cfg_file['advanced_settings']['behavioral_tags']['movie']
    except:
        pass

    try:
        cfg_default['advanced_settings']['behavioral_tags']['episode']=cfg_file['advanced_settings']['behavioral_tags']['episode']
    except:
        pass

    try:
        cfg_default['advanced_settings']['behavioral_tags']['audio']=cfg_file['advanced_settings']['behavioral_tags']['audio']
    except:
        pass

    if (server_brand == 'jellyfin'):

        try:
            cfg_default['advanced_settings']['behavioral_tags']['audiobook']=cfg_file['advanced_settings']['behavioral_tags']['audiobook']
        except:
            pass

    try:
        cfg_default['advanced_settings']['whitetags']['global']=cfg_file['advanced_settings']['whitetags']['global']
    except:
        try:
            cfg_default['advanced_settings']['whitetags']['global']=cfg_file['advanced_settings']['whitetags']
        except:
            pass
    try:
        cfg_default['advanced_settings']['whitetags']['movie']=cfg_file['advanced_settings']['whitetags']['movie']
    except:
        try:
            cfg_default['advanced_settings']['whitetags']['movie']=cfg_file['advanced_settings']['behavioral_statements']['movie']['whitetagged']['tags']
        except:
            pass
    try:
        cfg_default['advanced_settings']['whitetags']['episode']=cfg_file['advanced_settings']['whitetags']['episode']
    except:
        try:
            cfg_default['advanced_settings']['whitetags']['episode']=cfg_file['advanced_settings']['behavioral_statements']['episode']['whitetagged']['tags']
        except:
            pass
    try:
        cfg_default['advanced_settings']['whitetags']['audio']=cfg_file['advanced_settings']['whitetags']['audio']
    except:
        try:
            cfg_default['advanced_settings']['whitetags']['audio']=cfg_file['advanced_settings']['behavioral_statements']['audio']['whitetagged']['tags']
        except:
            pass
    if (server_brand == 'jellyfin'):
        try:
            cfg_default['advanced_settings']['whitetags']['audiobook']=cfg_file['advanced_settings']['whitetags']['audiobook']
        except:
            try:
                cfg_default['advanced_settings']['whitetags']['audiobook']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['tags']
            except:
                pass

    try:
        cfg_default['advanced_settings']['blacktags']['global']=cfg_file['advanced_settings']['blacktags']['global']
    except:
        try:
            cfg_default['advanced_settings']['blacktags']['global']=cfg_file['advanced_settings']['blacktags']
        except:
            pass
    try:
        cfg_default['advanced_settings']['blacktags']['movie']=cfg_file['advanced_settings']['blacktags']['movie']
    except:
        try:
            cfg_default['advanced_settings']['blacktags']['movie']=cfg_file['advanced_settings']['behavioral_statements']['movie']['blacktagged']['tags']
        except:
            pass
    try:
        cfg_default['advanced_settings']['blacktags']['episode']=cfg_file['advanced_settings']['blacktags']['episode']
    except:
        try:
            cfg_default['advanced_settings']['blacktags']['episode']=cfg_file['advanced_settings']['behavioral_statements']['episode']['blacktagged']['tags']
        except:
            pass
    try:
        cfg_default['advanced_settings']['blacktags']['audio']=cfg_file['advanced_settings']['blacktags']['audio']
    except:
        try:
            cfg_default['advanced_settings']['blacktags']['audio']=cfg_file['advanced_settings']['behavioral_statements']['audio']['blacktagged']['tags']
        except:
            pass
    if (server_brand == 'jellyfin'):
        try:
            cfg_default['advanced_settings']['blacktags']['audiobook']=cfg_file['advanced_settings']['blacktags']['audiobook']
        except:
            try:
                cfg_default['advanced_settings']['blacktags']['audiobook']=cfg_file['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['tags']
            except:
                pass

    try:
        cfg_default['advanced_settings']['delete_empty_folders']['episode']['season']=cfg_file['advanced_settings']['delete_empty_folders']['episode']['season']
    except:
        pass
    try:
        cfg_default['advanced_settings']['delete_empty_folders']['episode']['series']=cfg_file['advanced_settings']['delete_empty_folders']['episode']['series']
    except:
        pass

    try:
        cfg_default['advanced_settings']['episode_control']['minimum_episodes']=cfg_file['advanced_settings']['episode_control']['minimum_episodes']
    except:
        pass
    try:
        cfg_default['advanced_settings']['episode_control']['minimum_played_episodes']=cfg_file['advanced_settings']['episode_control']['minimum_played_episodes']
    except:
        pass
    try:
        cfg_default['advanced_settings']['episode_control']['minimum_episodes_behavior']=cfg_file['advanced_settings']['episode_control']['minimum_episodes_behavior']
    except:
        pass
    try:
        cfg_default['advanced_settings']['episode_control']['series_ended']['delete_episodes']=cfg_file['advanced_settings']['episode_control']['series_ended']['delete_episodes']
    except:
        pass

    try:
        cfg_default['advanced_settings']['radarr']['movie']['unmonitor']=cfg_file['advanced_settings']['radarr']['movie']['unmonitor']
    except:
        pass
    try:
        cfg_default['advanced_settings']['radarr']['movie']['remove']=cfg_file['advanced_settings']['radarr']['movie']['remove']
    except:
        pass

    try:
        cfg_default['advanced_settings']['sonarr']['series']['unmonitor']=cfg_file['advanced_settings']['sonarr']['series']['unmonitor']
    except:
        pass
    try:
        cfg_default['advanced_settings']['sonarr']['series']['remove']=cfg_file['advanced_settings']['sonarr']['series']['unmonitor']
    except:
        pass
    try:
        cfg_default['advanced_settings']['sonarr']['episode']['unmonitor']=cfg_file['advanced_settings']['sonarr']['episode']['remove']
    except:
        pass

    try:
        cfg_default['advanced_settings']['lidarr']['album']['unmonitor']=cfg_file['advanced_settings']['lidarr']['album']['unmonitor']
    except:
        pass
    try:
        cfg_default['advanced_settings']['lidarr']['album']['remove']=cfg_file['advanced_settings']['album']['album']['remove']
    except:
        pass
    try:
        cfg_default['advanced_settings']['lidarr']['track']['unmonitor']=cfg_file['advanced_settings']['lidarr']['track']['unmonitor']
    except:
        pass

    try:
        cfg_default['advanced_settings']['readarr']['book']['unmonitor']=cfg_file['advanced_settings']['readarr']['readarr']['unmonitor']
    except:
        pass
    try:
        cfg_default['advanced_settings']['readarr']['book']['delete']=cfg_file['advanced_settings']['readarr']['readarr']['delete']
    except:
        pass

    try:
        cfg_default['advanced_settings']['trakt_fix']['set_missing_last_played_date']['movie']=cfg_file['advanced_settings']['trakt_fix']['set_missing_last_played_date']['movie']
    except:
        pass
    try:
        cfg_default['advanced_settings']['trakt_fix']['set_missing_last_played_date']['episode']=cfg_file['advanced_settings']['trakt_fix']['set_missing_last_played_date']['episode']
    except:
        pass
    try:
        cfg_default['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audio']=cfg_file['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audio']
    except:
        pass
    if (server_brand == 'jellyfin'):
        try:
            cfg_default['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audiobook']=cfg_file['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audiobook']
        except:
            pass

    try:
        cfg_default['advanced_settings']['console_controls']['headers']['script']['show']=cfg_file['advanced_settings']['console_controls']['headers']['script']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['headers']['script']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['headers']['script']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['headers']['user']['show']=cfg_file['advanced_settings']['console_controls']['headers']['user']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['headers']['user']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['headers']['user']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['headers']['summary']['show']=cfg_file['advanced_settings']['console_controls']['headers']['summary']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['headers']['summary']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['headers']['summary']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['footers']['script']['show']=cfg_file['advanced_settings']['console_controls']['footers']['script']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['footers']['script']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['footers']['script']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['warnings']['script']['show']=cfg_file['advanced_settings']['console_controls']['warnings']['script']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['warnings']['script']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['warnings']['script']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['movie']['delete']['show']=cfg_file['advanced_settings']['console_controls']['movie']['delete']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['delete']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['movie']['delete']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['movie']['keep']['show']=cfg_file['advanced_settings']['console_controls']['movie']['keep']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['keep']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['movie']['keep']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['movie']['post_processing']['show']=cfg_file['advanced_settings']['console_controls']['movie']['post_processing']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['movie']['summary']['show']=cfg_file['advanced_settings']['console_controls']['movie']['summary']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['movie']['summary']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['movie']['summary']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['episode']['delete']['show']=cfg_file['advanced_settings']['console_controls']['episode']['delete']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['delete']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['episode']['delete']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['episode']['keep']['show']=cfg_file['advanced_settings']['console_controls']['episode']['keep']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['keep']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['episode']['keep']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['episode']['post_processing']['show']=cfg_file['advanced_settings']['console_controls']['episode']['post_processing']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['episode']['summary']['show']=cfg_file['advanced_settings']['console_controls']['episode']['summary']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['episode']['summary']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['episode']['summary']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['audio']['delete']['show']=cfg_file['advanced_settings']['console_controls']['audio']['delete']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['delete']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['audio']['delete']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['audio']['keep']['show']=cfg_file['advanced_settings']['console_controls']['audio']['keep']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['keep']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['audio']['keep']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['audio']['post_processing']['show']=cfg_file['advanced_settings']['console_controls']['audio']['post_processing']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['background']['color']
    except:
        pass

    try:
        cfg_default['advanced_settings']['console_controls']['audio']['summary']['show']=cfg_file['advanced_settings']['console_controls']['audio']['summary']['show']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['color']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['style']
    except:
        pass
    try:
        cfg_default['advanced_settings']['console_controls']['audio']['summary']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['audio']['summary']['formatting']['background']['color']
    except:
        pass

    if (server_brand == 'jellyfin'):
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['delete']['show']=cfg_file['advanced_settings']['console_controls']['audiobook']['delete']['show']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['color']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['style']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['background']['color']
        except:
            pass

        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['keep']['show']=cfg_file['advanced_settings']['console_controls']['audiobook']['keep']['show']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['color']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['style']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['background']['color']
        except:
            pass

        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['post_processing']['show']=cfg_file['advanced_settings']['console_controls']['audiobook']['post_processing']['show']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['color']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['style']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['background']['color']
        except:
            pass

        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['summary']['show']=cfg_file['advanced_settings']['console_controls']['audiobook']['summary']['show']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['color']=cfg_file['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['color']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['style']=cfg_file['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['style']
        except:
            pass
        try:
            cfg_default['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['background']['color']=cfg_file['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['background']['color']
        except:
            pass

    try:
        cfg_default['advanced_settings']['UPDATE_CONFIG']=cfg_file['advanced_settings']['UPDATE_CONFIG']
    except:
        pass
    try:
        cfg_default['advanced_settings']['REMOVE_FILES']=cfg_file['advanced_settings']['REMOVE_FILES']
    except:
        pass
        #error_found_in_mumc_config_yaml+='ConfigError: advanced_settings > REMOVE_FILES is missing from the MUMC config file\n'

    try:
        cfg_default['admin_settings']['behavior']['list']=cfg_file['admin_settings']['behavior']['list']
    except:
        pass
    try:
        cfg_default['admin_settings']['behavior']['matching']=cfg_file['admin_settings']['behavior']['matching']
    except:
        pass
    try:
        cfg_default['admin_settings']['behavior']['users']['monitor_disabled']=cfg_file['admin_settings']['behavior']['users']['monitor_disabled']
    except:
        pass

    cfg_default['admin_settings']['server']['brand']=server_brand
    try:
        cfg_default['admin_settings']['server']['url']=cfg_file['admin_settings']['server']['url']
    except:
        pass
        #error_found_in_mumc_config_yaml+='ConfigError: admin_settings > server > url is missing from the MUMC config file\n'
    try:
        cfg_default['admin_settings']['server']['auth_key']=cfg_file['admin_settings']['server']['auth_key']
    except:
        pass
        #error_found_in_mumc_config_yaml+='ConfigError: admin_settings > server > auth_key is missing from the MUMC config file\n'
    try:
        cfg_default['admin_settings']['server']['admin_id']=cfg_file['admin_settings']['server']['admin_id']
    except:
        pass
        #error_found_in_mumc_config_yaml+='ConfigError: admin_settings > server > admin_id is missing from the MUMC config file\n'

    try:
        #cfg_default['admin_settings']['users']=cfg_file['admin_settings']['users']
        cfg_file['admin_settings']['users']=cfg_file['admin_settings']['users']
        if (len(cfg_file['admin_settings']['users']) >= 1):
            #cfg_default['admin_settings']['users'].append({})
            for userInfo in cfg_file['admin_settings']['users']:
                cfg_default['admin_settings']['users'].append({})
                try:
                    userInfo['user_id']=userInfo['user_id']
                    cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['user_id']=userInfo['user_id']
                except:
                    error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users > ' + str(cfg_file['admin_settings']['users'].index(userInfo)) + ' > user_id is missing from the MUMC config file\n'
                try:
                    userInfo['user_name']=userInfo['user_name']
                    cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['user_name']=userInfo['user_name']
                except:
                    error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users > ' + str(cfg_file['admin_settings']['users'].index(userInfo)) + ' > user_name is missing from the MUMC config file\n'
                try:
                    userInfo['whitelist']=userInfo['whitelist']
                    if (len(userInfo['whitelist']) >= 1):
                        cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist']=[]
                        #cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'].append({})
                        for whitelistInfo in userInfo['whitelist']:
                            cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'].append({})
                            try:
                                whitelistInfo['lib_id']=whitelistInfo['lib_id']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'][userInfo['whitelist'].index(whitelistInfo)]['lib_id']=whitelistInfo['lib_id']
                            except:
                                error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users > ' + str(cfg_file['admin_settings']['users'].index(userInfo)) + ' > whitelist > ' + userInfo['whitelist'].index(whitelistInfo) + ' > lib_id is missing from the MUMC config file\n'
                            try:
                                whitelistInfo['collection_type']=whitelistInfo['collection_type']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'][userInfo['whitelist'].index(whitelistInfo)]['collection_type']=whitelistInfo['collection_type']
                            except:
                                error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users > ' + str(cfg_file['admin_settings']['users'].index(userInfo)) + ' > whitelist > ' + userInfo['whitelist'].index(whitelistInfo) + ' > collection_type is missing from the MUMC config file\n'
                            try:
                                whitelistInfo['path']=whitelistInfo['path']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'][userInfo['whitelist'].index(whitelistInfo)]['path']=whitelistInfo['path']
                            except:
                                error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users > ' + str(cfg_file['admin_settings']['users'].index(userInfo)) + ' > whitelist > ' + userInfo['whitelist'].index(whitelistInfo) + ' > path is missing from the MUMC config file\n'
                            try:
                                whitelistInfo['network_path']=whitelistInfo['network_path']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'][userInfo['whitelist'].index(whitelistInfo)]['network_path']=whitelistInfo['network_path']
                            except:
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'][userInfo['whitelist'].index(whitelistInfo)]['network_path']=cfg_default['admin_settings']['users'][0]['whitelist'][0]['network_path']
                            try:
                                whitelistInfo['subfolder_id']=whitelistInfo['subfolder_id']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'][userInfo['whitelist'].index(whitelistInfo)]['subfolder_id']=whitelistInfo['subfolder_id']
                            except:
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'][userInfo['whitelist'].index(whitelistInfo)]['subfolder_id']=cfg_default['admin_settings']['users'][0]['whitelist'][0]['subfolder_id']
                            try:
                                whitelistInfo['lib_enabled']=whitelistInfo['lib_enabled']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'][userInfo['whitelist'].index(whitelistInfo)]['lib_enabled']=whitelistInfo['lib_enabled']
                            except:
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['whitelist'][userInfo['whitelist'].index(whitelistInfo)]['lib_enabled']=cfg_default['admin_settings']['users'][0]['whitelist'][0]['lib_enabled']
                    else:
                        pass
                except:
                    cfg_default['admin_settings']['users'][1]['whitelist']=cfg_default['admin_settings']['users'][0]['whitelist']
                try:
                    userInfo['blacklist']=userInfo['blacklist']
                    if (len(userInfo['blacklist']) >= 1):
                        cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist']=[]
                        #cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'].append({})
                        for blacklistInfo in userInfo['blacklist']:
                            cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'].append({})
                            try:
                                blacklistInfo['lib_id']=blacklistInfo['lib_id']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'][userInfo['blacklist'].index(blacklistInfo)]['lib_id']=blacklistInfo['lib_id']
                            except:
                                error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users > ' + str(cfg_file['admin_settings']['users'].index(userInfo)) + ' > blacklist > ' + userInfo['blacklist'].index(blacklistInfo) + ' > lib_id is missing from the MUMC config file\n'
                            try:
                                blacklistInfo['collection_type']=blacklistInfo['collection_type']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'][userInfo['blacklist'].index(blacklistInfo)]['collection_type']=blacklistInfo['collection_type']
                            except:
                                error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users > ' + str(cfg_file['admin_settings']['users'].index(userInfo)) + ' > blacklist > ' + userInfo['blacklist'].index(blacklistInfo) + ' > collection_type is missing from the MUMC config file\n'
                            try:
                                blacklistInfo['path']=blacklistInfo['path']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'][userInfo['blacklist'].index(blacklistInfo)]['path']=blacklistInfo['path']
                            except:
                                error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users > ' + str(cfg_file['admin_settings']['users'].index(userInfo)) + ' > blacklist > ' + userInfo['blacklist'].index(blacklistInfo) + ' > path is missing from the MUMC config file\n'
                            try:
                                blacklistInfo['network_path']=blacklistInfo['network_path']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'][userInfo['blacklist'].index(blacklistInfo)]['network_path']=blacklistInfo['network_path']
                            except:
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'][userInfo['blacklist'].index(blacklistInfo)]['network_path']=cfg_default['admin_settings']['users'][0]['blacklist'][0]['network_path']
                            try:
                                blacklistInfo['subfolder_id']=blacklistInfo['subfolder_id']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'][userInfo['blacklist'].index(blacklistInfo)]['subfolder_id']=blacklistInfo['subfolder_id']
                            except:
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'][userInfo['blacklist'].index(blacklistInfo)]['subfolder_id']=cfg_default['admin_settings']['users'][0]['blacklist'][0]['subfolder_id']
                            try:
                                blacklistInfo['lib_enabled']=blacklistInfo['lib_enabled']
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'][userInfo['blacklist'].index(blacklistInfo)]['lib_enabled']=blacklistInfo['lib_enabled']
                            except:
                                cfg_default['admin_settings']['users'][cfg_file['admin_settings']['users'].index(userInfo) + 1]['blacklist'][userInfo['blacklist'].index(blacklistInfo)]['lib_enabled']=cfg_default['admin_settings']['users'][0]['blacklist'][0]['lib_enabled']
                    else:
                        pass
                except:
                    cfg_default['admin_settings']['users'][1]['blacklist']=cfg_default['admin_settings']['users'][0]['blacklist']
        else:
            pass
            #error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users list is empty\n'
    except:
        pass
        #error_found_in_mumc_config_yaml+='ConfigError: admin_settings > users is missing from the MUMC config file\n'

    cfg_default['admin_settings']['users'].pop(0)

    try:
        cfg_default['admin_settings']['media_managers']['radarr']['enabled']=cfg_file['admin_settings']['media_managers']['radarr']['enabled']
    except:
        pass
    try:
        cfg_default['admin_settings']['media_managers']['radarr']['url']=cfg_file['admin_settings']['media_managers']['radarr']['url']
    except:
        pass
    try:
        cfg_default['admin_settings']['media_managers']['radarr']['api_key']=cfg_file['admin_settings']['media_managers']['radarr']['api_key']
    except:
        pass

    try:
        cfg_default['admin_settings']['media_managers']['sonarr']['enabled']=cfg_file['admin_settings']['media_managers']['sonarr']['enabled']
    except:
        pass
    try:
        cfg_default['admin_settings']['media_managers']['sonarr']['url']=cfg_file['admin_settings']['media_managers']['sonarr']['url']
    except:
        pass
    try:
        cfg_default['admin_settings']['media_managers']['sonarr']['api_key']=cfg_file['admin_settings']['media_managers']['sonarr']['api_key']
    except:
        pass

    try:
        cfg_default['admin_settings']['media_managers']['lidarr']['enabled']=cfg_file['admin_settings']['media_managers']['lidarr']['enabled']
    except:
        pass
    try:
        cfg_default['admin_settings']['media_managers']['lidarr']['url']=cfg_file['admin_settings']['media_managers']['lidarr']['url']
    except:
        pass
    try:
        cfg_default['admin_settings']['media_managers']['lidarr']['api_key']=cfg_file['admin_settings']['media_managers']['lidarr']['api_key']
    except:
        pass

    try:
        cfg_default['admin_settings']['media_managers']['readarr']['enabled']=cfg_file['admin_settings']['media_managers']['readarr']['enabled']
    except:
        pass
    try:
        cfg_default['admin_settings']['media_managers']['readarr']['url']=cfg_file['admin_settings']['media_managers']['readarr']['url']
    except:
        pass
    try:
        cfg_default['admin_settings']['media_managers']['readarr']['api_key']=cfg_file['admin_settings']['media_managers']['readarr']['api_key']
    except:
        pass

    try:
        cfg_default['admin_settings']['api_controls']['attempts']=cfg_file['admin_settings']['api_controls']['attempts']
    except:
        pass
    try:
        cfg_default['admin_settings']['api_controls']['item_limit']=cfg_file['admin_settings']['api_controls']['item_limit']
    except:
        pass

    try:
        cfg_default['admin_settings']['cache']['size']=cfg_file['admin_settings']['cache']['size']
    except:
        pass
    try:
        cfg_default['admin_settings']['cache']['fallback_behavior']=cfg_file['admin_settings']['cache']['fallback_behavior']
    except:
        pass
    try:
        cfg_default['admin_settings']['cache']['minimum_age']=cfg_file['admin_settings']['cache']['minimum_age']
    except:
        try:
            cfg_default['admin_settings']['cache']['minimum_age']=cfg_file['admin_settings']['cache']['last_accessed_time']
        except:
            pass

    try:
        cfg_default['admin_settings']['output_controls']['character_limit']['print']=cfg_file['admin_settings']['output_controls']['character_limit']['print']
    except:
        pass
    #try:
        #cfg_default['admin_settings']['output_controls']['character_limit']['write']=cfg_file['admin_settings']['output_controls']['character_limit']['write']
    #except:
        #pass

    #Bring all errors found to users attention
    if (not (error_found_in_mumc_config_yaml == '')):
        if (cfg_default['DEBUG']):
            appendTo_DEBUG_log("\n" + error_found_in_mumc_config_yaml,2,cfg_default)
        print('\n' + error_found_in_mumc_config_yaml)
        sys.exit(0)

    #before saving; reorder some keys for consistency
    cfg_default['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']=cfg_default['advanced_settings']['behavioral_statements']['movie']['favorited'].pop('extra')
    cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']=cfg_default['advanced_settings']['behavioral_statements']['episode']['favorited'].pop('extra')
    cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']=cfg_default['advanced_settings']['behavioral_statements']['audio']['favorited'].pop('extra')
    if (server_brand == 'jellyfin'):
        cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']=cfg_default['advanced_settings']['behavioral_statements']['audiobook']['favorited'].pop('extra')

    return cfg_default