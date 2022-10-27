from datetime import datetime, timedelta
from flask import Flask,jsonify,Response,request
import datetime,pytz
import os 
import shutil
from os import path
import hashlib
import gzip
import tarfile
import zipfile
from datetime import datetime 
import time
import subprocess
import psycopg2
from psycopg2.extras import Json, DictCursor
import json
utc=pytz.UTC
from flask_cors import CORS
from flask_api import status
from flask_debug import Debug

time_to_expired_token = 7200 #30
app = Flask(__name__)
# CORS helps to hit mutliple 
cors = CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)
Debug(app)

con = psycopg2.connect("user='postgres' host='localhost' password='postgres'  port=5432")
cur = con.cursor(cursor_factory=DictCursor)

#cur.execute("""ALTER TABLE device_token_generater_1  ALTER COLUMN device_id  TYPE VARCHAR(50);""")
#cur.execute("""CREATE TABLE IF NOT EXISTS device_token_generater_2 (device_id VARCHAR(40) NOT NULL,
# device_token VARCHAR(50) NOT NULL,token_status VARCHAR (50) NOT NULL ,token_generate_time TIMESTAMP NOT NULL );""")
#con.commit()
#CREATE TABLE accounts ( 	user_id serial PRIMARY KEY,	username VARCHAR ( 50 ) UNIQUE NOT NULL,	password VARCHAR ( 50 ) NOT NULL,
#	email VARCHAR ( 255 ) UNIQUE NOT NULL,token_generate_time TIMESTAMP NOT NULL,        last_login TIMESTAMP );


@app.errorhandler(404)                                                         
def not_found(error):
    """ error handler """
    #LOG.error(error)
    return make_response(jsonify({'result':'false','output':'Ohh Snap! Double Check Your URL'}), 404)


@app.errorhandler(503)
def handle_timeout(error):
    if utils.misc.request_is_xhr(request):
        return jsonify({'api_timeout': True}), 503
    return redirect(url_for('errors.api_timeout', path=request.path))


@app.errorhandler(401)
def custom_401(error):
    return make_response(jsonify({'result':'false','output':'Unauthorized URL'}), 401)


# BAD REQUEST HANDLER
@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def handle_bad_request(e):
    return make_response(jsonify({'result':'false','output':'Bad Request - Your request is missing data. Please verify and resubmit.'}), 400)

@app.errorhandler(405)
def error405(error):
	return make_response(jsonify({"success":'false','message':"Incorrect Method Used, Change The Method ."}), 400)





def get_now_time():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S.%f")
    return (dt_string)



#cur.execute("""CREATE TABLE IF NOT EXISTS device_token_generater (device_id INT NOT NULL,device_token VARCHAR ( 50 )  NOT NULL,token_status VARCHAR ( 50 ) NOT NULL ,token_generate_time TIMESTAMP NOT NULL );""")
#con.commit()

#cur.execute(''' insert into device_token_generater (device_id,device_token,token_status,token_generate_time) values (1,'abcdekjadfjkadfjkdk','off',get_now_time());''')
#con.commit()






def list_all_files(folder):
    files_list=[os.path.join(path, name) for path, subdirs, files in os.walk(folder) for name in files]
    return files_list


def file_created_time(filename):
    year,month,day,hour,minute,second=time.localtime(os.path.getmtime(filename))[:-3]
    created_time= "%02d/%02d/%d %02d:%02d:%02d"%(day,month,year,hour,minute,second)
    return (created_time)


def file_modified_time(filename):
    year,month,day,hour,minute,second=time.localtime(os.path.getmtime(filename))[:-3]
    modified_time= "%02d/%02d/%d %02d:%02d:%02d"%(day,month,year,hour,minute,second)
    return (modified_time)

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles



# function checks for is file is zipped file 
def check_all_zip(filename):
    return filename.endswith((".tar.xz", ".zip", ".gz",".tar.gz",".tgz",".tar",".tar.xz"))


# function checks for is file is .tar.xz file 
def _is_tarxz(filename):
    return filename.endswith(".tar.xz")

# function checks for is file is .tar file 
def _is_tar(filename):
    return filename.endswith(".tar")

# function checks for is file is .tar.gz file 
def _is_targz(filename):
    return filename.endswith(".tar.gz")

# function checks for is file is .tgz file 
def _is_tgz(filename):
    return filename.endswith(".tgz")

# function checks for is file is .gz file 
def _is_gzip(filename):
    return filename.endswith(".gz") and not filename.endswith(".tar.gz")

# function checks for is file is .zip file 
def _is_zip(filename):
    return filename.endswith(".zip")


#  function checks for is given file is exists or not  
def is_file_(filename):
    return os.path.exists(filename)

# list the files from the folder
def is_file_or_directory(filename):
    if check_all_zip(filename):
        folderpath,filename =os.path.split(filename)
        filename,extenstion = os.path.splitext(filename)
        all_files = getListOfFiles(os.path.join(folderpath,filename))
    else:
        exists= os.path.exists(filename)
        all_files=filename
    return all_files

#  function checks for is given directory or folder  is exists or not
def is__directory_(filename):
    exists=False
    if check_all_zip(filename):
        folderpath,filename =os.path.split(filename)
        filename,extenstion = os.path.splitext(filename)
        exists= os.path.exists(os.path.join(folderpath,filename))
    return exists

# function checks for given file or folder exists or not 
def is_file_or_directory_exists(filename):
    exists=False   
    if check_all_zip(filename):
        folderpath,filename =os.path.split(filename)
        filename,extenstion = os.path.splitext(filename)
        exists= os.path.exists(os.path.join(folderpath,filename))
    elif os.path.isfile(filename):
        exists= os.path.exists(filename)
    return exists

# function extract the zip file and remove zip file from the destination path 
def extract_archive(from_path, to_path=None, remove_finished=True):
    if to_path is None:
        to_path = os.path.dirname(from_path)
    if _is_tar(from_path):
        with tarfile.open(from_path, 'r') as tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, path=to_path)
    elif _is_targz(from_path) or _is_tgz(from_path):
        with tarfile.open(from_path, 'r:gz') as tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, path=to_path)
    elif _is_tarxz(from_path):
        with tarfile.open(from_path, 'r:xz') as tar:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar, path=to_path)
    elif _is_gzip(from_path):
        to_path = os.path.join(to_path, os.path.splitext(os.path.basename(from_path))[0])
        with open(to_path, "wb") as out_f, gzip.GzipFile(from_path) as zip_f:
            out_f.write(zip_f.read())
    elif _is_zip(from_path):
        with zipfile.ZipFile(from_path, 'r') as z:
            z.extractall(to_path)
    else:
        raise ValueError("Extraction of {} not supported".format(from_path))

    if remove_finished:
        os.remove(from_path)



