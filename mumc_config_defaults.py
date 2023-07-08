#!/usr/bin/env python3

######!!!ATTENTION!!!#####
#This file only applies to the legacy mumc_config.py file
#With the addition of a human readable mumc_config.yaml; configuration defaults are OBSOLETE
#This file will be removed in the near future to prevent confusion
######!!!ATTENTION!!!#####

#This module can be used to change some of the default configuration values used before the script is first run
#Script will check for valid values after the first run
#Configuration values outside of the valid range will throw an error
#See https://github.com/terrelsa13/MUMC for a description of each configuration value


defaultConfigValues={

        #'example_number_config':0
        #'example_string_config':'abc'
        #'example_boolean_config':True

        #-------------Basic Config Options Start Here---------------#

        'played_filter_movie':[-1,'>=',1],
        'played_filter_episode':[-1,'>=',1],
        'played_filter_audio':[-1,'>=',1],
        'played_filter_audiobook':[-1,'>=',1],

        'created_filter_movie':[-1,'>=',1,True],
        'created_filter_episode':[-1,'>=',1,True],
        'created_filter_audio':[-1,'>=',1,True],
        'created_filter_audiobook':[-1,'>=',1,True],

        #------------Advanced Config Options Start Here-------------#

        'favorited_behavior_movie':['keep','any','ignore',3],
        'favorited_behavior_episode':['keep','any','ignore',3],
        'favorited_behavior_audio':['keep','any','ignore',3],
        'favorited_behavior_audiobook':['keep','any','ignore',3],

        'favorited_advanced_movie_genre':0,
        'favorited_advanced_movie_library_genre':0,

        'favorited_advanced_episode_genre':0,
        'favorited_advanced_season_genre':0,
        'favorited_advanced_series_genre':0,
        'favorited_advanced_tv_library_genre':0,
        'favorited_advanced_tv_studio_network':0,
        'favorited_advanced_tv_studio_network_genre':0,

        'favorited_advanced_track_genre':0,
        'favorited_advanced_album_genre':0,
        'favorited_advanced_music_library_genre':0,
        'favorited_advanced_track_artist':0,
        'favorited_advanced_album_artist':0,

        'favorited_advanced_audiobook_track_genre':0,
        'favorited_advanced_audiobook_genre':0,
        'favorited_advanced_audiobook_library_genre':0,
        'favorited_advanced_audiobook_track_author':0,
        'favorited_advanced_audiobook_author':0,
        'favorited_advanced_audiobook_library_author':0,

        'whitetag':'',

        'whitetagged_behavior_movie':['keep','all','ignore',0],
        'whitetagged_behavior_episode':['keep','all','ignore',0],
        'whitetagged_behavior_audio':['keep','all','ignore',0],
        'whitetagged_behavior_audiobook':['keep','all','ignore',0],

        'blacktag':'',

        'blacktagged_behavior_movie':['delete','all','any_played',0],
        'blacktagged_behavior_episode':['delete','all','any_played',0],
        'blacktagged_behavior_audio':['delete','all','any_played',0],
        'blacktagged_behavior_audiobook':['delete','all','any_played',0],

        'whitelisted_behavior_movie':['keep','any','ignore',3],
        'whitelisted_behavior_episode':['keep','any','ignore',3],
        'whitelisted_behavior_audio':['keep','any','ignore',3],
        'whitelisted_behavior_audiobook':['keep','any','ignore',3],

        'blacklisted_behavior_movie':['delete','any','any_played',3],
        'blacklisted_behavior_episode':['delete','any','any_played',3],
        'blacklisted_behavior_audio':['delete','any','any_played',3],
        'blacklisted_behavior_audiobook':['delete','any','any_played',3],

        'minimum_number_episodes':0,
        'minimum_number_played_episodes':0,
        'minimum_number_episodes_behavior':'Max Played Min Unplayed',

        'movie_set_missing_last_played_date':True,
        'episode_set_missing_last_played_date':True,
        'audio_set_missing_last_played_date':True,
        'audiobook_set_missing_last_played_date':True,

        'print_script_header':True,
        'print_warnings':True,
        'print_user_header':True,
        'print_movie_delete_info':True,
        'print_movie_keep_info':True,
        'print_episode_delete_info':True,
        'print_episode_keep_info':True,
        'print_audio_delete_info':True,
        'print_audio_keep_info':True,
        'print_audiobook_delete_info':True,
        'print_audiobook_keep_info':True,
        'print_movie_post_processing_info':True,
        'print_episode_post_processing_info':True,
        'print_audio_post_processing_info':True,
        'print_audiobook_post_processing_info':True,
        'print_summary_header':True,
        'print_movie_summary':True,
        'print_episode_summary':True,
        'print_audio_summary':True,
        'print_audiobook_summary':True,
        'print_script_footer':True,

        'script_header_format':['','',''],
        'script_warnings_format':['','',''],
        'user_header_format':['','',''],
        'movie_delete_info_format':['','',''],
        'movie_keep_info_format':['','',''],
        'episode_delete_info_format':['','',''],
        'episode_keep_info_format':['','',''],
        'audio_delete_info_format':['','',''],
        'audio_keep_info_format':['','',''],
        'audiobook_delete_info_format':['','',''],
        'audiobook_keep_info_format':['','',''],
        'movie_post_processing_format':['','',''],
        'episode_post_processing_format':['','',''],
        'audio_post_processing_format':['','',''],
        'audiobook_post_processing_format':['','',''],
        'summary_header_format':['','',''],
        'movie_summary_format':['','',''],
        'episode_summary_format':['','',''],
        'audio_summary_format':['','',''],
        'audiobook_summary_format':['','',''],
        'script_footer_format':['','',''],

        #------------Cache Settings-------------#

        'api_query_cache_size':32,
        'api_query_cache_fallback_behavior':'LRU',
        'api_query_cache_last_accessed_time':200
    }


#get default configuration values
def get_default_config_values(config_value):

    #preConfigDebug = True
    preConfigDebug = False
    
    #DEBUG
    if (preConfigDebug):
        print(str(config_value) + '=' + str(defaultConfigValues[config_value]))

    return(defaultConfigValues[config_value])
