

#Check select argv/environmental variables are as expected
def cfgCheckARGENV(argvCfgChecker):

    #check if command line option exists
    if (argvCfgChecker.getValue('-server_brand')):
        #verify command line option has an expected data type and/or value
        if ((server_brand:=argvCfgChecker.checkString('-server_brand',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False,comparisonValues=['emby','jellyfin'])) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: server_brand option/environmental-variable must be a string\n\tValid values {",".join(["emby","jellyfin"])}\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-server_url')):
        #verify command line option has an expected data type and/or value
        if ((server_url:=argvCfgChecker.checkString('-server_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: server_url option/environmental-variable must be a string\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-server_port')):
        #verify command line option has an expected data type and/or value
        if ((server_port:=argvCfgChecker.checkInteger('-server_port',value=None,instanceType=argvCfgChecker.int,required=False,minValue=1,maxValue=65535,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: server_port option/environmental-variable must be an integer\n\tValid values 1 thru 65535\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-server_base_url')):
        #verify command line option has an expected data type and/or value
        if ((server_base_url:=argvCfgChecker.checkString('-server_base_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: server_base_url option/environmental-variable must be a string\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-admin_username')):
        #verify command line option has an expected data type and/or value
        if ((admin_username:=argvCfgChecker.checkString('-admin_username',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: admin_username option/environmental-variable must be a string\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-admin_password')):
        #verify command line option has an expected data type and/or value
        if ((admin_password:=argvCfgChecker.checkString('-admin_password',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: admin_password option/environmental-variable must be a string\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-server_auth_key')):
        #verify command line option has an expected data type and/or value
        if ((server_auth_key:=argvCfgChecker.checkString('-server_auth_key',value=None,instanceType=argvCfgChecker.str,required=False,minLength=8,maxLength=32,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: server_auth_key option/environmental-variable must be a string\n\tValid minimium length is: 8\n\tValid maximium length is: 32\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-server_admin_id')):
        #verify command line option has an expected data type and/or value
        if ((server_admin_id:=argvCfgChecker.checkString('-server_admin_id',value=None,instanceType=argvCfgChecker.str,required=False,minLength=8,maxLength=32,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: server_admin_id option/environmental-variable must be a string\n\tValid minimium length is: 8\n\tValid maximium length is: 32\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-list_behavior')):
        #verify command line option has an expected data type and/or value
        if ((list_behavior:=argvCfgChecker.checkString('-list_behavior',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False,comparisonValues=['blacklist','whitelist'])) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: list_behavior option/environmental-variable must be a string\n\tValid values {",".join(["blacklist","whitelist"])}\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-matching_behavior')):
        #verify command line option has an expected data type and/or value
        if ((matching_behavior:=argvCfgChecker.checkString('-matching_behavior',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False,comparisonValues=['byid','bypath','bynetworkpath'])) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: matching_behavior option/environmental-variable must be a string\n\tValid values {",".join(["byid","bypath","bynetworkpath"])}\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-global_blacktags')):
        #verify command line option has an expected data type and/or value
        if (not ((global_blacktags:=argvCfgChecker.checkList('-global_blacktags',value=None,instanceType=argvCfgChecker.list,required=False,minLength=None,maxLength=None,errOut=False)) == None)):
            #loop thru all tags
            for thisTag in global_blacktags:
                #verify is expected data type and/or value
                if ((tag:=argvCfgChecker.checkString(*(),value=thisTag,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
                    #set error if not expected data type and/or value
                    argvCfgChecker.setCustomErrorText(f'CmdEnvError: global_blacktag > {thisTag} option/environmental-variable must be a string\n')
        else:
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: global_blacktag option/environmental-variable must be a comma separated string of tags\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-global_whitetags')):
        #verify command line option has an expected data type and/or value
        if (not ((global_whitetags:=argvCfgChecker.checkList('-global_whitetags',value=None,instanceType=argvCfgChecker.list,required=False,minLength=None,maxLength=None,errOut=False)) == None)):
            #loop thru all tags
            for thisTag in global_whitetags:
                #verify is expected data type and/or value
                if ((tag:=argvCfgChecker.checkString(*(),value=thisTag,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
                    #set error if not expected data type and/or value
                    argvCfgChecker.setCustomErrorText(f'CmdEnvError: global_whitetag > {thisTag} option/environmental-variable must be a string\n')
        else:
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: global_whitetag option/environmental-variable must be a comma separated string of tags\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-monitor_disabled_users')):
        #verify command line option has an expected data type and/or value
        if ((monitor_disabled_users:=argvCfgChecker.checkBoolean('-monitor_disabled_users',value=None,instanceType=argvCfgChecker.bool,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: monitor_disabled_users option/environmental-variable must be a boolean\n\tValid values True,False\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-user_library_selection')):
        #verify command line option has an expected data type and/or value
        if ((user_library_selection:=argvCfgChecker.checkInteger('-user_library_selection',value=None,instanceType=argvCfgChecker.int,required=False,minValue=0,maxValue=3,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: user_library_selection option/environmental-variable must be an integer\n\tValid values 0 thru 3\n')

    #check if command line option exists
    if ((argvCfgChecker.getValue('-radarr_url')) and (argvCfgChecker.getValue('-radarr_api_key'))):
        #verify command line option has an expected data type and/or value
        if (not ((radarr_url:=argvCfgChecker.checkList('-radarr_url',value=None,instanceType=argvCfgChecker.list,required=False,minLength=len(argvCfgChecker.cfg['-radarr_api_key']),maxLength=len(argvCfgChecker.cfg['-radarr_api_key']),errOut=False)) == None)):
            #loop thru all urls
            for thisURL in radarr_url:
                #verify is expected data type and/or value
                if ((url:=argvCfgChecker.checkString(*(),value=thisURL,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
                    #set error if not expected data type and/or value
                    argvCfgChecker.setCustomErrorText(f'CmdEnvError: radarr_url > {thisURL} option/environmental-variable must be a string\n')
        else:
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: radarr_url option/environmental-variable must be a comma separated string of URLs\n\tradarr_url and radarr_api_key must have the same number of entries\n')
    else:
            #set error if not used with sibling
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: radarr_url and radarr_api_key options/environmental-variables must be used together\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-radarr_port')):
        #verify command line option has an expected data type and/or value
        if ((radarr_port:=argvCfgChecker.checkInteger('-radarr_port',value=None,instanceType=argvCfgChecker.int,required=False,minValue=1,maxValue=65535,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: radarr_port option/environmental-variable must be an integer\n\tValid values 1 thru 65535\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-radarr_base_url')):
        #verify command line option has an expected data type and/or value
        if ((radarr_base_url:=argvCfgChecker.checkString('-radarr_base_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: radarr_base_url option/environmental-variable must be a string\n')

    #check if command line option exists
    if ((argvCfgChecker.getValue('-radarr_api_key')) and (argvCfgChecker.getValue('-radarr_url'))):
        #verify command line option has an expected data type and/or value
        if (not ((radarr_api_key:=argvCfgChecker.checkList('-radarr_api_key',value=None,instanceType=argvCfgChecker.list,required=False,minLength=len(argvCfgChecker.cfg['-radarr_url']),maxLength=len(argvCfgChecker.cfg['-radarr_url']),errOut=False)) == None)):
            #loop thru all urls
            for thisAPIKey in radarr_api_key:
                #verify is expected data type and/or value
                if ((url:=argvCfgChecker.checkString(*(),value=thisAPIKey,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
                    #set error if not expected data type and/or value
                    argvCfgChecker.setCustomErrorText(f'CmdEnvError: radarr_api_key > {thisAPIKey} option/environmental-variable must be a string\n')
        else:
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: radarr_api_key option/environmental-variable must be a comma separated string of API keys\n\tradarr_url and radarr_api_key must have the same number of entries\n')
    else:
            #set error if not used with sibling
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: radarr_api_key and radarr_url options/environmental-variables must be used together\n')

    #check if command line option exists
    if ((argvCfgChecker.getValue('-sonarr_url')) and (argvCfgChecker.getValue('-sonarr_api_key'))):
        #verify command line option has an expected data type and/or value
        if (not ((sonarr_url:=argvCfgChecker.checkList('-sonarr_url',value=None,instanceType=argvCfgChecker.list,required=False,minLength=len(argvCfgChecker.cfg['-sonarr_api_key']),maxLength=len(argvCfgChecker.cfg['-sonarr_api_key']),errOut=False)) == None)):
            #loop thru all urls
            for thisURL in sonarr_url:
                #verify is expected data type and/or value
                if ((url:=argvCfgChecker.checkString(*(),value=thisURL,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
                    #set error if not expected data type and/or value
                    argvCfgChecker.setCustomErrorText(f'CmdEnvError: sonarr_url > {thisURL} option/environmental-variable must be a string\n')
        else:
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: sonarr_url option/environmental-variable must be a comma separated string of URLs\n\tsonarr_url and sonarr_api_key must have the same number of entries\n')
    else:
            #set error if not used with sibling
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: sonarr_url and sonarr_api_key options/environmental-variables must be used together\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-sonarr_port')):
        #verify command line option has an expected data type and/or value
        if ((sonarr_port:=argvCfgChecker.checkInteger('-sonarr_port',value=None,instanceType=argvCfgChecker.int,required=False,minValue=1,maxValue=65535,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: sonarr_port option/environmental-variable must be an integer\n\tValid values 1 thru 65535\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-sonarr_base_url')):
        #verify command line option has an expected data type and/or value
        if ((sonarr_base_url:=argvCfgChecker.checkString('-sonarr_base_url',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: sonarr_base_url option/environmental-variable must be a string\n')

    #check if command line option exists
    if ((argvCfgChecker.getValue('-sonarr_api_key')) and (argvCfgChecker.getValue('-sonarr_url'))):
        #verify command line option has an expected data type and/or value
        if (not ((sonarr_api_key:=argvCfgChecker.checkList('-sonarr_api_key',value=None,instanceType=argvCfgChecker.list,required=False,minLength=len(argvCfgChecker.cfg['-sonarr_url']),maxLength=len(argvCfgChecker.cfg['-sonarr_url']),errOut=False)) == None)):
            #loop thru all urls
            for thisAPIKey in sonarr_api_key:
                #verify is expected data type and/or value
                if ((url:=argvCfgChecker.checkString(*(),value=thisAPIKey,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
                    #set error if not expected data type and/or value
                    argvCfgChecker.setCustomErrorText(f'CmdEnvError: sonarr_api_key > {thisAPIKey} option/environmental-variable must be a string\n')
        else:
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: sonarr_api_key option/environmental-variable must be a comma separated string of API keys\n\tsonarr_url and sonarr_api_key must have the same number of entries\n')
    else:
            #set error if not used with sibling
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: sonarr_api_key and sonarr_url options/environmental-variables must be used together\n')

    #check if command line option exists
    if (argvCfgChecker.getValue('-config')):
        #verify command line option has an expected data type and/or value
        if ((config:=argvCfgChecker.checkString('-config',value=None,instanceType=argvCfgChecker.str,required=False,minLength=None,maxLength=None,errOut=False)) == None):
            #set error if not expected data type and/or value
            argvCfgChecker.setCustomErrorText(f'CmdEnvError: config option/environmental-variable must be a string\n')

    #print any logged errors
    argvCfgChecker.printError()

    return argvCfgChecker.cfg