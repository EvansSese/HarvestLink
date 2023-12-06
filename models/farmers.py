from datetime import datetime
from models import Base
from models.engine.storage import DatabaseStorage
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, Session
from models.products import Product


class Farmer(Base):
    __tablename__ = 'farmers'

    id = Column(String(60), primary_key=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=False)
    phone = Column(String(128), nullable=False)
    location = Column(String(128), nullable=False)
    password = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    def add_farmer(session, u_id, name, email, phone, location, password):
        """Add a new farmer to the 'farmers' table."""
        new_farmer = Farmer(id=u_id, name=name, email=email, phone=phone,
                            location=location, password=password)
        session.add(new_farmer)
        session.commit()

    def get_products(self, session: Session):
        """
        Get the products added by the farmer.
        """
        return session.query(Product).filter_by(farmer_id=self.id).all()


if __name__ == "__main__":
    # Initialize the DatabaseStorage
    db_storage = DatabaseStorage()

    # Create the 'farmers' table if it doesn't exist
    Base.metadata.create_all(db_storage.engine)

    # Create a session to interact with the database
    session = db_storage.get_session()
