import sys
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_tagged import get_isPlayedCreated_FilterStatementTag
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

def merge_configuration(default_base,merge):

    error_found_in_mumc_config_yaml=''

    try:
        default_base['version']=merge['version']
    except:
        error_found_in_mumc_config_yaml+='ConfigNameError: version is missing from the mumc_config.yaml\n'

    try:
        merge['advanced_settings']=merge['advanced_settings']
    except:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings is missing from the mumc_config.yaml\n'
    try:
        default_base['DEBUG']=merge['DEBUG']
    except:
        default_base['DEBUG']=0

    try:
        server_brand=merge['admin_settings']['server']['brand']
    except:
        server_brand='emby'

    try:
        default_base['basic_settings']['filter_statements']['movie']['played']['condition_days']=merge['basic_settings']['filter_statements']['movie']['played']['condition_days']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['movie']['played']['count_equality']=merge['basic_settings']['filter_statements']['movie']['played']['count_equality']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['movie']['played']['count']=merge['basic_settings']['filter_statements']['movie']['played']['count']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['movie']['created']['condition_days']=merge['basic_settings']['filter_statements']['movie']['created']['condition_days']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['movie']['created']['count_equality']=merge['basic_settings']['filter_statements']['movie']['created']['count_equality']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['movie']['created']['count']=merge['basic_settings']['filter_statements']['movie']['created']['count']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['movie']['created']['behavioral_control']=merge['basic_settings']['filter_statements']['movie']['created']['behavioral_control']
    except:
        pass

    try:
        default_base['basic_settings']['filter_statements']['episode']['played']['condition_days']=merge['basic_settings']['filter_statements']['episode']['played']['condition_days']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['episode']['played']['count_equality']=merge['basic_settings']['filter_statements']['episode']['played']['count_equality']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['episode']['played']['count']=merge['basic_settings']['filter_statements']['episode']['played']['count']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['episode']['created']['condition_days']=merge['basic_settings']['filter_statements']['episode']['created']['condition_days']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['episode']['created']['count_equality']=merge['basic_settings']['filter_statements']['episode']['created']['count_equality']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['episode']['created']['count']=merge['basic_settings']['filter_statements']['episode']['created']['count']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['episode']['created']['behavioral_control']=merge['basic_settings']['filter_statements']['episode']['created']['behavioral_control']
    except:
        pass

    try:
        default_base['basic_settings']['filter_statements']['audio']['played']['condition_days']=merge['basic_settings']['filter_statements']['audio']['played']['condition_days']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['audio']['played']['count_equality']=merge['basic_settings']['filter_statements']['audio']['played']['count_equality']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['audio']['played']['count']=merge['basic_settings']['filter_statements']['audio']['played']['count']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['audio']['created']['condition_days']=merge['basic_settings']['filter_statements']['audio']['created']['condition_days']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['audio']['created']['count_equality']=merge['basic_settings']['filter_statements']['audio']['created']['count_equality']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['audio']['created']['count']=merge['basic_settings']['filter_statements']['audio']['created']['count']
    except:
        pass
    try:
        default_base['basic_settings']['filter_statements']['audio']['created']['behavioral_control']=merge['basic_settings']['filter_statements']['audio']['created']['behavioral_control']
    except:
        pass

    if (server_brand == 'jellyfin'):
        try:
            default_base['basic_settings']['filter_statements']['audiobook']['played']['condition_days']=merge['basic_settings']['filter_statements']['audiobook']['played']['condition_days']
        except:
            pass
        try:
            default_base['basic_settings']['filter_statements']['audiobook']['played']['count_equality']=merge['basic_settings']['filter_statements']['audiobook']['played']['count_equality']
        except:
            pass
        try:
            default_base['basic_settings']['filter_statements']['audiobook']['played']['count']=merge['basic_settings']['filter_statements']['audiobook']['played']['count']
        except:
            pass
        try:
            default_base['basic_settings']['filter_statements']['audiobook']['created']['condition_days']=merge['basic_settings']['filter_statements']['audiobook']['created']['condition_days']
        except:
            pass
        try:
            default_base['basic_settings']['filter_statements']['audiobook']['created']['count_equality']=merge['basic_settings']['filter_statements']['audiobook']['created']['count_equality']
        except:
            pass
        try:
            default_base['basic_settings']['filter_statements']['audiobook']['created']['count']=merge['basic_settings']['filter_statements']['audiobook']['created']['count']
        except:
            pass
        try:
            default_base['basic_settings']['filter_statements']['audiobook']['created']['behavioral_control']=merge['basic_settings']['filter_statements']['audiobook']['created']['behavioral_control']
        except:
            pass

    try:
        default_base['basic_settings']['filter_tags']['movie']['whitetags']=merge['basic_settings']['filter_tags']['movie']['whitetags']
    except:
        pass
    try:
        default_base['basic_settings']['filter_tags']['movie']['blacktags']=merge['basic_settings']['filter_tags']['movie']['blacktags']
    except:
        pass

    try:
        default_base['basic_settings']['filter_tags']['episode']['whitetags']=merge['basic_settings']['filter_tags']['episode']['whitetags']
    except:
        pass
    try:
        default_base['basic_settings']['filter_tags']['episode']['blacktags']=merge['basic_settings']['filter_tags']['episode']['blacktags']
    except:
        pass

    try:
        default_base['basic_settings']['filter_tags']['audio']['whitetags']=merge['basic_settings']['filter_tags']['audio']['whitetags']
    except:
        pass
    try:
        default_base['basic_settings']['filter_tags']['audio']['blacktags']=merge['basic_settings']['filter_tags']['audio']['blacktags']
    except:
        pass

    if (server_brand == 'jellyfin'):
        try:
            default_base['basic_settings']['filter_tags']['audiobook']['whitetags']=merge['basic_settings']['filter_tags']['audiobook']['whitetags']
        except:
            pass
        try:
            default_base['basic_settings']['filter_tags']['audiobook']['blacktags']=merge['basic_settings']['filter_tags']['audiobook']['blacktags']
        except:
            pass

    try:
        default_base['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['favorited']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['favorited']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['favorited']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['favorited'] & merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['whitetagged']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['whitetagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['whitetagged']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitetagged'] & merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['blacktagged']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['blacktagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['blacktagged']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacktagged'] & merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['whitelisted']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']
            except:
                pass
    try:
        default_base['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['favorited']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['favorited']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['favorited']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['favorited'] & merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['whitetagged']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['whitetagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['whitetagged']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['whitetagged'] & merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['blacktagged']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['blacktagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['blacktagged']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacktagged'] & merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['blacklisted']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']
            except:
                pass

    try:
        default_base['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['favorited']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['favorited']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['favorited']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['favorited'] & merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['whitetagged']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['whitetagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['whitetagged']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitetagged'] & merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['blacktagged']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['blacktagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['blacktagged']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacktagged'] & merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['whitelisted']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']
            except:
                pass
    try:
        default_base['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['favorited']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['favorited']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['favorited']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['favorited'] & merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['whitetagged']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['whitetagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['whitetagged']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['whitetagged'] & merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['blacktagged']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['blacktagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['blacktagged']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacktagged'] & merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['blacklisted']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']
            except:
                pass

    try:
        default_base['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['favorited']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['favorited']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['favorited']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['favorited'] & merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['whitetagged']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['whitetagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['whitetagged']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitetagged'] & merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['blacktagged']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['blacktagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['blacktagged']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacktagged'] & merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['whitelisted']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']
            except:
                pass
    try:
        default_base['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['favorited']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['favorited']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['favorited']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['favorited'] & merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['whitetagged']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['whitetagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['whitetagged']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['whitetagged'] & merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['blacktagged']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['blacktagged']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['blacktagged']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacktagged'] & merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']
        except:
            pass
    try:
        default_base['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']
    except:
        try:
            default_base['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['blacklisted']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']
            except:
                pass

    if (server_brand == 'jellyfin'):
        try:
            default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['favorited']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['favorited']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['favorited']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['favorited'] & merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']
            except:
                pass
        try:
            default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['whitetagged']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['whitetagged']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['whitetagged']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitetagged'] & merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']
            except:
                pass
        try:
            default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['blacktagged']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['blacktagged']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['blacktagged']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacktagged'] & merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']
            except:
                pass
        try:
            default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['whitelisted']
            except:
                try:
                    default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']
                except:
                    pass
        try:
            default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['favorited']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['favorited']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['favorited']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['favorited'] & merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']
            except:
                pass
        try:
            default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['whitetagged']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['whitetagged']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['whitetagged']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitetagged'] & merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']
            except:
                pass
        try:
            default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['blacktagged']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['blacktagged']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['blacktagged']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacktagged'] & merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']
            except:
                pass
        try:
            default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']
        except:
            try:
                default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['blacklisted']
            except:
                try:
                    default_base['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']=merge['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']
                except:
                    pass

    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['favorited']['action']=merge['advanced_settings']['behavioral_statements']['movie']['favorited']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['favorited']['user_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['favorited']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['favorited']['played_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['favorited']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['favorited']['action_control']=merge['advanced_settings']['behavioral_statements']['movie']['favorited']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['genre']=merge['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['genre']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['library_genre']=merge['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['library_genre']
    except:
        pass
    
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action']=merge['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitetagged']['user_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['whitetagged']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitetagged']['played_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['whitetagged']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action_control']=merge['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitetagged']['tags']=merge['advanced_settings']['behavioral_statements']['movie']['whitetagged']['tags']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action']=merge['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacktagged']['user_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['blacktagged']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacktagged']['played_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['blacktagged']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action_control']=merge['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacktagged']['tags']=merge['advanced_settings']['behavioral_statements']['movie']['blacktagged']['tags']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action']=merge['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitelisted']['user_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['whitelisted']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitelisted']['played_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['whitelisted']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action_control']=merge['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action']=merge['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacklisted']['user_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['blacklisted']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacklisted']['played_conditional']=merge['advanced_settings']['behavioral_statements']['movie']['blacklisted']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action_control']=merge['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['action']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['user_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['played_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['action_control']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['genre']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['genre']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['season_genre']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['season_genre']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['series_genre']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['series_genre']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['library_genre']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['library_genre']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network_genre']=merge['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network_genre']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action']=merge['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitetagged']['user_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['whitetagged']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitetagged']['played_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['whitetagged']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action_control']=merge['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitetagged']['tags']=merge['advanced_settings']['behavioral_statements']['episode']['whitetagged']['tags']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action']=merge['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacktagged']['user_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['blacktagged']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacktagged']['played_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['blacktagged']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action_control']=merge['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacktagged']['tags']=merge['advanced_settings']['behavioral_statements']['episode']['blacktagged']['tags']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action']=merge['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitelisted']['user_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['whitelisted']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitelisted']['played_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['whitelisted']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action_control']=merge['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action']=merge['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacklisted']['user_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['blacklisted']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacklisted']['played_conditional']=merge['advanced_settings']['behavioral_statements']['episode']['blacklisted']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action_control']=merge['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['action']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['action_control']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['genre']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['genre']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_genre']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_genre']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['library_genre']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['library_genre']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['track_artist']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['track_artist']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_artist']=merge['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_artist']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action']=merge['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitetagged']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['whitetagged']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitetagged']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['whitetagged']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action_control']=merge['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitetagged']['tags']=merge['advanced_settings']['behavioral_statements']['audio']['whitetagged']['tags']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action']=merge['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacktagged']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['blacktagged']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacktagged']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['blacktagged']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action_control']=merge['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacktagged']['tags']=merge['advanced_settings']['behavioral_statements']['audio']['blacktagged']['tags']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action']=merge['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitelisted']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['whitelisted']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitelisted']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['whitelisted']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action_control']=merge['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action']=merge['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacklisted']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['blacklisted']['user_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacklisted']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audio']['blacklisted']['played_conditional']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action_control']=merge['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action_control']
    except:
        pass
    try:
        default_base['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']
    except:
        pass

    #loop thru in reverse to preserve order
    if (server_brand == 'jellyfin'):
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['user_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['played_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action_control']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action_control']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['genre']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['genre']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['audiobook_genre']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['audiobook_genre']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_genre']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_genre']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['track_author']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['track_author']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['author']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['author']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_author']=merge['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_author']
        except:
            pass

        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['user_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['played_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action_control']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action_control']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['tags']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['tags']
        except:
            pass

        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['user_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['played_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action_control']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action_control']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['tags']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['tags']
        except:
            pass

        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['user_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['played_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action_control']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action_control']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']
        except:
            pass

        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['user_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['user_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['played_conditional']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['played_conditional']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action_control']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action_control']
        except:
            pass
        try:
            default_base['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']=merge['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']
        except:
            pass

    try:
        default_base['advanced_settings']['behavioral_tags']['movie']=merge['advanced_settings']['behavioral_tags']['movie']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_tags']['episode']=merge['advanced_settings']['behavioral_tags']['episode']
    except:
        pass

    try:
        default_base['advanced_settings']['behavioral_tags']['audio']=merge['advanced_settings']['behavioral_tags']['audio']
    except:
        pass

    if (server_brand == 'jellyfin'):

        try:
            default_base['advanced_settings']['behavioral_tags']['audiobook']=merge['advanced_settings']['behavioral_tags']['audiobook']
        except:
            pass

    '''
    #loop thru in reverse to preserve order
    #for thisTag in reversed(merge['advanced_settings']['behavioral_tags']['movie']):
    for thisTag in merge['advanced_settings']['behavioral_tags']['movie']:
        if (_:=get_isPlayedCreated_FilterStatementTag(thisTag)):
            try:
                ##save dictionary so behavioral tags are at the top and preserve the order they appear in the config
                #temp_dict=default_base['advanced_settings']['behavioral_tags']['movie'].copy()
                #default_base['advanced_settings']['behavioral_tags']['movie'].clear()
                #default_base['advanced_settings']['behavioral_tags']['movie'][thisTag]=merge['advanced_settings']['behavioral_tags']['movie'][thisTag]
                #default_base['advanced_settings']['behavioral_tags']['movie'].update(temp_dict)
                default_base['advanced_settings']['behavioral_tags']['movie'][thisTag].update(merge['advanced_settings']['behavioral_tags']['movie'][thisTag])
            except:
                #default_base['advanced_settings']['behavioral_tags']['movie'][thisTag]=None
                pass

    #loop thru in reverse to preserve order
    #for thisTag in reversed(merge['advanced_settings']['behavioral_tags']['episode']):
    for thisTag in merge['advanced_settings']['behavioral_tags']['episode']:
        if (_:=get_isPlayedCreated_FilterStatementTag(thisTag)):
            try:
                ##save dictionary so behavioral tags are at the top and preserve the order they appear in the config
                #temp_dict=default_base['advanced_settings']['behavioral_tags']['episode'].copy()
                #default_base['advanced_settings']['behavioral_tags']['episode'].clear()
                #default_base['advanced_settings']['behavioral_tags']['episode'][thisTag]=merge['advanced_settings']['behavioral_tags']['episode'][thisTag]
                #default_base['advanced_settings']['behavioral_tags']['episode'].update(temp_dict)
                default_base['advanced_settings']['behavioral_tags']['episode'][thisTag].update(merge['advanced_settings']['behavioral_tags']['episode'][thisTag])
            except:
                #default_base['advanced_settings']['behavioral_tags']['episode'][thisTag]=None
                pass

    #loop thru in reverse to preserve order
    #for thisTag in reversed(merge['advanced_settings']['behavioral_tags']['audio']):-
    for thisTag in merge['advanced_settings']['behavioral_tags']['audio']:
        if (_:=get_isPlayedCreated_FilterStatementTag(thisTag)):
            try:
                ##save dictionary so behavioral tags are at the top and preserve the order they appear in the config
                #temp_dict=default_base['advanced_settings']['behavioral_tags']['audio'].copy()
                #default_base['advanced_settings']['behavioral_tags']['audio'].clear()
                #default_base['advanced_settings']['behavioral_tags']['audio'][thisTag]=merge['advanced_settings']['behavioral_tags']['audio'][thisTag]
                #default_base['advanced_settings']['behavioral_tags']['audio'].update(temp_dict)
                default_base['advanced_settings']['behavioral_tags']['audio'][thisTag].update(merge['advanced_settings']['behavioral_tags']['audio'][thisTag])
            except:
                #default_base['advanced_settings']['behavioral_tags']['audio'][thisTag]=None
                pass

    #loop thru in reverse to preserve order
    if (server_brand == 'jellyfin'):
        #for thisTag in reversed(merge['advanced_settings']['behavioral_tags']['audiobook']):
        for thisTag in merge['advanced_settings']['behavioral_tags']['audiobook']:
            if (_:=get_isPlayedCreated_FilterStatementTag(thisTag)):
                try:
                    ##save dictionary so behavioral tags are at the top and preserve the order they appear in the config
                    #temp_dict=default_base['advanced_settings']['behavioral_tags']['audiobook'].copy()
                    #default_base['advanced_settings']['behavioral_tags']['audiobook'].clear()
                    #default_base['advanced_settings']['behavioral_tags']['audiobook'][thisTag]=merge['advanced_settings']['behavioral_tags']['audiobook'][thisTag]
                    #default_base['advanced_settings']['behavioral_tags']['audiobook'].update(temp_dict)
                    default_base['advanced_settings']['behavioral_tags']['audiobook'][thisTag].update(merge['advanced_settings']['behavioral_tags']['audiobook'][thisTag])
                except:
                    #default_base['advanced_settings']['behavioral_tags']['audiobook'][thisTag]=None
                    pass
    '''

    try:
        default_base['advanced_settings']['whitetags']=merge['advanced_settings']['whitetags']
    except:
        pass
    try:
        default_base['advanced_settings']['blacktags']=merge['advanced_settings']['blacktags']
    except:
        pass

    try:
        default_base['advanced_settings']['delete_empty_folders']['episode']['season']=merge['advanced_settings']['delete_empty_folders']['episode']['season']
    except:
        pass
    try:
        default_base['advanced_settings']['delete_empty_folders']['episode']['series']=merge['advanced_settings']['delete_empty_folders']['episode']['series']
    except:
        pass

    try:
        default_base['advanced_settings']['episode_control']['minimum_episodes']=merge['advanced_settings']['episode_control']['minimum_episodes']
    except:
        pass
    try:
        default_base['advanced_settings']['episode_control']['minimum_played_episodes']=merge['advanced_settings']['episode_control']['minimum_played_episodes']
    except:
        pass
    try:
        default_base['advanced_settings']['episode_control']['minimum_episodes_behavior']=merge['advanced_settings']['episode_control']['minimum_episodes_behavior']
    except:
        pass

    try:
        default_base['advanced_settings']['trakt_fix']['set_missing_last_played_date']['movie']=merge['advanced_settings']['trakt_fix']['set_missing_last_played_date']['movie']
    except:
        pass
    try:
        default_base['advanced_settings']['trakt_fix']['set_missing_last_played_date']['episode']=merge['advanced_settings']['trakt_fix']['set_missing_last_played_date']['episode']
    except:
        pass
    try:
        default_base['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audio']=merge['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audio']
    except:
        pass
    if (server_brand == 'jellyfin'):
        try:
            default_base['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audiobook']=merge['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audiobook']
        except:
            pass

    try:
        default_base['advanced_settings']['console_controls']['headers']['script']['show']=merge['advanced_settings']['console_controls']['headers']['script']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['headers']['script']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['headers']['script']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['headers']['user']['show']=merge['advanced_settings']['console_controls']['headers']['user']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['headers']['user']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['headers']['user']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['headers']['summary']['show']=merge['advanced_settings']['console_controls']['headers']['summary']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['headers']['summary']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['headers']['summary']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['footers']['script']['show']=merge['advanced_settings']['console_controls']['footers']['script']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['footers']['script']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['footers']['script']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['warnings']['script']['show']=merge['advanced_settings']['console_controls']['warnings']['script']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['warnings']['script']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['warnings']['script']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['movie']['delete']['show']=merge['advanced_settings']['console_controls']['movie']['delete']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['delete']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['movie']['delete']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['movie']['keep']['show']=merge['advanced_settings']['console_controls']['movie']['keep']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['keep']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['movie']['keep']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['movie']['post_processing']['show']=merge['advanced_settings']['console_controls']['movie']['post_processing']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['movie']['summary']['show']=merge['advanced_settings']['console_controls']['movie']['summary']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['movie']['summary']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['movie']['summary']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['episode']['delete']['show']=merge['advanced_settings']['console_controls']['episode']['delete']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['delete']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['episode']['delete']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['episode']['keep']['show']=merge['advanced_settings']['console_controls']['episode']['keep']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['keep']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['episode']['keep']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['episode']['post_processing']['show']=merge['advanced_settings']['console_controls']['episode']['post_processing']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['episode']['summary']['show']=merge['advanced_settings']['console_controls']['episode']['summary']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['episode']['summary']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['episode']['summary']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['audio']['delete']['show']=merge['advanced_settings']['console_controls']['audio']['delete']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['delete']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['audio']['delete']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['audio']['keep']['show']=merge['advanced_settings']['console_controls']['audio']['keep']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['keep']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['audio']['keep']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['audio']['post_processing']['show']=merge['advanced_settings']['console_controls']['audio']['post_processing']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['background']['color']
    except:
        pass

    try:
        default_base['advanced_settings']['console_controls']['audio']['summary']['show']=merge['advanced_settings']['console_controls']['audio']['summary']['show']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['color']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['style']
    except:
        pass
    try:
        default_base['advanced_settings']['console_controls']['audio']['summary']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['audio']['summary']['formatting']['background']['color']
    except:
        pass

    if (server_brand == 'jellyfin'):
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['delete']['show']=merge['advanced_settings']['console_controls']['audiobook']['delete']['show']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['color']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['style']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['background']['color']
        except:
            pass

        try:
            default_base['advanced_settings']['console_controls']['audiobook']['keep']['show']=merge['advanced_settings']['console_controls']['audiobook']['keep']['show']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['color']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['style']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['background']['color']
        except:
            pass

        try:
            default_base['advanced_settings']['console_controls']['audiobook']['post_processing']['show']=merge['advanced_settings']['console_controls']['audiobook']['post_processing']['show']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['color']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['style']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['background']['color']
        except:
            pass

        try:
            default_base['advanced_settings']['console_controls']['audiobook']['summary']['show']=merge['advanced_settings']['console_controls']['audiobook']['summary']['show']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['color']=merge['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['color']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['style']=merge['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['style']
        except:
            pass
        try:
            default_base['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['background']['color']=merge['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['background']['color']
        except:
            pass

    try:
        default_base['advanced_settings']['UPDATE_CONFIG']=merge['advanced_settings']['UPDATE_CONFIG']
    except:
        pass
    try:
        default_base['advanced_settings']['REMOVE_FILES']=merge['advanced_settings']['REMOVE_FILES']
    except:
        error_found_in_mumc_config_yaml+='ConfigNameError: advanced_settings > REMOVE_FILES is missing from the mumc_config.yaml\n'

    try:
        default_base['admin_settings']['behavior']['list']=merge['admin_settings']['behavior']['list']
    except:
        pass
    try:
        default_base['admin_settings']['behavior']['matching']=merge['admin_settings']['behavior']['matching']
    except:
        pass
    try:
        default_base['admin_settings']['behavior']['users']['monitor_disabled']=merge['admin_settings']['behavior']['users']['monitor_disabled']
    except:
        pass

    default_base['admin_settings']['server']['brand']=server_brand
    try:
        default_base['admin_settings']['server']['url']=merge['admin_settings']['server']['url']
    except:
        error_found_in_mumc_config_yaml+='ConfigNameError: admin_settings > server > url is missing from the mumc_config.yaml\n'
    try:
        default_base['admin_settings']['server']['auth_key']=merge['admin_settings']['server']['auth_key']
    except:
        error_found_in_mumc_config_yaml+='ConfigNameError: admin_settings > server > auth_key is missing from the mumc_config.yaml\n'
    try:
        default_base['admin_settings']['server']['admin_id']=merge['admin_settings']['server']['admin_id']
    except:
        pass
        #error_found_in_mumc_config_yaml+='ConfigNameError: admin_settings > server > admin_id is missing from the mumc_config.yaml\n'

    try:
        default_base['admin_settings']['users']=merge['admin_settings']['users']
    except:
        error_found_in_mumc_config_yaml+='ConfigNameError: admin_settings > users is missing from the mumc_config.yaml\n'

    try:
        default_base['admin_settings']['api_controls']['attempts']=merge['admin_settings']['api_controls']['attempts']
    except:
        pass
    try:
        default_base['admin_settings']['api_controls']['item_limit']=merge['admin_settings']['api_controls']['item_limit']
    except:
        pass

    try:
        default_base['admin_settings']['cache']['size']=merge['admin_settings']['cache']['size']
    except:
        pass
    try:
        default_base['admin_settings']['cache']['fallback_behavior']=merge['admin_settings']['cache']['fallback_behavior']
    except:
        pass
    try:
        default_base['admin_settings']['cache']['minimum_age']=merge['admin_settings']['cache']['minimum_age']
    except:
        try:
            default_base['admin_settings']['cache']['minimum_age']=merge['admin_settings']['cache']['last_accessed_time']
        except:
            pass

    try:
        default_base['admin_settings']['output_controls']['character_limit']['print']=merge['admin_settings']['output_controls']['character_limit']['print']
    except:
        pass
    #try:
        #default_base['admin_settings']['output_controls']['character_limit']['write']=merge['admin_settings']['output_controls']['character_limit']['write']
    #except:
        #pass

    #Bring all errors found to users attention
    if (not (error_found_in_mumc_config_yaml == '')):
        if (default_base['DEBUG']):
            appendTo_DEBUG_log("\n" + error_found_in_mumc_config_yaml,2,default_base)
        print('\n' + error_found_in_mumc_config_yaml)
        sys.exit(0)

    #before saving; reorder some keys for consistency
    default_base['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']=default_base['advanced_settings']['behavioral_statements']['movie']['favorited'].pop('extra')
    default_base['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']=default_base['advanced_settings']['behavioral_statements']['episode']['favorited'].pop('extra')
    default_base['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']=default_base['advanced_settings']['behavioral_statements']['audio']['favorited'].pop('extra')
    if (server_brand == 'jellyfin'):
        default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']=default_base['advanced_settings']['behavioral_statements']['audiobook']['favorited'].pop('extra')

    return default_base