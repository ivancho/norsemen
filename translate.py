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
    'Frøya': 'Fabiana',
    'Orm': 'Ognyan',
    'Varg': 'Vancho',
    'Liv': 'Linda',
}

RE_WORD_HYPHENATION = re.compile(r'(?<=\S)-\n(?=\S)')

def update_text(caption, new_text, flag_name):
    d = caption.__dict__.setdefault('preprocess', {})
    if caption.text != new_text:
        d[flag_name] = caption.text
        caption.text = new_text


def encode_names(captions, back=False):
    for caption in captions:
        for name, code in NAME_CODES.items():
            if back:
                if 'person_name' not in caption.preprocess:
                    continue # to avoid some weird materialization of characters
                name, code = code, name
            update_text(caption, re.sub(r'\b{}\b'.format(name), code, caption.text), 'person_name')


def fix_hyphenation(captions):
    '''Translate doesn't understand hyphenations across lines, so we join them.'''
    for caption in captions:
        update_text(caption, re.sub(RE_WORD_HYPHENATION, '', caption.text), 'hyphenation')
        update_text(caption, re.sub(r'^-(?=\S)', '- ', caption.text), 'leading_hyphen')


def revert_hyphenation(captions):
    for caption in captions:
        if 'leading_hyphen' in caption.preprocess:
            caption.text = re.sub('^- ', '-', caption.text)


def translate_texts(captions, method='inplace'):
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
        if method == 'inplace':
            c.text = t
        elif method == 'concat':
            c.text = '{}\n---\n{}'.format(c.text, t)
        else:
            raise Exception('Unsupported translation method {}'.format(method))


def translate_captions_file(inbuf, outbuf, method='inplace'):
    '''Translates captions from input buffer to output buffer'''
    captions = webvtt.read_buffer(inbuf)

    # Preprocess
    encode_names(captions)
    fix_hyphenation(captions)

    # Main
    translate_texts(captions, method)

    # Postprocess
    encode_names(captions, back=True)
    revert_hyphenation(captions)

    captions.write(outbuf)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--method', default='inplace')
    args = parser.parse_args()

    # Handle filename stuff outside (e.g. translate.py <$in >$out)
    translate_captions_file(sys.stdin, sys.stdout, args.method)
