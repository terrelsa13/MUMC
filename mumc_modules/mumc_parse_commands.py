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
def findCMDRequest(argv,expectedCMD):
    for cmdOption in argv:
        #if ((cmdOption.casefold() == '-sb') or (cmdOption.casefold() == '-server_brand')):
        if (cmdOption == expectedCMD):
            return cmdOption
    return False


#verify the -command is not the last item; we are expecting a argument to come after it
#def findCMDNotLast(cmdOption,argv,the_dict):
    #try:
        #if (cmdOption):
            ##for checkOption in argv:
            #if ((argv.index(cmdOption) + 1) >= len(argv)):
                #raise CMDOptionIndexError
            #else:
                #return cmdOption.casefold()
        #else:
            #raise CMDOptionMissingIndexError
    #except (CMDOptionIndexError,CMDOptionMissingIndexError):
        #missing_config_argument_helper(argv,the_dict)
        #default_helper_menu(the_dict)
        #sys.exit(0)


#verify the -command is not equal to another -command; we are expecting an argument to come after it
def findNoCMDAfterCMD(cmdOption,argv,optionsList,the_dict):
    try:
        if (cmdOption):
            #for checkOption in optionsList:
            if (argv[cmdOption] in optionsList):
                raise CMDArgumentError
            else:
                return cmdOption
        else:
            raise CMDMissingArgumentError
    except (CMDArgumentError,CMDMissingArgumentError):
        missing_config_argument_format_helper(argv,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)


#get the argument related to this -command
def getCMDArgument(cmdOption,argv):
    if (cmdOption):
        return argv[cmdOption]
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
                argPath=Path(os.path.dirname(file_path))
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
def findAlternateConfigCMDAndArgument(argv,optionsList,moduleExtension,the_dict,expectedCMD):
    if (cmdOption:=findCMDRequest(argv,expectedCMD)):
        #if (cmdOption:=findCMDNotLast(cmdOption,argv,the_dict)):
        if (cmdOption:=findNoCMDAfterCMD(cmdOption,argv,optionsList,the_dict)):
            #if (cmdArgument:=getCMDArgument(cmdOption,argv)):
            cmdArgument=argv[cmdOption]
            if(verifyPathFileExist(cmdArgument,argv,the_dict)):
                [argumentPath,argumentFileNoExt,argumentFileExt]=parsePathFileSyntax(argv,cmdArgument,cmdOption,moduleExtension,the_dict)
                return argumentPath,argumentFileNoExt,argumentFileExt
            #else:
                #return cmdArgument
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
def findCMD_getArgument(argv,optionsList,expectedCMD,the_dict):
    if (cmdOption:=findCMDRequest(argv,expectedCMD)):
        #if (cmdOption:=findCMDNotLast(cmdOption,argv,the_dict)):
        if (cmdOption:=findNoCMDAfterCMD(cmdOption,argv,optionsList,the_dict)):
            #return getCMDArgument(cmdOption,argv)
            return argv[cmdOption]
    else:
        return cmdOption


def convertCMDOptionsToDict(argv,optionsList):
    cmd_dict={}
    argv.pop(0)
    for cmd in argv:
        if ((cmd == '-a') or (cmd == '-attrs') or (cmd == '-attributes') or
            (cmd == '-d') or (cmd == '-container') or
            (cmd == '-u') or (cmd == '-config_updater') or
            (cmd == '-h') or (cmd == '-help') or (cmd == '-?') or
            (cmd == '--h') or (cmd == '--help') or (cmd == '--?')):

            if (((argv.index(cmd) + 1) < len(argv)) and
               (argv[argv.index(cmd) + 1].strip().casefold() == 'false')):
                #check if next list item is boolean
                #if (argv[argv.index(cmd) + 1].strip().casefold() == 'false'):
                cmd_dict[convertShortCMDOptionsToLongCMDOptions(cmd)]='false'
                #else:
                #cmd_dict[cmd.replace('-','')]='True'
            else:
                cmd_dict[convertShortCMDOptionsToLongCMDOptions(cmd)]='true'
        elif (cmd  in optionsList):
            cmd_dict[convertShortCMDOptionsToLongCMDOptions(cmd)]=argv[argv.index(cmd) + 1]

    return cmd_dict


