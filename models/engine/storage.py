import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseStorage:
    def __init__(self):
        self.db_username = os.getenv("HL_USERNAME")
        self.db_password = os.getenv("HL_PASSWORD")
        self.db_host = "localhost"
        self.db_port = "3306"
        self.db_name = os.getenv("HL_DATABASE")
        self.mysql_url = (f"mysql+mysqlconnector://"
                          f"{self.db_username}:{self.db_password}@"
                          f"{self.db_host}:{self.db_port}/{self.db_name}")
        self.engine = create_engine(self.mysql_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()
