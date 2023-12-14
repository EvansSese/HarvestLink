import uuid

from sqlalchemy.exc import SQLAlchemyError
from models import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session, aliased, joinedload
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
        return f"<Order(id={self.id}, checkout_id={self.checkout_id}, product_id={self.product_id}, " \
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

    @classmethod
    def view_orders(cls, session: Session, consumer_id: int):
        try:
            # Get the authenticated consumer's orders with product and farmer information
            orders = (
                session.query(cls)
                .filter_by(consumer_id=consumer_id)
                .options(joinedload(cls.product), joinedload(cls.farmer))
                .all()
            )

            return orders

        except SQLAlchemyError as e:
            print(f"Error fetching orders: {e}")
            print(e)
            return []

    @classmethod
    def get_orders(cls, session: Session, farmer_id):
        try:
            # Get orders associated with the logged-in farmer
            orders = (
                session.query(cls)
                .filter_by(farmer_id=farmer_id)
                .all()
            )
            print(orders)
            return orders

        except SQLAlchemyError as e:
            print(f"Error fetching orders: {e}")
            return []

    @classmethod
    def accept_order(cls, session: Session, order_id, farmer_id):
        try:
            # Get the order by ID
            order = session.query(cls).get(order_id)

            # Check if the order exists and belongs to the provided farmer
            if order and order.farmer_id == farmer_id:
                # Change the status of the order to "Accepted"
                order.status = 'Accepted'
                session.commit()
                return True
            else:
                raise ValueError(
                    "Order not found or does not belong to the provided farmer")

        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Error accepting order: {e}")

    @classmethod
    def decline_order(cls, session: Session, order_id, farmer_id):
        try:
            # Get the order by ID
            order = session.query(cls).get(order_id)

            # Check if the order exists and belongs to the provided farmer
            if order and order.farmer_id == farmer_id:
                # Change the status of the order to "Declined"
                order.status = 'Declined'
                session.commit()
                return True
            else:
                raise ValueError(
                    "Order not found or does not belong to the provided farmer")

        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Error declining order: {e}")

    @classmethod
    def deliver_order(cls, session: Session, order_id, farmer_id):
        try:
            # Get the order by ID
            order = session.query(cls).get(order_id)

            # Check if the order exists and belongs to the provided farmer
            if order and order.farmer_id == farmer_id:
                # Change the status of the order to "Declined"
                order.status = 'Delivered'
                session.commit()
                return True
            else:
                raise ValueError(
                    "Order not found or does not belong to the provided farmer")

        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError(f"Error delivering order: {e}")


if __name__ == "__main__":
    # Initialize the DatabaseStorage
    db_storage = DatabaseStorage()

    # Create the 'cart' table if it doesn't exist
    Base.metadata.create_all(db_storage.engine)

    # Create a session to interact with the database
    session = db_storage.get_session()
