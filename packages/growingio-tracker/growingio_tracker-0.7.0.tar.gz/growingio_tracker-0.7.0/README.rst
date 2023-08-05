growingio-track-python
==============================

GrowingIO提供在Python Server端部署的SDK，从而可以方便的进行事件上报等操作


Installation
------------

可以使用 pip 下载我们的sdk::

    pip install growingio_tracker

Getting Started
---------------

简单示例::

    from growingio_tracker import GrowingTracker

    # 方式1：使用默认配置
    growing_tracker = GrowingTracker('<product_id>', '<data_source_id>', '<server_host>')

    # 方式2: 自定义发送策略
    from growingio_tracker import DefaultConsumer
    default_consumer = DefaultConsumer('<product_id>', '<data_source_id>', '<server_host>')
    growing_tracker = GrowingTracker.consumer(default_consumer)


