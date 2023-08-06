# Ref: https://github.com/whitphx/streamlit-webrtc/blob/main/streamlit_webrtc/eventloop.py  # noqa

import asyncio

from streamlit.server.server import Server
from tornado.platform.asyncio import BaseAsyncIOLoop


def get_server_event_loop() -> asyncio.AbstractEventLoop:
    current_server = Server.get_current()
    ioloop = current_server._ioloop

    # `ioloop` is expected to be of type `BaseAsyncIOLoop`,
    # which has the `asyncio_loop` attribute.
    if not isinstance(ioloop, BaseAsyncIOLoop):
        raise Exception("Unexpectedly failed to access the asyncio event loop.")

    return ioloop.asyncio_loop
