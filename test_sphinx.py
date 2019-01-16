#!/usr/bin/env python
from os import environ, path
import time
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

def main():
    MODELDIR = "pocketsphinx/model"
    DATADIR = "pocketsphinx/test/data"

    # Create a decoder with certain model
    config = Decoder.default_config()
    config.set_string('-hmm', path.join(MODELDIR, 'en-us/en-us'))
    config.set_string('-lm', path.join(MODELDIR, 'en-us/en-us.lm.bin'))
    config.set_string('-dict', path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
    config.set_string('-mdef', path.join(MODELDIR, 'en-us/en-us/mdef'))
    decoder = Decoder(config)

    # Decode streaming data.
    decoder = Decoder(config)
    decoder.start_utt()
    stream = open(path.join(DATADIR, 'goforward.raw'), 'rb')
    while True:
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
        else:
            break
    decoder.end_utt()
    print ('Best hypothesis segments: ', [seg.word for seg in decoder.seg()])

if __name__== "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))