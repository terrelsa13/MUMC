import sys
from mumc_modules.mumc_versions import get_semantic_version_parts,checkYAMLVersion,get_script_version
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_server_type import isJellyfinServer
from mumc_modules.mumc_compare_items import keys_exist_return_value
from mumc_modules.mumc_tagged import get_isFilterStatementTag
from mumc_modules.mumc_data_checks import data_checker


#Check select argv/environmental variables are as expected
def cfgCheckARGV(argvCfgChecker):

    if (argvCfgChecker.getValue('-server_brand')):
        if ((server_brand:=argvCfgChecker.checkString('-server_brand',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False,comparisonValues=['emby','jellyfin'])) == None):
            argvCfgChecker.setCustomErrorText(f'server_brand option/environmental-variable must be a string\n\tValid values {",".join(["emby","jellyfin"])}')

    if (argvCfgChecker.getValue('-server_url')):
        if ((server_url:=argvCfgChecker.checkString('-server_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'server_url option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-server_port')):
        if ((server_port:=argvCfgChecker.checkInteger('-server_port',value=None,instanceType=argvCfgChecker.int,required=False,minValue=1,maxValue=65535,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'server_port option/environmental-variable must be a integer\n\tValid values 1 thru 65535')

    if (argvCfgChecker.getValue('-server_base_url')):
        if ((server_base_url:=argvCfgChecker.checkString('-server_base_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'server_base_url option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-admin_username')):
        if ((admin_username:=argvCfgChecker.checkString('-admin_username',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'admin_username option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-admin_password')):
        if ((admin_password:=argvCfgChecker.checkString('-admin_password',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'admin_password option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-server_auth_key')):
        if ((server_auth_key:=argvCfgChecker.checkString('-server_auth_key',value=None,instanceType=argvCfgChecker.str,required=False,minLength=8,maxLength=32,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'server_auth_key option/environmental-variable must be a string\n\tValid minimium length is: 8\n\tValid maximium length is: 32')

    if (argvCfgChecker.getValue('-server_admin_id')):
        if ((server_admin_id:=argvCfgChecker.checkString('-server_admin_id',value=None,instanceType=argvCfgChecker.str,required=False,minLength=8,maxLength=32,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'server_admin_id option/environmental-variable must be a string\n\tValid minimium length is: 8\n\tValid maximium length is: 32')

    if (argvCfgChecker.getValue('-list_behavior')):
        if ((list_behavior:=argvCfgChecker.checkString('-list_behavior',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False,comparisonValues=['blacklist','whitelist'])) == None):
            argvCfgChecker.setCustomErrorText(f'list_behavior option/environmental-variable must be a string\n\tValid values {",".join(["blacklist","whitelist"])}')

    if (argvCfgChecker.getValue('-matching_behavior')):
        if ((matching_behavior:=argvCfgChecker.checkString('-matching_behavior',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False,comparisonValues=['byid','bypath','bynetworkpath'])) == None):
            argvCfgChecker.setCustomErrorText(f'matching_behavior option/environmental-variable must be a string\n\tValid values {",".join(["byid","bypath","bynetworkpath"])}')

    if (argvCfgChecker.getValue('-global_blacktags')):
        if ((global_blacktags:=argvCfgChecker.checkList('-global_blacktags',value=None,instanceType=argvCfgChecker.list,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            for tag in global_blacktags:
                if ((tag:=argvCfgChecker.checkString((),value=tag,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
                    argvCfgChecker.setCustomErrorText(f'global_blacktag > \'{tag}\' option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-global_whitetags')):
        if ((global_whitetags:=argvCfgChecker.checkList('-global_whitetags',value=None,instanceType=argvCfgChecker.list,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            for tag in global_whitetags:
                if ((tag:=argvCfgChecker.checkString((),value=tag,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
                    argvCfgChecker.setCustomErrorText(f'global_whitetag > \'{tag}\' option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-monitor_disabled_users')):
        if ((monitor_disabled_users:=argvCfgChecker.checkBoolean('-monitor_disabled_users',value=None,instanceType=argvCfgChecker.bool,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'monitor_disabled_users option/environmental-variable must be a boolean\n\tValid values True,False')

    if (argvCfgChecker.getValue('-user_library_selection')):
        if ((user_library_selection:=argvCfgChecker.checkInteger('-user_library_selection',value=None,instanceType=argvCfgChecker.int,required=False,minValue=0,maxValue=3,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'user_library_selection option/environmental-variable must be a integer\n\tValid values 0 thru 3')

    if (argvCfgChecker.getValue('-radarr_url')):
        if ((radarr_url:=argvCfgChecker.checkString('-radarr_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'radarr_url option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-radarr_port')):
        if ((radarr_port:=argvCfgChecker.checkInteger('-radarr_port',value=None,instanceType=argvCfgChecker.int,required=False,minValue=1,maxValue=65535,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'radarr_port option/environmental-variable must be a integer\n\tValid values 1 thru 65535')

    if (argvCfgChecker.getValue('-radarr_base_url')):
        if ((radarr_base_url:=argvCfgChecker.checkString('-radarr_base_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'radarr_base_url option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-radarr_api_key')):
        if ((radarr_api_key:=argvCfgChecker.checkString('-radarr_api_key',value=None,instanceType=argvCfgChecker.str,required=False,minLength=8,maxLength=32,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'radarr_api_key option/environmental-variable must be a string\n\tValid minimium length is: 8\n\tValid maximium length is: 32')

    if (argvCfgChecker.getValue('-sonarr_url')):
        if ((sonarr_url:=argvCfgChecker.checkString('-sonarr_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'sonarr_url option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-sonarr_port')):
        if ((sonarr_port:=argvCfgChecker.checkInteger('-sonarr_port',value=None,instanceType=argvCfgChecker.int,required=False,minValue=1,maxValue=65535,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'sonarr_port option/environmental-variable must be a integer\n\tValid values 1 thru 65535')

    if (argvCfgChecker.getValue('-sonarr_base_url')):
        if ((sonarr_base_url:=argvCfgChecker.checkString('-sonarr_base_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'sonarr_base_url option/environmental-variable must be a string')

    if (argvCfgChecker.getValue('-sonarr_api_key')):
        if ((sonarr_api_key:=argvCfgChecker.checkString('-sonarr_api_key',value=None,instanceType=argvCfgChecker.str,required=False,minLength=8,maxLength=32,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'sonarr_api_key option/environmental-variable must be a string\n\tValid minimium length is: 8\n\tValid maximium length is: 32')

    if (argvCfgChecker.getValue('-config')):
        if ((config:=argvCfgChecker.checkString('-config',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            argvCfgChecker.setCustomErrorText(f'config option/environmental-variable must be a string')

    #if (argvCfgChecker.getValue('-config_updater')):
        #if ((config_updater:=argvCfgChecker.checkBoolean('config_updater',value=None,instanceType=argvCfgChecker.bool,errOut=False)) == None):
            #argvCfgChecker.setCustomErrorText(f'config_updater option/environmental-variable must be a boolean\n\tValid values True,False')

    #print any logged errors
    argvCfgChecker.printError()

    return argvCfgChecker.cfg