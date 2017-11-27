#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
from multiprocessing import Process, Queue
import logging
import logging.handlers
from sys import byteorder
from array import array
from struct import pack
from os.path import join, dirname
# from watson_developer_cloud import SpeechToTextV1
from transcribe_streaming_mic import speech2Text
# import snowboy/examples/Python3/snowboydecoder
# import signal
import json
import pyaudio
import wave
import os.path
import sys
from gtts import gTTS
import os
import time
import traceback

def exitProgram():
    signal_handler()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    exit()

try:
    import apiai
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    import apiai

try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "snowboy/examples/Python3"))
    import snowboydecoder as sb
except ImportError:
    exitProgram()

try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "utils/AMQP"))
    import amqp_client as amqp
except ImportError:
    exitProgram()

try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "utils/network"))
    import wifi_utils
except ImportError:
    exitProgram()

CLIENT_ACCESS_TOKEN = '587dba5ac7de45b3a05b7901a04f5b2e'

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
interrupted = False
model = os.path.join(TOP_DIR, "models/Hyper.pmdl")
detector = sb.HotwordDetector(model, sensitivity=0.5)
state = "Sleep";
OMEGA2P_MAC_ADDRESS = "40a36bc02daf"
HOST_MAC_ADDRESS = wifi_utils.getMACString()
AGENT_NAME = "Hyper"


ALL_TASKS = ['lightManager','musicManager','timeManager','answerCenter']


def loggingConfigurer():
    root = logging.getLogger()
    h = logging.handlers.RotatingFileHandler('testLogging.log', 'a', 10*1024*1024, 10)
    f = logging.Formatter('%(asctime)s %(name)-15s %(levelname)-8s %(message)s')
    h.setFormatter(f)
    root.addHandler(h)

def loggerInit(queue):
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    root.addHandler(h)
    root.setLevel(logging.INFO)
    processName = multiprocessing.current_process().name
    logger = logging.getLogger(processName)
    return logger

