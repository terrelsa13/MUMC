import sys
from mumc_modules.mumc_versions import get_semantic_version_parts,checkYAMLVersion,get_script_version
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_compare_items import keys_exist_return_value
from mumc_modules.mumc_tagged import get_isFilterStatementTag
from mumc_modules.mumc_data_checks import data_checker


#Check select config variables are as expected
def cfgCheckYAML(cfg,init_dict):

    #TODO: find clean way to put cfg.variable_names in a dict/list/etc... and use the dict/list/etc... to call the varibles by name in a for loop

    #Start as blank error string
    error_found_in_mumc_config_yaml=''
    filter_tag_formatting_value_url=''

#######################################################################################################

    cfgChecker=data_checker(cfg,init_dict)

    server_brand='invalid'
    if (not ((check:=cfgChecker.checkString('admin_settings','server','brand',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['emby','jellyfin'])) == None)):
        server_brand=check

#######################################################################################################

    #sets of tags for user later
    filter_movie_whitetag_set=set()
    filter_movie_blacktag_set=set()
    filter_episode_whitetag_set=set()
    filter_episode_blacktag_set=set()
    filter_audio_whitetag_set=set()
    filter_audio_blacktag_set=set()
    if (isJellyfinServer(server_brand)):
        filter_audiobook_whitetag_set=set()
        filter_audiobook_blacktag_set=set()
    movie_whitetag_set=set()
    movie_blacktag_set=set()
    episode_whitetag_set=set()
    episode_blacktag_set=set()
    audio_whitetag_set=set()
    audio_blacktag_set=set()
    if (isJellyfinServer(server_brand)):
        audiobook_whitetag_set=set()
        audiobook_blacktag_set=set()
    global_whitetag_set=set()
    global_blacktag_set=set()

#######################################################################################################

    error_found_in_mumc_config_yaml+=checkYAMLVersion(cfg,init_dict)

#######################################################################################################

    errorFlag=True
    if (not ((check:=cfgChecker.checkString('version',value=None,instanceType=cfgChecker.str,minLength=5,maxLength=None,errOut=False,comparisonValues=None)) == None)):
        check_parts=get_semantic_version_parts(check)
        if (not (cfgChecker.checkInteger(*(),value=check_parts['major'],instanceType=cfgChecker.int,minValue=0,maxValue=None,errOut=False,comparisonValues=None) == None)):
            if (not (cfgChecker.checkInteger(*(),value=check_parts['minor'],instanceType=cfgChecker.int,minValue=0,maxValue=None,errOut=False,comparisonValues=None) == None)):
                if (not (cfgChecker.checkInteger(*(),value=check_parts['patch'],instanceType=cfgChecker.int,minValue=0,maxValue=None,errOut=False,comparisonValues=None) == None)):
                    if (not (cfgChecker.checkString(*(),value=check_parts['release'],instanceType=cfgChecker.str,minLength=5,maxLength=None,errOut=False,comparisonValues=['alpha','beta','stable']) == None)):
                        errorFlag=False
    if (errorFlag):
        cfgChecker.setCustomErrorText('ConfigValueError: version must be in the semantic versioning syntax\n\tFormatted as shown: MAJOR#.MINOR#.PATCH# (e.g. ' + get_script_version() +')')

