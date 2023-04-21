import modules

class YoutubeRevancedExtended(modules.GithubReleases):
    def __init__(self):
        super().__init__("NoName-exe/revanced-extended", False)
        self.apk_name = "app.rvx.android.youtube.apk"
        
    def filter_asset(self, asset) -> bool:
        return asset['name'].startswith('youtube-revanced-extended')
    

modules = [
    YoutubeRevancedExtended()
]