# device restart apis helps to restart or shutdown the device 
@app.route('/device_restart' ,methods=['POST'])
def device_restart_():
    ret = {"success": False,"message":"An unexpected error has occurred, please try again later."}
    try :
        jsonobject=request.json
        if jsonobject == None:
            jsonobject = {}
        request_key_array=['device_id','restart/shutdown','device_token','token_status']
        jsonobjectarray= list(set(jsonobject))
        # checking missed key from frontend 
        missing_key=set(request_key_array).difference(jsonobjectarray)        
        if not missing_key:
            # checking empty values from frontend 
            output=[k for k, v in jsonobject.items() if v =='']
            if output:
                ret['message']='You have missed these parameters '+str(output)+' to enter, please enter properly.'
            else:
                # assigning json parameters 
                device_id=jsonobject['device_id']
                command_type =jsonobject['restart/shutdown']
                device_token =jsonobject['device_token']
                token_status =jsonobject['token_status']
                device_token_str = "'"+device_token+"'" 
                # checking token_status                  
                if token_status == "True":
                    # fetching data from db for device token 
                    cur.execute("""SELECT * FROM device_token_generater_1 WHERE device_token = {0};""".format(device_token_str))
                    row =  cur.fetchall()
                    # checking whethere given token key is exist or not 
                    if not row:
                        ret['message']='Invalid token key.'
                    else:
                        token_generate_time_from_db = None
                        for i in row:
                            device_id_from_db=i[0]
                            device_token_from_db=i[1]
                            token_status_from_db=i[2]
                            token_generate_time_from_db=i[3]  
                        now  = datetime.now()#.astimezone(pytz.timezone('Asia/Calcutta'))
                        #print('now time = ',now)
                        #print('db time =',token_generate_time_from_db)
                        # checks token expiration time limit
                        #now.astimezone(pytz.timezone('Asia/Calcutta'))
                        difference = (now- token_generate_time_from_db )
                        #print(difference.days)
                        #print(difference.minutes)
                        #print(difference.seconds)
                        #7200
                        if difference.seconds < time_to_expired_token:                         
                        #now  = datetime.now().astimezone(pytz.timezone('Asia/Calcutta'))
                        # checks token expiration time limit
                        #if utc.localize(token_generate_time_from_db).astimezone(pytz.timezone('Asia/Calcutta')) < now:                         
                            if command_type=='restart':
                                #running restart command to restart the system 
                                os.system("shutdown -r now + 10 seconds")#("shutdown -r -h now + 10 seconds")
                                ret = {"success": True,"message":"System will getting restart in 10 seconds."}
                            elif command_type=='shutdown':
                                #running shutdown command to shutdown the system 
                                os.system("shutdown -h now + 10 seconds")#"sudo shutdown -s -t 10")
                                ret = {"success": True,"message":"System will getting shutdown in 10 seconds."}
                            else:                                
                                ret['message']='You have gived invalid command.'
                        else:
                            ret['message']='token key is expired.'
                else:
                    if command_type=='restart':
                        #running restart command to restart the system
                        os.system("shutdown -r now + 10 seconds")#("shutdown -r -h now + 10 seconds")
                        ret = {"success": True,"message":"System will getting restart in 10 seconds."}
                    elif command_type=='shutdown':
                        #running shutdown command to shutdown the system 
                        os.system("shutdown -h now + 10 seconds")#"sudo shutdown -s -t 10")
                        ret = {"success": True,"message":"System will getting shutdown in 10 seconds."}
                    else:                            
                        ret['message']='you have give invalid command please try to give valid command'
        else:
            ret={'message':'Please enter missed json keys '+ str(missing_key)+'.',"success": False}
    except Exception as e:
        ret['message']='Error --- ' +str(e)+'.'
    return  jsonify(ret)


