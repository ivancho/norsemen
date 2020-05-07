# -*- coding: utf-8 -*-
#
# WebVTT format subtitle files translation
# Takes care of parsing and quirks of subtitles,
# and passes the text to a translation service.
#
import re
import requests
import sys
import webvtt

SERVICE_URL = 'http://localhost:5009/translate'

# Translate sometimes decides names are typoed words and mis-translates them
# We hide them as strings that it will not touch, and later replace back
NAME_CODES = {
    'Frøya': 'FFFFF',
    'Orm': 'OOOOO',
}


def encode_names(captions, back=False):
    for caption in captions:
        for name, code in NAME_CODES.items():
            if back:
                name, code = code, name
            caption.text = re.sub(r'\b{}\b'.format(name), code, caption.text)


def fix_hyphenation(captions):
    '''Translate doesn't understand hyphenations across lines, so we join them'''
    for caption in captions:
        caption.text = re.sub(r'(?<=\S)-\n(?=\S)', '', caption.text)


def translate_texts(captions):
    '''Translate in-place the caption texts using service'''
    # To send all captions in one batch text,
    # we join them with a recognizable separator.
    # We can't send the VTT file, because Translate
    # will mangle the timestamps
    sep = '\n~~~~\n'
    text = sep.join(c.text for c in captions)

    resp = requests.post(SERVICE_URL, data={'text': text})

    translated = resp.content.decode('utf-8').split(sep)

    for c, t in zip(captions, translated):
        c.text = t


def translate_captions_file(inbuf, outbuf):
    '''Translates captions from input buffer to output buffer'''
    captions = webvtt.read_buffer(inbuf)

    encode_names(captions)
    fix_hyphenation(captions)

    translate_texts(captions)

    encode_names(captions, back=True)

    captions.write(outbuf)


if __name__ == '__main__':
    if sys.stdin.isatty(): # can pass 2 filenames on command line
        with open(sys.argv[1]) as inbuf, open(sys.argv[2], 'w') as outbuf:
            translate_captions_file(inbuf, outbuf)
    else: # or pipe through
        translate_captions_file(sys.stdin, sys.stdout)
