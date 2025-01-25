import os
import sys
import copy
from pathlib import Path
from mumc_modules.mumc_console_info import default_helper_menu,print_full_help_menu,missing_config_argument_helper,missing_config_argument_format_helper,alt_config_file_does_not_exists_helper,alt_config_syntax_helper,unknown_command_line_option_helper
from mumc_modules.mumc_paths_files import getFullPathName,getFileExtension,doesFileExist
from mumc_modules.mumc_console_attributes import console_text_attributes
from mumc_modules.mumc_setup_questions import get_admin_username,get_admin_password
from mumc_modules.mumc_key_authentication import authenticate_user_by_name,get_labelled_authentication_keys,get_MUMC_labelled_authentication_key,create_labelled_authentication_key,delete_labelled_authentication_key
from mumc_modules.mumc_config_updater import yaml_configurationUpdater
from mumc_modules.mumc_config_import import importConfig
from mumc_modules.mumc_yaml_check import cfgCheckYAML


#define custom exception
class UnknownCMDOptionError(Exception):
    pass


#define custom exception
class CMDOptionIndexError(Exception):
    pass


#define custom exception
class CMDOptionMissingIndexError(Exception):
    pass


#define custom exception
class CMDArgumentError(Exception):
    pass


#define custom exception
class CMDMissingArgumentError(Exception):
    pass


#define custom exception
class CMDArgumentNotFoundError(Exception):
    pass


#define custom exception
class CMDArgumentMissingNotFoundError(Exception):
    pass


#define custom exception
class CMDArgumentSyntaxError(Exception):
    pass


#define custom exception
class CMDArgumentMissingSyntaxError(Exception):
    pass


#find command "-?"
#verify we do not end with a "-?"
#verify another "-?" not come after this "-?"
#get the argument related to the "-?" command
#verify argument after "-?" exists and/or is formatted correctly


#find command
def findCMDRequest(argv,*queriedcommands):
    for cmdOption in argv:
        #if ((cmdOption.casefold() == '-sb') or (cmdOption.casefold() == '-server_brand')):
        if (cmdOption.casefold() in queriedcommands):
            return cmdOption.casefold()
    return False


#verify there -? command is not the last item; we are expecting a argument to come after it
def findCMDNotLast(cmdOption,argv,the_dict):
    try:
        if (cmdOption):
            #for checkOption in argv:
            if ((argv.index(cmdOption) + 1) >= len(argv)):
                raise CMDOptionIndexError
            else:
                return cmdOption.casefold()
        else:
            raise CMDOptionMissingIndexError
    except (CMDOptionIndexError,CMDOptionMissingIndexError):
        missing_config_argument_helper(argv,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)


#verify there -? command is not followed by another -?; we are expecting a argument to come after it
def findNoCMDAfterCMD(cmdOption,argv,optionsList,the_dict):
    try:
        if (cmdOption):
            #for checkOption in optionsList:
            if ((argv[argv.index(cmdOption) + 1]) in optionsList):
                raise CMDArgumentError
            else:
                return cmdOption.casefold()
        else:
            raise CMDMissingArgumentError
    except (CMDArgumentError,CMDMissingArgumentError):
        missing_config_argument_format_helper(argv,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)


#get the argument related to this -? command
def getCMDArgument(cmdOption,argv):
    if (cmdOption):
        return argv[argv.index(cmdOption) + 1]
    else:
        return None


##wip
#verify alternate config exists
def verifyPathFileExist(file_path,argv,the_dict):
    try:
        if (file_path):
            fullPathName=getFullPathName(file_path)
            #verify alternate config path and file exist
            if (fullPathName == None):
                raise CMDArgumentNotFoundError
            else:
                return fullPathName
        else:
            raise CMDArgumentMissingNotFoundError
    except (CMDArgumentNotFoundError,CMDArgumentMissingNotFoundError):
        alt_config_file_does_not_exists_helper(argv,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)


