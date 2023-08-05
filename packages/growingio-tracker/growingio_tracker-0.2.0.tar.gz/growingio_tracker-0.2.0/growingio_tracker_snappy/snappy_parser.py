# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import json
from growingio_tracker.data_parser import JsonParser
import snappy


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
        xor = bytearray()
        for nowByte in bytearray(raw_data):
            newByte = nowByte ^ int(password & 0xff)
            xor.extend(bytes([newByte]))
        return xor

    def get_headers(self):
        if self._crypt_data:
            return {'content-type': 'application/json', 'X-Compress-Codec': '2', 'X-Crypt-Codec': '1'}
        return {'content-type': 'application/json', 'X-Compress-Codec': '2'}