def convertShortCMDOptionsToLongCMDOptions(cmd):
    if ((cmd.casefold() == '-a') or (cmd.casefold() == '-attrs')):
        return '-attributes'
    elif (cmd.casefold() == '-c'):
        return '-config'
    elif (cmd.casefold() == '-d'):
        return '-container'
    elif (cmd.casefold() == '-u'):
        return '-config_updater'
    elif (cmd.casefold() == '-brand'):
        return '-server_brand'
    elif (cmd.casefold() == '-url'):
        return '-server_url'
    elif (cmd.casefold() == '-port'):
        return '-server_port'
    elif (cmd.casefold() == '-base'):
        return '-server_base_url'
    elif (cmd.casefold() == '-username'):
        return '-admin_username'
    elif (cmd.casefold() == '-password'):
        return '-admin_password'
    elif (cmd.casefold() == '-authkey'):
        return '-server_auth_key'
    elif (cmd.casefold() == '-adminid'):
        return '-server_admin_id'
    elif (cmd.casefold() == '-lstbeh'):
        return '-list_behavior'
    elif (cmd.casefold() == '-matbeh'):
        return '-matching_behavior'
    elif (cmd.casefold() == '-blacktags'):
        return '-global_blacktags'
    elif (cmd.casefold() == '-whitetags'):
        return '-global_whitetags'
    elif (cmd.casefold() == '-disusrs'):
        return '-monitor_disabled_users'
    elif (cmd.casefold() == '-rdurl'):
        return '-radarr_url'
    elif (cmd.casefold() == '-rdprt'):
        return '-radarr_port'
    elif (cmd.casefold() == '-rdapi'):
        return '-radarr_api'
    elif (cmd.casefold() == '-snurl'):
        return '-sonarr_url'
    elif (cmd.casefold() == '-snprt'):
        return '-sonarr_port'
    elif (cmd.casefold() == '-snapi'):
        return '-sonarr_api'
    elif ((cmd.casefold() == '-h') or (cmd.casefold() == '-?') or (cmd.casefold() == '--h') or (cmd.casefold() == '--help') or (cmd.casefold() == '--?')):
        return '-help'
    else:
        return cmd.casefold()


