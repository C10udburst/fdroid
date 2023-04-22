from .classes import DownloadModule
from httpx import AsyncClient


class GithubReleases(DownloadModule):
    def __init__(self, repository: str, prereleases = False, limit = 1):
        super().__init__()
        self.repository = repository
        self.prereleases = prereleases
        self.limit = limit
        
    def filter_asset(self, asset) -> bool:
        raise NotImplementedError()
    
    async def find_url(self) -> Iterator[str]:
        # use github api to find the latest apk dl
        async with AsyncClient() as client:
            r = await client.get(f"https://api.github.com/repos/{self.repository}/releases?per_page={self.limit}")
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
                    yield asset["browser_download_url"]