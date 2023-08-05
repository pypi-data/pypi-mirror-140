# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
import time
import uuid

from .version import VERSION
from .default_consumer import DefaultConsumer
from .debug_consumer import DebugConsumer
from .buffered_consumer import BufferedConsumer
from .async_buffered_consumer import AsyncBufferedConsumer
from .consumer import Consumer
from .message import CustomEventMessage, ItemMessage, UserLoginMessage

__version__ = VERSION


class GrowingTracker(object):

    def __init__(self, product_id, data_source_id, server_host, consumer=None):
        self._product_id = product_id
        self._data_source_id = data_source_id
        self._server_host = server_host
        self._consumer = consumer or DefaultConsumer(product_id, data_source_id, server_host)

    @staticmethod
    def consumer(consumer):
        return GrowingTracker(consumer._product_id, consumer._data_source_id, consumer._server_host, consumer)

    @staticmethod
    def _now():
        return int(time.time() * 1000)

    @staticmethod
    def _make_insert_id():
        return uuid.uuid4().hex

    def track_custom_event(self, event_name, event_time=None, anonymous_id=None, login_user_key=None,
                           login_user_id=None,
                           attributes=None):
        message = CustomEventMessage.EventBuilder() \
            .set_product_id(self._product_id).set_data_source_id(self._data_source_id) \
            .set_event_name(event_name).set_event_time(event_time).set_anonymous_id(anonymous_id) \
            .set_login_user(login_user_key, login_user_id).set_attributes(attributes).build()
        self._consumer.send(message)

    def submit_item(self, item_key, item_id, item_attrs=None):
        message = ItemMessage.ItemBuilder().set_item_key(item_key).set_item_id(item_id) \
            .set_product_id(self._product_id).set_data_source_id(self._data_source_id) \
            .set_attributes(item_attrs).build()
        self._consumer.send(message)

    def track_user(self, login_user_key=None, login_user_id=None, anonymous_id=None, event_time=None, attributes=None):
        message = UserLoginMessage.UserBuilder() \
            .set_product_id(self._product_id).set_data_source_id(self._data_source_id) \
            .set_event_time(event_time).set_anonymous_id(anonymous_id) \
            .set_login_user(login_user_key, login_user_id).set_attributes(attributes).build()
        self._consumer.send(message)

    def track(self, message):
        message.set_product_id(self._product_id)
        message.set_data_source_id(self._data_source_id)
        self._consumer.send(message)
