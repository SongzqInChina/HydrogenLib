import asyncio


async def test():
    print("Start")
    await asyncio.sleep(1)
    print("End")
    return 1


def test_wrapper():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    res = loop.run_until_complete(test())
    return res


print(test_wrapper())

