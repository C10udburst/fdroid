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
            await asyncio.create_subprocess_exec("wget", "--show-progress", url, "-O", f"fdroid/repo/{name}")

class MergeSplitModule(DownloadModule):

    def __init__(self, name):
        self.name = name
        os.mkdirs(name, exists_ok=True)

    async def find_url(self) -> Iterator[str]:
        raise NotImplementedError()

    async def download_splits(self):
        async for url in self.find_url():
            name = url.split("/")[-1]
            print(f"Downloading {name} from {url}")
            await asyncio.create_subprocess_exec("wget", "--show-progress", url, "-O", f"{self.name}/{name}")

    async def download(self):
        # join apks
        await self.download_splits()
        print("merging splits")
        await asyncio.create_subprocess_exec("java", "-jar", "APKEditor.jar", "m", "-i", self.name)
        await asyncio.create_subprocess_exec("jarsigner", "-verbose","-sigalg","SHA1withRSA",
            "-digestalg","SHA1","-keystore", "fdroid/keystore.jks",f"{self.name}_merged.apk", "repokey", "-storepass", os.getenv("KEYSTOREPASS"))
        await asyncio.create_subprocess_exec("zipalign", "-v", "4", f"{self.name}_merged.apk", f"fdroid/repo/{self.name}")