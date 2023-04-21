import asyncio

class DownloadModule():
    apk_name: str
    
    async def find_url(self) -> str:
        raise NotImplementedError()
    
    async def download(self):
        # download using wget
        url = await self.find_url()
        print(f"Downloading {self.apk_name} from {url}")
        await asyncio.create_subprocess_exec("wget", "--show-progress", url, "-O", f"fdroid/repo/{self.apk_name}")