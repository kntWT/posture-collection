from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, DOUBLE, TIMESTAMP, String, BOOLEAN
from sqlalchemy.sql.functions import current_timestamp
from config.db import meta, engine

internal_posture = Table(
    'internal_postures', meta,
    Column('id', Integer, nullable=False, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey("users.id"), nullable=False, server_default="1"),
    Column('file_name', String(255), nullable=False),
    Column('set_id', Integer),
    Column('orientation_alpha', DOUBLE, nullable=False),
    Column('orientation_beta', DOUBLE, nullable=False),
    Column('orientation_gamma', DOUBLE, nullable=False),
    Column('pitch', DOUBLE),
    Column('yaw', DOUBLE),
    Column('roll', DOUBLE),
    Column('nose_x', DOUBLE),
    Column('nose_y', DOUBLE),
    Column('neck_x', DOUBLE),
    Column('neck_y', DOUBLE),
    Column('neck_to_nose', DOUBLE),
    Column('standard_dist', DOUBLE),
    Column('calibrate_flag', BOOLEAN, server_default="False"),
    Column('created_at', TIMESTAMP, server_default=None),
    Column('updated_at', TIMESTAMP, server_default=current_timestamp())
)

meta.create_all(engine)