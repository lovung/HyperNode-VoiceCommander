import sys
import os.path
import logging
import json

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "network"))
    import wifi_utils
except ImportError:
    print("File: " + __file__ + " - Import network failed")
    exit()

try:
    import amqp_client as amqp
except ImportError:
    print("File: " + __file__ + " - Import AMQP failed")
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
    def __init__(self, value=None):
        super(LightDevice, self).__init__()
        self.value = value

    def update_value(new_value):
        self.value = new_value

    def get():
        return self.value

    def command_set_value(strValue):
        if value == "on":
            pinValue = "0"
        else:
            pinValue = "1"
        return json_utils.jsonDoubleGenerate(json_utils.jsonSimpleGenerate("command","set"),json_utils.jsonSimpleGenerate("value", pinValue))

OMEGA2P_MAC_ADDRESS = "42A36B002DAF"
HOST_MAC_ADDRESS = wifi_utils.getMACString()
DemoLight = LightDevice("off")

def AMQPReceiveMessageCallback(ch, method, properties, body):
    print("Receive: %s" % body.decode('utf-8'))
    state = js.jsonSimpleParser(body,"state")
    if state == "1":
        DemoLight.update_value("off")
    else:
        DemoLight.update_value("on")

def processCommand(logger, audio_q, subCommand, typeCommand, parameters):
    if subCommand == "check":
        logger.log(logging.INFO, "The humidity is " + str(DemoLight.get()))
        speechScript = "The humidity is " + str(DemoLight.get()) + " right now"
        audio_q.put(str(json_utils.jsonSimpleGenerate("speech", speechScript)))
        return 0
    elif "switch":
        if typeCommand == "check":
            logger.log(logging.INFO, "The humidity is " + str(DemoLight.get()))
            speechScript = "The power status is " + str(DemoLight.get()) + " right now"
            audio_q.put(str(json_utils.jsonSimpleGenerate("speech", speechScript)))
            return 0
        elif typeCommand == "on":
            logger.log(logging.INFO, "Turn the light on")
            DemoLight.command_set_value(typeCommand)
            return 0
        elif typeCommand == "off":
            logger.log(logging.INFO, "Turn the power off")
            DemoLight.command_set_value(typeCommand)
            return 0

def AMQPLightProcess(log_q, send_q, cmd_q):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "AMQPProcess is started")

    # Connect for sending:
    AMQPClient = amqp.hyperAMQPClient()
    AMQPSendTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", "lightManager", "sub")
    logger.log(logging.DEBUG, AMQPSendTopic_lightManager)
    AMQPClient.declareTopic(AMQPSendTopic_lightManager)
    AMQPClient.startSubcribe(AMQPReceiveMessageCallback, AMQPSendTopic_lightManager)

    # For receiving:
    AMQPRcvTopic_lightManager = AMQPClient.topicGenerator(OMEGA2P_MAC_ADDRESS, "0001", "lightManager", "pub")
    logger.log(logging.DEBUG, AMQPRcvTopic_lightManager)
    AMQPClient.declareTopic(AMQPRcvTopic_lightManager)
    AMQPClient.startSubcribe(AMQPReceiveMessageCallback, AMQPRcvTopic_lightManager)

    while True:
        try:
            command = cmd_q.get()
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
                
                processCommand(logger, audio_q, subCommand, typeCommand, parameters)
            else:
                logger.log(logging.DEBUG, "The des is wrong")
                cmd_q.put(command)
                time.sleep(2)
        except Exception as e:
            logger.log(logging.ERROR, "Failed to run Humidifier Process: exception={})".format(e))
