import traceback
from mumc_modules.mumc_output import appendTo_DEBUG_log,print_byType
from mumc_modules.mumc_url import requestURL,build_request_message


#api call to delete items
def delete_media_item(itemID,the_dict):
    #Below are the x3 ways to delete media items

#########################################################################################################
    #1
    #build API delete request for specified media item (only single itemIds)
    url=the_dict['admin_settings']['server']['url'] + '/Items/' + str(itemID) #DELETE
    req=build_request_message(url,the_dict,method='DELETE')
#########################################################################################################
    #2
    #build API delete request for specified media item (multiple comma separated itemIds)
    #url=the_dict['admin_settings']['server']['url'] + '/Items?Ids=' + str(itemID) #DELETE
    #req=build_request_message(url,the_dict,method='DELETE')
#########################################################################################################
    #3
    #build API delete request for specified media item (multiple comma separated itemIds)
    #url=the_dict['admin_settings']['server']['url'] + '/Items/Delete?Ids=' + str(itemID) #POST
    #req=build_request_message(url,the_dict,method='POST')
#########################################################################################################

    if (the_dict['DEBUG']):
        appendTo_DEBUG_log("\nSending Delete Request For: " + itemID,3,the_dict)
        appendTo_DEBUG_log("\nURL:\n" + url,3,the_dict)
        appendTo_DEBUG_log("\nRequest:\n" + str(req),4,the_dict)

    #Check if REMOVE_FILES='True'; send request to Emby/Jellyfin to delete specified media item
    if (the_dict['advanced_settings']['REMOVE_FILES']):
        try:
            requestURL(req, the_dict['DEBUG'], 'delete_media_item_request_for_' + itemID, 3, the_dict)
        except:
            print_byType('\nGeneric exception occured for media with Id: ' + str(itemID),True,the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])
            print_byType('\nGeneric exception occured: ' + str(traceback.format_exc()),True,the_dict,the_dict['advanced_settings']['console_controls']['warnings']['script']['formatting'])
        return
    #else in dry-run mode; REMOVE_FILES='False'; exit this function
    else:
        return