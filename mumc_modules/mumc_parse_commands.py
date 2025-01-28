import os
import sys
import copy
from pathlib import Path
from mumc_modules.mumc_console_info import default_helper_menu,print_full_help_menu,missing_config_argument_helper,missing_config_argument_format_helper,alt_config_file_does_not_exist_helper,alt_config_syntax_helper,unknown_command_line_option_helper
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
        alt_config_file_does_not_exist_helper(argv,the_dict)
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
            if(verifyPathFileExist(argv[cmdOption],argv,the_dict)):
                [argumentPath,argumentFileNoExt,argumentFileExt]=parsePathFileSyntax(argv,argv[cmdOption],cmdOption,moduleExtension,the_dict)
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
    if (envar.get('A')):
        argv['-attributes']=envar.get('A')
    if (envar.get('ATTRS')):
        argv['-attributes']=envar.get('ATTRS')
    if (envar.get('ATTRIBUTES')):
        argv['-attributes']=envar.get('ATTRIBUTES')

    #save environmental variable - C,CONFIG
    #if (not ('-config' in argv)):
    if (envar.get('C')):
        argv['-config']=envar.get('C')
    if (envar.get('CONFIG')):
        argv['-config']=envar.get('CONFIG')

    #save environmental variable - D,CONTAINER
    #if (not ('-container' in argv)):
    if (envar.get('D')):
        argv['-container']=envar.get('D')
    if (envar.get('CONTAINER')):
        argv['-container']=envar.get('CONTAINER')

    #save environmental variable - U,CONFIG_UPDATER
    #if (not ('-config_updater' in argv)):
    if (envar.get('U')):
        argv['-config_updater']=envar.get('U')
    if (envar.get('CONFIG_UPDATER')):
        argv['-config_updater']=envar.get('CONFIG_UPDATER')

    #save environmental variable - BRAND,SERVER_BRAND
    #if (not ('-server_brand' in argv)):
    if (envar.get('BRAND')):
        argv['-server_brand']=envar.get('BRAND')
    if (envar.get('SERVER_BRAND')):
        argv['-server_brand']=envar.get('SERVER_BRAND')

    #save environmental variable - URL,SERVER_URL
    #if (not ('-server_url' in argv)):
    if (envar.get('URL')):
        argv['-server_url']=envar.get('URL')
    if (envar.get('SERVER_URL')):
        argv['-server_url']=envar.get('SERVER_URL')

    #save environmental variable - PORT,SERVER_PORT
    #if (not ('-server_port' in argv)):
    if (envar.get('PORT')):
        argv['-server_port']=envar.get('PORT')
    if (envar.get('SERVER_PORT')):
        argv['-server_port']=envar.get('SERVER_PORT')

    #save environmental variable - BASE,SERVER_BASE_URL
    #if (not ('-server_base_url' in argv)):
    if (envar.get('BASE')):
        argv['-server_base_url']=envar.ge('BASE')
    if (envar.get('SERVER_BASE_URL')):
        argv['-server_base_url']=envar.get('SERVER_BASE_URL')

    #save environmental variable - USERNAME,ADMIN_USERNAME
    #if (not ('-admin_username' in argv)):
    if (envar.get('USERNAME')):
        argv['-admin_username']=envar.get('USERNAME')
    if (envar.get('ADMIN_USERNAME')):
        argv['-admin_username']=envar.get('ADMIN_USERNAME')

    #save environmental variable - PASSWORD,ADMIN_PASSWORD
    #if (not ('-admin_password' in argv)):
    if (envar.get('PASSWORD')):
        argv['-admin_password']=envar.get('PASSWORD')
    if (envar.get('ADMIN_PASSWORD')):
        argv['-admin_password']=envar.get('ADMIN_PASSWORD')

    #save environmental variable - AUTHKEY,SERVER_AUTH_KEY
    #if (not ('-server_auth_key' in argv)):
    if (envar.get('AUTHKEY')):
        argv['-server_auth_key']=envar.get('AUTHKEY')
    if (envar.get('SERVER_AUTH_KEY')):
        argv['-server_auth_key']=envar.get('SERVER_AUTH_KEY')

    #save environmental variable - ADMINID,SERVER_ADMIN_ID
    #if (not ('-server_admin_id' in argv)):
    if (envar.get('ADMINID')):
        argv['-server_admin_id']=envar.get('ADMINID')
    if (envar.get('SERVER_ADMIN_ID')):
        argv['-server_admin_id']=envar.get('SERVER_ADMIN_ID')

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
    #cmdopt_dict['containerized']=False
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
    cmdopt_dict['argv']|=convertEnvironmentalVariablesToCMDOptions(cmdopt_dict['argv'],cmdopt_dict['envar'])

    #second convert command line argument list into dictionary; overwriting environmental variables; command line arguments have a higher priority
    cmdopt_dict['argv']|=convertCMDOptionsToDict(the_dict['argv'],cmdopt_dict['optionsList'])

    #normalize all 'true'/'false' strings as booleans
    #normalize all '#' as intergers
    for cmd in cmdopt_dict['argv']:
        if (cmdopt_dict['argv'][cmd].casefold() == 'true'):
            cmdopt_dict['argv'][cmd]=True
        elif (cmdopt_dict['argv'][cmd].casefold() == 'false'):
            cmdopt_dict['argv'][cmd]=False
        else:
            try:
                cmdopt_dict['argv'][cmd]=int(cmdopt_dict['argv'][cmd])
            except:
                pass

    #look for unknown command line options
    findUnknownCMDRequest(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict)

    #cmdopt_dict['containerized']=cmdopt_dict['argv']['-container']
    #cmdopt_dict['configUpdater']=cmdopt_dict['argv']['-config_updater']

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

    #if -config not input as a command line option or environmental variable
    #and we are running as a docker container
    #then set the default config location: '/usr/src/app/config/mumc_config.yaml'
    if ((not ('-config' in cmdopt_dict['argv'])) and
       ('-container' in cmdopt_dict['argv']) and
       (cmdopt_dict['argv']['-container'])):
        cmdopt_dict['argv']['-config']='/usr/src/app/config/mumc_config.yaml'

    #look for -c or -attributesconfig command line option and argument
    if (alternatePathInfo:=findAlternateConfigCMDAndArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],cmdopt_dict['moduleExtension'],the_dict,'-config')):
        cmdopt_dict['altConfigPath']=alternatePathInfo[0]
        cmdopt_dict['altConfigFileNoExt']=alternatePathInfo[1]
        cmdopt_dict['altConfigFileExt']=alternatePathInfo[2]
    else:
        cmdopt_dict['altConfigPath']=None
        cmdopt_dict['altConfigFileNoExt']=None
        cmdopt_dict['altConfigFileExt']=None

    return cmdopt_dict