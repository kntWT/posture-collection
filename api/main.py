from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import cv2
from demo_image import calc_neck_dist, calc_head_angle
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def get_hello_world():
    return {"Hello": "World"}

@app.post("/neck")
def get_neck_dist(file: UploadFile = File(...)) -> float:
    file_name: str = f"temp-images/{file.filename.replace(' ','-').replace('/', '-')}"
    with open(file_name,'wb+') as f:
        f.write(file.file.read())
        f.close()
    img = cv2.imread(file_name)
    dist: float = calc_neck_dist(img)
    try:
        os.remove(file_name)
    except FileNotFoundError:
        print(f"the file {file_name} does not exist")
        print(os.listdir("temp-images/"))
    
    return dist

@app.get("/head")
def get_head_angle() -> float:
    return calc_head_angle("")