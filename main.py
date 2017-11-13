from sys import byteorder
from array import array
from struct import pack
from os.path import join, dirname
# from watson_developer_cloud import SpeechToTextV1
from transcribe_streaming_mic import speech2Text
import json
import pyaudio
import wave
import os.path
import sys
from gtts import gTTS
import os

#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = 'df1ec06dbe73433aa3d33b2a4674c542'

# speech_to_text = SpeechToTextV1(
#     username='bdc32f14-9895-419b-8ad2-dd6030248aad',
#     password='16GMSUKRDSfP',
#     x_watson_learning_opt_out=False
# )

# print(json.dumps(speech_to_text.models(), indent=2))

# print(json.dumps(speech_to_text.get_model('en-US_BroadbandModel'), indent=2))

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100


def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD


def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM) / max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i * times))
    return r


def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i) > THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data


def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in xrange(int(seconds * RATE))])
    r.extend(snd_data)
    r.extend([0 for i in xrange(int(seconds * RATE))])
    return r


def record():
    """
    Record a word or words from the microphone and 
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the 
    start and end, and pads with 0.5 seconds of 
    blank sound to make sure VLC et al can play 
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
                    input=True, output=True,
                    frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True

        if snd_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r


def record_to_file(path):
    "Records from the microphone and outputs the resulting data to 'path'"
    sample_width, data = record()
    data = pack('<' + ('h' * len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()


def apiaiPGetResponse(transcript):
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = "vulong"
    request.query = transcript
    response = request.getresponse()

    return response.read()


if __name__ == '__main__':
    while 1:
        # print("please speak a word into the microphone")
        # record_to_file('demo.wav')
        # print("done - result written to demo.wav")

        # Use Google API stream mic:
        transcript = speech2Text()
        apiaiResponse = apiaiPGetResponse(transcript)
        print(apiaiResponse.decode('utf-8'))
        apiaiResponse = json.loads(apiaiResponse.decode('utf-8'))
        if apiaiResponse["result"]:
            print(apiaiResponse["result"]["action"])
            speechScript = apiaiResponse["result"]["fulfillment"]["speech"]
            if speechScript:
                print(speechScript)
                tts = gTTS(text=speechScript, lang='en')
                tts.save("speech.mp3")
                os.system("mpg321 speech.mp3")
            speechScript2 = apiaiResponse["result"]["fulfillment"]["messages"][0]["speech"]
            if (speechScript != speechScript2) and speechScript2:
                tts = gTTS(text=speechScript2, lang='en')
                tts.save("speech.mp3")
                os.system("mpg321 speech.mp3")
                print(speechScript)
        else:
            print("Null api results")

        # Use Watson API.

        # with open(join(dirname(__file__), 'demo.wav'),
        #           'rb') as audio_file:
        #     json_data = json.dumps(speech_to_text.recognize(
        #         audio_file, content_type='audio/wav', timestamps=True,
        #         word_confidence=True),
        #         indent=2)
        #     json_data = json.loads(json_data)
        #     if json_data["results"]:
        #         transcript = json_data["results"][0][
        #             "alternatives"][0]["transcript"]
        #         print("Transcript")
        #         print(transcript)
        #         apiaiResponse = apiaiPGetResponse(transcript)
        #         print(apiaiResponse)
        #         apiaiResponse = json.loads(apiaiResponse)
        #         if apiaiResponse["result"]:
        #             print(apiaiResponse["result"]["action"])
        #             print(apiaiResponse["result"]["fulfillment"]["speech"])
        #             print(apiaiResponse["result"]["fulfillment"][
        #                   "messages"][0]["speech"])
        #         else:
        #             print("Null api results")
        #     else:
        #         print("Null watson results")
