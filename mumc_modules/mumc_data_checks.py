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