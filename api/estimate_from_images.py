import os
import sys
from typing import List
import asyncio
import re

from estimation.internal_posture import update_estimation

user_id_reg = re.compile(r"\d+")
jpg_reg = re.compile(r".jpg")

targets = sys.argv[1:]

if __name__ == "__main__":
    for user_id in os.listdir("images/") if len(targets) <= 0 else targets:
        if not user_id_reg.search(user_id):
            continue
        dir_path = f"images/{user_id}/original"
        file_names = os.listdir(dir_path)
        for file_name in file_names:
            if not jpg_reg.search(file_name):
                continue
            loop = asyncio.get_event_loop()
            loop.run_until_complete(update_estimation(dir_path, file_name))
            print("done")