from bomancli.base_logger import logging
from bomancli.Config import Config
import yaml
import json
import requests
import os
from bomancli import utils as Utils
#### read the input from the yaml file -- MM ------------------------------------------------------------

def yamlValidation():

    logging.info('Finding boman.yaml file')

    try: 
        with open('boman.yaml', 'r') as file:
            Config.config_data = yaml.safe_load(file)    
        logging.info('Config yaml file found')    
    except:
        
        logging.error('No config yaml file found')
        exit(-1)

    logging.info('Prasing & Validating the config yaml file')
   


    try:
        if Config.config_data['Auth'] != '':
            Config.app_token = Config.config_data['Auth']['project_token']
            Config.customer_token =Config.config_data['Auth']['customer_token']


    except KeyError:

        logging.error('App & customer token is mandatory to run the scan. Refer the documentation')    


    try: 

        if  Config.config_data['SAST'] != '':
            Config.sast_lang = Config.config_data['SAST']['language'].split(",") ## comma sperated if mulitple
            
            Config.sast_present = True

            #logging.info('sast is configured with %s',type(Config.sast_lang))

            try:
                Config.sast_build_dir  = Config.config_data['SAST']['work_dir']
            except KeyError: 
                Config.sast_build_dir = os.getcwd()+'/'

        if 'java' in Config.sast_lang:

            try:
                Config.sast_target =  Config.config_data['SAST']['target']
            except KeyError: 
                logging.error('Java requires a target file to be mentioned in the boman.yaml file. refer the documentation')
                Config.sast_present = False   
        #exit(-1)    
    except KeyError:    
        Config.sast_present = False
        logging.warning('SAST was not properly defined in the config')
        logging.info('Ignoring SAST, Please provide all mandatory inputs incase you like to run SAST scan.')
        

    
    ## DAST

    try: 
        Config.dast_target = Config.config_data['DAST']['URL']
        Config.dast_type = Config.config_data['DAST']['type']

        Config.dast_present = True

        try:        
            if Config.config_data['DAST']['cred'] == 'true':
                Config.dast_cred = True
                Config.dast_uname = Config.config_data['DAST']['username']
                Config.dast_password = Config.config_data['DAST']['password']
        except KeyError:
            Config.dast_cred_present = False 


        if Utils.testDastUrl(Config.dast_target):
            logging.info('Proceeding further with DAST target')
        else:    
            logging.info('DAST target is not reachable, ignoring DAST scan')
            Config.dast_present = False
                
    except KeyError:    
        Config.dast_present = False
        logging.warning('DAST was not properly defined in the config.')
        logging.warning('Ignoring DAST, Please provide all mandatory inputs incase you like to run DAST scan.')
        



    ## SCA

    try: 
        if  Config.config_data['SCA'] != '':
            Config.sca_lang = Config.config_data['SCA']['language'].split(",") ## comma sperated if mulitple
            
            Config.sca_present =  True

            try:
                Config.sca_build_dir = Config.config_data['SCA']['work_dir']
            except KeyError: 
                Config.sca_build_dir = os.getcwd()
    except KeyError:    
        Config.sca_present =  False
        logging.warning('SCA was not properly defined in the config')
        logging.info('Ignoring SCA, Please provide all mandatory inputs incase you like to run SCA scan.')
        

    try:
        if Config.config_data['Secret_Scan'] == False:
            Config.secret_scan_present = False
        else:    
            try:
                Config.secret_scan_present =  True if Utils.isGitDirectory(Config.sast_build_dir) else False          
            except KeyError:
                Config.secret_scan_present = False
    except KeyError:
        Config.secret_scan_present = False    

        

    

## need to use lingudetect here, but the results are not trustable and misleading ------ MM -------------------
def findLang():
    print('[INFO]: Detecting Language')
