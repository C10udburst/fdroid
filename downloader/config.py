import modules
from httpx import AsyncClient


class Cloudstream(modules.GithubReleases):
    def __init__(self):
        super().__init__("recloudstream/cloudstream", True, limit=2)
        
    def filter_asset(self, asset) -> bool:
        return True

class YoutubeRevancedExtended(modules.GithubReleases):
    def __init__(self):
        super().__init__("NoName-exe/revanced-extended", False, limit=2)
        
    def filter_asset(self, asset) -> bool:
        return asset['name'].startswith('youtube-revanced-extended')
    
class Messenger(modules.GithubReleases):
    def __init__(self):
        super().__init__("c10udburst-actions/revanced-builder", False)
        
    def filter_asset(self, asset) -> bool:
        return asset['name'].startswith('messenger')

class Spotify(modules.Telegram):
    def __init__(self):
        super().__init__("xManagerSupport")

    def filter_media(self, media) -> bool:
        name = media['document']['attributes'][0]['file_name']
        return name.startswith("Spotify") and "Cloned" not in name and "AB" in name

class Vendetta(modules.MergeSplitModule):
    def __init__(self):
        super().__init__("vendetta-arm64")

    async def find_url(self):
        async with AsyncClient() as client:
            r = await client.get("https://discord.k6.tf/index.json")
            versions = r.json()
        version = versions['latest']['stable']
        for name in ["base-360-lspatched", "split_config.arm64_v8a-360-lspatched","split_config.en-360-lspatched","split_config.xxhdpi-360-lspatched"]:
            yield f"https://discord.k6.tf/{version}/{name}.apk"
            
class Logra(modules.GithubActions):
    def __init__(self):
        super().__init__("logra", "wingio/Logra", "build-debug", "main", "app-debug.zip")

    def filter_asset(self, path) -> bool:
        return True

modules = [
    Cloudstream(),
    YoutubeRevancedExtended(),
    Messenger(),
    Spotify(),
    Vendetta(),
    Logra()
]
