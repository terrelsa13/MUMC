import urllib.request as urlrequest
from datetime import datetime
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json
from mumc_modules.mumc_url import requestURL
from mumc_modules.mumc_server_type import isEmbyServer


#when played media item is missing the LastPlayedDate, send the current date-time to the server as a starting point
def modify_lastPlayedDate(item,userKey,the_dict):

    serverURL=the_dict['admin_settings']['server']['url']
    authKey=the_dict['admin_settings']['server']['auth_key']

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\n['UserData']['LastPlayedDate'] from server before requesting update:\n" + str(convert2json(item["UserData"])),2,the_dict)

    #save current date-time with specified format to item["UserData"]["LastPlayedDate"]
    item['UserData']['LastPlayedDate']=str(datetime.strftime(the_dict['date_time_now'], "%Y-%m-%dT%H:%M:%S.0000000Z"))

    #emby and jellyfin have different formatting for  ['UserData']['LastPlayedDate']
    if (isEmbyServer()):
        lastPlayedDate=str(datetime.strftime(the_dict['date_time_now'], "%Y%m%d%H%M%S"))
    else:
        lastPlayedDate=str(datetime.strftime(the_dict['date_time_now'], "%Y-%m-%dT%H:%M:%S.0000000Z"))

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nAdd missing LastPlayedDate of " + str(item['UserData']['LastPlayedDate']) + " to media item with Id: " + str(item["Id"]),2,the_dict)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nPending ['UserData']['LastPlayedDate'] update request to be sent to server:\n" + str(convert2json(item['UserData'])),2,the_dict)

    #specify json in header
    headers = {'accept' : 'application/json'}

    #build full POST request    
    req = urlrequest.Request(url=serverURL + '/Users/' + userKey + '/PlayedItems/' + item['Id'] + '?dateplayed=' + lastPlayedDate + '&api_key=' + authKey, method='POST', headers=headers)

    #API POST for UserData modification
    requestURL(req, the_dict['DEBUG'], 'add_missing_LastPlayedDate', 3, the_dict)