import copy
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_console_info import print_config_options_added_warning,print_config_options_removed_warning


def add_minium_age_to_yaml(missing_minimum_age_dict,init_dict,cfg):
    temp_dict={}
    temp_dict['admin_settings']={}
    temp_dict['admin_settings']['cache']={}

    temp_dict['admin_settings']['cache']=copy.deepcopy(cfg['admin_settings']['cache'])

    cfg['admin_settings']['cache']={}
    cfg['admin_settings']['cache']['size']=temp_dict['admin_settings']['cache']['size']
    cfg['admin_settings']['cache']['fallback_behavior']=temp_dict['admin_settings']['cache']['fallback_behavior']
    cfg['admin_settings']['cache']['minimum_age']=missing_minimum_age_dict['admin_settings']['cache']['minimum_age']

    init_dict['advanced_settings']={}
    init_dict['advanced_settings'].update(cfg['advanced_settings'])

    #Notify user of graceful config changes
    print_config_options_added_warning(init_dict,'admin_settings','cache','minimum_age')
    print_config_options_removed_warning(init_dict,'admin_settings','cache','last_accessed_time')

    return cfg


def add_query_filter_to_yaml(missing_query_filter_dict,init_dict,cfg):
    temp_dict=copy.deepcopy(cfg['advanced_settings'])
    cfg['advanced_settings']={}
    cfg['advanced_settings'].update(missing_query_filter_dict['advanced_settings'])
    cfg['advanced_settings']['behavioral_statements']={}
    cfg['advanced_settings']['behavioral_statements'].update(temp_dict['behavioral_statements'])
    cfg['advanced_settings']['whitetags']=[]
    cfg['advanced_settings']['whitetags'].extend(temp_dict['whitetags'])
    cfg['advanced_settings']['blacktags']=[]
    cfg['advanced_settings']['blacktags'].extend(temp_dict['blacktags'])
    cfg['advanced_settings']['episode_control']={}
    cfg['advanced_settings']['episode_control'].update(temp_dict['episode_control'])
    cfg['advanced_settings']['trakt_fix']={}
    cfg['advanced_settings']['trakt_fix'].update(temp_dict['trakt_fix'])
    cfg['advanced_settings']['console_controls']={}
    cfg['advanced_settings']['console_controls'].update(temp_dict['console_controls'])
    cfg['advanced_settings']['UPDATE_CONFIG']=temp_dict['UPDATE_CONFIG']
    cfg['advanced_settings']['REMOVE_FILES']=temp_dict['REMOVE_FILES']

    init_dict['advanced_settings']={}
    init_dict['advanced_settings'].update(cfg['advanced_settings'])

    #Notify user of graceful config changes
    print_config_options_added_warning(init_dict,'advanced_settings','filter_statements','etc...')
        
    return cfg


