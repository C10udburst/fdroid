import modules

class YoutubeRevancedExtended(modules.GithubReleases):
    def __init__(self):
        super().__init__("NoName-exe/revanced-extended", False)
        
    def filter_asset(self, asset) -> bool:
        return asset['name'].startswith('youtube-revanced-extended')

class XManager(modules.Telegram):
    def __init__(self):
        super().__init__("xManagerSupport")

    def filter_media(self, media) -> bool:
        name = media['document']['attributes'][0]['file_name']
        return name.startswith("Spotify") and "Cloned" not in name


modules = [
    YoutubeRevancedExtended(),
    XManager() # Spotify, Spotify Lite
]