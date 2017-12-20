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

mbp162_sub_topic = "dev/000AE22F0021PJPVcjxA/sub"
mbp162_pub_topic = "dev/000AE22F0021PJPVcjxA/pub"

hyper_sub_topic = "hyper/xxxxxxxxxxxx/sub"
# hyper_pub_topic = "hyper/xxxxxxxxxxxx/pub"
is_connected = False

def mqttc_on_connect_cb(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        is_connected = True

def AirPurifierProcess(log_q, audio_q, cmd_q):
    try:
        logger = log.loggerInit(log_q)
    except Exception as e:
        print("Create logger failed")
        exit()

    try:
        logger.log(logging.INFO, "AirPurifier Process is started")

        mqttc = mqtt.hyperMQTTClient(log_q, connect_cb = mqttc_on_connect_cb)
        logger.log(logging.INFO, "Wait some seconds to connect to MQTT server")
        mqttc.connect()
        time.sleep(1)

        # while(is_connected != True):
        #     continue

        logger.log(logging.INFO, "Connect success!")
        mqttc.subscribe(mbp162_pub_topic)
        mqttc.subscribe(mbp162_sub_topic)
        mqttc.subscribe(hyper_sub_topic)
        current_time_epoch = int(time.time())
        # mqttc.add_broadcast(mbp162_sub_topic)
        getsetting_message = "2app_topic_sub="+hyper_sub_topic+"&time="+str(current_time_epoch)+"&action=command&command=get_projector_setting"
        mqttc.publish(mbp162_sub_topic, getsetting_message)
        
        mqttc.loop_forever()
        logger.log(logging.INFO, "Continue")
    except Exception as e:
        logger.log(logging.ERROR, "Failed to create custom metric: exception={})".format(e))
        raise e
    