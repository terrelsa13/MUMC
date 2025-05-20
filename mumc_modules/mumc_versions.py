import platform
from mumc_modules.mumc_url import requestURL,build_emby_jellyfin_request_message,build_radarr_request_message,build_sonarr_request_message


#Get the current script version
def get_script_version():
    return '5.11.17-beta'


#Get the min config version
def get_min_config_version():
    return '5.0.0'


#Get the max config version
def get_max_config_version():
    max_version=''
    #max_version='#.#.#-release'

    if (max_version == ''):
        max_version=get_script_version()

    return max_version


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
    ServerInfo=requestURL(the_dict, req, the_dict['DEBUG'], lookupTopic, the_dict['admin_settings']['api_controls']['attempts'])

    return(ServerInfo['Version'])


#Get the current Python verison
def get_python_version():
    return(platform.python_version())


#Get the Radarr version
def get_radarr_version(arrInfo,the_dict):
    lookupTopic="get_radarr_version"

    #Get additonal item information
    url=arrInfo['url'] + '/api/v3/system/status'

    req=build_radarr_request_message(url=url,arrInfo=arrInfo)

    #api call
    ServerInfo=requestURL(the_dict, req, the_dict['DEBUG'], lookupTopic, the_dict['admin_settings']['api_controls']['attempts'])

    return(ServerInfo['version'])


#Get the Sonarr version
def get_sonarr_version(arrInfo,the_dict):
    lookupTopic="get_sonarr_version"

    #Get additonal item information
    url=arrInfo['url'] + '/api/v3/system/status'

    req=build_sonarr_request_message(url=url,arrInfo=arrInfo)

    #api call
    ServerInfo=requestURL(the_dict, req, the_dict['DEBUG'], lookupTopic, the_dict['admin_settings']['api_controls']['attempts'])

    return(ServerInfo['version'])


#Get the operating system information
def get_operating_system_info():
    return(platform.platform())


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


#Get major, minor and patch version numbers along with release version information
def get_semantic_version_parts(version):
    semVersionDict={}
    try:
        semVersionDict['major']=abs(int(get_major_semantic_version(version)))
        semVersionDict['minor']=abs(int(get_minor_semantic_version(version)))
        semVersionDict['patch']=abs(int(get_patch_semantic_version(version)))
        semVersionDict['release']=str(get_prerelease_semantic_version(version))
        return semVersionDict
    except:
        raise ValueError(f"version: {version} is not formatted correctly in the configuration file")


def compareSemanticVersions(currentVersion,minVersion,maxVersion=None):
    current_version=get_semantic_version_parts(currentVersion)
    currentMajorStr=str(current_version['major'])
    currentMinorStr=str(current_version['minor'])
    currentPatchStr=str(current_version['patch'])
    currentMajorStrLen=len(currentMajorStr)
    currentMinorStrLen=len(currentMinorStr)
    currentPatchStrLen=len(currentPatchStr)

    min_version=get_semantic_version_parts(minVersion)
    minMajorStr=str(min_version['major'])
    minMinorStr=str(min_version['minor'])
    minPatchStr=str(min_version['patch'])
    minMajorStrLen=len(minMajorStr)
    minMinorStrLen=len(minMinorStr)
    minPatchStrLen=len(minPatchStr)

    if (not (maxVersion == None)):
        max_version=get_semantic_version_parts(maxVersion)
        maxMajorStr=str(max_version['major'])
        maxMinorStr=str(max_version['minor'])
        maxPatchStr=str(max_version['patch'])
        maxMajorStrLen=len(maxMajorStr)
        maxMinorStrLen=len(maxMinorStr)
        maxPatchStrLen=len(maxPatchStr)

    if (currentMajorStrLen < minMajorStrLen):
        currentMajorStr=currentMajorStr.zfill(minMajorStrLen)
    elif (currentMajorStrLen > minMajorStrLen):
        minMajorStr=minMajorStr.zfill(currentMajorStrLen)

    if (currentMinorStrLen < minMinorStrLen):
        currentMinorStr=currentMinorStr.zfill(minMinorStrLen)
    elif (currentMinorStrLen > minMinorStrLen):
        minMinorStr=minMinorStr.zfill(currentMinorStrLen)

    if (currentPatchStrLen < minPatchStrLen):
        currentPatchStr=currentPatchStr.zfill(minPatchStrLen)
    elif (currentPatchStrLen > minPatchStrLen):
        minPatchStr=minPatchStr.zfill(currentPatchStrLen)

    if (not (maxVersion == None)):
        if (currentMajorStrLen < maxMajorStrLen):
            currentMajorStr=currentMajorStr.zfill(maxMajorStrLen)
        elif (currentMajorStrLen > maxMajorStrLen):
            maxMajorStr=maxMajorStr.zfill(currentMajorStrLen)

        if (currentMinorStrLen < maxMinorStrLen):
            currentMinorStr=currentMinorStr.zfill(maxMinorStrLen)
        elif (currentMinorStrLen > maxMinorStrLen):
            maxMinorStr=maxMinorStr.zfill(currentMinorStrLen)

        if (currentPatchStrLen < maxPatchStrLen):
            currentPatchStr=currentPatchStr.zfill(maxPatchStrLen)
        elif (currentPatchStrLen > maxPatchStrLen):
            maxPatchStr=maxPatchStr.zfill(currentPatchStrLen)

        if (minMajorStrLen < maxMajorStrLen):
            minMajorStr=minMajorStr.zfill(maxMajorStrLen)

        if (minMinorStrLen < maxMinorStrLen):
            minMinorStr=minMinorStr.zfill(maxMinorStrLen)

        if (minPatchStrLen < maxPatchStrLen):
            minPatchStr=minPatchStr.zfill(maxPatchStrLen)

    currentVersion=int('1' + currentMajorStr + currentMinorStr + currentPatchStr)
    minVersion=int('1' + minMajorStr + minMinorStr + minPatchStr)
    if (not (maxVersion == None)):
        maxVersion=int('1' + maxMajorStr + maxMinorStr + maxPatchStr)

    version_ok=True

    if (currentVersion < minVersion):
        version_ok=False

    if (not (maxVersion == None)):
        if (currentVersion > maxVersion):
            version_ok=False

    return version_ok


def checkYAMLVersion(cfg,init_dict):

    if (cfg['version'] == ''):
        return False
    else:
        config_version_ok=compareSemanticVersions(cfg['version'],init_dict['min_config_version'],init_dict['max_config_version'])

    if (not (config_version_ok)):
        return False
    else:
        return True