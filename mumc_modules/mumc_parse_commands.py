import os
import sys
import copy
from pathlib import Path
from mumc_modules.mumc_console_info import default_helper_menu,print_full_help_menu,missing_config_argument_format_helper,alt_config_file_does_not_exist_helper,alt_config_syntax_helper,unknown_command_line_option_helper
from mumc_modules.mumc_paths_files import getFullPathName,getFileExtension,doesFileExist,add_to_PATH
from mumc_modules.mumc_console_attributes import console_text_attributes
from mumc_modules.mumc_setup_questions import get_admin_username,get_admin_password
from mumc_modules.mumc_key_authentication import authenticate_user_by_name,get_labelled_authentication_keys,get_MUMC_labelled_authentication_key,create_labelled_authentication_key,delete_labelled_authentication_key
from mumc_modules.mumc_config_updater import yaml_configurationUpdater
from mumc_modules.mumc_config_import import importConfig
from mumc_modules.mumc_yaml_check import cfgCheckYAML


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


#find command
def findCMDRequest(argv,expectedCMD):
    for cmdOption in argv:
        if (cmdOption == expectedCMD):
            return cmdOption
    return False


#verify the -command is not equal to another -command; we are expecting an argument to come after it
def findNoCMDAfterCMD(cmdOption,argv,optionsList,the_dict):
    try:
        if (cmdOption):
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


