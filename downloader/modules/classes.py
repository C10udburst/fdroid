import asyncio
from collections.abc import Iterator
import os
from datetime import datetime
from typing import Union, Tuple
from pathlib import Path

class DownloadModule():
    
    """
    This function should return:
    - a string if the url is the direct download link
    - (optional) a datetime object when the file was last updated
    """
    async def find_url(self) -> Iterator[Union[str, Tuple[str, datetime]]]:
        raise NotImplementedError()
    
    @property
    def uniq_prefix(self):
        return self.__class__.__name__.lower()
    
    async def download(self):
        # download using wget
        async for entry in self.find_url():
            url, last_updated = [None, None]
            if isinstance(entry, tuple):
                url, last_updated = entry
            else:
                url = entry
                last_updated = None
            name = url.split("/")[-1]
            print(f"Downloading {name} from {url}")
            process = await asyncio.create_subprocess_exec("wget", "-nv", url, "-O", f"fdroid/repo/{self.uniq_prefix}-{name}")
            await process.wait()
            if last_updated:
                p = Path(f"fdroid/repo/{self.uniq_prefix}-{name}")
                p.touch()
                p.stat().st_ctime = last_updated.timestamp()
                p.stat().st_mtime = last_updated.timestamp()

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
        process = await asyncio.create_subprocess_exec("java", "-jar", "APKEditor.jar", "m", "-i", self.name, "-clean-meta", "-o", f"{self.name}_merged.apk")
        await process.wait()
        process = await asyncio.create_subprocess_exec("apksigner", "sign", "-v", "--ks", "fdroid/keystore.jks", "--ks-key-alias", "repokey", "--ks-pass", "env:KEYSTOREPASS", "--out", f"fdroid/repo/{self.uniq_prefix}-{self.name}.apk", f"{self.name}_merged.apk")
        await process.wait()
