import sys
import os.path
import logging
import json

TOP_DIR = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), os.pardir)
UTILS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

try:
    import amqp_client as amqp
except ImportError:
    exit()

try:
    sys.path.insert(0, os.path.join(UTILS_DIR, "logger"))
    import logger as log
except ImportError:
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/JSON"))
    import json_utils
except ImportError:
    exit()


actionStatusList = ["check"]
actionTimerList = ["alarm", "time"]
actionLightList = ["smarthome.lights", "lights"]
actionMusicList = ["music", "music_player_control", "video", "video_player_control"]
actionHumidifierList = ["smarthome.humidity"]
actionList = [actionStatusList, actionTimerList, actionLightList, actionMusicList, actionHumidifierList]
processName = ["status", "timer", "light", "music", "humidifier"]

def ActionManagerProcess(log_q, action_q, cmd_q):
    try:
        logger = log.loggerInit(log_q)
    except Exception as e:
        print("Create logger failed")
        exit()

    try:
        logger.log(logging.INFO, "Action Manager Process is started")
        while True:
            action = action_q.get()
            # action = "{\"action\":\"smarthome.lights.switch.on\"}"
            if action is None:
                # continue
                pass
            else:
                actionStr = json_utils.jsonSimpleParsor(action, "action")
                gotIt = False
                for index, item in enumerate(actionList):
                    for i in item:
                        if (str.find(actionStr,i) >= 0):
                            gotIt = True
                            break
                    if gotIt is True:
                        break
                if gotIt is True:
                    processTarget = processName[index]
                    logger.log(logging.DEBUG, "Process Taiget: " + processTarget)
                    cmdStr = "{"+json_utils.jsonSimpleGenerate("des",processTarget)+",\n"+action+"}"
                    logger.log(logging.DEBUG, "Cmd Str: " + cmdStr)
                    cmd_q.put_nowait(cmdStr)
                else:
                    print("Not found")
    except Exception as e:
        logger.log(logging.ERROR, "Failed to create custom metric: exception={})".format(e))
        raise e
