import os
from typing import List
import asyncio

from estimation.internal_posture import update_estimation

file_names: List[str] = os.listdir("images/original")

if __name__ == "__main__":
    for file_name in file_names:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(update_estimation(file_name))
        print("done")