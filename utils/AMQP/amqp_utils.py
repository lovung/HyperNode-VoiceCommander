import logging
import json

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "network"))
    import wifi_utils
except ImportError:
    exit()

try:
    import amqp_client as amqp
except ImportError:
    exit()

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "logger"))
    import logger as log
except ImportError:
    exitProgram()

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "audio"))
    import microphone
    import speaker
except ImportError:
    exitProgram()

OMEGA2P_MAC_ADDRESS = "40a36bc02daf"
HOST_MAC_ADDRESS = wifi_utils.getMACString()
ALL_TASKS = ['lightManager','musicManager','timeManager','answerCenter']

def AMQPReceiveMessageCallback(ch, method, properties, body):
    print("Receive: %s" % body.decode('utf-8'))

def AMQPProcess(sendQueue, rcvQueue):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "AMQPProcess is started")
    # Connect for sending:
    AMQPClient = amqp.hyperAMQPClient()
    # AMQPSendTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", "lightManager", "sub")
    logger.log(logging.DEBUG, AMQPSendTopic_lightManager)
    AMQPClient.declareTopic(AMQPSendTopic_lightManager)

    # For receiving:
    AMQPRcvTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", "lightManager", "pub")
    AMQPClient.declareTopic(AMQPRcvTopic_lightManager)
    # AMQPClient.publishMessage(AMQPTopic, "Hello Hyper")
    AMQPClient.startSubcribe(AMQPReceiveMessageCallback, AMQPRcvTopic_lightManager)

    while True:
        try:
            jsonStr = sendQueue.get_nowait()
            jsonStr = json.loads(jsonStr)

            AMQPClient.publishMessage(routing_key=AMQPSendTopic_lightManager)
        except Exception as e:
            pass