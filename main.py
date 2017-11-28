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
# from watson_developer_cloud import SpeechToTextV1
# import snowboy/examples/Python3/snowboydecoder
# import signal

import wave
import os.path
import sys
import os
import time
import traceback

TOP_DIR = os.path.dirname(os.path.realpath(__file__)), 

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



# def testQueue(AudioQueue):
#     print("Put script to AudioQueue")
#     AudioQueue.put(jsonSimpleGenerate("speech", "Hello"))

def main(): 
    # Init queue for sending and receiving:
    LoggingQueue = Queue(1024)
    AMQPSendQueue = Queue(1024)
    AMQPRcvQueue = Queue(1024)
    ManagerJSONQueue = Queue(50)
    AudioQueue = Queue(50)

    amqp_p = Process(target=amqp.AMQPProcess, args=(AMQPSendQueue, AMQPRcvQueue, ManagerJSONQueue, ))
    amqp_p.start()

    logging_p = Process(target=logger.loggingProcess, args=(LoggingQueue, ))
    logging_p.start()

    voice_p = Process(target=microphone.voiceProcess, args=(LoggingQueue, ManagerJSONQueue, AudioQueue, ))
    voice_p.start()
    
    audio_p = Process(target=speaker.audioProcess, args=(LoggingQueue, AudioQueue, ))
    audio_p.start()

    voice_p.join()
    audio_p.join()
    amqp_p.join()
    logging_p.join()
    
    # process3 = Process(target=managerProcess, args=(ManagerJSONQueue, ))
    # process3.start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.log(logging.DEBUG, 'Interrupted')
        exitProgram()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(type(e))
    
    
        