##wip
#verify alternate config file name follows the python module naming convention
def parsePathFileSyntax(argv,file_path,cmdOption,moduleExtension,the_dict):
    try:
        if (file_path):
            argExt=getFileExtension(file_path)
            if ((argExt in moduleExtension) and
                #((os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])).count(".") == 0) and
                #((os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])).count(" ") == 0)):
                ((os.path.basename(os.path.splitext(file_path)[0])).count(".") == 0) and
                ((os.path.basename(os.path.splitext(file_path)[0])).count(" ") == 0)):
                #Get path without file.name
                argPath=Path(os.path.dirname(file_path + 1))
                #Get file without extension
                argFileNoExt=os.path.basename(os.path.splitext(file_path)[0])
                return argPath,argFileNoExt,argFileNoExt+argExt
            else:
                raise CMDArgumentSyntaxError
        else:
            raise CMDArgumentMissingSyntaxError
    except (CMDArgumentSyntaxError,CMDArgumentMissingSyntaxError):
        alt_config_syntax_helper(argv,cmdOption,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)

    #return argPath,argFileNoExt,argFileNoExt+argExt


#find unknown command line options
def findUnknownCMDRequest(argv,optionsList,the_dict):
    unknownCommands=[]
    for cmdOption in argv:
        if (cmdOption.startswith('-')):
            if (not(cmdOption in optionsList)):
                unknownCommands.append(cmdOption)

    if (unknownCommands):
        for unknownCommand in unknownCommands:
            unknown_command_line_option_helper(unknownCommand,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)


#find the show help command
#def findHelpCMDRequest(argv,the_dict):
    #if (findCMDRequest(argv,'-h','-help','-?')):
        #print_full_help_menu(the_dict)
        #sys.exit(0)


#find command to show console attributes
#def findConsoleAttributeShowRequest(argv):
    #if (findCMDRequest(argv,'-a','-attr','-attrs','-attribute','-attributes')):
        #console_text_attributes().console_attribute_test()
        #sys.exit(0)


#find alternate configuration command and argument
def findAlternateConfigCMDAndArgument(argv,optionsList,moduleExtension,the_dict,*queriedcommands):
    if (cmdOption:=findCMDRequest(argv,queriedcommands)):
        if (cmdOption:=findCMDNotLast(cmdOption,argv,the_dict)):
            if (cmdOption:=findNoCMDAfterCMD(cmdOption,argv,optionsList,the_dict)):
                if (cmdArgument:=getCMDArgument(cmdOption,argv)):
                    if(verifyPathFileExist(cmdArgument,argv,the_dict)):
                        [argumentPath,argumentFileNoExt,argumentFileExt]=parsePathFileSyntax(argv,cmdArgument,cmdOption,moduleExtension,the_dict)
                        return argumentPath,argumentFileNoExt,argumentFileExt
                else:
                    return cmdArgument
    else:
        return cmdOption


#find running as container command
#def findContainerCMDRequest(argv):
    #if (findCMDRequest(argv,'-d','-container')):
        #return True
    #return False


#find configuration updater command
#def findConfigUpdaterCMDRequest(argv):
    #if (findCMDRequest(argv,'-u','-updater','-config-updater','-configuration-updater')):
        #return True
    #return False


