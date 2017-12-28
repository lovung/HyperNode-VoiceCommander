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
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/AMQP"))
    import amqp_utils as amqp
except ImportError:
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/action"))
    import action
except ImportError:
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/network"))
    import wifi_utils
except ImportError:
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/audio"))
    import microphone
    import speaker
except ImportError:
    exitProgram()

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/IoT_devices"))
    import air_purifier
    import humidifier
except ImportError:
    print("Import failed")
    exitProgram()

# def testQueue(AudioQueue):
#     print("Put script to AudioQueue")
#     AudioQueue.put(jsonSimpleGenerate("speech", "Hello"))

def main(): 
    # Init queue for sending and receiving:
    LoggingQueue = Queue(1024)
    AMQPSendQueue = Queue(1024)
    AMQPRcvQueue = Queue(1024)
    CommandQueue = Queue(1024)
    ActionQueue = Queue(1024)
    AudioQueue = Queue(1024)

    print("Start")
    logging_p = Process(target=logger.loggingProcess, args=(LoggingQueue, ))
    logging_p.start()

    # amqp_p = Process(target=amqp.AMQPProcess, args=(LoggingQueue, AMQPSendQueue, AMQPRcvQueue, CommandQueue, ))
    # amqp_p.start()

    action_p = Process(target=action.ActionManagerProcess, args=(LoggingQueue, ActionQueue, CommandQueue, ))
    action_p.start()

    # status_p = Process(target=status.StatusProcess, args=(LoggingQueue, AMQPSendQueue, CommandQueue, ))
    # status_p.start()

    audio_p = Process(target=speaker.audioProcess, args=(LoggingQueue, AudioQueue, CommandQueue, ))
    audio_p.start()

    voice_p = Process(target=microphone.voiceProcess, args=(LoggingQueue, ActionQueue, AudioQueue, CommandQueue, ))
    voice_p.start()

    # music_p = Process(target=music.MusicProcess, args=(LoggingQueue, AMQPSendQueue, AudioQueue, CommandQueue, ))
    # music_p.start()

    # timer_p = Process(target=timer.TimerProcess, args=(LoggingQueue, AMQPSendQueue, AudioQueue, CommandQueue, ))
    # timer_p.start()

    # light_p = Process(target=light.LightProcess, args=(LoggingQueue, AMQPSendQueue, AudioQueue, CommandQueue, ))
    # light_p.start()

    # airPurifier_p = Process(target=air_purifier.AirPurifierProcess, args=(LoggingQueue, AudioQueue, Command_q))
    # airPurifier_p.start()

    humidifier_p = Process(target=humidifier.HumidifierProcess, args=(LoggingQueue, AudioQueue, CommandQueue, ))
    humidifier_p.start()

    voice_p.join()
    audio_p.join()
    # amqp_p.join()
    # airPurifier_p.join()
    humidifier_p.join()
    action_p.join()
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
    
    
        
