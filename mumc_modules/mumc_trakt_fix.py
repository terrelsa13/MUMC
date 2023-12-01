
import urllib.request as urlrequest
from datetime import datetime
from mumc_modules.mumc_output import appendTo_DEBUG_log,convert2json
from mumc_modules.mumc_url import requestURL


#when played media item is missing the LastPlayedDate, send the current date-time to the server as a starting point
def modify_lastPlayedDate(item,userKey,the_dict):

    serverURL=the_dict['server_url']
    authKey=the_dict['auth_key']

    #save current date-time with specified format to item["UserData"]["LastPlayedDate"]
    item["UserData"]["LastPlayedDate"]=str(datetime.strftime(the_dict['date_time_now'], "%Y-%m-%dT%H:%M:%S.000Z"))

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nAdd missing LastPlayedDate of " + str(item["UserData"]["LastPlayedDate"]) + " to media item with Id: " + str(item["Id"]),3)

    #convert item to json element
    DATA = convert2json(item["UserData"])
    #encode json element
    DATA = DATA.encode('utf-8')

    #specify json in header
    headers = {'Content-Type' : 'application/json'}

    #build full POST request
    req = urlrequest.Request(url=serverURL + '/Users/' + userKey + '/Items/' + item["Id"] + '/UserData?api_key=' + authKey, data=DATA, method='POST', headers=headers)

    #API POST for UserData modification
    requestURL(req, the_dict['DEBUG'], 'add_missing_LastPlayedDate', 3, the_dict)