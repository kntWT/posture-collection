from sqlalchemy import create_engine, MetaData

import os
import time
from dotenv import load_dotenv
from config.env import user, password, db_name

load_dotenv(".env")

host = 'mysql' # dockerのdbのサービス名 

def connect_db(trial: int):
    if trial >= 30:
        print("connection refused")
        return None, None, None
    try:
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
        meta = MetaData()
        conn = engine.connect()
        return engine, meta, conn
    except Exception as e:
        time.sleep(1)
        print(e)
        return connect_db(trial + 1)
    
engine, meta, conn = connect_db(0)