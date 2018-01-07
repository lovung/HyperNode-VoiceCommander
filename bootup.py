import os.path
import sys
from gtts import gTTS 

TOP_DIR = os.path.dirname(os.path.realpath(__file__))

try:
    sys.path.insert(0, os.path.join(TOP_DIR, "utils/network"))
    import wifi_utils
except ImportError:
    print("File: " + __file__ + " - Import network failed")
    exitProgram()

speech = "My local IP is " + wifi_utils.getLocalWifiIP()
tts = gTTS(text=speech, lang='en')
tts.save("Resources/ip.mp3")
os.system("mpg321 Resources/ip.mp3")
exit()
