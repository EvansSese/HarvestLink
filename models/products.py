from sqlalchemy.exc import SQLAlchemyError
from models import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
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
        return (f"<Product(id={self.id}, name={self.name}, "
                f"category={self.category}, price={self.price},"
                f"quantity={self.quantity}, farmer_id={self.farmer_id})>")

    def add_product(session, u_id, name, category, price, location, quantity,
                    farmer_id, created_at, updated_at):
        """Add a new farmer to the 'farmers' table."""
        new_product = Product(id=u_id, name=name, category=category,
                              price=price,
                              location=location, quantity=quantity,
                              farmer_id=farmer_id, created_at=created_at,
                              updated_at=updated_at)
        session.add(new_product)
        session.commit()

    @classmethod
    def update_product(cls, session: Session, product_id, farmer_id,
                       new_data: dict) -> bool:
        """
        Update a product with the given ID belonging to the specified farmer.
        Returns True if the update is successful, False otherwise.
        """
        try:
            product_to_update = (
                session.query(cls)
                .filter_by(id=product_id, farmer_id=farmer_id)
                .first()
            )

            if product_to_update:
                # Update product attributes with new data
                for key, value in new_data.items():
                    setattr(product_to_update, key, value)

                # Update the 'updated_at' timestamp
                product_to_update.updated_at = datetime.now()

                session.commit()
                return True

        except SQLAlchemyError as e:
            print(f"Error updating product: {e}")

        return False

    @classmethod
    def delete_product(cls, session: Session, product_id, farmer_id) -> bool:
        """
        Delete a product with the given ID belonging to the specified farmer.
        Returns True if the deletion is successful, False otherwise.
        """
        try:
            product_to_delete = (
                session.query(cls)
                .filter_by(id=product_id, farmer_id=farmer_id)
                .first()
            )

            if product_to_delete:
                session.delete(product_to_delete)
                session.commit()
                return True

        except SQLAlchemyError as e:
            print(f"Error deleting product: {e}")

        return False


if __name__ == "__main__":
    # Initialize the DatabaseStorage
    db_storage = DatabaseStorage()

    # Create the 'products' table if it doesn't exist
    Base.metadata.create_all(db_storage.engine)

    # Create a session to interact with the database
    session = db_storage.get_session()
