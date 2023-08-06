from datetime import datetime
#import ast
import os, sys
sys.path.insert(0, '..')

import PlantNannyDB.settings as settings
import PlantNannyDB.database_use as db

def log_action(event,result, additional_info=''):
    #break apart event into components
    Assigned_id, Assigned_type, Assigned_name, device_id, device_name, action_freq=event
    
    
    #create writing information
    if result=='success':
        severity='d' #informational
        message_prefix='Successfully performed device action(s): '
    elif result=='failure':
        severity='w' #warning
        message_prefix='Failed to perform device action(s): '
        
    message_base= 'Assigned_type= %s, Assigned_id= %s, Assigned_name= %s, device_id= %s, device_name= %s' % (Assigned_type, Assigned_id, Assigned_name, device_id, device_name)
    
    message=message_prefix + message_base
    
    if additional_info!='':
        message=message + '; ' + additional_info
            
    log_info(severity,message)
    
    
def log_info(log_level,message, filename_log='log_trans', local=False):
    dt=datetime.now()

    if log_level=='p':
        print('(' + dt.strftime("%m/%d/%Y, %H:%M:%S") + '): ' + message)
    elif local==True:
        msg=[dt.strftime("%m/%d/%Y, %H:%M:%S"), log_level, message]
        log_locally(info=msg, filename=filename_log)
    elif log_level in settings.log_levels:
        db.write_to_db(table='log_trans',
                                 write_info=[datetime.now(), log_level, message])


def log_locally(info, filename, folder_path=settings.log_directory, filetype=settings.file_suffix):
    #called when database is unavailable
    
    fullpath=folder_path + filename + filetype
    
    #Make directory if doesnt already exist
    if os.path.exists(folder_path)==False:
        os.mkdir(folder_path)
    
    #Build string
    msg=''
    for item in info:
        if item==info[0]:
            msg+=str(item)
        else:
            msg+= '; ' + item
    
    #Write information to file
    f=open(fullpath,"a")
    f.write(msg + '\n')
    f.close()

def local_logs_exist():
    #checks if any queue exists for uploading data to database
    directory=settings.log_directory
    
    count=0
    logfiles=0
    otherfiles=0
    
    for filename in os.listdir(directory):
        if filename.endswith(".txt") or filename.endswith(".csv"):
            logfiles+=1
            f=open(directory+filename,"r")
            for line in f:
                count+= 1
        else:
            otherfile+=1
            
    if otherfiles!=0:
        msg="%s log(s) exist between %s log file(s) (%s non-log files exist)" % (count, logfiles, otherfiles)
    else:
        msg="%s log(s) exist between %s log file(s)" % (count, logfiles)
        
        
    return count, msg


def upload_local_logs():
#attempt to upload queued logs to database
    log_info(log_level = 'p', message = "Attempting to upload queued logs....")

    directory=settings.log_directory
    logfiles=0
    count=0
    logs_success=0
    logs_failed=0
    
    #loop through log files
    for filename in os.listdir(directory):
        if filename.endswith(".txt") or filename.endswith(".csv"):
            logfiles+=1
            table_name=os.path.splitext(filename)[0]
            
            #Below section opens file (read) and stores info in variable
            #Next, the file is opened (write) to overwrite the file
            #    ONLY info that couldn't be uploaded
            with open(directory+filename,"r") as f:
                #loop through log lines
                lines = f.readlines()
            with open(directory+filename, "w") as f:
                for line in lines:
                    count+= 1
                    
                    #extract information
                    line=str(line)
                    list_str=line.rstrip()
                    lst=list_str.split('; ')
                    
                    #attempt to upload to db
                    try:
                        db.write_to_db(table=table_name,
                                       write_info=lst,
                                       log_local=False)
                        logs_success+=1
                    except:
                        f.write(line)
                        logs_failed+=1
    
    #Build result message
    msg='Results of re-uploading queued logs: %s successful,  %s failed (%s files involved)' % (logs_success, logs_failed, logfiles)                   
    log_info(log_level='p',message=msg)  
                

if __name__=="__main__":
    local_logs_exist()