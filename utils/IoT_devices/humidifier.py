# import paho.mqtt.client as mqtt
# import ssl
import os.path
import sys
import logging
import time
import json

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/logger"))
    import logger as log
except ImportError:
    print("File: " + __file__ + " - Import log failed")
    exit()

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "MQTT"))
    import mqtt_client as mqtt
except ImportError:
    print("File: " + __file__ + " - Import MQTT failed")
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/JSON"))
    import json_utils
except ImportError:
    print("File: " + __file__ + " - Import JSON failed")
    exit()

# airPurifier_sub_topic = "dev/000AE2345D31MydWBUOg/sub"
# airPurifier_pub_topic = "dev/000AE2345D31MydWBUOg/pub"

# mbp162_sub_topic = "dev/000AE22F0021PJPVcjxA/sub"
# mbp162_pub_topic = "dev/000AE22F0021PJPVcjxA/pub"

humidifier_topic_key = "000AE2390DDEgqDQNJRQ"

hyper_sub_topic = "hyper/xxxxxxxxxxxx/sub"
getsetting_command = "get_sys_info"
power_on_command = "power_on"
power_off_command = "power_off"
set_mist_command = "set_mist_level&value="
set_hotmist_command = "set_hotmist&value="

class HubbleHumidifierDevice(object):
    def __init__(self, mqttc, topic_key):
        self.mqttc = mqttc
        self.topic_key = topic_key
        self.sub_topic = "dev/"+topic_key+"/sub"
        self.pub_topic = "dev/"+topic_key+"/pub"

    def dev_subscribe(self):
        self.mqttc.subscribe(self.pub_topic)

    def dev_publish(self, message):
        self.mqttc.publish(self.sub_topic, message)

    def dev_send_command(self, command):
        message = "2app_topic_sub="+hyper_sub_topic+"&time="+str(int(time.time()))+"&action=command&command="+command
        self.mqttc.publish(self.sub_topic, message)  

    def update_status(self, get_sys_info):
        jsonSysInfo = json.loads(get_sys_info)
        self.power_s = jsonSysInfo["power"]
        self.mist_level_s = jsonSysInfo["mist_level"]
        self.timer_left_hour_s = jsonSysInfo["timer_left_hour"]
        self.timer_left_minute_s = jsonSysInfo["timer_left_minute"]
        self.filter_timer_s = jsonSysInfo["filter_timer"]
        self.ota_status_s = jsonSysInfo["ota_status"]
        self.low_water_s = jsonSysInfo["low_water"]
        self.hot_mist_s = jsonSysInfo["hot_mist"]
        self.air_purification_s = jsonSysInfo["air_purification"]
        self.nlight_level_s = jsonSysInfo["nlight_level"]
        self.buzzer_s = jsonSysInfo["buzzer"]
        self.baby_mode_s = jsonSysInfo["baby_mode"]
        self.hum_set_s = jsonSysInfo["hum_set"]
        self.hum_measure_s = jsonSysInfo["hum_measure"]
        self.ipl_s = jsonSysInfo["ipl"]

    def get_power_s(self):
        return self.power_s

    def set_power_s(self, value):
        if value == 1 or value == "on":
            self.dev_send_command("power_on")
            return 0
        elif value == 0 or value == "off":
            self.dev_send_command("power_off")
            return 0
        else:
            return -1

    def get_mist_level_s(self):
        return self.mist_level_s

    def set_mist_level_s(self, value):
        if value > 0 and value < 5:
            self.dev_send_command("set_mist_level&value="+str(value))
        else:
            return -1

    def get_hot_mist_s(self):
        return self.hot_mist_s

    def set_hot_mist_s(self, value):
        if value == 0 or value == 1:
            self.dev_send_command("set_hotmist&value="+str(value))
        elif value == "auto":
            self.dev_send_command("set_hotmist&value=4")
        else:
            return -1

    def get_humidity_s(self):
        return self.hum_measure_s

