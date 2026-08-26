from sqlalchemy.orm import Session, joinedload
from models import Collaborator, Department, DepartmentName
from views import CollaboratorScreen, CreateCollaboratorScreen
from services import PasswordServices

class CollaboratorController:
    """
    """

    def __init__(self, epic_events_app, session):
        self.session: Session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None

    def start(self, on_back=None):
        self.on_back_callback = on_back
        collaborators = self.get_all_collaborators()
        collaborators_screen = CollaboratorScreen(collaborators)
        self.epic_events_app.push_screen(collaborators_screen, callback=self.handle_user_choice)

    def handle_user_choice(self, user_choice):
        """Callback when user chooses from collaborator menu"""
        match user_choice:
            case 'display_all_collaborators':
                all_collaborators = self.get_all_collaborators()
                all_collaborators_screen = CollaboratorScreen(all_collaborators)
                self.epic_events_app.push_screen(all_collaborators_screen, callback=self.handle_user_choice)
            case 'create_collaborator':
                # pass
                all_departments = self.get_all_departments()
                create_collaborator_screen = CreateCollaboratorScreen(all_departments)
                self.epic_events_app.push_screen(create_collaborator_screen, callback=self.create_collaborator)
            case ('update_collaborator', collaborator_id):
                pass
                # collaborator_to_update = self.load_collaborator_data_for_update(collaborator_id)
                # update_collaborator_screen = UpdatecollaboratorScreen(collaborator_to_update)
                # self.epic_events_app.push_screen(update_collaborator_screen, callback=self.update_collaborator)
            case 'delete_collaborator':
                pass
            case ('consult_customer', customer_id):
                pass
            case ('consult_event', event_id):
                pass
            case 'back':
                if self.on_back_callback:
                    self.on_back_callback()
                return
            case 'quit':
                self.epic_events_app.exit()

    def get_all_collaborators(self) -> list[Collaborator]:
        """
        Returns all collaborators from the database.
        """
        return self.session.query(Collaborator).options(
            joinedload(Collaborator.department),
            joinedload(Collaborator.customers), #Keep c-ustomers
            joinedload(Collaborator.events)
        ).all()

    def get_all_departments(self) -> list[Department]:
        """Returns all departments from the database."""
        return self.session.query(Department).all()

    def load_collaborator_data_for_update(self, collaborator_id: int):
        """
        """
        collaborator = self.session.query(collaborator).filter(
            Collaborator.id == collaborator_id
        ).first()

        return {
            'collaborator_id': collaborator.id,
            "collaborator_first_name": collaborator.first_name,
            "collaborator_last_name": collaborator.last_name,
            "department": collaborator.department
        }

    def create_collaborator(self, new_collaborator_data):
        """
        """
        # If creation is cancelled
        if not new_collaborator_data:
            self.epic_events_app.notify('Collaborator creation cancelled', severity='warning')
            self.start(self.on_back_callback)
            return

        # Else, transform raw data (dict) from submitted form
        # Email (firstname.lastname@epicevents.com)
        new_collaborator_email = (
            (new_collaborator_data['collaborator_first_name']).lower() +
            '.' +
            (new_collaborator_data['collaborator_last_name']).lower() +
            '@epicevents.com'
        )
        # Hash password
        new_collaborator_password = (
            PasswordServices.hash_password(
                new_collaborator_data['password']
            )
        )
        # Create department instance
        new_collaborator_department = self.session.query(Department).filter_by(
            name=DepartmentName(new_collaborator_data['department'])
        ).first()

        collaborator = Collaborator(
            last_name=new_collaborator_data['collaborator_last_name'],
            first_name=new_collaborator_data['collaborator_first_name'],
            email=new_collaborator_email,
            password=new_collaborator_password,
            department=new_collaborator_department,
        )

        self.session.add(collaborator)
        self.session.commit()
        self.epic_events_app.notify('Collaborator successfully created', severity='information')
        self.start(self.on_back_callback)

    def update_collaborator(self, updated_collaborator_data):
        """
        """
        if not updated_collaborator_data:
            self.epic_events_app.notify('Collaborator update cancelled', severity='warning')
            self.start(self.on_back_callback)
            return

        self.session.query(Collaborator).filter(Collaborator.id == updated_collaborator_data['id']).update(
            {
                "first_name": updated_collaborator_data['first_name'],
                "last_name": updated_collaborator_data['last_name'],
                "email": updated_collaborator_data['company_name'],
                "department_id": updated_collaborator_data['department_id']
            }
        )

        self.session.commit()
        self.epic_events_app.notify('Collaborator successfully updated', severity='information')
        self.start(self.on_back_callback)
        
    def delete_collaborator(self):
        pass