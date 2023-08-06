from contextlib import contextmanager
import contextvars
import sys
import threading
import asyncio
from asyncio.runners import _cancel_all_tasks
from threading import Thread
import os
import logging
import time
from typing import Optional
import concurrent
import uuid


try:
    import uvloop
except:
    uvloop = None


from koil.checker.registry import get_checker_registry
from koil.state import KoilState


logger = logging.getLogger(__name__)

lock = threading.Lock()  # for setting exactly one thread
loop = [None]
current_koil = contextvars.ContextVar("current_koil", default=None)
iothread = [None]  # dedicated KoilLoop thread


def get_current_koil(**kwargs):
    global GLOBAL_KOIL
    koil = current_koil.get()
    if koil is None:
        return GLOBAL_KOIL

    return koil


def set_global_koil(koil):
    global GLOBAL_KOIL
    GLOBAL_KOIL = koil

    return koil


own_loops = {}
own_threads = {}


@contextmanager
def _selector_policy():
    original_policy = asyncio.get_event_loop_policy()
    try:
        if (
            sys.version_info >= (3, 8)
            and os.name == "nt"
            and hasattr(asyncio, "WindowsSelectorEventLoopPolicy")
        ):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        yield
    finally:
        asyncio.set_event_loop_policy(original_policy)


def newloop(loop, loop_started):
    asyncio.set_event_loop(loop)
    try:
        loop_started.set()
        print("Running New Event loop in another Thread")
        loop.run_forever()
    finally:
        print("Loop Shutting Down")
        try:
            _cancel_all_tasks(loop)
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            asyncio.set_event_loop(None)
            loop.close()


def get_global_loop(uvify=True):
    """Create or return the default Koil IO loop
    The loop will be running on a separate thread.
    """
    if uvify and uvloop is not None:
        uvloop.install()

    if loop[0] is None:
        with lock:
            # repeat the check just in case the loop got filled between the
            # previous two calls from another thread
            if loop[0] is None:
                with _selector_policy():
                    loop[0] = asyncio.new_event_loop()

                loop_started_event = threading.Event()
                th = threading.Thread(
                    target=newloop, args=(loop, loop_started_event), name="KoilLoop"
                )
                th.daemon = True
                th.start()
                loop_started_event.wait()
                iothread[0] = th

    return loop[0]


def get_threaded_loop(uvify=True, name="KoilLoop"):
    """Create or return the default Koil IO loop
    The loop will be running on a separate thread.
    """
    if uvify and uvloop is not None:
        uvloop.install()

    if name not in own_loops:
        with lock:
            # repeat the check just in case the loop got filled between the
            # previous two calls from another thread
            if name not in own_loops:
                with _selector_policy():
                    own_loops[name] = asyncio.new_event_loop()
                th = threading.Thread(target=own_loops[name].run_forever, name=name)
                th.daemon = True
                th.start()
                own_threads[name] = th

    return own_loops[name]


class KoilTask:
    def __init__(self, future, loop) -> None:
        self.future = future
        self.loop = loop
        self.task = None

    def run(self):
        self.task = self.loop.create_task(self.future)
        return self

    async def acancel(self):
        try:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError as e:
                print("Cancelled KoilTask")
        except Exception as e:
            print("Koil Task Cancellation failed")

    def cancel(self):
        return asyncio.run_coroutine_threadsafe(self.acancel(), self.loop).result()


class Koil:
    def __init__(
        self,
        allowed_grace_period: Optional[int] = None,
        uvify=True,
        register_global=False,
        name=None,
    ) -> None:
        self.loop = None
        self.allow_grace_period = allowed_grace_period
        self.uvify = uvify
        self.name = name or f"Koil Loop {str(uuid.uuid4())}"

        if register_global:
            set_global_koil(self)

    def run(self, func, *args, timeout=None, **kwargs):
        if self.loop is None:
            self.loop = get_threaded_loop(self.uvify)

        try:
            if self.loop.is_closed():
                raise RuntimeError("Loop is not running")
            try:
                loop0 = asyncio.events.get_running_loop()
                if loop0 is self.loop:
                    raise NotImplementedError(
                        "Calling sync() from within a running loop"
                    )
            except RuntimeError:
                pass

            coro = func(*args, **kwargs)
            co_future = asyncio.run_coroutine_threadsafe(coro, self.loop)

            return co_future.result(timeout=timeout)
        except KeyboardInterrupt:
            print("Grace period triggered?")
            raise

    def task(self, func, *args, timeout=None, **kwargs):
        if self.loop is None:
            self.loop = get_threaded_loop()

        try:
            if self.loop.is_closed():
                raise RuntimeError("Loop is not running")
            try:
                loop0 = asyncio.events.get_running_loop()
                if loop0 is self.loop:
                    raise NotImplementedError(
                        "Calling sync() from within a running loop"
                    )
            except RuntimeError:
                pass

            coro = func(*args, **kwargs)
            return KoilTask(coro, self.loop).run()
        except KeyboardInterrupt:
            print("Grace period triggered?")
            raise

    def yieldfrom(self, iterate, *args, timeout=None, **kwargs):
        if self.loop is None:
            self.loop = get_threaded_loop()

        try:
            if self.loop.is_closed():
                raise RuntimeError("Loop is not running")
            try:
                loop0 = asyncio.events.get_running_loop()
                if loop0 is self.loop:
                    raise NotImplementedError(
                        "Calling sync() from within a running loop"
                    )
            except RuntimeError:
                pass

            ait = iterate(*args, **kwargs).__aiter__()

            async def next_on_ait():
                try:
                    try:
                        obj = await ait.__anext__()
                        return False, obj
                    except StopAsyncIteration:
                        return True, None
                except asyncio.CancelledError as e:
                    return True, Exception("Await cancelled Task")

            while True:
                res = asyncio.run_coroutine_threadsafe(next_on_ait(), self.loop)
                done, obj = res.result(timeout=timeout)
                if done:
                    if obj:
                        raise obj
                    break
                yield obj

        except KeyboardInterrupt:
            if self.allow_grace_period:
                print("Allowing loop to shutdown gracefully")
                if not res.done():
                    res.cancel()
                try:
                    res.result(timeout=timeout)
                except concurrent.futures.CancelledError:
                    print("Grace period was sucessfull?")
                except concurrent.futures.TimeoutError:
                    print("Could not gracefully shutdown loop")
                except Exception as ex:
                    print(ex)
            raise

    def close(self):
        asyncio.run_coroutine_threadsafe(self.aclose(), self.loop)

        while self.loop.is_running():
            print("Waiting for the Loop to close")
            time.sleep(0.1)

    def __enter__(self):
        assert self.loop is None, "You cannot enter an already spunup loop"
        self.loop = get_threaded_loop()
        current_koil.set(self)
        return self

    def __exit__(self, *args, **kwargs):
        self.close()
        current_koil.set(None)

    def __repr__(self) -> str:
        return f"Koil running in  {self.thread_id}"


current_koil = contextvars.ContextVar("current_koil", default=None)
GLOBAL_KOIL = None

default_koil = Koil(register_global=True)
