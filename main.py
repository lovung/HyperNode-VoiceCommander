#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import byteorder
from array import array
from struct import pack
from os.path import join, dirname
# from watson_developer_cloud import SpeechToTextV1
from transcribe_streaming_mic import speech2Text
# import snowboy/examples/Python3/snowboydecoder
import signal
import json
import pyaudio
import wave
import os.path
import sys
from gtts import gTTS
import os
import time

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

try:
    import snowboydecoder
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "snowboy/examples/Python3"))
    import snowboydecoder

try:
    import amqp_client
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "utils"))
    import amqp_client as amqp

CLIENT_ACCESS_TOKEN = '587dba5ac7de45b3a05b7901a04f5b2e'

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
interrupted = False
model = os.path.join(TOP_DIR, "models/Hyper.pmdl")
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.4)
state = "Sleep";

# speech_to_text = SpeechToTextV1(
#     username='bdc32f14-9895-419b-8ad2-dd6030248aad',
#     password='16GMSUKRDSfP',
#     x_watson_learning_opt_out=False
# )

# print(json.dumps(speech_to_text.models(), indent=2))

# print(json.dumps(speech_to_text.get_model('en-US_BroadbandModel'), indent=2))


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

    # Use Watson API.

    # with open(join(dirname(__file__), 'demo.wav'),
    #           'rb') as audio_file:
    #     json_data = json.dumps(speech_to_text.recognize(
    #         audio_file, content_type='audio/wav', timestamps=True,
    #         word_confidence=True),
    #         indent=2)
    #     json_data = json.loads(json_data)
    #     if json_data["results"]:
    #         transcript = json_data["results"][0][
    #             "alternatives"][0]["transcript"]
    #         print("Transcript")
    #         print(transcript)
    #         apiaiResponse = apiaiPGetResponse(transcript)
    #         print(apiaiResponse)
    #         apiaiResponse = json.loads(apiaiResponse)
    #         if apiaiResponse["result"]:
    #             print(apiaiResponse["result"]["action"])
    #             print(apiaiResponse["result"]["fulfillment"]["speech"])
    #             print(apiaiResponse["result"]["fulfillment"][
    #                   "messages"][0]["speech"])
    #         else:
    #             print("Null api results")
    #     else:
    #         print("Null watson results")
def hotWordCallback():
    snowboydecoder.play_audio_file()
    print("Terminate hotWordDetect")
    detector.terminate()
    time.sleep(0.3)
    global state
    state = "Run"

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

def hotWordDetect(modelPath=model):
    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    print('Listening... Press Ctrl+C to exit')

    # main loop
    detector.start(detected_callback=hotWordCallback,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)    

def main():
    AMQPClient = amqp.hyperAMQPClient()
    AMQPTopic = AMQPClient.topicGenerator("000AE22F0031", "0001", "lightManager", "sub")
    AMQPClient.declareTopic(AMQPTopic)
    AMQPClient.publishMessage(AMQPTopic, "Hello Hyper")
    while 1:
        global state
        if state == "Sleep":
            hotWordDetect()
        else:
            while 1:
                parsedAction = voice2JSONProcess()
                if (parsedAction == -1):
                    break
                if (parsedAction == "smalltalk.greetings.bye"):
                    break
                # else:
                    # assignAction(parsedAction)
            state = "Sleep"

if __name__ == '__main__':
    main()
    
        