import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from windowbox.configs.base import DATABASE_CONFIG

_engine = sa.create_engine(DATABASE_CONFIG['URI'], **DATABASE_CONFIG['KWARGS'])
DeclarativeBase = declarative_base(bind=_engine)
session = sa.orm.sessionmaker(bind=_engine, autocommit=False, autoflush=False)()
