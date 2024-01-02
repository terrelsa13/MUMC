from collections.abc import Mapping
from mumc_modules.mumc_output import appendTo_DEBUG_log


def is_instance(the_element):
    if not isinstance(the_element, Mapping):
        raise TypeError('keys_exist() expects a dict-like object as the first argument.')


def keys_exist(the_element, *keys_indexes):
    is_instance(the_element)
    if not keys_indexes:
        raise ValueError('keys_exist() expects at least one key/index argument.')

    temp_element = the_element
    for key_index in keys_indexes:
        if key_index not in temp_element:
            return False
        temp_element = temp_element[key_index]
    return True


def return_key_value(the_element, *keys_indexes):
    is_instance(the_element)
    if len(keys_indexes) < 1:
        raise IndexError('return_key_value() expects at least one key/index argument.')

    temp_element = the_element
    for key_index in keys_indexes:
        try:
            temp_element = temp_element[key_index]
        except (KeyError, IndexError):
            return None
    return temp_element


def keys_exist_return_value(the_element, *keys_indexes):
    if (keys_exist(the_element, *keys_indexes)):
        return return_key_value(the_element, *keys_indexes)
    return None  


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

                #if ((not (single_item_one == '')) and (not (single_item_two == '')) and
                    #(not (single_item_one == "''")) and (not (single_item_two == "''")) and
                    #(not (single_item_one == '""')) and (not (single_item_two == '""'))):
                if (single_item_one and single_item_two):
                    if ((single_item_one == single_item_two) or
                         single_item_two.startswith(single_item_one)):
                        #found a match; return true and the matching value
                        return True,single_item_one

    #nothing matched; return false and empty string
    return False,''