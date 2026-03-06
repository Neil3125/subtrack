import asyncio
from fastapi import FastAPI
from app.main import lifespan

async def run_test():
    app = FastAPI()
    async with lifespan(app):
        print("Lifespan setup finished successfully!")

if __name__ == "__main__":
    asyncio.run(run_test())
