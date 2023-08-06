import asyncio

from .eventloop import get_server_event_loop
from .session_info import get_this_session


def delayed_rerun(delay: float) -> None:
    this_session = get_this_session()

    loop = get_server_event_loop()

    async def callback() -> None:
        await asyncio.sleep(delay)
        this_session.request_rerun(client_state=None)

    loop.create_task(callback())
