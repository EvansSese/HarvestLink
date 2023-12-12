import uuid

from sqlalchemy.exc import SQLAlchemyError

from models import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
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

    def __repr__(self):
        return f"<Cart(id={self.id}, product_id={self.product_id}, quantity={self.quantity}, consumer_id={self.consumer_id})>"

    @classmethod
    def add_item(cls, session: Session, u_id, product_id, consumer_id,
                 quantity: int, created_at, updated_at) -> bool:
        """
        Add an item to the cart for the specified consumer.
        Returns True if the addition is successful, False otherwise.
        """
        try:
            cart_item = (
                session.query(cls)
                .filter_by(product_id=product_id, consumer_id=consumer_id)
                .first()
            )

            if cart_item:
                # If the item is already in the cart, update the quantity
                cart_item.quantity += quantity
                cart_item.updated_at = datetime.now()
            else:
                # If the item is not in the cart, create a new entry
                new_cart_item = cls(
                    id=u_id,
                    product_id=product_id,
                    quantity=quantity,
                    consumer_id=consumer_id,
                    created_at=created_at,
                    updated_at=updated_at
                )
                session.add(new_cart_item)

            session.commit()
            return True

        except SQLAlchemyError as e:
            print(f"Error adding item to the cart: {e}")

        return False

    @classmethod
    def edit_quantity(cls, session: Session, product_id, consumer_id,
                      new_quantity: int) -> bool:
        try:
            cart_item = (
                session.query(cls)
                .filter_by(product_id=product_id, consumer_id=consumer_id)
                .first()
            )

            if cart_item:
                cart_item.quantity = new_quantity
                session.commit()
                return True

        except SQLAlchemyError as e:
            print(f"Error editing quantity in the cart: {e}")

        return False

    @classmethod
    def delete_item(cls, session: Session, id, consumer_id) -> bool:
        try:
            cart_item = (
                session.query(cls)
                .filter_by(id=id, consumer_id=consumer_id)
                .first()
            )

            if cart_item:
                session.delete(cart_item)
                session.commit()
                return True

        except SQLAlchemyError as e:
            print(f"Error deleting item from the cart: {e}")

        return False


if __name__ == "__main__":
    # Initialize the DatabaseStorage
    db_storage = DatabaseStorage()

    # Create the 'cart' table if it doesn't exist
    Base.metadata.create_all(db_storage.engine)

    # Create a session to interact with the database
    session = db_storage.get_session()
