from config import modules
import asyncio

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