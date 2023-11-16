import requests
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
from typing import Dict, NoReturn
import json
import datetime

API_URL: str = "http://localhost:4201"

def login(trial: int = 0) -> Dict:
    if trial >= 5:
        return {}
    user_name: str = input()
    password: str = input()
    auth = HTTPBasicAuth(user_name, password)
    try:
        res = requests.get(f"{API_URL}/user/auth/", auth=auth)
        res.raise_for_status()
        user = res.json()
        return user
    except HTTPError as e:
        print(e)
        return login(trial + 1)
    
def calibrate(user_id: int, offset: float) -> NoReturn:
    data = json.dumps({"neck_angle_offset": offset})
    try:
        res = requests.put(f"{API_URL}/user/calibration/external-posture/{user_id}", data)
        res.raise_for_status()
        return
    except HTTPError as e:
        print(e)
        return
    finally:
        return

def post(user_id: int, neck_angle: float, torso_angle, now: datetime) -> NoReturn:
    if user_id <= 0:
        return
    data = json.dumps({
        "user_id": user_id,
        "neck_angle": neck_angle,
        "torso_angle": torso_angle,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S.%f")
    })
    try:
        res = requests.post(f"{API_URL}/external-posture/", data)
        res.raise_for_status()
        return
    except HTTPError as e:
        print(e)
        return