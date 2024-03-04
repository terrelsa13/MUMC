from mumc_modules.mumc_compare_items import keys_exist

#Set yaml config skeleton
def setYAMLConfigSkeleton(the_dict):
    if (keys_exist(the_dict,'admin_settings','server','brand')):
        server_brand=the_dict['admin_settings']['server']['brand']
    else: #(keys_exist(the_dict,'server_brand')):
        server_brand=the_dict['server_brand']

    the_dict['basic_settings']={}
    the_dict['basic_settings']['filter_statements']={}
    the_dict['basic_settings']['filter_statements']['movie']={}
    the_dict['basic_settings']['filter_statements']['movie']['played']={}
    the_dict['basic_settings']['filter_statements']['movie']['created']={}

    the_dict['basic_settings']['filter_statements']['episode']={}
    the_dict['basic_settings']['filter_statements']['episode']['played']={}
    the_dict['basic_settings']['filter_statements']['episode']['created']={}

    the_dict['basic_settings']['filter_statements']['audio']={}
    the_dict['basic_settings']['filter_statements']['audio']['played']={}
    the_dict['basic_settings']['filter_statements']['audio']['created']={}

    if (server_brand == 'jellyfin'):
        the_dict['basic_settings']['filter_statements']['audiobook']={}
        the_dict['basic_settings']['filter_statements']['audiobook']['played']={}
        the_dict['basic_settings']['filter_statements']['audiobook']['created']={}

    the_dict['advanced_settings']={}
    the_dict['advanced_settings']['filter_statements']={}
    the_dict['advanced_settings']['filter_statements']['movie']={}
    the_dict['advanced_settings']['filter_statements']['movie']['query_filter']={}
    the_dict['advanced_settings']['filter_statements']['movie']['query_filter']['favorited']=None
    the_dict['advanced_settings']['filter_statements']['movie']['query_filter']['whitetagged']=None
    the_dict['advanced_settings']['filter_statements']['movie']['query_filter']['blacktagged']=None
    the_dict['advanced_settings']['filter_statements']['movie']['query_filter']['whitelisted']=None
    the_dict['advanced_settings']['filter_statements']['movie']['query_filter']['blacklisted']=None

    the_dict['advanced_settings']['filter_statements']['episode']={}
    the_dict['advanced_settings']['filter_statements']['episode']['query_filter']={}
    the_dict['advanced_settings']['filter_statements']['episode']['query_filter']['favorited']=None
    the_dict['advanced_settings']['filter_statements']['episode']['query_filter']['whitetagged']=None
    the_dict['advanced_settings']['filter_statements']['episode']['query_filter']['blacktagged']=None
    the_dict['advanced_settings']['filter_statements']['episode']['query_filter']['whitelisted']=None
    the_dict['advanced_settings']['filter_statements']['episode']['query_filter']['blacklisted']=None

    the_dict['advanced_settings']['filter_statements']['audio']={}
    the_dict['advanced_settings']['filter_statements']['audio']['query_filter']={}
    the_dict['advanced_settings']['filter_statements']['audio']['query_filter']['favorited']=None
    the_dict['advanced_settings']['filter_statements']['audio']['query_filter']['whitetagged']=None
    the_dict['advanced_settings']['filter_statements']['audio']['query_filter']['blacktagged']=None
    the_dict['advanced_settings']['filter_statements']['audio']['query_filter']['whitelisted']=None
    the_dict['advanced_settings']['filter_statements']['audio']['query_filter']['blacklisted']=None

    if (server_brand == 'jellyfin'):
        the_dict['advanced_settings']['filter_statements']['audiobook']={}
        the_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']={}
        the_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['favorited']=None
        the_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitetagged']=None
        the_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacktagged']=None
        the_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['whitelisted']=None
        the_dict['advanced_settings']['filter_statements']['audiobook']['query_filter']['blacklisted']=None

    the_dict['advanced_settings']['behavioral_statements']={}
    the_dict['advanced_settings']['behavioral_statements']['movie']={}
    the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']={}
    the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['action_control']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['dynamic_behavior']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['favorited']['extra']={}

    the_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']={}
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['dynamic_behavior']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitetagged']['tags']=[]

    the_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']={}
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['dynamic_behavior']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacktagged']['tags']=[]

    the_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']={}
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['movie']['whitelisted']['dynamic_behavior']=None

    the_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']={}
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['movie']['blacklisted']['dynamic_behavior']=None

    the_dict['advanced_settings']['behavioral_statements']['episode']={}
    the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']={}
    the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['action_control']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['dynamic_behavior']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['favorited']['extra']={}

    the_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']={}
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['dynamic_behavior']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitetagged']['tags']=[]

    the_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']={}
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['dynamic_behavior']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacktagged']['tags']=[]

    the_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']={}
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['episode']['whitelisted']['dynamic_behavior']=None

    the_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']={}
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['episode']['blacklisted']['dynamic_behavior']=None

    the_dict['advanced_settings']['behavioral_statements']['audio']={}
    the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']={}
    the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['action_control']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['dynamic_behavior']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['favorited']['extra']={}

    the_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']={}
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['dynamic_behavior']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitetagged']['tags']=[]

    the_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']={}
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['dynamic_behavior']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacktagged']['tags']=[]

    the_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']={}
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['audio']['whitelisted']['dynamic_behavior']=None

    the_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']={}
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']['user_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']['played_conditional']=None
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']['action_control']=-1
    the_dict['advanced_settings']['behavioral_statements']['audio']['blacklisted']['dynamic_behavior']=None

    if (server_brand == 'jellyfin'):
        the_dict['advanced_settings']['behavioral_statements']['audiobook']={}
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']={}
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['user_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['played_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['action_control']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['dynamic_behavior']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['favorited']['extra']={}

        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']={}
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['user_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['played_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['action_control']=-1
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['dynamic_behavior']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitetagged']['tags']=[]

        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']={}
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['user_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['played_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['action_control']=-1
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['dynamic_behavior']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacktagged']['tags']=[]

        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']={}
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['user_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['played_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['action_control']=-1
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['whitelisted']['dynamic_behavior']=None

        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']={}
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['user_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['played_conditional']=None
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['action_control']=-1
        the_dict['advanced_settings']['behavioral_statements']['audiobook']['blacklisted']['dynamic_behavior']=None

    the_dict['advanced_settings']['whitetags']=[]
    the_dict['advanced_settings']['blacktags']=[]
    
    the_dict['advanced_settings']['delete_empty_folders']={}
    the_dict['advanced_settings']['delete_empty_folders']['episode']={}
    the_dict['advanced_settings']['delete_empty_folders']['episode']['season']=False
    the_dict['advanced_settings']['delete_empty_folders']['episode']['series']=False

    the_dict['advanced_settings']['episode_control']={}

    the_dict['advanced_settings']['trakt_fix']={}
    the_dict['advanced_settings']['trakt_fix']['set_missing_last_played_date']={}

    the_dict['advanced_settings']['console_controls']={}
    the_dict['advanced_settings']['console_controls']['headers']={}
    the_dict['advanced_settings']['console_controls']['headers']['script']={}
    the_dict['advanced_settings']['console_controls']['headers']['script']['show']=True
    the_dict['advanced_settings']['console_controls']['headers']['script']['formatting']={}
    the_dict['advanced_settings']['console_controls']['headers']['script']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['headers']['script']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['headers']['user']={}
    the_dict['advanced_settings']['console_controls']['headers']['user']['show']=True
    the_dict['advanced_settings']['console_controls']['headers']['user']['formatting']={}
    the_dict['advanced_settings']['console_controls']['headers']['user']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['headers']['user']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['headers']['summary']={}
    the_dict['advanced_settings']['console_controls']['headers']['summary']['show']=True
    the_dict['advanced_settings']['console_controls']['headers']['summary']['formatting']={}
    the_dict['advanced_settings']['console_controls']['headers']['summary']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['headers']['summary']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['footers']={}
    the_dict['advanced_settings']['console_controls']['footers']['script']={}
    the_dict['advanced_settings']['console_controls']['footers']['script']['show']=True
    the_dict['advanced_settings']['console_controls']['footers']['script']['formatting']={}
    the_dict['advanced_settings']['console_controls']['footers']['script']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['footers']['script']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['warnings']={}
    the_dict['advanced_settings']['console_controls']['warnings']['script']={}
    the_dict['advanced_settings']['console_controls']['warnings']['script']['show']=True
    the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting']={}
    the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['movie']={}
    the_dict['advanced_settings']['console_controls']['movie']['delete']={}
    the_dict['advanced_settings']['console_controls']['movie']['delete']['show']=True
    the_dict['advanced_settings']['console_controls']['movie']['delete']['formatting']={}
    the_dict['advanced_settings']['console_controls']['movie']['delete']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['movie']['delete']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['movie']['keep']={}
    the_dict['advanced_settings']['console_controls']['movie']['keep']['show']=True
    the_dict['advanced_settings']['console_controls']['movie']['keep']['formatting']={}
    the_dict['advanced_settings']['console_controls']['movie']['keep']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['movie']['keep']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['movie']['post_processing']={}
    the_dict['advanced_settings']['console_controls']['movie']['post_processing']['show']=True
    the_dict['advanced_settings']['console_controls']['movie']['post_processing']['formatting']={}
    the_dict['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['movie']['post_processing']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['movie']['summary']={}
    the_dict['advanced_settings']['console_controls']['movie']['summary']['show']=True
    the_dict['advanced_settings']['console_controls']['movie']['summary']['formatting']={}
    the_dict['advanced_settings']['console_controls']['movie']['summary']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['movie']['summary']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['episode']={}
    the_dict['advanced_settings']['console_controls']['episode']['delete']={}
    the_dict['advanced_settings']['console_controls']['episode']['delete']['show']=True
    the_dict['advanced_settings']['console_controls']['episode']['delete']['formatting']={}
    the_dict['advanced_settings']['console_controls']['episode']['delete']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['episode']['delete']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['episode']['keep']={}
    the_dict['advanced_settings']['console_controls']['episode']['keep']['show']=True
    the_dict['advanced_settings']['console_controls']['episode']['keep']['formatting']={}
    the_dict['advanced_settings']['console_controls']['episode']['keep']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['episode']['keep']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['episode']['post_processing']={}
    the_dict['advanced_settings']['console_controls']['episode']['post_processing']['show']=True
    the_dict['advanced_settings']['console_controls']['episode']['post_processing']['formatting']={}
    the_dict['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['episode']['post_processing']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['episode']['summary']={}
    the_dict['advanced_settings']['console_controls']['episode']['summary']['show']=True
    the_dict['advanced_settings']['console_controls']['episode']['summary']['formatting']={}
    the_dict['advanced_settings']['console_controls']['episode']['summary']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['episode']['summary']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['audio']={}
    the_dict['advanced_settings']['console_controls']['audio']['delete']={}
    the_dict['advanced_settings']['console_controls']['audio']['delete']['show']=True
    the_dict['advanced_settings']['console_controls']['audio']['delete']['formatting']={}
    the_dict['advanced_settings']['console_controls']['audio']['delete']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['audio']['delete']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['audio']['keep']={}
    the_dict['advanced_settings']['console_controls']['audio']['keep']['show']=True
    the_dict['advanced_settings']['console_controls']['audio']['keep']['formatting']={}
    the_dict['advanced_settings']['console_controls']['audio']['keep']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['audio']['keep']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['audio']['post_processing']={}
    the_dict['advanced_settings']['console_controls']['audio']['post_processing']['show']=True
    the_dict['advanced_settings']['console_controls']['audio']['post_processing']['formatting']={}
    the_dict['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['audio']['post_processing']['formatting']['background']={}

    the_dict['advanced_settings']['console_controls']['audio']['summary']={}
    the_dict['advanced_settings']['console_controls']['audio']['summary']['show']=True
    the_dict['advanced_settings']['console_controls']['audio']['summary']['formatting']={}
    the_dict['advanced_settings']['console_controls']['audio']['summary']['formatting']['font']={}
    the_dict['advanced_settings']['console_controls']['audio']['summary']['formatting']['background']={}

    if (server_brand == 'jellyfin'):
        the_dict['advanced_settings']['console_controls']['audiobook']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['delete']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['delete']['show']=True
        the_dict['advanced_settings']['console_controls']['audiobook']['delete']['formatting']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['font']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['delete']['formatting']['background']={}

        the_dict['advanced_settings']['console_controls']['audiobook']['keep']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['keep']['show']=True
        the_dict['advanced_settings']['console_controls']['audiobook']['keep']['formatting']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['font']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['keep']['formatting']['background']={}

        the_dict['advanced_settings']['console_controls']['audiobook']['post_processing']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['post_processing']['show']=True
        the_dict['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['font']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['post_processing']['formatting']['background']={}

        the_dict['advanced_settings']['console_controls']['audiobook']['summary']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['summary']['show']=True
        the_dict['advanced_settings']['console_controls']['audiobook']['summary']['formatting']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['font']={}
        the_dict['advanced_settings']['console_controls']['audiobook']['summary']['formatting']['background']={}

    the_dict['admin_settings']={}

    the_dict['admin_settings']['server']={}

    the_dict['admin_settings']['behavior']={}

    the_dict['admin_settings']['users']=[]

    the_dict['admin_settings']['api_controls']={}

    the_dict['admin_settings']['cache']={}

    return the_dict