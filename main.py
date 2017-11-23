#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing as MTP
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

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
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
detector = sb.HotwordDetector(model, sensitivity=0.6)
state = "Sleep";
OMEGA2P_MAC_ADDRESS = "40A36BC02DAF"
HOST_MAC_ADDRESS = wifi_utils.getMACString()

# speech_to_text = SpeechToTextV1(
#     username='bdc32f14-9895-419b-8ad2-dd6030248aad',
#     password='16GMSUKRDSfP',
#     x_watson_learning_opt_out=False
# )

# print(json.dumps(speech_to_text.models(), indent=2))

# print(json.dumps(speech_to_text.get_model('en-US_BroadbandModel'), indent=2))


def exitProgram():
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    exit()

def apiaiPGetResponse(transcript):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = "vulong"
    request.query = transcript
    response = request.getresponse()

    return response.read()

def voice2JSONProcess():
    # Use Google API stream mic:
    transcript = speech2Text()
    apiaiResponse = apiaiPGetResponse(transcript)
    print(apiaiResponse.decode('utf-8'))
    apiaiResponse = json.loads(apiaiResponse.decode('utf-8'))
    if apiaiResponse["result"]:
        parsedAction = apiaiResponse["result"]["action"]
        print(parsedAction)
        speechScript = apiaiResponse["result"]["fulfillment"]["speech"]
        if speechScript:
            print(speechScript)
            tts = gTTS(text=speechScript, lang='en')
            tts.save("speech.mp3")
            os.system("mpg321 speech.mp3")
        speechScript2 = apiaiResponse["result"]["fulfillment"]["messages"][0]["speech"]
        if (speechScript != speechScript2) and speechScript2:
            tts = gTTS(text=speechScript2, lang='en')
            tts.save("speech.mp3")
            os.system("mpg321 speech.mp3")
            print(speechScript)
        return parsedAction
    else:
        print("Null api results")
        return -1

def hotWordCallback():
    sb.play_audio_file()
    print("Terminate hotWordDetect")
    detector.terminate()
    time.sleep(0.3)
    global state
    state = "Run"

def signal_handler():
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

def hotWordDetect(modelPath=model):
    # capture SIGINT signal, e.g., Ctrl+C
    # signal.signal(signal.SIGINT, signal_handler)
        
    print('Listening... Press Ctrl+C to exit')
    # main loop
    detector.start(detected_callback=hotWordCallback,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)
def voiceProcess():
    try:        
        while True:
            global state
            if state == "Sleep":
                state = "Pause"
                hotWordDetect()
            elif state == "Run":
                while True:
                    parsedAction = voice2JSONProcess()
                    if (parsedAction == -1):
                        break
                    if (parsedAction == "smalltalk.greetings.bye"):
                        break
                    # else:
                        # assignAction(parsedAction)
                state = "Sleep"
            elif state == "Pause":
                time.sleep(1)
    except Exception as e:
        print(type(e))

def AMQPReceiveMessageCallback(ch, method, properties, body):


def AMQPProcess(sendQueue, rcvQueue):
    try:
        # Connect for sending:
        AMQPClient = amqp.hyperAMQPClient()
        AMQPSendTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", "lightManager", "sub")
        print(AMQPSendTopic_lightManager)
        AMQPClient.declareTopic(AMQPSendTopic_lightManager)

        # For receiving:
        AMQPRcvTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", "lightManager", "pub")
        AMQPClient.declareTopic(AMQPRcvTopic_lightManager)
        # AMQPClient.publishMessage(AMQPTopic, "Hello Hyper")
        AMQPClient.startSubcribe(AMQPReceiveMessageCallback, AMQPRcvTopic_lightManager)

    except Exception as e:
        print(type(e))

def main():
    try:        
        # Init queue for sending and receiving:
        AMQPSendQueue = MTP.Queue()
        AMQPRcvQueue = MTP.Queue()
        process1 = MTP.Process(target=AMQPProcess, args=(AMQPSendQueue, AMQPRcvQueue, ))
        process1.start()

    except Exception as e:
        print(type(e))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        signal_handler()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
        exit()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(type(e))
    
    
        