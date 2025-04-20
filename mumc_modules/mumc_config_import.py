import sys
from mumc_modules.mumc_config_builder import build_configuration_file
from mumc_modules.mumc_paths_files import doesFileExist
from mumc_modules.mumc_output import open_and_return_file


def cannotFindConfig(init_dict,cmdopt_dict):
    #config not found
    #or
    #config found; but missing DEBUG or version options; automatically start to rebuild new config
    init_dict['DEBUG']=0
    init_dict['advanced_settings']={}
    init_dict['advanced_settings']['UPDATE_CONFIG']=False

    init_dict['config_file_path']=cmdopt_dict['config_file_path']
    init_dict['config_file_name_yaml']=cmdopt_dict['config_file_name_yaml']
    init_dict['config_file_name_yml']=cmdopt_dict['config_file_name_yml']
    init_dict['config_file_name_no_ext']=cmdopt_dict['config_file_name_no_ext']

    build_configuration_file(init_dict)

    #exit gracefully
    sys.exit(0)


#verify specified variables are avaialbe in the config
def assignVarTest(cfg):
    try:
        #check if mumc_config.yaml exists but is blank
        if (not (cfg == None)):
            #removing either 'version:' or 'DEBUG:' from mumc_config.yaml will cause script to attempt rebuilding a new config.yaml
            #try assigning the below variables from the mumc_config.yaml file
            #if any do not exist go to except and return False
            cfg['version']=cfg['version']
            cfg['DEBUG']=cfg['DEBUG']
            assignVarTestSuccessful=True
        else:
            assignVarTestSuccessful=False
    except (AttributeError, ModuleNotFoundError, KeyError):
        assignVarTestSuccessful=False

    return assignVarTestSuccessful


#import config file if it exists; else create the config file
def importConfig(init_dict,cmdopt_dict):
    try:
        #check if default yaml (i.e. config/mumc_config.yaml) or a custom yaml (i.e. /path/to/some_config.yaml) exists
        if (doesFileExist(cmdopt_dict['config_file_path'] / cmdopt_dict['config_file_name_yaml'])):
            #open and return config file
            cfg=open_and_return_file(cmdopt_dict['config_file_path'] / cmdopt_dict['config_file_name_yaml'])
            #make sure a few of the necessary config variables are there
            if (assignVarTest(cfg)):
                init_dict['config_file_path']=cmdopt_dict['config_file_path']
                init_dict['config_file_name_yaml']=cmdopt_dict['config_file_name_yaml']
                init_dict['config_file_name_yml']=cmdopt_dict['config_file_name_yaml']
                init_dict['config_file_name_no_ext']=cmdopt_dict['config_file_name_no_ext']
                #update the cmdopt_dict['config_file_name_yml] entry
                cmdopt_dict['config_file_name_yml']=cmdopt_dict['config_file_name_yaml']
            #assing variable test failed
            else:
                cannotFindConfig(init_dict,cmdopt_dict)
        #check if default yaml (i.e. config/mumc_config.yml) exists
        elif (doesFileExist(cmdopt_dict['config_file_path'] / cmdopt_dict['config_file_name_yml'])):
            #open and return config file
            cfg=open_and_return_file(cmdopt_dict['config_file_path'] / cmdopt_dict['config_file_name_yml'])
            #make sure a few of the necessary config variables are there
            if (assignVarTest(cfg)):
                init_dict['config_file_path']=cmdopt_dict['config_file_path']
                init_dict['config_file_name_yaml']=cmdopt_dict['config_file_name_yml']
                init_dict['config_file_name_yml']=cmdopt_dict['config_file_name_yml']
                init_dict['config_file_name_no_ext']=cmdopt_dict['config_file_name_no_ext']
                #update the cmdopt_dict['config_file_name_yaml] entry
                cmdopt_dict['config_file_name_yaml']=cmdopt_dict['config_file_name_yml']
            #assing variable test failed
            else:
                cannotFindConfig(init_dict,cmdopt_dict)
        else:
            cannotFindConfig(init_dict,cmdopt_dict)
    except (AttributeError, ModuleNotFoundError, KeyError):
        cannotFindConfig(init_dict,cmdopt_dict)

    return cfg,init_dict