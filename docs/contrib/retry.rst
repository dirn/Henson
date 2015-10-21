=====
Retry
=====

Retry is a plugin to add the ability for Henson to automatically retry messages
that fail to process.

.. warning::

   Retry registers itself as an error callback on the
   :class:`~henson.base.Application` instance. When doing so, it inserts itself
   at the beginning of the list of error callbacks. It does this so that it can
   prevent other callbacks from running.

   If you have an error callback that you want to run even when retrying a
   message, make sure you register it *after* initializing Retry.

Configuration
=============

Retry provides a couple settings to control how many times a message will be
retried. ``RETRY_THESHOLD`` and ``RETRY_TIMEOUT`` work in tandem. If values are
specified for both, whichever limit is reached first will cause Henson to stop
retrying the message. By default, Henson will try forever (yes, this is
literally insane).

+------------------+----------------------------------------------------------+
| RETRY_BACKOFF    | If set to True, the delay between retry attempts will    |
|                  | increase between each subsequent retry. Defaults to      |
|                  | False.                                                   |
+------------------+----------------------------------------------------------+
| RETRY_CALLBACK   | A callable that encapsulates the functionality needed to |
|                  | retry the message. If no value is provided, a            |
|                  | ``TypeError`` will be raised.                            |
+------------------+----------------------------------------------------------+
| RETRY_EXCEPTIONS | An exception or tuple of exceptions that will cause      |
|                  | Henson to retry the message.  Defaults to                |
|                  | `RetryableException`.                                    |
+------------------+----------------------------------------------------------+
| RETRY_DELAY      | The number of seconds to wait before scheduling a retry. |
|                  | If ``RETRY_BACKOFF`` is set to True, the delay will      |
|                  | increase between each retry. Defaults to 0.              |
+------------------+----------------------------------------------------------+
| RETRY_THRESHOLD  | The maximum number of times that a Henson application    |
|                  | will try to process a message before marking it as a     |
|                  | failure. if set to 0, the message will not be retried.   |
|                  | If set to None, the limit will be controlled by          |
|                  | ``RETRY_TIMEOUT``. Defaults to None.                     |
+------------------+----------------------------------------------------------+
| RETRY_TIMEOUT    | The maximum number of seconds during which a message can |
|                  | be retried. If set to None, the limit will be controlled |
|                  | by ``RETRY_THRESHOLD``. Defaults to None.                |
+------------------+----------------------------------------------------------+

Usage
=====

Application definition::

    from henson import Application
    from henson.contrib.retry import Retry

    def print_message(app, message):
        print(message)

    app = Application('retryable-application', callback=my_callback)
    app.settings['RETRY_CALLBACK'] = print_message
    Retry(app)

Somwhere inside the application::

   from henson.contrib.retry import RetryableException

   def my_callback(app, message):
       raise RetryableException

API
===

.. autoclass:: henson.contrib.retry.Retry
   :members:

.. autoclass:: henson.contrib.retry.RetryableException