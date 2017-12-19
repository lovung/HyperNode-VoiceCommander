import sys
from os.path import join, dirname
from transcribe_streaming_mic import speech2Text
import pyaudio
import time
import json 
import os.path
import logging

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
try:
    import apiai
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    import apiai

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/logger"))
    import logger as log
except ImportError:
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "snowboy/examples/Python3"))
    import snowboydecoder as sb
except ImportError:
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/JSON"))
    import json_utils
except ImportError:
    exit()

state = "Sleep"
model = os.path.join(TOP_DIR, "models/Hyper.pmdl")
detector = sb.HotwordDetector(model, sensitivity=0.5)
interrupted = False
CLIENT_ACCESS_TOKEN = '587dba5ac7de45b3a05b7901a04f5b2e'

# Hot word detection callback (which will be run whenever user say the hot word)
def hotWordCallback():
    sb.play_audio_file()
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


def voiceProcess(log_q, action_q, aud_q, cmd_q):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "voiceProcess is started")
    while True:
        global state
        if state == "Sleep":
            state = "Pause"
            hotWordDetect()
        elif state == "Run":
            logger.log(logging.INFO, "Voice is detected")
            [action, actionIncomplete, score, parameters, speechScript, speechScript2] = voice2JSON()
            logger.log(logging.INFO, "Action: " + action)
            logger.log(logging.DEBUG, "actionIncomplete: " + str(actionIncomplete))
            logger.log(logging.DEBUG, "score: " + str(score))
            logger.log(logging.DEBUG, "parameters: " + str(parameters))
            logger.log(logging.DEBUG, "speechScript: " + speechScript)
            logger.log(logging.DEBUG, "speechScript2: " + speechScript2)
            if (action == -1 or action == "smalltalk.greetings.bye"):
                aud_q.put(json_utils.jsonSimpleGenerate("speech", speechScript))
                state = "Sleep"
                continue
            if (score < 0.5 or actionIncomplete == 'true' or not(speechScript)):
                try:
                    aud_q.put_nowait(json_utils.jsonSimpleGenerate("speech", "I am not sure to understand what you mean. Can you repeat or explain more?"))
                    # mng_q.put_nowait(jsonSimpleGenerate("action", action))
                    continue
                except Exception as e:
                    logger.log(logging.WARNING, "Action is not complete or score is low")
                    state = "Sleep"
                    continue
            else:
                try:
                    # ManagerJSONQueue.put(jsonSimpleGenerate("action", action))
                    if not aud_q.full():
                        if (speechScript and speechScript != -1):
                            logger.log(logging.DEBUG, "Put script to AudioQueue")
                            aud_q.put_nowait(json_utils.jsonSimpleGenerate("speech", speechScript))
                        if (speechScript2 and speechScript2 != -1 and speechScript != speechScript2):
                            time.sleep(1)
                            logger.log(logging.DEBUG, "Put script to AudioQueue")
                            aud_q.put_nowait(json_utils.jsonSimpleGenerate("speech", speechScript2))
                    else:
                        logger.log(logging.WARNING, "Audio queue is full")
                        state = "Sleep"
                        continue    
                except Exception as e:
                    logger.log(logging.WARNING, str(type(e)))
                    state = "Sleep"
                    continue
        elif state == "Pause":
            time.sleep(1)
