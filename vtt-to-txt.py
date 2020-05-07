# -*- coding: utf-8 -*-
import re
import sys
import webvtt

def print_text_from_vtt(inbuf):
    captions = webvtt.read_buffer(inbuf)
    text = '\n'.join(c.text for c in captions)
    text = re.sub('-\n-', '', text)
    print(text)


if __name__ == '__main__':
    print_text_from_vtt(sys.stdin)
