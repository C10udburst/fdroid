from config import modules
import asyncio
from cleaner import remove_duplicate_apks

async def run():
    tasks = []
    for module in modules:
        tasks.append(asyncio.create_task(module.download()))
    return await asyncio.gather(*tasks, return_exceptions=True)
    
if __name__ == "__main__":
    results = asyncio.run(run())
    for result in results:
        if isinstance(result, Exception):
            print(result)

    remove_duplicate_apks("fdroid/repo/")