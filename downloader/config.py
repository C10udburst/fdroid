import modules
from httpx import AsyncClient


class PreviousFdroid(modules.Fdroid):
    def __init__(self):
        super().__init__("https://c10udburst.github.io/fdroid")

    def filter_asset(self, asset) -> bool:
        return True

class Cloudstream(modules.GithubReleases):
    def __init__(self):
        super().__init__("recloudstream/cloudstream", True, limit=2)
        
    def filter_asset(self, asset) -> bool:
        return True

class KiwiBrowser(modules.GithubReleases):
    def __init__(self):
        super().__init__("kiwibrowser/src.next", True)

    def filter_asset(self, asset) -> bool:
        return asset['name'].startswith('com.kiwibrowser.browser-arm64')

class YoutubeRevancedExtended(modules.GithubReleases):
    def __init__(self):
        super().__init__("NoName-exe/revanced-extended", False, limit=3)
        
    def filter_asset(self, asset) -> bool:
        return asset['name'].startswith('youtube-revanced-extended')
    
class Messenger(modules.GithubReleases):
    def __init__(self):
        super().__init__("j-hc/revanced-magisk-module", False, limit=3)
        
    def filter_asset(self, asset) -> bool:
        return asset['name'].startswith('messenger')
    
class YTRevanced(modules.GithubReleases):
    def __init__(self):
        super().__init__("j-hc/revanced-magisk-module", False, limit=3)
        
    def filter_asset(self, asset) -> bool:
        return asset['name'].startswith('youtube-revanced')

# class Spotify(modules.Telegram):
#     def __init__(self):
#         super().__init__("xManagerSupport")

#     def filter_media(self, media) -> bool:
#         name = media['document']['attributes'][0]['file_name']
#         return name.startswith("Spotify") and "Cloned" not in name and "AB" in name

# class Vendetta(modules.MergeSplitModule):
#     def __init__(self):
#         super().__init__("vendetta-arm64")

#     async def find_url(self):
#         async with AsyncClient() as client:
#             r = await client.get("https://discord.k6.tf/index.json")
#             versions = r.json()
#         version = versions['latest']['stable']
#         for name in ["base-360-lspatched", "split_config.arm64_v8a-360-lspatched","split_config.en-360-lspatched","split_config.xxhdpi-360-lspatched"]:
#             yield f"https://discord.k6.tf/{version}/{name}.apk"
            
class Logra(modules.GithubActions):
    def __init__(self):
        super().__init__("logra", "wingio/Logra", "Build Debug", "main", "app-debug")

    def filter_asset(self, path) -> bool:
        return True

class Gloom(modules.GithubActions):
    def __init__(self):
        super().__init__("gloom", "MateriiApps/Gloom", "Build debug APK", "main", "gloom-debug")

    def filter_asset(self, path) -> bool:
        return True

        
class Echo(modules.GithubActions):
    def __init__(self):
        super().__init__("echo", "brahmkshatriya/echo", "nightly", "main", "artifact")

    def filter_asset(self, path) -> bool:
        return True

class ExteraGram(modules.GithubReleases):
    def __init__(self):
        super().__init__("exteraSquad/exteraGram", False)
        
    def filter_asset(self, asset) -> bool:
        return True
    
class LogFox(modules.GithubReleases):
    def __init__(self):
        super().__init__("F0x1d/LogFox", True, limit=2)
        
    def filter_asset(self, asset) -> bool:
        return True

class ClipType(modules.GithubReleases):
    def __init__(self):
        super().__init__("C10udburst/ClipType")
        
    def filter_asset(self, asset) -> bool:
        return True
    
class SpotifyEx(modules.GithubReleases):
    def __init__(self):
        super().__init__("C10udburst/SpotifyEx")
        
    def filter_asset(self, asset) -> bool:
        return True

class MessengerEx(modules.GithubReleases):
    def __init__(self):
        super().__init__("C10udburst/MessengerEx")
        
    def filter_asset(self, asset) -> bool:
        return True

class SwiftBackupPrem(modules.GithubReleases):
    def __init__(self):
        super().__init__("Juby210/SwiftBackupPrem")
        
    def filter_asset(self, asset) -> bool:
        return True

class RecentsGrid(modules.GithubReleases):
    def __init__(self):
        super().__init__("Juby210/RecentsGrid")
        
    def filter_asset(self, asset) -> bool:
        return True

modules = [
    PreviousFdroid(),
    Cloudstream(),
    KiwiBrowser(),
    YoutubeRevancedExtended(),
    YTRevanced(),
    Messenger(),
    #Spotify(),
    Logra(),
    Gloom(),
    Echo(),
    ExteraGram(),
    LogFox(),
    ClipType(),
    SpotifyEx(),
    MessengerEx(),
    SwiftBackupPrem(),
    RecentsGrid()
]
