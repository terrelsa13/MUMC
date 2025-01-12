import sys
import json
import time
import urllib.request as urlrequest
from urllib.error import HTTPError,URLError
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json
from mumc_modules.mumc_compare_items import keys_exist_return_value


def build_emby_jellyfin_request_message(url,the_dict,authorization='Authorization',client=None,device=None,deviceId=None,version=None,token=None,contentType=None,data=None,method='GET'):

    if (client == None):
        #assume stored name if not defined
        client=the_dict['client_name']

    if (device == None):
        #assume stored device if not defined
        device=the_dict['app_name_long']

    if (deviceId == None):
        #assume stored deviceId if not defined
        deviceId=the_dict['app_name_short']

    if (version == None):
        #assume stored version if not defined
        version=the_dict['script_version']

    if (not (token == None)):
        token=token
    elif (not ((token:=keys_exist_return_value(the_dict,'admin_settings','server','auth_key')) == None)):
        #assume stored token if not defined
        token=token
    else:
        token=''

    if (data == None):
        DATA=data
    else:
        #encode any data passed in
        #DATA = urlparse.urlencode(values)
        #DATA = DATA.encode('ascii')
        DATA = convert2json(data)
        DATA = DATA.encode('utf-8')

    if (contentType == None):
        contentType='application/json'
    elif (contentType == ''):
        pass
    else:
        contentType=contentType

    #build headers
    headers = {authorization : 'MediaBrowser Client="' + client + '", Device="' + device + '", DeviceId="' + deviceId + '", Version="' + version + '", Token="'+ token + '"', 'Content-Type' : contentType}

    #package url, headers, data, and method into a request message
    req = urlrequest.Request(url=url, headers=headers, data=DATA, method=method)
    
    return req


def build_radarr_request_message(url,the_dict,accept=None,token=None,contentType=None,data=None,method='GET'):
    
    if (not (token == None)):
        token=token
    elif (not ((token:=keys_exist_return_value(the_dict,'admin_settings','media_managers','radarr','api_key')) == None)):
        #assume stored token if not defined
        token=token
    else:
        token=''

    if (data == None):
        DATA=data
    else:
        #encode any data passed in
        #DATA = urlparse.urlencode(values)
        #DATA = DATA.encode('ascii')
        DATA = convert2json(data)
        DATA = DATA.encode('utf-8')

    headers={}

    if (accept == None):
        headers['accept']='application/json'
    elif (accept == ''):
        pass
    else:
        headers['accept']=accept

    headers['X-Api-Key']=token

    if (contentType == None):
        headers['Content-Type']='application/json'
    elif (contentType == ''):
        pass
    else:
        headers['Content-Type']=contentType

    #package url, headers, data, and method into a request message
    req = urlrequest.Request(url=url, headers=headers, data=DATA, method=method)
    
    return req


def build_sonarr_request_message(url,the_dict,accept=None,token=None,contentType=None,data=None,method='GET'):
    
    if (not (token == None)):
        token=token
    elif (not ((token:=keys_exist_return_value(the_dict,'admin_settings','media_managers','sonarr','api_key')) == None)):
        #assume stored token if not defined
        token=token
    else:
        token=''

    if (data == None):
        DATA=data
    else:
        #encode any data passed in
        #DATA = urlparse.urlencode(values)
        #DATA = DATA.encode('ascii')
        DATA = convert2json(data)
        DATA = DATA.encode('utf-8')

    headers={}

    if (accept == None):
        headers['accept']='application/json'
    elif (accept == ''):
        pass
    else:
        headers['accept']=accept

    headers['X-Api-Key']=token

    if (contentType == None):
        headers['Content-Type']='application/json'
    elif (contentType == ''):
        pass
    else:
        headers['Content-Type']=contentType

    #package url, headers, data, and method into a request message
    req = urlrequest.Request(url=url, headers=headers, data=DATA, method=method)
    
    return req


#Limit the amount of data returned for a single API call
def api_query_handler(suffix_str,var_dict,the_dict):

    url=var_dict['apiQuery_' + suffix_str]
    StartIndex=var_dict['StartIndex_' + suffix_str]
    TotalItems=var_dict['TotalItems_' + suffix_str]
    QueryLimit=var_dict['QueryLimit_' + suffix_str]
    APIDebugMsg=var_dict['APIDebugMsg_' + suffix_str]

    data=requestURL(url, the_dict['DEBUG'], APIDebugMsg, the_dict['admin_settings']['api_controls']['attempts'], the_dict)

    TotalItems = data['TotalRecordCount']
    StartIndex = StartIndex + QueryLimit
    QueryLimit = the_dict['admin_settings']['api_controls']['item_limit']
    if ((StartIndex + QueryLimit) >= (TotalItems)):
        QueryLimit = TotalItems - StartIndex

    QueryItemsRemaining=False
    if (QueryLimit > 0):
        QueryItemsRemaining=True

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nAPI Query Control Data For The NEXT LOOP: " + str(APIDebugMsg),2,the_dict)
        appendTo_DEBUG_log("\nStarting at record index: " + str(StartIndex),2,the_dict)
        appendTo_DEBUG_log("\nAsking for " + str(QueryLimit) + " records",2,the_dict)
        appendTo_DEBUG_log("\nTotal records for this query is: " + str(TotalItems),2,the_dict)
        appendTo_DEBUG_log("\nAre there records remaining: " + str(QueryItemsRemaining),2,the_dict)

    var_dict['data_' + suffix_str]=data
    var_dict['StartIndex_' + suffix_str]=StartIndex
    var_dict['TotalItems_' + suffix_str]=TotalItems
    var_dict['QueryLimit_' + suffix_str]=QueryLimit
    var_dict['QueriesRemaining_' + suffix_str]=QueryItemsRemaining

    return var_dict


