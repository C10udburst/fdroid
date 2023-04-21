from .classes import DownloadModule
from telethon import TelegramClient
from os import getenv

class Telegram(DownloadModule):
    def __init__(self, channel):
        super().__init__()
        
        self.api_id = int(getenv("TG_ID"))
        self.api_hash = getenv("TG_HASH")
        self.channel = channel
    
    def filter_media(self, asset) -> bool:
        raise NotImplementedError()
        
    async def download(self):
        async with TelegramClient('main', self.api_id, self.api_hash) as client:
            channel = await client.get_input_entity(self.channel)
            async for msg in client.iter_messages(channel, limit=10):
                if not msg.media:
                    continue
                media = msg.media.to_dict()
                if media['document']['mime_type'] != 'application/vnd.android.package-archive':
                    continue
                if not self.filter_media(media):
                    continue
                name = media['document']['attributes'][0]['file_name']
                with open(name, "w+b") as fp:
                    await client.download_media(msg, fp)