@app.route('/edge/device/application/fileupdate/<file_type_upload>', methods=['POST'])
def file_udpate(file_type_upload):
    ret = {"success": False,"message":"An unexpected error has occurred, please try again later."}
    #if True:
    try:
        if file_type_upload =='other':            
            jsonobject=request.form
            if jsonobject == None:
                jsonobject = {}
            file_array=request.files
            request_key_array=['device_id','file_type','destination_path','device_token','token_status']
            request_key_array1=['file']
            jsonobjectarray= list(set(jsonobject))
            # checking missed key from frontend 
            missing_key=set(request_key_array).difference(jsonobjectarray)
            missing_key_in_files= set(request_key_array1).difference(file_array)  
            missing_key_final= missing_key | missing_key_in_files  
            if not missing_key and not missing_key_in_files:
                # checking empty values from frontend
                output=[k for k, v in jsonobject.items() if v =='']
                uploading_file = request.files['file']
                if uploading_file.filename == '' :
                    output.append('file')
                if output :
                    ret['message']='you have missed these parameters '+str(output)+' to enter. please enter properly.'
                else:
                    device_id=jsonobject['device_id']
                    file_type =jsonobject['file_type']
                    file_details=[]
                    device_token =jsonobject['device_token']
                    token_status =jsonobject['token_status']
                    device_token_str = "'"+device_token+"'"
                    if token_status == "True" :
                        # fetching data from db for device token 
                        cur.execute("""SELECT * FROM device_token_generater_1 WHERE device_token = {0};""". format(device_token_str))
                        row =  cur.fetchall()
                        # checking whethere given token key is exist or not 
                        if not row:
                            ret['message']='Invalid token key'
                        else:
                            token_generate_time_from_db = None
                            for i in row:
                                device_id_from_db=i[0]
                                device_token_from_db=i[1]
                                token_status_from_db=i[2]
                                token_generate_time_from_db=i[3]
                            now  = datetime.now()#.astimezone(pytz.timezone('Asia/Calcutta'))
                            #print('now time = ',now)
                            #print('db time =',token_generate_time_from_db)
                            # checks token expiration time limit
                            #now.astimezone(pytz.timezone('Asia/Calcutta'))
                            difference = (now- token_generate_time_from_db )
                            #print(difference.days)
                            #print(difference.minutes)
                            #print(difference.seconds)
                            #7200
                            if difference.seconds < time_to_expired_token:
                            #now  = datetime.now().astimezone(pytz.timezone('Asia/Calcutta'))
                            # checks token expiration time limit

                            #if utc.localize(token_generate_time_from_db).astimezone(pytz.timezone('Asia/Calcutta')) < now: 

                                if file_type_upload == 'other':
                                    uploading_path=jsonobject['destination_path']#"/home/docketrun/flask_application/application/dummy_upload"
                                    file_name_to_print=os.path.join(uploading_path,uploading_file.filename)
                                    # checking given path is folder or not 
                                    if os.path.exists(os.path.join(uploading_path,uploading_file.filename)):
                                        if check_all_zip(uploading_file.filename):
                                            # listing all files from the given folder                                
                                            all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                            for i in all_files:
                                                #getting size of each file  
                                                size_of_file = os.stat(i).st_size
                                                #converting file size Bytes into Kilo Bytes
                                                final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                #file created time function gives created time of each file from the given directory 
                                                #file_created_time(i)
                                                #file modified time function gives last modified time of each file from the given directory
                                                #file_modified_time(i)
                                                file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                            #saving files from the folder the uploading folder 
                                            uploading_file.save(os.path.join(uploading_path,uploading_file.filename))
                                            #extracting zipped folder and removing it  
                                            extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                            ret = {"success": True,"message":"other folder is successfully updated.",'existed_file_details':file_details}
                                        ## checking give path is file or not
                                        elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                            # listing file of the given file      
                                            all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                            #getting size of file                                                  
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            #saving file to uploading folder 
                                            uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                            ret = {"success": True,"message":"Other file is successfully updated.",'existed_file_details':file_details}
                                        else:
                                            ret['message']='Give file or folder '
                                    else:
                                        ret['message']='Given file or folder is does not exist please give valid one .'
                                else:
                                    ret['message']='file type is invalid please give proper one .'
                            else:
                                ret['message']='Device token key has expired.'
                    else:
                        if file_type_upload == 'other':
                            uploading_path=jsonobject['destination_path']#"/home/docketrun/flask_application/application/dummy_upload"
                            file_name_to_print=os.path.join(uploading_path,uploading_file.filename)
                            if check_all_zip(uploading_file.filename):
                                # listing all files from the given folder   
                                all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                for i in all_files:
                                    #getting size of each file 
                                    size_of_file = os.stat(i).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)                                    
                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                #saving files from the folder the uploading folder 
                                uploading_file.save(os.path.join(uploading_path,uploading_file.filename))
                                #extracting zipped folder and removing it    
                                extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                ret = {"success": True,"message":"Other folder is successfully updated.",'existed_file_details':file_details}
                            elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                # listing all files from the given folder   
                                all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                #getting size of each file 
                                size_of_file = os.stat(all_files).st_size
                                #converting file size Bytes into Kilo Bytes
                                final_size = str(round(size_of_file / 1024, 3))+'KB'
                                #file created time function gives created time of each file from the given directory 
                                #file_created_time(i)
                                #file modified time function gives last modified time of each file from the given directory
                                #file_modified_time(i)
                                file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                ret = {"success": True,"message":"Other file is successfully updated.",'existed_file_details':file_details}
                            else:
                                ret['message']='Given file or folder is not found.'
                        else:
                            ret['message']='Given file type is not found.'
            else:
                ret={'message':'Please enter missed json keys '+ str(missing_key_final)+'.',"success": False}


        elif file_type_upload =='new':
            ret = {"success": False,"message":"An unexpected error has occurred, please try again later."}
            jsonobject=request.form
            if jsonobject == None:
                jsonobject = {}
            file_array=request.files
        
            request_key_array=['device_id','file_type','destination_path']
            request_key_array1=['file']
            jsonobjectarray= list(set(jsonobject))
            # checking missed key from frontend 
            missing_key=set(request_key_array).difference(jsonobjectarray)
            missing_key_in_files= set(request_key_array1).difference(file_array)  
            missing_key_final= missing_key | missing_key_in_files  
            if not missing_key and not missing_key_in_files:
                # checking empty values from frontend
                output=[k for k, v in jsonobject.items() if v =='']
                uploading_file = request.files['file']
                if uploading_file.filename == '' :
                    output.append('file')
                if output :
                    ret['message']='you have missed these parameters '+str(output)+' to enter. please enter properly.'
                else:
                    device_id=jsonobject['device_id']
                    file_type =jsonobject['file_type']
                    device_token =jsonobject['device_token']
                    token_status =jsonobject['token_status']
                    device_token_str = "'"+device_token+"'"
                    if token_status == "True" :
                        # fetching data from db for device token 
                        cur.execute("""SELECT * FROM device_token_generater_1 WHERE device_token = {0};""". format(device_token_str))
                        row =  cur.fetchall()
                        # checking whethere given token key is exist or not 
                        if not row:
                            ret['message']='Invalid token key.'
                        else:
                            token_generate_time_from_db = None
                            for i in row:
                                device_id_from_db=i[0]
                                device_token_from_db=i[1]
                                token_status_from_db=i[2]
                                token_generate_time_from_db=i[3]
                            now  = datetime.now()#.astimezone(pytz.timezone('Asia/Calcutta'))
                            #print('now time = ',now)
                            #print('db time =',token_generate_time_from_db)
                            # checks token expiration time limit
                            #now.astimezone(pytz.timezone('Asia/Calcutta'))
                            difference = (now- token_generate_time_from_db )
                            #print(difference.days)
                            #print(difference.minutes)
                            #print(difference.seconds)
                            #7200
                            if difference.seconds < time_to_expired_token:
                            #now  = datetime.now().astimezone(pytz.timezone('Asia/Calcutta'))
                            # checks token expiration time limit
                            #if utc.localize(token_generate_time_from_db).astimezone(pytz.timezone('Asia/Calcutta')) < now: 
                                file_details=[]                            
                                if file_type == 'new':
                                    uploading_path=jsonobject['destination_path']#"/home/docketrun/flask_application/application/dummy_upload"
                                    if is_file_or_directory_exists(os.path.join(uploading_path,uploading_file.filename)) == True :
                                        # checking given path is folder or not 
                                        if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                            if check_all_zip(uploading_file.filename):
                                                # listing all files from the given folder                                 
                                                all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                                for i in all_files:
                                                    #getting size of each file 
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                                extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                                ret = {"success": True,"message":"other replace files are successfully updated.",'existed_file_details':file_details}
                                        elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                            # listing all files from the given folder   
                                            all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))  
                                            #getting size of each file                                               
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                            ret = {"success": True,"message":"Common files are successfully updated.",'existed_file_details':file_details}                                        
                                        else:
                                            ret['message']='Given file or folder is not found.' 
                                    else:
                                        if check_all_zip(os.path.join(uploading_path,uploading_file.filename)):
                                            filename,extenstion_ = os.path.splitext(os.path.join(uploading_path,uploading_file.filename))
                                            if not os.path.exists(os.path.join(folderpath,filename)):
                                                os.makedirs(os.path.join(folderpath,filename)) 
                                            # checking given path is folder or not                                                                                                            
                                            if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                                # listing all files from the given folder   
                                                all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                                for i in all_files:
                                                    #getting size of each file 
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)                                                    
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                                extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                                ret = {"success": True,"message":"New files are created successfully.",'existed_file_details':file_details}
                                            else:
                                                ret['message']='Folder is not able to create.'
                                        if not os.path.exists(os.path.join(uploading_path,uploading_file.filename)):
                                            with open(os.path.join(uploading_path,uploading_file.filename), 'w'): 
                                                uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                                ret = {"success": True,"message":"New files are created successfully."}
                                        else:
                                            ret = {"success": False,"message":"New file not able to create."}
                                else:
                                    ret['message']='Given file or folder is not found.'
                            else:
                                ret['message']='device token has expired.'
                    else:
                        file_details=[]
                        if file_type == 'new':
                            uploading_path=jsonobject['destination_path']#"/home/docketrun/flask_application/application/dummy_upload"
                            if is_file_or_directory_exists(os.path.join(uploading_path,uploading_file.filename)) == True :
                                # checking given path is folder or not 
                                if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                    if check_all_zip(uploading_file.filename):   
                                        # listing all files from the given folder                               
                                        all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                        for i in all_files:
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                        extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                        ret = {"success": True,"message":"New file is created successfully.",'existed_file_details':file_details}
                                elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                    # listing all files from the given folder   
                                    all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                    #getting size of each file 
                                    size_of_file = os.stat(all_files).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                    uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                    ret = {"success": True,"message":"New file is created successfully.",'existed_file_details':file_details}
                                else:
                                    ret['message']='Given file or folder is not found.' 
                            else:
                                if check_all_zip(os.path.join(uploading_path,uploading_file.filename)):
                                    folderpath,filename =os.path.split(os.path.join(uploading_path,uploading_file.filename))
                                    filename,extenstion_ = os.path.splitext(os.path.join(uploading_path,uploading_file.filename))
                                    if not os.path.exists(os.path.join(folderpath,filename)):
                                            os.makedirs(os.path.join(folderpath,filename))
                                    # checking given path is folder or not 
                                    if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                        # listing all files from the given folder   
                                        all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                        for i in all_files:
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                        extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                        ret = {"success": True,"message":"Newfolder is created successfully.",'existed_file_details':file_details}
                                    else:
                                        ret['message']='Folder is not able to create.'
                                if not os.path.exists(os.path.join(uploading_path,uploading_file.filename)):
                                    with open(os.path.join(uploading_path,uploading_file.filename), 'w'):
                                        uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                        ret = {"success": True,"message":"New file is create successfully."}
                                else:
                                    ret = {"success": False,"message":"New file is not able to create."}
                        else:
                            ret['message']='Given file type is not found.'
            else:
                    ret={'message':'Please enter missed json keys '+ str(missing_key_final)+'.',"success": False}



        else:
            ret = {"success": False,"message":"An unexpected error has occurred, please try again later."}
            jsonobject=request.form
            if jsonobject == None:
                jsonobject = {}
            file_array=request.files
            request_key_array=['device_id','file_type']
            request_key_array1=['file']
            jsonobjectarray= list(set(jsonobject))
            # checking missed key from frontend 
            missing_key=set(request_key_array).difference(jsonobjectarray)
            missing_key_in_files= set(request_key_array1).difference(file_array)    
            missing_key_final= missing_key | missing_key_in_files 
            if not missing_key and not missing_key_in_files:
                # checking empty values from frontend
                output=[k for k, v in jsonobject.items() if v =='']
                uploading_file = request.files['file']
                if uploading_file.filename == '' :
                    output.append('file')
                if output :
                    ret['message']='you have missed these parameters '+str(output)+' to enter. please enter properly.'
                else:
                    device_id=jsonobject['device_id']
                    file_type =jsonobject['file_type']
                    device_token =jsonobject['device_token']
                    token_status =jsonobject['token_status']
                    device_token_str = "'"+device_token+"'"
                    if token_status == "True" :
                        # fetching data from db for device token 
                        cur.execute("""SELECT * FROM device_token_generater_1 WHERE device_token = {0};""". format(device_token_str))
                        row =  cur.fetchall()
                        ## checking whethere given token key is exist or not 
                        if not row:
                            ret['message']='Invalid token key.'
                        else:
                            token_generate_time_from_db = None
                            for i in row:
                                device_id_from_db=i[0]
                                device_token_from_db=i[1]
                                token_status_from_db=i[2]
                                token_generate_time_from_db=i[3]
                            now  = datetime.now()#.astimezone(pytz.timezone('Asia/Calcutta'))
                            #print('now time = ',now)
                            #print('db time =',token_generate_time_from_db)
                            # checks token expiration time limit
                            #now.astimezone(pytz.timezone('Asia/Calcutta'))
                            difference = (now- token_generate_time_from_db )
                            #print(difference.days)
                            #print(difference.minutes)
                            #print(difference.seconds)
                            #7200
                            if difference.seconds < time_to_expired_token:
                            #now  = datetime.now().astimezone(pytz.timezone('Asia/Calcutta'))
                            # checks token expiration time limit
                            #if utc.localize(token_generate_time_from_db).astimezone(pytz.timezone('Asia/Calcutta')) < now: 
                                file_details=[]
                                list_of_file_type= ['common','classification_model','detection_model','analysis_config_code_file']
                                if file_type in list_of_file_type :
                                    if file_type == 'common':
                                        uploading_path="/home/docketrun/flask_application/application/dummy_upload"#"/home/docketrun/flask_application/application/dummy_upload"
                                        # checking given path is folder or not 
                                        if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                            if check_all_zip(uploading_file.filename):   
                                                # listing all files from the given folder                               
                                                all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                                for i in all_files: 
                                                    #getting size of each file                                    
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                                extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                                ret = {"success": True,"message":"Common files are successfully updated.",'existed_file_details':file_details}
                                        elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                            # listing all files from the given folder   
                                            all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))                                                
                                            #getting size of each file 
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                            ret = {"success": True,"message":"Common files are successfully updated.",'existed_file_details':file_details}
                                        else:
                                            ret['message']='Given file or folder is not found.' 

                                    elif file_type== 'classification_model':
                                        uploading_path="/home/docketrun/flask_application/application/dummy_upload"#"/home/docketrun/flask_application/application/dummy_upload"
                                        # checking given path is folder or not 
                                        if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                            if check_all_zip(uploading_file.filename):   
                                                # listing all files from the given folder                               
                                                all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                                for i in all_files:  
                                                    #getting size of each file                                   
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                                extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                                ret = {"success": True,"message":"Classification_model files are successfully updated.",'existed_file_details':file_details}
                                        elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                            # listing all files from the given folder   
                                            all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))                                                
                                            #getting size of each file 
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                            ret = {"success": True,"message":"Classification_model files are successfully updated.",'existed_file_details':file_details}
                                        else:
                                            ret['message']='Given file or folder is not found.'
                                    elif file_type== 'detection_model':
                                        uploading_path="/home/docketrun/flask_application/application/dummy_upload"#"/home/docketrun/flask_application/application/dummy_upload"
                                        # checking given path is folder or not 
                                        if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                            if check_all_zip(uploading_file.filename):   
                                                # listing all files from the given folder                               
                                                all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                                for i in all_files:      
                                                    #getting size of each file 
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                                extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                                ret = {"success": True,"message":"Detection_model files are successfully updated.",'existed_file_details':file_details}
                                        elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                            # listing all files from the given folder   
                                            all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))                                                
                                            #getting size of each file 
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)size_of_file = os.stat(all_files).st_size
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                            ret = {"success": True,"message":"Detection_model files are successfully updated.",'existed_file_details':file_details}
                                        else:
                                            ret['message']='Given file or folder is not found.'

                                    elif file_type== 'analysis_config_code_file':
                                        uploading_path="/home/docketrun/flask_application/application/dummy_upload"#"/home/docketrun/flask_application/application/dummy_upload"
                                        # checking given path is folder or not 
                                        if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                            if check_all_zip(uploading_file.filename):     
                                                # listing all files from the given folder                             
                                                all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                                for i in all_files:    
                                                    #getting size of each file                                 
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                                extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                                ret = {"success": True,"message":"Analysis_config_code_file files are successfully updated.",'existed_file_details':file_details}
                                        elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                            # listing all files from the given folder   
                                            all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename)) 
                                            #getting size of each file 
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                            ret = {"success": True,"message":"Analysis_config_code_file files are successfully updated.",'existed_file_details':file_details}
                                        else:
                                            ret['message']='Given file or folder is not found.'
                                    else:
                                        ret['message'] ='Given file type is not found.'
                                else:
                                    ret['message'] ='Given file type is not in the list, Please try to give correct file type.'
                            else:
                                ret['message']= "Device token has exipred."
                    else:
                        file_details=[]
                        list_of_file_type= ['common','classification_model','detection_model','analysis_config_code_file']
                        if file_type in list_of_file_type :
                            if file_type == 'common':
                                uploading_path="/home/docketrun/flask_application/application/dummy_upload"#"/home/docketrun/flask_application/application/dummy_upload"
                                # checking given path is folder or not 
                                if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                    if check_all_zip(uploading_file.filename):    
                                        # listing all files from the given folder                              
                                        all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                        for i in all_files:
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                        extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                        ret = {"success": True,"message":"Common files are successfully updated.",'existed_file_details':file_details}
                                elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                    # listing all files from the given folder   
                                    all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename)) 
                                    #getting size of each file 
                                    size_of_file = os.stat(all_files).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                    uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                    ret = {"success": True,"message":"Common files are successfully updated.",'existed_file_details':file_details}
                                else:
                                    ret['message']='Given file or folder is not found.'

                            elif file_type== 'classification_model':
                                uploading_path="/home/docketrun/flask_application/application/dummy_upload"#"/home/docketrun/flask_application/application/dummy_upload
                                if check_all_zip(uploading_file.filename):   
                                    # listing all files from the given folder                               
                                    all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                    for i in all_files:       
                                        #getting size of each file 
                                        size_of_file = os.stat(i).st_size
                                        #converting file size Bytes into Kilo Bytes
                                        final_size = str(round(size_of_file / 1024, 3))+'KB'
                                        #file created time function gives created time of each file from the given directory 
                                        #file_created_time(i)
                                        #file modified time function gives last modified time of each file from the given directory
                                        #file_modified_time(i)
                                        file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                    uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                    extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                    ret = {"success": True,"message":"classification_model files are successfully updated.",'existed_file_details':file_details}
                                elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                    # listing all files from the given folder   
                                    all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                            
                                    #getting size of each file 
                                    size_of_file = os.stat(all_files).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                    uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                    ret = {"success": True,"message":"classification_model files are successfully updated.",'existed_file_details':file_details}
                                else:
                                    ret['message']='Given file or folder is not found.'

                            elif file_type== 'detection_model':
                                uploading_path="/home/docketrun/flask_application/application/dummy_upload"#"/home/docketrun/flask_application/application/dummy_upload"
                                # checking given path is folder or not 
                                if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                    if check_all_zip(uploading_file.filename):   
                                        # listing all files from the given folder                               
                                        all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                        for i in all_files:   
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                        extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                        ret = {"success": True,"message":"Detection_model files are successfully updated.",'existed_file_details':file_details}
                                elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                    # listing all files from the given folder   
                                    all_files = is_file_or_directory(all_files)                                            
                                    #getting size of each file 
                                    size_of_file = os.stat(all_files).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                    uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                    ret = {"success": True,"message":"Detection_model files are successfully updated.",'existed_file_details':file_details}
                                else:
                                    ret['message']='Given file or folder is not found.'

                            elif file_type== 'analysis_config_code_file':
                                uploading_path="/home/docketrun/flask_application/application/dummy_upload"#"/home/docketrun/flask_application/application/dummy_upload"
                                # checking given path is folder or not 
                                if is__directory_(os.path.join(uploading_path,uploading_file.filename)):
                                    if check_all_zip(uploading_file.filename): 
                                        # listing all files from the given folder                                 
                                        all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))
                                        for i in all_files:      
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        uploading_file.save(os.path.join(uploading_path,uploading_file.filename))  
                                        extract_archive(os.path.join(uploading_path,uploading_file.filename))
                                        ret = {"success": True,"message":"Analysis_config_code_file files are successfully updated.",'existed_file_details':file_details}
                                elif is_file_(os.path.join(uploading_path,uploading_file.filename)):
                                    # listing all files from the given folder   
                                    all_files = is_file_or_directory(os.path.join(uploading_path,uploading_file.filename))                                            
                                    #getting size of each file 
                                    size_of_file = os.stat(all_files).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                    uploading_file.save(os.path.join(uploading_path,uploading_file.filename))   
                                    ret = {"success": True,"message":"Analysis_config_code_file files are successfully updated.",'existed_file_details':file_details}
                                else:
                                    ret['message']='Given file or folder is not found.'
                            else:
                                ret['message'] ='Given file type is not found.'
                        else:
                            ret['message'] ='Given file type is not in the list, Please try to give correct file type.'
            else:
                ret={'message':'Please enter missed json keys '+ str(missing_key_final)+'.',"success": False}  
    #else:
    except Exception as e:
        ret['message']='Error --- ' +str(e)+'.'
    return  jsonify(ret)

