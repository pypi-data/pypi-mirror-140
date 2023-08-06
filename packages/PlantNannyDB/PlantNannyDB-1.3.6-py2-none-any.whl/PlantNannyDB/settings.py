#settings.py

"""---------QUICK-EDIT SETTINGS---------"""
database_connection='Local'

#Interval for checking for new information
refresh_mins=10
#Instrument Settings
read_frequency_mins=1



"""-------ADVANCED CONFIG SETTINGS-------"""
#MySQL Database Information (Local):
database_local={
    'db_name'       :   'plantnanny',    
    'hostname'      :   'localhost',
    'db_username'   :   'mainuser',
    'db_password'   :   'mainuser'
}
phpmyadmin_password='Balk45610'

#MySQL Database Information (Remote):
database_remote={
    'db_name'       :   'plantnan_plantnanny',       #cpanelUsername_databaseName
    'hostname'      :   '50.87.253.14:3306',        #server IP Address:connection port
    'db_username'   :   'plantnan_raspberrypi',  #cpanelUsername_databaseUsername
    'db_password'   :   'FBoIxeR7bB=b'          #database User Password
}

#Local Logging Information:
#(only used to store data if MySQL database is unavailable)
log_directory='/home/pi/Documents/Plant_Nanny/Logs/'
file_suffix='.txt'

#Log levels permitted; comment out any undesired level
log_levels=(
    'i', #informational
    'w', #warning
    #'d', #debugging
    's', #severe
    #'p', #print (prints to the shell; not logged into database) DO NOT UNCOMMENT!!!
    )
    
#I2C Instruments
addr_sensor_soil=0X36
addr_sensor_gas=0X58

#Camera Information
image_directory='/home/pi/Documents/Plant_Nanny/Plant-Photos/'
image_filetype='.jpg'

#Graphics Information
graphics_directory='/home/pi/Documents/Plant_Nanny/Graphics/'
graphics_filetype='.png'
