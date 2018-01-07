import sys, os
from os.path import join, dirname
import pyaudio
import time
import json 
import os.path
import logging

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/logger"))
    import logger as log
except ImportError:
    print("File: " + __file__ + " - Import log failed")
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/JSON"))
    import json_utils
except ImportError:
    print("File: " + __file__ + " - Import JSON failed")
    exit()

timerList = []
def processCommand(logger, subCommand, typeCommand, parameters):
    if subCommand == "alarm":
        if typeCommand == "set":
            if parameters["time"]:
                print("Time put: " + parameters["time"])
                timerList.append(parameters["time"])


def checkForAlarm():
    ctime = time.strftime("%H:%M:%S")
    print("CTime get: " + ctime)
    for t in timerList:
        if ctime == t:
            os.system("cvlc Resources/alarm.mp3 &")
            break
    # nowhour = int(time.strftime("%H"))
    # nowmin = int(time.strftime("%M"))
    # nowsec = int(time.strftime("%S"))


def TimerProcess(log_q, audio_q, cmd_q):
    logger = log.loggerInit(log_q)
    logger.log(logging.INFO, "Timer proccess is started")

    while True:
        time.sleep(1)
        try:
            command = None
            try:
                command = cmd_q.get_nowait()
            except Exception as e:
                pass
            
            if command == None:
                continue

            logger.log(logging.DEBUG, "Command: " + command)
            if json_utils.jsonSimpleParser(command, "des") == "timer":
                parameters = json_utils.jsonSimpleParser(command, "parameters")
                actionStr = str(json_utils.jsonSimpleParser(command, "action"))
                actionWords = actionStr.split('.')

                subCommand = actionWords[0]
                logger.log(logging.DEBUG, "Sub Command: " + subCommand)
                typeCommand = actionWords[1]
                logger.log(logging.DEBUG, "Type Command: " + typeCommand)

                processCommand(logger, subCommand, typeCommand, parameters)
                checkForAlarm()
            
        except Exception as e:
            logger.log(logging.ERROR, "Failed to run Timer process: exception={})".format(e))
            continue