#find option to remake authentication key in the GUI
def findRemakeAuthKeyRequest(cmdopt_dict,the_dict):

    argv=cmdopt_dict['argv']
    #import config file
    cfg,the_dict=importConfig(the_dict,cmdopt_dict)
    #get and check config values are what we expect them to be
    cfg=cfgCheckYAML(cfg,the_dict)
    #merge cfg and init_dict; goal is to preserve cfg's structure
    the_dict.update(copy.deepcopy(cfg))
    cfg=copy.deepcopy(the_dict)

    if (cmdopt_dict['altConfigInfo'] and doesFileExist(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt'])):
        config_file_full_path=cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt']
        cfg['mumc_path']=cmdopt_dict['altConfigPath']
        cfg['config_file_name_yaml']=cmdopt_dict['altConfigFileExt']
    elif (doesFileExist(cfg['mumc_path'] / cfg['config_file_name_yaml'])):
        config_file_full_path=cfg['mumc_path'] / cfg['config_file_name_yaml']
    else:
        print('Unable to find valid configuration file.')
        sys.exit(0)
        
    #for cmdOption in argv:
    #if ((cmdOption == '-rak') or (cmdOption == '-remake-api-key')):
    if (findCMDRequest(argv,'-rak','-remake-api-key')):
        print('')
        #admin username?
        admin_username=get_admin_username()
        print('')
        #admin password?
        admin_password=get_admin_password()
        print('')
        #ask server for authentication key using administrator username and password
        authenticated_user_data=authenticate_user_by_name(admin_username,admin_password,cfg)
        cfg['admin_settings']['server']['auth_key']=authenticated_user_data['AccessToken']
        cfg['admin_settings']['server']['admin_id']=authenticated_user_data['User']['Id']
        #authenticated_user_data=authenticate_user_by_name(admin_username,admin_password,cfg)
        
        #get all existing labelled authentication keys
        labelled_authentication_keys=get_labelled_authentication_keys(authenticated_user_data,cfg)
        #parse for existing authentication keys already labelled MUMC
        mumc_labelled_key=get_MUMC_labelled_authentication_key(labelled_authentication_keys,cfg)
        #if there is an existing key labelled MUMC in the GUI, try to delete it
        if (mumc_labelled_key):
            try:
                #delete existing MUMC key
                delete_labelled_authentication_key(mumc_labelled_key,authenticated_user_data,cfg)
            except:
                pass
        #create authentication key labelled MUMC
        create_labelled_authentication_key(authenticated_user_data,cfg)
        #clear previously cached data from get_labelled_authentication_keys() so the same key data is not returned
        # which would not contain the newly created labelled MUMC key
        cfg['cached_data'].removeCachedEntry(labelled_authentication_keys['request_url'])
        #get all existing labelled authentication keys
        labelled_authentication_keys=get_labelled_authentication_keys(authenticated_user_data,cfg)
        #parse for existing labelled MUMC specific authentication key
        cfg['admin_settings']['server']['auth_key']=get_MUMC_labelled_authentication_key(labelled_authentication_keys,cfg)

        yaml_configurationUpdater(cfg)

        print('The new API key was saved to ' + str(config_file_full_path) + 'as admin_settings > server > auth_key.')
        print('\nAPI Key: ' + str(cfg['admin_settings']['server']['auth_key']))
        sys.exit(0)


#find command and get argument
def findCMD_getArgument(argv,optionsList,the_dict,*queriedcommands):
    if (cmdOption:=findCMDRequest(argv,queriedcommands)):
        if (cmdOption:=findCMDNotLast(cmdOption,argv,the_dict)):
            if (cmdOption:=findNoCMDAfterCMD(cmdOption,argv,optionsList,the_dict)):
                return getCMDArgument(cmdOption,argv)
    else:
        return cmdOption


def convertEnvironmentalVariablesToCMDOptions(argv,envar):
#environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'e725d238c8cc', 'SERVER_ADMIN_ID': 'some other hex value', 'SERVER_URL': 'https://embyfin.com', 'SERVER_AUTH_KEY': 'some  hex  value', 'ADMIN_USERNAME': 'you-and_me', 'TZ': 'America/New_York', 'ADMIN_PASSWORD': '  abc  123  zyx  987  ', 'CONTAINER': 'true', 'CONFIG': '/usr/src/app/config', 'ATTRS': 'False', 'SERVER_BRAND': 'EMBYFIN', 'LANG': 'C.UTF-8', 'GPG_KEY': 'A035C8C19219BA821ECEA86B64E628F8D684696D', 'PYTHON_VERSION': '3.11.11', 'PYTHON_SHA256': '2a9920c7a0cd236de33644ed980a13cbbc21058bfdc528febb6081575ed73be3', 'HOME': '/root'})
#['./mumc.py', '-d']
#['./mumc.py', '-d', '-attrs', 'False', '-config', '/usr/src/app/config', '-server_brand', 'EMBYFIN', '-server_url', 'https://embyfin.com', '-admin_username', 'you-and_me', '-admin_password', '  abc  123  zyx  987  ', '-server_auth_key', 'some  hex  value', '-server_admin_id', 'some other hex value']

    #need to parse to take into account all the ways people can enter/format these commands/environmental variables

    #save container environmental variables
    #save environmental variable - ATTRS,ATTRIBUTES
    if (not (envar.get('ATTRS') == None)):
        if (not ('-attrs' in argv)):
            argv.append('-attrs')
            argv.append(envar['ATTRS'])
    if (not (envar.get('ATTRIBUTES') == None)):
        if (not ('-attributes' in argv)):
            argv.append('-attributes')
            argv.append(envar['ATTRIBUTES'])

    #save environmental variable - CONFIG
    if (not (envar.get('CONFIG') == None)):
        if (not ('-config' in argv)):
            argv.append('-config')
            argv.append(envar['CONFIG'])

    #save environmental variable - SERVER_BRAND
    if (not (envar.get('SERVER_BRAND') == None)):
        if (not ('-server_brand' in argv)):
            argv.append('-server_brand')
            argv.append(envar['SERVER_BRAND'])

    #save environmental variable - SERVER_URL
    if (not (envar.get('SERVER_URL') == None)):
        if (not ('-server_url' in argv)):
            argv.append('-server_url')
            argv.append(envar['SERVER_URL'])

    #save environmental variable - ADMIN_USERNAME
    if (not (envar.get('ADMIN_USERNAME') == None)):
        if (not ('-admin_username' in argv)):
            argv.append('-admin_username')
            argv.append(envar['ADMIN_USERNAME'])

    #save environmental variable - ADMIN_PASSWORD
    if (not (envar.get('ADMIN_PASSWORD') == None)):
        if (not ('-admin_password' in argv)):
            argv.append('-admin_password')
            argv.append(envar['ADMIN_PASSWORD'])

    #save environmental variable - SERVER_AUTH_KEY
    if (not (envar.get('SERVER_AUTH_KEY') == None)):
        if (not ('-server_auth_key' in argv)):
            argv.append('-server_auth_key')
            argv.append(envar['SERVER_AUTH_KEY'])

    #save environmental variable - SERVER_ADMIN_ID
    if (not (envar.get('SERVER_ADMIN_ID') == None)):
        if (not ('-server_admin_id' in argv)):
            argv.append('-server_admin_id')
            argv.append(envar['SERVER_ADMIN_ID'])

    #save environmental variable - LIST_BEHAVIOR
    #save environmental variable - MATCHING_BEHAVIOR
    #save environmental variable - MONITOR_DISABLED_USERS
    #save environmental variable - RADARR_URL
    #save environmental variable - RADARR_API
    #save environmental variable - SONARR_URL
    #save environmental variable - SONARR_API
    #save environmental variable - LIDARR_URL
    #save environmental variable - LIDARR_API
    #save environmental variable - READARR_URL
    #save environmental variable - READARR_API
    return argv


#parse the command line options
def parse_command_line_options(the_dict):

    cmdopt_dict={}
    cmdopt_dict['argv']=the_dict['argv']
    cmdopt_dict['envar']=the_dict['envar']
    cmdopt_dict['containerized']=False
    cmdopt_dict['moduleExtension']=['.yml','.yaml','.py']

    cmdopt_dict['optionsList']=['-a','-attrs','-attributes',
                                '-c','-config',
                                '-d','-container',
                                '-u','-updater','-config_updater','-configuration_updater',
                                #'-rak','-remake-api-key',
                                '-sb','-server_brand',
                                '-su','-server_url',
                                '-au','-admin_username',
                                '-ap','-admin_password',
                                '-sak','-server_auth_key',
                                '-sai','-server_admin_id',
                                '-lb','-list_behavior',
                                '-mb','-matching_behavior',
                                '-mdu','-monitor_disabled_users',
                                #'-ui','-user_ids',
                                #'-un','-user_names',
                                #'-wli','-whitelist_*_lib_ids',
                                #'-bli','-blacklist_*_lib_ids',
                                #'-wct','-whitelist_*_collection_types',
                                #'-bct','-blacklist_*_collection_types',
                                #'-wp','-whitelist_*_paths',
                                #'-pb','-blacklist_*_paths',
                                #'-wnp','-whitelist_*_network_paths',
                                #'-bnp','-blacklist_*_network_paths',
                                #'-wsi','-whitelist_*_subfolder_ids',
                                #'-bsi','-blacklist_*_subfolder_ids',
                                #'-wle','-whitelist_*_libs_enabled',
                                #'-ble','-blacklist_*_libs_enabled',
                                '-ru','-radarr_url',
                                '-ra','-radarr_api',
                                '-su','-sonarr_url',
                                '-sa','-sonarr_api',
                                #'-lu','-lidarr_url',
                                #'-la','-lidarr_api',
                                #'-du','-readarr_url',
                                #'-da','-readarr_api',
                                '-h','-help','-?'
                                ]

    print()
    print(cmdopt_dict['envar'])
    print()
    print('a')
    print()
    print(cmdopt_dict['argv'])
    cmdopt_dict['argv']=convertEnvironmentalVariablesToCMDOptions(cmdopt_dict['argv'],cmdopt_dict['envar'])
    print()
    print('b')
    print()
    print(cmdopt_dict['argv'])
    print()
    sys.exit(0)

    #look for unknown command line options
    findUnknownCMDRequest(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict)

    #look for -h or -help command line option
    if (findCMDRequest(cmdopt_dict['argv'],'-h','-help','-?')):
        print_full_help_menu(the_dict)
        sys.exit(0)

    #look for -a, -attrs, -attributes, -attr, or -attribute command line option
    if (findCMDRequest(cmdopt_dict['argv'],'-a','-attrs','-attributes')):
        console_text_attributes().console_attribute_test()
        sys.exit(0)

    #look for -c or -config command line option and argument
    if (alternatePathInfo:=findAlternateConfigCMDAndArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],cmdopt_dict['moduleExtension'],the_dict,'-c','-config')):
        cmdopt_dict['altConfigPath']=alternatePathInfo[0]
        cmdopt_dict['altConfigFileNoExt']=alternatePathInfo[1]
        cmdopt_dict['altConfigFileExt']=alternatePathInfo[2]
    else:
        cmdopt_dict['altConfigPath']=None
        cmdopt_dict['altConfigFileNoExt']=None
        cmdopt_dict['altConfigFileExt']=None
 
    #look for -d or -container command line option
    cmdopt_dict['containerized']=findCMDRequest(cmdopt_dict['argv'],'-d','-container')

    #look for -u, -updater, -config-updater, or -configuration-updater command line option
    cmdopt_dict['configUpdater']=findCMDRequest(cmdopt_dict['argv'],'-u','-config-updater')

    #look for -sb or -server_brand command line option and argument
    cmdopt_dict['server_brand']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-sb','-server_brand')

    #look for -su or -server_url command line option and argument
    cmdopt_dict['server_url']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-su','-server_url')

    #look for -au or -admin_username command line option and argument
    cmdopt_dict['admin_username']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-au','-admin_username')

    #look for -ap or -admin_password command line option and argument
    cmdopt_dict['admin_password']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-ap','-admin_password')
    
    #look for -sak or -server_auth_key command line option and argument
    cmdopt_dict['server_auth_key']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-sak','-server_auth_key')

    #look for -sai or -server_admin_id command line option and argument
    cmdopt_dict['server_admin_id']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-sai','-server_admin_id')

    #look for -lb or -list_behavior command line option and argument
    cmdopt_dict['list_behavior']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-lb','-list_behavior')

    #look for -mb or -matching_behavior command line option and argument
    cmdopt_dict['matching_behavior']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-mb','-matching_behavior')

    #look for -mdu or -monitor_disabled_users command line option and argument
    cmdopt_dict['monitor_disabled_users']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-mdu','-monitor_disabled_users')

    #look for -mdu or -monitor_disabled_users command line option and argument
    cmdopt_dict['monitor_disabled_users']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-mdu','-monitor_disabled_users')

    #look for -ru or -radarr_url command line option and argument
    cmdopt_dict['radarr_url']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-ru','-radarr_url')

    #look for -ra or -radarr_api command line option and argument
    cmdopt_dict['radarr_api']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-ra','-radarr_api')

    #look for -su or -sonarr_url command line option and argument
    cmdopt_dict['sonarr_url']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-su','-sonarr_url')

    #look for -sa or -sonarr_api command line option and argument
    cmdopt_dict['sonarr_api']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict,'-sa','-sonarr_api')

    return cmdopt_dict