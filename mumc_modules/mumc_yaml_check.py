import sys
from mumc_modules.mumc_versions import get_semantic_version_parts,checkYAMLVersion,get_script_version
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_compare_items import keys_exist_return_value
from mumc_modules.mumc_tagged import get_isFilterStatementTag
from mumc_modules.mumc_data_checks import data_checker


#Check select config variables are as expected
def cfgCheckYAML(cfg,init_dict):
#######################################################################################################

    cfgChecker=data_checker(cfg,init_dict)

#######################################################################################################

    errorFlag=True
    if (not ((version:=cfgChecker.checkString('version',value=None,instanceType=cfgChecker.str,required=True,minLength=5,maxLength=None,errOut=False,comparisonValues=None)) == None)):
        version_parts=get_semantic_version_parts(version)
        if (not (cfgChecker.checkInteger(*(),value=version_parts['major'],instanceType=cfgChecker.int,minValue=0,maxValue=None,errOut=False,comparisonValues=None) == None)):
            if (not (cfgChecker.checkInteger(*(),value=version_parts['minor'],instanceType=cfgChecker.int,minValue=0,maxValue=None,errOut=False,comparisonValues=None) == None)):
                if (not (cfgChecker.checkInteger(*(),value=version_parts['patch'],instanceType=cfgChecker.int,minValue=0,maxValue=None,errOut=False,comparisonValues=None) == None)):
                    if (not (cfgChecker.checkString(*(),value=version_parts['release'],instanceType=cfgChecker.str,minLength=5,maxLength=None,errOut=False,comparisonValues=['alpha','beta','stable']) == None)):
                        errorFlag=False
    if (errorFlag):
        cfgChecker.setCustomErrorText('ConfigValueError: version must be in the semantic versioning syntax\n\tFormatted as shown: MAJOR#.MINOR#.PATCH# (e.g. ' + str(get_script_version()) +')')

    errorFlag=True
    if (checkYAMLVersion(cfg,init_dict)):
        errorFlag=False

    if (errorFlag):
        cfgChecker.setCustomErrorText('ConfigValueError: ' + str(init_dict['mumc_path_config_dir']) + '/' + str(init_dict['config_file_name_yaml']) + ' v' + str(init_dict['version']) + ' is not compatible with MUMC v' + str(get_script_version()) + '\n\tMinimum allowed version is ' + str(init_dict['min_config_version']) + '\n\tMaximum allowed version is ' + str(init_dict['max_config_version']))

#######################################################################################################

    debug=cfgChecker.checkInteger('DEBUG',value=None,instanceType=cfgChecker.int,required=True,minValue=None,maxValue=None,errOut=True,comparisonValues=[0,1,2,3,4,255])

