import uuid

from sqlalchemy.exc import SQLAlchemyError
from models import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session, aliased
from models.engine.storage import DatabaseStorage
from models.products import Product
from models.consumers import Consumer
from models.farmers import Farmer
from models.cart import Cart


class Order(Base):
    __tablename__ = 'orders'

    id = Column(String(60), primary_key=True)
    checkout_id = Column(String(60), nullable=False)
    product_id = Column(String(60), ForeignKey('products.id'), nullable=False)
    consumer_id = Column(String(60), ForeignKey('consumers.id'), nullable=False)
    farmer_id = Column(String(60), ForeignKey('farmers.id'), nullable=False)
    product_name = Column(String(128), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    category = Column(String(128), nullable=False)
    location = Column(String(128), nullable=False)
    status = Column(String(128), default='Pending')
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    # Define relationships with the Cart, Product, Consumer, and Farmer models
    product = relationship('Product', backref='orders')
    consumer = relationship('Consumer', backref='orders')
    farmer = relationship('Farmer', backref='orders')

    def __repr__(self):
        return f"<Order(id={self.id}, cart_id={self.cart_id}, product_id={self.product_id}, " \
               f"consumer_id={self.consumer_id}, farmer_id={self.farmer_id}, " \
               f"product_name={self.product_name}, quantity={self.quantity}, " \
               f"price={self.price}, category={self.category}, location={self.location}, status={self.status})>"

    @classmethod
    def place_order(cls, session: Session, id, consumer_id,
                    consumer_location) -> bool:
        try:
            # Get cart items for the logged-in consumer
            cart_items = (
                session.query(Cart, Product)
                .join(Product, Cart.product_id == Product.id)
                .filter(Cart.consumer_id == consumer_id)
                .all()
            )
            if not cart_items:
                print("Cart is empty. No order placed.")
                return False

            for cart_item in cart_items:
                # Create an Order object for each cart item
                order = cls(
                    id=str(uuid.uuid4()),
                    checkout_id=id,
                    product_id=cart_item.Cart.product_id,
                    consumer_id=cart_item.Cart.consumer_id,
                    farmer_id=cart_item.Product.farmer_id,
                    product_name=cart_item.Product.name,
                    quantity=cart_item.Cart.quantity,
                    price=cart_item.Product.price,
                    category=cart_item.Product.category,
                    location=consumer_location,
                )
                # Add the order to the orders table
                session.add(order)

            # Delete the cart items associated with the logged-in consumer
            session.query(Cart).filter_by(consumer_id=consumer_id).delete()

            session.commit()
            return True

        except SQLAlchemyError as e:
            print(f"Error placing order: {e}")
            session.rollback()
            return False


if __name__ == "__main__":
    # Initialize the DatabaseStorage
    db_storage = DatabaseStorage()

    # Create the 'cart' table if it doesn't exist
    Base.metadata.create_all(db_storage.engine)

    # Create a session to interact with the database
    session = db_storage.get_session()