@app.route('/edge/device/application/filedelete/<file_type_delete>', methods=['POST'])
def filedelete(file_type_delete):
    ret = {"success": False,"message":"An unexpected error has occurred, please try again later."}
    try:

        if file_type_delete =='other':
            jsonobject=request.json
            if jsonobject == None:
                jsonobject = {}
            request_key_array=['device_id','file_type','destination_path','file_or_folder_name']
            jsonobjectarray= list(set(jsonobject))
            # checking missed key from frontend 
            missing_key=set(request_key_array).difference(jsonobjectarray)
            if not missing_key :
                # checking empty values from frontend            
                output=[k for k, v in jsonobject.items() if v =='']
                if output :
                    ret['message']='you have missed these parameters '+str(output)+' to enter. please enter properly.'
                else:
                    device_id=jsonobject['device_id']
                    file_type =jsonobject['file_type']
                    file_or_folder_name=jsonobject['file_or_folder_name'] 
                    device_token =jsonobject['device_token']
                    token_status =jsonobject['token_status']
                    device_token_str = "'"+device_token+"'"
                    # checking token_status
                    if token_status == "True":
                        # fetching data from db for device token 
                        cur.execute("""SELECT * FROM device_token_generater_1 WHERE device_token = {0};""". format(device_token_str))
                        row =  cur.fetchall()
                        # checking whethere given token key is exist or not 
                        if not row:
                            ret['message']='Invalid token'
                        else:
                            token_generate_time_from_db = None
                            for i in row:
                                device_id_from_db=i[0]
                                device_token_from_db=i[1]
                                token_status_from_db=i[2]
                                token_generate_time_from_db=i[3]
                            now  = datetime.now()#.astimezone(pytz.timezone('Asia/Calcutta'))
                            #print('now time = ',now)
                            #print('db time =',token_generate_time_from_db)
                            # checks token expiration time limit
                            #now.astimezone(pytz.timezone('Asia/Calcutta'))
                            difference = (now- token_generate_time_from_db )
                            #print(difference.days)
                            #print(difference.minutes)
                            #print(difference.seconds)
                            #7200
                            if difference.seconds < time_to_expired_token:
                            #now  = datetime.now().astimezone(pytz.timezone('Asia/Calcutta'))
                            # checks token expiration time limit
                            #if utc.localize(token_generate_time_from_db).astimezone(pytz.timezone('Asia/Calcutta')) < now:                     
                                file_details=[]            
                                if file_type_delete == 'other':
                                    uploading_path=jsonobject['destination_path']#"/home/docketrun/flask_application/application/dummy_upload"
                                    if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                        all_files =[] 
                                        for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                            for file in files:
                                                all_files.append(os.path.join(root,file))
                                        for i in all_files:
                                            try:
                                                #getting size of each file 
                                                #getting size of each file 
                                                size_of_file = os.stat(i).st_size
                                                #converting file size Bytes into Kilo Bytes
                                                final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                #file created time function gives created time of each file from the given directory 
                                                #file_created_time(i)
                                                #file modified time function gives last modified time of each file from the given directory
                                                #file_modified_time(i)
                                                file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                            except:
                                                file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                        shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                        ret = {"success": True,"message":"Other folder is successfully deleted.",'existed_file_details':file_details}
                                    elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                        all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                        #getting size of each file 
                                        size_of_file = os.stat(all_files).st_size
                                        #converting file size Bytes into Kilo Bytes
                                        final_size = str(round(size_of_file / 1024, 3))+'KB'
                                        #file created time function gives created time of each file from the given directory 
                                        #file_created_time(i)
                                        #file modified time function gives last modified time of each file from the given directory
                                        #file_modified_time(i)
                                        file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                        os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                        ret = {"success": True,"message":"Other file is successfully deleted.",'existed_file_details':file_details}
                                    else:
                                        ret['message']='Given file or folder is not found.'
                                else:
                                    ret['message']='Given file type is not found.'
                            else:
                                ret['message']='Device token has expired.'
                    else:
                        file_details=[]            
                        if file_type_delete == 'other':
                            uploading_path=jsonobject['destination_path']#"/home/docketrun/flask_application/application/dummy_upload"
                            if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                all_files =[] 
                                for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                    for file in files:
                                        all_files.append(os.path.join(root,file))
                                for i in all_files:
                                    try:
                                        #getting size of each file 
                                        size_of_file = os.stat(i).st_size
                                        #converting file size Bytes into Kilo Bytes
                                        final_size = str(round(size_of_file / 1024, 3))+'KB'
                                        #file created time function gives created time of each file from the given directory 
                                        #file_created_time(i)
                                        #file modified time function gives last modified time of each file from the given directory
                                        #file_modified_time(i)
                                        file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                    except:
                                        file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                ret = {"success": True,"message":"Other folder is successfully deleted.",'existed_file_details':file_details}


                            elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                #getting size of each file 
                                size_of_file = os.stat(all_files).st_size
                                #converting file size Bytes into Kilo Bytes
                                final_size = str(round(size_of_file / 1024, 3))+'KB'
                                #file created time function gives created time of each file from the given directory 
                                #file_created_time(i)
                                #file modified time function gives last modified time of each file from the given directory
                                #file_modified_time(i)
                                file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                ret = {"success": True,"message":"Other file is successfully deleted.",'existed_file_details':file_details}
                            else:
                                ret['message']='Given file or folder is not found.'
                        else:
                            ret['message']='Given file type is not found.'                    
            else:
                ret={'message':'Please enter missed json keys '+ str(missing_key)+'.',"success": False}


        else:
            ret = {"success": False,"message":"An unexpected error has occurred, please try again later."}
            jsonobject=request.json
            if jsonobject == None:
                jsonobject = {}
            request_key_array=['device_id','file_type','file_or_folder_name']
            jsonobjectarray= list(set(jsonobject))
            # checking missed key from frontend 
            missing_key=set(request_key_array).difference(jsonobjectarray)
            if not missing_key : 
                # checking empty values from frontend           
                output=[k for k, v in jsonobject.items() if v =='']
                if output :
                    ret['message']='you have missed these parameters '+str(output)+' to enter. please enter properly.'
                else:
                    device_id=jsonobject['device_id']
                    file_type =jsonobject['file_type']
                    file_or_folder_name=jsonobject['file_or_folder_name'] 
                    device_token =jsonobject['device_token']
                    token_status =jsonobject['token_status']
                    device_token_str = "'"+device_token+"'"
                    # checking token_status
                    if token_status == "True":
                        # fetching data from db for device token 
                        cur.execute("""SELECT * FROM device_token_generater_1 WHERE device_token = {0};""". format(device_token_str))
                        row =  cur.fetchall()
                        # checking whethere given token key is exist or not 
                        if not row:
                            ret['message']='Invalid token key.'
                        else: 
                            token_generate_time_from_db = None
                            for i in row:
                                device_id_from_db=i[0]
                                device_token_from_db=i[1]
                                token_status_from_db=i[2]
                                token_generate_time_from_db=i[3]
                            #now  = datetime.now().astimezone(pytz.timezone('Asia/Calcutta'))
                            # checks token expiration time limit
                            now  = datetime.now()#.astimezone(pytz.timezone('Asia/Calcutta'))
                            #print('now time = ',now)
                            #print('db time =',token_generate_time_from_db)
                            # checks token expiration time limit
                            #now.astimezone(pytz.timezone('Asia/Calcutta'))
                            difference = (now- token_generate_time_from_db )
                            #print(difference.days)
                            #print(difference.minutes)
                            #print(difference.seconds)
                            #7200
                            if difference.seconds < time_to_expired_token:    
                            #if utc.localize(token_generate_time_from_db).astimezone(pytz.timezone('Asia/Calcutta')) < now: 
                                file_details=[]
                                list_of_file_type= ['common','classification_model','detection_model','analysis_config_code_file']
                                if file_type in list_of_file_type :
                                    if file_type == 'common':
                                        uploading_path="/home/docketrun/flask_application/application/dummy_upload"
                                        if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                            all_files =[]
                                            for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                                for file in files:
                                                    all_files.append(os.path.join(root,file))
                                            for i in all_files:
                                                try:
                                                    #getting size of each file 
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                except:
                                                    file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                            shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                            ret = {"success": True,"message":"Common folders are successfully deleted.",'existed_file_details':file_details}

                                        elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                            all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                            #getting size of each file 
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                            ret = {"success": True,"message":"Common file is successfully deleted.",'existed_file_details':file_details}
                                        else:
                                            ret['message']='Given file or folder is not found.'
                                    elif file_type == 'classification_model':
                                        uploading_path="/home/docketrun/flask_application/application/dummy_upload"
                                        if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                            all_files =[]
                                            for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                                for file in files:
                                                    all_files.append(os.path.join(root,file))
                                            for i in all_files:
                                                try:
                                                    #getting size of each file 
                                                    #getting size of each file 
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                except:
                                                    file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                            shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                            ret = {"success": True,"message":"Classification_model folders are successfully deleted.",'existed_file_details':file_details}
                                        elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                            all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                            #getting size of each file 
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                            ret = {"success": True,"message":"Classification_model file is successfully deleted.",'existed_file_details':file_details}                                            
                                        else:
                                            ret['message']='Given file or folder is not found.'

                                    elif file_type== 'detection_model':
                                        uploading_path="/home/docketrun/flask_application/application/dummy_upload"
                                        if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                            all_files =[]
                                            for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                                for file in files:
                                                    all_files.append(os.path.join(root,file))
                                            for i in all_files:
                                                try:
                                                    #getting size of each file 
                                                    #getting size of each file 
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                except:
                                                    file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                            shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                            ret = {"success": True,"message":"Detection_model folders are successfully deleted.",'existed_file_details':file_details}

                                        elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                            all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                            #getting size of each file 
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                            ret = {"success": True,"message":"Detection_model file is successfully deleted.",'existed_file_details':file_details}                                            
                                        else:
                                            ret['message']='Given file or folder is not found.'
                                    elif file_type== 'analysis_config_code_file':
                                        uploading_path="/home/docketrun/flask_application/application/dummy_upload"
                                        if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                            all_files =[]
                                            for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                                for file in files:
                                                    all_files.append(os.path.join(root,file))
                                            for i in all_files:
                                                try:
                                                    #getting size of each file 
                                                    #getting size of each file 
                                                    size_of_file = os.stat(i).st_size
                                                    #converting file size Bytes into Kilo Bytes
                                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                                    #file created time function gives created time of each file from the given directory 
                                                    #file_created_time(i)
                                                    #file modified time function gives last modified time of each file from the given directory
                                                    #file_modified_time(i)
                                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                                except:
                                                    file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                            shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                            ret = {"success": True,"message":"Analysis_config_code folders are successfully deleted.",'existed_file_details':file_details}
                                        elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                            all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                            #getting size of each file 
                                            size_of_file = os.stat(all_files).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                            os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                            ret = {"success": True,"message":"Analysis_config_code file is successfully deleted.",'existed_file_details':file_details}
                                        else:
                                            ret['message']='Given file or folder is not found.'
                                    else:
                                        ret['message']='Given file type is not found.'
                                else:
                                    ret['message'] ='Given file type is not found in the list, Please give valid file type.'
                            else:
                                ret['message'] ='Device token has expired.'
                    else:
                        file_details=[]
                        list_of_file_type= ['common','classification_model','detection_model','analysis_config_code_file']
                        if file_type in list_of_file_type :
                            if file_type == 'common':
                                uploading_path="/home/docketrun/flask_application/application/dummy_upload"
                                if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                    all_files =[]
                                    for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                        for file in files:
                                            all_files.append(os.path.join(root,file))
                                    for i in all_files:
                                        try: 
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        except:
                                            file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                    shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                    ret = {"success": True,"message":"Common folders are successfully deleted.",'existed_file_details':file_details}

                                elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                    all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                    #getting size of each file 
                                    size_of_file = os.stat(all_files).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                    os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                    ret = {"success": True,"message":"Common file is successfully deleted.",'existed_file_details':file_details}                                        
                                else:
                                    ret['message']='Given file or folder is not found.'

                            elif file_type == 'classification_model':
                                uploading_path="/home/docketrun/flask_application/application/dummy_upload"
                                if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                    all_files =[]
                                    for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                        for file in files:
                                            all_files.append(os.path.join(root,file))
                                    for i in all_files:
                                        try:
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        except:
                                            file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                    shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                    ret = {"success": True,"message":"classification_model folders are successfully deleted.",'existed_file_details':file_details}

                                elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                    all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                    #getting size of each file 
                                    size_of_file = os.stat(all_files).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                    os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                    ret = {"success": True,"message":"Classification_model file is successfully deleted.",'existed_file_details':file_details}                                            
                                else:
                                    ret['message']='Given file or folder is not found.'

                            elif file_type== 'detection_model':
                                uploading_path="/home/docketrun/flask_application/application/dummy_upload"
                                if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                    all_files =[]
                                    for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                        for file in files:
                                            all_files.append(os.path.join(root,file))                                    
                                    for i in all_files:
                                        try:
                                            #getting size of each file 
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        except:
                                            file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                    shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                    ret = {"success": True,"message":"Detection_model folders are successfully deleted.",'existed_file_details':file_details}
                                elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                    all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                    #getting size of each file 
                                    size_of_file = os.stat(all_files).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                    os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                    ret = {"success": True,"message":"Detection_model file is successfully deleted.",'existed_file_details':file_details}                                            
                                else:
                                    ret['message']='Given file or folder is not found.'
                            elif file_type== 'analysis_config_code_file':
                                uploading_path="/home/docketrun/flask_application/application/dummy_upload"
                                if os.path.isdir(os.path.join(uploading_path,file_or_folder_name)): 
                                    all_files =[]
                                    for root, dirs, files in os.walk(os.path.join(uploading_path,file_or_folder_name)):
                                        for file in files:
                                            all_files.append(os.path.join(root,file))
                                    for i in all_files:
                                        try:
                                            #getting size of each file 
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        except:
                                            file_details.append({'filename':i,'file_size':None,'file_created_time':None,'file_modified_time':None})
                                    shutil.rmtree(os.path.join(uploading_path,file_or_folder_name), ignore_errors=True)
                                    ret = {"success": True,"message":"Analysis_config_code folders are successfully deleted.",'existed_file_details':file_details}
                                elif os.path.isfile(os.path.join(uploading_path,file_or_folder_name)):
                                    all_files = is_file_or_directory(os.path.join(uploading_path,file_or_folder_name))                                
                                    #getting size of each file 
                                    size_of_file = os.stat(all_files).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':all_files,'file_size':final_size,'file_created_time':file_created_time(all_files),'file_modified_time':file_modified_time(all_files)})
                                    os.remove(os.path.join(uploading_path,file_or_folder_name)  )  
                                    ret = {"success": True,"message":"Analysis_config_code file is successfully deleted.",'existed_file_details':file_details}
                                else:
                                    ret['message']='Given file or folder is not found.'
                            else:
                                ret['message'] ='Given file type is not found.'
                        else:
                            ret['message'] = "Given file type not found in the list, Please give valid file type."                    
            else:
                ret={'message':'Please enter missed json keys '+ str(missing_key)+'.',"success": False}                  
    except Exception as e:
        ret['message']='Error --- ' +str(e)+'.'
    return  jsonify(ret)