#######################################################################################################

    cfgChecker.checkString('admin_settings','server','url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('admin_settings','server','auth_key',value=None,instanceType=cfgChecker.str,minLength=32,maxLength=32,errOut=True,comparisonValues=None)

    cfgChecker.checkAlphaNumeric('admin_settings','server','admin_id',value=None,instanceType=cfgChecker.alnum,minLength=None,maxLength=None,errOut=True,comparisonValues=None) == None

#######################################################################################################

    user_ids_check_list=[]
    user_names_check_list=[]
    if (not ((userList:=cfgChecker.checkList('admin_settings','users',value=None,instanceType=cfgChecker.list,minLength=1,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
        for userInfo in userList:
            if (not ((userInfo:=cfgChecker.checkDict('admin_settings','users',userList.index(userInfo),value=None,instanceType=cfgChecker.dict,minLength=4,maxLength=4,errOut=True,comparisonValues=None)) == None)):
                if (not ((user_id:=cfgChecker.checkAlphaNumeric('admin_settings','users',userList.index(userInfo),'user_id',value=None,instanceType=cfgChecker.alnum,minLength=1,maxLength=32,errOut=True,comparisonValues=None)) == None)):
                    user_ids_check_list.append(user_id)
                    if (not ((user_name:=cfgChecker.checkString('admin_settings','users',userList.index(userInfo),'user_name',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                        user_names_check_list.append(user_name)
                        if (not ((userWhitelist:=cfgChecker.checkList('admin_settings','users',userList.index(userInfo),'whitelist',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                            for userWhitelistInfo in userWhitelist:
                                if (not ((userWhitelistInfo:=cfgChecker.checkDict('admin_settings','users',userList.index(userInfo),'whitelist',userWhitelist.index(userWhitelistInfo),value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                                    cfgChecker.checkAlphaNumeric('admin_settings','users',userList.index(userInfo),'whitelist',userWhitelist.index(userWhitelistInfo),'lib_id',value=None,instanceType=cfgChecker.alnum,minLength=1,maxLength=32,errOut=True,comparisonValues=None)
                                    cfgChecker.checkString('admin_settings','users',userList.index(userInfo),'whitelist',userWhitelist.index(userWhitelistInfo),'collection_type',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=['movies','tvshows','music','audiobooks'])
                                    cfgChecker.checkString('admin_settings','users',userList.index(userInfo),'whitelist',userWhitelist.index(userWhitelistInfo),'path',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
                                    cfgChecker.checkString('admin_settings','users',userList.index(userInfo),'whitelist',userWhitelist.index(userWhitelistInfo),'network_path',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
                                    #cfgChecker.checkString('admin_settings','users',userList.index(userInfo),'whitelist',userWhitelist.index(userWhitelistInfo),'subfolder_id',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
                                    cfgChecker.checkBoolean('admin_settings','users',userList.index(userInfo),'whitelist',userWhitelist.index(userWhitelistInfo),'lib_enabled',value=None,instanceType=cfgChecker.bool,errOut=True)
                        if (not ((userblacklist:=cfgChecker.checkList('admin_settings','users',userList.index(userInfo),'blacklist',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                            for userblacklistInfo in userblacklist:
                                if (not ((userblacklistInfo:=cfgChecker.checkDict('admin_settings','users',userList.index(userInfo),'blacklist',userblacklist.index(userblacklistInfo),value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                                    cfgChecker.checkAlphaNumeric('admin_settings','users',userList.index(userInfo),'blacklist',userblacklist.index(userblacklistInfo),'lib_id',value=None,instanceType=cfgChecker.alnum,minLength=1,maxLength=32,errOut=True,comparisonValues=None)
                                    cfgChecker.checkString('admin_settings','users',userList.index(userInfo),'blacklist',userblacklist.index(userblacklistInfo),'collection_type',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=['movies','tvshows','music','audiobooks'])
                                    cfgChecker.checkString('admin_settings','users',userList.index(userInfo),'blacklist',userblacklist.index(userblacklistInfo),'path',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
                                    cfgChecker.checkString('admin_settings','users',userList.index(userInfo),'blacklist',userblacklist.index(userblacklistInfo),'network_path',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
                                    #cfgChecker.checkString('admin_settings','users',userList.index(userInfo),'blacklist',userblacklist.index(userblacklistInfo),'subfolder_id',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
                                    cfgChecker.checkBoolean('admin_settings','users',userList.index(userInfo),'blacklist',userblacklist.index(userblacklistInfo),'lib_enabled',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkInteger('basic_settings','filter_statements','movie','played','condition_days',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkString('basic_settings','filter_statements','movie','played','count_equality',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
    cfgChecker.checkInteger('basic_settings','filter_statements','movie','played','count',value=None,instanceType=cfgChecker.int,minValue=1,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('basic_settings','filter_statements','movie','created','condition_days',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkString('basic_settings','filter_statements','movie','created','count_equality',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
    cfgChecker.checkInteger('basic_settings','filter_statements','movie','created','count',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('basic_settings','filter_statements','movie','created','behavioral_control',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkInteger('basic_settings','filter_statements','episode','played','condition_days',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkString('basic_settings','filter_statements','episode','played','count_equality',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
    cfgChecker.checkInteger('basic_settings','filter_statements','episode','played','count',value=None,instanceType=cfgChecker.int,minValue=1,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('basic_settings','filter_statements','episode','created','condition_days',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkString('basic_settings','filter_statements','episode','created','count_equality',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
    cfgChecker.checkInteger('basic_settings','filter_statements','episode','created','count',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('basic_settings','filter_statements','episode','created','behavioral_control',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkInteger('basic_settings','filter_statements','audio','played','condition_days',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkString('basic_settings','filter_statements','audio','played','count_equality',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
    cfgChecker.checkInteger('basic_settings','filter_statements','audio','played','count',value=None,instanceType=cfgChecker.int,minValue=1,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('basic_settings','filter_statements','audio','created','condition_days',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkString('basic_settings','filter_statements','audio','created','count_equality',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
    cfgChecker.checkInteger('basic_settings','filter_statements','audio','created','count',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('basic_settings','filter_statements','audio','created','behavioral_control',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        cfgChecker.checkInteger('basic_settings','filter_statements','audiobook','played','condition_days',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
        cfgChecker.checkString('basic_settings','filter_statements','audiobook','played','count_equality',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
        cfgChecker.checkInteger('basic_settings','filter_statements','audiobook','played','count',value=None,instanceType=cfgChecker.int,minValue=1,maxValue=730500,errOut=False,comparisonValues=None)
        cfgChecker.checkInteger('basic_settings','filter_statements','audiobook','created','condition_days',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
        cfgChecker.checkString('basic_settings','filter_statements','audiobook','created','count_equality',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
        cfgChecker.checkInteger('basic_settings','filter_statements','audiobook','created','count',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
        cfgChecker.checkBoolean('basic_settings','filter_statements','audiobook','created','behavioral_control',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    storedFilterTags={}
    storedFilterTags['movie']={}
    storedFilterTags['episode']={}
    storedFilterTags['audio']={}
    if (isJellyfinServer(server_brand)):
        storedFilterTags['audiobook']={}
    storedFilterTags['movie']['whitetags']=[]
    storedFilterTags['movie']['blacktags']=[]
    storedFilterTags['episode']['whitetags']=[]
    storedFilterTags['episode']['blacktags']=[]
    storedFilterTags['audio']['whitetags']=[]
    storedFilterTags['audio']['blacktags']=[]
    if (isJellyfinServer(server_brand)):
        storedFilterTags['audibook']['whitetags']=[]
        storedFilterTags['audibook']['blacktags']=[]

    if (not ((filterTagList:=cfgChecker.checkList('basic_settings','filter_tags','movie','whitetags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
        storedFilterTags['movie']['whitetags']=filterTagList
        for tag in filterTagList:
            cfgChecker.checkString('basic_settings','filter_tags','movie','whitetags',filterTagList.index(tag),value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
            if (tagPartList:=get_isFilterStatementTag(tag)):
                tagType=cfgChecker.checkString(*(),value=tagPartList[0],instanceType=cfgChecker.str,minLength=6,maxLength=7,errOut=True,comparisonValues=['played','created'])
                cfgChecker.checkInteger(*(),value=tagPartList[1],instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
                cfgChecker.checkString(*(),value=tagPartList[2],instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
                cfgChecker.checkInteger(*(),value=tagPartList[3],instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
                if (tagType == 'created'):
                    cfgChecker.checkBoolean(*(),value=tagPartList[4],instanceType=cfgChecker.bool,errOut=True)

    if (not ((filterTagList:=cfgChecker.checkList('basic_settings','filter_tags','movie','blacktags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
        storedFilterTags['movie']['blacktags']=filterTagList
        for tag in filterTagList:
            cfgChecker.checkString('basic_settings','filter_tags','movie','blacktags',filterTagList.index(tag),value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
            if (tagPartList:=get_isFilterStatementTag(tag)):
                tagType=cfgChecker.checkString(*(),value=tagPartList[0],instanceType=cfgChecker.str,minLength=6,maxLength=7,errOut=True,comparisonValues=['played','created'])
                cfgChecker.checkInteger(*(),value=tagPartList[1],instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
                cfgChecker.checkString(*(),value=tagPartList[2],instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
                cfgChecker.checkInteger(*(),value=tagPartList[3],instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
                if (tagType == 'created'):
                    cfgChecker.checkBoolean(*(),value=tagPartList[4],instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    if (not ((filterTagList:=cfgChecker.checkList('basic_settings','filter_tags','episode','whitetags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
        storedFilterTags['episode']['whitetags']=filterTagList
        for tag in filterTagList:
            cfgChecker.checkString('basic_settings','filter_tags','episode','whitetags',filterTagList.index(tag),value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
            if (tagPartList:=get_isFilterStatementTag(tag)):
                tagType=cfgChecker.checkString(*(),value=tagPartList[0],instanceType=cfgChecker.str,minLength=6,maxLength=7,errOut=True,comparisonValues=['played','created'])
                cfgChecker.checkInteger(*(),value=tagPartList[1],instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
                cfgChecker.checkString(*(),value=tagPartList[2],instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
                cfgChecker.checkInteger(*(),value=tagPartList[3],instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
                if (tagType == 'created'):
                    cfgChecker.checkBoolean(*(),value=tagPartList[4],instanceType=cfgChecker.bool,errOut=True)

    if (not ((filterTagList:=cfgChecker.checkList('basic_settings','filter_tags','episode','blacktags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
        storedFilterTags['episode']['blacktags']=filterTagList
        for tag in filterTagList:
            cfgChecker.checkString('basic_settings','filter_tags','episode','blacktags',filterTagList.index(tag),value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
            if (tagPartList:=get_isFilterStatementTag(tag)):
                tagType=cfgChecker.checkString(*(),value=tagPartList[0],instanceType=cfgChecker.str,minLength=6,maxLength=7,errOut=True,comparisonValues=['played','created'])
                cfgChecker.checkInteger(*(),value=tagPartList[1],instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
                cfgChecker.checkString(*(),value=tagPartList[2],instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
                cfgChecker.checkInteger(*(),value=tagPartList[3],instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
                if (tagType == 'created'):
                    cfgChecker.checkBoolean(*(),value=tagPartList[4],instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    if (not ((filterTagList:=cfgChecker.checkList('basic_settings','filter_tags','audio','whitetags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
        storedFilterTags['audio']['whitetags']=filterTagList
        for tag in filterTagList:
            cfgChecker.checkString('basic_settings','filter_tags','audio','whitetags',filterTagList.index(tag),value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
            if (tagPartList:=get_isFilterStatementTag(tag)):
                tagType=cfgChecker.checkString(*(),value=tagPartList[0],instanceType=cfgChecker.str,minLength=6,maxLength=7,errOut=True,comparisonValues=['played','created'])
                cfgChecker.checkInteger(*(),value=tagPartList[1],instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
                cfgChecker.checkString(*(),value=tagPartList[2],instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
                cfgChecker.checkInteger(*(),value=tagPartList[3],instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
                if (tagType == 'created'):
                    cfgChecker.checkBoolean(*(),value=tagPartList[4],instanceType=cfgChecker.bool,errOut=True)

    if (not ((filterTagList:=cfgChecker.checkList('basic_settings','filter_tags','audio','blacktags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
        storedFilterTags['audio']['blacktags']=filterTagList
        for tag in filterTagList:
            cfgChecker.checkString('basic_settings','filter_tags','audio','blacktags',filterTagList.index(tag),value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
            if (tagPartList:=get_isFilterStatementTag(tag)):
                tagType=cfgChecker.checkString(*(),value=tagPartList[0],instanceType=cfgChecker.str,minLength=6,maxLength=7,errOut=True,comparisonValues=['played','created'])
                cfgChecker.checkInteger(*(),value=tagPartList[1],instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
                cfgChecker.checkString(*(),value=tagPartList[2],instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
                cfgChecker.checkInteger(*(),value=tagPartList[3],instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
                if (tagType == 'created'):
                    cfgChecker.checkBoolean(*(),value=tagPartList[4],instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        if (not ((filterTagList:=cfgChecker.checkList('basic_settings','filter_tags','audiobook','whitetags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
            storedFilterTags['audiobook']['whitetags']=filterTagList
            for tag in filterTagList:
                cfgChecker.checkString('basic_settings','filter_tags','audiobook','whitetags',filterTagList.index(tag),value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
                if (tagPartList:=get_isFilterStatementTag(tag)):
                    tagType=cfgChecker.checkString(*(),value=tagPartList[0],instanceType=cfgChecker.str,minLength=6,maxLength=7,errOut=True,comparisonValues=['played','created'])
                    cfgChecker.checkInteger(*(),value=tagPartList[1],instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
                    cfgChecker.checkString(*(),value=tagPartList[2],instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
                    cfgChecker.checkInteger(*(),value=tagPartList[3],instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
                    if (tagType == 'created'):
                        cfgChecker.checkBoolean(*(),value=tagPartList[4],instanceType=cfgChecker.bool,errOut=True)

        if (not ((filterTagList:=cfgChecker.checkList('basic_settings','filter_tags','audiobook','blacktags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
            storedFilterTags['audiobook']['blacktags']=filterTagList
            for tag in filterTagList:
                cfgChecker.checkString('basic_settings','filter_tags','audiobook','blacktags',filterTagList.index(tag),value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)
                if (tagPartList:=get_isFilterStatementTag(tag)):
                    tagType=cfgChecker.checkString(*(),value=tagPartList[0],instanceType=cfgChecker.str,minLength=6,maxLength=7,errOut=True,comparisonValues=['played','created'])
                    cfgChecker.checkInteger(*(),value=tagPartList[1],instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)
                    cfgChecker.checkString(*(),value=tagPartList[2],instanceType=cfgChecker.str,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])
                    cfgChecker.checkInteger(*(),value=tagPartList[3],instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)
                    if (tagType == 'created'):
                        cfgChecker.checkBoolean(*(),value=tagPartList[4],instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','whitelisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','whitelisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','whitelisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','whitelisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)
    #cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','whitelisted','whitelisted',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','blacklisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','blacklisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','blacklisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','blacklisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)
    #cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','blacklisted','blacklisted',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','whitelisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','whitelisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','whitelisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','whitelisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)
    #cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','whitelisted','whitelisted',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','blacklisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','blacklisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','blacklisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','blacklisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)
    #cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','blacklisted','blacklisted',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','whitelisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','whitelisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','whitelisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','whitelisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)
    #cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','whitelisted','whitelisted',value=None,instanceType=cfgChecker.bool,errOut=True)

######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','blacklisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','blacklisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','blacklisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','blacklisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)
    #cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','blacklisted','blacklisted',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','whitelisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','whitelisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','whitelisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','whitelisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)
        #cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','whitelisted','whitelisted',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','blacklisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','blacklisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','blacklisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','blacklisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)
        #cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','blacklisted','blacklisted',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','favorited','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','favorited','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','favorited','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','favorited','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','favorited','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','favorited','extra','genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','favorited','extra','library_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitetagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitetagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitetagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','whitetagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','whitetagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacktagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacktagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacktagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','blacktagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','blacktagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitelisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitelisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitelisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','whitelisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','whitelisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacklisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacklisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacklisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','blacklisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','blacklisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','favorited','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','favorited','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','favorited','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','favorited','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','season_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','series_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','library_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','studio_network',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','studio_network_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitetagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitetagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitetagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','whitetagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','whitetagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacktagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacktagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacktagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','blacktagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','blacktagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitelisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitelisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitelisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','whitelisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','whitelisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacklisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacklisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacklisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','blacklisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','blacklisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','favorited','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','favorited','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','favorited','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','favorited','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','album_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','library_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','track_artist',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','album_artist',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitetagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitetagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitetagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','whitetagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','whitetagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacktagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacktagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacktagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','blacktagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','blacktagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitelisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitelisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitelisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','whitelisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','whitelisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacklisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacklisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
    cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacklisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
    cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','blacklisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
    cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','blacklisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','favorited','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','favorited','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','favorited','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
        cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','favorited','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','audiobook_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','library_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','track_artist',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','album_artist',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

#######################################################################################################

        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitetagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitetagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitetagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','whitetagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
        cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','whitetagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacktagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacktagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacktagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','blacktagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
        cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','blacktagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitelisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitelisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitelisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','whitelisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
        cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','whitelisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacklisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacklisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
        cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacklisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
        cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','blacklisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
        cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','blacklisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    behavioral_tags=cfgChecker.checkDict('advanced_settings','behavioral_tags','movie',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
    for behavioral_tag in behavioral_tags:
        cfgChecker.checkString(*(),value=behavioral_tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=False,comparisonValues=storedFilterTags['movie']['whitetags'] + storedFilterTags['movie']['blacktags'])
        behavioral_tag_contents=cfgChecker.checkDict(*(),value=behavioral_tags[behavioral_tag],instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=['action','user_conditional','played_conditional','action_conditional','action_control','dynamic_behavior','high_priority'])
        cfgChecker.checkString(*(),value=behavioral_tag_contents['action'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['keep','delete'])
        cfgChecker.checkString(*(),value=behavioral_tag_contents['user_conditional'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
        cfgChecker.checkString(*(),value=behavioral_tag_contents['played_conditional'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
        cfgChecker.checkInteger(*(),value=behavioral_tag_contents['action_control'],instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
        cfgChecker.checkBoolean(*(),value=behavioral_tag_contents['dynamic_behavior'],instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkBoolean(*(),value=behavioral_tag_contents['high_priority'],instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    behavioral_tags=cfgChecker.checkDict('advanced_settings','behavioral_tags','episode',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
    for behavioral_tag in behavioral_tags:
        cfgChecker.checkString(*(),value=behavioral_tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=False,comparisonValues=storedFilterTags['episode']['whitetags'] + storedFilterTags['episode']['blacktags'])
        behavioral_tag_contents=cfgChecker.checkDict(*(),value=behavioral_tags[behavioral_tag],instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=['action','user_conditional','played_conditional','action_conditional','action_control','dynamic_behavior','high_priority'])
        cfgChecker.checkString(*(),value=behavioral_tag_contents['action'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['keep','delete'])
        cfgChecker.checkString(*(),value=behavioral_tag_contents['user_conditional'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
        cfgChecker.checkString(*(),value=behavioral_tag_contents['played_conditional'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
        cfgChecker.checkInteger(*(),value=behavioral_tag_contents['action_control'],instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
        cfgChecker.checkBoolean(*(),value=behavioral_tag_contents['dynamic_behavior'],instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkBoolean(*(),value=behavioral_tag_contents['high_priority'],instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    behavioral_tags=cfgChecker.checkDict('advanced_settings','behavioral_tags','audio',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
    for behavioral_tag in behavioral_tags:
        cfgChecker.checkString(*(),value=behavioral_tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=False,comparisonValues=storedFilterTags['audio']['whitetags'] + storedFilterTags['audio']['blacktags'])
        behavioral_tag_contents=cfgChecker.checkDict(*(),value=behavioral_tags[behavioral_tag],instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=['action','user_conditional','played_conditional','action_conditional','action_control','dynamic_behavior','high_priority'])
        cfgChecker.checkString(*(),value=behavioral_tag_contents['action'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['keep','delete'])
        cfgChecker.checkString(*(),value=behavioral_tag_contents['user_conditional'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
        cfgChecker.checkString(*(),value=behavioral_tag_contents['played_conditional'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
        cfgChecker.checkInteger(*(),value=behavioral_tag_contents['action_control'],instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
        cfgChecker.checkBoolean(*(),value=behavioral_tag_contents['dynamic_behavior'],instanceType=cfgChecker.bool,errOut=True)
        cfgChecker.checkBoolean(*(),value=behavioral_tag_contents['high_priority'],instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        behavioral_tags=cfgChecker.checkDict('advanced_settings','behavioral_tags','audiobook',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
        for behavioral_tag in behavioral_tags:
            cfgChecker.checkString(*(),value=behavioral_tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=False,comparisonValues=storedFilterTags['audiobook']['whitetags'] + storedFilterTags['audiobook']['blacktags'])
            behavioral_tag_contents=cfgChecker.checkDict(*(),value=behavioral_tags[behavioral_tag],instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=['action','user_conditional','played_conditional','action_conditional','action_control','dynamic_behavior','high_priority'])
            cfgChecker.checkString(*(),value=behavioral_tag_contents['action'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['keep','delete'])
            cfgChecker.checkString(*(),value=behavioral_tag_contents['user_conditional'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])
            cfgChecker.checkString(*(),value=behavioral_tag_contents['played_conditional'],instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])
            cfgChecker.checkInteger(*(),value=behavioral_tag_contents['action_control'],instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=False,comparisonValues=None)
            cfgChecker.checkBoolean(*(),value=behavioral_tag_contents['dynamic_behavior'],instanceType=cfgChecker.bool,errOut=True)
            cfgChecker.checkBoolean(*(),value=behavioral_tag_contents['high_priority'],instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    tags=cfgChecker.checkList('advanced_settings','whitetags','global',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
    for tag in tags:
        cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
        if ((tag.find('\\') < 0) or (tag == None)):
            global_whitetag_set.add(tag)

#######################################################################################################

    tags=cfgChecker.checkList('advanced_settings','whitetags','movie',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
    for tag in tags:
        cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
        if ((tag.find('\\') < 0) or (tag == None)):
            global_whitetag_set.add(tag)

#######################################################################################################

    tags=cfgChecker.checkList('advanced_settings','whitetags','episode',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
    for tag in tags:
        cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
        if ((tag.find('\\') < 0) or (tag == None)):
            global_whitetag_set.add(tag)

#######################################################################################################

    tags=cfgChecker.checkList('advanced_settings','whitetags','audio',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
    for tag in tags:
        cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
        if ((tag.find('\\') < 0) or (tag == None)):
            global_whitetag_set.add(tag)

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        tags=cfgChecker.checkList('advanced_settings','whitetags','audiobook',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
        for tag in tags:
            cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
            if ((tag.find('\\') < 0) or (tag == None)):
                global_whitetag_set.add(tag)

#######################################################################################################

    tags=cfgChecker.checkList('advanced_settings','blacktags','global',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
    for tag in tags:
        cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
        if ((tag.find('\\') < 0) or (tag == None)):
            global_blacktag_set.add(tag)

#######################################################################################################

    tags=cfgChecker.checkList('advanced_settings','blacktags','movie',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
    for tag in tags:
        cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
        if ((tag.find('\\') < 0) or (tag == None)):
            global_blacktag_set.add(tag)

#######################################################################################################

    tags=cfgChecker.checkList('advanced_settings','blacktags','episode',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
    for tag in tags:
        cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
        if ((tag.find('\\') < 0) or (tag == None)):
            global_blacktag_set.add(tag)

#######################################################################################################

    tags=cfgChecker.checkList('advanced_settings','blacktags','audio',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
    for tag in tags:
        cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
        if ((tag.find('\\') < 0) or (tag == None)):
            global_blacktag_set.add(tag)

#######################################################################################################

    if (isJellyfinServer(server_brand)):

        tags=cfgChecker.checkList('advanced_settings','blacktags','audiobook',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)
        for tag in tags:
            cfgChecker.checkString(*(),value=tag,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
            if ((tag.find('\\') < 0) or (tag == None)):
                global_blacktag_set.add(tag)


#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','delete_empty_folders','episode','season',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkBoolean('advanced_settings','delete_empty_folders','episode','series',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkInteger('advanced_settings','episode_control','minimum_episodes',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)

    cfgChecker.checkInteger('advanced_settings','episode_control','minimum_played_episodes',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)

    behavior_values_list=['maxplayed','maxplayedmaxplayed','minplayed','minplayedminplayed','maxunplayed','maxunplayedmaxunplayed','minunplayed','minunplayedminunplayed',
                          'maxplayedmaxunplayed','minplayedminunplayed','maxplayedminunplayed','minplayedmaxunplayed','minunplayedminplayed','minunplayedmaxunplayed',
                          'minunplayedmaxplayed','minplayedmaxplayed','maxunplayedminunplayed','maxunplayedminplayed','maxunplayedmaxplayed','maxplayedminplayed']

    cfgChecker.checkString('advanced_settings','episode_control','minimum_episodes_behavior',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=user_ids_check_list + user_names_check_list + behavior_values_list)

    cfgChecker.checkBoolean('advanced_settings','episode_control','series_ended','delete_episodes',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','radarr','movie','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkBoolean('advanced_settings','radarr','movie','remove',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','sonarr','series','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkBoolean('advanced_settings','sonarr','series','remove',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkBoolean('advanced_settings','sonarr','episode','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','lidarr','album','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkBoolean('advanced_settings','lidarr','album','remove',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkBoolean('advanced_settings','lidarr','track','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','readarr','book','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkBoolean('advanced_settings','readarr','book','remove',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','trakt_fix','set_missing_last_played_date','movie',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkBoolean('advanced_settings','trakt_fix','set_missing_last_played_date','episode',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkBoolean('advanced_settings','trakt_fix','set_missing_last_played_date','audio',value=None,instanceType=cfgChecker.bool,errOut=True)

    if (isJellyfinServer(server_brand)):

        cfgChecker.checkBoolean('advanced_settings','trakt_fix','set_missing_last_played_date','audiobook',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','console_controls','headers','script','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','headers','script','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','script','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','script','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','user','show',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','user','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','user','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','user','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','summary','show',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','headers','summary','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','footers','script','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','footers','script','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','footers','script','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','footers','script','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','warnings','script','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','warnings','script','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','warnings','script','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','warnings','script','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','movie','delete','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','movie','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','movie','delete','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','movie','delete','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','movie','keep','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','movie','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','movie','keep','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','movie','keep','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','movie','post_processing','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','movie','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','movie','post_processing','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','movie','post_processing','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','movie','summary','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','movie','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','movie','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','movie','summary','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','episode','delete','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','episode','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','delete','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','delete','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','episode','keep','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','episode','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','keep','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','keep','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','post_processing','show',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','post_processing','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','post_processing','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','episode','summary','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','episode','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','episode','summary','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','audio','delete','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','audio','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','audio','delete','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','audio','delete','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','audio','keep','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','audio','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','audio','keep','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','audio','keep','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','audio','post_processing','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','audio','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','audio','post_processing','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','audio','post_processing','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkBoolean('advanced_settings','console_controls','audio','summary','show',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('advanced_settings','console_controls','audio','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','audio','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('advanced_settings','console_controls','audio','summary','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    if (isJellyfinServer(server_brand)):

        cfgChecker.checkBoolean('advanced_settings','console_controls','audiobook','delete','show',value=None,instanceType=cfgChecker.bool,errOut=True)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','delete','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','delete','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','keep','show',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','keep','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','keep','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkBoolean('advanced_settings','console_controls','audiobook','post_processing','show',value=None,instanceType=cfgChecker.bool,errOut=True)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','post_processing','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','post_processing','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkBoolean('advanced_settings','console_controls','audiobook','summary','show',value=None,instanceType=cfgChecker.bool,errOut=True)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

        cfgChecker.checkString('advanced_settings','console_controls','audiobook','summary','formatting','background','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','UPDATE_CONFIG',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkBoolean('advanced_settings','REMOVE_FILES',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    cfgChecker.checkString('admin_settings','behavior','list',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['whitelist','blacklist'])

    cfgChecker.checkString('admin_settings','behavior','matching',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['byid','bypath','bynetworkpath'])

    cfgChecker.checkBoolean('admin_settings','behavior','users','monitor_disabled',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','users')) == None)):
        
        error_found_in_mumc_config_yaml+=cfgChecker.cfgCheckYAML_forLibraries(check, user_ids_check_list, user_names_check_list, 'admin_settings > users')
        if (not (len(check) == len(user_ids_check_list))):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > users Number of configured users does not match the expected value\n'

#######################################################################################################

    cfgChecker.checkBoolean('admin_settings','media_managers','radarr','enabled',value=None,instanceType=cfgChecker.bool,errOut=True)

    cfgChecker.checkString('admin_settings','media_managers','radarr','url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkInteger('admin_settings','media_managers','radarr','port',value=None,instanceType=cfgChecker.int,minValue=1,maxValue=65535,errOut=False,comparisonValues=None)

    cfgChecker.checkString('admin_settings','media_managers','radarr','base_url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkAlphaNumeric('admin_settings','media_managers','radarr','api_key',value=None,instanceType=cfgChecker.alnum,minLength=1,maxLength=32,errOut=True,comparisonValues=None)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','media_managers','sonarr','enabled')) == None)):
        if (
            not (isinstance(check,bool) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > media_managers > sonarr > enabled must be a boolean\n\tValid values True or False\n'

    cfgChecker.checkString('admin_settings','media_managers','sonarr','url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkInteger('admin_settings','media_managers','sonarr','port',value=None,instanceType=cfgChecker.int,minValue=1,maxValue=65535,errOut=False,comparisonValues=None)

    cfgChecker.checkString('admin_settings','media_managers','sonarr','base_url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('admin_settings','media_managers','sonarr','api_key',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','media_managers','lidarr','enabled')) == None)):
        if (
            not (isinstance(check,bool) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > media_managers > lidarr > enabled must be a boolean\n\tValid values True or False\n'

    cfgChecker.checkString('admin_settings','media_managers','lidarr','url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkInteger('admin_settings','media_managers','lidarr','port',value=None,instanceType=cfgChecker.int,minValue=1,maxValue=65535,errOut=False,comparisonValues=None)

    cfgChecker.checkString('admin_settings','media_managers','lidarr','base_url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)
    
    cfgChecker.checkString('admin_settings','media_managers','lidarr','api_key',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

    if (not ((check:=keys_exist_return_value(cfg,'admin_settings','media_managers','readarr','enabled')) == None)):
        if (
            not (isinstance(check,bool) and
                (check == True) or (check == False))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: admin_settings > media_managers > readarr > enabled must be a boolean\n\tValid values True or False\n'

    cfgChecker.checkString('admin_settings','media_managers','readarr','url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkInteger('admin_settings','media_managers','readarr','port',value=None,instanceType=cfgChecker.int,minValue=1,maxValue=65535,errOut=False,comparisonValues=None)

    cfgChecker.checkString('admin_settings','media_managers','readarr','base_url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkString('admin_settings','media_managers','readarr','api_key',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

    cfgChecker.checkInteger('admin_settings','api_controls','attempts',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=16,errOut=False,comparisonValues=None)

    cfgChecker.checkInteger('admin_settings','api_controls','attempts',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=10000,errOut=False,comparisonValues=None)

#######################################################################################################

    cfgChecker.checkInteger('admin_settings','cache','size',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=10000,errOut=False,comparisonValues=None)

    cfgChecker.checkString('admin_settings','cache','fallback_behavior',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

    cfgChecker.checkInteger('admin_settings','cache','minimum_age',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=60000,errOut=False,comparisonValues=None)

#######################################################################################################

    cfgChecker.checkInteger('admin_settings','output_controls','character_limit','print',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

    cfgChecker.checkInteger('admin_settings','output_controls','character_limit','write',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

#######################################################################################################

    cfgChecker.checkInteger('admin_settings','output_controls','character_limit','write',value=None,instanceType=cfgChecker.int,minValue=None,maxValue=None,errOut=False,comparisonValues=[0,1,2,3,4,255])

#######################################################################################################

#Check for overlapping tags between blacklists and whitelists

    #check global blacktags and global whitetags do not have a common string
    if (overlapping_tags_set:=global_blacktag_set.intersection(global_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check media specific blacktags and media specific whitetags do not have a common string
    if (overlapping_tags_set:=movie_blacktag_set.intersection(movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > movie > blacktagged > tags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=episode_blacktag_set.intersection(episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > episode > blacktagged > tags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=audio_blacktag_set.intersection(audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audio > blacktagged > tags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=audiobook_blacktag_set.intersection(audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audiobook > blacktagged > tags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check media specific filter blacktags and media specific filter whitetags do not have a common string
    if (overlapping_tags_set:=filter_movie_blacktag_set.intersection(filter_movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > movie > blacktagged > tags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=filter_episode_blacktag_set.intersection(filter_episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > episode > blacktagged > tags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=filter_audio_blacktag_set.intersection(filter_audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audio > blacktagged > tags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=filter_audiobook_blacktag_set.intersection(filter_audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audiobook > blacktagged > tags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check global blacktags and media specific whitetags do not have a common string
    if (overlapping_tags_set:=global_blacktag_set.intersection(movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_blacktag_set.intersection(episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_blacktag_set.intersection(audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=global_blacktag_set.intersection(audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

    #check global whitetags and media specific blacktags do not have a common string
    if (overlapping_tags_set:=global_whitetag_set.intersection(movie_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > movie > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_whitetag_set.intersection(episode_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > episode > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_whitetag_set.intersection(audio_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audio > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=global_whitetag_set.intersection(audiobook_blacktag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audiobook > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check global blacktags and media specific filter whitetags do not have a common string
    if (overlapping_tags_set:=global_blacktag_set.intersection(filter_movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_blacktag_set.intersection(filter_episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_blacktag_set.intersection(filter_audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=global_blacktag_set.intersection(filter_audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > blacktags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

    #check global whitetags and media specific filter blacktags do not have a common string
    if (overlapping_tags_set:=global_whitetag_set.intersection(filter_movie_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > movie > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_whitetag_set.intersection(filter_episode_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > episode > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=global_whitetag_set.intersection(filter_audio_blacktag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audio > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=global_whitetag_set.intersection(filter_audiobook_blacktag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > whitetags and advanced_settings > behavioral_statements > audiobook > blacktagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #check media specific blacktags and media specific filter whitetags do not have a common string
    if (overlapping_tags_set:=movie_blacktag_set.intersection(filter_movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > movie > blacktagged > tags and basic_settings > filter_tags > movie > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=episode_blacktag_set.intersection(filter_episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > episode > blacktagged > tags and basic_settings > filter_tags > episode > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=audio_blacktag_set.intersection(filter_audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audio > blacktagged > tags and basic_settings > filter_tags > audio > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=audiobook_blacktag_set.intersection(filter_audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both advanced_settings > behavioral_statements > audiobook > blacktagged > tags and basic_settings > filter_tags > audiobook > whitetags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

    #check media specific filter blacktags and media specific whitetags do not have a common string
    if (overlapping_tags_set:=filter_movie_blacktag_set.intersection(movie_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both basic_settings > filter_tags > movie > blacktags and advanced_settings > behavioral_statements > movie > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=filter_episode_blacktag_set.intersection(episode_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both basic_settings > filter_tags > episode > blacktags and advanced_settings > behavioral_statements > episode > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (overlapping_tags_set:=filter_audio_blacktag_set.intersection(audio_whitetag_set)):
        error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both basic_settings > filter_tags > audio > blacktags and advanced_settings > behavioral_statements > audio > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'
    if (isJellyfinServer(server_brand)):
        if (overlapping_tags_set:=filter_audiobook_blacktag_set.intersection(audiobook_whitetag_set)):
            error_found_in_mumc_config_yaml+='ConfigValueError: The same tag cannot be used for both basic_settings > filter_tags > audiobook > blacktags and advanced_settings > behavioral_statements > audiobook > whitetagged > tags\n\tTo proceed the following tags need to be fixed: ' +  str(list(overlapping_tags_set))  + '\n'

#######################################################################################################

    #Bring all errors found to users attention
    if (not (error_found_in_mumc_config_yaml == '')):
        if (init_dict['DEBUG']):
            appendTo_DEBUG_log("\n" + error_found_in_mumc_config_yaml,2,init_dict)
        print('\n' + error_found_in_mumc_config_yaml)
        sys.exit(0)

#######################################################################################################
    return cfg,init_dict


#admin_settings and server have to be checked early
def pre_cfgCheckYAML(cfg):
    error_found_in_mumc_config_yaml=''
    try:
        cfg['admin_settings']=cfg['admin_settings']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']=cfg['admin_settings']['server']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']['brand']=cfg['admin_settings']['server']['brand']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > brand is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']['url']=cfg['admin_settings']['server']['url']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > url is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']['auth_key']=cfg['admin_settings']['server']['auth_key']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > auth_key is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['server']['admin_id']=cfg['admin_settings']['server']['admin_id']
    except:
        pass
        #error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > admin_id is missing from the mumc_config.yaml\n'
    try:
        cfg['admin_settings']['users']=cfg['admin_settings']['users']
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > users is missing from the mumc_config.yaml\n'

    #Bring all errors found to users attention
    if (not (error_found_in_mumc_config_yaml == '')):
        print('\n' + error_found_in_mumc_config_yaml)
        sys.exit(0)