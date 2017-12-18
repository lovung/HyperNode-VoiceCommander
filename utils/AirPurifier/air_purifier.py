# import paho.mqtt.client as mqtt
# import ssl
import os.path
import sys

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/logger"))
    import logger as log
except ImportError:
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/MQTT"))
    import mqtt_client as mqtt
except ImportError:
    exit()

airPurifier_sub_topic = "dev/000AE2345D31MydWBUOg/sub"
airPurifier_pub_topic = "dev/000AE2345D31MydWBUOg/pub"

mbp162_sub_topic = "dev/000AE22F001AfBKgECfn/sub"
mbp162_pub_topic = "dev/000AE22F001AfBKgECfn/pub"

hyper_sub_topic = "hyper/xxxxxxxxxxxx/sub"
# hyper_pub_topic = "hyper/xxxxxxxxxxxx/pub"

def AirPurifierProcess(log_q, audio_q, cmd_q):
    logger = log.loggerInit(log_q)
    print("AirPurifier Process is started")
    logger.log(logging.INFO, "AirPurifier Process is started")

    mqttc = mqtt.hyperMQTTClient()
    mqttc.connect()
    mqttc.subcribe(mbp162_pub_topic)
    mqttc.subcribe(hyper_sub_topic)
    mqttc.add_broadcast(mbp162_sub_topic)
    getsetting_message = "2app_topic_sub="+hyper_sub_topic+"&time=1513618350814&action=command&cofmmand=get_projector_setting"
    mqttc.publish(mbp162_sub_topic, message)
    mqttc.loop_forever()