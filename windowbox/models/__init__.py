from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from windowbox import app

engine = create_engine(app.config['DATABASE_URI'], **app.config['DATABASE_OPTIONS'])
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

sess = Session()
