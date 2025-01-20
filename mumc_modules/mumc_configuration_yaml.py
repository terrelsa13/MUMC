import copy
from mumc_modules.mumc_output import save_yaml_config,print2json


def filterYAMLConfigKeys_ToKeep(dirty_dict,*clean_keys):

    return {cleanKey:dirty_dict[cleanKey] for cleanKey in clean_keys}


def yaml_configurationLayout(config_data,server_brand):

    #start building config yaml
    config_data['basic_settings']['filter_statements']['movie']['played']['condition_days']=-1
    config_data['basic_settings']['filter_statements']['movie']['played']['count_equality']='>='
    config_data['basic_settings']['filter_statements']['movie']['played']['count']=1
    config_data['basic_settings']['filter_statements']['movie']['created']['condition_days']=-1
    config_data['basic_settings']['filter_statements']['movie']['created']['count_equality']='>='
    config_data['basic_settings']['filter_statements']['movie']['created']['count']=1
    config_data['basic_settings']['filter_statements']['movie']['created']['behavioral_control']=True

    config_data['basic_settings']['filter_statements']['episode']['played']['condition_days']=-1
    config_data['basic_settings']['filter_statements']['episode']['played']['count_equality']='>='
    config_data['basic_settings']['filter_statements']['episode']['played']['count']=1
    config_data['basic_settings']['filter_statements']['episode']['created']['condition_days']=-1
    config_data['basic_settings']['filter_statements']['episode']['created']['count_equality']='>='
    config_data['basic_settings']['filter_statements']['episode']['created']['count']=1
    config_data['basic_settings']['filter_statements']['episode']['created']['behavioral_control']=True

    config_data['basic_settings']['filter_statements']['audio']['played']['condition_days']=-1
    config_data['basic_settings']['filter_statements']['audio']['played']['count_equality']='>='
    config_data['basic_settings']['filter_statements']['audio']['played']['count']=1
    config_data['basic_settings']['filter_statements']['audio']['created']['condition_days']=-1
    config_data['basic_settings']['filter_statements']['audio']['created']['count_equality']='>='
    config_data['basic_settings']['filter_statements']['audio']['created']['count']=1
    config_data['basic_settings']['filter_statements']['audio']['created']['behavioral_control']=True

    if (server_brand == 'jellyfin'):
        config_data['basic_settings']['filter_statements']['audiobook']['played']['condition_days']=-1
        config_data['basic_settings']['filter_statements']['audiobook']['played']['count_equality']='>='
        config_data['basic_settings']['filter_statements']['audiobook']['played']['count']=1
        config_data['basic_settings']['filter_statements']['audiobook']['created']['condition_days']=-1
        config_data['basic_settings']['filter_statements']['audiobook']['created']['count_equality']='>='
        config_data['basic_settings']['filter_statements']['audiobook']['created']['count']=1
        config_data['basic_settings']['filter_statements']['audiobook']['created']['behavioral_control']=True

    #INTENTIONALLY COMMENTED OUT
    #config_data['basic_settings']['filter_tags']['movie']['whitetags']=[]
    #config_data['basic_settings']['filter_tags']['movie']['blacktags']=[]
    #config_data['basic_settings']['filter_tags']['episode']['whitetags']=[]
    #config_data['basic_settings']['filter_tags']['episode']['blacktags']=[]
    #config_data['basic_settings']['filter_tags']['audio']['whitetags']=[]
    #config_data['basic_settings']['filter_tags']['audio']['blacktags']=[]
    #if (server_brand == 'jellyfin'):
        #config_data['basic_settings']['filter_tags']['audiobook']['whitetags']=[]
        #config_data['basic_settings']['filter_tags']['audiobook']['blacktags']=[]

    config_data['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['favorited']=False
    config_data['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['whitetagged']=False
    config_data['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['blacktagged']=True
    config_data['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']['played']=False

    config_data['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['favorited']=True
    config_data['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['whitetagged']=False
    config_data['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['blacktagged']=True
    config_data['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']['played']=True

    config_data['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['favorited']=False
    config_data['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['whitetagged']=False
    config_data['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['blacktagged']=True
    config_data['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']['played']=False

    config_data['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['favorited']=True
    config_data['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['whitetagged']=False
    config_data['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['blacktagged']=True
    config_data['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']['played']=True

    config_data['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['favorited']=False
    config_data['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['whitetagged']=False
    config_data['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['blacktagged']=True
    config_data['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']['played']=False

    config_data['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['favorited']=True
    config_data['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['whitetagged']=False
    config_data['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['blacktagged']=True
    config_data['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']['played']=True

    if (server_brand == 'jellyfin'):
        config_data['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['favorited']=False
        config_data['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['whitetagged']=False
        config_data['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['blacktagged']=True
        config_data['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']['played']=False

        config_data['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['favorited']=True
        config_data['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['whitetagged']=False
        config_data['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['blacktagged']=True
        config_data['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']['played']=True

    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['action']='keep'
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['user_conditional']='any'
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['played_conditional']='ignore'
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['action_control']=3
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']=False
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['genre']=0
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['library_genre']=0

    config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action']='keep'
    config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['user_conditional']='all'
    config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['played_conditional']='ignore'
    config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action_control']=0
    config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']=False
    #INTENTIONALLY COMMENTED OUT
    #config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['tags']=[]

    config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action']='delete'
    config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['user_conditional']='all'
    config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['played_conditional']='any_played'
    config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action_control']=0
    config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']=False
    #INTENTIONALLY COMMENTED OUT
    #config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['tags']=[]

    config_data['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action']='keep'
    config_data['advanced_settings']['behavioral_statements']['movie']['whitelisted']['user_conditional']='any'
    config_data['advanced_settings']['behavioral_statements']['movie']['whitelisted']['played_conditional']='ignore'
    config_data['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action_control']=3
    config_data['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']=False

    config_data['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action']='delete'
    config_data['advanced_settings']['behavioral_statements']['movie']['blacklisted']['user_conditional']='any'
    config_data['advanced_settings']['behavioral_statements']['movie']['blacklisted']['played_conditional']='any_played'
    config_data['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action_control']=3
    config_data['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']=False
    
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['action']='keep'
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['user_conditional']='any'
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['played_conditional']='ignore'
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['action_control']=3
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']=False
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['genre']=0
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['season_genre']=0
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['series_genre']=0
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['library_genre']=0
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network']=0
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network_genre']=0

    config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action']='keep'
    config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['user_conditional']='all'
    config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['played_conditional']='ignore'
    config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action_control']=0
    config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']=False
    #INTENTIONALLY COMMENTED OUT
    #config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['tags']=[]

    config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action']='delete'
    config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['user_conditional']='all'
    config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['played_conditional']='any_played'
    config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action_control']=0
    config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']=False
    #INTENTIONALLY COMMENTED OUT
    #config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['tags']=[]

    config_data['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action']='keep'
    config_data['advanced_settings']['behavioral_statements']['episode']['whitelisted']['user_conditional']='any'
    config_data['advanced_settings']['behavioral_statements']['episode']['whitelisted']['played_conditional']='ignore'
    config_data['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action_control']=3
    config_data['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']=False

    config_data['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action']='delete'
    config_data['advanced_settings']['behavioral_statements']['episode']['blacklisted']['user_conditional']='any'
    config_data['advanced_settings']['behavioral_statements']['episode']['blacklisted']['played_conditional']='any_played'
    config_data['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action_control']=3
    config_data['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']=False

    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['action']='keep'
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['user_conditional']='any'
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['played_conditional']='ignore'
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['action_control']=3
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']=False
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['genre']=0
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_genre']=0
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['library_genre']=0
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['track_artist']=0
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_artist']=0

    config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action']='keep'
    config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['user_conditional']='all'
    config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['played_conditional']='ignore'
    config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action_control']=0
    config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']=False
    #INTENTIONALLY COMMENTED OUT
    #config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['tags']=[]

    config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action']='delete'
    config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['user_conditional']='all'
    config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['played_conditional']='any_played'
    config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action_control']=0
    config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']=False
    #INTENTIONALLY COMMENTED OUT
    #config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['tags']=[]

    config_data['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action']='keep'
    config_data['advanced_settings']['behavioral_statements']['audio']['whitelisted']['user_conditional']='any'
    config_data['advanced_settings']['behavioral_statements']['audio']['whitelisted']['played_conditional']='ignore'
    config_data['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action_control']=3
    config_data['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']=False

    config_data['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action']='delete'
    config_data['advanced_settings']['behavioral_statements']['audio']['blacklisted']['user_conditional']='any'
    config_data['advanced_settings']['behavioral_statements']['audio']['blacklisted']['played_conditional']='any_played'
    config_data['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action_control']=3
    config_data['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']=False

    if (server_brand == 'jellyfin'):
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action']='keep'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['user_conditional']='any'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['played_conditional']='ignore'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action_control']=3
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']=False
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['genre']=0
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['audiobook_genre']=0
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_genre']=0
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['track_author']=0
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['author']=0
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_author']=0

        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action']='keep'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['user_conditional']='all'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['played_conditional']='ignore'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action_control']=0
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=False
        #INTENTIONALLY COMMENTED OUT
        #config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['tags']=[]

        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action']='delete'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['user_conditional']='all'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['played_conditional']='any_played'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action_control']=0
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']=False
        #INTENTIONALLY COMMENTED OUT
        #config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['tags']=[]

        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action']='keep'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['user_conditional']='any'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['played_conditional']='ignore'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action_control']=3
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']=False

        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action']='delete'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['user_conditional']='any'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['played_conditional']='any_played'
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action_control']=3
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']=False

    #INTENTIONALLY COMMENTED OUT
    #config_data['advanced_settings']['behavioral_tags']['movie']['played:-1:>=:1']['action']='keep'
    #config_data['advanced_settings']['behavioral_tags']['movie']['played:-1:>=:1']['user_conditional']='all'
    #config_data['advanced_settings']['behavioral_tags']['movie']['played:-1:>=:1']['played_conditional']='ignore'
    #config_data['advanced_settings']['behavioral_tags']['movie']['played:-1:>=:1']['action_control']=0
    #config_data['advanced_settings']['behavioral_tags']['movie']['played:-1:>=:1']['dynamic_behavior']=False
    #config_data['advanced_settings']['behavioral_tags']['movie']['played:-1:>=:1']['high_priority']=False

    #config_data['advanced_settings']['behavioral_tags']['movie']['created:-1:>=:1:true']['action']='keep'
    #config_data['advanced_settings']['behavioral_tags']['movie']['created:-1:>=:1:true']['user_conditional']='all'
    #config_data['advanced_settings']['behavioral_tags']['movie']['created:-1:>=:1:true']['played_conditional']='ignore'
    #config_data['advanced_settings']['behavioral_tags']['movie']['created:-1:>=:1:true']['action_control']=0
    #config_data['advanced_settings']['behavioral_tags']['movie']['created:-1:>=:1:true']['dynamic_behavior']=False
    #config_data['advanced_settings']['behavioral_tags']['movie']['created:-1:>=:1:true']['high_priority']=False

    #config_data['advanced_settings']['behavioral_tags']['episode']['played:-1:>=:1']['action']='keep'
    #config_data['advanced_settings']['behavioral_tags']['episode']['played:-1:>=:1']['user_conditional']='all'
    #config_data['advanced_settings']['behavioral_tags']['episode']['played:-1:>=:1']['played_conditional']='ignore'
    #config_data['advanced_settings']['behavioral_tags']['episode']['played:-1:>=:1']['action_control']=0
    #config_data['advanced_settings']['behavioral_tags']['episode']['played:-1:>=:1']['dynamic_behavior']=False
    #config_data['advanced_settings']['behavioral_tags']['episode']['played:-1:>=:1']['high_priority']=False

    #config_data['advanced_settings']['behavioral_tags']['episode']['created:-1:>=:1:true']['action']='keep'
    #config_data['advanced_settings']['behavioral_tags']['episode']['created:-1:>=:1:true']['user_conditional']='all'
    #config_data['advanced_settings']['behavioral_tags']['episode']['created:-1:>=:1:true']['played_conditional']='ignore'
    #config_data['advanced_settings']['behavioral_tags']['episode']['created:-1:>=:1:true']['action_control']=0
    #config_data['advanced_settings']['behavioral_tags']['episode']['created:-1:>=:1:true']['dynamic_behavior']=False
    #config_data['advanced_settings']['behavioral_tags']['episode']['created:-1:>=:1:true']['high_priority']=False

    #config_data['advanced_settings']['behavioral_tags']['audio']['played:-1:>=:1']['action']='keep'
    #config_data['advanced_settings']['behavioral_tags']['audio']['played:-1:>=:1']['user_conditional']='all'
    #config_data['advanced_settings']['behavioral_tags']['audio']['played:-1:>=:1']['played_conditional']='ignore'
    #config_data['advanced_settings']['behavioral_tags']['audio']['played:-1:>=:1']['action_control']=0
    #config_data['advanced_settings']['behavioral_tags']['audio']['played:-1:>=:1']['dynamic_behavior']=False
    #config_data['advanced_settings']['behavioral_tags']['audio']['played:-1:>=:1']['high_priority']=False

    #config_data['advanced_settings']['behavioral_tags']['audio']['created:-1:>=:1:true']['action']='keep'
    #config_data['advanced_settings']['behavioral_tags']['audio']['created:-1:>=:1:true']['user_conditional']='all'
    #config_data['advanced_settings']['behavioral_tags']['audio']['created:-1:>=:1:true']['played_conditional']='ignore'
    #config_data['advanced_settings']['behavioral_tags']['audio']['created:-1:>=:1:true']['action_control']=0
    #config_data['advanced_settings']['behavioral_tags']['audio']['created:-1:>=:1:true']['dynamic_behavior']=False
    #config_data['advanced_settings']['behavioral_tags']['audio']['created:-1:>=:1:true']['high_priority']=False

    #if (server_brand == 'jellyfin'):
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['played:-1:>=:1']['action']='keep'
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['played:-1:>=:1']['user_conditional']='all'
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['played:-1:>=:1']['played_conditional']='ignore'
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['played:-1:>=:1']['action_control']=0
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['played:-1:>=:1']['dynamic_behavior']=False
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['played:-1:>=:1']['high_priority']=False

        #config_data['advanced_settings']['behavioral_tags']['audiobook']['created:-1:>=:1:true']['action']='keep'
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['created:-1:>=:1:true']['user_conditional']='all'
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['created:-1:>=:1:true']['played_conditional']='ignore'
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['created:-1:>=:1:true']['action_control']=0
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['created:-1:>=:1:true']['dynamic_behavior']=False
        #config_data['advanced_settings']['behavioral_tags']['audiobook']['created:-1:>=:1:true']['high_priority']=False

    #INTENTIONALLY COMMENTED OUT
    #config_data['advanced_settings']['whitetags']=[]
    #config_data['advanced_settings']['whitetags']['global']=[]
    #config_data['advanced_settings']['whitetags']['movie']=[]
    #config_data['advanced_settings']['whitetags']['episode']=[]
    #config_data['advanced_settings']['whitetags']['audio']=[]
    #if (server_brand == 'jellyfin'):
        #config_data['advanced_settings']['whitetags']['audiobook']=[]

    #INTENTIONALLY COMMENTED OUT
    #config_data['advanced_settings']['blacktags']=[]
    #config_data['advanced_settings']['blacktags']['global']=[]
    #config_data['advanced_settings']['blacktags']['movie']=[]
    #config_data['advanced_settings']['blacktags']['episode']=[]
    #config_data['advanced_settings']['blacktags']['audio']=[]
    #if (server_brand == 'jellyfin'):
        #config_data['advanced_settings']['blacktags']['audiobook']=[]

    config_data['advanced_settings']['delete_empty_folders']['episode']['season']=False
    config_data['advanced_settings']['delete_empty_folders']['episode']['series']=False

    config_data['advanced_settings']['episode_control']['minimum_episodes']=0
    config_data['advanced_settings']['episode_control']['minimum_played_episodes']=0
    config_data['advanced_settings']['episode_control']['minimum_episodes_behavior']='Max Played Min Unplayed'
    config_data['advanced_settings']['episode_control']['series_ended']['delete_episodes']=False

    config_data['advanced_settings']['radarr']['movie']['unmonitor']=True
    config_data['advanced_settings']['radarr']['movie']['remove']=False

    config_data['advanced_settings']['sonarr']['series']['unmonitor']=True
    config_data['advanced_settings']['sonarr']['series']['remove']=False
    config_data['advanced_settings']['sonarr']['episode']['unmonitor']=True

    #config_data['advanced_settings']['lidarr']['album']['unmonitor']=True
    #config_data['advanced_settings']['lidarr']['album']['remove']=False
    #config_data['advanced_settings']['lidarr']['track']['unmonitor']=True

    #config_data['advanced_settings']['readarr']['book']['unmonitor']=True
    #config_data['advanced_settings']['readarr']['book']['remove']=False

    config_data['advanced_settings']['trakt_fix']['set_missing_last_played_date']['movie']=True
    config_data['advanced_settings']['trakt_fix']['set_missing_last_played_date']['episode']=True
    config_data['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audio']=True
    if (server_brand == 'jellyfin'):
        config_data['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audiobook']=True

    config_data['advanced_settings']['console_controls']['headers']['script']['show']=True
    config_data['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['headers']['script']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['headers']['user']['show']=True
    config_data['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['headers']['user']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['headers']['summary']['show']=True
    config_data['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['headers']['summary']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['footers']['script']['show']=True
    config_data['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['footers']['script']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['warnings']['script']['show']=True
    config_data['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['warnings']['script']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['movie']['delete']['show']=True
    config_data['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['movie']['delete']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['movie']['keep']['show']=True
    config_data['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['movie']['keep']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['movie']['post_processing']['show']=True
    config_data['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['movie']['summary']['show']=True
    config_data['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['movie']['summary']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['episode']['delete']['show']=True
    config_data['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['episode']['delete']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['episode']['keep']['show']=True
    config_data['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['episode']['keep']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['episode']['post_processing']['show']=True
    config_data['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['episode']['summary']['show']=True
    config_data['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['episode']['summary']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['audio']['delete']['show']=True
    config_data['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['audio']['delete']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['audio']['keep']['show']=True
    config_data['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['audio']['keep']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['audio']['post_processing']['show']=True
    config_data['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['background']['color']=''

    config_data['advanced_settings']['console_controls']['audio']['summary']['show']=True
    config_data['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['color']=''
    config_data['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['style']=''
    config_data['advanced_settings']['console_controls']['audio']['summary']['formatting']['background']['color']=''

    if (server_brand == 'jellyfin'):
        config_data['advanced_settings']['console_controls']['audiobook']['delete']['show']=True
        config_data['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['color']=''
        config_data['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['style']=''
        config_data['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['background']['color']=''

        config_data['advanced_settings']['console_controls']['audiobook']['keep']['show']=True
        config_data['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['color']=''
        config_data['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['style']=''
        config_data['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['background']['color']=''

        config_data['advanced_settings']['console_controls']['audiobook']['post_processing']['show']=True
        config_data['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['color']=''
        config_data['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['style']=''
        config_data['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['background']['color']=''

        config_data['advanced_settings']['console_controls']['audiobook']['summary']['show']=True
        config_data['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['color']=''
        config_data['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['style']=''
        config_data['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['background']['color']=''

    config_data['advanced_settings']['UPDATE_CONFIG']=False

    config_data['advanced_settings']['REMOVE_FILES']=False

    config_data['admin_settings']['behavior']['list']='blacklist'
    config_data['admin_settings']['behavior']['matching']='byId'
    config_data['admin_settings']['behavior']['users']['monitor_disabled']=True

    #INTENTIONALLY COMMENTED OUT
    #config_data['admin_settings']['users'][0]['user_id']=''
    #config_data['admin_settings']['users'][0]['user_name']=''
    #config_data['admin_settings']['users'][0]['whitelist'][0]['lib_id']=''
    #config_data['admin_settings']['users'][0]['whitelist'][0]['collection_type']=''
    #config_data['admin_settings']['users'][0]['whitelist'][0]['path']=''
    #config_data['admin_settings']['users'][0]['whitelist'][0]['network_path']=''
    #config_data['admin_settings']['users'][0]['whitelist'][0]['subfolder_id']=''
    #config_data['admin_settings']['users'][0]['whitelist'][0]['lib_enabled']=''
    #config_data['admin_settings']['users'][0]['whitelist'][1]['lib_id']=''
    #config_data['admin_settings']['users'][0]['whitelist'][1]['collection_type']=''
    #config_data['admin_settings']['users'][0]['whitelist'][1]['path']=''
    #config_data['admin_settings']['users'][0]['whitelist'][1]['network_path']=''
    #config_data['admin_settings']['users'][0]['whitelist'][1]['subfolder_id']=''
    #config_data['admin_settings']['users'][0]['whitelist'][1]['lib_enabled']=''
    #config_data['admin_settings']['users'][0]['whitelist'][#]['lib_id']=''
    #config_data['admin_settings']['users'][0]['whitelist'][#]['collection_type']=''
    #config_data['admin_settings']['users'][0]['whitelist'][#]['path']=''
    #config_data['admin_settings']['users'][0]['whitelist'][#]['network_path']=''
    #config_data['admin_settings']['users'][0]['whitelist'][#]['subfolder_id']=''
    #config_data['admin_settings']['users'][0]['whitelist'][#]['lib_enabled']=''
    #config_data['admin_settings']['users'][0]['blacklist'][0]['lib_id']=''
    #config_data['admin_settings']['users'][0]['blacklist'][0]['collection_type']=''
    #config_data['admin_settings']['users'][0]['blacklist'][0]['path']=''
    #config_data['admin_settings']['users'][0]['blacklist'][0]['network_path']=''
    #config_data['admin_settings']['users'][0]['blacklist'][0]['subfolder_id']=''
    #config_data['admin_settings']['users'][0]['blacklist'][0]['lib_enabled']=''
    #config_data['admin_settings']['users'][0]['blacklist'][1]['lib_id']=''
    #config_data['admin_settings']['users'][0]['blacklist'][1]['collection_type']=''
    #config_data['admin_settings']['users'][0]['blacklist'][1]['path']=''
    #config_data['admin_settings']['users'][0]['blacklist'][1]['network_path']=''
    #config_data['admin_settings']['users'][0]['blacklist'][1]['subfolder_id']=''
    #config_data['admin_settings']['users'][0]['blacklist'][1]['lib_enabled']=''
    #config_data['admin_settings']['users'][0]['blacklist'][#]['lib_id']=''
    #config_data['admin_settings']['users'][0]['blacklist'][#]['collection_type']=''
    #config_data['admin_settings']['users'][0]['blacklist'][#]['path']=''
    #config_data['admin_settings']['users'][0]['blacklist'][#]['network_path']=''
    #config_data['admin_settings']['users'][0]['blacklist'][#]['subfolder_id']=''
    #config_data['admin_settings']['users'][0]['blacklist'][#]['lib_enabled']=''
    #config_data['admin_settings']['users'][1]['user_id']=''
    #config_data['admin_settings']['users'][1]['user_name']=''
    #config_data['admin_settings']['users'][1]['whitelist'][0]['lib_id']=''
    #config_data['admin_settings']['users'][1]['whitelist'][0]['collection_type']=''
    #config_data['admin_settings']['users'][1]['whitelist'][0]['path']=''
    #config_data['admin_settings']['users'][1]['whitelist'][0]['network_path']=''
    #config_data['admin_settings']['users'][1]['whitelist'][0]['subfolder_id']=''
    #config_data['admin_settings']['users'][1]['whitelist'][0]['lib_enabled']=''
    #config_data['admin_settings']['users'][1]['whitelist'][1]['lib_id']=''
    #config_data['admin_settings']['users'][1]['whitelist'][1]['collection_type']=''
    #config_data['admin_settings']['users'][1]['whitelist'][1]['path']=''
    #config_data['admin_settings']['users'][1]['whitelist'][1]['network_path']=''
    #config_data['admin_settings']['users'][1]['whitelist'][1]['subfolder_id']=''
    #config_data['admin_settings']['users'][1]['whitelist'][1]['lib_enabled']=''
    #config_data['admin_settings']['users'][1]['whitelist'][#]['lib_id']=''
    #config_data['admin_settings']['users'][1]['whitelist'][#]['collection_type']=''
    #config_data['admin_settings']['users'][1]['whitelist'][#]['path']=''
    #config_data['admin_settings']['users'][1]['whitelist'][#]['network_path']=''
    #config_data['admin_settings']['users'][1]['whitelist'][#]['subfolder_id']=''
    #config_data['admin_settings']['users'][1]['whitelist'][#]['lib_enabled']=''
    #config_data['admin_settings']['users'][1]['blacklist'][0]['lib_id']=''
    #config_data['admin_settings']['users'][1]['blacklist'][0]['collection_type']=''
    #config_data['admin_settings']['users'][1]['blacklist'][0]['path']=''
    #config_data['admin_settings']['users'][1]['blacklist'][0]['network_path']=''
    #config_data['admin_settings']['users'][1]['blacklist'][0]['subfolder_id']=''
    #config_data['admin_settings']['users'][1]['blacklist'][0]['lib_enabled']=''
    #config_data['admin_settings']['users'][1]['blacklist'][1]['lib_id']=''
    #config_data['admin_settings']['users'][1]['blacklist'][1]['collection_type']=''
    #config_data['admin_settings']['users'][1]['blacklist'][1]['path']=''
    #config_data['admin_settings']['users'][1]['blacklist'][1]['network_path']=''
    #config_data['admin_settings']['users'][1]['blacklist'][1]['subfolder_id']=''
    #config_data['admin_settings']['users'][1]['blacklist'][1]['lib_enabled']=''
    #config_data['admin_settings']['users'][1]['blacklist'][#]['lib_id']=''
    #config_data['admin_settings']['users'][1]['blacklist'][#]['collection_type']=''
    #config_data['admin_settings']['users'][1]['blacklist'][#]['path']=''
    #config_data['admin_settings']['users'][1]['blacklist'][#]['network_path']=''
    #config_data['admin_settings']['users'][1]['blacklist'][#]['subfolder_id']=''
    #config_data['admin_settings']['users'][1]['blacklist'][#]['lib_enabled']=''
    #config_data['admin_settings']['users'][#]['user_id']=''
    #config_data['admin_settings']['users'][#]['user_name']=''
    #config_data['admin_settings']['users'][#]['whitelist'][0]['lib_id']=''
    #config_data['admin_settings']['users'][#]['whitelist'][0]['collection_type']=''
    #config_data['admin_settings']['users'][#]['whitelist'][0]['path']=''
    #config_data['admin_settings']['users'][#]['whitelist'][0]['network_path']=''
    #config_data['admin_settings']['users'][#]['whitelist'][0]['subfolder_id']=''
    #config_data['admin_settings']['users'][#]['whitelist'][0]['lib_enabled']=''
    #config_data['admin_settings']['users'][#]['whitelist'][1]['lib_id']=''
    #config_data['admin_settings']['users'][#]['whitelist'][1]['collection_type']=''
    #config_data['admin_settings']['users'][#]['whitelist'][1]['path']=''
    #config_data['admin_settings']['users'][#]['whitelist'][1]['network_path']=''
    #config_data['admin_settings']['users'][#]['whitelist'][1]['subfolder_id']=''
    #config_data['admin_settings']['users'][#]['whitelist'][1]['lib_enabled']=''
    #config_data['admin_settings']['users'][#]['whitelist'][#]['lib_id']=''
    #config_data['admin_settings']['users'][#]['whitelist'][#]['collection_type']=''
    #config_data['admin_settings']['users'][#]['whitelist'][#]['path']=''
    #config_data['admin_settings']['users'][#]['whitelist'][#]['network_path']=''
    #config_data['admin_settings']['users'][#]['whitelist'][#]['subfolder_id']=''
    #config_data['admin_settings']['users'][#]['whitelist'][#]['lib_enabled']=''
    #config_data['admin_settings']['users'][#]['blacklist'][0]['lib_id']=''
    #config_data['admin_settings']['users'][#]['blacklist'][0]['collection_type']=''
    #config_data['admin_settings']['users'][#]['blacklist'][0]['path']=''
    #config_data['admin_settings']['users'][#]['blacklist'][0]['network_path']=''
    #config_data['admin_settings']['users'][#]['blacklist'][0]['subfolder_id']=''
    #config_data['admin_settings']['users'][#]['blacklist'][0]['lib_enabled']=''
    #config_data['admin_settings']['users'][#]['blacklist'][1]['lib_id']=''
    #config_data['admin_settings']['users'][#]['blacklist'][1]['collection_type']=''
    #config_data['admin_settings']['users'][#]['blacklist'][1]['path']=''
    #config_data['admin_settings']['users'][#]['blacklist'][1]['network_path']=''
    #config_data['admin_settings']['users'][#]['blacklist'][1]['subfolder_id']=''
    #config_data['admin_settings']['users'][#]['blacklist'][1]['lib_enabled']=''
    #config_data['admin_settings']['users'][#]['blacklist'][#]['lib_id']=''
    #config_data['admin_settings']['users'][#]['blacklist'][#]['collection_type']=''
    #config_data['admin_settings']['users'][#]['blacklist'][#]['path']=''
    #config_data['admin_settings']['users'][#]['blacklist'][#]['network_path']=''
    #config_data['admin_settings']['users'][#]['blacklist'][#]['subfolder_id']=''
    #config_data['admin_settings']['users'][#]['blacklist'][#]['lib_enabled']=''

    config_data['admin_settings']['media_managers']['radarr']['enabled']=True
    config_data['admin_settings']['media_managers']['radarr']['url']=None
    config_data['admin_settings']['media_managers']['radarr']['api_key']=None

    config_data['admin_settings']['media_managers']['sonarr']['enabled']=True
    config_data['admin_settings']['media_managers']['sonarr']['url']=None
    config_data['admin_settings']['media_managers']['sonarr']['api_key']=None

    #config_data['admin_settings']['media_managers']['lidarr']['enabled']=True
    #config_data['admin_settings']['media_managers']['lidarr']['url']=None
    #config_data['admin_settings']['media_managers']['lidarr']['api_key']=None
    
    #config_data['admin_settings']['media_managers']['readarr']['enabled']=True
    #config_data['admin_settings']['media_managers']['readarr']['url']=None
    #config_data['admin_settings']['media_managers']['readarr']['api_key']=None

    config_data['admin_settings']['api_controls']['attempts']=4
    config_data['admin_settings']['api_controls']['item_limit']=25

    config_data['admin_settings']['cache']['size']=32
    config_data['admin_settings']['cache']['fallback_behavior']='LRU'
    config_data['admin_settings']['cache']['minimum_age']=200

    config_data['admin_settings']['output_controls']['character_limit']['print']=128

    #before saving; reorder some keys for consistency
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']=config_data['advanced_settings']['behavioral_statements']['movie']['favorited'].pop('extra')
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']=config_data['advanced_settings']['behavioral_statements']['episode']['favorited'].pop('extra')
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']=config_data['advanced_settings']['behavioral_statements']['audio']['favorited'].pop('extra')
    if (server_brand == 'jellyfin'):
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']=config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited'].pop('extra')

    return config_data


def yaml_configurationBuilder(the_dict):

    print('0000')
    #strip out uneccessary data
    config_data=filterYAMLConfigKeys_ToKeep(copy.deepcopy(the_dict),'version','basic_settings','advanced_settings','admin_settings','DEBUG')

    print('0001')
    #start building config yaml
    config_data=yaml_configurationLayout(config_data,config_data['admin_settings']['server']['brand'])

    print('0002')
    config_data['basic_settings']['filter_statements'].pop('audio')
    print('0003')
    if (the_dict['admin_settings']['server']['brand'] == 'jellyfin'):
        config_data['basic_settings']['filter_statements'].pop('audiobook')
    print('0004')
    config_data['basic_settings'].pop('filter_tags')
    config_data['advanced_settings'].pop('filter_statements')
    config_data['advanced_settings'].pop('behavioral_statements')
    config_data['advanced_settings'].pop('behavioral_tags')
    print('0005')
    if (the_dict['advanced_settings']['whitetags']['global'] == []):
        print('0006')
        config_data['advanced_settings'].pop('whitetags')
        print('0007')
    else:
        print('0008')
        config_data['advanced_settings']['whitetags']['global']=the_dict['advanced_settings']['whitetags']['global']
        config_data['advanced_settings']['whitetags'].pop('movie')
        config_data['advanced_settings']['whitetags'].pop('episode')
        config_data['advanced_settings']['whitetags'].pop('audio')
        print('0009')
        if (the_dict['admin_settings']['server']['brand'] == 'jellyfin'):
            config_data['advanced_settings']['whitetags'].pop('audiobook')
    if (the_dict['advanced_settings']['blacktags']['global'] == []):
        print('000A')
        config_data['advanced_settings'].pop('blacktags')
        print('000B')
    else:
        print('000C')
        config_data['advanced_settings']['blacktags']['global']=the_dict['advanced_settings']['blacktags']['global']
        config_data['advanced_settings']['blacktags'].pop('movie')
        config_data['advanced_settings']['blacktags'].pop('episode')
        config_data['advanced_settings']['blacktags'].pop('audio')
        print('000D')
        if (the_dict['admin_settings']['server']['brand'] == 'jellyfin'):
            config_data['advanced_settings']['blacktags'].pop('audiobook')
    print2json(config_data,the_dict)
    print('000E')
    config_data['advanced_settings'].pop('delete_empty_folders')
    print('000F')
    config_data['advanced_settings'].pop('radarr')
    print('000G')
    config_data['advanced_settings'].pop('sonarr')
    print('000H')
    config_data['advanced_settings'].pop('lidarr')
    print('000I')
    config_data['advanced_settings'].pop('readarr')
    print('000J')
    config_data['advanced_settings'].pop('trakt_fix')
    print('000K')
    config_data['advanced_settings'].pop('console_controls')
    print('000L')
    config_data['advanced_settings'].pop('UPDATE_CONFIG')
    print('000M')
    if ((the_dict['admin_settings']['behavior']['list'] == 'blacklist') and (the_dict['admin_settings']['behavior']['matching'] == 'byId') and (the_dict['admin_settings']['behavior']['users']['monitor_disabled'])):
        config_data['admin_settings'].pop('behavior')
    else:
        if (the_dict['admin_settings']['behavior']['list'] == 'blacklist'):
            config_data['admin_settings']['behavior'].pop('list')
        else:
            config_data['admin_settings']['behavior']['list']=the_dict['admin_settings']['behavior']['list']
        if (the_dict['admin_settings']['behavior']['matching'] == 'byId'):
            config_data['admin_settings']['behavior'].pop('matching')
        else:
            config_data['admin_settings']['behavior']['matching']=the_dict['admin_settings']['behavior']['matching']
        if (the_dict['admin_settings']['behavior']['users']['monitor_disabled']):
            config_data['admin_settings']['behavior'].pop('users')
        else:
            config_data['admin_settings']['behavior']['users']['monitor_disabled']=the_dict['admin_settings']['behavior']['users']['monitor_disabled']

    if (the_dict['admin_settings']['media_managers']['radarr'] == {}):
        config_data['admin_settings']['media_managers'].pop('radarr')
    else:
        config_data['admin_settings']['media_managers']['radarr']=the_dict['admin_settings']['media_managers']['radarr']

    if (the_dict['admin_settings']['media_managers']['sonarr'] == {}):
        config_data['admin_settings']['media_managers'].pop('sonarr')
    else:
        config_data['admin_settings']['media_managers']['sonarr']=the_dict['admin_settings']['media_managers']['sonarr']

    if (the_dict['admin_settings']['media_managers']['lidarr'] == {}):
        config_data['admin_settings']['media_managers'].pop('lidarr')
    else:
        config_data['admin_settings']['media_managers']['lidarr']=the_dict['admin_settings']['media_managers']['lidarr']

    if (the_dict['admin_settings']['media_managers']['readarr'] == {}):
        config_data['admin_settings']['media_managers'].pop('readarr')
    else:
        config_data['admin_settings']['media_managers']['readarr']=the_dict['admin_settings']['media_managers']['readarr']

    if (len(config_data['admin_settings']['media_managers']) == 0):
        config_data['admin_settings'].pop('media_managers')

    config_data['admin_settings'].pop('api_controls')
    config_data['admin_settings'].pop('cache')
    config_data['admin_settings'].pop('output_controls')

    #save yaml config file
    save_yaml_config(config_data,the_dict['mumc_path'] / the_dict['config_file_name_yaml'])