#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
#import re
import emoji
import json
import yaml
from pathlib import Path
from sys import path


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


# Add directory to $PATH at specified position; if no position specified add to end of $PATH
def add_to_PATH(path_to_add,position=-1):
    if (not(path_to_add in path)):
        path.insert(position,path_to_add)


# Change to the specified directory
def change_to_directory(directory):
    #change back to specified directory
    os.chdir(os.path.abspath(os.path.dirname(directory)))


def getFullPathName(filePathName):
    #full path preferred
    #if not full path then search cwd, mumc_dir, and $PATH dirs
    fullPathName=None
    if (doesFileExist(filePathName)):
        fullPathName=str(Path(filePathName).resolve())
    else:
        for directory in reversed(path):
            if (doesFileExist(directory + '/' + filePathName)):
                fullPathName=str(Path(directory / filePathName))
    return fullPathName


def doesDirectoryExist(PathName):
    pathExists=False
    #check if path exists
    if (Path(PathName).is_dir()):
        pathExists=True
    return pathExists


def doesFileExist(filePathName):
    fileExists=False
    #check if file exists; script can be run from anywhere; recommend using full paths
    if (Path(filePathName).is_file()):
        fileExists=True
    return fileExists


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

    #remove emoticons
    #dataInput=remove_emoticons(dataInput)

    #remove emojis
    dataInput=remove_emojis(dataInput)

    #Save the config file
    with open(fullPathName,'a') as file:
        file.write(dataInput)


#Save file to the directory this script is running from; even when the cwd is not the same
def write_to_file(dataInput,filePathName):
    fullPathName=getFullPathName(filePathName)

    #Save the config file
    with open(fullPathName,'w') as file:
        file.write(dataInput)


def save_yaml_config(dataInput,filePathName):
    #Save the config file
    with open(filePathName,'w') as file:
        file.write('---\n')
        yaml.dump(dataInput,file,sort_keys=False,Dumper=NoAliasDumper)
        file.write('...')


def parse_string_and_newlines(string_to_print):
    string_to_print_list=[]
    string_to_print_list_0=string_to_print.splitlines(True)

    for string_to_print_item_0 in string_to_print_list_0:
        if ("\n" in string_to_print_item_0):
            string_to_print_item_1=[]
            if (not (string_to_print_item_0 == "\n")):
                string_to_print_item_1 = string_to_print_item_0.split("\n")
                string_to_print_item_1[1]="\n"
            else:
                string_to_print_item_1.append("\n")
            for string_to_print_list_item in string_to_print_item_1:
                string_to_print_list.append(string_to_print_list_item)
        else:
            string_to_print_list.append(string_to_print_item_0)

    return string_to_print_list


def print_byAttributes(string_to_print,text_attributes,the_dict):
    if (string_to_print == ''):
        print(string_to_print)
    elif ("\n" in string_to_print):
            string_to_print_list=parse_string_and_newlines(string_to_print)
            for str_to_print in string_to_print_list:
                if (str_to_print == "\n"):
                    str_to_print=the_dict['text_attrs'].build_ansi_escaped_newlines(str_to_print)
                else:
                    str_to_print=the_dict['text_attrs'].build_ansi_escaped_string(str_to_print,
                        the_dict['text_attrs'].build_ansi_escape_codes(
                        [the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',text_attributes['font']['color']),
                        the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',text_attributes['background']['color']),
                        the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',text_attributes['font']['style'])]))

            string_to_print=''.join(string_to_print_list).rstrip()
            print(''.join(string_to_print))
    else:
        print(the_dict['text_attrs'].build_ansi_escaped_string(string_to_print,
            the_dict['text_attrs'].build_ansi_escape_codes(
            [the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',text_attributes['font']['color']),
            the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',text_attributes['background']['color']),
            the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',text_attributes['font']['style'])])))


#save to mumc_DEBUG.log when DEBUG is enabled
def appendTo_DEBUG_log(string_to_save,debugLevel,the_dict):
    if (the_dict['DEBUG'] >= debugLevel):

        #if debug file does not exist; create blank file
        if (not(doesFileExist(Path(the_dict['mumc_path']) / the_dict['debug_file_name']))):
            with open(Path(the_dict['mumc_path']) / the_dict['debug_file_name'],'a') as file:
                #create blank file
                pass

        append_to_file(str(string_to_save),Path(the_dict['mumc_path']) / the_dict['debug_file_name'])


#determine if the requested console output line should be shown or hidden
def print_byType(string_to_print,ok_to_print,the_dict,text_attributes):
    if (ok_to_print):
            print_byAttributes(string_to_print,text_attributes,the_dict)
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log(string_to_print,1,the_dict)


def convert2json(rawjson):
    #return a formatted string of the python JSON object
    ezjson = json.dumps(rawjson, sort_keys=False, indent=4)
    return(ezjson)


def print2json(rawjson,the_dict):
    #create a formatted string of the python JSON object
    ezjson = convert2json(rawjson)
    print_byType(ezjson,True,the_dict,the_dict['advanced_settings']['console_controls']['headers']['script']['formatting'])