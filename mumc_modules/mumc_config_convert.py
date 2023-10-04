#!/usr/bin/env python3
import yaml
import json
from sys import path
from mumc_modules.mumc_versions import get_script_version
from mumc_modules.mumc_output import get_current_directory
from mumc_modules.mumc_config_skeleton import setYAMLConfigSkeleton


def libConvertLegacyToYAML(user_wl_libs,user_bl_libs):
    user_data_list=[]
    user_wl_data_list=[]
    user_bl_data_list=[]
    user_wl_data_dict={}
    user_bl_data_dict={}
    user_lib_dict={}
    user_wl_libs_loaded=json.loads(user_wl_libs)
    user_bl_libs_loaded=json.loads(user_bl_libs)

    for wlentry in user_wl_libs_loaded:
        user_wl_data_dict['user_id']=wlentry['userid']
        user_wl_data_dict['user_name']=wlentry['username']
        user_wl_data_dict['whitelist']=[]
        one_or_more_wl_entry=False
        for entry_data in wlentry:
            if (entry_data.isnumeric()):
                user_lib_dict['lib_id']=wlentry[entry_data]['libid']
                user_lib_dict['collection_type']=wlentry[entry_data]['collectiontype']
                user_lib_dict['path']=wlentry[entry_data]['path']
                user_lib_dict['network_path']=wlentry[entry_data]['networkpath']
                user_lib_dict['lib_enabled']=True
                user_wl_data_dict['whitelist'].append(user_lib_dict.copy())
                one_or_more_wl_entry=True
        #if user has no whitelist entries then set template with None/null values
        if (one_or_more_wl_entry == False):
            user_lib_dict['lib_id']=''
            user_lib_dict['collection_type']=''
            user_lib_dict['path']=''
            user_lib_dict['network_path']=''
            user_lib_dict['lib_enabled']=False
            user_wl_data_dict['whitelist'].append(user_lib_dict.copy())
        user_wl_data_list.append(user_wl_data_dict.copy())

    for blentry in user_bl_libs_loaded:
        user_bl_data_dict['user_id']=blentry['userid']
        user_bl_data_dict['user_name']=blentry['username']
        user_bl_data_dict['blacklist']=[]
        one_or_more_bl_entry=False
        for entry_data in blentry:
            if (entry_data.isnumeric()):
                user_lib_dict['lib_id']=blentry[entry_data]['libid']
                user_lib_dict['collection_type']=blentry[entry_data]['collectiontype']
                user_lib_dict['path']=blentry[entry_data]['path']
                user_lib_dict['network_path']=blentry[entry_data]['networkpath']
                user_lib_dict['lib_enabled']=True
                user_bl_data_dict['blacklist'].append(user_lib_dict.copy())
                one_or_more_bl_entry=True
        #if user has no blacklist entries then set template with None/null values
        if (one_or_more_bl_entry == False):
            user_lib_dict['lib_id']=''
            user_lib_dict['collection_type']=''
            user_lib_dict['path']=''
            user_lib_dict['network_path']=''
            user_lib_dict['lib_enabled']=False
            user_bl_data_dict['blacklist'].append(user_lib_dict.copy())
        user_bl_data_list.append(user_bl_data_dict.copy())

    #user_data_list=user_wl_data_list+user_bl_data_list
    for user in user_wl_data_list:
        user_data_list.append(user)
        user_data_list[user_data_list.index(user)]['blacklist']=user_bl_data_list[user_data_list.index(user)]['blacklist']

    return user_data_list


