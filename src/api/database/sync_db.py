from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.database.urls import SQLALCHEMY_DATABASE_URL
from src.api.v1.models import Base

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    # echo=True,
    # echo=settings.db_echo_log,
)

Session = sessionmaker(engine)


def get_db(session=Session):
    db = session()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)


def drop_tables():
    Base.metadata.drop_all(bind=engine)
