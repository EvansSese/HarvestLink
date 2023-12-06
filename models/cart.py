from models import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.engine.storage import DatabaseStorage
from models.products import Product
from models.consumers import Consumer


class Cart(Base):
    __tablename__ = 'cart'

    id = Column(String(60), primary_key=True)
    quantity = Column(Integer, nullable=False)
    product_id = Column(String(60), ForeignKey('products.id'), nullable=False)
    consumer_id = Column(String(60), ForeignKey('consumers.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    # Define the relationship with the Farmer model
    product = relationship('Product', backref='cart')
    consumer = relationship('Consumer', backref='cart')


if __name__ == "__main__":
    # Initialize the DatabaseStorage
    db_storage = DatabaseStorage()

    # Create the 'cart' table if it doesn't exist
    Base.metadata.create_all(db_storage.engine)

    # Create a session to interact with the database
    session = db_storage.get_session()
