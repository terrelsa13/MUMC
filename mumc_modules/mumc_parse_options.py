#!/usr/bin/env python3
import os
from mumc_modules.mumc_console_info import default_helper_menu,print_full_help_menu,missing_config_argument_helper,missing_config_argument_format_helper,alt_config_file_does_not_exists_helper,alt_config_syntax_helper
from mumc_modules.mumc_output import getFullPathName,getFileExtension
from mumc_modules.mumc_console_attributes import console_text_attributes

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
            exit(0)


#find unknown options
def findUnknownCMDRequest(argv,optionsList):
    for cmdOption in argv:
        if (cmdOption.startswith('-')):
            if (not(cmdOption in optionsList)):
                return True
    return False


#find option to show console attributes
def findConsoleAttributeShowRequest(argv):
    for cmdOption in argv:
        if ((cmdOption == '-a') or (cmdOption == '-attr') or (cmdOption == '-attrs') or (cmdOption == '-attribute') or (cmdOption == '-attributes')):
            console_text_attributes().console_attribute_test()
            exit(0)


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
        exit(0)


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
        exit(0)


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
        exit(0)


#verify alternate config file name follows the python module naming convention
def parseAltConfigPathFileSyntax(argv,altConfigInfo,cmdOption,moduleExtension,the_dict):
    try:
        if (altConfigInfo):
            altConfigExt=getFileExtension(argv[argv.index(cmdOption)+1])
            if ((altConfigExt in moduleExtension) and
                ((os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])).count(".") == 0) and
                ((os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])).count(" ") == 0)):
                #Get path without file.name
                altConfigPath=os.path.dirname(argv[argv.index(cmdOption)+1])
                #Get file without extension
                altConfigFileNoExt=os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])
            else:
                raise AlternateConfigSyntaxError
    except (AlternateConfigSyntaxError):
        alt_config_syntax_helper(argv,cmdOption,the_dict)
        default_helper_menu(the_dict)
        exit(0)

    return altConfigPath,altConfigFileNoExt,altConfigFileNoExt+altConfigExt


#parse the command line options
def parse_command_line_options(the_dict):

    cmdopt_dict={}
    cmdopt_dict['argv']=the_dict['argv']
    cmdopt_dict['containerized']=False
    cmdopt_dict['moduleExtension']=['.yml','.yaml','.py']

    cmdopt_dict['optionsList']=['-a','-attrs','-attributes','-attr','-attribute',
                                '-c','-config','-configuration',
                                '-d','-container',
                                '-u','-updater','-config-updater','-configuration-updater'
                                '-h', '-help','-?']

    #look for -h or -help command line option
    findHelpCMDRequest(cmdopt_dict['argv'],the_dict)

    #look for unknown command line options
    if (findUnknownCMDRequest(cmdopt_dict['argv'],cmdopt_dict['optionsList'])):
        raise UnknownCMDOptionError

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
        cmdopt_dict['altConfigPath'],cmdopt_dict['altConfigFileNoExt'],cmdopt_dict['altConfigFileExt']=parseAltConfigPathFileSyntax(cmdopt_dict['argv'],cmdopt_dict['altConfigInfo'],'-c',cmdopt_dict['moduleExtension'])
    else:
        cmdopt_dict['altConfigPath']=None
        cmdopt_dict['altConfigFileNoExt']=None
        cmdopt_dict['altConfigFileExt']=None

    return cmdopt_dict