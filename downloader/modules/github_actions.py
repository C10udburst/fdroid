from .classes import DownloadModule
import asyncio
from collections.abc import Iterator
from glob import glob
import os



class GithubActions(DownloadModule):
    def __init__(self, name: str, repository: str, workflow: str, branch: str, artifact: str):
        self.name = name
        self.artifact = artifact
        self.url = f"https://nightly.link/{repository}/workflows/{workflow}/{branch}/{artifact}"
        
    def filter_asset(self, path) -> bool:
        raise NotImplementedError()
        
    async def download(self):
        print(f"Downloading {self.artifact} from {self.url}")
        os.mkdir(self.name)
        process = await asyncio.create_subprocess_exec("wget", "-nv", self.url, "-O", f"{self.name}/{self.artifact}")
        await process.wait()
        process = await asyncio.create_subprocess_exec("7z", "x", f"{self.name}/{self.artifact}")
        await process.wait()
        for file in glob(f"{self.name}/**.apk"):
            if not self.filter_asset(file):
                continue
            name = file.split("/")[-1]
            process = await asyncio.create_subprocess_exec("mv","-v", file, f"fdroid/repo/{name}")
            await process.wait()
        process = await asyncio.create_subprocess_exec("rm", "-rf", self.name)
        await process.wait()