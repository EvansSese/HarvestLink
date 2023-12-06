# products.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.farmers import Base
from models.engine.storage import DatabaseStorage


class Product(Base):
    __tablename__ = 'products'

    id = Column(String(60), primary_key=True)
    name = Column(String(128), nullable=False)
    category = Column(String(128))
    price = Column(Float, nullable=False)
    location = Column(String(128), nullable=False)
    quantity = Column(Integer, nullable=False)
    farmer_id = Column(String(60), ForeignKey('farmers.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    # Define the relationship with the Farmer model
    farmer = relationship('Farmer', backref='products')

    def __repr__(self):
        return (f"<Product(id={self.id}, name={self.name}, price={self.price}, "
                f"quantity={self.quantity}, farmer_id={self.farmer_id})>")


def add_product(session, u_id, name, category, price, location, quantity,
                farmer_id, created_at, updated_at):
    """Add a new farmer to the 'farmers' table."""
    new_product = Product(id=u_id, name=name, category=category, price=price,
                          location=location, quantity=quantity,
                          farmer_id=farmer_id,created_at=created_at,
                          updated_at=updated_at)
    session.add(new_product)
    session.commit()


if __name__ == "__main__":
    # Initialize the DatabaseStorage
    db_storage = DatabaseStorage()

    # Create the 'farmers' table if it doesn't exist
    Base.metadata.create_all(db_storage.engine)

    # Create a session to interact with the database
    session = db_storage.get_session()
