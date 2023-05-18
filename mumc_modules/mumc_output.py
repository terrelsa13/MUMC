#!/usr/bin/env python3
import json
import os
from sys import path


# Change to the specified directory
def change_to_directory(directory):
    #change back to original working directory
    os.chdir(os.path.abspath(os.path.dirname(directory)))


def getFullPathName(filePathName):
    fullPathName=None

    if (doesFileExist(filePathName)):
        fullPathName=os.path.abspath(filePathName)
    else:
        for directory in path:
            if (doesFileExist(os.path.join(directory,filePathName))):
                fullPathName=os.path.join(directory,filePathName)
    return fullPathName


def doesFileExist(filePathName):
    fileExists=False

    #check if file exists; script can be run from anywhere; recommend using full paths
    if os.path.exists(os.path.abspath(filePathName)):
        fileExists=True
    return fileExists


def get_current_directory():
    return os.path.abspath(os.getcwd())


# Delete existing mumc_DEBUG.log file
def delete_file(the_dict):

    if (the_dict['cwd'] == None):
        #get cwd
        cwd=get_current_directory()
    else:
        cwd=the_dict['cwd']

    #check if file exists in cwd (script can be run from anywhere so this could be any directory)
    if (doesFileExist(the_dict['debug_file_name'])):
        fullPathName=getFullPathName(the_dict['debug_file_name'])
    else:
        fullPathName=os.path.join(os.path.abspath(os.path.dirname(__file__)),the_dict['debug_file_name'])

    #change to delete file's directory
    change_to_directory(fullPathName)

    try:
        #delete the file
        os.remove(fullPathName)
    except FileNotFoundError:
        print_byType('\n' + the_dict['debug_file_name'] + ' does not exist and therefore cannot be deleted',False,the_dict)
    #change back to cwd
    change_to_directory(cwd)


def action_to_file(fullPathName,action):
    #open file as append
    return open(fullPathName,action)


#Save file to the directory this script is running from; even when the cwd is not the same
def append_to_file(dataInput,filePathName):
    #get cwd
    cwd=get_current_directory()

    if (doesFileExist(filePathName)):
        fullPathName=getFullPathName(filePathName)
    else:
        fullPathName=os.path.join(os.path.abspath(os.path.dirname(__file__)),filePathName)

    #change to append file's directory
    change_to_directory(fullPathName)
    #open file as append
    f = action_to_file(fullPathName,'a')
    #Write data to file
    f.write(dataInput)
    #Close file
    f.close()
    #change back to cwd
    change_to_directory(cwd)


#Save file to the directory this script is running from; even when the cwd is not the same
def write_to_file(dataInput,filePathName):
    #get cwd
    cwd=get_current_directory()

    if (doesFileExist(filePathName)):
        fullPathName=getFullPathName(filePathName)
    else:
        #fullPathName=os.path.join(os.path.abspath(os.path.basename(__file__)),filePathName)
        #fullPathName=os.path.join(os.path.abspath(__file__),filePathName)
        fullPathName=filePathName

    #change to append file's directory
    change_to_directory(fullPathName)
    #open file as append
    f = action_to_file(fullPathName,'w')
    #Write data to file
    f.write(dataInput)
    #Close file
    f.close()
    #change back to cwd
    change_to_directory(cwd)


#save to mumc_DEBUG.log when DEBUG is enabled
def appendTo_DEBUG_log(string_to_save,debugLevel,the_dict):
    if (the_dict['DEBUG'] >= debugLevel):
        append_to_file(str(string_to_save),os.path.join(the_dict['cwd'],the_dict['debug_file_name']))


#determine if the requested console output line should be shown or hidden
def print_byType(string_to_print,ok_to_print,the_dict):
    if (ok_to_print):
        print(str(string_to_print))
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log(string_to_print,1,the_dict)


def convert2json(rawjson):
    #return a formatted string of the python JSON object
    ezjson = json.dumps(rawjson, sort_keys=False, indent=4)
    return(ezjson)


def print2json(rawjson,the_dict):
    #create a formatted string of the python JSON object
    ezjson = convert2json(rawjson)
    print_byType(ezjson,True,the_dict)