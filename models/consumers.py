from datetime import datetime
from models.engine.storage import DatabaseStorage
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Consumer(Base):
    __tablename__ = 'consumers'

    id = Column(String(60), primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    phone = Column(String(128), nullable=False)
    location = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())


def add_consumer(session, u_id, name, email, phone, location, password):
    """Add a new consumer to the 'consumers' table."""
    new_consumer = Consumer(id=u_id, name=name, email=email, phone=phone,
                          location=location, password=password)
    session.add(new_consumer)
    session.commit()


if __name__ == "__main__":
    # Initialize the DatabaseStorage
    db_storage = DatabaseStorage()

    # Create the 'farmers' table if it doesn't exist
    Base.metadata.create_all(db_storage.engine)

    # Create a session to interact with the database
    session = db_storage.get_session()
