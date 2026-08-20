from sqlalchemy.orm import Session
from models import Customer
from views import CustomerScreen, CreateCustomerScreen

class CustomerController:

    def __init__(self, epic_events_app, session):
        self.session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None

    def start(self, on_back=None):
        self.on_back_callback = on_back
        customers = self.get_all_customers(self.session)
        customers_screen = CustomerScreen(customers)
        self.epic_events_app.push_screen(customers_screen, callback=self.handle_user_choice)

    def handle_user_choice(self, user_choice: str):
        """Callback when user chooses from customer menu"""
        match user_choice:
            case 'display_all_customers':
                all_customers = self.get_all_customers(self.session)
                all_customers_screen = CustomerScreen(all_customers)
                self.epic_events_app.push_screen(all_customers_screen, callback=self.handle_user_choice)
            case 'display_own_customers':
                # user_id = self.get_user_id()
                own_customers = self.get_customers_by_sales_rep_id(self.session, user_id=4)
                own_customers_screen = CustomerScreen(own_customers)
                self.epic_events_app.push_screen(own_customers_screen, callback=self.handle_user_choice)
            case 'display_customers_without_rep':
                customers_without_rep = self.get_customers_without_sales_rep(self.session)
                customers_without_rep_screen = CustomerScreen(customers_without_rep)
                self.epic_events_app.push_screen(customers_without_rep_screen, callback=self.handle_user_choice)
            case 'create_customer':
                self.epic_events_app.notify('Create Customer', severity='error')
                create_customer_screen = CreateCustomerScreen()
                self.epic_events_app.push_screen(create_customer_screen, callback=self.handle_user_choice)
            case 'back':
                if self.on_back_callback:
                    self.on_back_callback()
            case 'quit':
                self.epic_events_app.exit()

    def get_all_customers(self, session: Session) -> list[Customer]:
        """
        Returns all customers from the database.
        """
        return session.query(Customer).all()

    def get_customers_by_sales_rep_id(self, session: Session, user_id: int) -> list[Customer]:
        """
        Returns all customers where sales_representative_id matches the given user_id.
        """
        return session.query(Customer).filter(Customer.sales_representative_id == user_id).all()

    def get_customers_without_sales_rep(self, session: Session) -> list[Customer]:
        """
        Returns all customers that have no sales_representative_id assigned.
        """
        return session.query(Customer).filter(Customer.sales_representative_id.is_(None)).all()

    def create_customer(self):
        pass

    def update_customer(self):
        pass

    def delete_customer(self):
        pass