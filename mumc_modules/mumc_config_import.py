import importlib
import time
import yaml
import sys
from mumc_modules.mumc_configcheck_legacy import cfgCheckLegacy
from mumc_modules.mumc_config_builder import build_configuration_file
from mumc_modules.mumc_paths_files import getFileExtension,add_to_PATH,doesFileExist
from mumc_modules.mumc_console_info import print_containerized_config_missing
from mumc_modules.mumc_config_convert import convert_legacyConfigToYAML


def cannotFindConfig(init_dict,cmdopt_dict):
    if (cmdopt_dict['containerized']):
        print_containerized_config_missing(init_dict)
        time.sleep(5)
        importConfig(init_dict,cmdopt_dict)
        print('00C')
    else:
        print('00D')
        #config not found
        #or
        #config found; but missing DEBUG or server_brand options; automatically start to rebuild new config
        init_dict['DEBUG']=0
        init_dict['advanced_settings']={}
        init_dict['advanced_settings']['UPDATE_CONFIG']=False
        if ((cmdopt_dict['altConfigPath'] == None) and (cmdopt_dict['altConfigFileExt'] == None)):
            init_dict['mumc_path']=init_dict['mumc_path']
            init_dict['config_file_name_yaml']=init_dict['config_file_name_yaml']
        else:
            init_dict['mumc_path']=cmdopt_dict['altConfigPath']
            init_dict['config_file_name_yaml']=cmdopt_dict['altConfigFileExt']
        build_configuration_file(init_dict)
        print('00E')
        #exit gracefully
        sys.exit(0)


#verify specified variables are avaialbe in the config
def assignVarTest(init_dict,cmdopt_dict,cfg):
    print('00F')
    try:
        print('00G')
        #check if mumc_config.yaml exists but is blank
        if (not (cfg == None)):
            print('00H')
            #removing any of the test variables from mumc_config.yaml will cause script to rebuild a new config.yaml
            #try assigning the below variables from the mumc_config.yaml file
            #if any do not exist go to except and rebuild the mumc_config.yaml file
            init_dict['version']=cfg['version']
            init_dict['DEBUG']=cfg['DEBUG']
        else:
            print('00I')
            raise ModuleNotFoundError

    except (AttributeError, ModuleNotFoundError, KeyError):
        print('00J')
        cannotFindConfig(init_dict,cmdopt_dict)

    return init_dict


