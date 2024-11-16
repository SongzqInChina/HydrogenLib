import asyncio
import io
import pathlib
import threading
import time
import urllib.parse

import requests
from aiohttp import ClientSession

from ..Class.Auto import AutoRegDict
from ..Doc.Struct import get_called_func
from ..QuickAiohttp import *
from ..ThreadingPlus import start_new_thread

lock = threading.Lock()


def log(*info):
    method = __package__
    thread = threading.current_thread().name
    try:
        task = asyncio.current_task().get_name()
    except RuntimeError:
        task = 'Unknown'
    func = get_called_func(2)
    with lock:
        print(
            f'[{method}][{thread}][{task}][{func}]',
            *info
        )


def _get_header(start, end):
    return {
        'Range': 'bytes={}-{}'.format(start, end)
    }


def assign(total, max_chunks, chunk_min_size=1024):
    if chunk_min_size * max_chunks > total:
        ans = []
        point = 0
        while total:
            ans.append((point, point + chunk_min_size - 1))
            total -= chunk_min_size
            point += chunk_min_size

        return ans

    else:
        chunk_size = total // max_chunks
        ans = [
            (i * chunk_size, (i + 1) * chunk_size - 1) for i in range(max_chunks - 1)
        ]
        ans.append(((max_chunks - 1) * chunk_size, total - 1))  # 防止丢失数据
        return ans


class Data:
    def __init__(self, data=b''):
        self.data = io.BytesIO(data)
        self.size = 0

    def write_right(self, data):
        self.data.seek(0, 2)  # 移动到文件末尾
        self.data.write(data)
        self.size += len(data)

    def read_left(self, size=-1):
        self.data.seek(0)  # 移动到文件开头
        data = self.data.read(size)  # 读取指定大小的数据

        if size == -1:
            self.data.seek(0)  # 如果读取全部数据，重置指针
            self.data.truncate()  # 清空数据
            self.size = 0
        else:
            remaining = self.data.read()  # 读取剩余数据
            self.data.seek(0)  # 移动到文件开头
            self.data.truncate()  # 清空数据
            self.data.write(remaining)  # 写回剩余数据
            self.size -= len(data)

        return data

    def has_data(self):
        return self.size != 0


class File:
    def __init__(self, fp):
        self.fp = fp
        self.fd = open(fp, 'wb')

    def move_write(self, pos, data):
        self.fd.seek(pos)
        self.fd.write(data)


def _get_name(url):
    parsed_data = urllib.parse.urlparse(url)
    path = pathlib.Path(parsed_data.path)
    name = urllib.parse.unquote(path.name)
    return name


async def _get_metadata(url):
    reponse = await aio_request('head', url)
    url = reponse.url
    name = _get_name(url)
    dct = {
        'length': int(reponse.headers['Content-Length']),
        'type': reponse.headers['Content-Type'],
        'name': name,
    }
    return dct


def _sync_get_metadata(url):
    reponse = requests.head(url)
    url = reponse.url
    name = _get_name(url)
    dct = {
        'length': int(reponse.headers['Content-Length']),
        'type': reponse.headers['Content-Type'],
        'name': name,
    }
    return dct


class DownloadCoro:
    @property
    def name(self):
        return self.task.get_name()

    def __init__(self, url, range__, chunk_size=1024):
        self.url = url
        self.start, self.end = range__
        self.size = self.end - self.start + 1
        self.chunk_size = chunk_size
        self.data = Data()
        self.task: asyncio.Task = None

    async def __download(self, session: ClientSession):
        print('get')
        async with session.get(self.url, headers=_get_header(self.start, self.end)) as reponse:
            print('Get reponse')
            async for data in reponse.content.iter_chunked(self.chunk_size):
                self.data.write_right(data)

    async def download_task(self):
        async with aiohttp.ClientSession() as session:
            await self.__download(session)

    def start_download(self):
        if not asyncio.get_event_loop().is_running():
            self.task = asyncio.get_event_loop().create_task(self.download_task())
        else:
            self.task = asyncio.create_task(self.download_task())
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))


class DownloadThread:
    @property
    def name(self):
        return self.thread.name

    def __init__(self, url, target=None, size=0, max_tasks=4):
        self.url = url
        self.size = size
        self.max_tasks = max_tasks
        self.thread: threading.Thread = None
        self.tasks: list[DownloadCoro] = None
        self.target: str = target

    def __thread(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.tasks = []
        file = File(self.target)

        size_assign_list = assign(self.size, self.max_tasks)
        for i, (start, end) in enumerate(size_assign_list):
            coro = DownloadCoro(self.url, (start, end))
            coro.start_download()
            self.tasks.append(coro)

        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0))  # 强制启动事件循环
        dct = AutoRegDict()
        dct.default_value = 0
        while True:
            done = 0
            time.sleep(1)
            for task in self.tasks:
                if task.task.done():
                    done += 1
                elif task.data.has_data():
                    data = task.data.read_left()
                    print('Movewrite:', task.start + dct[task.name])
                    file.move_write(task.start + dct[task.name], data)
                    dct[task.name] += len(data)
                else:
                    print("No data")
            if done == len(self.tasks):
                break

    def start_download(self):
        self.thread = start_new_thread(self.__thread)


class DownloadThreadManager:
    def __init__(self, url, target=None, max_thread=4, thread_max_tasks=4):
        self.url = url
        self.max_thread = max_thread
        self.thread_max_tasks = thread_max_tasks
        self.threads = []  # type: list[DownloadThread]
        self.target = target

    def __merge(self, temps):
        with open(self.target, 'wb') as fp:
            for temp in temps:
                with open(temp, 'rb') as f:
                    fp.write(f.read())

    def start_download(self):
        metadata = _sync_get_metadata(self.url)
        size = metadata['length']
        name = metadata['name']
        if self.target is None:
            self.target = name

        print('Target=', self.target, 'Metadata=', metadata)

        size_list = list(map(lambda x: x[1] - x[0], assign(size, self.max_thread, self.thread_max_tasks)))
        temps = [f'{name}-{i}.temp' for i in range(len(size_list))]
        for i, size in enumerate(size_list):
            thread = DownloadThread(self.url, temps[i], size)
            thread.start_download()
            self.threads.append(thread)

        for thread in self.threads:
            thread.thread.join()

        self.__merge(temps)


__all__ = [
    'DownloadCoro',
    'DownloadThread',
    'DownloadThreadManager',
]
