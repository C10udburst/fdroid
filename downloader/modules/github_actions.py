from .classes import DownloadModule
import asyncio
from typing import Optional, Tuple
from httpx import AsyncClient
from glob import glob
from datetime import datetime
import os



class GithubActions(DownloadModule):
    def __init__(self, name: str, repository: str, workflow: str, branch: str, artifact: str):
        self.name = name
        self.repository = repository
        self.artifact = artifact
        self.branch = branch
        self.workflow = workflow
        
    def filter_asset(self, path) -> bool:
        raise NotImplementedError()
    
    async def find_url(self) -> Optional[Tuple[str, datetime]]:
        async with AsyncClient() as client:
            r = await client.get(f"https://api.github.com/repos/{self.repository}/actions/workflows")
            workflows = r.json()
            workflow_id = None
            for workflow in workflows['workflows']:
                if workflow['name'] == self.workflow:
                    workflow_id = workflow['id']
                    break
            if not workflow_id:
                return
            r = await client.get(f"https://api.github.com/repos/{self.repository}/actions/workflows/{workflow_id}/runs")
            for run in r.json()['workflow_runs']:
                if run['status'] == 'completed' and run['conclusion'] == 'success' and run['head_branch'] == self.branch:
                    date = datetime.fromisoformat(run['created_at'])
                    return f"https://nightly.link/{self.repository}/actions/runs/{run['id']}/${self.artifact}.zip", date
        
    async def download(self):
        url_date = await self.find_url()
        if not url_date:
            print(f"Artifact {self.artifact} not found in repository {self.repository}")
            return
        url, date = url_date
        print(f"Downloading {self.artifact} from {url}")
        os.mkdir(self.name)
        process = await asyncio.create_subprocess_exec("wget", "-nv", url, "-O", f"{self.name}/{self.artifact}.zip")
        await process.wait()
        process = await asyncio.create_subprocess_exec("7z", "x", f"{self.name}/{self.artifact}.zip", f"-O{self.name}")
        await process.wait()
        for file in glob(f"{self.name}/**.apk"):
            if not self.filter_asset(file):
                continue
            name = file.split("/")[-1]
            process = await asyncio.create_subprocess_exec("mv", "-v", file, f"fdroid/repo/{self.uniq_prefix}-{name}")
            await process.wait()
            os.utime(f"fdroid/repo/{self.uniq_prefix}-{name}", (date.timestamp(), date.timestamp()))
        process = await asyncio.create_subprocess_exec("rm", "-rf", self.name)
        await process.wait()
