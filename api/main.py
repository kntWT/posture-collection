from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.user import user
from routers.internal_posture import internal_posture
from routers.external_posture import external_posture
from routers.all_feature import all_feature
import cv2
import asyncio
# from demo_image import calc_neck_dist, calc_head_angle, save_file, remove_file
from typing import Dict, List, Any
import uvicorn

app = FastAPI()
origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:4200",
    "https://localhost:4200",
    "http://localhost.justune.net",
    "https://localhost.justune.net",
    "http://localhost.justune.net:4200",
    "https://localhost.justune.net:4200",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/")
def get_hello_world():
    return {"Hello": "World"}

routers_list = [user, internal_posture, external_posture, all_feature]

for router in routers_list:
    app.include_router(router)

# @app.post("/score")
# async def get_posture_score(file: UploadFile = File(...)) -> Dict[str, float]:
#     file_name: str = save_file(file)
#     img = cv2.imread(file_name)
#     tasks: List[Any] = []
#     tasks.append(calc_neck_dist(img))
#     tasks.append(calc_head_angle(img))
#     [neck_len, head_angle] = await asyncio.gather(*tasks)
#     try:
#         remove_file(file_name)
#     except FileNotFoundError:
#         pass
#     return {
#         "neckLength": neck_len,
#         "headAngle": head_angle,
#     }

# @app.post("/neck")
# async def get_neck_dist(file: UploadFile = File(...)) -> float:
#     file_name: str = save_file(file)
#     img = cv2.imread(file_name)
#     dist: float = await calc_neck_dist(img)
#     try:
#         remove_file(file_name)
#     except FileNotFoundError:
#         pass
#     return dist

# @app.post("/head")
# async def get_head_angle(file: UploadFile = File(...)) -> float:
#     file_name: str = save_file(file)
#     img = cv2.imread(file_name)
#     try:
#         remove_file(file_name)
#     except FileNotFoundError:
#         pass
#     yaw: float = await calc_head_angle(img)
#     return yaw

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # ssl_keyfile="../ssl/localhost.justune.net-key.pem",
        # ssl_certfile="../ssl/localhost.justune.net.cert.pem"
    )