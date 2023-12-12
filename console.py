import cmd
import subprocess
from sqlalchemy import inspect
from models.engine.storage import DatabaseStorage


class HarvestLinkConsole(cmd.Cmd):
    db_storage = DatabaseStorage()
    prompt = "(hl) "

    def do_check_farmer(self, arg):
        """Check if the 'farmers' table exists in the MySQL database."""
        inspector = inspect(self.db_storage.engine)
        if 'farmers' in inspector.get_table_names():
            print('ok')
        else:
            print('fail')

    def do_create_farmers_table(self, arg):
        """Run farmers.py to create the 'farmers' table."""
        subprocess.run(["python", "models/farmers.py"])

    def do_create_consumers_table(self, arg):
        """Run consumers.py to create the 'consumers' table."""
        subprocess.run(["python", "models/consumers.py"])

    def do_create_products_table(self, arg):
        """Run products.py to create the 'products' table."""
        subprocess.run(["python", "models/products.py"])

    def do_create_cart_table(self, arg):
        """Run cart.py to create the 'cart' table."""
        subprocess.run(["python", "models/cart.py"])


    def do_create_orders_table(self, arg):
        """Run cart.py to create the 'cart' table."""
        subprocess.run(["python", "models/orders.py"])

    def do_exit(self, arg):
        """Exit the program."""
        print("Exiting.")
        return True


if __name__ == "__main__":
    HarvestLinkConsole().cmdloop()
