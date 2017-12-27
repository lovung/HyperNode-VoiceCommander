# import paho.mqtt.client as mqtt
# import ssl
import os.path
import sys
import logging
import time

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/logger"))
    import logger as log
except ImportError:
    print("Import log failed")
    exit()

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "MQTT"))
    import mqtt_client as mqtt
except ImportError:
    print("Import MQTT failed")
    exit()

# airPurifier_sub_topic = "dev/000AE2345D31MydWBUOg/sub"
# airPurifier_pub_topic = "dev/000AE2345D31MydWBUOg/pub"

# mbp162_sub_topic = "dev/000AE22F0021PJPVcjxA/sub"
# mbp162_pub_topic = "dev/000AE22F0021PJPVcjxA/pub"

humidifier_topic_key = "000AE2390DDEgqDQNJRQ"

hyper_sub_topic = "hyper/xxxxxxxxxxxx/sub"
is_connected = False

class HubbleHumidifierDevice(object):
    def __init__(self, mqttc, topic_key):
        self.mqttc = mqttc
        self.topic_key = topic_key
        self.sub_topic = "dev/"+topic_key+"/sub"
        self.pub_topic = "dev/"+topic_key+"/pub"

    def dev_subcribe(self):
        self.mqttc.subscribe(self.pub_topic)

    def dev_publish(self, message):
        self.mqttc.publish(self.sub_topic, message)

    def dev_send_command(self, command):
        message = "2app_topic_sub="+hyper_sub_topic+"&time="+str(int(time.time()))+"&action=command&command="+command
        self.mqttc.publish(self.sub_topic, message)        


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
    print("Received: ")
    print(msg.topic+" "+str(msg.payload.decode('utf-8')))

def mqttc_on_publish_cb(client, userdata, mid):
    print("Published: " + mid)

mqttc = mqtt.hyperMQTTClient(log_q, connect_cb = mqttc_on_connect_cb)
def HumidifierMQTTProcess(log_q):
    try:
        logger = log.loggerInit(log_q)
    except Exception as e:
        print("Create logger failed")
        exit()

    try:
        logger.log(logging.INFO, "HumidifierMQTT Process is started")
        mqttc.connect()
        logger.log(logging.INFO, "Wait some seconds to connect to MQTT server")
        time.sleep(1)

        mqttc.loop_forever()
    except Exception as e:
        logger.log(logging.ERROR, "Failed to create custom metric: exception={})".format(e))
        raise e    

def HumidifierProcess(log_q, audio_q, cmd_q):
    try:
        logger = log.loggerInit(log_q)
    except Exception as e:
        print("Create logger failed")
        exit()

    try:
        logger.log(logging.INFO, "Humidifier Process is started")

        while(mqttc.is_connected != True):
            continue

        logger.log(logging.INFO, "Connect success!")

        humifier2_A = HubbleHumidifierDevice(mqttc = mqttc, topic_key = humidifier_topic_key)
        humifier2_A.dev_subscribe()
        mqttc.subscribe(hyper_sub_topic)
        
        getsetting_command = "get_projector_setting"
        humifier2_A.dev_publish(getsetting_message)
        
        mqttc.loop_forever()
        logger.log(logging.INFO, "Continue")
    except Exception as e:
        logger.log(logging.ERROR, "Failed to create custom metric: exception={})".format(e))
        raise e
    