@app.route('/edge/device/application/list_files' ,methods=['POST'])
def list_all_files_from_folder():
    ret = {"success": False,"message":"An unexpected error has occurred, please try again later."}
    try:
        jsonobject=request.json
        if jsonobject == None:
            jsonobject = {}
        request_key_array=['folder_path_to_list_files','device_id']
        jsonobjectarray= list(set(jsonobject))
        # checking missed key from frontend 
        missing_key=set(request_key_array).difference(jsonobjectarray)
        if not missing_key:
            # checking empty values from frontend
            output=[k for k, v in jsonobject.items() if v =='']
            if output:
                ret['message']='you have missed these parameters '+str(output)+' to enter. please enter properly.'
            else:
                device_id=jsonobject['device_id']
                uploading_path =jsonobject['folder_path_to_list_files']
                device_token =jsonobject['device_token']
                token_status =jsonobject['token_status']
                device_token_str = "'"+device_token+"'"
                # checking token_status
                if token_status == "True":
                    # fetching data from db for device token 
                    cur.execute("""SELECT * FROM device_token_generater_1 WHERE device_token = {0};""". format(device_token_str))
                    row =  cur.fetchall()
                    # checking whethere given token key is exist or not 
                    if not row:
                        ret['message']='Invalid token key.'
                    else: 
                        token_generate_time_from_db = None
                        for i in row:
                            device_id_from_db=i[0]
                            device_token_from_db=i[1]
                            token_status_from_db=i[2]
                            token_generate_time_from_db=i[3]
                        now  = datetime.now()#.astimezone(pytz.timezone('Asia/Calcutta'))
                        #print('now time = ',now)
                        #print('db time =',token_generate_time_from_db)
                        # checks token expiration time limit
                        #now.astimezone(pytz.timezone('Asia/Calcutta'))
                        difference = (now- token_generate_time_from_db )
                        #print(difference.days)
                        #print(difference.minutes)
                        #print(difference.seconds)
                        #7200
                        if difference.seconds < time_to_expired_token: 
                        #if utc.localize(token_generate_time_from_db).astimezone(pytz.timezone('Asia/Calcutta')) > now:
                        #if utc.localize(token_generate_time_from_db).astimezone(pytz.timezone('Asia/Calcutta')) > now :
                            file_details=[]
                            if os.path.exists(uploading_path):
                                all_files = list_all_files(uploading_path)#'/home/docketrun/flask_application/application/dummy_upload/new_folder')
                                if len(all_files) != 0:                
                                    for i in all_files:
                                        try:
                                            #getting size of each file 
                                            #getting size of each file 
                                            size_of_file = os.stat(i).st_size
                                            #converting file size Bytes into Kilo Bytes
                                            final_size = str(round(size_of_file / 1024, 3))+'KB'
                                            #file created time function gives created time of each file from the given directory 
                                            #file_created_time(i)
                                            #file modified time function gives last modified time of each file from the given directory
                                            #file_modified_time(i)
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                        except:
                                            file_details.append({'filename':i,'file_size':final_size,'file_created_time':None,'file_modified_time':None})
                                    ret = {"success": True,"message":"Files are listed from given folder.",'listed_files':file_details}
                                else:
                                    ret['message']='Given folder is empty.'
                            else:
                                ret['message']="Given folder path is doesn't exist."
                        else:
                            ret['message']='Device token key has expired.'
                else:
                    file_details=[]
                    if os.path.exists(uploading_path):
                        all_files = list_all_files(uploading_path)#'/home/docketrun/flask_application/application/dummy_upload/new_folder')
                        if len(all_files) != 0:                
                            for i in all_files:
                                try:
                                    #getting size of each file 
                                    #getting size of each file 
                                    size_of_file = os.stat(i).st_size
                                    #converting file size Bytes into Kilo Bytes
                                    final_size = str(round(size_of_file / 1024, 3))+'KB'
                                    #file created time function gives created time of each file from the given directory 
                                    #file_created_time(i)
                                    #file modified time function gives last modified time of each file from the given directory
                                    #file_modified_time(i)
                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':file_created_time(i),'file_modified_time':file_modified_time(i)})
                                except:
                                    file_details.append({'filename':i,'file_size':final_size,'file_created_time':None,'file_modified_time':None})
                            ret = {"success": True,"message":"Files are listed from given folder.",'listed_files':file_details}
                        else:
                            ret['message']='Given folder is empty.'
                    else:
                        ret['message'] = "Given folder path is doesn't exist."
        else:
            ret={'message':'Please enter missed json keys '+ str(missing_key)+'.',"success": False}
    except Exception as e:
        ret['message']='Error --- ' +str(e)+'.'
    return  jsonify(ret)



