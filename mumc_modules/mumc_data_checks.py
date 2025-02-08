import sys
from collections.abc import Mapping
from mumc_modules.mumc_output import appendTo_DEBUG_log
from mumc_modules.mumc_compare_items import keys_exist_return_value


#Data checker class
class data_checker:
    #Initialize and define data checker variables
    def __init__(self,cfg,init_dict):
        self.cfg=cfg
        self.init_dict=init_dict
        self.wasErrorFlag=False
        self.errorString=''
        self.bool=bool
        self.str=str
        self.int=int
        self.alnum=str
        self.mapping=Mapping
        self.list=list
        self.dict=dict


    def printError(self,errorString):
        #Bring all errors found to users attention
        if (self.init_dict['DEBUG']):
            appendTo_DEBUG_log("\n" + errorString,2,self.init_dict)
        print('\n' + errorString)


    def wasErrorExit(self):
        if (self.wasErrorFlag):
            sys.exit(0)


    def getValue(self,*cfgLocationTuple):
        if (not ((value:=keys_exist_return_value(self.cfg,*cfgLocationTuple)) == None)):
            return value
        else:
            return None

    def compareMinLength(self,value,minLength):
        return minLength <= len(value)


    def compareMaxLength(self,value,maxLength):
        return maxLength >= len(value)


    def compareMinValue(self,value,minValue):
        if(isinstance(value,self.mapping)):
            return minValue <= min(value)
        else:
            return minValue <= value


    def compareMaxValue(self,value,maxValue):
        if(isinstance(value,self.mapping)):
            return maxValue >= max(value)
        else:
            return maxValue >= value


    def compareValueToValues(self,value,comparisonValues):
        if (isinstance(value,self.list)):
            for vItem in value:
                if (not (vItem in comparisonValues)):
                    return False
            else:
                return True
        elif (isinstance(value,self.dict)):
            for vItem in value:
                #if ((not (vItem in comparisonValues)) or
                    #(not (value[vItem] == comparisonValues[vItem]))):
                    #return False
                if (not (vItem in comparisonValues)):
                    return False
            else:
                return True
        else:
            if value in comparisonValues:
            #if (value == cmpStr):
                return True
            else:
                return False
 
    
    def setStringErrorText(self,comparisonValues,*cfgLocationTuple):
        return self.setErrorText('string',comparisonValues,*cfgLocationTuple)


    def setIntegerErrorText(self,comparisonValues,minValue,maxValue,*cfgLocationTuple):
        return self.setErrorText('integer',comparisonValues,minValue,maxValue,*cfgLocationTuple)


    def setAlphaNumericErrorText(self,comparisonValues,*cfgLocationTuple):
        return self.setErrorText('alphanumeric string',comparisonValues,*cfgLocationTuple)


    def setListErrorText(self,comparisonValues,*cfgLocationTuple):
        return self.setErrorText('list',comparisonValues,*cfgLocationTuple)


    def setErrorText(self,type,comparisonValues=None,minValue=None,maxValue=None,*cfgLocationTuple):
        self.wasErrorFlag=True
        if (not (comparisonValues == None)):
            return 'ConfigValueError: ' + ' > '.join(str(element) for element in cfgLocationTuple) + ' must be a ' + type + ' or is missing\n\tValid values are ' + ', '.join(str(element) for element in comparisonValues) + '\n'
        elif (not (minValue == None)):
            return 'ConfigValueError: ' + ' > '.join(str(element) for element in cfgLocationTuple) + ' must be a ' + type + ' or is missing\n\tValid values are ' + str(minValue) + ' thru 730500\n'
        elif (not (maxValue == None)):
            return 'ConfigValueError: ' + ' > '.join(str(element) for element in cfgLocationTuple) + ' must be a ' + type + ' or is missing\n\tValid values are -730500 thru ' + str(maxValue) + '\n'
        elif ((not (minValue == None)) and (not (maxValue == None))):
            return 'ConfigValueError: ' + ' > '.join(str(element) for element in cfgLocationTuple) + ' must be a ' + type + ' or is missing\n\tValid values are ' + str(minValue) + ' thru ' + str(maxValue) + '\n'
        else:
            return 'ConfigValueError: ' + ' > '.join(str(element) for element in cfgLocationTuple) + ' must be a ' + type + ' or is missing\n'


    def setCustomErrorText(self,customErrText):
        self.wasErrorFlag=True
        self.errorString+=customErrText


    def checkBoolean(self,*cfgLocationTuple,value=None,instanceType=None,errOut=True):
        isError=False
        if ((not (cfgLocationTuple == ())) and ((value:=self.getValue(*cfgLocationTuple)) == None)):
            isError=True
        if ((not (instanceType == None)) and (not (isinstance(value,instanceType)))):
            isError=True

        if (isError):
            if (errOut):
                self.errorString+=self.setStringErrorText(None,*cfgLocationTuple)
            return None
        else:
            return value


    #value=value.casefold()
    def checkString(self,*cfgLocationTuple,value=None,instanceType=None,minLength=None,maxLength=None,errOut=True,comparisonValues=None):
        isError=False
        if ((not (cfgLocationTuple == ())) and ((value:=self.getValue(*cfgLocationTuple)) == None)):
            isError=True
        if ((not (instanceType == None)) and (not (isinstance(value,instanceType)))):
            isError=True
        if ((not (value == None)) and (not (minLength == None)) and (not (self.compareMinLength(value,minLength)))):
            isError=True
        if ((not (value == None)) and (not (maxLength == None)) and (not (self.compareMaxLength(value,maxLength)))):
            isError=True
        if ((not (comparisonValues == None)) and (not (self.compareValueToValues(value.casefold(),comparisonValues)))):
            isError=True

        if (isError):
            if (errOut):
                self.errorString+=self.setStringErrorText(comparisonValues,*cfgLocationTuple)
            return None
        else:
            return value


    def checkInteger(self,*cfgLocationTuple,value=None,instanceType=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None):
        isError=False
        if ((not (cfgLocationTuple == ())) and ((value:=self.getValue(*cfgLocationTuple)) == None)):
            isError=True
        if ((not (instanceType == None)) and (not (isinstance(value,instanceType)))):
            isError=True
        if ((not (value == None)) and (not (minValue == None)) and (not (self.compareMinValue(value,minValue)))):
            isError=True
        if ((not (value == None)) and (not (maxValue == None)) and (not (self.compareMaxValue(value,maxValue)))):
            isError=True
        if ((not (comparisonValues == None)) and (not (self.compareValueToValues(value,comparisonValues)))):
            isError=True

        if (isError):
            if (errOut):
                self.errorString+=self.setIntegerErrorText(comparisonValues,minValue,maxValue,*cfgLocationTuple)
            return None
        else:
            return value


    def checkAlphaNumeric(self,*cfgLocationTuple,value=None,instanceType=None,minLength=None,maxLength=None,errOut=True,comparisonValues=None):
        isError=False
        if ((not (cfgLocationTuple == ())) and ((value:=self.getValue(*cfgLocationTuple)) == None)):
            isError=True
        if ((self.checkString(*(),value=value,instanceType=instanceType,minLength=minLength,maxLength=maxLength,errOut=False,comparisonValues=comparisonValues)) == None):
            isError=True
        if (not (value.isalnum())):
            isError=True

        if (isError):
            if (errOut):
                self.errorString+=self.setAlphaNumericErrorText(comparisonValues,*cfgLocationTuple)
            return None
        else:
            return value


    def checkList(self,*cfgLocationTuple,value=None,instanceType=None,minLength=None,maxLength=None,minValue=None,maxValue=None,errOut=True,comparisonValues=None):
        isError=False
        if ((not (cfgLocationTuple == ())) and ((value:=self.getValue(*cfgLocationTuple)) == None)):
            isError=True
        if ((not (instanceType == None)) and (not (isinstance(value,instanceType)))):
            isError=True
        if ((not (value == None)) and (not (minLength == None)) and (not (self.compareMinLength(value,minLength)))):
            isError=True
        if ((not (value == None)) and (not (maxLength == None)) and (not (self.compareMaxLength(value,maxLength)))):
            isError=True
        if ((not (value == None)) and (not (minValue == None)) and (not (self.compareMinValue(value,minValue)))):
            isError=True
        if ((not (value == None)) and (not (maxValue == None)) and (not (self.compareMaxValue(value,maxValue)))):
            isError=True
        if ((not (comparisonValues == None)) and (not (self.compareValueToValues(value,comparisonValues)))):
            isError=True

        if (isError):
            if (errOut):
                self.errorString+=self.setListErrorText(comparisonValues,*cfgLocationTuple)
            return None
        else:
            return value


    def checkDict(self,*cfgLocationTuple,value=None,instanceType=None,minLength=None,maxLength=None,errOut=True,comparisonValues=None):
        isError=False
        if ((not (cfgLocationTuple == ())) and ((value:=self.getValue(*cfgLocationTuple)) == None)):
            isError=True
        if ((not (instanceType == None)) and (not (isinstance(value,instanceType)))):
            isError=True
        if ((not (minLength == None)) and (not (self.compareMinLength(value,minLength))) and (not (value == None))):
            isError=True
        if ((not (maxLength == None)) and (not (self.compareMaxLength(value,maxLength))) and (not (value == None))):
            isError=True
        if ((not (comparisonValues == None)) and (not (self.compareValueToValues(value,comparisonValues))) and (not (value == None))):
            isError=True

        if (isError):
            if (errOut):
                self.errorString+=self.setListErrorText(comparisonValues,*cfgLocationTuple)
            return None
        else:
            return value


