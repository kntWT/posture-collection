from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, TIMESTAMP, DOUBLE
from sqlalchemy.sql.functions import current_timestamp
from config.db import meta, engine

user = Table(
    'users', meta,
    Column('id', Integer, nullable=False, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('password', String(255), nullable=False),
    Column('internal_posture_calibration_id', Integer),
    Column('neck_to_nose_standard', DOUBLE),
    Column('neck_angle_offset', DOUBLE, nullable=False, server_default="0"),
    Column('created_at', TIMESTAMP, server_default=current_timestamp())
)

meta.create_all(engine)