from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///windowbox.sqlite', convert_unicode=True, echo=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

sess = Session()
