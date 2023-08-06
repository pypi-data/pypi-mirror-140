## importing required libraries

#import docker
import yaml
import json
import time
import os
import requests
import argparse
import subprocess


##importing required files

#import linguDetect/lingu_detect as ling
from bomancli.base_logger import logging
from bomancli.Config import Config

from bomancli import validation as Validation
from bomancli import utils as Utils
from bomancli import auth as Auth





parser = argparse.ArgumentParser(
	prog='boman-cli',
	description='''
	#This is a CLI tool to communicate with Boman.ai server
	''',
	epilog='copyright (c) 2022 SUMERU'
	)


docker = Config.docker_client

### function to init the scan and will check the docker is in place
def init():
    
    print('#################################### -  BOMAN Scanner Initiated - ####################################')
    logging.info('Checking for Docker in the Env')
    try:
        #docker = docker.from_env()
        if docker.ping():
           logging.info('Docker is running in the Environment')
        else:
            logging.error('Unable to connect to docker, Please install docker in your environment')    
    except Exception as e:
        logging.error('Docker not found in your machine, Pls install')
        #print(str(e))
        exit(-1)




### Run the scanners -- MM
### function to run the image -- MM ---------------------------------------------------------------------------

def runImage(data=None,type=None):

    if data is None:
        logging.error('Unable to access the response data while running the scan')

    if type is None:
        logging.error('Unable to access the response data while running the scan')


      

    docker_image = data['image']
    #lang= None 
    tool_name =data['tool']
    command_line= data['command']
    output_file= data['output_file']
    will_generate_output = data['will_generate_output']
    tool_id= data['tool_id']
    scan_details_id= data['scan_details_id']
    conversion_required = data['conversion_required']

    #print(docker_image,tool_name,command_line,output_file,will_generate_output,tool_id,scan_details_id)

    if docker_image is None:
        print('Problem with running the scanner, image not specified.')
        exit('-1')
        
    uid = os.getuid()
    gid = os.getgid()


    userid= f"{uid}:{gid}"

    if type == 'SAST':
        target_file = Config.sast_target
        Utils.checkImageAlreadyExsist(docker_image)

        logging.info('Running %s in the repository',tool_name)
        
        if data['dynamic_comment'] == 1:
            command_line = "% s" % command_line.format(target_file = target_file)
            #print(Config.sast_build_dir,command_line,docker_image)
            #command_line =  repr(command_line)
        
       
        detach = True if data['detach'] == 1 else False
        
        try:
            container_output = docker.containers.run(docker_image, command_line, volumes={Config.sast_build_dir: {
                            'bind': data['bind']}}, user=userid,detach=detach)
            logging.info('[SUCCESS]: %s Scan Completed',tool_name)
        except:
            #print(container_output)
            logging.error('[WARNING]: Some Error recorded while scanning %s',tool_name)   ## need to rewrite the logic here --MM
   

        try:
            
            if will_generate_output == 1:
                #logging.info('WILL GENERATE OUTPUT') 
                uploadReport(output_file,tool_name,tool_id,scan_details_id)
            else:
                
                ## incase file type is other than json
                if conversion_required == 1:
                    if tool_name == 'Findsecbugs':
                        logging.info('Converting xml to json')
                        uploadReport(output_file,tool_name,tool_id,scan_details_id)

                ## incase of json 
                with open(Config.sast_build_dir+output_file, 'w', encoding='utf-8') as f:
                   json.dump(json.loads(container_output), f, ensure_ascii=False, indent=4)
                uploadReport(output_file,tool_name,tool_id,scan_details_id)
        except:
            logging.WARNING('Error while uploading the report of %s',tool_name)    
            


    if type == 'DAST':

        Utils.checkImageAlreadyExsist(docker_image)
        logging.info('Running %s on %s ',tool_name, Config.dast_target)
        #command_line = '-h '+Config.dast_target+' -maxtime 10 -o tmp/'+output_file
        #print(command_line_nikto)
        detach = True if data['detach'] == 1 else False

        if Config.sast_build_dir == None:
            Config.sast_build_dir = os.getcwd()+'/'

        if data['dynamic_comment'] == 1:
            target_url = Config.dast_target
            command_line = "% s" % command_line.format(target_url = target_url)
            #print(command_line)
        try:
            container= docker.containers.run(docker_image, command_line, volumes={Config.sast_build_dir: {
 				'bind': data['bind']}},user=1000,detach=detach)
            
            #print(output_file,toolname,tool_id,scan_details_id)
            logging.info('[SUCCESS]: %s Scan Completed',tool_name)
            
        except:
            #print(container)
            logging.error('Error recorded while Scanning %s',tool_name)

        try:
            if will_generate_output == 1:
                logging.info('Uploading %s to the server',output_file)
                uploadReport(output_file,tool_name,tool_id,scan_details_id)
            else:
                logging.error('Cant upload files to the server',tool_name)

        except:    
            logging.error('Error recorded while uploading the report %s',tool_name)    

    if type == 'SCA':
        logging.info(' Running %s',tool_name)
        try:
            container_output = docker.containers.run(docker_image, command_line, volumes={Config.sca_build_dir: {
                    'bind': data['bind']}}, user=uid)
            logging.info('[SUCCESS]: %s Scan Completed',tool_name)
        except:

            logging.error('Some Error recorded while scanning %s',tool_name)           ## need to change logic here -- MM   