@app.route('/edge/device/application/run_command' ,methods=['POST'])
def run_commands_in_device():
    ret = {"success": False,"message":"An unexpected error has occurred, please try again later."}
    try:
        jsonobject=request.json
        if jsonobject == None:
            jsonobject = {}
        request_key_array=['device_id','path','command']
        jsonobjectarray= list(set(jsonobject))
        # checking missed key from frontend 
        missing_key=set(request_key_array).difference(jsonobjectarray)
        if not missing_key:
            # checking empty values from frontend
            output=[k for k, v in jsonobject.items() if v =='']
            if output:
                ret['message']='You have missed these parameters '+str(output)+' to enter. please enter properly.'
            else:
                device_id=jsonobject['device_id']
                path_of_command =jsonobject['path']
                command_line= jsonobject['command']
                cmd='cd'+' '+str(path_of_command)+' '+'&&'+' '+str(command_line)
                device_token =jsonobject['device_token']
                token_status =jsonobject['token_status']
                device_token_str = "'"+device_token+"'"
                if token_status == "True":
                    # fetching data from db for device token 
                    cur.execute("""SELECT * FROM device_token_generater_1 WHERE device_token = {0};""". format(device_token_str))
                    row =  cur.fetchall()
                    # checking whethere given token key is exist or not 
                    if not row:
                        ret['message']='Invalid token key.'
                    else:
                        token_generate_time_from_db = None
                        for i in row:
                            device_id_from_db=i[0]
                            device_token_from_db=i[1]
                            token_status_from_db=i[2]
                            token_generate_time_from_db=i[3]
                        now  = datetime.now()#.astimezone(pytz.timezone('Asia/Calcutta'))
                        #print('now time = ',now)
                        #print('db time =',token_generate_time_from_db)
                        # checks token expiration time limit
                        #now.astimezone(pytz.timezone('Asia/Calcutta'))
                        difference = (now- token_generate_time_from_db )
                        #print(difference.days)
                        #print(difference.minutes)
                        #print(difference.seconds)
                        #7200
                        if difference.seconds < time_to_expired_token: 
                        #now  = datetime.now().astimezone(pytz.timezone('Asia/Calcutta'))
                        # checks token expiration time limit
                        #if utc.localize(token_generate_time_from_db).astimezone(pytz.timezone('Asia/Calcutta')) < now:
                            process = subprocess.getstatusoutput(cmd)
                            if process[0]==0:
                                if process[-1]=='':
                                    ret = {"success": True,"message":'Command is excuted successfully.'}
                                else:
                                    ret = {"success": True,"message":process[-1]+'.'}
                            elif process[0]==1:
                                ret["message"]=process[-1]+"."
                        else:
                            ret["message"]="Device token key has expired."
                else:
                    process = subprocess.getstatusoutput(cmd)
                    if process[0]==0:
                        if process[-1]=='':
                            ret = {"success": True,"message":'Command is excuted successfully.'}
                        else:
                            ret = {"success": True,"message":process[-1]+'.'}
                    elif process[0]==1:
                        ret["message"]=process[-1]+"."                
        else:
            ret={'message':'Please enter missed json keys '+ str(missing_key)+'.',"success": False}
    except Exception as e:
        ret['message']='Error --- ' +str(e)+'.'

    return  jsonify(ret)