#verify alternate config file name follows the python module naming convention
def parsePathFileSyntax(argv,file_path,cmdOption,moduleExtension,the_dict):
    try:
        if (file_path):
            argExt=getFileExtension(file_path)
            if ((argExt in moduleExtension) and
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


#find alternate configuration command and argument
def findAlternateConfigCMDAndArgument(argv,optionsList,moduleExtension,the_dict,expectedCMD):
    if (cmdOption:=findCMDRequest(argv,expectedCMD)):
        if (cmdOption:=findNoCMDAfterCMD(cmdOption,argv,optionsList,the_dict)):
            #if(verifyPathFileExist(argv[cmdOption],argv,the_dict)):
                #[argumentPath,argumentFileNoExt,argumentFileExt]=parsePathFileSyntax(argv,argv[cmdOption],cmdOption,moduleExtension,the_dict)
                #return argumentPath,argumentFileNoExt,argumentFileExt
            return Path(argv[cmdOption])
    else:
        return cmdOption


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

    if (doesFileExist(cfg['config_file_path'] / cfg['config_file_name_yaml'])):
        config_file_full_path=cfg['config_file_path'] / cfg['config_file_name_yaml']
    else:
        print('ConfigError: Unable to find valid configuration file.')
        sys.exit(0)
        
    #for cmdOption in argv:
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
        if (cmdOption:=findNoCMDAfterCMD(cmdOption,argv,optionsList,the_dict)):
            return argv[cmdOption]
    else:
        return cmdOption


def convertCMDOptionsToDict(argv,optionsList):
    cmd_dict={}
    argv.pop(0)
    for cmd in argv:
        if ((cmd == '-a') or (cmd == '-attrs') or (cmd == '-attributes') or
            (cmd == '-u') or (cmd == '-config_updater') or
            (cmd == '-h') or (cmd == '-help') or (cmd == '-?')):

            if (((argv.index(cmd) + 1) < len(argv)) and
               (argv[argv.index(cmd) + 1].strip().casefold() == 'false')):
                #check if next list item is boolean
                cmd_dict[convertShortCMDOptionsToLongCMDOptions(cmd)]='false'
            else:
                cmd_dict[convertShortCMDOptionsToLongCMDOptions(cmd)]='true'
        elif (cmd  in optionsList):
            cmd_dict[convertShortCMDOptionsToLongCMDOptions(cmd)]=argv[argv.index(cmd) + 1]

    return cmd_dict


def convertShortCMDOptionsToLongCMDOptions(cmd):

    if (cmd.casefold() == '-c'):
        return '-config'
    elif (cmd.casefold() == '-brand'):
        return '-server_brand'
    elif (cmd.casefold() == '-url'):
        return '-server_url'
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
    elif (cmd.casefold() == '-libsel'):
        return '-user_library_selection'
    elif (cmd.casefold() == '-rdurl'):
        return '-radarr_url'
    elif (cmd.casefold() == '-rdapi'):
        return '-radarr_api_key'
    elif (cmd.casefold() == '-snurl'):
        return '-sonarr_url'
    elif (cmd.casefold() == '-snapi'):
        return '-sonarr_api_key'
    elif ((cmd.casefold() == '-a') or (cmd.casefold() == '-attrs')):
        return '-attributes'
    elif (cmd.casefold() == '-u'):
        return '-config_updater'
    elif ((cmd.casefold() == '-h') or (cmd.casefold() == '-?')):
        return '-help'
    else:
        return cmd.casefold()


#convert container environmental variables into CMD options
def convertEnvironmentalVariablesToCMDOptions(argv,envar):

    #save environmental variable - C,CONFIG
    if (envar.get('C')):
        argv['-config']=envar.get('C')
    if (envar.get('CONFIG')):
        argv['-config']=envar.get('CONFIG')

    #save environmental variable - BRAND,SERVER_BRAND
    if (envar.get('BRAND')):
        argv['-server_brand']=envar.get('BRAND')
    if (envar.get('SERVER_BRAND')):
        argv['-server_brand']=envar.get('SERVER_BRAND')

    #save environmental variable - URL,SERVER_URL
    if (envar.get('URL')):
        argv['-server_url']=envar.get('URL')
    if (envar.get('SERVER_URL')):
        argv['-server_url']=envar.get('SERVER_URL')

    #save environmental variable - USERNAME,ADMIN_USERNAME
    if (envar.get('USERNAME')):
        argv['-admin_username']=envar.get('USERNAME')
    if (envar.get('ADMIN_USERNAME')):
        argv['-admin_username']=envar.get('ADMIN_USERNAME')

    #save environmental variable - PASSWORD,ADMIN_PASSWORD
    if (envar.get('PASSWORD')):
        argv['-admin_password']=envar.get('PASSWORD')
    if (envar.get('ADMIN_PASSWORD')):
        argv['-admin_password']=envar.get('ADMIN_PASSWORD')

    #save environmental variable - AUTHKEY,SERVER_AUTH_KEY
    if (envar.get('AUTHKEY')):
        argv['-server_auth_key']=envar.get('AUTHKEY')
    if (envar.get('SERVER_AUTH_KEY')):
        argv['-server_auth_key']=envar.get('SERVER_AUTH_KEY')

    #save environmental variable - ADMINID,SERVER_ADMIN_ID
    if (envar.get('ADMINID')):
        argv['-server_admin_id']=envar.get('ADMINID')
    if (envar.get('SERVER_ADMIN_ID')):
        argv['-server_admin_id']=envar.get('SERVER_ADMIN_ID')

    #save environmental variable - LSTBEH,LIST_BEHAVIOR
    if ('LSTBEH' in envar):
        argv['-list_behavior']=envar['LSTBEH']
    if ('LIST_BEHAVIOR' in envar):
        argv['-list_behavior']=envar['LIST_BEHAVIOR']

    #save environmental variable - MATBEH,MATCHING_BEHAVIOR
    if ('MATBEH' in envar):
        argv['-matching_behavior']=envar['MATBEH']
    if ('MATCHING_BEHAVIOR' in envar):
        argv['-matching_behavior']=envar['MATCHING_BEHAVIOR']

    #save environmental variable - BLACKTAGS,GLOBAL_BLACKTAGS
    if ('BLACKTAGS' in envar):
        argv['-global_blacktags']=envar['BLACKTAGS']
    if ('GLOBAL_BLACKTAGS' in envar):
        argv['-global_blacktags']=envar['GLOBAL_BLACKTAGS']

    #save environmental variable - WHITETAGS,GLOBAL_WHITETAGS
    if ('WHITETAGS' in envar):
        argv['-global_whitetags']=envar['WHITETAGS']
    if ('GLOBAL_WHITETAGS' in envar):
        argv['-global_whitetags']=envar['GLOBAL_WHITETAGS']

    #save environmental variable - DISUSRS,MONITOR_DISABLED_USERS
    if ('DISUSRS' in envar):
        argv['-monitor_disabled_users']=envar['DISUSRS']
    if ('MONITOR_DISABLED_USERS' in envar):
        argv['-monitor_disabled_users']=envar['MONITOR_DISABLED_USERS']

    #save environmental variable - LIBSEL,USER_LIBRARY_SELECTION
    if ('LIBSEL' in envar):
        argv['-user_library_selection']=envar['LIBSEL']
    if ('USER_LIBRARY_SELECTION' in envar):
        argv['-user_library_selection']=envar['USER_LIBRARY_SELECTION']

    #save environmental variable - RDURL,RADARR_URL
    if ('RDURL' in envar):
        argv['-radarr_url']=envar['RDURL']
    if ('RADARR_URL' in envar):
        argv['-radarr_url']=envar['RADARR_URL']

    #save environmental variable - RDAPI,radarr_api_key
    if ('RDAPI' in envar):
        argv['-radarr_api_key']=envar['RDAPI']
    if ('radarr_api_key' in envar):
        argv['-radarr_api_key']=envar['RADARR_API_KEY']

    #save environmental variable - RDURL,SONARR_URL
    if ('SNURL' in envar):
        argv['-sonarr_url']=envar['SNURL']
    if ('SONARR_URL' in envar):
        argv['-sonarr_url']=envar['SONARR_URL']

    #save environmental variable - SNAPI,sonarr_api_key
    if ('SNAPI' in envar):
        argv['-sonarr_api_key']=envar['SNAPI']
    if ('sonarr_api_key' in envar):
        argv['-sonarr_api_key']=envar['SONARR_API_KEY']

    #save environmental variable - LDURL,LIDARR_URL
    #save environmental variable - LDAPI,LIDARR_API

    #save environmental variable - REURL,READARR_URL
    #save environmental variable - REAPI,READARR_API

    #save environmental variable - A,ATTRS,ATTRIBUTES
    if (envar.get('A')):
        argv['-attributes']=envar.get('A')
    if (envar.get('ATTRS')):
        argv['-attributes']=envar.get('ATTRS')
    if (envar.get('ATTRIBUTES')):
        argv['-attributes']=envar.get('ATTRIBUTES')

    #save environmental variable - U,CONFIG_UPDATER
    if (envar.get('U')):
        argv['-config_updater']=envar.get('U')
    if (envar.get('CONFIG_UPDATER')):
        argv['-config_updater']=envar.get('CONFIG_UPDATER')

    return argv


#remove extra leading dashes, remove leading and trailing spaces, and remove capitalizatoin from command line options
def normalizeCommandLineOptions(argvs,options_list):
    #loop thru command line options
    for argv in argvs:
        #count the number of '-' (dashes) in the string
        dash_count=argv.count('-')
        #force lowercaes; replace "dash_count - 1" number of '-'es (dashes); then check if this new string is in the list of possible command line options
        if ((argv.strip().casefold().replace('-','',dash_count - 1)) in options_list):
            #remove all extra '-'es (dashes); save lowercase command line option with a single '-' (dash)
            argvs[argvs.index(argv)]=argv.strip().casefold().replace('-','',dash_count - 1)

    return argvs


def findAbnormalCommandLineOptions(argvs,options_list):
    #loop thru all arguments
    for argv in reversed(argvs):
        #strip leading/trailer whitespaces and split at '='
        argvEq=argv.strip().split('=',1)
        #strip leading/trailer whitespaces and split at first ' ' (space)
        argvSp=argv.strip().split(' ',1)
        #check if lenght of split list is == 2
        if (len(argvEq) == 2):
            #check if casefolded argv with '-' appended to the beginning is a recognized command line arguement
            if ('-' + str(argvEq[0].casefold().strip()) in options_list):
                #get the index
                argvEqIndex=argvs.index(argv)
                #remove the orginal
                argvs.pop(argvEqIndex)
                #insert argument at position of original
                argvs.insert(argvEqIndex,'-' + str(argvEq[0].casefold()))
                #insert value at position of original + 1
                argvs.insert(argvEqIndex + 1,argvEq[1])
        #check if lenght of split list is == 2
        if (len(argvSp) == 2):
            #check if casefolded argv with '-' appended to the beginning is a recognized command line arguement
            if ('-' + str(argvSp[0].casefold().strip()) in options_list):
                #get the index
                argvSpIndex=argvs.index(argv)
                #remove the orginal
                argvs.pop(argvSpIndex)
                #insert argument at position of original
                argvs.insert(argvSpIndex,'-' + str(argvSp[0].casefold()))
                #insert value at position of original + 1
                argvs.insert(argvSpIndex + 1,argvSp[1])
        #check it argv is docker's -e
        if (argv == '-e'):
            #get the index
            argv_EIndex=argvs.index(argv)
            #remove -e from dictionary
            argvs.pop(argv_EIndex)

    #loop thru all arguments; intent is to find arguements formatted like this (arg value) instead of like this (arg=value)
    for argv in argvs:
        #check if this argument is recognized after removing leading and trailing whitespace and appending '-' to the beginning
        if ('-' + str(argv.casefold().strip()) in options_list):
            #get the index
            argvIndex=argvs.index(argv)
            #append '-' to the beginning of the original arguement and save
            argvs[argvIndex]='-' + str(argv.casefold().strip())

    return argvs

#parse the command line options
def parse_command_line_options(the_dict):

    cmdopt_dict={}
    cmdopt_dict['argv']={}
    cmdopt_dict['envar']=the_dict['envar']
    cmdopt_dict['moduleExtension']=['.yaml','.yml','.py']

    cmdopt_dict['optionsList']=['-c','-config',
                                '-brand','-server_brand',
                                '-url','-server_url',
                                '-admin_username', #do not use '-username' as this could be a common username
                                '-admin_password', #do not use '-password' as this could be a common password
                                '-authkey','-server_auth_key',
                                '-adminid','-server_admin_id',
                                '-lstbeh','-list_behavior',
                                '-matbeh','-matching_behavior',
                                '-blacktags','-global_blacktags',
                                '-whitetags','-global_whitetags',
                                '-disusrs','-monitor_disabled_users',
                                '-libsel','-user_library_selection',
                                '-rdurl','-radarr_url',
                                '-rdapi','-radarr_api_key',
                                '-snurl','-sonarr_url',
                                '-snapi','-sonarr_api_key',
                                #'-ldurl','-lidarr_url',
                                #'-ldapi','-lidarr_api',
                                #'-reurl','-readarr_url',
                                #'-reapi','-readarr_api',
                                '-a','-attrs','-attributes',
                                '-u','-config_updater',
                                #'-rak','-remake-api-key',
                                '-h','-help','-?'
                                ]

    the_dict['argv']=findAbnormalCommandLineOptions(the_dict['argv'],cmdopt_dict['optionsList'])

    #normalize by removing too many leading '-'es (dashes), leading and trailing spaces, and forcing lowercase
    the_dict['argv']=normalizeCommandLineOptions(the_dict['argv'],cmdopt_dict['optionsList'])

    #first covert environmental variables to command line arguements; environamental variables have a lower priority
    cmdopt_dict['argv']|=convertEnvironmentalVariablesToCMDOptions(cmdopt_dict['argv'],cmdopt_dict['envar'])

    #second convert command line argument list into dictionary; overwriting environmental variables; command line arguments have a higher priority
    cmdopt_dict['argv']|=convertCMDOptionsToDict(the_dict['argv'],cmdopt_dict['optionsList'])

    #everything is string up to this point
    #normalize all 'true'/'false' strings as booleans
    #normalize all '#' as intergers
    #normalize blacktag/whitetag blank string '' to empty list []; remove leading/trailing spaces
    for cmd in cmdopt_dict['argv']:
        #if string version of True; convert to boolean
        if (cmdopt_dict['argv'][cmd].casefold() == 'true'):
            cmdopt_dict['argv'][cmd]=True
        #if string version of False; convert to boolean
        elif (cmdopt_dict['argv'][cmd].casefold() == 'false'):
            cmdopt_dict['argv'][cmd]=False
        #if -global_blacktags or -global_whitetags
        elif ((cmd == '-global_blacktags') or (cmd == '-global_whitetags')):
            #check if ''
            if (cmdopt_dict['argv'][cmd].strip() == ''):
                #save as empty list
                cmdopt_dict['argv'][cmd]=[]
            #check if after removing leading and trailing whitespaces if equal to ''
            elif (cmdopt_dict['argv'][cmd].strip() == ''):
                #save as empty list
                cmdopt_dict['argv'][cmd]=[]
            #check if an empty list with leading, trailing, and/or middle whitespaces
            elif ((cmdopt_dict['argv'][cmd].count(' ') + cmdopt_dict['argv'][cmd].count('[') + cmdopt_dict['argv'][cmd].count(']')) == len(cmdopt_dict['argv'][cmd])):
                #save as empty list
                cmdopt_dict['argv'][cmd]=[]
            else:
                #split into list at the commas
                cmdopt_dict['argv'][cmd]=cmdopt_dict['argv'][cmd].split(',')
                #loop thru list
                for item in cmdopt_dict['argv'][cmd]:
                    #strip leading and trailing whitespaces
                    cmdopt_dict['argv'][cmd][cmdopt_dict['argv'][cmd].index(item)]=item.strip()
                for item in cmdopt_dict['argv'][cmd][:]:
                    if (not(item.strip())):
                        cmdopt_dict['argv'][cmd].remove(item)
        else:
            try:
                #try converting to integer
                cmdopt_dict['argv'][cmd]=int(cmdopt_dict['argv'][cmd])
            except:
                pass

    #look for unknown command line options
    findUnknownCMDRequest(cmdopt_dict['argv'],cmdopt_dict['optionsList'],the_dict)

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

    return cmdopt_dict


def get_config_location(cmdopt_dict,the_dict):
    #look for -c or -attributesconfig command line option and argument
    if (alternatePathInfo:=findAlternateConfigCMDAndArgument(cmdopt_dict['argv'],cmdopt_dict['optionsList'],cmdopt_dict['moduleExtension'],the_dict,'-config')):
        cmdopt_dict['config_file_path']=alternatePathInfo.parent
        cmdopt_dict['config_file_name_yaml']=alternatePathInfo.name
        cmdopt_dict['config_file_name_yml']=alternatePathInfo.name
        cmdopt_dict['config_file_name_no_ext']=alternatePathInfo.stem
    else:
        cmdopt_dict['config_file_path']=the_dict['script_file_path'] / 'config'
        cmdopt_dict['config_file_name_yaml']='mumc_config.yaml'
        cmdopt_dict['config_file_name_yml']='mumc_config.yml'
        cmdopt_dict['config_file_name_no_ext']='mumc_config'

    add_to_PATH(cmdopt_dict['config_file_path'],2)

    return cmdopt_dict