#### fucntion to upload the test report to the server with other data -- MM ------------------------------------
def uploadReport(filename,toolname,tool_id,scan_details_id): #,scan_token,tool_id,tool_type): #,scan_token
    ##print(scan_token) # = 'f6fdf1d8-096c-4bbe-bc59-5eeae30560f1'
    
    logging.info('Uploading %s report with filename: %s', toolname,filename)
    if True:
        #build_dir = '/home/boxuser/box/trainingdata/repos/youtube-dl/'
        #print(Config.sast_build_dir+filename)
        #files = open(build_dir+filename)
        
        try:
            logging.info('fetching the %s file from the directory %s',filename,Config.sast_build_dir)
            with open(Config.sast_build_dir+filename) as f:
                data = json.load(f)
        except EnvironmentError as e:
            logging.error('Error while fetching the output file from the directory')
            logging.debug(e)
            return 0
 
        tool_output = json.dumps(data, ensure_ascii=False, indent=4)
        values = {'tool_name': toolname, 'time': time.time(),'scan_token':Config.scan_token, 'app_token':Config.app_token,'customer_token':Config.customer_token,'tool_id':tool_id,'scan_details_id':scan_details_id,"tool_results":tool_output}
        url = Config.boman_url+"/api/scan/upload/results"
        r = requests.post(url, data=values)
        #print(r.status_code)
        if r.status_code == 200:
            logging.info('[COMPLETED]: %s Report uploaded Successfully! Report Name: %s',toolname,filename)
            return 1
        elif r.status_code == 401 :
            logging.error('Unauthorized Access while uploading the results. Please check the app/customer tokens')
            exit(-1)
        else:
            logging.error('Problem While uploading the results.') 
            return 0   
    else:
       logging.error(toolname,' Report cant be uploaded filename: %s',filename)
       return 0 ## need to write a logic here

    return 1    




## function for seceert scan using trufflehog
def initSecertScan(path,data):
    
    build_dir = path
    command_line_truffle = data[0]['command']
    image_name= data[0]['image']
    tool_name = data[0]['tool']
    bind_dir = data[0]['bind']
    Utils.checkImageAlreadyExsist(image_name)


    try:
        logging.info('Running Secert Scanning on the repository')
        container = Config.docker_client.containers.run(image_name, command_line_truffle, detach=True,volumes={build_dir: {
                    'bind': bind_dir}})
        op = []
        for iteration_main,line in enumerate(container.logs(stream=True)):
            try:
                op.append(json.loads(line.strip()))
                #print(op[iteration_main]['stringsFound'])
                for iteration,key in enumerate(op[iteration_main]['stringsFound']):
                   #print(key)
                    op[iteration_main]['stringsFound'][iteration] = Utils.masker(key)
                            
            except:
                logging.error('Some Findings from the trufflehog is unrecognisble.Skiping them.')
                break

       
        logging.info('[SUCCESS]: Secert Scanning Completed ')            
    except ContainerError as exc:
        logging.error('Error Occured while running Trufflehog on the repository') 


    try:
        file_name = data[0]['output_file']
        path = Config.sast_build_dir+file_name
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(op, f, ensure_ascii=False, indent=4)   
        
        if uploadReport(file_name,tool_name,'5','1'):
            logging.info('[COMPLETED]: Secert Scanning report Uploaded')
        else:
            logging.error('Error Occured while uploading report to boman.ai server. Please contact admin.')           
    except Exception as error: 
         logging.error(' Error Occured while generating report for secert scan') 

    return True    



