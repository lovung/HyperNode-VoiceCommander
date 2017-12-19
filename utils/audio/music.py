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
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/JSON"))
    import json_utils
except ImportError:
    exit()

