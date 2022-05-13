#!/usr/bin/env python3

from media_cleaner import convert2json

#This module can be used to change some of the default configuration values used before the script is first run
#Script will check for valid values after the first run
#Configuration values outside of the valid range will throw an error
#See https://github.com/terrelsa13/media_cleaner for a description of each configuration value

#get default configuration values
def get_default_config_values(config_value):
    
    defaultConfigValues={

        #'example_config':0
        #'example_config':'abc'

        'played_age_movie':-1,
        'played_age_episode':-1,
        'played_age_audio':-1,
        'played_age_audiobook':-1,

        'keep_favorites_movie':1,
        'keep_favorites_episode':1,
        'keep_favorites_audio':1,
        'keep_favorites_audiobook':1,

        'multiuser_whitelist_movie':1,
        'multiuser_whitelist_episode':1,
        'multiuser_whitelist_audio':1,
        'multiuser_whitelist_audiobook':1,

        'blacktag':'',

        'keep_blacktagged_movie':0,
        'keep_blacktagged_episode':0,
        'keep_blacktagged_audio':0,
        'keep_blacktagged_audiobook':0,

        'whitetag':'',

        'keep_favorites_advanced_movie_genre':0,
        'keep_favorites_advanced_movie_library_genre':0,

        'keep_favorites_advanced_episode_genre':0,
        'keep_favorites_advanced_season_genre':0,
        'keep_favorites_advanced_series_genre':0,
        'keep_favorites_advanced_tv_library_genre':0,
        'keep_favorites_advanced_tv_studio_network':0,
        'keep_favorites_advanced_tv_studio_network_genre':0,

        'keep_favorites_advanced_track_genre':0,
        'keep_favorites_advanced_album_genre':0,
        'keep_favorites_advanced_music_library_genre':0,
        'keep_favorites_advanced_track_artist':0,
        'keep_favorites_advanced_album_artist':0,
        'keep_favorites_advanced_music_library_artist':0,

        'keep_favorites_advanced_audio_book_track_genre':0,
        'keep_favorites_advanced_audio_book_genre':0,
        'keep_favorites_advanced_audio_book_library_genre':0,
        'keep_favorites_advanced_audio_book_track_author':0,
        'keep_favorites_advanced_audio_book_author':0,
        'keep_favorites_advanced_audio_book_library_author':0,

    }

    #preConfigDebug = True
    preConfigDebug = False
    
    #DEBUG
    if (preConfigDebug):
        print(str(config_value) + '=' + str(defaultConfigValues[config_value]))

    return(defaultConfigValues[config_value])
