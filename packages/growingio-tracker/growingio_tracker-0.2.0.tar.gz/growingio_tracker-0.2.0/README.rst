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

    growing_tracker = GrowingTracker('<ProductId>', '<DataSOurceId>', '<ServerHost>')
    growing_tracker.track_custom_event("test", attributes={'name': 'cpacm', 'age': '100'},
                                       login_user_id='user', login_user_key='email')
    growing_tracker.submit_item('test', 'python', item_attrs={'name': 'cpacm'})


