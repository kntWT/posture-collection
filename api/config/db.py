from sqlalchemy import create_engine, MetaData

import os
import time
from dotenv import load_dotenv

load_dotenv(".env")

user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
db_name = os.environ.get("MYSQL_DATABASE")
host = 'mysql' # dockerのdbのサービス名 

def connect_db(trial: int):
    if trial >= 10000:
        print("connection refused")
        return None, None, None
    try:
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{db_name}')
        meta = MetaData()
        conn = engine.connect()
        return engine, meta, conn
    except(Exception):
        time.sleep(1)
        return connect_db(trial + 1)
    
engine, meta, conn = connect_db(0)