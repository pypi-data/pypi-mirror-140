import logging
import asyncio
import time
from koil.vars import current_cancel_event

logger = logging.getLogger(__name__)


class KoilTask:
    def __init__(
        self, coro, loop, func_args, func_kwargs, *args, log_errors=True, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.coro = coro
        self.args = func_args
        self.kwargs = func_kwargs
        self.loop = loop
        self.task = None

    def run(self):
        self.future = asyncio.run_coroutine_threadsafe(
            self.coro(*self.args, **self.kwargs), self.loop
        )
        return self

    def done(self):
        return self.future.done()

    async def acancel(self):
        try:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError as e:
                logger.debug("Cancelled KoilTask")
        except Exception as e:
            logger.debug("Koil Task Cancellation failed")

    def cancel(self):
        self.future.cancel()

    def result(self):
        return self.future.result()


class KoilGeneratorTask:
    def __init__(self, iterator, loop, func_args, func_kwargs, *args, **kwargs) -> None:
        print("initializitng generator task")
        super().__init__(*args, **kwargs)
        self.iterator = iterator
        self.args = func_args
        self.kwargs = func_kwargs
        self.loop = loop
        self.task = None

    def run(self):
        ait = self.iterator(*self.args, **self.kwargs).__aiter__()
        res = [False, False]
        cancel_event = current_cancel_event.get()

        async def next_on_ait_with_context():
            try:
                try:
                    obj = await ait.__anext__()
                    return [False, obj]
                except StopAsyncIteration:
                    return [True, None]
            except asyncio.CancelledError as e:
                return [False, e]

        while True:
            res = asyncio.run_coroutine_threadsafe(
                next_on_ait_with_context(), loop=self.loop
            )
            while not res.done():
                if cancel_event and cancel_event.is_set():
                    raise Exception("Task was cancelled")

                time.sleep(0.01)
            done, obj = res.result()
            if done:
                if obj:
                    raise obj
                break
            yield obj
