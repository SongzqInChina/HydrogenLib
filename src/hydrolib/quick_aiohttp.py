import aiohttp


async def aio_get(session, url, *args, **kwargs) -> aiohttp.ClientResponse:
    async with session.get(url, *args, **kwargs) as response:
        return response


async def aio_head(session, url, *args, **kwargs) -> aiohttp.ClientResponse:
    async with session.head(url, *args, **kwargs) as response:
        return response


async def aio_post(session, url, *args, **kwargs) -> aiohttp.ClientResponse:
    async with session.post(url, *args, **kwargs) as response:
        return response


async def aio_request(url, type__='get', *args, **kwargs) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        if type__ == 'head':
            return await aio_head(session, url, *args, **kwargs)
        elif type__ == 'get':
            return await aio_get(session, url, *args, **kwargs)
        elif type__ == 'post':
            return await aio_post(session, url, *args, **kwargs)
        else:
            raise ValueError('Invalid type')
