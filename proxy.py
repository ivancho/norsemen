# -*- coding: utf-8 -*-
#
# Microservice to wrap translation requests into appropriate garments
# and send them to a Google Translate endpoint
# that doesn't require authentication.
#
import flask
import html
import os
import re
import requests

app = flask.Flask(__name__)

GOOG_URL = 'https://translate.googleusercontent.com/translate_f'

REQ_HEADERS = {
    'Origin': 'https://translate.google.com', # tee-hee
    'Referrer': 'https://translate.google.com',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Host': 'translate.googleusercontent.com',
    'Accept-Language': 'en-US,en;q=0.5',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:75.0) Gecko/20100101 Firefox/75.0',
}

TRANSLATE_PARAMS = {
    'hl': (None, 'en'),
    'ie': (None, 'UTF-8'),
    'js': (None, 'y'),
    'prev': (None, '_t'),
    'sl': (None, 'auto'),
    'tl': (None, 'en'),
}


def unpack_content(content):
    '''It comes as bytes, single <pre> tag with html entities encoded'''
    content = html.unescape(content.decode('utf-8'))
    return re.sub('(^<pre>|</pre>$)', '', content)


@app.route('/translate', methods=['POST'])
def translate():
    text=flask.request.form['text']

    multipart = {**TRANSLATE_PARAMS,
                 'file': ['UHH32000118.txt', text, 'text/plain']}

    request = requests.post(GOOG_URL,
                            files=multipart,
                            headers=REQ_HEADERS)

    return unpack_content(request.content)


if __name__ == '__main__':
    app.debug = True
    app.run(port=os.environ.get("TRANSLATE_PORT", 5009))
