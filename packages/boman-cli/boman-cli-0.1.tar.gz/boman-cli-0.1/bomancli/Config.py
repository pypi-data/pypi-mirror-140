import docker
import os 

class Config:

    #boman_url
    try:
        docker_client = docker.from_env()
    except Exception as e:
        print('Docker not found in your machine, Pls install')
        #print(str(e))
        exit(-1)

    boman_url = "http://devapi.boman.ai"  ## boman server ip

    sast_present = None
    sast_lang = None
    sast_target = None
    

    dast_present = None
    dast_target = None
    dast_type = None

    dast_cred_present = None
    dast_username = None
    dast_password = None
    
    sca_present = None
    sca_lang = None


    app_token = None
    customer_token = None


    sast_build_dir = None
    sca_build_dir = None

    secret_scan_present = None


    dast_response = None
    sast_response = None
    sca_response = None
    secret_scan_response = None

    scan_token = None

    log_level = "INFO"