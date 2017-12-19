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

