import asyncio
from collections.abc import Iterator

class DownloadModule():
    
    async def find_url(self) -> Iterator[str]:
        raise NotImplementedError()
    
    async def download(self):
        # download using wget
        async for url in self.find_url():
            name = url.split("/")[-1]
            print(f"Downloading {name} from {url}")
            await asyncio.create_subprocess_exec("wget", "--show-progress", url, "-O", f"fdroid/repo/{name}")