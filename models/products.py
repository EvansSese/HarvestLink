# products.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from farmers import Base
from models.engine.storage import DatabaseStorage


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    category = Column(String(128))
    price = Column(Float, nullable=False)
    location = Column(String(128), nullable=False)
    quantity = Column(Integer, nullable=False)
    farmer_id = Column(String(60), ForeignKey('farmers.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    # Define the relationship with the Farmer model
    farmer = relationship('Farmer', back_populates='products')

    def __repr__(self):
        return (f"<Product(id={self.id}, name={self.name}, price={self.price}, "
                f"quantity={self.quantity}, farmer_id={self.farmer_id})>")


if __name__ == "__main__":
    # Initialize the DatabaseStorage
    db_storage = DatabaseStorage()

    # Create the 'farmers' table if it doesn't exist
    Base.metadata.create_all(db_storage.engine)

    # Create a session to interact with the database
    session = db_storage.get_session()
