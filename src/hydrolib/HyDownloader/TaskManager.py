import asyncio


class TaskManager:
    def __init__(self, loop, max_length=16):
        self.loop = loop
        self.tasks = set()  # 使用集合来存储任务，避免重复
        self.finished = set()
        self.max_length = max_length

    async def task(self, coro):
        await coro
        self.tasks.remove(asyncio.current_task())
        self.finished.add(asyncio.current_task())

    async def submit(self, coro):
        if len(self.tasks) >= self.max_length:
            while self.max_length <= len(self.tasks):
                await asyncio.sleep(0.5)
            return await self.submit(coro)
        else:
            task = asyncio.create_task(self.task(coro))
            self.tasks.add(task)
            return task

    async def cancel(self):
        for task in self.tasks:
            task.cancel()

    async def wait_all(self):
        await asyncio.gather(*self.tasks)
