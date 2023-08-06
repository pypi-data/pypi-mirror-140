
""" Database-Related Dictionaries:  """

#Writing information to database
sql_insert={
    'soilsensor_trans'  :   "INSERT INTO soilsensor_trans (DateTime, plant_id, SoilTemp_DegC, SoilMoisture_val) VALUES (%s, %s, %s, %s)",
    'gassensor_trans'   :   "INSERT INTO `gassensor_trans` (`record_id`, `DateTime`, `room_id`, `eCO2_ppm`, `TVOC_ppb`) VALUES (NULL, %s, %s, %s, %s)",
    'lightsensor_trans' :   "INSERT INTO `lightsensor_trans` (`record_id`, `DateTime`, `room_id`, `colour_red`, `colour_green`, `colour_blue`, `colour_clear`) VALUES (NULL, %s, %s, %s, %s, %s, %s)",
    'airsensor_trans'   :   "INSERT INTO `airsensor_trans` (`record_id`, `DateTime`, `room_id`, `AirTemp_DegC`, `AirHumidity_percent`, `AirGas_ohms`, `AirPressure_hpa`) VALUES (NULL, %s, %s, %s, %s, %s, %s)",
    'photo_trans'       :   "INSERT INTO `photo_trans` (`record_id`, `capture_datetime`, `plant_id`, `image_path`) VALUES (NULL, %s, %s, %s)",
    'log_trans'         :   "INSERT INTO `log_trans` (`record_id`, `datetime`, `log_type`, `log_message`) VALUES (NULL, %s, %s, %s)"
}           

#Retrieving information from database
sql_select={
    'air_temp'          :   "SELECT CAST(a.DateTime as Time) as Timestamp, a.AirTemp_DegC FROM airsensor_trans a WHERE a.DateTime >= '%s' AND a.DateTime < '%s' AND a.room_id= '%s'",
    'air_humidity'      :   "SELECT CAST(a.DateTime as Time) as Timestamp, a.AirHumidity_percent FROM airsensor_trans a WHERE a.DateTime >= '%s' AND a.DateTime < '%s' AND a.room_id= '%s'",
    'sensors'           :   "SELECT * FROM sensors",
    'sensor_freq'       :   "SELECT read_frequency_min FROM sensors",
    'device_assignments':   "SELECT DA.`id_room` AS Assigned_ID, 'Environment' AS Assigned_Type, E.`name_short` AS Assigned_Name, DA.`id_device`, D.`model` AS Device_Name, COALESCE(DA.`action_freq_mins`, D.`default_action_freq_mins`) AS Action_Frequency FROM `def_device_assignments` AS DA LEFT JOIN `def_devices` AS D ON DA.`id_device`=D.id LEFT JOIN `def_environments` AS E ON DA.id_room=E.id_room WHERE DA.`active`=1 AND E.`active`=1 AND D.`supported`=1 AND DA.id_room>0 UNION SELECT DA.`id_plant` AS Assigned_ID, 'Plant' AS Assigned_Type, P.`name` AS Assigned_Name, DA.`id_device`, D.`model` AS Device_Name, COALESCE(DA.`action_freq_mins`, D.`default_action_freq_mins`) AS Action_Frequency FROM `def_device_assignments` AS DA LEFT JOIN `def_devices` AS D ON DA.`id_device`=D.id LEFT JOIN `def_plants` AS P ON DA.id_plant=P.id WHERE DA.`active`=1 AND P.`active`=1 AND D.`supported`=1 AND DA.id_plant>0"
}

""" Error Handling Dictionaries:    """

#Error Statements
err_statement={}    #TODO: Complete Dictionary

if __name__=="__main__":
    x=sql_select['air_humidity']
    print(x)