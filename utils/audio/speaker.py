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
    exitProgram()

AGENT_NAME = "Hyper"


def audioProcess(log_q, audio_q):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "audioProcess is started")
    
    while True:
        time.sleep(1)
        try:
            jsonStr = audio_q.get_nowait()
            logger.log(logging.DEBUG, "JSON: "+ jsonStr)
            jsonStr = json.loads(jsonStr)
        
            if jsonStr["speech"]:
                logger.log(logging.INFO, AGENT_NAME + ":" + jsonStr["speech"])
                tts = gTTS(text=jsonStr["speech"], lang='en')
                tts.save("speech.mp3")
                os.system("mpg321 speech.mp3")
        except Exception as e:
            print('.', end='', flush=True)
            pass