def loggingProcess(queue, configurer):
    configurer()
    while True:
        try:
            record = queue.get()
            if record is None:  # We send this as a sentinel to tell the listener to quit.
                break
            logger = logging.getLogger(record.name)
            logger.handle(record)  # No level or filter logic applied - just do it!
        except Exception:
            import sys, traceback
            print('Whoops! Problem:', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


# apiai for Natural language understanding
def apiaiPGetResponse(transcript):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = "vulong"
    request.query = transcript
    response = request.getresponse()

    return response.read()

# cover 2 process: call speech to text and call NLU module
def voice2JSON():
    # Use Google API stream mic:
    transcript = speech2Text()
    apiaiResponse = apiaiPGetResponse(transcript)
    # print(apiaiResponse.decode('utf-8'))
    apiaiResponse = json.loads(apiaiResponse.decode('utf-8'))
    if apiaiResponse["result"]:
        parsedAction = apiaiResponse["result"]["action"]
        parsedActionImcomplete = apiaiResponse["result"]["actionIncomplete"]
        parsedScore = apiaiResponse["result"]["score"]
        parsedParameters = apiaiResponse["result"]["parameters"]
        parsedSpeechScript = apiaiResponse["result"]["fulfillment"]["speech"]
        parsedSpeechScript2 = apiaiResponse["result"]["fulfillment"]["messages"][0]["speech"]
        return parsedAction, parsedActionImcomplete, parsedScore, parsedParameters, parsedSpeechScript, parsedSpeechScript2
    else:
        print("Null api results")
        return -1, -1, -1, -1, -1, -1

# Hot word detection callback (which will be run whenever user say the hot word)
def hotWordCallback():
    sb.play_audio_file()
    print("Terminate hotWordDetect")
    detector.terminate()
    time.sleep(0.3)
    global state
    state = "Run"

# interrupt the hotword process loop
def signal_handler():
    global interrupted
    interrupted = True

# call back to check for interrupt
def interrupt_callback():
    global interrupted
    return interrupted

# hot word detection: main function
def hotWordDetect(modelPath=model):
    # capture SIGINT signal, e.g., Ctrl+C
    # signal.signal(signal.SIGINT, signal_handler)
        
    print('Listening... Press Ctrl+C to exit')
    # main loop
    detector.start(detected_callback=hotWordCallback,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)
# the simple funtion to generate the JSON
def jsonSimpleGenerate(key, value):
    data = {}
    data[key] = value
    jsonData = json.dumps(data)
    return jsonData

def testQueue(AudioQueue):
    print("Put script to AudioQueue")
    AudioQueue.put(jsonSimpleGenerate("speech", "Hello"))

def voiceProcess(log_q, mng_q, aud_q):
    logger = loggerInit(log_q)
    logger.log(logging.INFO, "voiceProcess is started")
    while True:
        global state
        if state == "Sleep":
            state = "Pause"
            hotWordDetect()
        elif state == "Run":
            [action, actionIncomplete, score, parameters, speechScript, speechScript2] = voice2JSON()
            logger.log(logging.INFO, "Action: " + action)
            logger.log(logging.DEBUG, "actionIncomplete: " + actionIncomplete)
            logger.log(logging.DEBUG, "score: " + score)
            logger.log(logging.DEBUG, "parameters: " + parameters)
            logger.log(logging.DEBUG, "speechScript: " + speechScript)
            logger.log(logging.DEBUG, "speechScript2: " + speechScript2)
            if (action == -1 or action == "smalltalk.greetings.bye"):
                aud_q.put(jsonSimpleGenerate("speech", speechScript))
                state = "Sleep"
                continue
            if (score < 0.5 or actionIncomplete == 'true' or not(speechScript)):
                try:
                    aud_q.put_nowait(jsonSimpleGenerate("speech", "I am not sure to understand what you mean. Can you repeat or explain more?"))
                    # mng_q.put_nowait(jsonSimpleGenerate("action", action))
                    continue
                except Exception as e:
                    state = "Sleep"
                    continue
            else:
                try:
                    # ManagerJSONQueue.put(jsonSimpleGenerate("action", action))
                    if not aud_q.full():
                        if (speechScript and speechScript != -1):
                            logger.log(logging.DEBUG, "Put script to AudioQueue")
                            aud_q.put_nowait(jsonSimpleGenerate("speech", speechScript))
                        if (speechScript2 and speechScript2 != -1 and speechScript != speechScript2):
                            time.sleep(1)
                            logger.log(logging.DEBUG, "Put script to AudioQueue")
                            aud_q.put_nowait(jsonSimpleGenerate("speech", speechScript2))
                    else:
                        state = "Sleep"
                        continue    
                except Exception as e:
                    state = "Sleep"
                    continue
        elif state == "Pause":
            time.sleep(1)

def audioProcess(log_q, audio_q):
    global state
    logger = loggerInit(log_q)
    logger.log(logging.INFO, "audioProcess is started")
    
    while True:
        time.sleep(1)
        try:
            jsonStr = audio_q.get(True,1)
            logger.log(logging.DEBUG, "JSON: "+ jsonStr)
            jsonStr = json.loads(jsonStr)
        
            if jsonStr["speech"]:
                state = "Pause"
                logger.log(logging.INFO, AGENT_NAME + ":" + jsonStr["speech"])
                tts = gTTS(text=jsonStr["speech"], lang='en')
                tts.save("speech.mp3")
                os.system("mpg321 speech.mp3")
                state = "Run"
        except Exception as e:
            # print('.', end='', flush=True)
            pass


def AMQPReceiveMessageCallback(ch, method, properties, body):
    print("Receive: %s" % body.decode('utf-8'))

def AMQPProcess(sendQueue, rcvQueue):
    logger = loggerInit(log_q)
    logger.log(logging.INFO, "AMQPProcess is started")
    # Connect for sending:
    AMQPClient = amqp.hyperAMQPClient()
    # AMQPSendTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", "lightManager", "sub")
    logger.log(logging.DEBUG, AMQPSendTopic_lightManager)
    AMQPClient.declareTopic(AMQPSendTopic_lightManager)

    # For receiving:
    AMQPRcvTopic_lightManager = AMQPClient.topicGeneratro(HOST_MAC_ADDRESS, "0001", "lightManager", "pub")
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

def main(): 
    # Init queue for sending and receiving:
    LoggingQueue = Queue(1024)
    # AMQPSendQueue = Queue()
    # AMQPRcvQueue = Queue()
    ManagerJSONQueue = Queue(50)
    AudioQueue = Queue(50)


    # process1 = Process(target=AMQPProcess, args=(AMQPSendQueue, AMQPRcvQueue, ManagerJSONQueue, ))
    # process1.start()

    # processTest = Process(target=testQueue, args=(AudioQueue, ))
    # processTest.start()
    logging_p = Process(target=loggingProcess, args=(LoggingQueue, loggingConfigurer, ))
    logging_p.start()

    voice_p = Process(target=voiceProcess, args=(LoggingQueue, ManagerJSONQueue, AudioQueue, ))
    voice_p.start()
    

    audio_p = Process(target=audioProcess, args=(LoggingQueue, AudioQueue, ))
    audio_p.start()

    voice_p.join()
    audio_p.join()

    # process3 = Process(target=managerProcess, args=(ManagerJSONQueue, ))
    # process3.start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.log(logging.DEBUG, 'Interrupted')
        exitProgram()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(type(e))
    
    
        
