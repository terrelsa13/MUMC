import os
import sys
import copy
from pathlib import Path
from mumc_modules.mumc_console_info import default_helper_menu,print_full_help_menu,missing_config_argument_helper,missing_config_argument_format_helper,alt_config_file_does_not_exists_helper,alt_config_syntax_helper,unknown_command_line_option_helper
from mumc_modules.mumc_paths import getFullPathName,getFileExtension,doesFileExist
from mumc_modules.mumc_console_attributes import console_text_attributes
from mumc_modules.mumc_setup_questions import get_admin_username,get_admin_password
from mumc_modules.mumc_key_authentication import authenticate_user_by_name,get_labelled_authentication_keys,get_MUMC_labelled_authentication_key,create_labelled_authentication_key,delete_labelled_authentication_key
from mumc_modules.mumc_config_updater import yaml_configurationUpdater
from mumc_modules.mumc_config_import import importConfig
from mumc_modules.mumc_yaml_check import cfgCheckYAML

#define custom exception
class CMDOptionIndexError(Exception):
    pass


#define custom exception
class AlternateConfigArgumentError(Exception):
    pass


#define custom exception
class AlternateConfigNotFoundError(Exception):
    pass


#define custom exception
class UnknownCMDOptionError(Exception):
    pass


#define custom exception
class AlternateConfigSyntaxError(Exception):
    pass

#show the command line help text
def findHelpCMDRequest(argv,the_dict):
    for cmdOption in argv:
        if ((cmdOption == '-h') or (cmdOption == '-help') or (cmdOption == '-?')):
            print_full_help_menu(the_dict)
            sys.exit(0)


#find unknown options
def findUnknownCMDRequest(argv,optionsList):
    for cmdOption in argv:
        if (cmdOption.startswith('-')):
            if (not(cmdOption in optionsList)):
                return cmdOption
    return False


#find option to show console attributes
def findConsoleAttributeShowRequest(argv):
    for cmdOption in argv:
        if ((cmdOption == '-a') or (cmdOption == '-attr') or (cmdOption == '-attrs') or (cmdOption == '-attribute') or (cmdOption == '-attributes')):
            console_text_attributes().console_attribute_test()
            sys.exit(0)


#find alternate config option
def findAltConfigCMDRequest(argv):
    for cmdOption in argv:
        if ((cmdOption == '-c') or (cmdOption == '-config') or (cmdOption == '-configuration')):
            return True
    return False


#find argument (aka path) for the alternate config
def findAltConfigOptionArgument(argv,altConfigInfo,optionsList,the_dict):
    try:
        if (altConfigInfo):
            #loop thru options and verify -c has an alternate path after it
            for checkOption in optionsList:
                if (argv.index('-c')+1 >= len(argv)):
                    raise CMDOptionIndexError
    except (CMDOptionIndexError):
        missing_config_argument_helper(argv,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)


#find running as container option
def findContainerCMDRequest(argv):
    for cmdOption in argv:
        if ((cmdOption == '-d') or (cmdOption == '-container')):
            return True
    return False


#find configuration updater option
def findConfigUpdaterCMDRequest(argv):
    for cmdOption in argv:
        if ((cmdOption == '-u') or (cmdOption == '-updater') or (cmdOption == '-config-updater') or (cmdOption == '-configuration-updater')):
            return True
    return False


#check if alternate config argument is missing
def findNoOptionAfterAltConfigCMDRequest(argv,altConfigInfo,optionsList,the_dict):
    try:
        if (altConfigInfo):
            #loop thru options and verify what comes after -c is not another option
            for checkOption in optionsList:
                if ((argv[argv.index('-c')+1]) == checkOption):
                    raise AlternateConfigArgumentError
    except (AlternateConfigArgumentError):
        missing_config_argument_format_helper(argv,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)


#verify alternate config exists
def verifyAltConfigPathFileExist(argv,altConfigInfo,the_dict):
    try:
        if (altConfigInfo):
            fullPathName=getFullPathName(argv[argv.index('-c')+1])
            #verify alternate config path and file exist
            if (fullPathName == None):
                raise AlternateConfigNotFoundError
    except (AlternateConfigNotFoundError):
        alt_config_file_does_not_exists_helper(argv,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)


