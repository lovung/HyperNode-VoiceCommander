#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue
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
detector = sb.HotwordDetector(model, sensitivity=0.5)
state = "Sleep";
OMEGA2P_MAC_ADDRESS = "40A36BC02DAF"
HOST_MAC_ADDRESS = wifi_utils.getMACString()

ALL_TASKS = ['lightManager','musicManager','timeManager']

# speech_to_text = SpeechToTextV1(
#     username='bdc32f14-9895-419b-8ad2-dd6030248aad',
#     password='16GMSUKRDSfP',
#     x_watson_learning_opt_out=False
# )

# print(json.dumps(speech_to_text.models(), indent=2))

# print(json.dumps(speech_to_text.get_model('en-US_BroadbandModel'), indent=2))


def exitProgram():
    signal_handler()
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

def voice2JSON():
    # Use Google API stream mic:
    transcript = speech2Text()
    apiaiResponse = apiaiPGetResponse(transcript)
    # print(apiaiResponse.decode('utf-8'))
    apiaiResponse = json.loads(apiaiResponse.decode('utf-8'))
    if apiaiResponse["result"]:
        parsedAction = apiaiResponse["result"]["action"]
        # print(parsedAction)
        parsedActionImcomplete = apiaiResponse["result"]["actionIncomplete"]
        parsedScore = apiaiResponse["result"]["score"]
        parsedParameters = apiaiResponse["result"]["parameters"]
        parsedSpeechScript = apiaiResponse["result"]["fulfillment"]["speech"]
        parsedSpeechScript2 = apiaiResponse["result"]["fulfillment"]["messages"][0]["speech"]
        return parsedAction, parsedActionImcomplete, parsedScore, parsedParameters, parsedSpeechScript, parsedSpeechScript2
    else:
        print("Null api results")
        return -1, -1, -1, -1, -1, -1

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
def jsonSimpleGenerate(key, value):
    data = {}
    data[key] = value
    jsonData = json.dumps(data)
    return jsonData

def testQueue(AudioQueue):
    print("Put script to AudioQueue")
    AudioQueue.put(jsonSimpleGenerate("speech", "Hello"))

def voiceProcess(ManagerJSONQueue, AudioQueue):
    try:        
        print("voiceProcess is started")
        while True:
            global state
            if state == "Sleep":
                state = "Pause"
                hotWordDetect()
            elif state == "Run":
                [action, actionIncomplete, score, parameters, speechScript, speechScript2] = voice2JSON()
                print("Action: ", action)
                print("actionIncomplete: ", actionIncomplete)
                print("score: ", score)
                print("parameters: ", parameters)
                print("speechScript: ", speechScript)
                print("speechScript2: ", speechScript2)
                if (action == -1 or action == "smalltalk.greetings.bye"):
                    AudioQueue.put(jsonSimpleGenerate("speech", speechScript))
                    state = "Sleep"
                    continue
                if (score < 0.5 or actionIncomplete == 'true' or not(speechScript)):
                    try:
                        AudioQueue.put(jsonSimpleGenerate("speech", "I am not sure to understand what you mean. Can you repeat or explain more?"))
                        # ManagerJSONQueue.put_nowait(jsonSimpleGenerate("action", action))
                        continue
                    except Exception as e:
                        state = "Sleep"
                        continue
                else:
                    try:
                        # ManagerJSONQueue.put(jsonSimpleGenerate("action", action))
                        if not AudioQueue.full():
                            if (speechScript and speechScript != -1):
                                # print("Put script to AudioQueue")
                                AudioQueue.put_nowait(jsonSimpleGenerate("speech", speechScript))
                            if (speechScript2 and speechScript2 != -1 and speechScript != speechScript2):
                                time.sleep(1)
                                # print("Put script to AudioQueue")
                                AudioQueue.put_nowait(jsonSimpleGenerate("speech", speechScript2))
                        else:
                            state = "Sleep"
                            continue    
                    except Exception as e:
                        state = "Sleep"
                        continue
            elif state == "Pause":
                time.sleep(1)
    except Exception as e:
        print(type(e))

def audioProcess(AudioQueue):
    global state
    print("audioProcess is started")
    while True:
        time.sleep(1)
        try:
            jsonStr = AudioQueue.get(True,1)
            print("JSON: ", jsonStr)
            jsonStr = json.loads(jsonStr)
        
            if jsonStr["speech"]:
                state = "Pause"
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
    try:
        print("AMQPProcess is started")
        # Connect for sending:
        AMQPClient = amqp.hyperAMQPClient()
        # AMQPSendTopic_lightManager = AMQPClient.topicGenerator(HOST_MAC_ADDRESS, "0001", "lightManager", "sub")
        print(AMQPSendTopic_lightManager)
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

    except Exception as e:
        print(type(e))

def main(): 
    # Init queue for sending and receiving:
    # AMQPSendQueue = Queue()
    # AMQPRcvQueue = Queue()
    ManagerJSONQueue = Queue(50)
    AudioQueue = Queue(50)
    # process1 = Process(target=AMQPProcess, args=(AMQPSendQueue, AMQPRcvQueue, ManagerJSONQueue, ))
    # process1.start()

    # processTest = Process(target=testQueue, args=(AudioQueue, ))
    # processTest.start()
    
    process2 = Process(target=voiceProcess, args=(ManagerJSONQueue, AudioQueue, ))
    process2.start()
    

    process4 = Process(target=audioProcess, args=(AudioQueue, ))
    process4.start()


    process2.join()
    process4.join()


    
    # process3 = Process(target=managerProcess, args=(ManagerJSONQueue, ))
    # process3.start()

    time.sleep(10)
    print("main put")
    AudioQueue.put(jsonSimpleGenerate("speech", "Hello"))
    print("main put success")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        exitProgram()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(type(e))
    
    
        
