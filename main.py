#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
from multiprocessing import Process, Queue, Value, Lock
import logging
import logging.handlers
from sys import byteorder
from array import array
from struct import pack
from os.path import join, dirname
import wave
import os.path
import sys
import os
import time
import traceback

TOP_DIR = os.path.dirname(os.path.realpath(__file__))

def exitProgram():
    signal_handler()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
    exit()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/logger"))
    import logger
except ImportError:
    print("File: " + __file__ + " - Import logger failed")
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/AMQP"))
    import amqp_utils as amqp
except ImportError:
    print("File: " + __file__ + " - Import AMQP failed")
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/action"))
    import action
except ImportError:
    print("File: " + __file__ + " - Import action failed")
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/network"))
    import wifi_utils
except ImportError:
    print("File: " + __file__ + " - Import network failed")
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/audio"))
    import microphone
    import music
    import speaker
except ImportError:
    print("File: " + __file__ + " - Import audio failed")
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/IoT_devices"))
    import air_purifier
    import humidifier
except ImportError:
    print("File: " + __file__ + " - Import IoT_devices failed")
    exitProgram()

# def testQueue(AudioQueue):
#     print("Put script to AudioQueue")
#     AudioQueue.put(jsonSimpleGenerate("speech", "Hello"))
class StateMachine(object):
    """docstring for StateMachine"""
    def __init__(self, initVal = 0):
        super(StateMachine, self).__init__()
        self.val = Value('i', initVal)
        self.lock = Lock()

    def set(self, inputValue):
        self.val.value = inputValue

    def get(self):
        return self.val.value
        
def main(): 
    # Init queue for sending and receiving:
    LoggingQueue = Queue(1024)
    AMQPSendQueue = Queue(1024)
    AMQPRcvQueue = Queue(1024)
    CommandQueue = Queue(1024)
    ActionQueue = Queue(1024)
    AudioQueue = Queue(1024)

    state_machine = StateMachine(0)

    print("Start")
    logging_p = Process(name = "Log", target=logger.loggingProcess, args=(LoggingQueue, ))
    logging_p.start()

    # amqp_p = Process(name = "AMQP", target=amqp.AMQPProcess, args=(LoggingQueue, AMQPSendQueue, AMQPRcvQueue, CommandQueue, ))
    # amqp_p.start()

    action_p = Process(name = "Action", target=action.ActionManagerProcess, args=(LoggingQueue, ActionQueue, CommandQueue, state_machine, ))
    action_p.start()

    # status_p = Process(name = "Status", target=status.StatusProcess, args=(LoggingQueue, AMQPSendQueue, CommandQueue, ))
    # status_p.start()

    audio_p = Process(name = "Speaker", target=speaker.audioProcess, args=(LoggingQueue, AudioQueue, CommandQueue, state_machine,))
    audio_p.start()

    voice_p = Process(name = "Micro", target=microphone.voiceProcess, args=(LoggingQueue, ActionQueue, AudioQueue, CommandQueue, state_machine,))
    voice_p.start()

    music_p = Process(name = "Music", target=music.MusicProcess, args=(LoggingQueue, AMQPSendQueue, AudioQueue, CommandQueue, state_machine,))
    music_p.start()

    # timer_p = Process(name = "Timer", target=timer.TimerProcess, args=(LoggingQueue, AMQPSendQueue, AudioQueue, CommandQueue, ))
    # timer_p.start()

    # light_p = Process(name = "Light", target=light.LightProcess, args=(LoggingQueue, AMQPSendQueue, AudioQueue, CommandQueue, ))
    # light_p.start()

    # airPurifier_p = Process(name = "AirPur", target=air_purifier.AirPurifierProcess, args=(LoggingQueue, AudioQueue, Command_q))
    # airPurifier_p.start()

    # humidifier_p = Process(name = "Humidifier", target=humidifier.HumidifierProcess, args=(LoggingQueue, AudioQueue, CommandQueue, state_machine,))
    # humidifier_p.start()

    # voice_p.join()
    # audio_p.join()
    # amqp_p.join()
    # airPurifier_p.join()
    # humidifier_p.join()
    # action_p.join()
    logging_p.join()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.log(logging.DEBUG, 'Interrupted')
        exitProgram()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(type(e))
    
    
        
