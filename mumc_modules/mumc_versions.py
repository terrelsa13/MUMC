import platform
from mumc_modules.mumc_url import requestURL,build_request_message


#Get the current script version
def get_script_version():
    return '5.7.0'


#Get the min config version
def get_min_config_version():
    return '5.0.0'


#Get the current Emby/Jellyfin server version
def get_server_version(the_dict):

    lookupTopic="get_server_version"

    #Get additonal item information
    url=the_dict['admin_settings']['server']['url'] + '/System/Info'

    req=build_request_message(url=url,the_dict=the_dict)

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