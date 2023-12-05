import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseStorage:
    def __init__(self):
        self.db_username = os.getenv("HL_USERNAME")
        self.db_password = os.getenv("HL_PASSWORD")
        self.db_host = os.getenv("HL_HOST")
        self.db_port = os.getenv("HL_PORT")
        self.db_name = os.getenv("HL_DATABASE")
        self.mysql_url = (f"mysql+mysqlconnector://"
                          f"{self.db_username}:{self.db_password}@"
                          f"{self.db_host}:{self.db_port}/{self.db_name}")
        self.engine = create_engine(self.mysql_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()
