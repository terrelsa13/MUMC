import sys
import json
import yaml
from pathlib import Path
from mumc_modules.mumc_paths_files import doesFileExist,append_to_file,append_long_string_to_file,doesDirectoryExistCreateIfNot


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def open_and_return_file(full_file_path):
    with open(full_file_path, 'r') as opened_file:
        try:
            return yaml.safe_load(opened_file)
        except:
            print('\nConfigError: Format or Syntax of configuration file is incorrect.\n\tUnable to load ' + str(full_file_path) + '\n')
            sys.exit(0)


def save_yaml_config(dataInput,filePathName):
    #Check if directory exists; if not create it and it's parent directory structure
    doesDirectoryExistCreateIfNot(filePathName.parent)

    #if config does NOT exist create it; then write data to it
    #if config does exist; then write data to it
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
            str_to_print_list=[]
            for str_to_print in string_to_print_list:
                if (str_to_print == "\n"):
                    str_to_print=the_dict['text_attrs'].build_ansi_escaped_newlines(str_to_print)
                else:
                    str_to_print=the_dict['text_attrs'].build_ansi_escaped_string(str_to_print,
                        the_dict['text_attrs'].build_ansi_escape_codes(
                        [the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',text_attributes['font']['color']),
                        the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',text_attributes['background']['color']),
                        the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',text_attributes['font']['style'])]))
                str_to_print_list.append(str_to_print)

            #string_to_print=''.join(string_to_print_list)
            print(''.join(str_to_print_list),end="",flush=True)
    else:
        print(the_dict['text_attrs'].build_ansi_escaped_string(string_to_print,
            the_dict['text_attrs'].build_ansi_escape_codes(
            [the_dict['text_attrs'].get_text_attribute_ansi_code('font_color',text_attributes['font']['color']),
            the_dict['text_attrs'].get_text_attribute_ansi_code('background_color',text_attributes['background']['color']),
            the_dict['text_attrs'].get_text_attribute_ansi_code('font_style',text_attributes['font']['style'])])),end="",flush=True)


def print_long_string_byAttributes(string_to_print,text_attributes,the_dict):
    try:
        character_limit=int(the_dict['admin_settings']['output_controls']['character_limit']['print'])
    except:
        character_limit=128

    string_to_print_len=len(string_to_print)
    string_to_print_mod=string_to_print_len % character_limit
    for string_to_print_pos in range(0,(string_to_print_len - string_to_print_mod),character_limit):
        print_byAttributes(string_to_print[string_to_print_pos:string_to_print_pos+character_limit],text_attributes,the_dict)
    else:
        if (string_to_print_mod):
            string_to_print_pos=string_to_print_pos + character_limit
            print_byAttributes(string_to_print[string_to_print_pos:string_to_print_pos+string_to_print_mod],text_attributes,the_dict)


#save to mumc_DEBUG.log when DEBUG is enabled
def appendTo_DEBUG_log(string_to_save,debugLevel,the_dict):
    if (the_dict['DEBUG'] >= debugLevel):

        try:
            character_limit=int(the_dict['admin_settings']['output_controls']['character_limit']['print'])
        except:
            character_limit=128

        #create ../logs/ path if it does not exists
        doesDirectoryExistCreateIfNot(the_dict['debug_file_path'])

        #if debug file does not exist; create blank file
        if (not(doesFileExist(Path(the_dict['debug_file_path']) / the_dict['debug_file_name_log']))):
            with open(Path(the_dict['debug_file_path']) / the_dict['debug_file_name_log'],'a') as file:
                #create blank file
                pass

        #limit number of characters in a single write to 250
        #loop thru inputs > 250 characters and write in multiple passes
        if (len(string_to_save) > character_limit):
            append_long_string_to_file(str(string_to_save),Path(the_dict['debug_file_path']) / the_dict['debug_file_name_log'],character_limit)
        else:
            append_to_file(str(string_to_save),Path(the_dict['debug_file_path']) / the_dict['debug_file_name_log'])


#determine if the requested console output line should be shown or hidden
def print_byType(string_to_print,ok_to_print,the_dict,text_attributes):
    if (ok_to_print):

        try:
            character_limit=int(the_dict['admin_settings']['output_controls']['character_limit']['print'])
        except:
            character_limit=128

        #limit number of characters in a single print to character limit
        #loop thru inputs > character limit characters and print in multiple passes
        if (len(string_to_print) > character_limit):
            print_long_string_byAttributes(string_to_print,text_attributes,the_dict)
        else:
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