#######################################################################################################

    if (not ((admin_settings:=cfgChecker.checkDict('admin_settings',value=None,instanceType=cfgChecker.dict,required=True,minLength=2,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

        if (not ((server:=cfgChecker.checkDict('admin_settings','server',value=None,instanceType=cfgChecker.dict,required=True,minLength=3,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            brand=None
            if ((brand:=cfgChecker.checkString('admin_settings','server','brand',value=None,instanceType=cfgChecker.str,required=True,minLength=None,maxLength=None,errOut=False,comparisonValues=['emby','jellyfin'])) == None):
                cfgChecker.setCustomErrorText('ConfigValueError: admin_settings > server > brand must be a string or is missing\n\tValid values are emby, jellyfin\n')
            else:
                cfgChecker.brand=brand

            url=cfgChecker.checkString('admin_settings','server','url',value=None,instanceType=cfgChecker.str,required=True,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

            auth_key=cfgChecker.checkString('admin_settings','server','auth_key',value=None,instanceType=cfgChecker.str,required=True,minLength=32,maxLength=32,errOut=True,comparisonValues=None)

            admin_id=cfgChecker.checkAlphaNumeric('admin_settings','server','admin_id',value=None,instanceType=cfgChecker.alnum,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

        if (not ((behavior:=cfgChecker.checkDict('admin_settings','behavior',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            behaviorList=cfgChecker.checkString('admin_settings','behavior','list',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['whitelist','blacklist'])

            matching=cfgChecker.checkString('admin_settings','behavior','matching',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['byid','bypath','bynetworkpath'])

#######################################################################################################

            if (not ((users:=cfgChecker.checkDict('admin_settings','behavior','users',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                monitor_disabled=cfgChecker.checkBoolean('admin_settings','behavior','users','monitor_disabled',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    #define userId and username lists to be used later
    user_ids_check_list=[]
    user_names_check_list=[]

#######################################################################################################

    if (not ((usersList:=cfgChecker.checkList('admin_settings','users',value=None,instanceType=cfgChecker.list,required=True,minLength=1,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################
  
        for userInfo in usersList:
            if (not ((userInfo:=cfgChecker.checkDict('admin_settings','users',usersList.index(userInfo),value=None,instanceType=cfgChecker.dict,required=True,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((user_id:=cfgChecker.checkAlphaNumeric('admin_settings','users',usersList.index(userInfo),'user_id',value=None,instanceType=cfgChecker.alnum,required=True,minLength=1,maxLength=32,errOut=True,comparisonValues=None)) == None)):
                    user_ids_check_list.append(user_id)

                if (not ((user_name:=cfgChecker.checkString('admin_settings','users',usersList.index(userInfo),'user_name',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                    user_names_check_list.append(user_name)

                if (not ((whitelistList:=cfgChecker.checkList('admin_settings','users',usersList.index(userInfo),'whitelist',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

                    for userWhitelistListInfo in whitelistList:
                        if (not ((userWhitelistListInfo:=cfgChecker.checkDict('admin_settings','users',usersList.index(userInfo),'whitelist',whitelistList.index(userWhitelistListInfo),value=None,instanceType=cfgChecker.dict,required=True,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            lib_id=cfgChecker.checkAlphaNumeric('admin_settings','users',usersList.index(userInfo),'whitelist',whitelistList.index(userWhitelistListInfo),'lib_id',value=None,instanceType=cfgChecker.alnum,minLength=1,maxLength=32,errOut=True,comparisonValues=None)

                            collection_type=cfgChecker.checkString('admin_settings','users',usersList.index(userInfo),'whitelist',whitelistList.index(userWhitelistListInfo),'collection_type',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=None,errOut=True,comparisonValues=['movies','tvshows','music','audiobooks'])

                            path=cfgChecker.checkString('admin_settings','users',usersList.index(userInfo),'whitelist',whitelistList.index(userWhitelistListInfo),'path',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=None,errOut=True,comparisonValues=None)

                            network_path=cfgChecker.checkString('admin_settings','users',usersList.index(userInfo),'whitelist',whitelistList.index(userWhitelistListInfo),'network_path',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            subfolder_id=cfgChecker.checkString('admin_settings','users',usersList.index(userInfo),'whitelist',whitelistList.index(userWhitelistListInfo),'subfolder_id',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)

                            lib_enabled=cfgChecker.checkBoolean('admin_settings','users',usersList.index(userInfo),'whitelist',whitelistList.index(userWhitelistListInfo),'lib_enabled',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((blacklistList:=cfgChecker.checkList('admin_settings','users',usersList.index(userInfo),'blacklist',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

                    for userBlacklistListInfo in blacklistList:
                        if (not ((userBlacklistListInfo:=cfgChecker.checkDict('admin_settings','users',usersList.index(userInfo),'blacklist',blacklistList.index(userBlacklistListInfo),value=None,instanceType=cfgChecker.dict,required=True,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            lib_id=cfgChecker.checkAlphaNumeric('admin_settings','users',usersList.index(userInfo),'blacklist',blacklistList.index(userBlacklistListInfo),'lib_id',value=None,instanceType=cfgChecker.alnum,minLength=1,maxLength=32,errOut=True,comparisonValues=None)

                            collection_type=cfgChecker.checkString('admin_settings','users',usersList.index(userInfo),'blacklist',blacklistList.index(userBlacklistListInfo),'collection_type',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=['movies','tvshows','music','audiobooks'])

                            path=cfgChecker.checkString('admin_settings','users',usersList.index(userInfo),'blacklist',blacklistList.index(userBlacklistListInfo),'path',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)

                            network_path=cfgChecker.checkString('admin_settings','users',usersList.index(userInfo),'blacklist',blacklistList.index(userBlacklistListInfo),'network_path',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            subfolder_id=cfgChecker.checkString('admin_settings','users',usersList.index(userInfo),'blacklist',blacklistList.index(userBlacklistListInfo),'subfolder_id',value=None,instanceType=cfgChecker.str,minLength=1,maxLength=None,errOut=True,comparisonValues=None)

                            lib_enabled=cfgChecker.checkBoolean('admin_settings','users',usersList.index(userInfo),'blacklist',blacklistList.index(userBlacklistListInfo),'lib_enabled',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (not ((media_managers:=cfgChecker.checkDict('admin_settings','media_managers',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((radarr:=cfgChecker.checkDict('admin_settings','media_managers','radarr',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                radarr_enabled=cfgChecker.checkBoolean('admin_settings','media_managers','radarr','enabled',value=None,instanceType=cfgChecker.bool,errOut=True)

                radarr_url=cfgChecker.checkString('admin_settings','media_managers','radarr','url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                radarr_api_key=cfgChecker.checkAlphaNumeric('admin_settings','media_managers','radarr','api_key',value=None,instanceType=cfgChecker.alnum,minLength=1,maxLength=32,errOut=True,comparisonValues=None)

#######################################################################################################

            if (not ((sonarr:=cfgChecker.checkDict('admin_settings','media_managers','sonarr',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                sonarr_enabled=cfgChecker.checkBoolean('admin_settings','media_managers','sonarr','enabled',value=None,instanceType=cfgChecker.bool,errOut=True)

                sonarr_url=cfgChecker.checkString('admin_settings','media_managers','sonarr','url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                sonarr_api_key=cfgChecker.checkString('admin_settings','media_managers','sonarr','api_key',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

            if (not ((lidarr:=cfgChecker.checkDict('admin_settings','media_managers','lidarr',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                lidarr_enabled=cfgChecker.checkBoolean('admin_settings','media_managers','lidarr','enabled',value=None,instanceType=cfgChecker.bool,errOut=True)

                lidarr_url=cfgChecker.checkString('admin_settings','media_managers','lidarr','url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                lidarr_api_key=cfgChecker.checkString('admin_settings','media_managers','lidarr','api_key',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

            if (not ((readarr:=cfgChecker.checkDict('admin_settings','media_managers','readarr',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                readarr_enabled=cfgChecker.checkBoolean('admin_settings','media_managers','readarr','enabled',value=None,instanceType=cfgChecker.bool,errOut=True)

                readarr_url=cfgChecker.checkString('admin_settings','media_managers','readarr','url',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                readarr_api_key=cfgChecker.checkString('admin_settings','media_managers','readarr','api_key',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

        if (not ((api_controls:=cfgChecker.checkDict('admin_settings','api_controls',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            attempts=cfgChecker.checkInteger('admin_settings','api_controls','attempts',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=16,errOut=False,comparisonValues=None)

            item_limit=cfgChecker.checkInteger('admin_settings','api_controls','item_limit',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=10000,errOut=False,comparisonValues=None)

#######################################################################################################

        if (not ((cache:=cfgChecker.checkDict('admin_settings','cache',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            size=cfgChecker.checkInteger('admin_settings','cache','size',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=10000,errOut=False,comparisonValues=None)

            fallback_behavior=cfgChecker.checkString('admin_settings','cache','fallback_behavior',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['fifo','lfu','lru'])

            minimum_age=cfgChecker.checkInteger('admin_settings','cache','minimum_age',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=600000,errOut=False,comparisonValues=None)

#######################################################################################################

        if (not ((output_controls:=cfgChecker.checkDict('admin_settings','output_controls',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((character_limit:=cfgChecker.checkDict('admin_settings','output_controls','character_limit',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                print=cfgChecker.checkInteger('admin_settings','output_controls','character_limit','print',value=None,instanceType=cfgChecker.int,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

#######################################################################################################

    if (not ((basic_settings:=cfgChecker.checkDict('basic_settings',value=None,instanceType=cfgChecker.dict,required=True,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

        if (not ((filter_statements:=cfgChecker.checkDict('basic_settings','filter_statements',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((movie:=cfgChecker.checkDict('basic_settings','filter_statements','movie',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((played:=cfgChecker.checkDict('basic_settings','filter_statements','movie','played',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    condition_days=cfgChecker.checkInteger('basic_settings','filter_staements','movie','played','condition_days',value=None,instanceType=cfgChecker.int,required=True,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

                    count_equality=cfgChecker.checkString('basic_settings','filter_statements','movie','played','count_equality',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])

                    count=cfgChecker.checkInteger('basic_settings','filter_statements','movie','played','count',value=None,instanceType=cfgChecker.int,required=True,minValue=1,maxValue=730500,errOut=False,comparisonValues=None)

#######################################################################################################

                if (not ((created:=cfgChecker.checkDict('basic_settings','filter_statements','movie','created',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    condition_days=cfgChecker.checkInteger('basic_settings','filter_statements','movie','created','condition_days',value=None,instanceType=cfgChecker.int,required=True,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

                    count_equality=cfgChecker.checkString('basic_settings','filter_statements','movie','created','count_equality',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])

                    count=cfgChecker.checkInteger('basic_settings','filter_statements','movie','created','count',value=None,instanceType=cfgChecker.int,required=True,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)

                    behavioral_control=cfgChecker.checkBoolean('basic_settings','filter_statements','movie','created','behavioral_control',value=None,instanceType=cfgChecker.bool,required=True,errOut=True)

#######################################################################################################

            if (not ((episode:=cfgChecker.checkDict('basic_settings','filter_statements','episode',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((played:=cfgChecker.checkDict('basic_settings','filter_statements','episode','played',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    condition_days=cfgChecker.checkInteger('basic_settings','filter_staements','episode','played','condition_days',value=None,instanceType=cfgChecker.int,required=True,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

                    count_equality=cfgChecker.checkString('basic_settings','filter_statements','episode','played','count_equality',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])

                    count=cfgChecker.checkInteger('basic_settings','filter_statements','episode','played','count',value=None,instanceType=cfgChecker.int,required=True,minValue=1,maxValue=730500,errOut=False,comparisonValues=None)

#######################################################################################################

                if (not ((created:=cfgChecker.checkDict('basic_settings','filter_statements','episode','created',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    condition_days=cfgChecker.checkInteger('basic_settings','filter_statements','episode','created','condition_days',value=None,instanceType=cfgChecker.int,required=True,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

                    count_equality=cfgChecker.checkString('basic_settings','filter_statements','episode','created','count_equality',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])

                    count=cfgChecker.checkInteger('basic_settings','filter_statements','episode','created','count',value=None,instanceType=cfgChecker.int,required=True,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)

                    behavioral_control=cfgChecker.checkBoolean('basic_settings','filter_statements','episode','created','behavioral_control',value=None,instanceType=cfgChecker.bool,required=True,errOut=True)

#######################################################################################################

            if (not ((audio:=cfgChecker.checkDict('basic_settings','filter_statements','audio',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((played:=cfgChecker.checkDict('basic_settings','filter_statements','audio','played',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    condition_days=cfgChecker.checkInteger('basic_settings','filter_staements','audio','played','condition_days',value=None,instanceType=cfgChecker.int,required=True,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

                    count_equality=cfgChecker.checkString('basic_settings','filter_statements','audio','played','count_equality',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])

                    count=cfgChecker.checkInteger('basic_settings','filter_statements','audio','played','count',value=None,instanceType=cfgChecker.int,required=True,minValue=1,maxValue=730500,errOut=False,comparisonValues=None)

#######################################################################################################

                if (not ((created:=cfgChecker.checkDict('basic_settings','filter_statements','audio','created',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    condition_days=cfgChecker.checkInteger('basic_settings','filter_statements','audio','created','condition_days',value=None,instanceType=cfgChecker.int,required=True,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

                    count_equality=cfgChecker.checkString('basic_settings','filter_statements','audio','created','count_equality',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])

                    count=cfgChecker.checkInteger('basic_settings','filter_statements','audio','created','count',value=None,instanceType=cfgChecker.int,required=True,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)

                    behavioral_control=cfgChecker.checkBoolean('basic_settings','filter_statements','audio','created','behavioral_control',value=None,instanceType=cfgChecker.bool,required=True,errOut=True)

#######################################################################################################

            if (isJellyfinServer(brand)):

                if (not ((audiobook:=cfgChecker.checkDict('basic_settings','filter_statements','audiobook',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    if (not ((played:=cfgChecker.checkDict('basic_settings','filter_statements','audiobook','played',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        condition_days=cfgChecker.checkInteger('basic_settings','filter_staements','audiobook','played','condition_days',value=None,instanceType=cfgChecker.int,required=True,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

                        count_equality=cfgChecker.checkString('basic_settings','filter_statements','audiobook','played','count_equality',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])

                        count=cfgChecker.checkInteger('basic_settings','filter_statements','audiobook','played','count',value=None,instanceType=cfgChecker.int,required=True,minValue=1,maxValue=730500,errOut=False,comparisonValues=None)

#######################################################################################################

                    if (not ((created:=cfgChecker.checkDict('basic_settings','filter_statements','audiobook','created',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        condition_days=cfgChecker.checkInteger('basic_settings','filter_statements','audiobook','created','condition_days',value=None,instanceType=cfgChecker.int,required=True,minValue=-1,maxValue=730500,errOut=False,comparisonValues=None)

                        count_equality=cfgChecker.checkString('basic_settings','filter_statements','audiobook','created','count_equality',value=None,instanceType=cfgChecker.str,required=True,minLength=1,maxLength=6,errOut=True,comparisonValues=['>','<','>=','<=','=','not ==','not >','not <','not >=','not <='])

                        count=cfgChecker.checkInteger('basic_settings','filter_statements','audiobook','created','count',value=None,instanceType=cfgChecker.int,required=True,minValue=0,maxValue=730500,errOut=False,comparisonValues=None)

                        behavioral_control=cfgChecker.checkBoolean('basic_settings','filter_statements','audiobook','created','behavioral_control',value=None,instanceType=cfgChecker.bool,required=True,errOut=True)

#######################################################################################################

        #sets of filter tags for user later
        filter_movie_whitetag_set=set()
        filter_movie_blacktag_set=set()
        filter_episode_whitetag_set=set()
        filter_episode_blacktag_set=set()
        filter_audio_whitetag_set=set()
        filter_audio_blacktag_set=set()
        filter_audiobook_whitetag_set=set()
        filter_audiobook_blacktag_set=set()

#######################################################################################################

        if (not ((filter_tags:=cfgChecker.checkDict('basic_settings','filter_tags',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((movie:=cfgChecker.checkDict('basic_settings','filter_tags','movie',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((filtertagsMovieWhitetagsList:=cfgChecker.checkList('basic_settings','filter_tags','movie','whitetags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                    filter_movie_whitetag_set.update(filtertagsMovieWhitetagsList)

#######################################################################################################

                    for filtertagMovie in filtertagsMovieWhitetagsList:
                        if (not ((filtertagMovie:=cfgChecker.checkString('basic_settings','filter_tags','movie','whitetags',filtertagsMovieWhitetagsList.index(filtertagMovie),value=None,instanceType=cfgChecker.str,minLength=12,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                            if (not get_isFilterStatementTag(filtertagMovie)):
                                cfgChecker.setCustomErrorText('ConfigValueError: basic_settings > filter_tags > movie > whitetags: ' + filtertagMovie + ' must be a string\n\tfilter_tags must follow the pre-defined format and values as explained in the MUMC Wiki\n')

#######################################################################################################

                if (not ((filtertagsMovieBlacktagsList:=cfgChecker.checkList('basic_settings','filter_tags','movie','blacktags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                    filter_movie_blacktag_set.update(filtertagsMovieBlacktagsList)

#######################################################################################################

                    for filtertagMovie in filtertagsMovieBlacktagsList:
                        if (not ((filtertagMovie:=cfgChecker.checkString('basic_settings','filter_tags','movie','blacktags',filtertagsMovieBlacktagsList.index(filtertagMovie),value=None,instanceType=cfgChecker.str,minLength=12,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                            if (not get_isFilterStatementTag(filtertagMovie)):
                                cfgChecker.setCustomErrorText('ConfigValueError: basic_settings > filter_tags > movie > blacktags: ' + filtertagMovie + ' must be a string\n\tfilter_tags must follow the pre-defined format and values as explained in the MUMC Wiki\n')

#######################################################################################################

            if (not ((episode:=cfgChecker.checkDict('basic_settings','filter_tags','episode',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((filtertagsEpisodeWhitetagsList:=cfgChecker.checkList('basic_settings','filter_tags','episode','whitetags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                    filter_episode_whitetag_set.update(filtertagsEpisodeWhitetagsList)

#######################################################################################################

                    for filtertagEpisode in filtertagsEpisodeWhitetagsList:
                        if (not ((filtertagEpisode:=cfgChecker.checkString('basic_settings','filter_tags','episode','whitetags',filtertagsEpisodeWhitetagsList.index(filtertagEpisode),value=None,instanceType=cfgChecker.str,minLength=12,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                            if (not get_isFilterStatementTag(filtertagEpisode)):
                                cfgChecker.setCustomErrorText('ConfigValueError: basic_settings > filter_tags > episode > whitetags: ' + filtertagMovie + ' must be a string\n\tfilter_tags must follow the pre-defined format and values as explained in the MUMC Wiki\n')

#######################################################################################################

                if (not ((filtertagsEpisodeBlacktagsList:=cfgChecker.checkList('basic_settings','filter_tags','episode','blacktags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                    filter_episode_blacktag_set.update(filtertagsEpisodeBlacktagsList)

#######################################################################################################

                    for filtertagEpisode in filtertagsEpisodeBlacktagsList:
                        if (not ((filtertagEpisode:=cfgChecker.checkString('basic_settings','filter_tags','episode','blacktags',filtertagsEpisodeBlacktagsList.index(filtertagEpisode),value=None,instanceType=cfgChecker.str,minLength=12,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                            if (not get_isFilterStatementTag(filtertagEpisode)):
                                cfgChecker.setCustomErrorText('ConfigValueError: basic_settings > filter_tags > episode > blacktags: ' + filtertagMovie + ' must be a string\n\tfilter_tags must follow the pre-defined format and values as explained in the MUMC Wiki\n')

#######################################################################################################

            if (not ((audio:=cfgChecker.checkDict('basic_settings','filter_tags','audio',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((filtertagsAudioWhitetagsList:=cfgChecker.checkList('basic_settings','filter_tags','audio','whitetags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                    filter_audio_whitetag_set.update(filtertagsAudioWhitetagsList)

#######################################################################################################

                    for filtertagAudio in filtertagsAudioWhitetagsList:
                        if (not ((filtertagAudio:=cfgChecker.checkString('basic_settings','filter_tags','audio','whitetags',filtertagsAudioWhitetagsList.index(filtertagAudio),value=None,instanceType=cfgChecker.str,minLength=12,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                            if (not get_isFilterStatementTag(filtertagAudio)):
                                cfgChecker.setCustomErrorText('ConfigValueError: basic_settings > filter_tags > audio > whitetags: ' + filtertagMovie + ' must be a string\n\tfilter_tags must follow the pre-defined format and values as explained in the MUMC Wiki\n')

#######################################################################################################

                if (not ((filtertagsAudioBlacktagsList:=cfgChecker.checkList('basic_settings','filter_tags','audio','blacktags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                    filter_audio_blacktag_set.update(filtertagsAudioBlacktagsList)

#######################################################################################################

                    for filtertagAudio in filtertagsAudioBlacktagsList:
                        if (not ((filtertagAudio:=cfgChecker.checkString('basic_settings','filter_tags','audio','blacktags',filtertagsAudioBlacktagsList.index(filtertagAudio),value=None,instanceType=cfgChecker.str,minLength=12,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                            if (not get_isFilterStatementTag(filtertagAudio)):
                                cfgChecker.setCustomErrorText('ConfigValueError: basic_settings > filter_tags > audio > blacktags: ' + filtertagMovie + ' must be a string\n\tfilter_tags must follow the pre-defined format and values as explained in the MUMC Wiki\n')

#######################################################################################################

            if (isJellyfinServer(brand)):
                if (not ((audiobook:=cfgChecker.checkDict('basic_settings','filter_tags','audiobook',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    if (not ((filtertagsAudiobookWhitetagsList:=cfgChecker.checkList('basic_settings','filter_tags','audiobook','whitetags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                        filter_audiobook_whitetag_set.update(filtertagsAudiobookWhitetagsList)

#######################################################################################################

                        for filtertagAudiobook in filtertagsAudiobookWhitetagsList:
                            if (not ((filtertagAudiobook:=cfgChecker.checkString('basic_settings','filter_tags','audiobook','whitetags',filtertagsAudiobookWhitetagsList.index(filtertagAudiobook),value=None,instanceType=cfgChecker.str,minLength=12,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                                if (not get_isFilterStatementTag(filtertagAudiobook)):
                                    cfgChecker.setCustomErrorText('ConfigValueError: basic_settings > filter_tags > audiobook > whitetags: ' + filtertagMovie + ' must be a string\n\tfilter_tags must follow the pre-defined format and values as explained in the MUMC Wiki\n')

#######################################################################################################

                    if (not ((filtertagsAudiobookBlacktagsList:=cfgChecker.checkList('basic_settings','filter_tags','audiobook','blacktags',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):
                        filter_audiobook_blacktag_set.update(filtertagsAudiobookBlacktagsList)

#######################################################################################################

                        for filtertagAudiobook in filtertagsAudiobookBlacktagsList:
                            if (not ((filtertagAudiobook:=cfgChecker.checkString('basic_settings','filter_tags','audiobook','blacktags',filtertagsAudiobookBlacktagsList.index(filtertagAudiobook),value=None,instanceType=cfgChecker.str,minLength=12,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                                if (not get_isFilterStatementTag(filtertagAudiobook)):
                                    cfgChecker.setCustomErrorText('ConfigValueError: basic_settings > filter_tags > audiobook > blacktags: ' + filtertagMovie + ' must be a string\n\tfilter_tags must follow the pre-defined format and values as explained in the MUMC Wiki\n')

#######################################################################################################

    if (not ((advanced_settings:=cfgChecker.checkDict('advanced_settings',value=None,instanceType=cfgChecker.dict,required=True,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

        if (not ((filter_statements:=cfgChecker.checkDict('advanced_settings','filter_statements',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((movie:=cfgChecker.checkDict('advanced_settings','filter_statements','movie',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((query_filter:=cfgChecker.checkDict('advanced_settings','filter_statements','movie','query_filter',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    if (not ((whitelisted:=cfgChecker.checkDict('advanced_settings','filter_statements','movie','query_filter','whitelisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        favorited=cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','whitelisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)

                        whitetagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','whitelisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        blacktagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','whitelisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        played=cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','whitelisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((blacklisted:=cfgChecker.checkDict('advanced_settings','filter_statements','movie','query_filter','blacklisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        favorited=cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','blacklisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)

                        whitetagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','blacklisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        blacktagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','blacklisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        played=cfgChecker.checkBoolean('advanced_settings','filter_statements','movie','query_filter','blacklisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

            if (not ((episode:=cfgChecker.checkDict('advanced_settings','filter_statements','episode',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((query_filter:=cfgChecker.checkDict('advanced_settings','filter_statements','episode','query_filter',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    if (not ((whitelisted:=cfgChecker.checkDict('advanced_settings','filter_statements','episode','query_filter','whitelisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        favorited=cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','whitelisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)

                        whitetagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','whitelisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        blacktagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','whitelisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        played=cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','whitelisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((blacklisted:=cfgChecker.checkDict('advanced_settings','filter_statements','episode','query_filter','blacklisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        favorited=cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','blacklisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)

                        whitetagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','blacklisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        blacktagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','blacklisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        played=cfgChecker.checkBoolean('advanced_settings','filter_statements','episode','query_filter','blacklisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

            if (not ((audio:=cfgChecker.checkDict('advanced_settings','filter_statements','audio',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((query_filter:=cfgChecker.checkDict('advanced_settings','filter_statements','audio','query_filter',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    if (not ((whitelisted:=cfgChecker.checkDict('advanced_settings','filter_statements','audio','query_filter','whitelisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        favorited=cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','whitelisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)

                        whitetagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','whitelisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        blacktagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','whitelisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        played=cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','whitelisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((blacklisted:=cfgChecker.checkDict('advanced_settings','filter_statements','audio','query_filter','blacklisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        favorited=cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','blacklisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)

                        whitetagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','blacklisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        blacktagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','blacklisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                        played=cfgChecker.checkBoolean('advanced_settings','filter_statements','audio','query_filter','blacklisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

            if (isJellyfinServer(brand)):
                if (not ((audiobook:=cfgChecker.checkDict('advanced_settings','filter_statements','audiobook',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    if (not ((query_filter:=cfgChecker.checkDict('advanced_settings','filter_statements','audiobook','query_filter',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((whitelisted:=cfgChecker.checkDict('advanced_settings','filter_statements','audiobook','query_filter','whitelisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            favorited=cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','whitelisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)

                            whitetagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','whitelisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                            blacktagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','whitelisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                            played=cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','whitelisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                        if (not ((blacklisted:=cfgChecker.checkDict('advanced_settings','filter_statements','audiobook','query_filter','blacklisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            favorited=cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','blacklisted','favorited',value=None,instanceType=cfgChecker.bool,errOut=True)

                            whitetagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','blacklisted','whitetagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                            blacktagged=cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','blacklisted','blacktagged',value=None,instanceType=cfgChecker.bool,errOut=True)

                            played=cfgChecker.checkBoolean('advanced_settings','filter_statements','audiobook','query_filter','blacklisted','played',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (not ((behavioral_statements:=cfgChecker.checkDict('advanced_settings','behavioral_statements',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((movie:=cfgChecker.checkDict('advanced_settings','behavioral_statements','movie',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((favorited:=cfgChecker.checkDict('advanced_settings','behavioral_statements','movie','favorited',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','favorited','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','favorited','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','favorited','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','favorited','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','favorited','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

                    if (not ((extra:=cfgChecker.checkDict('advanced_settings','behavioral_statements','movie','favorited','extra',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

                        genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','favorited','extra','genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        library_genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','favorited','extra','library_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

#######################################################################################################

                if (not ((whitetagged:=cfgChecker.checkDict('advanced_settings','behavioral_statements','movie','whitetagged',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitetagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitetagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitetagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','whitetagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','whitetagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((blacktagged:=cfgChecker.checkDict('advanced_settings','behavioral_statements','movie','blacktagged',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacktagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacktagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacktagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','blacktagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','blacktagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((whitelisted:=cfgChecker.checkDict('advanced_settings','behavioral_statements','movie','whitelisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitelisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitelisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','whitelisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','whitelisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','whitelisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((blacklisted:=cfgChecker.checkDict('advanced_settings','behavioral_statements','movie','blacklisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacklisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacklisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','movie','blacklisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','movie','blacklisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','movie','blacklisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

            if (not ((episode:=cfgChecker.checkDict('advanced_settings','behavioral_statements','episode',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((favorited:=cfgChecker.checkDict('advanced_settings','behavioral_statements','episode','favorited',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','favorited','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','favorited','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','favorited','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','favorited','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

                    if (not ((extra:=cfgChecker.checkDict('advanced_settings','behavioral_statements','episode','favorited','extra',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

                        genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        season_genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','season_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        series_genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','series_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        library_genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','library_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        studio_network=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','studio_network',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        studio_network_genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','favorited','extra','studio_network_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

#######################################################################################################

                if (not ((whitetagged:=cfgChecker.checkDict('advanced_settings','behavioral_statements','episode','whitetagged',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitetagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitetagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitetagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','whitetagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','whitetagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((blacktagged:=cfgChecker.checkDict('advanced_settings','behavioral_statements','episode','blacktagged',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacktagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacktagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacktagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','blacktagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','blacktagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((whitelisted:=cfgChecker.checkDict('advanced_settings','behavioral_statements','episode','whitelisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitelisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitelisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','whitelisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','whitelisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','whitelisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((blacklisted:=cfgChecker.checkDict('advanced_settings','behavioral_statements','episode','blacklisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacklisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacklisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','episode','blacklisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','episode','blacklisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','episode','blacklisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

            if (not ((audio:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audio',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((favorited:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audio','favorited',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','favorited','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','favorited','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','favorited','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','favorited','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

                    if (not ((extra:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audio','favorited','extra',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

                        genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        album_genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','album_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        library_genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','library_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        track_artist=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','track_artist',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                        album_artist=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','favorited','extra','album_artist',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

#######################################################################################################

                if (not ((whitetagged:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audio','whitetagged',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitetagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitetagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitetagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','whitetagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','whitetagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((blacktagged:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audio','blacktagged',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacktagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacktagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacktagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','blacktagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','blacktagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((whitelisted:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audio','whitelisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitelisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitelisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','whitelisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','whitelisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','whitelisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                if (not ((blacklisted:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audio','blacklisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    action=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacklisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                    user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacklisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                    played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audio','blacklisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                    action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audio','blacklisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                    dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audio','blacklisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

            if (isJellyfinServer(brand)):
                if (not ((audiobook:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audiobook',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    if (not ((favorited:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audiobook','favorited',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        action=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','favorited','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                        user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','favorited','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                        played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','favorited','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                        action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                        dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','favorited','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

                        if (not ((extra:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audiobook','favorited','extra',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

                            genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                            audiobook_genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','audiobook_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                            library_genre=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','library_genre',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                            track_artist=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','track_artist',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

                            album_artist=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','favorited','extra','album_artist',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=2,errOut=False,comparisonValues=None)

#######################################################################################################

                    if (not ((whitetagged:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audiobook','whitetagged',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        action=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitetagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                        user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitetagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                        played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitetagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                        action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','whitetagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                        dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','whitetagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((blacktagged:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audiobook','blacktagged',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        action=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacktagged','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                        user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacktagged','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                        played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacktagged','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                        action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','blacktagged','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                        dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','blacktagged','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((whitelisted:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audiobook','whitelisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        action=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitelisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                        user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitelisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                        played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','whitelisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                        action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','whitelisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                        dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','whitelisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((blacklisted:=cfgChecker.checkDict('advanced_settings','behavioral_statements','audiobook','blacklisted',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        action=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacklisted','action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['delete','keep'])

                        user_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacklisted','user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['any','all'])

                        played_conditional=cfgChecker.checkString('advanced_settings','behavioral_statements','audiobook','blacklisted','played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all','any','all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                        action_control=cfgChecker.checkInteger('advanced_settings','behavioral_statements','audiobook','blacklisted','action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                        dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_statements','audiobook','blacklisted','dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (not ((behavioral_tags:=cfgChecker.checkDict('advanced_settings','behavioral_tags',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((behavioral_tags_movie:=cfgChecker.checkDict('advanced_settings','behavioral_tags','movie',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for behavioral_tag_movie in behavioral_tags_movie:
                    if (not ((behavioral_tag_movie:=cfgChecker.checkString(*(),value=behavioral_tag_movie,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=False,comparisonValues=list(filter_movie_whitetag_set) + list(filter_movie_blacktag_set))) == None)):

#######################################################################################################

                        behavioral_tag_contents=cfgChecker.checkDict('advanced_settings','behavioral_tags','movie',behavioral_tag_movie,value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                        action=cfgChecker.checkString('advanced_settings','behavioral_tags','movie',behavioral_tag_movie,'action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['keep','delete'])

                        user_conditional=cfgChecker.checkString('advanced_settings','behavioral_tags','movie',behavioral_tag_movie,'user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                        played_conditional=cfgChecker.checkString('advanced_settings','behavioral_tags','movie',behavioral_tag_movie,'played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                        action_control=cfgChecker.checkInteger('advanced_settings','behavioral_tags','movie',behavioral_tag_movie,'action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                        dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_tags','movie',behavioral_tag_movie,'dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

                        high_priority=cfgChecker.checkBoolean('advanced_settings','behavioral_tags','movie',behavioral_tag_movie,'high_priority',value=None,instanceType=cfgChecker.bool,errOut=True)

                    else:
                        cfgChecker.setCustomErrorText('ConfigValueError: advanced_settings > behavioral_tags > movie > ' + str(behavioral_tag_movie) + ' must be a(n) string or does not match any basic_settings > filter_tags > movie > whitetags or blacktags\n\tValid value(s) are: ' + ', '.join(str(element) for element in (list(filter_movie_whitetag_set) + list(filter_movie_blacktag_set))) + '\n')

#######################################################################################################

            if (not ((behavioral_tags_episode:=cfgChecker.checkDict('advanced_settings','behavioral_tags','episode',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for behavioral_tag_episode in behavioral_tags_episode:
                    if (not ((behavioral_tag_episode:=cfgChecker.checkString(*(),value=behavioral_tag_episode,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=False,comparisonValues=list(filter_episode_whitetag_set) + list(filter_episode_blacktag_set))) == None)):

#######################################################################################################

                        behavioral_tag_contents=cfgChecker.checkDict('advanced_settings','behavioral_tags','episode',behavioral_tag_episode,value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                        action=cfgChecker.checkString('advanced_settings','behavioral_tags','episode',behavioral_tag_episode,'action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['keep','delete'])

                        user_conditional=cfgChecker.checkString('advanced_settings','behavioral_tags','episode',behavioral_tag_episode,'user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                        played_conditional=cfgChecker.checkString('advanced_settings','behavioral_tags','episode',behavioral_tag_episode,'played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                        action_control=cfgChecker.checkInteger('advanced_settings','behavioral_tags','episode',behavioral_tag_episode,'action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                        dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_tags','episode',behavioral_tag_episode,'dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

                        high_priority=cfgChecker.checkBoolean('advanced_settings','behavioral_tags','episode',behavioral_tag_episode,'high_priority',value=None,instanceType=cfgChecker.bool,errOut=True)

                    else:
                        cfgChecker.setCustomErrorText('ConfigValueError: advanced_settings > behavioral_tags > episode > ' + str(behavioral_tag_episode) + ' must be a(n) string or does not match any basic_settings > filter_tags > episode > whitetags or blacktags\n\tValid value(s) are: ' + ', '.join(str(element) for element in (list(filter_episode_whitetag_set) + list(filter_episode_blacktag_set))) + '\n')

#######################################################################################################

            if (not ((behavioral_tags_audio:=cfgChecker.checkDict('advanced_settings','behavioral_tags','audio',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for behavioral_tag_audio in behavioral_tags_audio:
                    if (not ((behavioral_tag_audio_ok:=cfgChecker.checkString(*(),value=behavioral_tag_audio,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=False,comparisonValues=list(filter_audio_whitetag_set) + list(filter_audio_blacktag_set))) == None)):

#######################################################################################################

                        behavioral_tag_contents=cfgChecker.checkDict('advanced_settings','behavioral_tags','audio',behavioral_tag_audio_ok,value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                        action=cfgChecker.checkString('advanced_settings','behavioral_tags','audio',behavioral_tag_audio_ok,'action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['keep','delete'])

                        user_conditional=cfgChecker.checkString('advanced_settings','behavioral_tags','audio',behavioral_tag_audio_ok,'user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                        played_conditional=cfgChecker.checkString('advanced_settings','behavioral_tags','audio',behavioral_tag_audio_ok,'played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                        action_control=cfgChecker.checkInteger('advanced_settings','behavioral_tags','audio',behavioral_tag_audio_ok,'action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                        dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_tags','audio',behavioral_tag_audio_ok,'dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

                        high_priority=cfgChecker.checkBoolean('advanced_settings','behavioral_tags','audio',behavioral_tag_audio_ok,'high_priority',value=None,instanceType=cfgChecker.bool,errOut=True)

                    else:
                        cfgChecker.setCustomErrorText('ConfigValueError: advanced_settings > behavioral_tags > audio > ' + str(behavioral_tag_audio) + ' must be a(n) string or does not match any basic_settings > filter_tags > audio > whitetags or blacktags\n\tValid value(s) are: ' + ', '.join(str(element) for element in (list(filter_audio_whitetag_set) + list(filter_audio_blacktag_set))) + '\n')

#######################################################################################################

            if (isJellyfinServer(brand)):
                if (not ((behavioral_tags_audiobook:=cfgChecker.checkDict('advanced_settings','behavioral_tags','audiobook',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    for behavioral_tag_audiobook in behavioral_tags_audiobook:
                        if (not ((behavioral_tag_audiobook_ok:=cfgChecker.checkString(*(),value=behavioral_tag_audiobook,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=False,comparisonValues=list(filter_audiobook_whitetag_set) + list(filter_audiobook_blacktag_set))) == None)):

#######################################################################################################

                            behavioral_tag_contents=cfgChecker.checkDict('advanced_settings','behavioral_tags','audiobook',behavioral_tag_audiobook_ok,value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            action=cfgChecker.checkString('advanced_settings','behavioral_tags','audiobook',behavioral_tag_audiobook_ok,'action',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['keep','delete'])

                            user_conditional=cfgChecker.checkString('advanced_settings','behavioral_tags','audiobook',behavioral_tag_audiobook_ok,'user_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all'])

                            played_conditional=cfgChecker.checkString('advanced_settings','behavioral_tags','audiobook',behavioral_tag_audiobook_ok,'played_conditional',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=['all_all','any_any','any_all','all_any','any_played','all_played','any_created','all_created','ignore'])

                            action_control=cfgChecker.checkInteger('advanced_settings','behavioral_tags','audiobook',behavioral_tag_audiobook_ok,'action_control',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=8,errOut=True,comparisonValues=None)

                            dynamic_behavior=cfgChecker.checkBoolean('advanced_settings','behavioral_tags','audiobook',behavioral_tag_audiobook_ok,'dynamic_behavior',value=None,instanceType=cfgChecker.bool,errOut=True)

                            high_priority=cfgChecker.checkBoolean('advanced_settings','behavioral_tags','audiobook',behavioral_tag_audiobook_ok,'high_priority',value=None,instanceType=cfgChecker.bool,errOut=True)

                        else:
                            cfgChecker.setCustomErrorText('ConfigValueError: advanced_settings > behavioral_tags > audiobook > ' + str(behavioral_tag_audiobook) + ' must be a(n) string or does not match any basic_settings > filter_tags > audiobook > whitetags or blacktags\n\tValid value(s) are: ' + ', '.join(str(element) for element in (list(filter_audiobook_whitetag_set) + list(filter_audiobook_blacktag_set))) + '\n')

#######################################################################################################

        #sets of global tags for user later
        global_whitetag_set=set()
        global_blacktag_set=set()

        #sets of tags for user later
        movie_whitetag_set=set()
        movie_blacktag_set=set()
        episode_whitetag_set=set()
        episode_blacktag_set=set()
        audio_whitetag_set=set()
        audio_blacktag_set=set()
        audiobook_whitetag_set=set()
        audiobook_blacktag_set=set()

#######################################################################################################

        if (not ((whitetags:=cfgChecker.checkDict('advanced_settings','whitetags',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((whitetags_global:=cfgChecker.checkList('advanced_settings','whitetags','global',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for whitetag_global in whitetags_global:
                    if (not ((whitetag_global:=cfgChecker.checkString('advanced_settings','whitetags','global',whitetags_global.index(whitetag_global),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                        #if ((whitetag_global.find('\\') < 0) or (whitetag_global == None)):
                        if (whitetag_global.find('\\') < 0):
                            global_whitetag_set.add(whitetag_global)

#######################################################################################################

            if (not ((whitetags_movie:=cfgChecker.checkList('advanced_settings','whitetags','movie',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for whitetag_movie in whitetags_movie:
                    if (not ((whitetag_movie:=cfgChecker.checkString('advanced_settings','whitetags','movie',whitetags_movie.index(whitetag_movie),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                        #if ((whitetag_movie.find('\\') < 0) or (whitetag_movie == None)):
                        if (whitetag_movie.find('\\') < 0):
                            movie_whitetag_set.add(whitetag_movie)

#######################################################################################################

            if (not ((whitetags_episode:=cfgChecker.checkList('advanced_settings','whitetags','episode',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for whitetag_episode in whitetags_episode:
                    if (not ((whitetag_episode:=cfgChecker.checkString('advanced_settings','whitetags','episode',whitetags_episode.index(whitetag_episode),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                        #if ((whitetag_episode.find('\\') < 0) or (whitetag_episode == None)):
                        if (whitetag_episode.find('\\') < 0):
                            episode_whitetag_set.add(whitetag_episode)

#######################################################################################################

            if (not ((whitetags_audio:=cfgChecker.checkList('advanced_settings','whitetags','audio',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for whitetag_audio in whitetags_audio:
                    if (not ((whitetag_audio:=cfgChecker.checkString('advanced_settings','whitetags','audio',whitetags_audio.index(whitetag_audio),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                        #if ((whitetag_audio.find('\\') < 0) or (whitetag_audio == None)):
                        if (whitetag_audio.find('\\') < 0):
                            audio_whitetag_set.add(whitetag_audio)

#######################################################################################################

            if (isJellyfinServer(brand)):
                if (not ((whitetags_audiobook:=cfgChecker.checkList('advanced_settings','whitetags','audiobook',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    for whitetag_audiobook in whitetags_audiobook:
                        if (not ((whitetag_audiobook:=cfgChecker.checkString('advanced_settings','whitetags','audiobook',whitetags_audiobook.index(whitetag_audiobook),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                            #if ((whitetag_audiobook.find('\\') < 0) or (whitetag_audiobook == None)):
                            if (whitetag_audiobook.find('\\') < 0):
                                audiobook_whitetag_set.add(whitetag_audiobook)

#######################################################################################################

        if (not ((blacktags:=cfgChecker.checkDict('advanced_settings','blacktags',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((blacktags_global:=cfgChecker.checkList('advanced_settings','blacktags','global',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for blacktag_global in blacktags_global:
                    if (not ((blacktag_global:=cfgChecker.checkString('advanced_settings','blacktags','global',blacktags_global.index(blacktag_global),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                        #if ((blacktag_global.find('\\') < 0) or (blacktag_global == None)):
                        if (blacktag_global.find('\\') < 0):
                            global_blacktag_set.add(blacktag_global)

#######################################################################################################

            if (not ((blacktags_movie:=cfgChecker.checkList('advanced_settings','blacktags','movie',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for blacktag_movie in blacktags_movie:
                    if (not ((blacktag_movie:=cfgChecker.checkString('advanced_settings','blacktags','movie',blacktags_movie.index(blacktag_movie),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                        #if ((blacktag_movie.find('\\') < 0) or (blacktag_movie == None)):
                        if (blacktag_movie.find('\\') < 0):
                            movie_blacktag_set.add(blacktag_movie)

#######################################################################################################

            if (not ((blacktags_episode:=cfgChecker.checkList('advanced_settings','blacktags','episode',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for blacktag_episode in blacktags_episode:
                    if (not ((blacktag_episode:=cfgChecker.checkString('advanced_settings','blacktags','episode',blacktags_episode.index(blacktag_episode),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                        #if ((blacktag_episode.find('\\') < 0) or (blacktag_episode == None)):
                        if (blacktag_episode.find('\\') < 0):
                            episode_blacktag_set.add(blacktag_episode)

#######################################################################################################

            if (not ((blacktags_audio:=cfgChecker.checkList('advanced_settings','blacktags','audio',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                for blacktag_audio in blacktags_audio:
                    if (not ((blacktag_audio:=cfgChecker.checkString('advanced_settings','blacktags','audio',blacktags_audio.index(blacktag_audio),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                        #if ((blacktag_audio.find('\\') < 0) or (blacktag_audio == None)):
                        if (blacktag_audio.find('\\') < 0):
                            audio_blacktag_set.add(blacktag_audio)

#######################################################################################################

            if (isJellyfinServer(brand)):
                if (not ((blacktags_audiobook:=cfgChecker.checkList('advanced_settings','blacktags','audiobook',value=None,instanceType=cfgChecker.list,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    for blacktag_audiobook in blacktags_audiobook:
                        if (not ((blacktag_audiobook:=cfgChecker.checkString('advanced_settings','blacktags','audiobook',blacktags_audiobook.index(blacktag_audiobook),value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):
                            #if ((blacktag_audiobook.find('\\') < 0) or (blacktag_audiobook == None)):
                            if (blacktag_audiobook.find('\\') < 0):
                                audiobook_blacktag_set.add(blacktag_audiobook)

#######################################################################################################

        if (not ((delete_empty_folders:=cfgChecker.checkDict('advanced_settings','delete_empty_folders',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((episode:=cfgChecker.checkDict('advanced_settings','delete_empty_folders','episode',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                season=cfgChecker.checkBoolean('advanced_settings','delete_empty_folders','episode','season',value=None,instanceType=cfgChecker.bool,errOut=True)

                series=cfgChecker.checkBoolean('advanced_settings','delete_empty_folders','episode','series',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (not ((episode_control:=cfgChecker.checkDict('advanced_settings','episode_control',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            minimum_episodes=cfgChecker.checkInteger('advanced_settings','episode_control','minimum_episodes',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=True,comparisonValues=None)

            minimum_played_episodes=cfgChecker.checkInteger('advanced_settings','episode_control','minimum_played_episodes',value=None,instanceType=cfgChecker.int,minValue=0,maxValue=730500,errOut=True,comparisonValues=None)

            behavior_values_list_with_spaces=['max played','max played max played','min played','min played min played','max unplayed','max unplayed max unplayed','min unplayed','min unplayed min unplayed',
                                'max played max unplayed','min played min unplayed','max played min unplayed','min played max unplayed','min unplayed min played','min unplayed max unplayed',
                                'min unplayed max played','min played max played','max unplayed min unplayed','max unplayed mi nplayed','max unplayed max played','max played min played']

            behavior_values_list_without_spaces=['maxplayed','maxplayedmaxplayed','minplayed','minplayedminplayed','maxunplayed','maxunplayedmaxunplayed','minunplayed','minunplayedminunplayed',
                                'maxplayedmaxunplayed','minplayedminunplayed','maxplayedminunplayed','minplayedmaxunplayed','minunplayedminplayed','minunplayedmaxunplayed',
                                'minunplayedmaxplayed','minplayedmaxplayed','maxunplayedminunplayed','maxunplayedminplayed','maxunplayedmaxplayed','maxplayedminplayed']

            minimum_episodes_behavior=cfgChecker.checkString('advanced_settings','episode_control','minimum_episodes_behavior',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=user_ids_check_list + user_names_check_list + behavior_values_list_with_spaces + behavior_values_list_without_spaces)

            if (not ((series_ended:=cfgChecker.checkDict('advanced_settings','episode_control','series_ended',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

                delete_episodes=cfgChecker.checkBoolean('advanced_settings','episode_control','series_ended','delete_episodes',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (not ((radarr:=cfgChecker.checkDict('advanced_settings','radarr',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((movie:=cfgChecker.checkDict('advanced_settings','radarr','movie',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                unmonitor=cfgChecker.checkBoolean('advanced_settings','radarr','movie','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

                remove=cfgChecker.checkBoolean('advanced_settings','radarr','movie','remove',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (not ((sonarr:=cfgChecker.checkDict('advanced_settings','sonarr',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((series:=cfgChecker.checkDict('advanced_settings','sonarr','series',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                unmonitor=cfgChecker.checkBoolean('advanced_settings','sonarr','series','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

                remove=cfgChecker.checkBoolean('advanced_settings','sonarr','series','remove',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

            if (not ((episode:=cfgChecker.checkDict('advanced_settings','sonarr','episode',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                unmonitor=cfgChecker.checkBoolean('advanced_settings','sonarr','episode','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (not ((lidarr:=cfgChecker.checkDict('advanced_settings','lidarr',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((album:=cfgChecker.checkDict('advanced_settings','lidarr','album',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                unmonitor=cfgChecker.checkBoolean('advanced_settings','lidarr','album','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

                remove=cfgChecker.checkBoolean('advanced_settings','lidarr','album','remove',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

            if (not ((track:=cfgChecker.checkDict('advanced_settings','lidarr','track',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                unmonitor=cfgChecker.checkBoolean('advanced_settings','lidarr','track','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (isJellyfinServer(brand)):
            if (not ((readarr:=cfgChecker.checkDict('advanced_settings','readarr',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((book:=cfgChecker.checkDict('advanced_settings','readarr','book',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    unmonitor=cfgChecker.checkBoolean('advanced_settings','readarr','book','unmonitor',value=None,instanceType=cfgChecker.bool,errOut=True)

                    remove=cfgChecker.checkBoolean('advanced_settings','readarr','book','remove',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (not ((trakt_fix:=cfgChecker.checkDict('advanced_settings','trakt_fix',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((episode_control:=cfgChecker.checkDict('advanced_settings','trakt_fix','set_missing_last_played_date',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                trakt_fix_movie=cfgChecker.checkBoolean('advanced_settings','trakt_fix','set_missing_last_played_date','movie',value=None,instanceType=cfgChecker.bool,errOut=True)

                trakt_fix_episode=cfgChecker.checkBoolean('advanced_settings','trakt_fix','set_missing_last_played_date','episode',value=None,instanceType=cfgChecker.bool,errOut=True)

                trakt_fix_audio=cfgChecker.checkBoolean('advanced_settings','trakt_fix','set_missing_last_played_date','audio',value=None,instanceType=cfgChecker.bool,errOut=True)

                if (isJellyfinServer(brand)):

                    trakt_fix_audiobook=cfgChecker.checkBoolean('advanced_settings','trakt_fix','set_missing_last_played_date','audiobook',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        if (not ((console_controls:=cfgChecker.checkDict('advanced_settings','console_controls',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

            if (not ((headers:=cfgChecker.checkDict('advanced_settings','console_controls','headers',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((script:=cfgChecker.checkDict('advanced_settings','console_controls','headers','script',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','headers','script','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','headers','script','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','headers','script','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','headers','script','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','headers','script','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','headers','script','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','headers','script','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((user:=cfgChecker.checkDict('advanced_settings','console_controls','headers','user',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','headers','user','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','headers','user','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','headers','user','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','headers','user','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','headers','user','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','headers','user','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','headers','user','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################
                if (not ((summary:=cfgChecker.checkDict('advanced_settings','console_controls','headers','summary',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','headers','summary','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','headers','summary','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','headers','summary','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','headers','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','headers','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','headers','summary','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','headers','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

            if (not ((footers:=cfgChecker.checkDict('advanced_settings','console_controls','footers',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((script:=cfgChecker.checkDict('advanced_settings','console_controls','footers','script',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','footers','script','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','footers','script','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','footers','script','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','footers','script','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','footers','script','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','footers','script','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','footers','script','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

            if (not ((warnings:=cfgChecker.checkDict('advanced_settings','console_controls','warnings',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((script:=cfgChecker.checkDict('advanced_settings','console_controls','warnings','script',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','warnings','script','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','warnings','script','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','warnings','script','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','warnings','script','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','warnings','script','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','warnings','script','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','warnings','script','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

            if (not ((movie:=cfgChecker.checkDict('advanced_settings','console_controls','movie',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((delete:=cfgChecker.checkDict('advanced_settings','console_controls','movie','delete',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','movie','delete','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','movie','delete','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','movie','delete','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','movie','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','movie','delete','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','movie','delete','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','movie','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((keep:=cfgChecker.checkDict('advanced_settings','console_controls','movie','keep',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','movie','keep','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','movie','keep','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','movie','keep','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','movie','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','movie','keep','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','movie','keep','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','movie','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((post_processing:=cfgChecker.checkDict('advanced_settings','console_controls','movie','post_processing',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','movie','post_processing','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','movie','post_processing','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','movie','post_processing','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','movie','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','movie','post_processing','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','movie','post_processing','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','movie','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((summary:=cfgChecker.checkDict('advanced_settings','console_controls','movie','summary',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','movie','summary','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','movie','summary','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','movie','summary','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','movie','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','movie','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','movie','summary','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','movie','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

            if (not ((episode:=cfgChecker.checkDict('advanced_settings','console_controls','episode',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((delete:=cfgChecker.checkDict('advanced_settings','console_controls','episode','delete',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','episode','delete','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','episode','delete','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','episode','delete','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','episode','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','episode','delete','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','episode','delete','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','episode','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((keep:=cfgChecker.checkDict('advanced_settings','console_controls','episode','keep',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','episode','keep','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','episode','keep','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','episode','keep','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','episode','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','episode','keep','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','episode','keep','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','episode','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((post_processing:=cfgChecker.checkDict('advanced_settings','console_controls','episode','post_processing',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','episode','post_processing','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','episode','post_processing','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','episode','post_processing','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','episode','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','episode','post_processing','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','episode','post_processing','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','episode','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((summary:=cfgChecker.checkDict('advanced_settings','console_controls','episode','summary',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','episode','summary','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','episode','summary','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','episode','summary','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','episode','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','episode','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','episode','summary','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','episode','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

            if (not ((audio:=cfgChecker.checkDict('advanced_settings','console_controls','audio',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                if (not ((delete:=cfgChecker.checkDict('advanced_settings','console_controls','audio','delete',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','audio','delete','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','audio','delete','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','audio','delete','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','audio','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','audio','delete','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','audio','delete','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','audio','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((keep:=cfgChecker.checkDict('advanced_settings','console_controls','audio','keep',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','audio','keep','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','audio','keep','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','audio','keep','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','audio','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','audio','keep','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','audio','keep','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','audio','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((post_processing:=cfgChecker.checkDict('advanced_settings','console_controls','audio','post_processing',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','audio','post_processing','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','audio','post_processing','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','audio','post_processing','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','audio','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','audio','post_processing','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','audio','post_processing','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','audio','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                if (not ((summary:=cfgChecker.checkDict('advanced_settings','console_controls','audio','summary',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    show=cfgChecker.checkBoolean('advanced_settings','console_controls','audio','summary','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                    if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','audio','summary','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','audio','summary','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','audio','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                            style=cfgChecker.checkString('advanced_settings','console_controls','audio','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                        if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','audio','summary','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            color=cfgChecker.checkString('advanced_settings','console_controls','audio','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

            if (isJellyfinServer(brand)):
                if (not ((audiobook:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                    if (not ((delete:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','delete',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        show=cfgChecker.checkBoolean('advanced_settings','console_controls','audiobook','delete','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                        if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','delete','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','delete','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                                color=cfgChecker.checkString('advanced_settings','console_controls','audiobook','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                                style=cfgChecker.checkString('advanced_settings','console_controls','audiobook','delete','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                            if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','delete','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                                color=cfgChecker.checkString('advanced_settings','console_controls','audiobook','delete','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                    if (not ((keep:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','keep',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        show=cfgChecker.checkBoolean('advanced_settings','console_controls','audiobook','keep','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                        if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','keep','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','keep','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                                color=cfgChecker.checkString('advanced_settings','console_controls','audiobook','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                                style=cfgChecker.checkString('advanced_settings','console_controls','audiobook','keep','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                            if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','keep','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                                color=cfgChecker.checkString('advanced_settings','console_controls','audiobook','keep','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                    if (not ((post_processing:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','post_processing',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        show=cfgChecker.checkBoolean('advanced_settings','console_controls','audiobook','post_processing','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                        if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','post_processing','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','post_processing','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                                color=cfgChecker.checkString('advanced_settings','console_controls','audiobook','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                                style=cfgChecker.checkString('advanced_settings','console_controls','audiobook','post_processing','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                            if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','post_processing','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                                color=cfgChecker.checkString('advanced_settings','console_controls','audiobook','post_processing','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                    if (not ((summary:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','summary',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                        show=cfgChecker.checkBoolean('advanced_settings','console_controls','audiobook','summary','show',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

                        if (not ((formatting:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','summary','formatting',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                            if (not ((font:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','summary','formatting','font',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                                color=cfgChecker.checkString('advanced_settings','console_controls','audiobook','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

                                style=cfgChecker.checkString('advanced_settings','console_controls','audiobook','summary','formatting','font','style',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

                            if (not ((background:=cfgChecker.checkDict('advanced_settings','console_controls','audiobook','summary','formatting','background',value=None,instanceType=cfgChecker.dict,minLength=None,maxLength=None,errOut=True,comparisonValues=None)) == None)):

#######################################################################################################

                                color=cfgChecker.checkString('advanced_settings','console_controls','audiobook','summary','formatting','font','color',value=None,instanceType=cfgChecker.str,minLength=None,maxLength=None,errOut=True,comparisonValues=None)

#######################################################################################################

        update_config=cfgChecker.checkBoolean('advanced_settings','UPDATE_CONFIG',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

        remove_files=cfgChecker.checkBoolean('advanced_settings','REMOVE_FILES',value=None,instanceType=cfgChecker.bool,errOut=True)

#######################################################################################################

    #Check for overlapping tags between blacklists and whitelists
    cfgChecker.checkOverlappingTags(global_whitetag_set,global_blacktag_set,
                                      movie_whitetag_set,movie_blacktag_set,filter_movie_whitetag_set,filter_movie_blacktag_set,
                                      episode_whitetag_set,episode_blacktag_set,filter_episode_whitetag_set,filter_episode_blacktag_set,
                                      audio_whitetag_set,audio_blacktag_set,filter_audio_whitetag_set,filter_audio_blacktag_set,
                                      audiobook_whitetag_set,audiobook_blacktag_set,filter_audiobook_whitetag_set,filter_audiobook_blacktag_set)

#######################################################################################################

    cfgChecker.printError()

    ##Bring all errors found to users attention
    #if (not (error_found_in_mumc_config_yaml == '')):
        #if (init_dict['DEBUG']):
            #appendTo_DEBUG_log("\n" + error_found_in_mumc_config_yaml,2,init_dict)
        #print('\n' + error_found_in_mumc_config_yaml)
        #sys.exit(0)

#######################################################################################################
    return cfg,init_dict


#admin_settings and server have to be checked early
def pre_cfgCheckYAML(cfg):
    error_found_in_mumc_config_yaml=''
    try:
        cfg['admin_settings']=cfg['admin_settings']
        try:
            cfg['admin_settings']['server']=cfg['admin_settings']['server']
            try:
                cfg['admin_settings']['server']['brand']=cfg['admin_settings']['server']['brand']
            except:
                error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > brand is missing from the configuration file\n'
            try:
                cfg['admin_settings']['server']['url']=cfg['admin_settings']['server']['url']
            except:
                error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > url is missing from the configuration file\n'
            try:
                cfg['admin_settings']['server']['auth_key']=cfg['admin_settings']['server']['auth_key']
            except:
                error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > auth_key is missing from the configuration file\n'
            try:
                cfg['admin_settings']['server']['admin_id']=cfg['admin_settings']['server']['admin_id']
            except:
                pass
                #error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server > admin_id is missing from the configuration file\n'
        except:
            error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > server is missing from the configuration file\n'
        try:
            cfg['admin_settings']['users']=cfg['admin_settings']['users']
        except:
            error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings > users is missing from the configuration file\n'
    except:
        error_found_in_mumc_config_yaml+='ConfigVariableError: admin_settings is missing from the configuration file\n'

    #Bring all errors found to users attention
    if (not (error_found_in_mumc_config_yaml == '')):
        print('\n' + error_found_in_mumc_config_yaml)
        sys.exit(0)