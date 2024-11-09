from collections.abc import Mapping
from mumc_modules.mumc_output import appendTo_DEBUG_log


def is_instance(the_element):
    if (not isinstance(the_element, Mapping)):
        raise TypeError('keys_exist() expects a dict-like object as the first argument.')


def keys_exist(the_element, *keys_indexes):
    if isinstance(the_element, Mapping):
        if (not keys_indexes):
            raise ValueError('keys_exist() expects at least one key/index argument.')

        temp_element = the_element
        for key_index in keys_indexes:
            if (isinstance(key_index,int)):
                try:
                    temp_element = temp_element[key_index]
                except:
                    return False
            else:
                if ((temp_element == None) or (key_index not in temp_element)):
                    return False
                temp_element = temp_element[key_index]
        return True
    else:
        return False


def return_key_value(the_element, *keys_indexes):
    if isinstance(the_element, Mapping):
        if len(keys_indexes) < 1:
            raise IndexError('return_key_value() expects at least one key/index argument.')

        temp_element = the_element
        for key_index in keys_indexes:
            try:
                temp_element = temp_element[key_index]
            except (KeyError, IndexError):
                return None
        return temp_element
    else:
        return None


def keys_exist_return_value(the_element, *keys_indexes):
    if (keys_exist(the_element, *keys_indexes)):
        return return_key_value(the_element, *keys_indexes)
    return None  


#Check if json index exists
def does_index_exist(item, indexvalue):
    try:
        exists = item[indexvalue]
    except IndexError:
        return(False)
    return(True)


#Determine if there is a matching item or Determine if an item starts with the other
def get_isItemMatching(item_one,item_two,the_dict):

    match_dict={}
    match_dict['any_match']=False
    match_dict['all_match']=False
    match_dict['match_state']=[]
    match_dict['match_value']=[]

    temp_item_one=[]
    #for paths in Microsoft Windows, replace backslashes in Ids with forward slash
    if (isinstance(item_one,(list,set,tuple))):
        for item1 in item_one:
            if (not (item1 == None)):
                temp_item_one.append(item1.replace('\\','/'))
    elif (isinstance(item_one,str)):
        temp_item_one.append(item_one.replace('\\','/'))
    else:
        raise TypeError('ItemIsMatchingTypeError: item_one is an unexpected type; expecting list, set, tuple, or string.')

    temp_item_two=[]
    #for paths in Microsoft Windows, replace backslashes in Ids with forward slash
    if (isinstance(item_two,(list,set,tuple))):
        for item2 in item_two:
            if (not (item2 == None)):
                temp_item_two.append(item2.replace('\\','/'))
    elif (isinstance(item_two,str)):
        temp_item_two.append(item_two.replace('\\','/'))
    else:
        raise TypeError('ItemIsMatchingTypeError: item_two is an unexpected type; expecting list, set, tuple, or string.')

    #determine if media Id matches one of the other Ids
    for single_item_one in temp_item_one:
            for single_item_two in temp_item_two:
                if (the_dict['DEBUG']):
                    appendTo_DEBUG_log('\n\nComparing the below two items',3,the_dict)
                    appendTo_DEBUG_log('\n\'' + str(single_item_one) + '\'' + ':' + '\'' + str(single_item_two) + '\'',3,the_dict)

                if ((not ((single_item_one == '') or (single_item_two == ''))) and (not ((single_item_one == None) or (single_item_two == None)))):
                    if (single_item_one == single_item_two):
                        #found a full match; return true and the matching value
                        match_dict['match_state'].append(True)
                        match_dict['match_value'].append(single_item_one)
                    else:
                        #found no match; return false and the a None value
                        match_dict['match_state'].append(False)
                        match_dict['match_value'].append(None)
    
    match_dict['any_match']=any(match_dict['match_state'])
    #only check for all() if list is not empty
    if (not (match_dict['match_state'] == [])):
        match_dict['all_match']=all(match_dict['match_state'])
    
    return match_dict