def add_dynamic_behavior_to_yaml(missing_dynamic_behavior_dict,server_brand,init_dict,cfg):
    temp_dict=copy.deepcopy(cfg['advanced_settings'])
    cfg['advanced_settings']={}
    cfg['advanced_settings']['filter_statements']={}
    cfg['advanced_settings']['filter_statements'].update(temp_dict['filter_statements'])
    cfg['advanced_settings']['behavioral_statements']={}
    cfg['advanced_settings']['behavioral_statements']['movie']={}
    cfg['advanced_settings']['behavioral_statements']['movie']['favorited']={}
    cfg['advanced_settings']['behavioral_statements']['movie']['favorited']['action']=temp_dict['behavioral_statements']['movie']['favorited']['action']
    cfg['advanced_settings']['behavioral_statements']['movie']['favorited']['user_conditional']=temp_dict['behavioral_statements']['movie']['favorited']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['favorited']['played_conditional']=temp_dict['behavioral_statements']['movie']['favorited']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['favorited']['action_control']=temp_dict['behavioral_statements']['movie']['favorited']['action_control']
    cfg['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']=temp_dict['behavioral_statements']['movie']['favorited']['extra']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitetagged']={}
    cfg['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action']=temp_dict['behavioral_statements']['movie']['whitetagged']['action']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitetagged']['user_conditional']=temp_dict['behavioral_statements']['movie']['whitetagged']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitetagged']['played_conditional']=temp_dict['behavioral_statements']['movie']['whitetagged']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action_control']=temp_dict['behavioral_statements']['movie']['whitetagged']['action_control']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitetagged']['tags']=temp_dict['behavioral_statements']['movie']['whitetagged']['tags']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacktagged']={}
    cfg['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action']=temp_dict['behavioral_statements']['movie']['blacktagged']['action']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacktagged']['user_conditional']=temp_dict['behavioral_statements']['movie']['blacktagged']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacktagged']['played_conditional']=temp_dict['behavioral_statements']['movie']['blacktagged']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action_control']=temp_dict['behavioral_statements']['movie']['blacktagged']['action_control']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacktagged']['tags']=temp_dict['behavioral_statements']['movie']['blacktagged']['tags']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitelisted']={}
    cfg['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action']=temp_dict['behavioral_statements']['movie']['whitelisted']['action']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitelisted']['user_conditional']=temp_dict['behavioral_statements']['movie']['whitelisted']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitelisted']['played_conditional']=temp_dict['behavioral_statements']['movie']['whitelisted']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action_control']=temp_dict['behavioral_statements']['movie']['whitelisted']['action_control']
    cfg['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacklisted']={}
    cfg['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action']=temp_dict['behavioral_statements']['movie']['blacklisted']['action']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacklisted']['user_conditional']=temp_dict['behavioral_statements']['movie']['blacklisted']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacklisted']['played_conditional']=temp_dict['behavioral_statements']['movie']['blacklisted']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action_control']=temp_dict['behavioral_statements']['movie']['blacklisted']['action_control']
    cfg['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['episode']={}
    cfg['advanced_settings']['behavioral_statements']['episode']['favorited']={}
    cfg['advanced_settings']['behavioral_statements']['episode']['favorited']['action']=temp_dict['behavioral_statements']['episode']['favorited']['action']
    cfg['advanced_settings']['behavioral_statements']['episode']['favorited']['user_conditional']=temp_dict['behavioral_statements']['episode']['favorited']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['favorited']['played_conditional']=temp_dict['behavioral_statements']['episode']['favorited']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['favorited']['action_control']=temp_dict['behavioral_statements']['episode']['favorited']['action_control']
    cfg['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']=temp_dict['behavioral_statements']['episode']['favorited']['extra']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitetagged']={}
    cfg['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action']=temp_dict['behavioral_statements']['episode']['whitetagged']['action']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitetagged']['user_conditional']=temp_dict['behavioral_statements']['episode']['whitetagged']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitetagged']['played_conditional']=temp_dict['behavioral_statements']['episode']['whitetagged']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action_control']=temp_dict['behavioral_statements']['episode']['whitetagged']['action_control']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitetagged']['tags']=temp_dict['behavioral_statements']['episode']['whitetagged']['tags']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacktagged']={}
    cfg['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action']=temp_dict['behavioral_statements']['episode']['blacktagged']['action']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacktagged']['user_conditional']=temp_dict['behavioral_statements']['episode']['blacktagged']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacktagged']['played_conditional']=temp_dict['behavioral_statements']['episode']['blacktagged']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action_control']=temp_dict['behavioral_statements']['episode']['blacktagged']['action_control']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacktagged']['tags']=temp_dict['behavioral_statements']['episode']['blacktagged']['tags']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitelisted']={}
    cfg['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action']=temp_dict['behavioral_statements']['episode']['whitelisted']['action']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitelisted']['user_conditional']=temp_dict['behavioral_statements']['episode']['whitelisted']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitelisted']['played_conditional']=temp_dict['behavioral_statements']['episode']['whitelisted']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action_control']=temp_dict['behavioral_statements']['episode']['whitelisted']['action_control']
    cfg['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacklisted']={}
    cfg['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action']=temp_dict['behavioral_statements']['episode']['blacklisted']['action']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacklisted']['user_conditional']=temp_dict['behavioral_statements']['episode']['blacklisted']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacklisted']['played_conditional']=temp_dict['behavioral_statements']['episode']['blacklisted']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action_control']=temp_dict['behavioral_statements']['episode']['blacklisted']['action_control']
    cfg['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['audio']={}
    cfg['advanced_settings']['behavioral_statements']['audio']['favorited']={}
    cfg['advanced_settings']['behavioral_statements']['audio']['favorited']['action']=temp_dict['behavioral_statements']['audio']['favorited']['action']
    cfg['advanced_settings']['behavioral_statements']['audio']['favorited']['user_conditional']=temp_dict['behavioral_statements']['audio']['favorited']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['favorited']['played_conditional']=temp_dict['behavioral_statements']['audio']['favorited']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['favorited']['action_control']=temp_dict['behavioral_statements']['audio']['favorited']['action_control']
    cfg['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']=temp_dict['behavioral_statements']['audio']['favorited']['extra']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitetagged']={}
    cfg['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action']=temp_dict['behavioral_statements']['audio']['whitetagged']['action']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitetagged']['user_conditional']=temp_dict['behavioral_statements']['audio']['whitetagged']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitetagged']['played_conditional']=temp_dict['behavioral_statements']['audio']['whitetagged']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action_control']=temp_dict['behavioral_statements']['audio']['whitetagged']['action_control']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitetagged']['tags']=temp_dict['behavioral_statements']['audio']['whitetagged']['tags']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacktagged']={}
    cfg['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action']=temp_dict['behavioral_statements']['audio']['blacktagged']['action']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacktagged']['user_conditional']=temp_dict['behavioral_statements']['audio']['blacktagged']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacktagged']['played_conditional']=temp_dict['behavioral_statements']['audio']['blacktagged']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action_control']=temp_dict['behavioral_statements']['audio']['blacktagged']['action_control']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacktagged']['tags']=temp_dict['behavioral_statements']['audio']['blacktagged']['tags']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitelisted']={}
    cfg['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action']=temp_dict['behavioral_statements']['audio']['whitelisted']['action']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitelisted']['user_conditional']=temp_dict['behavioral_statements']['audio']['whitelisted']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitelisted']['played_conditional']=temp_dict['behavioral_statements']['audio']['whitelisted']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action_control']=temp_dict['behavioral_statements']['audio']['whitelisted']['action_control']
    cfg['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacklisted']={}
    cfg['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action']=temp_dict['behavioral_statements']['audio']['blacklisted']['action']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacklisted']['user_conditional']=temp_dict['behavioral_statements']['audio']['blacklisted']['user_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacklisted']['played_conditional']=temp_dict['behavioral_statements']['audio']['blacklisted']['played_conditional']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action_control']=temp_dict['behavioral_statements']['audio']['blacklisted']['action_control']
    cfg['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']
    if (isJellyfinServer(server_brand)):
        cfg['advanced_settings']['behavioral_statements']['audiobook']={}
        cfg['advanced_settings']['behavioral_statements']['audiobook']['favorited']={}
        cfg['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action']=temp_dict['behavioral_statements']['audiobook']['favorited']['action']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['favorited']['user_conditional']=temp_dict['behavioral_statements']['audiobook']['favorited']['user_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['favorited']['played_conditional']=temp_dict['behavioral_statements']['audiobook']['favorited']['played_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action_control']=temp_dict['behavioral_statements']['audiobook']['favorited']['action_control']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']=temp_dict['behavioral_statements']['audiobook']['favorited']['extra']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']={}
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action']=temp_dict['behavioral_statements']['audiobook']['whitetagged']['action']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['user_conditional']=temp_dict['behavioral_statements']['audiobook']['whitetagged']['user_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['played_conditional']=temp_dict['behavioral_statements']['audiobook']['whitetagged']['played_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action_control']=temp_dict['behavioral_statements']['audiobook']['whitetagged']['action_control']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['tags']=temp_dict['behavioral_statements']['audiobook']['whitetagged']['tags']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']={}
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action']=temp_dict['behavioral_statements']['audiobook']['blacktagged']['action']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['user_conditional']=temp_dict['behavioral_statements']['audiobook']['blacktagged']['user_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['played_conditional']=temp_dict['behavioral_statements']['audiobook']['blacktagged']['played_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action_control']=temp_dict['behavioral_statements']['audiobook']['blacktagged']['action_control']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['tags']=temp_dict['behavioral_statements']['audiobook']['blacktagged']['tags']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']={}
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action']=temp_dict['behavioral_statements']['audiobook']['whitelisted']['action']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['user_conditional']=temp_dict['behavioral_statements']['audiobook']['whitelisted']['user_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['played_conditional']=temp_dict['behavioral_statements']['audiobook']['whitelisted']['played_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action_control']=temp_dict['behavioral_statements']['audiobook']['whitelisted']['action_control']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']={}
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action']=temp_dict['behavioral_statements']['audiobook']['blacklisted']['action']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['user_conditional']=temp_dict['behavioral_statements']['audiobook']['blacklisted']['user_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['played_conditional']=temp_dict['behavioral_statements']['audiobook']['blacklisted']['played_conditional']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action_control']=temp_dict['behavioral_statements']['audiobook']['blacklisted']['action_control']
        cfg['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']=missing_dynamic_behavior_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']
    cfg['advanced_settings']['whitetags']=[]
    cfg['advanced_settings']['whitetags'].extend(temp_dict['whitetags'])
    cfg['advanced_settings']['blacktags']=[]
    cfg['advanced_settings']['blacktags'].extend(temp_dict['blacktags'])
    cfg['advanced_settings']['episode_control']={}
    cfg['advanced_settings']['episode_control'].update(temp_dict['episode_control'])
    cfg['advanced_settings']['trakt_fix']={}
    cfg['advanced_settings']['trakt_fix'].update(temp_dict['trakt_fix'])
    cfg['advanced_settings']['console_controls']={}
    cfg['advanced_settings']['console_controls'].update(temp_dict['console_controls'])
    cfg['advanced_settings']['UPDATE_CONFIG']=temp_dict['UPDATE_CONFIG']
    cfg['advanced_settings']['REMOVE_FILES']=temp_dict['REMOVE_FILES']

    init_dict['advanced_settings']={}
    init_dict['advanced_settings'].update(cfg['advanced_settings'])

    #Notify user of graceful config changes
    print_config_options_added_warning(init_dict,'advanced_settings','behavioral_statements','\'media_type\'','\'conditional_behavior\'','dynamic_behavior')

    return cfg


