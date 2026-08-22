from .authentication_controller import AuthenticationController
from sqlalchemy.orm import Session
from models import Customer, Contact, PhoneNumber, Collaborator
from views import CustomerScreen, CreateCustomerScreen, UpdateCustomerScreen

class CustomerController:

    def __init__(self, epic_events_app, session):
        self.session: Session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None
        self.authentication_controller = AuthenticationController(
            self.epic_events_app,
            self.session
        )

    def start(self, on_back=None):
        self.on_back_callback = on_back
        customers = self.get_all_customers(self.session)
        customers_screen = CustomerScreen(customers)
        self.epic_events_app.push_screen(customers_screen, callback=self.handle_user_choice)

    def handle_user_choice(self, user_choice):
        """Callback when user chooses from customer menu"""
        match user_choice:
            case 'display_all_customers':
                all_customers = self.get_all_customers(self.session)
                all_customers_screen = CustomerScreen(all_customers)
                self.epic_events_app.push_screen(all_customers_screen, callback=self.handle_user_choice)
            # case 'display_own_customers':
                # user_id = self.get_user_id()
                # own_customers = self.get_customers_by_sales_rep_id(self.session, user_id=4)
                # own_customers_screen = CustomerScreen(own_customers)
                # self.epic_events_app.push_screen(own_customers_screen, callback=self.handle_user_choice)
            # case 'display_customers_without_rep':
                # customers_without_rep = self.get_customers_without_sales_rep(self.session)
                # customers_without_rep_screen = CustomerScreen(customers_without_rep)
                # self.epic_events_app.push_screen(customers_without_rep_screen, callback=self.handle_user_choice)
            case 'create_customer':
                self.epic_events_app.notify('Create Customer', severity='warning')
                create_customer_screen = CreateCustomerScreen()
                self.epic_events_app.push_screen(create_customer_screen, callback=self.create_customer)
            case ('update_customer', customer_id):
                customer_to_update = self.load_customer_data_for_update(customer_id)
                update_customer_screen = UpdateCustomerScreen(customer_to_update)
                self.epic_events_app.push_screen(update_customer_screen, callback=self.update_customer)
            case 'back':
                if self.on_back_callback:
                    self.on_back_callback()
                return
            case 'quit':
                self.epic_events_app.exit()

    def handle_update_customer_(self):
        """
        """

    def get_all_customers(self, session: Session) -> list[Customer]:
        """
        Returns all customers from the database.
        """
        return session.query(Customer).all()

    def load_customer_data_for_update(self, customer_id: int):
        """
        """
        customer = self.session.query(Customer).filter(Customer.id == customer_id).first()
        # for contact in customer.contacts:

        return {
            'customer_id': customer.id,
            "customer_first_name": customer.first_name,
            "customer_last_name": customer.last_name,
            "company_name": customer.company_name,
            # "contacts": contacts, mettre en place un select parmis les contacts existants
        }

    def get_all_contacts(self, session: Session) -> list[Contact]:
            """
            Returns all customers from the database.
            """
            return session.query(Contact).all()

    def get_customers_by_sales_rep_id(self, user_id: int) -> list[Customer]:
        """
        Returns all customers where sales_representative_id matches the given user_id.
        """
        return self.session.query(Customer).filter(Customer.sales_representative_id == user_id).all()

    def get_customers_without_sales_rep(self) -> list[Customer]:
        """
        Returns all customers that have no sales_representative_id assigned.
        """
        return self.session.query(Customer).filter(Customer.sales_representative_id.is_(None)).all()

    def create_customer(self, new_customer_data):
        """
        """
        # If creation was cancelled
        if not new_customer_data:
            self.epic_events_app.notify('Customer creation cancelled', severity='warning')
            self.start(self.on_back_callback)
            return

        # Else, transform raw data (dict) from submitted form
        
        # Contact first
        contact = Contact(
            first_name=new_customer_data['contact_first_name'],
            last_name=new_customer_data['contact_last_name'],
            email=new_customer_data['email']
        )
        self.session.add(contact)

        # Phone number
        phone_number = PhoneNumber(
            number=new_customer_data['phone_number'],
            contact=contact
        )
        self.session.add(phone_number)

        # Customer
        customer = Customer(
            last_name=new_customer_data['customer_last_name'],
            first_name=new_customer_data['customer_first_name'],
            company_name=new_customer_data['company_name'],
            sales_representative=self.authentication_controller.get_user_info(),
        )
        customer.contacts.append(contact)

        self.session.add(customer)
        self.session.commit()
        self.epic_events_app.notify('Customer successfully added', severity='success')
        self.start(self.on_back_callback)

    def update_customer(self, updated_customer_data):
        """
        """
        if not updated_customer_data:
            self.epic_events_app.notify('Customer update cancelled', severity='warning')
            self.start(self.on_back_callback)
            return

        self.session.query(Customer).filter(Customer.id == updated_customer_data['id']).update(updated_customer_data)

        self.session.commit()
        self.epic_events_app.notify('Customer successfully updated', severity='success')
        self.start(self.on_back_callback)
        
    def delete_customer(self):
        pass