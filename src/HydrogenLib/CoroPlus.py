import asyncio


def run_in_new_loop(coro):
    loop = asyncio.new_event_loop()
    return loop, loop.run_until_complete(coro)


def run_in_existing_loop(coro, loop: asyncio.AbstractEventLoop):
    return loop.run_until_complete(coro)


def new_event_loop():
    return asyncio.new_event_loop()