def add_monitor_disabled_users_to_yaml(missing_monitor_disabled_users_dict,init_dict,cfg):
    temp_dict={}
    temp_dict['admin_settings']={}
    temp_dict['admin_settings']['behavior']={}

    temp_dict['admin_settings']['behavior']=copy.deepcopy(cfg['admin_settings']['behavior'])

    cfg['admin_settings']['behavior']={}
    cfg['admin_settings']['behavior']['list']=temp_dict['admin_settings']['behavior']['list']
    cfg['admin_settings']['behavior']['matching']=temp_dict['admin_settings']['behavior']['matching']
    cfg['admin_settings']['behavior']['users']={}
    cfg['admin_settings']['behavior']['users']['monitor_disabled']=missing_monitor_disabled_users_dict['admin_settings']['behavior']['users']['monitor_disabled']

    init_dict['advanced_settings']={}
    init_dict['advanced_settings'].update(cfg['advanced_settings'])

    #Notify user of graceful config changes
    print_config_options_added_warning(init_dict,'admin_settings','behavior','users','monitor_disabled')

    return cfg


def add_admin_id_to_yaml(missing_admin_id_dict,init_dict,cfg):
    temp_dict={}
    temp_dict['admin_settings']={}
    temp_dict['admin_settings']['server']={}

    temp_dict['admin_settings']['server']=copy.deepcopy(cfg['admin_settings']['server'])

    cfg['admin_settings']['server']['admin_id']=missing_admin_id_dict['admin_settings']['server']['admin_id']

    init_dict['advanced_settings']={}
    init_dict['advanced_settings'].update(cfg['advanced_settings'])

    return cfg

