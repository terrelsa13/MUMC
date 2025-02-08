import platform
from mumc_modules.mumc_url import requestURL,build_emby_jellyfin_request_message


#Get the current script version
def get_script_version():
    return '5.11.0-alpha'


#Get the min config version
def get_min_config_version():
    return '5.0.0'


#Get the min Python version
def get_min_python_version():
    return '3.10.0'


#Get the current Emby/Jellyfin server version
def get_server_version(the_dict):

    lookupTopic="get_server_version"

    #Get additonal item information
    url=the_dict['admin_settings']['server']['url'] + '/System/Info'

    req=build_emby_jellyfin_request_message(url=url,the_dict=the_dict)

    #api call
    ServerInfo=requestURL(req, the_dict['DEBUG'], lookupTopic, the_dict['admin_settings']['api_controls']['attempts'],the_dict)

    return(ServerInfo['Version'])


#Get the current Python verison
def get_python_version():
    return(platform.python_version())


#Get the operating system information
def get_operating_system_info():
    return(platform.platform())


#Get major, minor and patch version numbers along with release version information
def get_semantic_version_parts(version):
    semVersionDict={}
    try:
        semVersionDict['major']=int(get_major_semantic_version(version))
        semVersionDict['minor']=int(get_minor_semantic_version(version))
        semVersionDict['patch']=int(get_patch_semantic_version(version))
        semVersionDict['release']=str(get_prerelease_semantic_version(version))
        return semVersionDict
    except:
        raise ValueError(f"{version} is not formatted correctly")


#Get major semanic version number
def get_major_semantic_version(version):
    verParts = version.split(".")
    return verParts[0]


#Get minor semanic version number
def get_minor_semantic_version(version):
    verParts = version.split(".")
    return verParts[1]


#Get patch semanic version number
def get_patch_semantic_version(version):
    verParts = version.split(".")
    if (verParts[2].find("-") >= 0):
        verPreRel = version.split("-")
        verParts[2] = verParts[2].replace("-"+verPreRel[1],"")
    return verParts[2]


#Get release version information
def get_prerelease_semantic_version(version):
    verParts = version.split(".")
    if (verParts[2].find("-") >= 0):
        verPreRel = version.split("-")
        return verPreRel[1]
    else:
        return "stable"


def checkSemanticVersion(currentVersion,minVersion,maxVersion=None):
    current_version=get_semantic_version_parts(currentVersion)
    min_version=get_semantic_version_parts(minVersion)
    if (not (maxVersion == None)):
        max_version=get_semantic_version_parts(maxVersion)

    version_ok=True

    if (current_version['major'] < min_version['major']):
        version_ok=False
    else:
        if (current_version['minor'] < min_version['minor']):
            version_ok=False
        else:
            if (current_version['patch'] < min_version['patch']):
                version_ok=False

    if (not (maxVersion == None)):
        if (current_version['major'] > min_version['major']):
            version_ok=False
        else:
            if (current_version['minor'] > min_version['minor']):
                version_ok=False
            else:
                if (current_version['patch'] >   min_version['patch']):
                    version_ok=False

    return version_ok


def checkYAMLVersion(cfg,init_dict):

    if (cfg['version'] == ''):
        return 'ConfigVersionError: Config version is blank: \'\''\
                '\n Please use a config with a version greater than or equal to: '\
                + init_dict['min_config_version'] + ' or create a new config \n'
    else:
        config_version_ok=checkSemanticVersion(cfg['version'],init_dict['min_config_version'])

    if (not (config_version_ok)):
        return 'ConfigVersionError: Config version: ' + cfg['version'] + ' is not supported by script version: '\
                + init_dict['script_version'] + '\n Please use a config with a version greater than or equal to: '\
                + init_dict['min_config_version'] + ' or create a new config \n'
    else:
        return ''