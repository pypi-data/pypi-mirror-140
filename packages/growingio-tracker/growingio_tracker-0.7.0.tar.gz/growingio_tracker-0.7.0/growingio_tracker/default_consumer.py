# -*- coding: utf-8 -*-

from .data_parser import JsonParser
from .consumer import Consumer


class DefaultConsumer(Consumer):
    def __init__(self, product_id, data_source_id, server_host, data_parser=None,
                 retry_limit=3, request_timeout=5, retry_backoff_factor=0.25, verify_cert=True):
        super(DefaultConsumer, self).__init__(product_id, data_source_id, server_host,
                                              retry_limit, request_timeout, retry_backoff_factor, verify_cert)
        self._data_parse = data_parser or JsonParser()

    def send(self, message):
        if hasattr(message, 'event_type'):
            request_url = self.endpoints['collect']
        else:
            request_url = self.endpoints['item']

        messages = [message]
        self.post_data(request_url, messages)

    def post_data(self, request_url, messages):
        stm = self._data_parse.get_timestamp()
        data = self._data_parse.get_bytes(messages, stm)

        self.send_data(
            request_url,
            data,
            params=self._data_parse.get_params(stm=stm),
            headers=self._data_parse.get_headers()
        )