#verify alternate config file name follows the python module naming convention
def parseAltConfigPathFileSyntax(argv,altConfigInfo,cmdOption,moduleExtension,the_dict):
    try:
        if (altConfigInfo):
            altConfigExt=getFileExtension(argv[argv.index(cmdOption)+1])
            if ((altConfigExt in moduleExtension) and
                ((os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])).count(".") == 0) and
                ((os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])).count(" ") == 0)):
                #Get path without file.name
                altConfigPath=Path(os.path.dirname(argv[argv.index(cmdOption)+1]))
                #Get file without extension
                altConfigFileNoExt=os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])
            else:
                raise AlternateConfigSyntaxError
    except (AlternateConfigSyntaxError):
        alt_config_syntax_helper(argv,cmdOption,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)

    return altConfigPath,altConfigFileNoExt,altConfigFileNoExt+altConfigExt


#find option to show console attributes
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
        
    for cmdOption in argv:
        if ((cmdOption == '-rak') or (cmdOption == '-remake-api-key')):
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
            #parse for existing labelled MUMC specific authentication key
            mumc_labelled_key=get_MUMC_labelled_authentication_key(labelled_authentication_keys,cfg)
            #if there is an existing key labelled MUMC in the GUI, try to delete it
            if (mumc_labelled_key):
                try:
                    #delete existing MUMC key
                    delete_labelled_authentication_key(mumc_labelled_key,authenticated_user_data,cfg)
                except:
                    pass
            #create labelled MUMC specific authentication key
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


#parse the command line options
def parse_command_line_options(the_dict):

    cmdopt_dict={}
    cmdopt_dict['argv']=the_dict['argv']
    cmdopt_dict['containerized']=False
    cmdopt_dict['moduleExtension']=['.yml','.yaml','.py']

    cmdopt_dict['optionsList']=['-a','-attrs','-attributes','-attr','-attribute',
                                '-c','-config','-configuration',
                                '-d','-container',
                                '-u','-updater','-config-updater','-configuration-updater',
                                #'-rak','-remake-api-key',
                                '-h', '-help','-?']

    #look for -h or -help command line option
    findHelpCMDRequest(cmdopt_dict['argv'],the_dict)

    #look for unknown command line options
    cmdUnknown=findUnknownCMDRequest(cmdopt_dict['argv'],cmdopt_dict['optionsList'])
    if (cmdUnknown):
        unknown_command_line_option_helper(cmdUnknown,the_dict)
        default_helper_menu(the_dict)
        sys.exit(0)

    #look for console attribute show request command line option
    findConsoleAttributeShowRequest(cmdopt_dict['argv'])

    #look for -c or -config command line optoin
    cmdopt_dict['altConfigInfo']=findAltConfigCMDRequest(cmdopt_dict['argv'])
 
    #look for argument after -c or -config command line option
    findAltConfigOptionArgument(cmdopt_dict['argv'],cmdopt_dict['altConfigInfo'],cmdopt_dict['optionsList'],the_dict)
 
    #look for -d or -container command line option
    cmdopt_dict['containerized']=findContainerCMDRequest(cmdopt_dict['argv'])

    #look for -u or -updater or -config-updater or -configuration-updater command line option
    cmdopt_dict['configUpdater']=findConfigUpdaterCMDRequest(cmdopt_dict['argv'])

    #look for another option directly after -c or -config command instead of the path
    findNoOptionAfterAltConfigCMDRequest(cmdopt_dict['argv'],cmdopt_dict['altConfigInfo'],cmdopt_dict['optionsList'],the_dict)

    #verify the specified alternate config path and file exist
    verifyAltConfigPathFileExist(cmdopt_dict['argv'],cmdopt_dict['altConfigInfo'],the_dict)

    if (cmdopt_dict['altConfigInfo']):
        #verify alternate config path and file follow python naming conveniton
        cmdopt_dict['altConfigPath'],cmdopt_dict['altConfigFileNoExt'],cmdopt_dict['altConfigFileExt']=parseAltConfigPathFileSyntax(cmdopt_dict['argv'],cmdopt_dict['altConfigInfo'],'-c',cmdopt_dict['moduleExtension'],the_dict)
    else:
        cmdopt_dict['altConfigPath']=None
        cmdopt_dict['altConfigFileNoExt']=None
        cmdopt_dict['altConfigFileExt']=None

    return cmdopt_dict