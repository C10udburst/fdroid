import asyncio
import os
from typing import Optional, Tuple
from httpx import AsyncClient
from glob import glob
from datetime import datetime
import os

from .classes import DownloadModule, download, run


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
        async with AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(f"https://api.github.com/repos/{self.repository}/actions/workflows")
            workflows = r.json()
            workflow_id = None
            for workflow in workflows.get('workflows', []):
                if workflow['name'] == self.workflow:
                    workflow_id = workflow['id']
                    break
            if not workflow_id:
                return
            r = await client.get(f"https://api.github.com/repos/{self.repository}/actions/workflows/{workflow_id}/runs")
            for run_ in r.json().get('workflow_runs', []):
                if run_['status'] == 'completed' and run_['conclusion'] == 'success' and run_['head_branch'] == self.branch:
                    date = datetime.fromisoformat(run_['created_at'].replace('Z', '+00:00'))
                    return f"https://nightly.link/{self.repository}/actions/runs/{run_['id']}/{self.artifact}.zip", date

    async def download(self):
        url_date = await self.find_url()
        if not url_date:
            print(f"::warning::Artifact {self.artifact} not found in repository {self.repository}")
            return
        url, date = url_date
        print(f"Downloading {self.artifact} from {url}")
        os.makedirs(self.name, exist_ok=True)
        archive = f"{self.name}/{self.artifact}.zip"
        # nightly.link answers 404 once the artifact expires; don't feed that to 7z
        if not await download(url, archive):
            return
        code = await run(["7z", "x", archive, f"-O{self.name}"])
        if code != 0:
            print(f"::warning::{url}: extracting {archive} failed (exit code {code})")
            return
        for file in glob(f"{self.name}/**.apk"):
            if not self.filter_asset(file):
                continue
            name = file.split("/")[-1]
            dest = f"fdroid/repo/{self.uniq_prefix}-{name}"
            code = await run(["mv", "-v", file, dest])
            if code != 0:
                print(f"::warning::moving {file} to {dest} failed (exit code {code})")
                continue
            os.utime(dest, (date.timestamp(), date.timestamp()))
        await run(["rm", "-rf", self.name])
