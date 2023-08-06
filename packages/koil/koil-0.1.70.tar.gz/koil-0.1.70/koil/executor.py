from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading
from koil.vars import *


class KoiledExecutor(ThreadPoolExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
        )

    def submit(self, fn, *args, **kwargs):
        raise Exception("Do not call this directly. Await asubmit instead")

    async def asubmit(self, fn, *args, **kwargs):
        copy_loop = asyncio.get_event_loop()

        assert (
            copy_loop.is_running()
        ), "Loop is not running. You shouldn't be using this"

        cancel_event = threading.Event()

        def wrap(*args, **kwargs):
            current_loop.set(copy_loop)
            current_cancel_event.set(cancel_event)
            t = fn(*args, **kwargs)
            current_loop.set(None)
            current_cancel_event.set(None)
            return t

        try:
            return await asyncio.wrap_future(super().submit(wrap, fn, *args, **kwargs))
        except asyncio.CancelledError:
            cancel_event.set()
            raise
