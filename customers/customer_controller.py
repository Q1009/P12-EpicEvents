from datetime import UTC, datetime

from sqlalchemy.orm import Session, joinedload

from authentication.authentication_controller import (
    AuthenticationController,
)
from collaborators.collaborator_model import (
    Collaborator,
    Department,
    DepartmentName,
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
from services.authentication_services import (
    AuthenticationError,
    AuthenticationServices,
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
        self.push_customer_screen(
            customers=customers, customer_id=customer_id
        )

    def handle_user_choice(self, user_choice):
        """Callback when user chooses from customer menu"""
        match user_choice:
            case "create_customer":
                self.push_create_customer_screen()
            case ("update_customer", customer_id):
                self.push_update_customer_screen(customer_id=customer_id)
            case "create_contact":
                self.push_create_contact_screen()
            case ("update_contact", contact_id):
                self.push_update_contact_screen(contact_id=contact_id)
            case "back":
                if self.on_back_callback:
                    self.on_back_callback()
                # return
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

    def get_sales_representatives(self) -> list[Collaborator]:
        return (
            self.session.query(Collaborator)
            .join(Collaborator.department)
            .filter(Department.name == DepartmentName.SALES)
            .all()
        )

    def load_customer_data_for_update(self, customer_id: int):
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
            "customer_contacts": customer.contacts,
            "customer_sales_representative": customer.sales_representative,
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

    @AuthenticationServices.check_authentication
    def push_customer_screen(
        self,
        customers: list[Customer],
        customer_id: int | None = None,
    ) -> None:
        """
        Push the customer list screen onto the application screen stack.

        Instantiates a :class:`CustomerScreen` with the provided customers and an optional
        pre-selected customer ID, then pushes it onto the application's screen stack
        with a callback to :meth:`handle_user_choice`.

        :param customers: List of :class:`Customer` objects to display in the screen table.
        :type customers: list[Customer]
        :param customer_id: Optional ID of a customer to pre-select in the table.
            If provided, the corresponding customer will be highlighted. Defaults to None.
        :type customer_id: int | None
        :return: None
        :rtype: None
        """
        customers_screen = CustomerScreen(
            customers=customers,
            customer_id=customer_id,
        )
        self.epic_events_app.push_screen(
            customers_screen, callback=self.handle_user_choice
        )

    @AuthenticationServices.check_authentication
    def push_create_customer_screen(self) -> None:
        """
        Push the create customer screen onto the application screen stack.

        Retrieves all contacts and instantiates a :class:`CreateCustomerScreen`
        with them, then pushes it onto the application's screen stack with a callback
        to :meth:`create_customer`.

        :return: None
        :rtype: None
        """
        all_contacts = self.get_all_contacts()
        create_customer_screen = CreateCustomerScreen(
            contacts=all_contacts
        )
        self.epic_events_app.push_screen(
            create_customer_screen,
            callback=self.create_customer,
        )

    @AuthenticationServices.check_authentication
    def push_update_customer_screen(self, customer_id: int) -> None:
        """
        Push the update customer screen onto the application screen stack.

        Retrieves all contacts and sales representatives, loads the data for the
        customer to update, instantiates an :class:`UpdateCustomerScreen` with this
        data, and pushes it onto the application's screen stack with a callback
        to :meth:`update_customer`.

        :param customer_id: The ID of the customer to update. The corresponding
            customer data will be loaded and pre-filled in the update form.
        :type customer_id: int
        :return: None
        :rtype: None
        """
        all_contacts = self.get_all_contacts()
        sales_representatives = self.get_sales_representatives()
        customer_to_update = self.load_customer_data_for_update(
            customer_id
        )
        update_customer_screen = UpdateCustomerScreen(
            customer_data=customer_to_update,
            contacts=all_contacts,
            sales_representatives=sales_representatives,
        )
        self.epic_events_app.push_screen(
            update_customer_screen, callback=self.update_customer
        )

    @AuthenticationServices.check_authentication
    def push_create_contact_screen(self) -> None:
        """
        Push the create contact screen onto the application screen stack.

        Instantiates a :class:`CreateContactScreen` and pushes it onto the
        application's screen stack with a callback to :meth:`create_contact`.

        :return: None
        :rtype: None
        """
        create_contact_screen = CreateContactScreen()
        self.epic_events_app.push_screen(
            create_contact_screen, callback=self.create_contact
        )

    @AuthenticationServices.check_authentication
    def push_update_contact_screen(self, contact_id: int) -> None:
        """
        Push the update contact screen onto the application screen stack.

        Loads the data for the contact to update, instantiates an
        :class:`UpdateContactScreen` with this data, and pushes it onto the
        application's screen stack with a callback to :meth:`update_contact`.

        :param contact_id: The ID of the contact to update. The corresponding
            contact data will be loaded and pre-filled in the update form.
        :type contact_id: int
        :return: None
        :rtype: None
        """
        contact_to_update = self.load_contact_data_for_update(contact_id)
        update_contact_screen = UpdateContactScreen(
            contact_data=contact_to_update
        )
        self.epic_events_app.push_screen(
            update_contact_screen, callback=self.update_contact
        )

    @AuthenticationServices.check_authentication
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
        # Contact
        customer_contact = new_customer_data["customer_contact"]
        if isinstance(customer_contact, Contact):
            new_customer_contact = customer_contact
        else:
            new_customer_contact = Contact(
                last_name=customer_contact["last_name"],
                first_name=customer_contact["first_name"],
                email=customer_contact["email"],
            )
            self.session.add(new_customer_contact)

            # Phone Number
            phone_number = PhoneNumber(
                number=customer_contact["phone_number"],
                contact=new_customer_contact,
            )
            self.session.add(phone_number)

        # Customer
        customer = Customer(
            last_name=new_customer_data["customer_last_name"],
            first_name=new_customer_data["customer_first_name"],
            company_name=new_customer_data["company_name"],
            sales_representative=self.authentication_controller.get_user_info(),
        )
        customer.contacts.append(new_customer_contact)
        self.session.add(customer)

        # Commit session
        self.session.commit()
        self.epic_events_app.notify(
            "Customer successfully created", severity="information"
        )
        self.start(on_back=self.on_back_callback)

    @AuthenticationServices.check_authentication
    def update_customer(self, updated_customer_data):
        """ """
        if not updated_customer_data:
            self.epic_events_app.notify(
                "Customer update cancelled", severity="warning"
            )
            self.start(on_back=self.on_back_callback)
            return

        customer = self.session.query(Customer).filter(
            Customer.id == updated_customer_data["id"]
        )

        customer.update(
            {
                "first_name": updated_customer_data["customer_first_name"],
                "last_name": updated_customer_data["customer_last_name"],
                "company_name": updated_customer_data["company_name"],
                "sales_representative_id": updated_customer_data[
                    "customer_sales_representative"
                ].id,
                "updated_at": datetime.now(UTC),
            }
        )

        customer.first().contacts = updated_customer_data[
            "customer_contacts"
        ]

        self.session.commit()
        self.epic_events_app.notify(
            "Customer successfully updated", severity="information"
        )
        self.start(on_back=self.on_back_callback)

    @AuthenticationServices.check_authentication
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

    @AuthenticationServices.check_authentication
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

    def _handle_auth_failure(self, error: AuthenticationError | None):
        """Handles authentication failure"""
        # if error:
        #     self.epic_events_app.notify(
        #         f"[bold red]⚠️  {error!s}[/bold red]", severity="error"
        #     )
        self.on_back_callback()
