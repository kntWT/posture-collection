from typing import Any, NoReturn
import os
import json
from pydantic import BaseModel

original_image_dir: str = os.environ.get("ORIGINAL_IMAGE_DIR")

def save_file(file) -> str:
    file_name: str = f"{original_image_dir}/{file.filename}"
    with open(file_name,'wb+') as f:
        f.write(file.file.read())
        f.close()
    return file_name

def remove_file(file_name: str) -> NoReturn:
    try:
        os.remove(file_name)
    except FileNotFoundError:
        print(f"the file {file_name} does not exist")
    return


class JsonParser:
    def __init__(self, model: BaseModel):
        self.model = model

    def __call__(self, json_obj: json):
        dict_obj = json.loads(json_obj)
        return self.model(**dict_obj)