def importConfig(init_dict,cmdopt_dict):
    try:
        print('00K')
        #Attempt to import the alternate config file as cfg
        #Check for the .py extension and no spaces or periods in the module name
        if (cmdopt_dict['altConfigInfo']):
            print('00L')
            #Insert alternate config to path at the top of the path list so it can be searched and imported first
            #We want the alternate config path to be searched first incase the the alternate config is also named mumc_config.yaml
            #Searching the alternate config path first will allow the alternate config file to be found first
            add_to_PATH(cmdopt_dict['altConfigPath'],0)
            print('00M')

            #check if yaml config
            if ((getFileExtension(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt']) == '.yaml') or
               (getFileExtension(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt']) == '.yml')):
                print('00N')
                #open alternate yaml config
                with open(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)
                print('00O')

                init_dict['mumc_path']=cmdopt_dict['altConfigPath']
                init_dict['config_file_name_yaml']=cmdopt_dict['altConfigFileExt']
                print('00P')

            #check if legacy config
            else: #if (getFileExtension(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileExt']) == '.py'):
                print('00Q')
                #Cannot do a direct import using a variable; use the importlib.import_module instead
                #Also cannot import the whole path; add the path to path then import by filename
                cfg = importlib.import_module(cmdopt_dict['altConfigFileNoExt'],cmdopt_dict['altConfigInfo'])

                #run a config check on the legacy mumc_config.py before converting to mumc_config.yaml
                legacy_dict=cfgCheckLegacy(cfg,init_dict)

                print('00R')
                #function to convert legacy config to mumc_config.yaml
                convert_legacyConfigToYAML(cfg,cmdopt_dict['altConfigPath'],cmdopt_dict['altConfigFileNoExt'])
                print('00S')

                with open(cmdopt_dict['altConfigPath'] / cmdopt_dict['altConfigFileNoExt'] + '.yaml', 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)
                print('00T')

                init_dict['mumc_path']=cmdopt_dict['altConfigPath']
                init_dict['config_file_name_yaml']=cmdopt_dict['altConfigFileNoExt'] + '.yaml'

            print('00U')
            #make sure a few of the necessary config variables are there
            init_dict=assignVarTest(init_dict,cmdopt_dict,cfg)

        else:
            print('00V')
            if (doesFileExist(init_dict['mumc_path'] / init_dict['config_file_name_yaml'])):
                print('00W')
                #try importing the mumc_config.yaml file
                #if mumc_config.yaml file does not exist try importing the config/mumc_config.py file
                with open(init_dict['mumc_path'] / init_dict['config_file_name_yaml'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)
                print('00X')

                #make sure a few of the necessary config variables are there
                init_dict=assignVarTest(init_dict,cmdopt_dict,cfg)
            elif (doesFileExist(init_dict['mumc_path'] / init_dict['config_file_name_yml'])):
                print('00Y')
                #try importing the mumc_config.yaml file
                #if mumc_config.yaml file does not exist try importing the config/mumc_config.py file
                with open(init_dict['mumc_path'] / init_dict['config_file_name_yml'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)

                print('00Z')
                init_dict['config_file_name_yaml']=init_dict['config_file_name_yml']

                #make sure a few of the necessary config variables are there
                init_dict=assignVarTest(init_dict,cmdopt_dict,cfg)
                print('00!')
            elif (doesFileExist(init_dict['mumc_path_config_dir'] / init_dict['config_file_name_yaml'])):
                print('00@')
                #try importing the config/mumc_config.yaml file
                #if config/mumc_config.yaml file does not exist try importing the legacy mumc_config.py file
                #with open(init_dict['mumc_path'] / init_dict['config_file_name_yaml'], 'r') as mumc_config_yaml:
                with open(init_dict['mumc_path_config_dir'] / init_dict['config_file_name_yaml'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)
                print('00#')

                init_dict['mumc_path']=init_dict['mumc_path_config_dir']

                #make sure a few of the necessary config variables are there
                init_dict=assignVarTest(init_dict,cmdopt_dict,cfg)
                print('00$')
            elif (doesFileExist(init_dict['mumc_path_config_dir'] / init_dict['config_file_name_yml'])):
                print('00%')
                #try importing the config/mumc_config.yaml file
                #if config/mumc_config.yaml file does not exist try importing the legacy mumc_config.py file
                #with open(init_dict['mumc_path'] / init_dict['config_file_name_yaml'], 'r') as mumc_config_yaml:
                with open(init_dict['mumc_path_config_dir'] / init_dict['config_file_name_yml'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)
                print('00^')

                init_dict['mumc_path']=init_dict['mumc_path_config_dir']
                init_dict['config_file_name_yaml']=init_dict['config_file_name_yml']
                print('00&')


                #make sure a few of the necessary config variables are there
                init_dict=assignVarTest(init_dict,cmdopt_dict,cfg)
                print('00*')
            elif (doesFileExist(init_dict['mumc_path'] / init_dict['config_file_name_py'])):
                print('00(')
                #try importing the mumc_config.py file
                #if mumc_config.py file does not exist go to except and create one
                import mumc_config as cfg

                #run a config check on the legacy mumc_config.py before converting to mumc_config.yaml
                legacy_dict=cfgCheckLegacy(cfg,init_dict)
                print('00)')

                #convert legacy mumc_config.py to mumc_config.yaml; output is mumc_config.yaml
                convert_legacyConfigToYAML(legacy_dict,init_dict['mumc_path'],init_dict['config_file_name_no_ext'])
                print('00-')

                with open(init_dict['mumc_path'] / init_dict['config_file_name_yaml'], 'r') as mumc_config_yaml:
                    cfg = yaml.safe_load(mumc_config_yaml)

                print('00_')
                #make sure a few of the necessary config variables are there
                init_dict=assignVarTest(init_dict,cmdopt_dict,cfg)
                print('00=')
            else:
                print('00+')
                cannotFindConfig(init_dict,cmdopt_dict)
                print('00[')

    except (AttributeError, ModuleNotFoundError, KeyError):
        print('00]')
        cannotFindConfig(init_dict,cmdopt_dict)
        print('00{')

    return cfg,init_dict