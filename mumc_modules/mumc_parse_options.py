#!/usr/bin/env python3
import os
from mumc_modules.mumc_console_info import defaultHelper
from mumc_modules.mumc_output import print_byType,doesFileExist,getFullPathName
from mumc_modules.mumc_versions import get_script_version

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
            print_byType('\nMUMC Version: ' + get_script_version(),True,the_dict)
            print_byType('Multi-User Media Cleaner aka MUMC (pronounced Mew-Mick) will go through movies, tv episodes, audio tracks, and audiobooks in your Emby/Jellyfin libraries and delete media items you no longer want to keep.',True,the_dict)
            print_byType('',True,the_dict)
            print_byType('Usage:',True,the_dict)
            print_byType('/path/to/python3.x /path/to/mumc.py [-option] [arg]',True,the_dict)
            print_byType('',True,the_dict)
            print_byType('Options:',True,the_dict)
            print_byType('-c [path], -config [path]   Specify alternate *.py configuration file',True,the_dict)
            print_byType('-d, -container              Script is running in a container',True,the_dict)
            print_byType('-h, -help                   Show this help menu',True,the_dict)
            print_byType('',True,the_dict)
            print_byType('Latest Release:',True,the_dict)
            print_byType('https://github.com/terrelsa13/MUMC/releases',True,the_dict)
            print_byType('',True,the_dict)
            exit(0)


def findUnknownCMDRequest(argv,optionsList):
    for cmdOption in argv:
        if (cmdOption.startswith('-')):
            if (not(cmdOption in optionsList)):
                return True
    return False

def findAltConfigCMDRequest(argv):
    for cmdOption in argv:
        if ((cmdOption == '-c') or (cmdOption == '-config')):
            return True
    return False


def findAltConfigCMDArgument(argv,altConfigInfo,optionsList,the_dict):
    try:
        if (altConfigInfo):
            #loop thru options and verify -c has an alternate path after it
            for checkOption in optionsList:
                if (argv.index('-c')+1 >= len(argv)):
                    raise CMDOptionIndexError
    except (CMDOptionIndexError):
        print_byType('',True,the_dict)
        print_byType('CMDOptionIndexError: Cannot find /path/to/alternate_config.py after -c',True,the_dict)
        print_byType('',True,the_dict)
        print_byType('Verify the \'-c\' option looks like this: -c /path/to/alternate_config.py',True,the_dict)
        print_byType('',True,the_dict)
        print_byType(' '.join(argv),True,the_dict)
        print_byType('',True,the_dict)
        defaultHelper(the_dict)
        exit(0)


def findContainerCMDRequest(argv):
    for cmdOption in argv:
        if ((cmdOption == '-d') or (cmdOption == '-container')):
            return True
    return False


def findNoOptionAfterAltConfigCMDRequest(argv,altConfigInfo,optionsList,the_dict):
    try:
        if (altConfigInfo):
            #loop thru options and verify what comes after -c is not another option
            for checkOption in optionsList:
                if ((argv[argv.index('-c')+1]) == checkOption):
                    raise AlternateConfigArgumentError
    except (AlternateConfigArgumentError):
        print_byType('',True,the_dict)
        print_byType('AlternateConfigArgumentError: Cannot find /path/to/alternate_config.py after -c',True,the_dict)
        print_byType('',True,the_dict)
        print_byType('Verify the \'-c\' option looks like this: -c /path/to/alternate_config.py',True,the_dict)
        print_byType('',True,the_dict)
        print_byType(' '.join(argv),True,the_dict)
        print_byType('',True,the_dict)
        defaultHelper(the_dict)
        exit(0)


def verifyAltConfigPathFileExist(argv,altConfigInfo,the_dict):
    try:
        if (altConfigInfo):
            #verify alternate config path and file exist
            #if (not(os.path.exists(argv[argv.index('-c')+1]))):
                #raise AlternateConfigNotFoundError
            #check if file exists in cwd (script can be run from anywhere so this could be any directory)
            if (doesFileExist(argv[argv.index('-c')+1])):
                fullPathName=getFullPathName(argv[argv.index('-c')+1])
            else:
                fullPathName=os.path.join(os.path.abspath(os.path.dirname(__file__)),argv[argv.index('-c')+1])
            #verify alternate config path and file exist
            if (not(doesFileExist(fullPathName))):
                raise AlternateConfigNotFoundError
    except (AlternateConfigNotFoundError):
        print_byType('',True,the_dict)
        print_byType('AlternateConfigNotFoundError: Alternate config path or file does not exist; check for typo or create file',True,the_dict)
        print_byType('',True,the_dict)
        print_byType(' '.join(argv),True,the_dict)
        print_byType('',True,the_dict)
        defaultHelper(the_dict)
        exit(0)


