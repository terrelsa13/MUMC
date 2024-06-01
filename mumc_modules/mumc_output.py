import json
from pathlib import Path
from mumc_modules.mumc_paths import doesFileExist,append_to_file


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