#convert container environmental variables into CMD options
def convertEnvironmentalVariablesToCMDOptions(argv,envar):
    #save environmental variable - A,ATTRS,ATTRIBUTES
    #if (not ('-attributes' in argv)):
    if ('A' in envar):
        argv['-attributes']=envar['A']
    if ('ATTRS' in envar):
        argv['-attributes']=envar['ATTRS']
    if ('ATTRIBUTES' in envar):
        argv['-attributes']=envar['ATTRIBUTES']

    #save environmental variable - C,CONFIG
    #if (not ('-config' in argv)):
    if ('C' in envar):
        argv['-config']=envar['C']
    if ('CONFIG' in envar):
        argv['-config']=envar['CONFIG']

    #save environmental variable - D,CONTAINER
    #if (not ('-container' in argv)):
    if ('D' in envar):
        argv['-container']=envar['D']
    if ('CONTAINER' in envar):
        argv['-container']=envar['CONTAINER']

    #save environmental variable - U,CONFIG_UPDATER
    #if (not ('-config_updater' in argv)):
    if ('U' in envar):
        argv['-config_updater']=envar['U']
    if ('CONFIG_UPDATER' in envar):
        argv['-config_updater']=envar['CONFIG_UPDATER']

    #save environmental variable - BRAND,SERVER_BRAND
    #if (not ('-server_brand' in argv)):
    if ('BRAND' in envar):
        argv['-server_brand']=envar['BRAND']
    if ('SERVER_BRAND' in envar):
        argv['-server_brand']=envar['SERVER_BRAND']

    #save environmental variable - URL,SERVER_URL
    #if (not ('-server_url' in argv)):
    if ('URL' in envar):
        argv['-server_url']=envar['URL']
    if ('SERVER_URL' in envar):
        argv['-server_url']=envar['SERVER_URL']

    #save environmental variable - PORT,SERVER_PORT
    #if (not ('-server_port' in argv)):
    if ('PORT' in envar):
        argv['-server_port']=envar['PORT']
    if ('SERVER_PORT' in envar):
        argv['-server_port']=envar['SERVER_PORT']

    #save environmental variable - BASE,SERVER_BASE_URL
    #if (not ('-server_base_url' in argv)):
    if ('BASE' in envar):
        argv['-server_base_url']=envar['BASE']
    if ('SERVER_BASE_URL' in envar):
        argv['-server_base_url']=envar['SERVER_BASE_URL']

    #save environmental variable - USERNAME,ADMIN_USERNAME
    #if (not ('-admin_username' in argv)):
    if ('USERNAME' in envar):
        argv['-admin_username']=envar['USERNAME']
    if ('SERVER_BASE_URL' in envar):
        argv['-admin_username']=envar['ADMIN_USERNAME']

    #save environmental variable - PASSWORD,ADMIN_PASSWORD
    #if (not ('-admin_password' in argv)):
    if ('PASSWORD' in envar):
        argv['-admin_password']=envar['PASSWORD']
    if ('ADMIN_PASSWORD' in envar):
        argv['-admin_password']=envar['ADMIN_PASSWORD']

    #save environmental variable - AUTHKEY,SERVER_AUTH_KEY
    #if (not ('-server_auth_key' in argv)):
    if ('AUTHKEY' in envar):
        argv['-server_auth_key']=envar['AUTHKEY']
    if ('SERVER_AUTH_KEY' in envar):
        argv['-server_auth_key']=envar['SERVER_AUTH_KEY']

    #save environmental variable - ADMINID,SERVER_ADMIN_ID
    #if (not ('-server_admin_id' in argv)):
    if ('ADMINID' in envar):
        argv['-server_admin_id']=envar['ADMINID']
    if ('SERVER_ADMIN_ID' in envar):
        argv['-server_admin_id']=envar['SERVER_ADMIN_ID']

    #save environmental variable - LSTBEH,LIST_BEHAVIOR
    #if (not ('-list_behavior' in argv)):
    if ('LSTBEH' in envar):
        argv['-list_behavior']=envar['LSTBEH']
    if ('LIST_BEHAVIOR' in envar):
        argv['-list_behavior']=envar['LIST_BEHAVIOR']

    #save environmental variable - MATBEH,MATCHING_BEHAVIOR
    #if (not ('-matching_behavior' in argv)):
    if ('MATBEH' in envar):
        argv['-matching_behavior']=envar['MATBEH']
    if ('MATCHING_BEHAVIOR' in envar):
        argv['-matching_behavior']=envar['MATCHING_BEHAVIOR']

    #save environmental variable - BLACKTAGS,GLOBAL_BLACKTAGS
    #if (not ('-global_blacktags' in argv)):
    if ('BLACKTAGS' in envar):
        argv['-global_blacktags']=envar['BLACKTAGS']
    if ('GLOBAL_BLACKTAGS' in envar):
        argv['-global_blacktags']=envar['GLOBAL_BLACKTAGS']

    #save environmental variable - WHITETAGS,GLOBAL_WHITETAGS
    #if (not ('-global_whitetags' in argv)):
    if ('WHITETAGS' in envar):
        argv['-global_whitetags']=envar['WHITETAGS']
    if ('GLOBAL_WHITETAGS' in envar):
        argv['-global_whitetags']=envar['GLOBAL_WHITETAGS']

    #save environmental variable - DISUSRS,MONITOR_DISABLED_USERS
    #if (not ('-monitor_disabled_users' in argv)):
    if ('DISUSRS' in envar):
        argv['-monitor_disabled_users']=envar['DISUSRS']
    if ('MONITOR_DISABLED_USERS' in envar):
        argv['-monitor_disabled_users']=envar['MONITOR_DISABLED_USERS']

    #save environmental variable - LIBSEL,USER_LIBRARY_SELECTION
    #if (not ('-library_selection' in argv)):
    #if ('LIBSEL' in envar):
        #argv['-library_selection']=envar['LIBSEL']
    #if ('USER_LIBRARY_SELECTION' in envar):
        #argv['-library_selection']=envar['USER_LIBRARY_SELECTION']

    #save environmental variable - RDURL,RADARR_URL
    #if (not ('-radarr_url' in argv)):
    if ('RDURL' in envar):
        argv['-radarr_url']=envar['RDURL']
    if ('RADARR_URL' in envar):
        argv['-radarr_url']=envar['RADARR_URL']

    #save environmental variable - RDPRT,RADARR_PORT
    #if (not ('-radarr_port' in argv)):
    if ('RDPRT' in envar):
        argv['-radarr_port']=envar['RDPRT']
    if ('RADARR_PORT' in envar):
        argv['-radarr_port']=envar['RADARR_PORT']

    #save environmental variable - RDAPI,RADARR_API
    #if (not ('-radarr_api' in argv)):
    if ('RDAPI' in envar):
        argv['-radarr_api']=envar['RDAPI']
    if ('RADARR_API' in envar):
        argv['-radarr_api']=envar['RADARR_API']

    #save environmental variable - SNURL,SONARR_URL
    #if (not ('-sonarr_url' in argv)):
    if ('SNURL' in envar):
        argv['-sonarr_url']=envar['SNURL']
    if ('SONARR_URL' in envar):
        argv['-sonarr_url']=envar['SONARR_URL']

    #save environmental variable - SNPrT,SONARR_PORT
    #if (not ('-sonarr_port' in argv)):
    if ('SNPRT' in envar):
        argv['-sonarr_port']=envar['SNPRT']
    if ('SONARR_PORT' in envar):
        argv['-sonarr_port']=envar['SONARR_PORT']

    #save environmental variable - SNAPI,SONARR_API
    #if (not ('-sonarr_api' in argv)):
    if ('SNAPI' in envar):
        argv['-sonarr_api']=envar['SNAPI']
    if ('SONARR_API' in envar):
        argv['-sonarr_api']=envar['SONARR_API']

    #save environmental variable - LDURL,LIDARR_URL
    #save environmental variable - LDPRT,LIDARR_PORT
    #save environmental variable - LDAPI,LIDARR_API
    #save environmental variable - REURL,READARR_URL
    #save environmental variable - REPRT,READARR_PORT
    #save environmental variable - REAPI,READARR_API

    return argv