#Check blacklist and whitelist config variables are as expected
def cfgCheckYAML_forLibraries(check_list, user_ids_check_list, user_names_check_list, config_var_name):

    error_found_in_mumc_config_yaml=''

    for check_irt in check_list:
        #Check if user_id exists
        if ('user_id' in check_irt):
            #Set user tracker to zero
            user_found=0
            #Check user from user_keys is also a user in this blacklist/whitelist
            for user_check in user_ids_check_list:
                if (user_check == check_irt['user_id']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user_id ' + check_irt['user_id'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user_id ' + check_irt['user_id'] + ' is seen more than once\n'
            #Check user_id is string
            if (not (isinstance(check_irt['user_id'], str))):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' the user_id is not a string or is not a list for at least one user\n'
            else:
                #Check user_id is 32 character long alphanumeric
                if (not (
                    (check_irt['user_id'].isalnum()) and
                    (len(check_irt['user_id']) == 32)
                )):
                    error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' + at least one user_id is not a 32-character alphanumeric string\n'
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The ' + config_var_name + ' > user_id key is missing for at least one user\n'


        #Check if user_name exists
        if ('user_name' in check_irt):
            #Set user tracker to zero
            user_found=0
            #Check user from user_name is also a user in this blacklist/whitelist
            for user_check in user_names_check_list:
                if (user_check == check_irt['user_name']):
                    user_found+=1
            if (user_found == 0):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user_name ' + check_irt['user_name'] + ' does not match any user from user_keys\n'
            if (user_found > 1):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user_name ' + check_irt['user_name'] + ' is seen more than once\n'
            #Check user_name is string
            if (not (isinstance(check_irt['user_name'], str))):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' the user_name is not a string or is not a list for at least one user\n'
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The ' + config_var_name + ' > user_name is missing for at least one user\n'

        #Check if whitelist exists
        if ('whitelist' in check_irt):
            #Check whitelist is string
            if (not (isinstance(check_irt['whitelist'], list))):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' the whitelist is not a string or is not a list for at least one user\n'
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The ' + config_var_name + ' > whitelist is missing for at least one user\n'

        #Check if blacklist exists
        if ('blacklist' in check_irt):
            #Check blacklist is string
            if (not (isinstance(check_irt['blacklist'], list))):
                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' the blacklist is not a string or is not a list for at least one user\n'
        else:
            error_found_in_mumc_config_yaml+='ConfigNameError: The ' + config_var_name + ' > blacklist is missing for at least one user\n'

        #Get number of elements
        for user_elements in check_irt:
            #Ignore user_id and user_name
            #Check whitelist and blacklist only if they are not empty lists
            if (((not (user_elements == 'user_id')) and (not (user_elements == 'user_name'))) and (((user_elements == 'whitelist') or (user_elements == 'blacklist')) and check_irt[user_elements])):
                #Set library key trackers to zero
                lib_id_found=0
                collection_type_found=0
                path_found=0
                network_path_found=0
                subfolder_id_found=0
                lib_enabled_found=0
                #Check if this num_element exists before proceeding
                if (user_elements in check_irt):
                    for libinfo in check_irt[user_elements]:
                        if ('lib_id' in libinfo):
                            lib_id_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['lib_id']
                            #Check lib_id is alphanumeric string
                            if (not (isinstance(check_item,str) and (check_item.isalpha() or check_item.isalnum() or check_item.isnumeric()))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > lib_id: ' + str(check_item) + ' is not an expected string value\n'

                        if ('collection_type' in libinfo):
                            collection_type_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['collection_type']
                            #Check collection_type is string
                            if (not (isinstance(check_item,str) or (check_item == ''))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > collection_type: ' + str(check_item) + ' is not an expected string value\n'

                        if ('path' in libinfo):
                            path_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['path']
                            #Check path is string; checking for backslashes does not work for windows
                            #if (not ((isinstance(check_item,str) and (check_item.find('\\') < 0)) or (check_item == '') or (check_item == None))):
                            if (not (isinstance(check_item,str) or (check_item == '') or (check_item == None))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > path: ' + str(check_item) + ' is not an expected string value\n'

                        if ('network_path' in libinfo):
                            network_path_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['network_path']
                            #Check network_path is string; checking for backslashes does not work for windows
                            #if (not ((isinstance(check_item,str) and (check_item.find('\\') < 0)) or (check_item == '') or (check_item == None))):
                            if (not (isinstance(check_item,str) or (check_item == '') or (check_item == None))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > network_path: ' + str(check_item) + ' is not an expected string value\n'

                        if ('subfolder_id' in libinfo):
                            subfolder_id_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['subfolder_id']
                            #Check subfolder_id is alphanumeric string
                            if (not ((check_item == None) or (isinstance(check_item,str) and (check_item.isalpha() or check_item.isalnum() or check_item.isnumeric())))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > subfolder_id: ' + str(check_item) + ' is not an expected string value. Try adding quotes: \'' + str(check_item) + '\' or null if Jellyfin\n'

                        if ('lib_enabled' in libinfo):
                            lib_enabled_found += 1
                            check_item=check_irt[user_elements][int(check_irt[user_elements].index(libinfo))]['lib_enabled']
                            #Check lib_enabled is boolean
                            if (not (isinstance(check_item,bool))):
                                error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' > user_id: ' + str(check_irt['user_id']) + ' > ' + user_elements + ' > library_id: ' + str(libinfo['lib_id']) + ' > enabled: ' + str(check_item) + ' is not an expected boolean value\n'

                    if (lib_id_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key lib_id is missing\n'

                    if (collection_type_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key collection_type is missing\n'

                    if (network_path_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key network_path is missing\n'

                    if (path_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key path is missing\n'

                    if (subfolder_id_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key subfolder_id is missing\n'

                    if (lib_enabled_found == 0):
                        error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' for user ' + check_irt['user_id'] + ' key lib_enabled is missing\n'

                else:
                    error_found_in_mumc_config_yaml+='ConfigValueError: ' + config_var_name + ' user ' + check_irt['user_id'] + ' key'+ str(user_elements) +' does not exist\n'
    return(error_found_in_mumc_config_yaml)


#Check filter_tags are formatted as expected
def cfgCheckYAML_isFilterTag(tag,tag_list):
    
    no_error_found=True
    
    if (
        not (isinstance(tag,str) and isinstance(tag_list,list) and
            (isinstance(tag_list[0],str) and ((tag_list[0] == 'played') or (tag_list[0] == 'created')) and
                isinstance(tag_list[1],int) and ((tag_list[1] >= -1) and (tag_list[1] <= 730500)) and
                isinstance(tag_list[2],str) and
                ((tag_list[2] == '>') or (tag_list[2] == '<') or
                (tag_list[2] == '>=') or (tag_list[2] == '<=') or
                (tag_list[2] == '==') or (tag_list[2] == 'not ==') or
                (tag_list[2] == 'not >') or (tag_list[2] == 'not <') or
                (tag_list[2] == 'not >=') or (tag_list[2] == 'not <=')) and
                isinstance(tag_list[3],int) and ((tag_list[3] >= -1) and (tag_list[3] <= 730500)) and
                ((tag_list[0] == 'played') or ((tag_list[0] == 'created') and isinstance(tag_list[4],bool) and ((tag_list[4] == True) or (tag_list[4] == False)))))
            )
        ):
        no_error_found=False

    return no_error_found


#Check behavioral_tags config variables are as expected
def cfgCheckYAML_isBehavioralTag(cfg,tag,media_type):
    
    error_found_in_mumc_config_yaml=''

    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'action')) == None)):
        if (
            not (isinstance(check,str) and
                ((check.casefold() == 'delete') or (check.casefold() == 'keep')))
            ):
            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > action must be a string\n\tValid values \'delete\' and \'keep\'\n'
        else:
            if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'user_conditional')) == None)):
                if (
                    not (isinstance(check,str) and
                        (check.casefold() == 'all'))
                    ):
                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > user_conditional must be a string\n\tValid values \'any\' and \'all\'\n'
                else:
                    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'played_conditional')) == None)):
                        if (
                            not (isinstance(check,str) and
                                ((check.casefold() == 'all') or (check.casefold() == 'any') or #legacy values
                                (check.casefold() == 'all_all') or (check.casefold() == 'any_any') or
                                (check.casefold() == 'any_all') or (check.casefold() == 'all_any') or
                                (check.casefold() == 'any_played') or (check.casefold() == 'all_played') or
                                (check.casefold() == 'any_created') or (check.casefold() == 'all_created') or
                                (check.casefold() == 'ignore')))
                            ):
                            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > played_conditional must be a string\n\tValid values \'any_any\', \'all_all\', \'any_all\', \'all_any\', \'any_played\', \'all_played\', \'any_created\', and \'all_created\'\n'
                        else:
                            if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'action_control')) == None)):
                                if (
                                    not (isinstance(check,int) and
                                        ((check >= 0) and (check <= 8)))
                                    ):
                                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > action_control must be an integer\n\tValid range 0 thru 8\n'
                                else:
                                    if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'dynamic_behavior')) == None)):
                                        if (
                                            not (isinstance(check,bool) and
                                                ((check == True) or (check == False)))
                                            ):
                                            error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > dynamic_behavior must be an boolean\n\tValid values True or False\n'
                                        else:
                                            if (not ((check:=keys_exist_return_value(cfg,'advanced_settings','behavioral_tags',media_type,tag,'high_priority')) == None)):
                                                if (
                                                    not (isinstance(check,bool) and
                                                        ((check == True) or (check == False)))
                                                    ):
                                                    error_found_in_mumc_config_yaml+='ConfigValueError: advanced_settings > behavioral_tags > ' +  media_type + ' > ' + tag + ' > high_priority must be an boolean\n\tValid values True or False\n'

    return error_found_in_mumc_config_yaml