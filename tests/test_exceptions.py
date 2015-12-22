"""Test Henson's exceptions."""

import asyncio

from henson import exceptions
from henson.base import Application


def test_abort_preprocessor(event_loop, cancelled_future, queue):
    """Test that aborted preprocessors stop execution."""
    # This test sets up two preprocessors, a callback, and a
    # postprocessor. The first preprocessor will raise an Abort
    # exception. None of the others should be called.
    preprocess1_called = False
    preprocess2_called = False
    callback_called = False
    postprocess_called = False

    queue.put_nowait({'a': 1})

    @asyncio.coroutine
    def preprocess1(app, message):
        nonlocal preprocess1_called
        preprocess1_called = True
        raise exceptions.Abort('testing', message)

    @asyncio.coroutine
    def preprocess2(app, message):
        nonlocal preprocess2_called
        preprocess2_called = True
        return message

    @asyncio.coroutine
    def callback(app, message):
        nonlocal callback_called
        callback_called = True
        return message

    @asyncio.coroutine
    def postprocess(app, result):
        nonlocal postprocess_called
        postprocess_called = True
        return result

    app = Application(
        'testing',
        callback=callback,
        message_preprocessors=[preprocess1, preprocess2],
        result_postprocessors=[postprocess],
    )

    event_loop.run_until_complete(app._process(cancelled_future, queue))

    assert preprocess1_called
    assert not preprocess2_called
    assert not callback_called
    assert not postprocess_called


def test_abort_callback(event_loop, cancelled_future, queue):
    """Test that aborted callbacks stop execution."""
    # This test sets up a callback and a postprocessor. The callback
    # will raise an Abort exception. The postprocessor shouldn't be
    # called.
    callback_called = False
    postprocess_called = False

    queue.put_nowait({'a': 1})

    @asyncio.coroutine
    def callback(app, message):
        nonlocal callback_called
        callback_called = True
        raise exceptions.Abort('testing', message)

    @asyncio.coroutine
    def postprocess(app, result):
        nonlocal postprocess_called
        postprocess_called = True
        return result

    app = Application(
        'testing',
        callback=callback,
        result_postprocessors=[postprocess],
    )

    event_loop.run_until_complete(app._process(cancelled_future, queue))

    assert callback_called
    assert not postprocess_called


def test_abort_postprocess(event_loop, cancelled_future, queue):
    """Test that aborted postprocessors stop execution of the result."""
    # This test sets up a callback and two postprocessors. The first
    # will raise an Abort exception for one of the two results returned
    # by the callback.
    postprocess1_called_count = 0
    postprocess2_called_count = 0

    queue.put_nowait({'a': 1})

    @asyncio.coroutine
    def callback(app, message):
        return [True, False]

    @asyncio.coroutine
    def postprocess1(app, result):
        nonlocal postprocess1_called_count
        postprocess1_called_count += 1
        if result:
            raise exceptions.Abort('testing', result)
        return result

    @asyncio.coroutine
    def postprocess2(app, result):
        nonlocal postprocess2_called_count
        postprocess2_called_count += 1
        return result

    app = Application(
        'testing',
        callback=callback,
        result_postprocessors=[postprocess1, postprocess2],
    )

    event_loop.run_until_complete(app._process(cancelled_future, queue))

    assert postprocess1_called_count == 2
    assert postprocess2_called_count == 1