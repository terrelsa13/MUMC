#!/usr/bin/env python3


#https://en.wikipedia.org/wiki/ANSI_escape_code
class console_text_attributes:

    def __init__(self):
        self.text_attribute_dict={'font_color':{},'background_color':{},'font_style':{},'background_style':{}}
######################################
        #End Attributes
        self.text_attribute_dict['end_attr'] = '\033[0m'
######################################
        #Font Color Attributes
        self.text_attribute_dict['font_color']['black']=30
        self.text_attribute_dict['font_color']['red']=31
        self.text_attribute_dict['font_color']['green']=32
        self.text_attribute_dict['font_color']['yellow']=33
        self.text_attribute_dict['font_color']['blue']=34
        self.text_attribute_dict['font_color']['magenta']=35
        self.text_attribute_dict['font_color']['cyan']=36
        self.text_attribute_dict['font_color']['white']=37
        #SET_TEXT_COLOR = '38' #Next arguments are 5;<n> or 2;<r>;<g>;<b>, see below
        self.text_attribute_dict['font_color']['default']=39 #Implementation defined (according to standard)
        self.text_attribute_dict['font_color']['bright black']=90 #Aixterm (not in standard)
        self.text_attribute_dict['font_color']['bright red']=91 #Aixterm (not in standard)
        self.text_attribute_dict['font_color']['bright green']=92 #Aixterm (not in standard)
        self.text_attribute_dict['font_color']['bright yellow']=93 #Aixterm (not in standard)
        self.text_attribute_dict['font_color']['bright blue']=94 #Aixterm (not in standard)
        self.text_attribute_dict['font_color']['bright magenta']=95 #Aixterm (not in standard)
        self.text_attribute_dict['font_color']['bright cyan']=96 #Aixterm (not in standard)
        self.text_attribute_dict['font_color']['bright white']=97 #Aixterm (not in standard)
######################################
        #Background Color Attributes
        self.text_attribute_dict['background_color']['black']=40
        self.text_attribute_dict['background_color']['red']=41
        self.text_attribute_dict['background_color']['green']=42
        self.text_attribute_dict['background_color']['yellow']=43
        self.text_attribute_dict['background_color']['blue']=44
        self.text_attribute_dict['background_color']['magenta']=45
        self.text_attribute_dict['background_color']['cyan']=46
        self.text_attribute_dict['background_color']['white']=47
        #SET_HIGHLIGHT_COLOR = '48' #Next arguments are 5;<n> or 2;<r>;<g>;<b>, see below
        self.text_attribute_dict['background_color']['default']=49 #Implementation defined (according to standard)
        self.text_attribute_dict['background_color']['bright black']=100 #Aixterm (not in standard)
        self.text_attribute_dict['background_color']['bright red']=101 #Aixterm (not in standard)
        self.text_attribute_dict['background_color']['bright green']=102 #Aixterm (not in standard)
        self.text_attribute_dict['background_color']['bright yellow']=103 #Aixterm (not in standard)
        self.text_attribute_dict['background_color']['bright blue']=104 #Aixterm (not in standard)
        self.text_attribute_dict['background_color']['bright magenta']=105 #Aixterm (not in standard)
        self.text_attribute_dict['background_color']['bright cyan']=106 #Aixterm (not in standard)
        self.text_attribute_dict['background_color']['bright white']=107 #Aixterm (not in standard)
######################################
        #Font Style Attributes
        self.text_attribute_dict['font_style']['bold']=1
        self.text_attribute_dict['font_style']['faint']=2 #Not widely supported.
        self.text_attribute_dict['font_style']['italic']=3 #Not widely supported. Sometimes treated as inverse.
        self.text_attribute_dict['font_style']['underline']=4
        self.text_attribute_dict['font_style']['slow blink']=5 #Less than 150 per minute
        self.text_attribute_dict['font_style']['fast blink']=6 #MS-DOS ANSI.SYS; 150+ per minute; not widely supported
        self.text_attribute_dict['font_style']['swap']=7 #Swap foreground and background colors
        self.text_attribute_dict['font_style']['conceal']=8 #Not widely supported.
        self.text_attribute_dict['font_style']['strikethrough']=9 #Characters legible, but marked for deletion. Not widely supported.
        self.text_attribute_dict['font_style']['default']=10
        self.text_attribute_dict['font_style']['fraktur']=20 #Hardly ever supported
        self.text_attribute_dict['font_style']['double underline']=21 #Double underline hardly ever supported.
        self.text_attribute_dict['font_style']['reveal']=28 #Conceal off
        #ALTERNATE_FONT = '11' thru '19' #Select alternate font n-10
        self.text_attribute_dict['font_style']['frame']=51 #Hardly ever supported
        self.text_attribute_dict['font_style']['encircle']=52 #Hardly ever supported
        self.text_attribute_dict['font_style']['overline']=53 #Hardly ever supported
        self.text_attribute_dict['font_style']['ideogram underline']=60 #Hardly ever supported
        self.text_attribute_dict['font_style']['ideogram double underline']=61 #Hardly ever supported
        self.text_attribute_dict['font_style']['ideogram overline']=62 #Hardly ever supported
        self.text_attribute_dict['font_style']['ideogram double overline']=63 #Hardly ever supported
        self.text_attribute_dict['font_style']['ideogram stress mark']=64 #Hardly ever supported
        self.text_attribute_dict['font_style']['superscript']=73 #Implemented only in mintty
        self.text_attribute_dict['font_style']['subscript']=74 #Implemented only in mintty
######################################

    def get_text_attribute_ansi_code(self,key0,key1):
        if (key0 in self.text_attribute_dict):
            if (key1 in self.text_attribute_dict[key0]):
                return self.text_attribute_dict[key0][key1]
        return None

    def build_ansi_escape_codes(self,attr_list):
        len_inc=0
        all_attrs=''

        for x in attr_list:
            if (not (x == None)):
                all_attrs += str(x) + ';'
            len_inc += 1

        return all_attrs.rstrip(';')

    def build_ansi_escaped_string(self,string_to_print,attr_str):
        if (attr_str == ''):
            return string_to_print
        else:
            return f'\033[' + attr_str + 'm' + string_to_print + self.text_attribute_dict['end_attr']

    def build_ansi_escaped_newlines(self,string_to_print):
        return self.text_attribute_dict['end_attr'] + string_to_print

    def console_attribute_test(self):
        attrs_show=''
        for r1 in range (0,11):
            for r2 in range (0,10):
                z=(10 * r1) + r2
                if (z <= 107):
                    attrs_show += f'\033[{z}m{z:4}\033[0m'
                if (r2 >= 9):
                    attrs_show += '\n'
        print(attrs_show)


############# START OF SCRIPT #############

if (__name__ == "__main__"):
    console_text_attributes().console_attribute_test()
    exit(0)

############# END OF SCRIPT #############