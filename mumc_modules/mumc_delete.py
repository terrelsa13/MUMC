
import traceback
import urllib.request as urlrequest
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType
from mumc_modules.mumc_url import requestURL


#api call to delete items
def delete_media_item(itemID,the_dict):
    #build API delete request for specified media item
    url=the_dict['admin_settings']['server']['url'] + '/Items/' + itemID + '?api_key=' + the_dict['admin_settings']['server']['auth_key']

    #specify json in header
    headers = {'accept' : 'application/json'}

    req = urlrequest.Request(url,method='DELETE',headers=headers)

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nSending Delete Request For: " + itemID,3,the_dict)
        appendTo_DEBUG_log("\nURL:\n" + url,3,the_dict)
        appendTo_DEBUG_log("\nRequest:\n" + str(req),4,the_dict)

    #Check if REMOVE_FILES='True'; send request to Emby/Jellyfin to delete specified media item
    if (the_dict['advanced_settings']['REMOVE_FILES']):
        try:
            requestURL(req, the_dict['DEBUG'], 'delete_media_item_request', 3, the_dict)
        except:
            print_byType('\ngeneric exception: ' + str(traceback.format_exc()),True,the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])
        return
    #else in dry-run mode; REMOVE_FILES='False'; exit this function
    else:
        return