#main fucntion where all the actions have been initiated 
def main():
  
    
    
    init()
    Validation.yamlValidation()
    Utils.testServer()
    content = Auth.authorize()
    global scan_token

    if Config.secret_scan_present == True:

        if Utils.isGitDirectory(Config.sast_build_dir):
            logging.info('Git repository is found in the directroy')
            logging.info('Initizating Secert Scanning')
            for data in Config.secret_scan_response:
                initSecertScan(Config.sast_build_dir,data=Config.secret_scan_response)
        else:
            logging.info('Git repository not found in the directroy %s',Config.sast_build_dir)
            logging.info('Sikping Secert Scanning')    

    scan_token = Config.scan_token


    if Config.sast_present is True:


        logging.info('Preparing SAST Scan')
        logging.info('Working directory is %s',Config.sast_build_dir)
        if Config.sast_lang is None:
            #findLang()
            logging.error('Language Not Defined. Exiting')
            exit(-1)



        sast_len = len(Config.sast_lang)

        if sast_len > 1: ## if the mentioned languages are more than one
            logging.info('Detected Languges %s',Config.sast_lang)
            for lang in Config.sast_lang:
                loc = Utils.getLoc(Config.sast_build_dir, lang)
                #print(loc)
                logging.info('Running scanner with language: %s',lang)


        else:
            logging.info("Detected Language is : %s",Config.sast_lang)          
            loc =  Utils.getLoc(Config.sast_build_dir, Config.sast_lang[0])
            logging.info('Loc found in the %s : %s',Config.sast_build_dir,loc)

        for data in Config.sast_response:
            runImage(data=data,type='SAST')

    else:
        logging.info('Ignoring SAST Scan')


    if Config.dast_present is True:
        logging.info('Preparing DAST scan')
        


        if Utils.testDastUrl(Config.dast_target):
           

           for data in Config.dast_response:
                runImage(data=data,type='DAST')
           # runImage(imagename= content['data']['dast']['tool_2']['image'], toolname= content['data']['dast']['tool_2']['tool'],type='DAST',output_file=content['data']['dast']['tool_2']['output_file'],tool_id=content['data']['dast']['tool_2']['tool_id'], scan_details_id=content['data']['dast']['scan_details_id'])


        else:
            logging.info('Ignoring DAST scan, since the target is unreachable')     

    else:
        logging.info('Ignoring DAST scan')


    if Config.sca_present is True:
        logging.info('Preparing SCA scan')
        for data in Config.sca_response:
            runImage(data=data,type='DAST')
        #print('running sca')
        ##runImage(imagename= content['data']['sca']['image'], toolname= content['data']['sca']['tool'],type='SCA',output_file=content['data']['sca']['output_file'],tool_id=content['data']['sca']['tool_id'], scan_details_id=content['data']['sca']['scan_details_id'])
    else:
        logging.info('Ignoring SCA scan')



    logging.info('################################ BOMAN Scanning Done ################################')
    logging.info('Please access your boman dashboard for the refined results.')
    exit(1)



def default():  

    parser.add_argument('-a','--action',default='init',help="Action arugment, you need to pass the value for action (eg: test-saas, test-docker, run)")
    parser.add_argument('-l','--log',default='INFO',help="Logging the output, default is INFO level (eg values : DEBUG, INFO)")
    #parser.add_argument('-check-docker',help='Check you docker is present in your system is compatable to run the boman.ai')
    args = parser.parse_args()

    if args.action == 'init':
        print('Welcome to Boman CLI, pass bomancli --help to view the commands args ')
        exit(1)
    elif args.action =='run':
        logging.info("New Scan has been Initiated")
        main()
        exit(1)
    elif args.action =='test-saas':
        Utils.testServer()   
        exit(1)
    elif args.action =='test-docker':
        Utils.testDockerAvailable() 
        exit(1)   
    elif args.action =='test-yaml':
       Validation.yamlValidation()  
       exit(1) 
    else:
        print('Welcome to Boman CLI, pass bomancli --help to view the commands args ')
    ## starting the cli
    


default()
