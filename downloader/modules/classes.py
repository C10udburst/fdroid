from abc import ABC, abstractmethod
import asyncio

class DownloadModule(ABC):
    apk_name: str
    
    @abstractmethod
    async def find_url(self) -> str:
        pass
    
    async def download(self):
        # download using wget
        url = await self.find_url()
        print(f"Downloading {self.apk_name} from {url}")
        await asyncio.create_subprocess_exec("wget", "--show-progress", url, "-O", f"fdroid/repo/{self.apk_name}")