def get_http_error_code_link(error_code):

    if ((error_code >= 100) and (error_code <200)):
        error_code_link='https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#1xx_informational_response'
    elif ((error_code >= 200) and (error_code <300)):
        error_code_link='https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#2xx_success'
    elif ((error_code >= 300) and (error_code <400)):
        error_code_link='https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#3xx_redirection'
    elif ((error_code >= 400) and (error_code <500)):
        error_code_link='https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#4xx_client_errors'
    elif ((error_code >= 500) and (error_code <600)):
        error_code_link='https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#5xx_server_errors'
    else:
        error_code_link='https://en.wikipedia.org/wiki/List_of_HTTP_status_codes'

    return error_code_link


#send url request
def requestURL(url, debugState, requestDebugMessage, retries, the_dict):

    if (debugState):
        #Double newline for better debug file readablilty
        appendTo_DEBUG_log("\n\n" + requestDebugMessage + ' - url request:',2,the_dict)
        appendTo_DEBUG_log("\n" + str(url),3,the_dict)

    #first delay if needed
     #delay value doubles each time the same API request is resent
    doubling_delay = 1
    #number of times after the intial API request to retry if an exception occurs
    retryAttempts = int(retries)

    #check if the method is GET and this url is cached; return the cached data if true
    if ((url.method == 'GET') and (not ((data:=the_dict['cached_data'].getCachedDataFromURL(url.full_url)) == None))):
        #request is cached; do not send request to server
        getdata = False
    else:
        #request is not cached; send request to server
        getdata = True

    #try sending url request specified number of times
     #starting with a 1 second delay if an exception occurs and doubling the doubling_delay each attempt
    while(getdata):
        try:
            #with urlrequest.urlopen(url,timeout=1000) as response:
            with urlrequest.urlopen(url) as response:
                if (debugState):
                    appendTo_DEBUG_log("\nResponse code: " + str(response.getcode()),2,the_dict)
                if ((response.getcode() == 200) or (response.getcode() == 202)):
                    try:
                        source = response.read()
                        data = json.loads(source)
                        if ((url.method == 'GET')):
                            the_dict['cached_data'].addEntryToCache(url.full_url,data)
                        getdata = False
                        if (debugState):
                            appendTo_DEBUG_log("\nResponse Code: " + str(response.getcode()) + " From The " + str(requestDebugMessage) + " Request:\n",2,the_dict)
                            appendTo_DEBUG_log("\nData Returned From The " + str(requestDebugMessage) + " Request:\n",2,the_dict)
                            appendTo_DEBUG_log(convert2json(data) + "\n",4,the_dict)
                    except Exception as err:
                        if (err.msg == 'Unauthorized'):
                            if (debugState):
                                appendTo_DEBUG_log("\n" + str(err),2,the_dict)
                                appendTo_DEBUG_log("\nAUTH_ERROR: User Not Authorized To Access Library",2,the_dict)
                            print("\nAUTH_ERROR: User Not Authorized To Access Library\n" + str(err))
                            print('\n  URL: ' + str(url))
                            sys.exit(0)
                        else:
                            time.sleep(doubling_delay)
                            #doubling_delay value doubles each time the same API request is resent
                            doubling_delay += doubling_delay
                            if (doubling_delay >= (2**retryAttempts)):
                                if (debugState):
                                    appendTo_DEBUG_log("\nAn error occured, a maximum of " + str(retryAttempts) + " attempts met, and no data retrieved from the \"" + requestDebugMessage + "\" lookup.",2,the_dict)
                                print("\nAn error occured, a maximum of " + str(retryAttempts) + " attempts met, and no data retrieved from the \"" + requestDebugMessage + "\" lookup.")
                                print('\n  URL: ' + str(url))
                                sys.exit(0)
                elif (response.getcode() == 204):
                    source = response.read()
                    data = source
                    if (url.method == 'GET'):
                        the_dict['cached_data'].addEntryToCache(url.full_url,data)
                    getdata = False
                    if (debugState):
                        appendTo_DEBUG_log("\nOptional for server to return data for the " + str(requestDebugMessage) + " request:",2,the_dict)
                        if (data):
                            appendTo_DEBUG_log("\n" + data,4,the_dict)
                        else:
                            appendTo_DEBUG_log("\nNo data returned",4,the_dict)
                else:
                    getdata = False
                    if (debugState):
                        appendTo_DEBUG_log("\nAn error occurred while attempting to retrieve data from the API.\nAttempt to get data at: " + requestDebugMessage + ". Server responded with code: " + str(response.getcode()),2,the_dict)
                    print("\nAn error occurred while attempting to retrieve data from the API.\nAttempt to get data at: " + requestDebugMessage + ". Server responded with code: " + str(response.getcode()))
                    print('\n  URL: ' + str(url))
                    sys.exit(0)
        except HTTPError as err:
            time.sleep(doubling_delay)
            #doubling_delay value doubles each time the same API request is resent
            doubling_delay += doubling_delay
            if (doubling_delay >= (2**retryAttempts)):
                print('\nHTTPError: Unable to get information from server during processing of: ' + requestDebugMessage)
                try:
                    print('  Object: ' + str(url.header_items))
                except:
                    print('  Object:')
                try:
                    print('     URL: ' + str(url.full_url))
                except:
                    print('     URL: ' + str(url))
                try:
                    print('  Method: ' + str(url.method))
                except:
                    print('  Method:')
                try:
                    print('  Header: ' + str(url.headers))
                except:
                    print('  Header:')
                try:
                    print('    Data: ' + str(url.data))
                except:
                    print('    Data:')
                print('\nHTTPError: ' + str(err.status) + ' - ' + str(err.reason))
                print('\nHTTP Error Codes: ' + get_http_error_code_link(err.status))
                if(debugState):
                    appendTo_DEBUG_log('\nHTTPError: Unable to get information from server during processing of: ' + requestDebugMessage,2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Object: ' + str(url.header_items),2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Object:',2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n     URL: ' + str(url.full_url),2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n     URL: ' + str(url),2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Method: ' + str(url.method),2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Method:',2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Header: ' + str(url.headers),2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Header:',2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n    Data: ' + str(url.data),2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n    Data:',2,the_dict)
                    appendTo_DEBUG_log('\nHTTPError: ' + str(err.status) + ' - ' + str(err.reason),2,the_dict)
                    appendTo_DEBUG_log('\nHTTP Error Codes: ' + get_http_error_code_link(err.status),1,the_dict)
                sys.exit(0)
        except URLError as err:
            time.sleep(doubling_delay)
            #doubling_delay value doubles each time the same API request is resent
            doubling_delay += doubling_delay
            if (doubling_delay >= (2**retryAttempts)):
                print('\nURLError: Unable to get information from server during processing of: ' + requestDebugMessage)
                try:
                    print('  Object: ' + str(url.header_items))
                except:
                    print('  Object:')
                try:
                    print('     URL: ' + str(url.full_url))
                except:
                    print('     URL: ' + str(url))
                try:
                    print('  Method: ' + str(url.method))
                except:
                    print('  Method:')
                try:
                    print('  Header: ' + str(url.headers))
                except:
                    print('  Header:')
                try:
                    print('    Data: ' + str(url.data))
                except:
                    print('    Data:')
                print('\n' + str(err.reason))
                print('\nCheck ip, url and/or port to server are correct')
                if(debugState):
                    appendTo_DEBUG_log('\nURLError: Unable to get information from server during processing of: ' + requestDebugMessage,1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Object: ' + str(url.header_items),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Object:',1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n     URL: ' + str(url.full_url),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n     URL: ' + str(url),1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Method: ' + str(url.method),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Method:',1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Header: ' + str(url.headers),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Header:',1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n    Data: ' + str(url.data),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n    Data:',1,the_dict)
                    appendTo_DEBUG_log('\n' + str(err.reason),1,the_dict)
                    appendTo_DEBUG_log('\nCheck ip, url and/or port to server are correct',1,the_dict)
                sys.exit(0)
        except TimeoutError:
            time.sleep(doubling_delay)
            #doubling_delay value doubles each time the same API request is resent
            doubling_delay += doubling_delay
            if (doubling_delay >= (2**retryAttempts)):
                print('\nTimeoutError: Unable to get response from server during processing of: ' + requestDebugMessage)
                try:
                    print('  Object: ' + str(url.header_items))
                except:
                    print('  Object:')
                try:
                    print('     URL: ' + str(url.full_url))
                except:
                    print('     URL: ' + str(url))
                try:
                    print('  Method: ' + str(url.method))
                except:
                    print('  Method:')
                try:
                    print('  Header: ' + str(url.headers))
                except:
                    print('  Header:')
                try:
                    print('    Data: ' + str(url.data))
                except:
                    print('    Data:')
                print('\nTimeout - Response taking too long')
                if(debugState):
                    appendTo_DEBUG_log('\nTimeoutError: Unable to get response from server during processing of: ' + requestDebugMessage,1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Object: ' + str(url.header_items),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Object:',1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n     URL: ' + str(url.full_url),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n     URL: ' + str(url),1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Method: ' + str(url.method),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Method:',1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Header: ' + str(url.headers),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Header:',1,the_dict)
                    try:
                        appendTo_DEBUG_log('\n    Data: ' + str(url.data),1,the_dict)
                    except:
                        appendTo_DEBUG_log('\n    Data:',1,the_dict)
                    appendTo_DEBUG_log('\nTimeout - Response taking too long',1,the_dict)
                sys.exit(0)

    return(data)