import asyncio
import os
import shlex
from collections.abc import Iterator
from datetime import datetime
from typing import Union

# The Nix dev shell sets APKEDITOR_PATH to the packaged binary; the default
# keeps working with a vendored jar.
APKEDITOR_CMD = shlex.split(os.environ.get("APKEDITOR_PATH", "java -jar APKEditor.jar"))


async def run(cmd: list[str]) -> int:
    """Run a command, returning its exit code (callers report failures)."""
    process = await asyncio.create_subprocess_exec(*cmd)
    return await process.wait()


async def download(url: str, dest: str, *, last_updated: datetime | None = None) -> bool:
    """wget a url, treating a failed or empty download as an error."""
    code = await run(["wget", "-nv", "--tries=3", "--retry-connrefused", url, "-O", dest])
    if code != 0 or not os.path.exists(dest) or os.path.getsize(dest) == 0:
        print(f"::warning::{url} could not be downloaded (exit code {code}), skipping")
        if os.path.exists(dest):
            os.remove(dest)
        return False
    if last_updated:
        os.utime(dest, (last_updated.timestamp(), last_updated.timestamp()))
    return True


class DownloadModule():

    """
    This function should return:
    - a string if the url is the direct download link
    - (optional) a datetime object when the file was last updated
    """
    async def find_url(self) -> Iterator[Union[str, tuple[str, datetime]]]:
        raise NotImplementedError()

    @property
    def uniq_prefix(self):
        return self.__class__.__name__.lower()

    async def download(self):
        # download using wget
        async for entry in self.find_url():
            url, last_updated = [None, None]
            if isinstance(entry, tuple):
                url, last_updated = entry
            else:
                url = entry
                last_updated = None
            name = url.split("/")[-1]
            print(f"Downloading {name} from {url}")
            await download(url, f"fdroid/repo/{self.uniq_prefix}-{name}",
                           last_updated=last_updated)


class MergeSplitModule(DownloadModule):

    def __init__(self, name):
        self.name = name
        os.makedirs(name, exist_ok=True)

    async def find_url(self) -> Iterator[str]:
        raise NotImplementedError()

    async def download_splits(self):
        async for url in self.find_url():
            name = url.split("/")[-1]
            print(f"Downloading {name} from {url}")
            await download(url, f"{self.name}/{name}")

    async def download(self):
        # join apks
        await self.download_splits()
        print("merging splits")
        merged = f"{self.name}_merged.apk"
        code = await run([*APKEDITOR_CMD, "m", "-i", self.name, "-clean-meta", "-o", merged])
        if code != 0 or not os.path.exists(merged):
            print(f"::warning::{self.name}: merging split APKs failed (exit code {code})")
            return
        out = f"fdroid/repo/{self.uniq_prefix}-{self.name}.apk"
        code = await run(["apksigner", "sign", "-v",
                          "--ks", "fdroid/keystore.jks",
                          "--ks-key-alias", "repokey",
                          "--ks-pass", "env:KEYSTOREPASS",
                          "--out", out, merged])
        if code != 0:
            print(f"::warning::{self.name}: apksigner failed (exit code {code})")
