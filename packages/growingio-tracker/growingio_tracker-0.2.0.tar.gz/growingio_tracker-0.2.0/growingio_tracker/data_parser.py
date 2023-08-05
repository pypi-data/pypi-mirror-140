# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import json
import time
from .version import VERSION


class DataParser(object):
    def get_bytes(self, messages, stm=None):
        pass

    def get_params(self, stm=None):
        pass

    def get_headers(self):
        pass

    @staticmethod
    def get_timestamp():
        return int(time.time() * 1000)


class JsonParser(DataParser):

    def __init__(self):
        pass

    def get_bytes(self, messages, stm=None):
        batch = []
        for message in messages:
            batch.append(self.json(message))
        batch_json = '[{0}]'.format(','.join(batch))
        return batch_json

    def get_headers(self):
        return {'content-type': 'application/json'}

    def get_params(self, stm=None):
        return {'stm': stm}

    @staticmethod
    def json_dumps(data, cls=None):
        return json.dumps(data, separators=(',', ':'), cls=cls)

    def json(self, message):
        dict = {}

        # event message
        if hasattr(message, 'event_type') and message.event_type is not None:
            dict['eventType'] = message.event_type
        if hasattr(message, 'event_time') and message.event_time is not None:
            dict['timestamp'] = message.event_time
        if hasattr(message, 'event_name') and message.event_name is not None:
            dict['eventName'] = message.event_name
        if hasattr(message, 'anonymous_id') and message.anonymous_id is not None:
            dict['deviceId'] = message.anonymous_id
        if hasattr(message, 'login_user_key') and message.login_user_key is not None:
            dict['userKey'] = message.login_user_key
        if hasattr(message, 'login_user_id') and message.login_user_id is not None:
            dict['userId'] = message.login_user_id
        if hasattr(message, 'attributes') and message.attributes is not None:
            dict['attributes'] = message.attributes

        # item message
        if hasattr(message, 'key') and message.key is not None:
            dict['key'] = message.key
        if hasattr(message, 'id') and message.id is not None:
            dict['id'] = message.id
        if hasattr(message, 'attrs') and message.attrs is not None:
            dict['attributes'] = message.attrs

        # common
        if hasattr(message, 'data_source_id'): dict['dataSourceId'] = message.data_source_id
        if hasattr(message, 'product_id'): dict['projectKey'] = message.product_id

        dict['sdkVersion'] = VERSION
        dict['sdkType'] = 'python'

        return self.json_dumps(dict)
