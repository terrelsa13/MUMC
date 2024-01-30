

#emby or jellyfin?
def get_brand():
    defaultbrand='emby'
    valid_brand=False
    selected_brand=defaultbrand
    while (valid_brand == False):
        print('0 - emby\n1 - jellyfin')
        brand=input('Enter number for server branding (default ' + defaultbrand + '): ')
        if (brand == ''):
            valid_brand = True
        elif (brand == '0'):
            valid_brand = True
        elif (brand == '1'):
            valid_brand = True
            selected_brand='jellyfin'
        else:
            print('\nInvalid choice. Try again.\n')
    return(selected_brand)


#ip address or url?
def get_url():
    defaulturl='http://localhost'
    url=input('Enter server ip or name (default ' + defaulturl + '): ')
    if (url == ''):
        return(defaulturl)
    else:
        if (url.find('://',3,8) >= 0):
            return(url)
        else:
           url='http://' + url
           print('Assuming server ip or name is: ' + url)
           return(url)


#http or https port?
def get_port():
    defaultport='8096'
    valid_port=False
    while (valid_port == False):
        print('If you have not explicity changed this option, press enter for default.')
        print('Space for no port.')
        port=input('Enter port (default ' + defaultport + '): ')
        if (port == ''):
            valid_port=True
            return(defaultport)
        elif (port == ' '):
            valid_port=True
            return('')
        else:
            try:
                port_float=float(port)
                if ((port_float % 1) == 0):
                    port_int=int(port_float)
                    if ((int(port_int) >= 1) and (int(port_int) <= 65535)):
                        valid_port=True
                        return(str(port_int))
                    else:
                        print('\nInvalid port. Try again.\n')
                else:
                    print('\nInvalid port. Try again.\n')
            except:
                print('\nInvalid port. Try again.\n')


#base url?
def get_base(brand):
    defaultbase='emby'
    if (brand == defaultbase):
        print('Using "/' + defaultbase + '" as base url')
        return(defaultbase)
    else:
        print('If you have not explicity changed this option in jellyfin, press enter for default.')
        print('For example: http://example.com/<baseurl>')
        base=input('Enter base url (default n/a): ')
        if (base == ''):
            return(base)
        else:
            if (base.find('/',0,1) == 0):
                return(base[1:len(base)])
            else:
                return(base)


#admin username?
def get_admin_username():
    return(input('Enter admin username: '))


#admin password?
def get_admin_password():
    print('Plain text password used to grab authentication key; password is not stored.')
    password=input('Enter admin password: ')
    return(password)


#Blacklisting or Whitelisting?
def get_library_setup_behavior(library_setup_behavior=None):
    defaultbehavior='blacklist'
    valid_behavior=False
    while (valid_behavior == False):
        print('Decide how the script will use the libraries chosen for each user.')
        print('0 - blacklist - Chosen libraries will blacklisted.')
        print('                All other libraries will be whitelisted.')
        print('1 - whitelist - Chosen libraries will whitelisted.')
        print('                All other libraries will be blacklisted.')
        if (not (library_setup_behavior == None)):
            if (library_setup_behavior.casefold() == 'blacklist'):
                print('')
                print('Script previously setup using \'0 - ' + library_setup_behavior + '\'.')
            elif (library_setup_behavior.casefold() == 'whitelist'):
                print('')
                print('Script previously setup using \'1 - ' + library_setup_behavior + '\'.')
        behavior=input('Choose how the script will use the chosen libraries. (default 0 - ' + defaultbehavior + '): ')
        if (behavior == ''):
            valid_behavior=True
            return(defaultbehavior)
        elif (behavior == '0'):
            valid_behavior=True
            return(defaultbehavior)
        elif (behavior == '1'):
            valid_behavior=True
            return('whitelist')
        else:
            print('\nInvalid choice. Try again.\n')


#Library behavior?
def get_library_matching_behavior(library_matching_behavior=None):
    defaultbehavior='byId'
    valid_behavior=False
    while (valid_behavior == False):
        print('Decide how the script will match media items to libraries.')
        print('0 - byId - Media items will be matched to libraries using \'LibraryIds\'.')
        print('1 - byPath - Media items will be matched to libraries using \'Paths\'.')
        print('2 - byNetworkPath - Media items will be matched to libraries using \'NetworkPaths\'.')
        print('   If your libraries do not have a \'Shared Network Folder\' you must filter byPath.')
        print('   If your libraries have a \'Shared Network Folder\' you must filter byNetworkPath.')
        print('   Filtering byId does not have the above limitations.')
        if (not (library_matching_behavior == None)):
            if ((library_matching_behavior.casefold() == 'byid') or
                (library_matching_behavior.casefold() == 'bypath') or
                (library_matching_behavior.casefold() == 'bynetworkpath')):
                print('')
                if (library_matching_behavior.casefold() == 'byid'):
                    print('Script previously setup to match media items to libraries 0 - ' + library_matching_behavior + '.')
                elif (library_matching_behavior.casefold() == 'bypath'):
                    print('Script previously setup to match media items to libraries 1 - ' + library_matching_behavior + '.')
                else: #(library_matching_behavior.casefold() == 'bynetworkpath'):
                    print('Script previously setup to match media items to libraries 2 - ' + library_matching_behavior + '.')
        behavior=input('Choose how the script will match media items to libraries. (default 0 - ' + defaultbehavior + '): ')
        if (behavior == ''):
            valid_behavior=True
            return(defaultbehavior)
        elif (behavior == '0'):
            valid_behavior=True
            return(defaultbehavior)
        elif (behavior == '1'):
            valid_behavior=True
            return('byPath')
        elif (behavior == '2'):
            valid_behavior=True
            return('byNetworkPath')
        else:
            print('\nInvalid choice. Try again.\n')