def convert_legacyConfigToYAML(cfg,configPath,configFileNameNoExt):
    config_data={}
    config_data=setYAMLConfigSkeleton(config_data)
    config_data['version']=get_script_version()
    config_data['basic_settings']['filter_statements']['movie']['played']['condition_days']=cfg.played_filter_movie[0]
    config_data['basic_settings']['filter_statements']['movie']['played']['count_equality']=cfg.played_filter_movie[1]
    config_data['basic_settings']['filter_statements']['movie']['played']['count']=cfg.played_filter_movie[2]
    config_data['basic_settings']['filter_statements']['movie']['created']['condition_days']=cfg.created_filter_movie[0]
    config_data['basic_settings']['filter_statements']['movie']['created']['count_equality']=cfg.created_filter_movie[1]
    config_data['basic_settings']['filter_statements']['movie']['created']['count']=cfg.created_filter_movie[2]
    config_data['basic_settings']['filter_statements']['movie']['created']['behavioral_control']=cfg.created_filter_movie[3]
    config_data['basic_settings']['filter_statements']['episode']['played']['condition_days']=cfg.played_filter_episode[0]
    config_data['basic_settings']['filter_statements']['episode']['played']['count_equality']=cfg.played_filter_episode[1]
    config_data['basic_settings']['filter_statements']['episode']['played']['count']=cfg.played_filter_episode[2]
    config_data['basic_settings']['filter_statements']['episode']['created']['condition_days']=cfg.created_filter_episode[0]
    config_data['basic_settings']['filter_statements']['episode']['created']['count_equality']=cfg.created_filter_episode[1]
    config_data['basic_settings']['filter_statements']['episode']['created']['count']=cfg.created_filter_episode[2]
    config_data['basic_settings']['filter_statements']['episode']['created']['behavioral_control']=cfg.created_filter_episode[3]
    config_data['basic_settings']['filter_statements']['audio']['played']['condition_days']=cfg.played_filter_audio[0]
    config_data['basic_settings']['filter_statements']['audio']['played']['count_equality']=cfg.played_filter_audio[1]
    config_data['basic_settings']['filter_statements']['audio']['played']['count']=cfg.played_filter_audio[2]
    config_data['basic_settings']['filter_statements']['audio']['created']['condition_days']=cfg.created_filter_audio[0]
    config_data['basic_settings']['filter_statements']['audio']['created']['count_equality']=cfg.created_filter_audio[1]
    config_data['basic_settings']['filter_statements']['audio']['created']['count']=cfg.created_filter_audio[2]
    config_data['basic_settings']['filter_statements']['audio']['created']['behavioral_control']=cfg.created_filter_audio[3]
    if (cfg.server_brand == 'jellyfin'):
        config_data['basic_settings']['filter_statements']['audiobook']['played']['condition_days']=cfg.played_filter_audiobook[0]
        config_data['basic_settings']['filter_statements']['audiobook']['played']['count_equality']=cfg.played_filter_audiobook[1]
        config_data['basic_settings']['filter_statements']['audiobook']['played']['count']=cfg.played_filter_audiobook[2]
        config_data['basic_settings']['filter_statements']['audiobook']['created']['condition_days']=cfg.created_filter_audiobook[0]
        config_data['basic_settings']['filter_statements']['audiobook']['created']['count_equality']=cfg.created_filter_audiobook[1]
        config_data['basic_settings']['filter_statements']['audiobook']['created']['count']=cfg.created_filter_audiobook[2]
        config_data['basic_settings']['filter_statements']['audiobook']['created']['behavioral_control']=cfg.created_filter_audiobook[3]
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['action']=cfg.favorited_behavior_movie[0]
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['user_conditional']=cfg.favorited_behavior_movie[1]
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['played_conditional']=cfg.favorited_behavior_movie[2]
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['action_control']=cfg.favorited_behavior_movie[3]
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['genre']=cfg.favorited_advanced_movie_genre
    config_data['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']['library_genre']=cfg.favorited_advanced_movie_library_genre
    config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action']=cfg.whitetagged_behavior_movie[0]
    config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['user_conditional']=cfg.whitetagged_behavior_movie[1]
    config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['played_conditional']=cfg.whitetagged_behavior_movie[2]
    config_data['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action_control']=cfg.whitetagged_behavior_movie[3]
    config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action']=cfg.blacktagged_behavior_movie[0]
    config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['user_conditional']=cfg.blacktagged_behavior_movie[1]
    config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['played_conditional']=cfg.blacktagged_behavior_movie[2]
    config_data['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action_control']=cfg.blacktagged_behavior_movie[3]
    config_data['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action']=cfg.whitelisted_behavior_movie[0]
    config_data['advanced_settings']['behavioral_statements']['movie']['whitelisted']['user_conditional']=cfg.whitelisted_behavior_movie[1]
    config_data['advanced_settings']['behavioral_statements']['movie']['whitelisted']['played_conditional']=cfg.whitelisted_behavior_movie[2]
    config_data['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action_control']=cfg.whitelisted_behavior_movie[3]
    config_data['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action']=cfg.blacklisted_behavior_movie[0]
    config_data['advanced_settings']['behavioral_statements']['movie']['blacklisted']['user_conditional']=cfg.blacklisted_behavior_movie[1]
    config_data['advanced_settings']['behavioral_statements']['movie']['blacklisted']['played_conditional']=cfg.blacklisted_behavior_movie[2]
    config_data['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action_control']=cfg.blacklisted_behavior_movie[3]
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['action']=cfg.favorited_behavior_episode[0]
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['user_conditional']=cfg.favorited_behavior_episode[1]
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['played_conditional']=cfg.favorited_behavior_episode[2]
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['action_control']=cfg.favorited_behavior_episode[3]
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['genre']=cfg.favorited_advanced_episode_genre
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['season_genre']=cfg.favorited_advanced_season_genre
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['series_genre']=cfg.favorited_advanced_series_genre
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['library_genre']=cfg.favorited_advanced_tv_library_genre
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network']=cfg.favorited_advanced_tv_studio_network
    config_data['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']['studio_network_genre']=cfg.favorited_advanced_tv_studio_network_genre
    config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action']=cfg.whitetagged_behavior_episode[0]
    config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['user_conditional']=cfg.whitetagged_behavior_episode[1]
    config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['played_conditional']=cfg.whitetagged_behavior_episode[2]
    config_data['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action_control']=cfg.whitetagged_behavior_episode[3]
    config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action']=cfg.blacktagged_behavior_episode[0]
    config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['user_conditional']=cfg.blacktagged_behavior_episode[1]
    config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['played_conditional']=cfg.blacktagged_behavior_episode[2]
    config_data['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action_control']=cfg.blacktagged_behavior_episode[3]
    config_data['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action']=cfg.whitelisted_behavior_episode[0]
    config_data['advanced_settings']['behavioral_statements']['episode']['whitelisted']['user_conditional']=cfg.whitelisted_behavior_episode[1]
    config_data['advanced_settings']['behavioral_statements']['episode']['whitelisted']['played_conditional']=cfg.whitelisted_behavior_episode[2]
    config_data['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action_control']=cfg.whitelisted_behavior_episode[3]
    config_data['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action']=cfg.blacklisted_behavior_episode[0]
    config_data['advanced_settings']['behavioral_statements']['episode']['blacklisted']['user_conditional']=cfg.blacklisted_behavior_episode[1]
    config_data['advanced_settings']['behavioral_statements']['episode']['blacklisted']['played_conditional']=cfg.blacklisted_behavior_episode[2]
    config_data['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action_control']=cfg.blacklisted_behavior_episode[3]
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['action']=cfg.favorited_behavior_audio[0]
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['user_conditional']=cfg.favorited_behavior_audio[1]
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['played_conditional']=cfg.favorited_behavior_audio[2]
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['action_control']=cfg.favorited_behavior_audio[3]
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['genre']=cfg.favorited_advanced_track_genre
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_genre']=cfg.favorited_advanced_album_genre
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['library_genre']=cfg.favorited_advanced_music_library_genre
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['track_artist']=cfg.favorited_advanced_track_artist
    config_data['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']['album_artist']=cfg.favorited_advanced_album_artist
    config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action']=cfg.whitetagged_behavior_audio[0]
    config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['user_conditional']=cfg.whitetagged_behavior_audio[1]
    config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['played_conditional']=cfg.whitetagged_behavior_audio[2]
    config_data['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action_control']=cfg.whitetagged_behavior_audio[3]
    config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action']=cfg.blacktagged_behavior_audio[0]
    config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['user_conditional']=cfg.blacktagged_behavior_audio[1]
    config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['played_conditional']=cfg.blacktagged_behavior_audio[2]
    config_data['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action_control']=cfg.blacktagged_behavior_audio[3]
    config_data['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action']=cfg.whitelisted_behavior_audio[0]
    config_data['advanced_settings']['behavioral_statements']['audio']['whitelisted']['user_conditional']=cfg.whitelisted_behavior_audio[1]
    config_data['advanced_settings']['behavioral_statements']['audio']['whitelisted']['played_conditional']=cfg.whitelisted_behavior_audio[2]
    config_data['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action_control']=cfg.whitelisted_behavior_audio[3]
    config_data['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action']=cfg.blacklisted_behavior_audio[0]
    config_data['advanced_settings']['behavioral_statements']['audio']['blacklisted']['user_conditional']=cfg.blacklisted_behavior_audio[1]
    config_data['advanced_settings']['behavioral_statements']['audio']['blacklisted']['played_conditional']=cfg.blacklisted_behavior_audio[2]
    config_data['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action_control']=cfg.blacklisted_behavior_audio[3]
    if (cfg.server_brand == 'jellyfin'):
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action']=cfg.favorited_behavior_audiobook[0]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['user_conditional']=cfg.favorited_behavior_audiobook[1]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['played_conditional']=cfg.favorited_behavior_audiobook[2]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action_control']=cfg.favorited_behavior_audiobook[3]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['genre']=cfg.favorited_advanced_audiobook_track_genre
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['audiobook_genre']=cfg.favorited_advanced_audiobook_genre
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_genre']=cfg.favorited_advanced_audiobook_library_genre
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['track_author']=cfg.favorited_advanced_audiobook_track_author
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['author']=cfg.favorited_advanced_audiobook_author
        config_data['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']['library_author']=cfg.favorited_advanced_audiobook_library_author
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action']=cfg.whitetagged_behavior_audiobook[0]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['user_conditional']=cfg.whitetagged_behavior_audiobook[1]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['played_conditional']=cfg.whitetagged_behavior_audiobook[2]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action_control']=cfg.whitetagged_behavior_audiobook[3]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action']=cfg.blacktagged_behavior_audiobook[0]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['user_conditional']=cfg.blacktagged_behavior_audiobook[1]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['played_conditional']=cfg.blacktagged_behavior_audiobook[2]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action_control']=cfg.blacktagged_behavior_audiobook[3]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action']=cfg.whitelisted_behavior_audiobook[0]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['user_conditional']=cfg.whitelisted_behavior_audiobook[1]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['played_conditional']=cfg.whitelisted_behavior_audiobook[2]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action_control']=cfg.whitelisted_behavior_audiobook[3]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action']=cfg.blacklisted_behavior_audiobook[0]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['user_conditional']=cfg.blacklisted_behavior_audiobook[1]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['played_conditional']=cfg.blacklisted_behavior_audiobook[2]
        config_data['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action_control']=cfg.blacklisted_behavior_audiobook[3]
    config_data['advanced_settings']['whitetags']=cfg.whitetag.split(',')
    config_data['advanced_settings']['blacktags']=cfg.blacktag.split(',')
    config_data['advanced_settings']['episode_control']['minimum_episodes']=cfg.minimum_number_episodes
    config_data['advanced_settings']['episode_control']['minimum_played_episodes']=cfg.minimum_number_played_episodes
    config_data['advanced_settings']['episode_control']['minimum_episodes_behavior']=cfg.minimum_number_episodes_behavior
    config_data['advanced_settings']['trakt_fix']['set_missing_last_played_date']['movie']=cfg.movie_set_missing_last_played_date
    config_data['advanced_settings']['trakt_fix']['set_missing_last_played_date']['episode']=cfg.episode_set_missing_last_played_date
    config_data['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audio']=cfg.audio_set_missing_last_played_date
    if (cfg.server_brand == 'jellyfin'):
        config_data['advanced_settings']['trakt_fix']['set_missing_last_played_date']['audiobook']=cfg.audiobook_set_missing_last_played_date
    config_data['advanced_settings']['console_controls']['headers']['script']['show']=cfg.print_script_header
    config_data['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['color']=cfg.script_header_format[0]
    config_data['advanced_settings']['console_controls']['headers']['script']['formatting']['font']['style']=cfg.script_header_format[2]
    config_data['advanced_settings']['console_controls']['headers']['script']['formatting']['background']['color']=cfg.script_header_format[1]
    config_data['advanced_settings']['console_controls']['headers']['user']['show']=cfg.print_user_header
    config_data['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['color']=cfg.user_header_format[0]
    config_data['advanced_settings']['console_controls']['headers']['user']['formatting']['font']['style']=cfg.user_header_format[2]
    config_data['advanced_settings']['console_controls']['headers']['user']['formatting']['background']['color']=cfg.user_header_format[1]
    config_data['advanced_settings']['console_controls']['headers']['summary']['show']=cfg.print_summary_header
    config_data['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['color']=cfg.summary_header_format[0]
    config_data['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']['style']=cfg.summary_header_format[1]
    config_data['advanced_settings']['console_controls']['headers']['summary']['formatting']['background']['color']=cfg.summary_header_format[2]
    config_data['advanced_settings']['console_controls']['footers']['script']['show']=cfg.print_script_footer
    config_data['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['color']=cfg.script_footer_format[0]
    config_data['advanced_settings']['console_controls']['footers']['script']['formatting']['font']['style']=cfg.script_footer_format[2]
    config_data['advanced_settings']['console_controls']['footers']['script']['formatting']['background']['color']=cfg.script_footer_format[1]
    config_data['advanced_settings']['console_controls']['warnings']['script']['show']=cfg.print_warnings
    config_data['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['color']=cfg.script_warnings_format[0]
    config_data['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']['style']=cfg.script_warnings_format[2]
    config_data['advanced_settings']['console_controls']['warnings']['script']['formatting']['background']['color']=cfg.script_warnings_format[1]
    config_data['advanced_settings']['console_controls']['movie']['delete']['show']=cfg.print_movie_delete_info
    config_data['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['color']=cfg.movie_delete_info_format[0]
    config_data['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']['style']=cfg.movie_delete_info_format[2]
    config_data['advanced_settings']['console_controls']['movie']['delete']['formatting']['background']['color']=cfg.movie_delete_info_format[1]
    config_data['advanced_settings']['console_controls']['movie']['keep']['show']=cfg.print_movie_keep_info
    config_data['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['color']=cfg.movie_keep_info_format[0]
    config_data['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']['style']=cfg.movie_keep_info_format[2]
    config_data['advanced_settings']['console_controls']['movie']['keep']['formatting']['background']['color']=cfg.movie_keep_info_format[1]
    config_data['advanced_settings']['console_controls']['movie']['post_processing']['show']=cfg.print_movie_post_processing_info
    config_data['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['color']=cfg.movie_post_processing_format[0]
    config_data['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']['style']=cfg.movie_post_processing_format[2]
    config_data['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['background']['color']=cfg.movie_post_processing_format[1]
    config_data['advanced_settings']['console_controls']['movie']['summary']['show']=cfg.print_movie_summary
    config_data['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['color']=cfg.movie_summary_format[0]
    config_data['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']['style']=cfg.movie_summary_format[2]
    config_data['advanced_settings']['console_controls']['movie']['summary']['formatting']['background']['color']=cfg.movie_summary_format[1]
    config_data['advanced_settings']['console_controls']['episode']['delete']['show']=cfg.print_episode_delete_info
    config_data['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['color']=cfg.episode_delete_info_format[0]
    config_data['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']['style']=cfg.episode_delete_info_format[2]
    config_data['advanced_settings']['console_controls']['episode']['delete']['formatting']['background']['color']=cfg.episode_delete_info_format[1]
    config_data['advanced_settings']['console_controls']['episode']['keep']['show']=cfg.print_episode_keep_info
    config_data['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['color']=cfg.episode_keep_info_format[0]
    config_data['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']['style']=cfg.episode_keep_info_format[2]
    config_data['advanced_settings']['console_controls']['episode']['keep']['formatting']['background']['color']=cfg.episode_keep_info_format[1]
    config_data['advanced_settings']['console_controls']['episode']['post_processing']['show']=cfg.print_episode_post_processing_info
    config_data['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['color']=cfg.episode_post_processing_format[0]
    config_data['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']['style']=cfg.episode_post_processing_format[2]
    config_data['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['background']['color']=cfg.episode_post_processing_format[1]
    config_data['advanced_settings']['console_controls']['episode']['summary']['show']=cfg.print_episode_summary
    config_data['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['color']=cfg.episode_summary_format[0]
    config_data['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']['style']=cfg.episode_summary_format[2]
    config_data['advanced_settings']['console_controls']['episode']['summary']['formatting']['background']['color']=cfg.episode_summary_format[1]
    config_data['advanced_settings']['console_controls']['audio']['delete']['show']=cfg.print_audio_delete_info
    config_data['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['color']=cfg.audio_delete_info_format[0]
    config_data['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']['style']=cfg.audio_delete_info_format[2]
    config_data['advanced_settings']['console_controls']['audio']['delete']['formatting']['background']['color']=cfg.audio_delete_info_format[1]
    config_data['advanced_settings']['console_controls']['audio']['keep']['show']=cfg.print_audio_keep_info
    config_data['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['color']=cfg.audio_keep_info_format[0]
    config_data['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']['style']=cfg.audio_keep_info_format[2]
    config_data['advanced_settings']['console_controls']['audio']['keep']['formatting']['background']['color']=cfg.audio_keep_info_format[1]
    config_data['advanced_settings']['console_controls']['audio']['post_processing']['show']=cfg.print_audio_post_processing_info
    config_data['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['color']=cfg.audio_post_processing_format[0]
    config_data['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']['style']=cfg.audio_post_processing_format[2]
    config_data['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['background']['color']=cfg.audio_post_processing_format[1]
    config_data['advanced_settings']['console_controls']['audio']['summary']['show']=cfg.print_audio_summary
    config_data['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['color']=cfg.audio_summary_format[0]
    config_data['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']['style']=cfg.audio_summary_format[2]
    config_data['advanced_settings']['console_controls']['audio']['summary']['formatting']['background']['color']=cfg.audio_summary_format[1]
    if (cfg.server_brand == 'jellyfin'):
        config_data['advanced_settings']['console_controls']['audiobook']['delete']['show']=cfg.print_audiobook_delete_info
        config_data['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['color']=cfg.audiobook_delete_info_format[0]
        config_data['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']['style']=cfg.audiobook_delete_info_format[2]
        config_data['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['background']['color']=cfg.audiobook_delete_info_format[1]
        config_data['advanced_settings']['console_controls']['audiobook']['keep']['show']=cfg.print_audiobook_keep_info
        config_data['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['color']=cfg.audiobook_keep_info_format[0]
        config_data['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']['style']=cfg.audiobook_keep_info_format[2]
        config_data['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['background']['color']=cfg.audiobook_keep_info_format[1]
        config_data['advanced_settings']['console_controls']['audiobook']['post_processing']['show']=cfg.print_audiobook_post_processing_info
        config_data['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['color']=cfg.audiobook_post_processing_format[0]
        config_data['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']['style']=cfg.audiobook_post_processing_format[2]
        config_data['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['background']['color']=cfg.audiobook_post_processing_format[1]
        config_data['advanced_settings']['console_controls']['audiobook']['summary']['show']=cfg.print_audiobook_summary
        config_data['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['color']=cfg.audiobook_summary_format[0]
        config_data['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']['style']=cfg.audiobook_summary_format[2]
        config_data['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['background']['color']=cfg.audiobook_summary_format[1]
    config_data['advanced_settings']['UPDATE_CONFIG']=cfg.UPDATE_CONFIG
    config_data['advanced_settings']['REMOVE_FILES']=cfg.REMOVE_FILES
    config_data['admin_settings']['server']['brand']=cfg.server_brand
    config_data['admin_settings']['server']['url']=cfg.server_url
    config_data['admin_settings']['server']['auth_key']=cfg.auth_key
    config_data['admin_settings']['behavior']['list']=cfg.library_setup_behavior
    config_data['admin_settings']['behavior']['matching']=cfg.library_matching_behavior

    config_data['admin_settings']['users']+=libConvertLegacyToYAML(cfg.user_wl_libs,cfg.user_bl_libs)

    config_data['admin_settings']['api_controls']['attempts']=cfg.api_query_attempts
    config_data['admin_settings']['api_controls']['item_limit']=cfg.api_query_item_limit
    config_data['admin_settings']['cache']['size']=cfg.api_query_cache_size
    config_data['admin_settings']['cache']['fallback_behavior']=cfg.api_query_cache_fallback_behavior
    config_data['admin_settings']['cache']['last_accessed_time']=cfg.api_query_cache_last_accessed_time
    config_data['DEBUG']=cfg.DEBUG

    if (configPath == None):
        configPath=get_current_directory()

    #Save the config file
    with open(configPath / (configFileNameNoExt + '.yaml'),'w') as file:
        file.write('---\n')
        yaml.safe_dump(config_data,file,sort_keys=False)
        file.write('...')