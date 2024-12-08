import httpx
import asyncio
from .classes import DownloadModule

import xml.etree.ElementTree as ET

class Fdroid(DownloadModule):
    
    def __init__(self, base_url):
        self.base_url = base_url

    async def fetch_index(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/repo/index.xml")
            return response.text

    async def find_url(self):
        index_xml = await self.fetch_index()
        root = ET.fromstring(index_xml)
        for application in root.findall(".//application"):
            for package in application.findall(".//package"):
                apkname = package.find("apkname").text
                yield f"{self.base_url}/repo/{apkname}"