@app.route('/edge/device/application/device_generate_token' ,methods=['POST'])
def device_generate_token():
    ret = {"success": False,"message":"An unexpected error has occurred, please try again later."}
    #if True:
    try:
        jsonobject=request.json
        if jsonobject == None:
            jsonobject = {}
        request_key_array=['device_id','device_token']
        jsonobjectarray= list(set(jsonobject))
        # checking missed key from frontend 
        missing_key=set(request_key_array).difference(jsonobjectarray)
        if not missing_key:
            # checking empty values from frontend
            output=[k for k, v in jsonobject.items() if v =='']
            if output:
                ret['message']='You have missed these parameters '+str(output)+' to enter. please enter properly.'
            else:
                device_id=jsonobject['device_id']
                device_token =jsonobject['device_token']
                token_status = jsonobject['token_status']
                #print(device_token)
                postgres_insert_query = """ insert into device_token_generater_1 (device_id,device_token,token_status,token_generate_time) 
                values (%s,%s,%s,%s)"""
                record_to_insert = (str(device_id),str(device_token) , str(token_status),(datetime.now() ))##(hours=2)
                cur.execute(postgres_insert_query, record_to_insert)
                #cur.execute(''' insert into device_token_generater_1 (device_id,device_token,token_status,token_generate_time) 
                #values ('abc123','adsadfkajdskfkjak24324','off',now());''')
                con.commit()
                ret={'message':'Device token recived successfully.',"success": True}
        else:
            ret={'message':'Please enter missed json keys '+ str(missing_key)+'.',"success": False}
    #else:
    except Exception as e:
        ret['message']='Error --- ' +str(e)+'.'
    return  jsonify(ret)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug = True)