# The callback for when the client receives a CONNACK response from the server.
def mqttc_on_connect_cb(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    global mqttc

    if rc == 0:
        mqttc.is_connected = True
        mqttc.subscribe(hyper_sub_topic)

def mqttc_on_disconnect_cb(client, userdata, rc):
    global mqttc
    if rc != 0:
        print("Unexpected disconnection.") 
        mqttc.is_connected = False
        mqttc.subscribe(hyper_sub_topic)

# The callback for when a PUBLISH message is received from the server.
def mqttc_on_message_cb(client, userdata, msg):
    receivedString = str(msg.payload.decode('utf-8'))
    strings = receivedString.split(' ')
    print("From "+ msg.topic +" - Received: "+ receivedString)
    if str.find(receivedString, "get_sys_info") >= 0:
        humidifier2_A.update_status(strings[3])

def mqttc_on_publish_cb(client, userdata, mid):
    print("Published: " + str(mid))

mqttc = mqtt.hyperMQTTClient(connect_cb = mqttc_on_connect_cb, message_cb = mqttc_on_message_cb, publish_cb = mqttc_on_publish_cb)
humidifier2_A = HubbleHumidifierDevice(mqttc = mqttc, topic_key = humidifier_topic_key)
def processCommand(logger, audio_q, subCommand, typeCommand, parameters):
    if subCommand == "check":
        logger.log(logging.INFO, "The humidity is " + str(humidifier2_A.get_humidity_s()))
        speechScript = "The humidity is " + str(humidifier2_A.get_humidity_s()) + " right now"
        audio_q.put(str(json_utils.jsonSimpleGenerate("speech", speechScript)))
        return 0
    elif subCommand == "power" or subCommand == "switch":
        if typeCommand == "get":
            logger.log(logging.INFO, "The humidity is " + str(humidifier2_A.get_power_s()))
            speechScript = "The power status is " + str(humidifier2_A.get_power_s()) + " right now"
            audio_q.put(str(json_utils.jsonSimpleGenerate("speech", speechScript)))
            return 0
        elif typeCommand == "set":
            if parameters["on_off"] == "on":
                logger.log(logging.INFO, "Turn the power on")
                humidifier2_A.set_power_s(1)
            elif parameters["on_off"] == "off":
                logger.log(logging.INFO, "Turn the power off")
                humidifier2_A.set_power_s(0)
            else:
                # Toggle
                humidifier2_A.set_power_s(1 - humidifier2_A.get_power_s()) 
            return 0
        elif typeCommand == "on":
            logger.log(logging.INFO, "Turn the power on")
            humidifier2_A.set_power_s(1)
        elif typeCommand == "off":
            logger.log(logging.INFO, "Turn the power off")
            humidifier2_A.set_power_s(0)
            
            
    elif subCommand == "hotmist":
        if typeCommand == "get":
            speechScript = "The hot mist status is " + str(humidifier2_A.get_hot_mist_s()) + " right now"
            audio_q.put(str(json_utils.jsonSimpleGenerate("speech", speechScript)))
            return 0
        elif typeCommand == "set":
            if parameters["on_off"] == "on":
                humidifier2_A.set_hot_mist_s(1)
            elif parameters["on_off"] == "off":
                humidifier2_A.set_hot_mist_s(0)
            else:
                # Toggle
                humidifier2_A.set_hot_mist_s(1 - humidifier2_A.get_hot_mist_s()) 
            return 0
    elif subCommand == "mistlevel":
        if typeCommand == "get":
            speechScript = "The mist level is " + str(humidifier2_A.get_hot_mist_s()) + " now"
            audio_q.put(str(json_utils.jsonSimpleGenerate("speech", speechScript)))
            return 0
        elif typeCommand == "set":
            level = parameters["humidifier-level"]
            if level == "1":
                humidifier2_A.set_mist_level_s(1)
            elif level == "2":
                humidifier2_A.set_mist_level_s(2)
            elif level == "3":
                humidifier2_A.set_mist_level_s(3)
            else:
                humidifier2_A.set_mist_level_s(4)
            return 0


def HumidifierProcess(log_q, audio_q, cmd_q, g_state):
    try:
        logger = log.loggerInit(log_q)
    except Exception as e:
        print("Create logger failed")
        exit()

    try:
        logger.log(logging.INFO, "Humidifier Process is started")
        
        mqttc.connect()
        logger.log(logging.INFO, "Wait some seconds to connect to MQTT server")
        time.sleep(1)

        mqttc.loop_start()
        humidifier2_A.dev_subscribe()
        
        humidifier2_A.dev_send_command(getsetting_command)
        logger.log(logging.INFO, "Continue")

    except Exception as e:
        logger.log(logging.ERROR, "Failed to run Humidifier Process: exception={})".format(e))

    while True:
        time.sleep(0.25)
        command = None
        try:
            command = cmd_q.get()
        except Exception as a:
            pass
        try:
            if command == None:
                continue
            logger.log(logging.DEBUG, "Command received: " + command)
            logger.log(logging.DEBUG, "Desination: " + str(json_utils.jsonSimpleParser(command, "des")))
            if str(json_utils.jsonSimpleParser(command, "des")) == "humidifier":
                parameters = json_utils.jsonSimpleParser(command, "parameters")
                actionStr = str(json_utils.jsonSimpleParser(command, "action"))
                logger.log(logging.DEBUG, "Action: " + actionStr)
                actionWords = actionStr.split('.')

                subCommand = actionWords[2]
                logger.log(logging.DEBUG, "Sub Command: " + subCommand)
                typeCommand = None
                if len(actionWords) >= 4:
                    typeCommand = actionWords[3]
                    logger.log(logging.DEBUG, "Type Command: " + typeCommand)
                
                processCommand(logger, audio_q, subCommand, typeCommand, parameters)
            else:
                logger.log(logging.DEBUG, "The des is wrong")
                cmd_q.put(command)
                time.sleep(2)
        except Exception as a:
            logger.log(logging.ERROR, "Failed to run Humidifier Process: exception={})".format(e))
            continue

        
    
