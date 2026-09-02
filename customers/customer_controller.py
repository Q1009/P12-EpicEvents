from datetime import UTC, datetime

from sqlalchemy.orm import Session, joinedload

from authentication.authentication_controller import (
    AuthenticationController,
)
from customers.customer_model import (
    Contact,
    Customer,
    PhoneNumber,
)
from customers.customer_view import (
    CreateContactScreen,
    CreateCustomerScreen,
    CustomerScreen,
    UpdateContactScreen,
    UpdateCustomerScreen,
)


class CustomerController:
    def __init__(self, epic_events_app, session):
        self.session: Session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None
        self.authentication_controller = AuthenticationController(
            self.epic_events_app, self.session
        )

    def start(self, customer_id=None, on_back=None):
        self.on_back_callback = on_back
        customers = self.get_all_customers()
        customers_screen = CustomerScreen(customers, customer_id)
        self.epic_events_app.push_screen(
            customers_screen, callback=self.handle_user_choice
        )

    def handle_user_choice(self, user_choice):
        """Callback when user chooses from customer menu"""
        match user_choice:
            case "create_customer":
                create_customer_screen = CreateCustomerScreen()
                self.epic_events_app.push_screen(
                    create_customer_screen, callback=self.create_customer
                )
            case ("update_customer", customer_id):
                customer_to_update = self.load_customer_data_for_update(
                    customer_id
                )
                contacts = self.get_all_contacts()
                update_customer_screen = UpdateCustomerScreen(
                    customer_to_update, contacts
                )
                self.epic_events_app.push_screen(
                    update_customer_screen, callback=self.update_customer
                )
            case "create_contact":
                create_contact_screen = CreateContactScreen()
                self.epic_events_app.push_screen(
                    create_contact_screen, callback=self.create_contact
                )
            case ("update_contact", contact_id):
                contact_to_update = self.load_contact_data_for_update(
                    contact_id
                )
                update_contact_screen = UpdateContactScreen(
                    contact_to_update
                )
                self.epic_events_app.push_screen(
                    update_contact_screen, callback=self.update_contact
                )
            case "back":
                if self.on_back_callback:
                    self.on_back_callback()
                return
            case "quit":
                self.epic_events_app.exit()

    def get_all_customers(self) -> list[Customer]:
        """
        Returns all customers from the database.
        """
        return (
            self.session.query(Customer)
            .options(
                joinedload(Customer.contacts).joinedload(
                    Contact.phone_numbers
                ),
                joinedload(Customer.sales_representative),
            )
            .all()
        )

    def load_customer_data_for_update(self, customer_id: int):
        """ """
        customer = (
            self.session.query(Customer)
            .filter(Customer.id == customer_id)
            .first()
        )

        return {
            "customer_id": customer.id,
            "customer_first_name": customer.first_name,
            "customer_last_name": customer.last_name,
            "company_name": customer.company_name,
            "customer_contacts_ids": [
                contact.id for contact in customer.contacts
            ],
        }

    def load_contact_data_for_update(self, contact_id: int):
        """
        Load contact data for the update form.
        """
        contact = (
            self.session.query(Contact)
            .options(joinedload(Contact.phone_numbers))
            .filter(Contact.id == contact_id)
            .first()
        )

        return {
            "contact_id": contact.id,
            "contact_first_name": contact.first_name,
            "contact_last_name": contact.last_name,
            "email": contact.email,
            "phone_numbers": [
                phone.number for phone in contact.phone_numbers
            ],
        }

    def get_all_contacts(self) -> list[Contact]:
        """
        Returns all contacts from the database.
        """
        return self.session.query(Contact).all()

    def get_customers_by_sales_rep_id(
        self, user_id: int
    ) -> list[Customer]:
        """
        Returns all customers where sales_representative_id matches the given user_id.
        """
        return (
            self.session.query(Customer)
            .filter(Customer.sales_representative_id == user_id)
            .all()
        )

    def get_customers_without_sales_rep(self) -> list[Customer]:
        """
        Returns all customers that have no sales_representative_id assigned.
        """
        return (
            self.session.query(Customer)
            .filter(Customer.sales_representative_id.is_(None))
            .all()
        )

    def create_customer(self, new_customer_data):
        """ """
        # If creation was cancelled
        if not new_customer_data:
            self.epic_events_app.notify(
                "Customer creation cancelled", severity="warning"
            )
            self.start(on_back=self.on_back_callback)
            return

        # Else, transform raw data (dict) from submitted form

        # Contact first
        contact = Contact(
            first_name=new_customer_data["contact_first_name"],
            last_name=new_customer_data["contact_last_name"],
            email=new_customer_data["email"],
        )
        self.session.add(contact)

        # Phone number
        phone_number = PhoneNumber(
            number=new_customer_data["phone_number"], contact=contact
        )
        self.session.add(phone_number)

        # Customer
        customer = Customer(
            last_name=new_customer_data["customer_last_name"],
            first_name=new_customer_data["customer_first_name"],
            company_name=new_customer_data["company_name"],
            sales_representative=self.authentication_controller.get_user_info(),
        )
        customer.contacts.append(contact)

        self.session.add(customer)
        self.session.commit()
        self.epic_events_app.notify(
            "Customer successfully created", severity="information"
        )
        self.start(on_back=self.on_back_callback)

    def update_customer(self, updated_customer_data):
        """ """
        if not updated_customer_data:
            self.epic_events_app.notify(
                "Customer update cancelled", severity="warning"
            )
            self.start(on_back=self.on_back_callback)
            return

        self.session.query(Customer).filter(
            Customer.id == updated_customer_data["id"]
        ).update(
            {
                "first_name": updated_customer_data["first_name"],
                "last_name": updated_customer_data["last_name"],
                "company_name": updated_customer_data["company_name"],
                "updated_at": datetime.now(UTC),
            }
        )

        customer = (
            self.session.query(Customer)
            .filter(Customer.id == updated_customer_data["id"])
            .first()
        )
        if customer:
            # Get selected contacts from update
            selected_contacts = (
                self.session.query(Contact)
                .filter(
                    Contact.id.in_(updated_customer_data["contact_ids"])
                )
                .all()
            )
            customer.contacts = selected_contacts

        self.session.commit()
        self.epic_events_app.notify(
            "Customer successfully updated", severity="information"
        )
        self.start(on_back=self.on_back_callback)

    def create_contact(self, new_contact_data):
        """ """
        # If creation was cancelled
        if not new_contact_data:
            self.epic_events_app.notify(
                "Contact creation cancelled", severity="warning"
            )
            self.start(on_back=self.on_back_callback)
            return

        # Else, transform raw data (dict) from submitted form
        contact = Contact(
            first_name=new_contact_data["contact_first_name"],
            last_name=new_contact_data["contact_last_name"],
            email=new_contact_data["email"],
        )
        self.session.add(contact)

        # Phone numbers
        for phone_number in new_contact_data["phone_numbers"]:
            new_phone_number = PhoneNumber(
                number=phone_number, contact=contact
            )
            self.session.add(new_phone_number)

        self.session.commit()
        self.epic_events_app.notify(
            "Contact successfully created", severity="information"
        )
        self.start(on_back=self.on_back_callback)

    def update_contact(self, updated_contact_data):
        """
        Update contact and its phone numbers.
        """
        if not updated_contact_data:
            self.epic_events_app.notify(
                "Contact update cancelled", severity="warning"
            )
            self.start(on_back=self.on_back_callback)
            return

        contact_id = updated_contact_data["id"]
        self.session.query(Contact).filter(
            Contact.id == updated_contact_data["id"]
        ).update(
            {
                "first_name": updated_contact_data["first_name"],
                "last_name": updated_contact_data["last_name"],
                "email": updated_contact_data["email"],
            }
        )
        # Delete old phone numbers
        old_phones = (
            self.session.query(PhoneNumber)
            .filter(PhoneNumber.contact_id == contact_id)
            .all()
        )
        for phone in old_phones:
            self.session.delete(phone)

        # Add new phone numbers
        contact = (
            self.session.query(Contact)
            .filter(Contact.id == updated_contact_data["id"])
            .first()
        )
        for phone_number in updated_contact_data.get("phone_numbers", []):
            new_phone = PhoneNumber(number=phone_number, contact=contact)
            self.session.add(new_phone)

        self.session.commit()
        self.epic_events_app.notify(
            "Contact successfully updated", severity="information"
        )
        self.start(on_back=self.on_back_callback)
