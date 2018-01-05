import sys
from os.path import join, dirname
from gtts import gTTS
import logging
import json
import time
import os.path

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/logger"))
    import logger as log
except ImportError:
    print("File: " + __file__ + " - Import log failed")
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/JSON"))
    import json_utils
except ImportError:
    print("File: " + __file__ + " - Import JSON failed")
    exitProgram()

AGENT_NAME = "Hyper"


def audioProcess(log_q, audio_q, cmd_q, g_state):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "audioProcess is started")
    
    while True:
        time.sleep(0.25)
        try:
            jsonStr = audio_q.get()
            logger.log(logging.DEBUG, "JSON: "+ jsonStr)

            speech = json_utils.jsonSimpleParser(jsonStr, "speech")
            logger.log(logging.DEBUG, "Speech: "+ speech)
            if speech is -1:
                logger.log(logging.ERROR, "JSON parse failed")
            else:
                if (g_state.get() == 1):
                    logger.log(logging.DEBUG, "Set g_state to 2")
                    g_state.set(2)
                logger.log(logging.INFO, AGENT_NAME + ":" + speech)
                tts = gTTS(text=speech, lang='en')
                tts.save("Resources/speech.mp3")
                os.system("mpg321 Resources/speech.mp3 &")
                if (g_state.get() == 2):
                    logger.log(logging.DEBUG, "Set g_state to 1")
                    g_state.set(1)

        except Exception as e:
            # logger.log(logging.ERROR, "Failed to run audioProcess: exception={})".format(e))
            pass