#Blacktagging or Whitetagging String Name?
def get_tag_name(tagbehavior,existingtag):
    repeat_tags=''
    tags_to_remove=[]
    valid_tag=False
    while (valid_tag == False):
        print('Enter the desired ' + tagbehavior + ' name. Do not use backslash \'\\\'.')
        print('Use a comma \',\' to seperate multiple tag names.')
        print('Empty space(s) at the beginning or end of tags will be removed')
        print(' Ex: tagname,tag name,tag-name')
        print('Leave blank to disable the ' + tagbehavior + 'ging functionality.')
        inputtagname=input('Input desired ' + tagbehavior + 's: ')

        #Remove duplicates
        inputtagname = ','.join(set(inputtagname.split(',')))
        if (inputtagname == ''):
            valid_tag=True
            return []
        else:
            if (inputtagname.find('\\') <= 0):
                #replace single quote (') with backslash-single quote (\')
                inputtagname=inputtagname.replace('\'','\\\'')
                valid_tag=True
                inputtagname_return=inputtagname.split(',')
                #clean space(s) at the beginning and end of each tag entry
                for inputtagname_temp in inputtagname_return:
                    inputtagname_clean=inputtagname_temp.strip()
                    inputtagname_return[inputtagname_return.index(inputtagname_temp)]=inputtagname_clean
                inputtagname_return=list(set(inputtagname_return))
                for inputtag in inputtagname_return:
                    if (not (inputtag == '')):
                        #existingtag_split=existingtag.split(',')
                        for donetag in existingtag:
                            if (inputtag == donetag):
                                valid_tag=False
                                if (not (repeat_tags)):
                                    repeat_tags+=inputtag
                                else:
                                    repeat_tags+=(', ' + inputtag)
                    else:
                        tags_to_remove.append(inputtag)
                #remove any blank tags
                for remove_tag in tags_to_remove:
                    inputtagname_return.remove(remove_tag)
                if (valid_tag):
                    return inputtagname_return
                else:
                    print('\nFound already used tag(s): ' + repeat_tags)
                    print('Cannot use the same tag for blacktags and whitetags.\n')
                    print('Use a comma \',\' to seperate multiple tag names. Try again.\n')
            else:
                print('\nDo not use backslash \'\\\'. Try again.\n')


def get_show_disabled_users():
    defaultvalue=True
    valid_value=False
    while (valid_value == False):
        print('Decide if users disabled in the GUI should be shown.')
        print('0 - Hide disabled users')
        print('1 - Show disabled users')
        selection=input('Enter number (default 1 - Show disabled users): ')
        if (selection == ''):
            valid_value = True
        elif (selection == '0'):
            valid_value = True
            defaultvalue=False
        elif (selection == '1'):
            valid_value = True
        else:
            print('\nInvalid choice. Try again.\n')
    return(defaultvalue)


def get_user_and_library_selection_type(library_setup_behavior):
    defaultvalue=0
    valid_value=False
    while (valid_value == False):
        print('Decide how to select users and/or libraries.')
        #print('0 - Select users and libraries; i.e. Select specific users and the specific libraries to be ' + str(library_setup_behavior) + 'ed for each user.')
        #print('1 - Select users only i.e. Selected users will have all libraries ' + str(library_setup_behavior) + 'ed according to their access policy.')
        #print('2 - Select libraries only i.e. Selected libraries will be ' + str(library_setup_behavior) + 'ed for all users according to their access polity.')
        #print('')
        print('0 - Select users and libraries.')
        print('    Select specific users and the specific libraries to be ' + str(library_setup_behavior) + 'ed for each user.')
        print('1 - Select users only.')
        print('    Selected users will have all libraries ' + str(library_setup_behavior) + 'ed according to their access policy.')
        print('2 - Select libraries only.')
        print('    Selected libraries will be ' + str(library_setup_behavior) + 'ed for all users according to their access policy.')
        selection=input('Enter number (default 0 - Select users and libraries): ')
        if (selection == ''):
            valid_value = True
        elif (selection == '0'):
            valid_value = True
        elif (selection == '1'):
            valid_value = True
            defaultvalue=1
        elif (selection == '2'):
            valid_value = True
            defaultvalue=2
        else:
            print('\nInvalid choice. Try again.\n')
    return(defaultvalue)