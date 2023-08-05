# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import json
import snappy
import six
from growingio_tracker.data_parser import JsonParser


class SnappyParser(JsonParser):

    def __init__(self, crypt_data=False):
        super(SnappyParser, self).__init__()
        self._crypt_data = crypt_data

    def get_bytes(self, messages, stm=None):
        batch = []
        for message in messages:
            batch.append(self.json(message))
        batch_json = '[{0}]'.format(','.join(batch))
        raw_data = json.dumps(batch_json)
        compress_data = snappy.compress(raw_data)
        if self._crypt_data:
            return self._xor_crypt(compress_data, stm)
        return compress_data

    def _xor_crypt(self, raw_data, password):
        if six.PY3:
            xor = bytearray()
            for nowByte in bytearray(raw_data):
                newByte = nowByte ^ int(password & 0xff)
                xor.extend(bytes([newByte]))
            return xor
        # elif six.PY2:
        #     xor = ''.join(chr(ord(x) ^ (password & 0xff)) for (x) in raw_data)
        #     return xor
        else:
            self._crypt_data = False
            return raw_data

    def get_headers(self):
        if self._crypt_data and six.PY3:
            return {'content-type': 'application/json', 'X-Compress-Codec': '2', 'X-Crypt-Codec': '1'}
        return {'content-type': 'application/json', 'X-Compress-Codec': '2'}