def parseAltConfigPathFileSyntax(argv,altConfigInfo,cmdOption,moduleExtension,the_dict):
    try:
        if (altConfigInfo):
            if ((os.path.splitext(argv[argv.index(cmdOption)+1])[1] == moduleExtension) and
                ((os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])).count(".") == 0) and
                ((os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])).count(" ") == 0)):
                #Get path without file.name
                altConfigPath=os.path.dirname(argv[argv.index(cmdOption)+1])
                #Get file without extension
                altConfigFileNoExt=os.path.basename(os.path.splitext(argv[argv.index(cmdOption)+1])[0])
            else:
                raise AlternateConfigSyntaxError
    except (AlternateConfigSyntaxError):
        print_byType('',True,the_dict)
        print_byType('Alternate configuration file must have a .py extension and follow the Python module naming convention',True,the_dict)
        print_byType('',True,the_dict)
        print_byType('These are NOT valid config file names:',True,the_dict)
        print_byType('',True,the_dict)
        print_byType('\t' + argv[argv.index(cmdOption)+1],True,the_dict)
        print_byType('',True,the_dict)
        print_byType('\t/path/to/alternate.config.py',True,the_dict)
        print_byType('\t/path/to/alternate config.py',True,the_dict)
        print_byType('\tc:\\path\\to\\alternate.config.py',True,the_dict)
        print_byType('\tc:\\path\\to\\alternate config.py',True,the_dict)
        print_byType('',True,the_dict)
        print_byType('These are valid config file names:',True,the_dict)
        print_byType('',True,the_dict)
        print_byType('\t/path/to/alternateconfig.py',True,the_dict)
        print_byType('\t/path/to/alternate_config.py',True,the_dict)
        print_byType('\tc:\\path\\to\\alternateconfig.py',True,the_dict)
        print_byType('\tc:\\path\\to\\alternate_config.py',True,the_dict)
        print_byType('',True,the_dict)
        defaultHelper(the_dict)
        exit(0)

    return altConfigPath,altConfigFileNoExt


def parse_command_line_options(the_dict):

    cmdopt_dict={}
    cmdopt_dict['argv']=the_dict['argv']
    cmdopt_dict['containerized']=False
    cmdopt_dict['optionsList']=['-c','-d','-h']
    cmdopt_dict['moduleExtension']='.py'

    #look for -h or -help command line option
    findHelpCMDRequest(cmdopt_dict['argv'],the_dict)

    #look for unknown command line options
    if (findUnknownCMDRequest(cmdopt_dict['argv'],cmdopt_dict['optionsList'])):
        raise UnknownCMDOptionError

    #look for -c or -config command line optoin
    cmdopt_dict['altConfigInfo']=findAltConfigCMDRequest(cmdopt_dict['argv'])
 
    #look for argument after -c or -config command line option
    findAltConfigCMDArgument(cmdopt_dict['argv'],cmdopt_dict['altConfigInfo'],cmdopt_dict['optionsList'],the_dict)
 
    #look for -d or -container command line option
    cmdopt_dict['containerized']=findContainerCMDRequest(cmdopt_dict['argv'])

    #look for another option directly after -c or -config command instead of the path
    findNoOptionAfterAltConfigCMDRequest(cmdopt_dict['argv'],cmdopt_dict['altConfigInfo'],cmdopt_dict['optionsList'],the_dict)

    #verify the specified alternate config path and file exist
    verifyAltConfigPathFileExist(cmdopt_dict['argv'],cmdopt_dict['altConfigInfo'],the_dict)

    if (cmdopt_dict['altConfigInfo']):
        #verify alternate config path and file follow python naming conveniton
        cmdopt_dict['altConfigPath'],cmdopt_dict['altConfigFileNoExt']=parseAltConfigPathFileSyntax(cmdopt_dict['argv'],cmdopt_dict['altConfigInfo'],'-c',cmdopt_dict['moduleExtension'])
    else:
        cmdopt_dict['altConfigPath']=None
        cmdopt_dict['altConfigFileNoExt']=None

    return cmdopt_dict