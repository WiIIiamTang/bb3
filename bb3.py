import asyncio
import os
from dotenv import load_dotenv

from src.bot.bb3_bot import main
from src.util.constants import (
    BB3_DEV_TOKEN,
    BB3_PREFIX,
)

load_dotenv()

asyncio.run(main(token=os.getenv(BB3_DEV_TOKEN), prefix=os.getenv(BB3_PREFIX)))
