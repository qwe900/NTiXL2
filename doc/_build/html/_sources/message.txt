message module
==============

.. inheritance-diagram:: ntixl2.message

.. automodule:: ntixl2.message

Basic Message Classes
*********************

There are two main different types of messages:

 - Query messages with a return
 - Messages without return

There are messages that need a parameter, some of these messages can have a repetition of this parameter.

.. autoclass:: ntixl2.message.Message
    :members:

.. autoclass:: ntixl2.message.MessageWithParam
    :show-inheritance:
    :members:

.. autoclass:: ntixl2.message.MessageWithParams
    :show-inheritance:
    :members:

Xl2 Messages
************

.. autoclass:: ntixl2.QUERY_IDN
    :show-inheritance:

.. autoclass:: ntixl2.SYSTEM_MSDMAC
    :show-inheritance: