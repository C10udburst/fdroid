import asyncio
from collections.abc import Iterator
import os

class DownloadModule():
    
    async def find_url(self) -> Iterator[str]:
        raise NotImplementedError()
    
    async def download(self):
        # download using wget
        async for url in self.find_url():
            name = url.split("/")[-1]
            print(f"Downloading {name} from {url}")
            process = await asyncio.create_subprocess_exec("wget", "-nv", url, "-O", f"fdroid/repo/{name}")
            await process.wait()

class MergeSplitModule(DownloadModule):

    def __init__(self, name):
        self.name = name
        os.mkdir(name)

    async def find_url(self) -> Iterator[str]:
        raise NotImplementedError()

    async def download_splits(self):
        async for url in self.find_url():
            name = url.split("/")[-1]
            print(f"Downloading {name} from {url}")
            process = await asyncio.create_subprocess_exec("wget", "-nv", url, "-O", f"{self.name}/{name}")
            await process.wait()

    async def download(self):
        # join apks
        await self.download_splits()
        print("merging splits")
        process = await asyncio.create_subprocess_exec("java", "-jar", "APKEditor.jar", "m", "-i", self.name)
        await process.wait()