def add_delete_season_folder_to_yaml(missing_delete_season_folder_dict,init_dict,cfg):
    temp_dict=copy.deepcopy(cfg['advanced_settings'])
    cfg['advanced_settings']={}
    cfg['advanced_settings']['filter_statements']={}
    cfg['advanced_settings']['filter_statements'].update(temp_dict['filter_statements'])
    cfg['advanced_settings']['behavioral_statements']={}
    cfg['advanced_settings']['behavioral_statements'].update(temp_dict['behavioral_statements'])
    cfg['advanced_settings']['whitetags']=[]
    cfg['advanced_settings']['whitetags'].extend(temp_dict['whitetags'])
    cfg['advanced_settings']['blacktags']=[]
    cfg['advanced_settings']['blacktags'].extend(temp_dict['blacktags'])
    cfg['advanced_settings']['delete_empty_folders']={}
    cfg['advanced_settings']['delete_empty_folders']['episode']={}
    cfg['advanced_settings']['delete_empty_folders']['episode']['season']=missing_delete_season_folder_dict['advanced_settings']['delete_empty_folders']['episode']['season']
    try:
        cfg['advanced_settings']['delete_empty_folders']['episode']['series']=temp_dict['delete_empty_folders']['episode']['series']
    except (KeyError):
        pass
    cfg['advanced_settings']['episode_control']={}
    cfg['advanced_settings']['episode_control'].update(temp_dict['episode_control'])
    cfg['advanced_settings']['trakt_fix']={}
    cfg['advanced_settings']['trakt_fix'].update(temp_dict['trakt_fix'])
    cfg['advanced_settings']['console_controls']={}
    cfg['advanced_settings']['console_controls'].update(temp_dict['console_controls'])
    cfg['advanced_settings']['UPDATE_CONFIG']=temp_dict['UPDATE_CONFIG']
    cfg['advanced_settings']['REMOVE_FILES']=temp_dict['REMOVE_FILES']

    init_dict['advanced_settings']={}
    init_dict['advanced_settings'].update(cfg['advanced_settings'])

    #Notify user of graceful config changes
    print_config_options_added_warning(init_dict,'advanced_settings','delete_empty_folders','episode','season')

    return cfg