#parse the command line options
def parse_command_line_options(the_dict):

    cmdopt_dict={}
    cmdopt_dict['argv']={}
    cmdopt_dict['envar']=the_dict['envar']
    cmdopt_dict['containerized']=False
    cmdopt_dict['moduleExtension']=['.yml','.yaml','.py']

    cmdopt_dict['optionsList']=['-a','-attrs','-attributes',
                                '-c','-config',
                                '-d','-container',
                                '-u','-config_updater',
                                #'-rak','-remake-api-key',
                                '-brand','-server_brand',
                                '-url','-server_url',
                                '-port','-server_port',
                                '-base','-server_base_url',
                                '-username','-admin_username',
                                '-password','-admin_password',
                                '-authkey','-server_auth_key',
                                '-adminid','-server_admin_id',
                                '-lstbeh','-list_behavior',
                                '-matbeh','-matching_behavior',
                                '-blacktags','-global_blacktags',
                                '-whitetags','-global_whitetags',
                                '-disusrs','-monitor_disabled_users',
                                '-libsel','-user_library_selection',
                                #'-uids','-user_ids',
                                #'-unames','-user_names',
                                #'-wlids','-whitelist_*_lib_ids',
                                #'-blids','-blacklist_*_lib_ids',
                                #'-wlctyps','-whitelist_*_collection_types',
                                #'-blctyps','-blacklist_*_collection_types',
                                #'-wlpths','-whitelist_*_paths',
                                #'-blpths','-blacklist_*_paths',
                                #'-wlnetpths','-whitelist_*_network_paths',
                                #'-blnetpths','-blacklist_*_network_paths',
                                #'-wlsids','-whitelist_*_subfolder_ids',
                                #'-blsids','-blacklist_*_subfolder_ids',
                                #'-wlen','-whitelist_*_libs_enabled',
                                #'-blen','-blacklist_*_libs_enabled',
                                '-rdurl','-radarr_url',
                                '-rdprt','-radarr_port',
                                '-rdapi','-radarr_api',
                                '-snurl','-sonarr_url',
                                '-snprt','-sonarr_port',
                                '-snapi','-sonarr_api',
                                #'-ldurl','-lidarr_url',
                                #'-ldprt','-lidarr_port',
                                #'-ldapi','-lidarr_api',
                                #'-reurl','-readarr_url',
                                #'-reprt','-readarr_port',
                                #'-reapi','-readarr_api',
                                '-h','-help','-?','--h','--help','--?'
                                ]

    #first covert environmental variables to command line arguements; environamental variables have a lower priority
    cmdopt_dict['argv']=convertEnvironmentalVariablesToCMDOptions(cmdopt_dict['argv'],cmdopt_dict['envar'])
    print('print argv after converting envar to argv\n')
    print(cmdopt_dict['argv'])
    print('\n')
    #second convert command line argument list into dictionary; overwriting environmental variables; command line arguments have a higher priority
    cmdopt_dict['argv']|=convertCMDOptionsToDict(the_dict['argv'],cmdopt_dict['optionsList'])
    print('print argv after converting argv to dictionary\n')
    print(cmdopt_dict['argv'])
    print('\n')

    #cmdopt_dict['argv']=convertEnvironmentalVariablesToCMDOptions(cmdopt_dict['argv'],cmdopt_dict['envar'])

    #look for unknown command line options
    findUnknownCMDRequest(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict)

    cmdopt_dict['containerized']=cmdopt_dict['argv']['-container']
    cmdopt_dict['configUpdater']=cmdopt_dict['argv']['-config_updater']

    #look for -h or -help command line option
    if (cmdOption:=findCMDRequest(cmdopt_dict['argv'],'-help')):
        if (cmdopt_dict['argv'][cmdOption]):
            print_full_help_menu(the_dict)
            sys.exit(0)

    #look for -a, -attrs, -attributes, -attr, or -attribute command line option
    if (cmdOption:=findCMDRequest(cmdopt_dict['argv'],'-attributes')):
        if (cmdopt_dict['argv'][cmdOption]):
            console_text_attributes().console_attribute_test()
            sys.exit(0)

    #look for -c or -attributesconfig command line option and argument
    if (alternatePathInfo:=findAlternateConfigCMDAndArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],cmdopt_dict['moduleExtension'],the_dict,'-config')):
        cmdopt_dict['altConfigPath']=alternatePathInfo[0]
        cmdopt_dict['altConfigFileNoExt']=alternatePathInfo[1]
        cmdopt_dict['altConfigFileExt']=alternatePathInfo[2]
    else:
        cmdopt_dict['altConfigPath']=None
        cmdopt_dict['altConfigFileNoExt']=None
        cmdopt_dict['altConfigFileExt']=None

    '''
    #look for -d or -container command line option
    cmdopt_dict['argv']['containerized']=findCMDRequest(cmdopt_dict['argv'],'-container')

    #look for -u, -config_updater, or -config_updater command line option
    cmdopt_dict['argv']['configUpdater']=findCMDRequest(cmdopt_dict['argv'],'-config_updater')

    #look for -sb or -server_brand command line option and argument
    cmdopt_dict['argv']['server_brand']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-server_brand',the_dict)

    #look for -su or -server_url command line option and argument
    cmdopt_dict['argv']['server_url']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-server_url',the_dict)

    #look for -sp or -server_port command line option and argument
    cmdopt_dict['argv']['server_port']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-server_port',the_dict)

    #look for -sbu or -server_base_url command line option and argument
    cmdopt_dict['argv']['server_base_url']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-server_base_url',the_dict)

    #look for -au or -admin_username command line option and argument
    cmdopt_dict['argv']['admin_username']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-admin_username',the_dict)

    #look for -ap or -admin_password command line option and argument
    cmdopt_dict['argv']['admin_password']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-admin_password',the_dict)
    
    #look for -sak or -server_auth_key command line option and argument
    cmdopt_dict['argv']['server_auth_key']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-server_auth_key',the_dict)

    #look for -sai or -server_admin_id command line option and argument
    cmdopt_dict['argv']['server_admin_id']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-server_admin_id',the_dict)

    #look for -lb or -list_behavior command line option and argument
    cmdopt_dict['argv']['list_behavior']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-list_behavior',the_dict)

    #look for -mb or -matching_behavior command line option and argument
    cmdopt_dict['argv']['matching_behavior']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-matching_behavior',the_dict)

    #look for -gb or -global_blacktags command line option and argument
    cmdopt_dict['argv']['global_blacktags']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-global_blacktags',the_dict)

    #look for -gb or -global_whitetags command line option and argument
    cmdopt_dict['argv']['global_whitetags']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-global_whitetags',the_dict)

    #look for -mdu or -monitor_disabled_users command line option and argument
    cmdopt_dict['argv']['monitor_disabled_users']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-monitor_disabled_users',the_dict)

    #look for -uls or -user_library_selection command line option and argument
    cmdopt_dict['argv']['user_library_selection']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-user_library_selection',the_dict)

    #look for -ru or -radarr_url command line option and argument
    cmdopt_dict['argv']['radarr_url']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-radarr_url',the_dict)

    #look for -ru or -radarr_port command line option and argument
    cmdopt_dict['argv']['radarr_port']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-radarr_port',the_dict)

    #look for -ra or -radarr_api command line option and argument
    cmdopt_dict['argv']['radarr_api']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-radarr_api',the_dict)

    #look for -nu or -sonarr_url command line option and argument
    cmdopt_dict['argv']['sonarr_url']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-sonarr_url',the_dict)

    #look for -np or -sonarr_port command line option and argument
    cmdopt_dict['argv']['sonarr_port']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-sonarr_port',the_dict)

    #look for -sa or -sonarr_api command line option and argument
    cmdopt_dict['argv']['sonarr_api']=findCMD_getArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],'-sonarr_api',the_dict)
    '''

    return cmdopt_dict