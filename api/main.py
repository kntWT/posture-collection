from fastapi import FastAPI, File, UploadFile
from demo_image import calc_neck_dist, calc_head_angle
app = FastAPI()

@app.get("/")
def get_hello_world():
    return {"Hello": "World"}

@app.get("/dist")
def get_neck_dist():
    return calc_neck_dist("")

@app.get("/head")
def get_head_angle():
    return calc_head_angle("")