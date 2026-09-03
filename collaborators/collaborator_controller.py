from sqlalchemy.orm import Session, joinedload

from collaborators.collaborator_model import (
    Collaborator,
    Department,
)
from collaborators.collaborator_view import (
    CollaboratorScreen,
    CreateCollaboratorScreen,
    UpdateCollaboratorScreen,
)
from services.authentication_services import PasswordServices


class CollaboratorController:
    """ """

    def __init__(self, epic_events_app, session):
        self.session: Session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None
        self.on_consult_customer_callback = None
        self.on_consult_event_callback = None

    def start(
        self, on_back=None, on_consult_customer=None, on_consult_event=None
    ):
        self.on_back_callback = on_back
        self.on_consult_customer_callback = on_consult_customer
        self.on_consult_event_callback = on_consult_event
        collaborators = self.get_all_collaborators()
        collaborators_screen = CollaboratorScreen(collaborators)
        self.epic_events_app.push_screen(
            collaborators_screen, callback=self.handle_user_choice
        )

    def handle_user_choice(self, user_choice):
        """Callback when user chooses from collaborator menu"""
        match user_choice:
            case "create_collaborator":
                all_departments = self.get_all_departments()
                create_collaborator_screen = CreateCollaboratorScreen(
                    all_departments
                )
                self.epic_events_app.push_screen(
                    create_collaborator_screen,
                    callback=self.create_collaborator,
                )
            case ("update_collaborator", collaborator_id):
                all_departments = self.get_all_departments()
                collaborator_to_update = (
                    self.load_collaborator_data_for_update(collaborator_id)
                )
                update_collaborator_screen = UpdateCollaboratorScreen(
                    collaborator_to_update, all_departments
                )
                self.epic_events_app.push_screen(
                    update_collaborator_screen,
                    callback=self.update_collaborator,
                )
            case ("delete_collaborator", collaborator_id):
                self.delete_collaborator(collaborator_id)
            case ("consult_customer", customer_id):
                self.on_consult_customer_callback(customer_id)
                return
            case ("consult_event", event_id):
                self.on_consult_event_callback(event_id)
                return
            case "back":
                if self.on_back_callback:
                    self.on_back_callback()
                return
            case "quit":
                self.epic_events_app.exit()

    def get_all_collaborators(self) -> list[Collaborator]:
        """
        Returns all collaborators from the database.
        """
        return (
            self.session.query(Collaborator)
            .options(
                joinedload(Collaborator.department),
                joinedload(Collaborator.customers),
                joinedload(Collaborator.events),
            )
            .all()
        )

    def get_all_departments(self) -> list[Department]:
        """Returns all departments from the database."""
        return self.session.query(Department).all()

    def load_collaborator_data_for_update(self, collaborator_id: int):
        """ """
        collaborator = (
            self.session.query(Collaborator)
            .filter(Collaborator.id == collaborator_id)
            .first()
        )

        return {
            "collaborator_id": collaborator.id,
            "collaborator_first_name": collaborator.first_name,
            "collaborator_last_name": collaborator.last_name,
            "department": collaborator.department,
        }

    def create_collaborator(self, new_collaborator_data):
        """ """
        # If creation is cancelled
        if not new_collaborator_data:
            self.epic_events_app.notify(
                "Collaborator creation cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_event=self.on_consult_event_callback,
            )
            return

        # Else, transform raw data (dict) from submitted form
        # Email (firstname.lastname@epicevents.com)
        new_collaborator_email = (
            (new_collaborator_data["collaborator_first_name"]).lower()
            + "."
            + (new_collaborator_data["collaborator_last_name"]).lower()
            + "@epicevents.com"
        )
        # Hash password
        new_collaborator_password = PasswordServices.hash_password(
            new_collaborator_data["password"]
        )

        collaborator = Collaborator(
            last_name=new_collaborator_data["collaborator_last_name"],
            first_name=new_collaborator_data["collaborator_first_name"],
            email=new_collaborator_email,
            password=new_collaborator_password,
            department=new_collaborator_data["department"],
        )

        self.session.add(collaborator)
        self.session.commit()
        self.epic_events_app.notify(
            "Collaborator successfully created", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_event=self.on_consult_event_callback,
        )

    def update_collaborator(self, updated_collaborator_data):
        """ """
        if not updated_collaborator_data:
            self.epic_events_app.notify(
                "Collaborator update cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_event=self.on_consult_event_callback,
            )
            return

        # Update email
        updated_collaborator_email = (
            (updated_collaborator_data["first_name"]).lower()
            + "."
            + (updated_collaborator_data["last_name"]).lower()
            + "@epicevents.com"
        )

        self.session.query(Collaborator).filter(
            Collaborator.id == updated_collaborator_data["id"]
        ).update(
            {
                "first_name": updated_collaborator_data["first_name"],
                "last_name": updated_collaborator_data["last_name"],
                "email": updated_collaborator_email,
                "department_id": updated_collaborator_data[
                    "department"
                ].id,
            }
        )

        self.session.commit()
        self.epic_events_app.notify(
            "Collaborator successfully updated", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_event=self.on_consult_event_callback,
        )

    def delete_collaborator(self, collaborator_id):
        if not collaborator_id:
            self.epic_events_app.notify(
                "Collaborator delete cancelled", severity="warning"
            )
            self.start(
                on_back=self.on_back_callback,
                on_consult_customer=self.on_consult_customer_callback,
                on_consult_event=self.on_consult_event_callback,
            )
            return

        self.session.query(Collaborator).filter(
            Collaborator.id == collaborator_id
        ).delete()

        self.session.commit()
        self.epic_events_app.notify(
            "Collaborator successfully deleted", severity="information"
        )
        self.start(
            on_back=self.on_back_callback,
            on_consult_customer=self.on_consult_customer_callback,
            on_consult_event=self.on_consult_event_callback,
        )
