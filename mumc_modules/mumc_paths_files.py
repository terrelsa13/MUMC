# -*- coding: utf-8 -*-
import os
#import re
#import yaml
import emoji
from sys import path
from pathlib import Path


#class NoAliasDumper(yaml.SafeDumper):
    #def ignore_aliases(self, data):
        #return True


# Add directory to $PATH at specified position; if no position specified add to end of $PATH
def add_to_PATH(path_to_add,position=-1):
    if (not(path_to_add in path)):
        path.insert(position,path_to_add)


# Change to the specified directory
def change_to_directory(directory):
    #change back to specified directory
    os.chdir(os.path.abspath(os.path.dirname(directory)))


def doesFileExist(filePathName):
    fileExists=False
    #check if file exists; script can be run from anywhere; recommend using full paths
    if (Path(filePathName).is_file()):
        fileExists=True
    return fileExists


def getFullPathName(filePathName):
    #full path preferred
    #if not full path then search cwd, mumc_dir, and $PATH dirs
    fullPathName=None
    if (doesFileExist(filePathName)):
        fullPathName=str(Path(filePathName).resolve())
    else:
        for directory in reversed(path):
            if (doesFileExist(Path(directory) / Path(filePathName))):
                fullPathName=str(Path(directory / filePathName))
    return fullPathName


def doesDirectoryExist(PathName):
    pathExists=False
    #check if path exists
    if (Path(PathName).is_dir()):
        pathExists=True
    return pathExists


def getFileExtension(path_or_filename):
    if (doesFileExist(path_or_filename)):
        return Path(path_or_filename).suffix
    else:
        return None


def get_current_directory():
    return Path('.').parent.resolve()


# Delete existing mumc_DEBUG.log file
def delete_debug_log(the_dict):
    Path(the_dict['mumc_path'] / the_dict['debug_file_name']).unlink(missing_ok=True)
    Path(the_dict['mumc_path_config_dir'] / the_dict['debug_file_name']).unlink(missing_ok=True)


#Remove emojis before printing to mumc_debug.log
def remove_emojis(dataInput: str) -> str:
    dataInput=emoji.replace_emoji(dataInput, replace="***emoji_removed***")
    return dataInput


#Remove emoticons before printing to mumc_debug.log
#def remove_emoticons(dataInput):

    #removeEmojis = re.compile(pattern =
    #"["
        #u"\U0001F600-\U0001F64F" # emoticons
        #u"\U0001F300-\U0001F5FF" # symbols & pictographs
        #u"\U0001F680-\U0001F6FF" # transport & map symbols
        #u"\U0001F1E0-\U0001F1FF" # flags (iOS)
    #"]+", flags = re.UNICODE)

    #return removeEmojis.sub(r'',dataInput)


#Save file to the directory this script is running from; even when the cwd is not the same
def append_to_file(dataInput,filePathName):
    fullPathName=getFullPathName(filePathName)

    #remove emojis
    dataInput=remove_emojis(dataInput)

    #Save the config file
    with open(fullPathName,'a') as file:
        file.write(dataInput)


def append_long_string_to_file(dataInput,filePathName,character_limit=128):

    dataInput_inc=character_limit
    dataInput_len=len(dataInput)
    dataInput_mod=dataInput_len % dataInput_inc

    #open file being written to
    file = open(filePathName, "a")

    try:
        #loop thru long string and write in smaller increments
        for dataInput_pos in range(0,(dataInput_len - dataInput_mod),dataInput_inc):
            file.write(dataInput[dataInput_pos:dataInput_pos+dataInput_inc])
        else:
            #for the last write only print the remaining characters
            if (dataInput_mod):
                dataInput_pos=dataInput_pos+dataInput_inc
                file.write(dataInput[dataInput_pos:dataInput_pos+dataInput_mod])
    finally:
        #finally close the file
        file.close()