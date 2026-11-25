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
    failures = [result for result in results if isinstance(result, Exception)]
    for result in failures:
        # a dead upstream should not fail the whole publish, but it should be visible
        print(f"::warning::{type(result).__name__}: {result}")
    if failures:
        print(f"{len(failures)} of {len(results)} download modules failed")

    remove_duplicate_apks("fdroid/repo/")