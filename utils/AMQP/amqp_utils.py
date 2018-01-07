import sys
import os.path
import logging
import json
from multiprocessing import Value, Lock
import time

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

try:
    import amqp_client as amqp
except ImportError:
    print("File: " + __file__ + " - Import AMQP failed")
    exit()

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "network"))
    import wifi_utils
except ImportError:
    print("File: " + __file__ + " - Import network failed")
    exit()

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "logger"))
    import logger as log
except ImportError:
    print("File: " + __file__ + " - Import logger failed")
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/JSON"))
    import json_utils
except ImportError:
    print("File: " + __file__ + " - Import JSON failed")
    exitProgram()


class LightDevice(object):
    """docstring for LightDevice"""
    def __init__(self, initValue=None):
        super(LightDevice, self).__init__()
        self.val = Value('i', initValue)
        self.lock = Lock()

    def update_value(self, new_value):
        self.val.value = new_value

    def get(self):
        return self.val.value

    def command_set_value(self, value):
        return json_utils.jsonDoubleGenerate(json_utils.jsonSimpleGenerate("command","set"),json_utils.jsonSimpleGenerate("value", value))

OMEGA2P_MAC_ADDRESS = "42A36B002DAF"
HOST_MAC_ADDRESS = wifi_utils.getMACString()
DemoLight = LightDevice(0)

def AMQPReceiveMessageCallback(ch, method, properties, body):
    print("Receive: %s" % body.decode('utf-8'))
    state = js.jsonSimpleParser(body,"state")
    if state == "1":
        DemoLight.update_value(1)
    else:
        DemoLight.update_value(0)

def processCommand(logger, audio_q, subCommand, typeCommand, parameters):
    if subCommand == "check":
        logger.log(logging.INFO, "The light state is " + str(DemoLight.get()))
        speechScript = "The light state is " + str(DemoLight.get()) + " right now"
        audio_q.put(str(json_utils.jsonSimpleGenerate("speech", speechScript)))
        return "0"
    elif "switch":
        if typeCommand == "check":
            logger.log(logging.INFO, "The light state is " + str(DemoLight.get()))
            speechScript = "The light state is " + str(DemoLight.get()) + " right now"
            audio_q.put(str(json_utils.jsonSimpleGenerate("speech", speechScript)))
            return "0"
        elif typeCommand == "on":
            logger.log(logging.INFO, "Turn the light on")
            return DemoLight.command_set_value(1)
        elif typeCommand == "off":
            logger.log(logging.INFO, "Turn the power off")
            return DemoLight.command_set_value(0)

def AMQPLightRcvProcess(log_q):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "AMQP Light Rcv Process is started")

    AMQPClient = amqp.hyperAMQPClient()
    # For receiving:
    AMQPRcvTopic_lightManager = AMQPClient.topicGenerator(OMEGA2P_MAC_ADDRESS, "0001", "lightManager", "pub")
    logger.log(logging.DEBUG, AMQPRcvTopic_lightManager)
    AMQPClient.declareTopic(AMQPRcvTopic_lightManager)
    AMQPClient.startSubcribe(AMQPReceiveMessageCallback, AMQPRcvTopic_lightManager)
    
def AMQPLightProcess(log_q, audio_q, cmd_q):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "AMQP Light Process is started")

    AMQPClient = amqp.hyperAMQPClient()

    AMQPSendTopic_lightManager = AMQPClient.topicGenerator(OMEGA2P_MAC_ADDRESS, "0001", "lightManager", "sub")
    logger.log(logging.DEBUG, AMQPSendTopic_lightManager)
    AMQPClient.declareTopic(AMQPSendTopic_lightManager)
    #AMQPClient.startSubcribe(AMQPReceiveMessageCallback, AMQPSendTopic_lightManager)

    logger.log(logging.DEBUG, "Declare done")
    while True:
        time.sleep(0.05)
        try:
            #logger.log(logging.DEBUG, "Check")
            command = cmd_q.get_nowait()
        except Exception as e:
            continue
        try:
            if command == None:
                continue
            logger.log(logging.DEBUG, "Command received: " + command)
            logger.log(logging.DEBUG, "Desination: " + str(json_utils.jsonSimpleParser(command, "des")))
            if str(json_utils.jsonSimpleParser(command, "des")) == "light":
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
                
                ret = processCommand(logger, audio_q, subCommand, typeCommand, parameters)
                if ret != "0":
                    AMQPClient.publishMessage(AMQPSendTopic_lightManager, ret)

            else:
                logger.log(logging.DEBUG, "The des is wrong")
                cmd_q.put(command)
                time.sleep(2)
        except Exception as e:
            logger.log(logging.ERROR, "Failed to run Light Process: exception={})".format(e))
            continue