def add_delete_series_folder_to_yaml(missing_delete_series_folder_dict,init_dict,cfg):
    temp_dict=copy.deepcopy(cfg['advanced_settings'])
    cfg['advanced_settings']={}
    cfg['advanced_settings']['filter_statements']={}
    cfg['advanced_settings']['filter_statements'].update(temp_dict['filter_statements'])
    cfg['advanced_settings']['behavioral_statements']={}
    cfg['advanced_settings']['behavioral_statements'].update(temp_dict['behavioral_statements'])
    cfg['advanced_settings']['whitetags']=[]
    cfg['advanced_settings']['whitetags'].extend(temp_dict['whitetags'])
    cfg['advanced_settings']['blacktags']=[]
    cfg['advanced_settings']['blacktags'].extend(temp_dict['blacktags'])
    cfg['advanced_settings']['delete_empty_folders']={}
    cfg['advanced_settings']['delete_empty_folders']['episode']={}
    try:
        cfg['advanced_settings']['delete_empty_folders']['episode']['season']=temp_dict['delete_empty_folders']['episode']['season']
    except (KeyError):
        pass
    cfg['advanced_settings']['delete_empty_folders']['episode']['series']=missing_delete_series_folder_dict['advanced_settings']['delete_empty_folders']['episode']['series']
    cfg['advanced_settings']['episode_control']={}
    cfg['advanced_settings']['episode_control'].update(temp_dict['episode_control'])
    cfg['advanced_settings']['trakt_fix']={}
    cfg['advanced_settings']['trakt_fix'].update(temp_dict['trakt_fix'])
    cfg['advanced_settings']['console_controls']={}
    cfg['advanced_settings']['console_controls'].update(temp_dict['console_controls'])
    cfg['advanced_settings']['UPDATE_CONFIG']=temp_dict['UPDATE_CONFIG']
    cfg['advanced_settings']['REMOVE_FILES']=temp_dict['REMOVE_FILES']

    init_dict['advanced_settings']={}
    init_dict['advanced_settings'].update(cfg['advanced_settings'])

    #Notify user of graceful config changes
    print_config_options_added_warning(init_dict,'advanced_settings','delete_empty_folders','episode','series')

    return cfg