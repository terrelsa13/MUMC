
import multiprocessing
from mumc_modules.mumc_output import appendTo_DEBUG_log


#Check if *keys (nested) exists in `element` (dict or list).
def keys_exist(the_element, *keys_indexes):

    if (not (isinstance(the_element, dict) or isinstance(the_element, multiprocessing.managers.DictProxy))):
        raise AttributeError('keys_exist() expects dict as first argument.')
    if len(keys_indexes) == 0:
        raise AttributeError('keys_exist() expects at least two arguments, one given.')

    temp_element = the_element
    for key_index in keys_indexes:
        try:
            temp_element = temp_element[key_index]
        except KeyError:
            return False
    return True


#Check if *keys (nested) exists in `element` (dict or list).
def return_key_value(the_element, *keys_indexes):

    if not isinstance(the_element, dict):
        raise AttributeError('return_key_value() expects dict as first argument.')
    if len(keys_indexes) == 0:
        raise AttributeError('return_key_value() expects at least two arguments, one given.')

    temp_element = the_element
    for key_index in keys_indexes:
        try:
            temp_element = temp_element[key_index]
        except KeyError:
            return None
    return temp_element


#Check if json index exists
def does_index_exist(item, indexvalue, the_dict):
    try:
        exists = item[indexvalue]
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n" + str(indexvalue) + " exist in " + str(item),2,the_dict)
    except IndexError:
        if (the_dict['DEBUG']):
            appendTo_DEBUG_log("\n" + str(indexvalue) + " does NOT exist in " + str(item),2,the_dict)
        return(False)
    return(True)


#Determine if there is a matching item or Determine if an item starts with the other
def get_isItemMatching_doesItemStartWith(item_one,item_two,the_dict):
    #for Ids in Microsoft Windows, replace backslashes in Ids with forward slash
    item_one = item_one.replace('\\','/')
    item_two = item_two.replace('\\','/')

    #read and split Ids to compare to
    item_one_split=item_one.split(',')
    item_two_split=item_two.split(',')

    #DEBUG log formatting
    if (the_dict['DEBUG']):
        appendTo_DEBUG_log('\n',1,the_dict)

    #determine if media Id matches one of the other Ids
    for single_item_one in item_one_split:
            for single_item_two in item_two_split:
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log('\nComparing the below two items',3,the_dict)
                    appendTo_DEBUG_log('\n\'' + str(single_item_one) + '\'' + ':' + '\'' + str(single_item_two) + '\'',3,the_dict)
                if ((not (single_item_one == '')) and (not (single_item_two == '')) and
                    (not (single_item_one == "''")) and (not (single_item_two == "''")) and
                    (not (single_item_one == '""')) and (not (single_item_two == '""'))):
                    if (single_item_one == single_item_two):
                        #found a match; return true and the matching value
                        return True,single_item_one
                    elif (single_item_two.startswith(single_item_one)):
                        #found a match; return true and the matching value
                        return True,single_item_one

    #nothing matched; return false and empty string
    return False,''