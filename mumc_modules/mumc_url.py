import urllib.request as urlrequest
from urllib.error import HTTPError,URLError
import json
import time
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json


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

    try:
        data = the_dict['cached_data'].getCachedDataFromURL(url)
    except:
        data = False

    if (data):
        getdata = False
    else:
        getdata = True

    #try sending url request specified number of times
     #starting with a 1 second doubling_delay if an exception occurs and doubling the doubling_delay each attempt
    while(getdata):
        try:
            #with urlrequest.urlopen(url,timeout=1000) as response:
            with urlrequest.urlopen(url) as response:
                if (debugState):
                    appendTo_DEBUG_log("\nResponse code: " + str(response.getcode()),2,the_dict)
                #request recieved; but taking long time to return data
                while (response.getcode() == 202):
                    #wait 20% of the delay value
                    time.sleep(doubling_delay/5)
                    if (debugState):
                        appendTo_DEBUG_log("\nWaiting for server to return data from the " + str(requestDebugMessage) + " Request; then trying again...",2,the_dict)
                if (response.getcode() == 200):
                    try:
                        source = response.read()
                        data = json.loads(source)
                        the_dict['cached_data'].addEntryToCache(url,data)
                        getdata = False
                        if (debugState):
                            appendTo_DEBUG_log("\nData Returned From The " + str(requestDebugMessage) + " Request:\n",2,the_dict)
                            appendTo_DEBUG_log(convert2json(data) + "\n",4,the_dict)
                    except Exception as err:
                        if (err.msg == 'Unauthorized'):
                            if (debugState):
                                appendTo_DEBUG_log("\n" + str(err),2,the_dict)
                                appendTo_DEBUG_log("\nAUTH_ERROR: User Not Authorized To Access Library",2,the_dict)
                            print("\nAUTH_ERROR: User Not Authorized To Access Library\n" + str(err))
                            print('\n  URL: ' + str(url) + '')
                            exit(0)
                        else:
                            time.sleep(doubling_delay)
                            #doubling_delay value doubles each time the same API request is resent
                            doubling_delay += doubling_delay
                            if (doubling_delay >= (2**retryAttempts)):
                                if (debugState):
                                    appendTo_DEBUG_log("\nAn error occured, a maximum of " + str(retryAttempts) + " attempts met, and no data retrieved from the \"" + requestDebugMessage + "\" lookup.",2,the_dict)
                                print("\nAn error occured, a maximum of " + str(retryAttempts) + " attempts met, and no data retrieved from the \"" + requestDebugMessage + "\" lookup.")
                                print('\n  URL: ' + str(url) + '')
                                exit(0)
                elif (response.getcode() == 204):
                    source = response.read()
                    data = source
                    if (not((response._method == 'DELETE') or (response._method == 'POST'))):
                        the_dict['cached_data'].addEntryToCache(url,data)
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
                    print('\n  URL: ' + str(url) + '')
                    exit(0)
        except HTTPError as err:
            time.sleep(doubling_delay)
            #doubling_delay value doubles each time the same API request is resent
            doubling_delay += doubling_delay
            if (doubling_delay >= (2**retryAttempts)):
                print('\nHTTPError: Unable to get information from server during processing of: ' + requestDebugMessage)
                try:
                    print('  Object: ' + str(url.header_items) + '')
                except:
                    print('  Object:')
                try:
                    print('     URL: ' + str(url.full_url) + '')
                except:
                    print('     URL: ' + str(url) + '')
                try:
                    print('  Method: ' + str(url.method) + '')
                except:
                    print('  Method:')
                try:
                    print('  Header: ' + str(url.headers) + '')
                except:
                    print('  Header:')
                try:
                    print('    Data: ' + str(url.data) + '')
                except:
                    print('    Data:')
                print('\nHTTPError: ' + str(err.status) + ' - ' + str(err.reason))
                if(debugState):
                    appendTo_DEBUG_log('\nHTTPError: Unable to get information from server during processing of: ' + requestDebugMessage,2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Object: ' + str(url.header_items) + '',2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Object:',2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n     URL: ' + str(url.full_url) + '',2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n     URL: ' + str(url) + '',2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Method: ' + str(url.method) + '',2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Method:',2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n  Header: ' + str(url.headers) + '',2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n  Header:',2,the_dict)
                    try:
                        appendTo_DEBUG_log('\n    Data: ' + str(url.data) + '',2,the_dict)
                    except:
                        appendTo_DEBUG_log('\n    Data:',2,the_dict)
                    appendTo_DEBUG_log('\nHTTPError: ' + str(err.status) + ' - ' + str(err.reason),2,the_dict)
                exit(0)
        except URLError as err:
            time.sleep(doubling_delay)
            #doubling_delay value doubles each time the same API request is resent
            doubling_delay += doubling_delay
            if (doubling_delay >= (2**retryAttempts)):
                print('\nURLError: Unable to get information from server during processing of: ' + requestDebugMessage)
                print('\n  URL: ' + str(url) + '')
                print('\n' + str(err.reason))
                if(debugState):
                    appendTo_DEBUG_log('\nURLError: Unable to get information from server during processing of: ' + requestDebugMessage,2,the_dict)
                    appendTo_DEBUG_log('\n  URL: ' + str(url) + '',2,the_dict)
                    appendTo_DEBUG_log('\n' + str(err.reason),2,the_dict)
                exit(0)
        except TimeoutError:
            time.sleep(doubling_delay)
            #doubling_delay value doubles each time the same API request is resent
            doubling_delay += doubling_delay
            if (doubling_delay >= (2**retryAttempts)):
                print('\nTimeoutError: Unable to get information from server during processing of: ' + requestDebugMessage)
                print('\n  URL: ' + str(url) + '')
                print('\nTimeout - Request taking too long')
                if(debugState):
                    appendTo_DEBUG_log('\nTimeoutError: Unable to get information from server during processing of: ' + requestDebugMessage,2,the_dict)
                    appendTo_DEBUG_log('\n  URL: ' + str(url) + '',2,the_dict)
                    appendTo_DEBUG_log('\nTimeout - Request taking too long',2,the_dict)
                exit(0)

    return(data)