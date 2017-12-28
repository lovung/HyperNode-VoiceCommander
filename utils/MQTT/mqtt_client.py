import os.path
import sys
import paho.mqtt.client as mqtt
import ssl
import logging

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/logger"))
    import logger as log
except ImportError:
    exit()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    if rc == 0:
        is_connected = True

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Received: ")
    print(msg.topic+" "+str(msg.payload.decode('utf-8')))

def on_publish(client, userdata, mid):
    print("Published: " + mid)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.") 

def publish_message(topic, message, qos=1):
    client.publish(topic, payload=message, qos=qos, retain=False)

class hyperMQTTClient(object):
    def __init__(self, connect_cb = on_connect, 
                 message_cb = on_message, 
                 publish_cb = on_publish,
                 disconnect_cb = on_disconnect):
        try:
            self.client = mqtt.Client()
            self.client.on_connect = connect_cb
            self.client.on_message = message_cb
            self.client.on_publish = publish_cb
            self.client.on_disconnect = disconnect_cb
            self.subscribe_list = []
            self.broadcastTopic = []
            self.is_connected = 0
            print("Created MQTT client")
        except Exception as e:
            logger.log(logging.ERROR, "Can not init MQTT client!")

    def connect(self, host="mqtt-iot.hubble.in",
                port=1883,
                kal_interval = 20):
        try:
            # self.host = host
            # self.port = port
            # self.kal_interval = kal_interval
            self.client.connect(host, port, kal_interval)
        except Exception as e:
            print("Can not connect to MQTT server!")

    def subscribe(self, topic, qos = 1):
        try:
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            # client.subscribe("$SYS/#")
            # client.subscribe(airPurifier_pub_topic, qos=1)
            # client.subscribe(mbp162_pub_topic, qos=1)
            self.client.subscribe(topic, qos=qos)
            self.subscribe_list.append(topic)
        except Exception as e:
            print("Can not subscribe to MQTT topic!")

    def unsubscribe(self, topic):
        try:
            self.client.unsubscribe(topic)
            self.subscribe_list.remove(topic)
        except Exception as e:
            print("Can not unsubscribe to MQTT topic!")

    def add_broadcast(self, topic):
        try:
            self.broadcastTopic.append(topic)
        except Exception as e:
            print("Can not add topic to broadcast list!")

    def remove_broadcast(self, topic):
        try:
            self.broadcastTopic.remove(topic)
        except ValueError:
            print("Can not remove topic to broadcast list! - ValueError")
        except Exception as e:
            print("Can not remove topic to broadcast list!")

    def publish(self, topic, message):
        try:
            self.client.publish(topic, payload=message)
        except Exception as e:
            print("Can not publish!")

    def broadcast(self, message):
        try:
            for topic in self.broadcastTopic:
                self.client.publish(topic, payload=message)
        except Exception as e:
            print("Can not broadcast!")

    def loop_forever(self):
        try:
            # Blocking call that processes network traffic, dispatches callbacks and
            # handles reconnecting.
            # Other loop*() functions are available that give a threaded interface and a
            # manual interface.
            self.client.loop_forever()
        except Exception as e:
            print("Can not loop forever!")

    def loop_start(self):
        try:
            self.client.loop_start()
        except Exception as e:
            print("Can not loop start!")
# class hyperMQTTClient_TSL(object):
#     def __init__(self, log_q):
#         try:
#             self.logger = log.loggerInit(log_q)
#         except Exception as e:
#             raise e
#         try:
#             self.client = mqtt.Client()
#             self.client.on_connect = on_connect
#             self.client.on_message = on_message
#             self.client.on_publish = on_publish
#             self.client.on_disconnect = on_disconnect
#             self.subscribe_list = []
#             self.broadcastTopic = []
#             self.logger.log(logging.INFO, "Created MQTT client")
#         except Exception as e:
#             logger.log(logging.ERROR, "Can not init MQTT client!")

#     def connect(self, host="mqtt-iot.hubble.in",
#                 port=1883,
#                 kal_interval = 20):
#         try:
#             self.client.connect(host, port, kal_interval)
#         except Exception as e:
#             self.logger.log(logging.ERROR, "Can not connect to MQTT server!")

#     def subscribe(self, topic, qos = 1):
#         try:
#             # Subscribing in on_connect() means that if we lose the connection and
#             # reconnect then subscriptions will be renewed.
#             # client.subscribe("$SYS/#")
#             # client.subscribe(airPurifier_pub_topic, qos=1)
#             # client.subscribe(mbp162_pub_topic, qos=1)
#             self.client.subscribe(topic, qos=qos)
#             self.subscribe_list.append(topic)
#         except Exception as e:
#             self.logger.log(logging.ERROR, "Can not subscribe to MQTT topic!")

#     def unsubscribe(self, topic):
#         try:
#             self.client.unsubscribe(topic)
#             self.subscribe_list.remove(topic)
#         except Exception as e:
#             self.logger.log(logging.ERROR, "Can not unsubscribe to MQTT topic!")

#     def add_broadcast(self, topic):
#         try:
#             self.broadcastTopic.append(topic)
#         except Exception as e:
#             self.logger.log(logging.ERROR, "Can not add topic to broadcast list!")

#     def remove_broadcast(self, topic):
#         try:
#             self.broadcastTopic.remove(topic)
#         except ValueError:
#             self.logger.log(logging.ERROR, "Can not remove topic to broadcast list! - ValueError")
#         except Exception as e:
#             self.logger.log(logging.ERROR, "Can not remove topic to broadcast list!")

#     def publish(self, topic, message):
#         try:
#             self.client.publish(topic, payload=message)
#         except Exception as e:
#             self.logger.log(logging.ERROR, "Can not publish!")

#     def broadcast(self, message):
#         try:
#             for topic in self.broadcastTopic:
#                 self.client.publish(topic, payload=message)
#         except Exception as e:
#             self.logger.log(logging.ERROR, "Can not broadcast!")

#     def loop_forever(self):
#         try:
#             # Blocking call that processes network traffic, dispatches callbacks and
#             # handles reconnecting.
#             # Other loop*() functions are available that give a threaded interface and a
#             # manual interface.
#             self.client.loop_forever()
#         except Exception as e:
#             self.logger.log(logging.ERROR, "Can not loop forever!")
