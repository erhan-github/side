
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path.cwd() / "backend" / "src"))

from side.storage.simple_db import SimplifiedDatabase
from side.services.monolith import generate_monolith

async def main():
    logging.basicConfig(level=logging.INFO)
    db = SimplifiedDatabase()
    path = await generate_monolith(db)
    print(f"Monolith generated at: {path}")

if __name__ == "__main__":
    asyncio.run(main())
