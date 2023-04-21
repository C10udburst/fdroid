from abc import abstractmethod
from .classes import DownloadModule
from httpx import AsyncClient

class GithubReleases(DownloadModule):
    def __init__(self, repository: str, prereleases = False):
        super().__init__()
        self.repository = repository
        self.prereleases = prereleases
        
    @abstractmethod
    def filter_asset(self, asset) -> bool:
        pass
    
    async def find_url(self) -> str:
        # use github api to find the latest apk dl
        async with AsyncClient() as client:
            r = await client.get(f"https://api.github.com/repos/{self.repository}/releases")
        releases = r.json()
        if not releases:
            raise Exception("No releases found")
        for release in releases:
            if release["draft"] or (not self.prereleases and release["prerelease"]):
                continue
            for asset in release["assets"]:
                # check if the file type is apk
                if not asset["content_type"] == "application/vnd.android.package-archive":
                    continue
                # check if it matches the filter
                if self.filter_asset(asset):
                    return asset["browser_download_url"]
            raise Exception("No assets found in release")