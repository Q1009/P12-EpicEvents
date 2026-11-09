from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:
    from textual.app import App


class CustomerController:
    """Controller for managing customers and contacts in the EpicEvents CRM.

    Handles all customer-related operations including listing, creating,
    updating, and managing customer and contact data. Coordinates between
    the database (via SQLAlchemy session), the views, and the
    authentication controller.

    :param epic_events_app: The main Textual application instance.
    :type epic_events_app: textual.app.App
    :param session: The SQLAlchemy database session for operations.
    :type session: sqlalchemy.orm.Session

    .. note::
        This controller uses the MVC pattern, receiving user input from views
        and updating both the model (database) and views accordingly.
    """

    def __init__(self, epic_events_app: "App", session: Session) -> None:
        """Initialize the CustomerController with application and
        database session.

        Stores references to the main application and database session, and
        initializes the authentication controller for user operations.

        :param epic_events_app: The main Textual application instance.
        :type epic_events_app: textual.app.App
        :param session: SQLAlchemy database session for operations.
        :type session: sqlalchemy.orm.Session
        """
        self.session: Session = session
        self.epic_events_app: App = epic_events_app
        self.on_back_callback: Callable[[], None] | None = None
        self.authentication_controller: AuthenticationController = (
            AuthenticationController(self.epic_events_app, self.session)
        )

    def start(
        self,
        customer_id: int | None = None,
        on_back: Callable[[], None] | None = None,
    ) -> None:
        """Start the customer management workflow.

        Stores the back callback and pushes the customer list screen with
        all customers, optionally pre-selecting a specific customer.

        :param customer_id: Optional ID of a customer to pre-select.
        :type customer_id: int | None
        :param on_back: Callback to execute when user returns to screen.
        :type on_back: Callable[[], None] | None
        """
        self.on_back_callback = on_back
        customers: list[Customer] = self.get_all_customers()
        self.push_customer_screen(
            customers=customers, customer_id=customer_id
        )

    def handle_user_choice(
        self, user_choice: str | tuple[str, Any]
    ) -> None:
        """Process user selection from the customer menu.

        Routes the user's menu choice to the appropriate action or screen.
        Handles navigation between screens, creating/updating customers and
        contacts, and application exit.

        :param user_choice: The user's selected menu option, which can be
            a simple string or a tuple with action and additional parameters.
        :type user_choice: str | tuple[str, Any]

        .. note::
            Available choices include: create_customer, update_customer,
            create_contact, update_contact, back, and quit.
        """
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
            case "quit":
                self.epic_events_app.exit()

    def get_all_customers(self) -> list[Customer]:
        """Retrieve all customers from the database.

        Returns all :class:`Customer` objects with their associated contacts,
        contact phone numbers, and sales representative loaded via eager
        loading.

        :return: List of all Customer objects with related data.
        :rtype: list[Customer]
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
        """Retrieve all collaborators from the sales department.

        :return: List of Collaborator objects in the sales department.
        :rtype: list[Collaborator]
        """
        return (
            self.session.query(Collaborator)
            .join(Collaborator.department)
            .filter(Department.name == DepartmentName.SALES)
            .all()
        )

    def load_customer_data_for_update(
        self, customer_id: int
    ) -> dict[str, Any]:
        """Load customer data for the update form.

        Retrieves a customer by ID and returns its data as a dictionary
        suitable for pre-filling an update form.

        :param customer_id: The ID of the customer to load.
        :type customer_id: int
        :return: Dictionary containing all customer fields for update.
        :rtype: dict[str, Any]
        """
        customer: Customer | None = (
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

    def load_contact_data_for_update(
        self, contact_id: int
    ) -> dict[str, Any]:
        """Load contact data for the update form.

        Retrieves a contact by ID and returns its data as a dictionary
        suitable for pre-filling an update form, including all phone numbers.

        :param contact_id: The ID of the contact to load.
        :type contact_id: int
        :return: Dictionary containing all contact fields for update.
        :rtype: dict[str, Any]
        """
        contact: Contact | None = (
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
        """Retrieve all contacts from the database.

        :return: List of all Contact objects.
        :rtype: list[Contact]
        """
        return self.session.query(Contact).all()

    def get_customers_by_sales_rep_id(
        self, user_id: int
    ) -> list[Customer]:
        """Retrieve all customers assigned to a specific sales representative.

        :param user_id: The ID of the sales representative.
        :type user_id: int
        :return: List of Customer objects for the specified representative.
        :rtype: list[Customer]
        """
        return (
            self.session.query(Customer)
            .filter(Customer.sales_representative_id == user_id)
            .all()
        )

    def get_customers_without_sales_rep(self) -> list[Customer]:
        """Retrieve all customers that have no sales representative assigned.

        :return: List of Customer objects with no sales representative.
        :rtype: list[Customer]
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
        """Push the customer list screen onto the application screen stack.

        Instantiates a :class:`CustomerScreen` with the provided customers and
        an optional pre-selected customer ID, then pushes it onto the
        application's screen stack with a callback.

        :param customers: List of :class:`Customer` objects to display.
        :type customers: list[Customer]
        :param customer_id: Optional ID of a customer to pre-select.
            If provided, the corresponding customer will be highlighted.
            Defaults to None.
        :type customer_id: int | None
        """
        current_user: Collaborator | None = (
            AuthenticationServices.get_user_info(self.session)
        )
        customers_screen = CustomerScreen(
            customers=customers,
            user=current_user,
            customer_id=customer_id,
        )
        self.epic_events_app.push_screen(
            customers_screen, callback=self.handle_user_choice
        )

    @AuthenticationServices.check_authentication
    def push_create_customer_screen(self) -> None:
        """Push the create customer screen onto the application screen stack.

        Retrieves all contacts and instantiates a
        :class:`CreateCustomerScreen` with them, then pushes it onto the
        application's screen stack with a callback to :meth:`create_customer`.
        """
        all_contacts: list[Contact] = self.get_all_contacts()
        create_customer_screen = CreateCustomerScreen(
            contacts=all_contacts
        )
        self.epic_events_app.push_screen(
            create_customer_screen,
            callback=self.create_customer,
        )

    @AuthenticationServices.check_authentication
    def push_update_customer_screen(self, customer_id: int) -> None:
        """Push the update customer screen onto the application screen stack.

        Retrieves all contacts and sales representatives, loads the data for
        the customer to update, instantiates an :class:`UpdateCustomerScreen`
        with this data, and pushes it onto the application's screen stack
        with a callback.

        :param customer_id: The ID of the customer to update.
            The corresponding customer data will be loaded and pre-filled.
        :type customer_id: int
        """
        all_contacts: list[Contact] = self.get_all_contacts()
        sales_representatives: list[Collaborator] = (
            self.get_sales_representatives()
        )
        customer_to_update: dict[str, Any] = (
            self.load_customer_data_for_update(customer_id)
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
        """Push the create contact screen onto the application screen stack.

        Instantiates a :class:`CreateContactScreen` and pushes it onto the
        application's screen stack with a callback to :meth:`create_contact`.
        """
        create_contact_screen = CreateContactScreen()
        self.epic_events_app.push_screen(
            create_contact_screen, callback=self.create_contact
        )

    @AuthenticationServices.check_authentication
    def push_update_contact_screen(self, contact_id: int) -> None:
        """Push the update contact screen onto the application screen stack.

        Loads the data for the contact to update, instantiates an
        :class:`UpdateContactScreen` with this data, and pushes it onto the
        application's screen stack with a callback to :meth:`update_contact`.

        :param contact_id: The ID of the contact to update.
            The corresponding contact data will be loaded and pre-filled.
        :type contact_id: int
        """
        contact_to_update: dict[str, Any] = (
            self.load_contact_data_for_update(contact_id)
        )
        update_contact_screen = UpdateContactScreen(
            contact_data=contact_to_update
        )
        self.epic_events_app.push_screen(
            update_contact_screen, callback=self.update_contact
        )

    @AuthenticationServices.check_authentication
    def create_customer(
        self, new_customer_data: dict[str, Any] | None
    ) -> None:
        """Create a new customer and associated contact in the database.

        Handles the customer creation form submission. If creation is
        cancelled, returns to the customer list. Otherwise, processes the form
        data, creates the contact, phone number, and customer objects, and saves
        them to the database.

        :param new_customer_data: Dictionary containing customer and contact
            data from the form, or None if creation was cancelled.
        :type new_customer_data: dict[str, Any] | None
        """
        # If creation was cancelled
        if not new_customer_data:
            self.epic_events_app.notify(
                "Customer creation cancelled", severity="warning"
            )
            self.start(on_back=self.on_back_callback)
            return

        # Else, transform raw data (dict) from submitted form
        # Contact
        customer_contact: Contact | dict[str, Any] = new_customer_data[
            "customer_contact"
        ]
        if isinstance(customer_contact, Contact):
            new_customer_contact: Contact = customer_contact
        else:
            new_customer_contact = Contact(
                last_name=customer_contact["last_name"],
                first_name=customer_contact["first_name"],
                email=customer_contact["email"],
            )
            self.session.add(new_customer_contact)

            # Phone Number
            phone_number: PhoneNumber = PhoneNumber(
                number=customer_contact["phone_number"],
                contact=new_customer_contact,
            )
            self.session.add(phone_number)

        # Customer
        customer: Customer = Customer(
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
    def update_customer(
        self, updated_customer_data: dict[str, Any] | None
    ) -> None:
        """Update an existing customer in the database.

        Handles the customer update form submission. If update is cancelled,
        returns to the customer list. Otherwise, processes the form data and
        updates the corresponding customer in the database, including its
        associated contacts and sales representative.

        :param updated_customer_data: Dictionary containing updated customer
            data from the form, or None if update was cancelled.
        :type updated_customer_data: dict[str, Any] | None
        """
        if not updated_customer_data:
            self.epic_events_app.notify(
                "Customer update cancelled", severity="warning"
            )
            self.start(on_back=self.on_back_callback)
            return

        customer_query = self.session.query(Customer).filter(
            Customer.id == updated_customer_data["id"]
        )

        customer_query.update(
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

        customer: Customer = customer_query.first()
        customer.contacts = updated_customer_data["customer_contacts"]

        self.session.commit()
        self.epic_events_app.notify(
            "Customer successfully updated", severity="information"
        )
        self.start(on_back=self.on_back_callback)

    @AuthenticationServices.check_authentication
    def create_contact(
        self, new_contact_data: dict[str, Any] | None
    ) -> None:
        """Create a new contact in the database.

        Handles the contact creation form submission. If creation is
        cancelled, returns to the customer list. Otherwise, processes the form
        data, creates the contact object and associated phone numbers, and
        saves them to the database.

        :param new_contact_data: Dictionary containing contact data from
            the form, or None if creation was cancelled.
        :type new_contact_data: dict[str, Any] | None
        """
        # If creation was cancelled
        if not new_contact_data:
            self.epic_events_app.notify(
                "Contact creation cancelled", severity="warning"
            )
            self.start(on_back=self.on_back_callback)
            return

        # Else, transform raw data (dict) from submitted form
        contact: Contact = Contact(
            first_name=new_contact_data["contact_first_name"],
            last_name=new_contact_data["contact_last_name"],
            email=new_contact_data["email"],
        )
        self.session.add(contact)

        # Phone numbers
        for phone_number in new_contact_data["phone_numbers"]:
            new_phone_number: PhoneNumber = PhoneNumber(
                number=phone_number, contact=contact
            )
            self.session.add(new_phone_number)

        self.session.commit()
        self.epic_events_app.notify(
            "Contact successfully created", severity="information"
        )
        self.start(on_back=self.on_back_callback)

    @AuthenticationServices.check_authentication
    def update_contact(
        self, updated_contact_data: dict[str, Any] | None
    ) -> None:
        """Update an existing contact in the database.

        Handles the contact update form submission. If update is cancelled,
        returns to the customer list. Otherwise, processes the form data and
        updates the corresponding contact in the database, including replacing
        all associated phone numbers with the new ones from the form.

        :param updated_contact_data: Dictionary containing updated contact
            data from the form, or None if update was cancelled.
        :type updated_contact_data: dict[str, Any] | None
        """
        if not updated_contact_data:
            self.epic_events_app.notify(
                "Contact update cancelled", severity="warning"
            )
            self.start(on_back=self.on_back_callback)
            return

        contact_id: int = updated_contact_data["id"]
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
        old_phones: list[PhoneNumber] = (
            self.session.query(PhoneNumber)
            .filter(PhoneNumber.contact_id == contact_id)
            .all()
        )
        for phone in old_phones:
            self.session.delete(phone)

        # Add new phone numbers
        contact: Contact = (
            self.session.query(Contact)
            .filter(Contact.id == updated_contact_data["id"])
            .first()
        )
        for phone_number in updated_contact_data.get("phone_numbers", []):
            new_phone: PhoneNumber = PhoneNumber(
                number=phone_number, contact=contact
            )
            self.session.add(new_phone)

        self.session.commit()
        self.epic_events_app.notify(
            "Contact successfully updated", severity="information"
        )
        self.start(on_back=self.on_back_callback)

    def _handle_auth_failure(
        self, error: AuthenticationError | None
    ) -> None:
        """Handle authentication failure scenarios.

        Called when authentication fails. Displays an error notification if
        an error occurred and returns to the previous screen via callback.

        :param error: The authentication error that occurred, if any.
        :type error: AuthenticationError | None
        """
        if error:
            self.epic_events_app.notify(
                f"[bold red]⚠️  {error!s}[/bold red]", severity="error"
            )
        if self.on_back_callback:
            self.on_back_callback()
