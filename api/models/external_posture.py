from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, DOUBLE, TIMESTAMP
from sqlalchemy.sql.functions import current_timestamp
from config.db import meta, engine

external_posture = Table(
    'external_postures', meta,
    Column('id', Integer, nullable=False, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey("users.id"), nullable=False, server_default=1),
    Column('internal_posture_id', Integer, ForeignKey("internal_postures.id")),
    Column('neck_angle', DOUBLE, nullable=False),
    Column('created_at', TIMESTAMP, server_default=current_timestamp())
)

meta.create_all(engine)