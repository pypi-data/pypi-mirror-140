# -*- coding: utf-8 -*-

from __future__ import absolute_import
import threading
from .default_consumer import DefaultConsumer


class FlushThread(threading.Thread):
    '''
    FlushThread is used to asynchronously flush the events stored in
    the AsyncBufferedConsumer buffers.
    '''

    def __init__(self, consumer):
        threading.Thread.__init__(self)
        self._consumer = consumer

        self._stop_event = threading.Event()
        self._finished_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        self._finished_event.wait()

    def run(self):
        while True:
            self._consumer.need_flush.wait(self._consumer.flush_after)
            if self._consumer.flush():
                self._consumer.need_flush.clear()
            if self._stop_event.isSet():
                break
        self._finished_event.set()


class AsyncBufferedConsumer(DefaultConsumer):

    def __init__(self, product_id, data_source_id, server_host, data_parser=None,
                 flush_after=10, max_size=500, request_timeout=2,
                 retry_limit=3, retry_backoff_factor=0.25, verify_cert=True):

        super(AsyncBufferedConsumer, self).__init__(
            product_id, data_source_id, server_host, data_parser,
            request_timeout=request_timeout,
            retry_limit=retry_limit,
            retry_backoff_factor=retry_backoff_factor,
            verify_cert=verify_cert,
        )

        # remove the minimum max size that the SynchronousBufferedConsumer
        self._max_size = max_size
        self.flush_after = flush_after

        self.need_flush = threading.Event()

        self._async_events = []
        self._async_items = []

        self._async_buffers = {
            'events': [],
            'items': [],
        }

        self._flushing_thread = FlushThread(self)
        self._flushing_thread.daemon = True
        self._flushing_thread.start()

        self.flush_lock = threading.Lock()
        self.flushing_thread = None

    def _flush_thread_is_free(self):
        return self.flushing_thread is None or not self.flushing_thread.is_alive()

    def _should_flush(self):
        full = len(self._async_events) >= self._max_size or len(self._async_items) > 0

        if full:
            return True

        return False

    def send(self, message):

        if hasattr(message, 'event_type'):
            buf = self._async_events
            buf.append(message)
        else:
            buf = self._async_items
            buf.append(message)

        should_flush = self._should_flush()
        if should_flush:
            self.need_flush.set()
            # self.flush()

    def stop(self):
        self._flushing_thread.stop()

    def flush(self):
        with self.flush_lock:
            if self._flush_thread_is_free():
                self.transfer_buffers()
                self._sync_flush()
                flushing = True
            else:
                flushing = False

        return flushing

    def transfer_buffers(self):
        buf = self._async_events
        while buf:
            self._async_buffers['events'].append(buf.pop(0))
        buf = self._async_items
        while buf:
            self._async_buffers['items'].append(buf.pop(0))

    def _sync_flush(self):
        if len(self._async_buffers['events']) > 0:
            request_url = self.endpoints['collect']
            buf = self._async_buffers['events']
            stm = self._data_parse.get_timestamp()
            while buf:
                batch = buf[:self._max_size]
                self.post_data(request_url, batch)
                buf = buf[self._max_size:]
            self._async_buffers['events'] = buf

        if len(self._async_buffers['items']) > 0:
            request_url = self.endpoints['item']
            buf = self._async_buffers['items']
            while buf:
                batch = buf[:self._max_size]
                self.post_data(request_url, batch)
                buf = buf[self._max_size:]
            self._async_buffers['items'] = buf
