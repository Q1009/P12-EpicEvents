from sqlalchemy.orm import Session, joinedload

from contracts.contract_model import (
    Contract,
    ContractStatus,
)
from contracts.contract_view import (
    ContractScreen,
    CreateContractScreen,
    UpdateContractScreen,
)
from customers.customer_model import Customer


class ContractController:
    """ """

    def __init__(self, epic_events_app, session):
        self.session: Session = session
        self.epic_events_app = epic_events_app
        self.on_back_callback = None

    def start(self, contract_id=None, on_back=None):
        self.on_back_callback = on_back
        contracts = self.get_all_contracts()
        contracts_screen = ContractScreen(contracts, contract_id)
        self.epic_events_app.push_screen(
            contracts_screen, callback=self.handle_user_choice
        )

    def handle_user_choice(self, user_choice):
        """Callback when user chooses from contract menu"""
        match user_choice:
            case "create_contract":
                # pass
                all_customers = self.get_all_customers()
                create_contract_screen = CreateContractScreen(
                    all_customers
                )
                self.epic_events_app.push_screen(
                    create_contract_screen,
                    callback=self.create_contract,
                )
            case ("update_contract", contract_id):
                # pass
                all_customers = self.get_all_customers()
                contract_to_update = self.load_contract_data_for_update(
                    contract_id
                )
                update_contract_screen = UpdateContractScreen(
                    contract_to_update, all_customers
                )
                self.epic_events_app.push_screen(
                    update_contract_screen,
                    callback=self.update_contract,
                )
            case ("create_event", contract_id):
                pass
                # contract_data_for_event = self.get_data(contract_id)
                # self.create_event(
                #     contract_data_for_event
                # )
            case ("consult_customer", customer_id):
                pass
            case ("consult_event", event_id):
                pass
            case "back":
                if self.on_back_callback:
                    self.on_back_callback()
                return
            case "quit":
                self.epic_events_app.exit()

    def get_all_contracts(self) -> list[Contract]:
        """
        Returns all contracts from the database.
        """
        return (
            self.session.query(Contract)
            .options(
                joinedload(Contract.customer),
                joinedload(Contract.event),
            )
            .all()
        )

    def get_all_customers(self) -> list[Customer]:
        return self.session.query(Customer).all()

    def load_contract_data_for_update(self, contract_id: int):
        """ """
        contract = (
            self.session.query(Contract)
            .filter(Contract.id == contract_id)
            .first()
        )

        return {
            "contract_id": contract.id,
            "contract_total_amount": contract.total_amount,
            "contract_amount_due": contract.amount_due,
            "contract_status": contract.status,
            "contract_customer": contract.customer,
        }

    def create_contract(self, new_contract_data):
        """ """
        # If creation is cancelled
        if not new_contract_data:
            self.epic_events_app.notify(
                "Contract creation cancelled", severity="warning"
            )
            self.start(self.on_back_callback)
            return

        # Else, transform raw data (dict) from submitted form
        # Status: always pending at creation
        new_contract_status = ContractStatus.PENDING

        contract = Contract(
            total_amount=new_contract_data["contract_total_amount"],
            amount_due=new_contract_data["contract_amount_due"],
            status=new_contract_status,
            customer=new_contract_data["contract_customer"],
        )

        self.session.add(contract)
        self.session.commit()
        self.epic_events_app.notify(
            "Contract successfully created", severity="information"
        )
        self.start(self.on_back_callback)

    def update_contract(self, updated_contract_data):
        """ """
        if not updated_contract_data:
            self.epic_events_app.notify(
                "Contract update cancelled", severity="warning"
            )
            self.start(self.on_back_callback)
            return

        self.session.query(Contract).filter(
            Contract.id == updated_contract_data["contract_id"]
        ).update(
            {
                "total_amount": updated_contract_data[
                    "contract_total_amount"
                ],
                "amount_due": updated_contract_data["contract_amount_due"],
                "status": updated_contract_data["contract_status"],
                "customer_id": updated_contract_data[
                    "contract_customer"
                ].id,
            }
        )

        self.session.commit()
        self.epic_events_app.notify(
            "Contract successfully updated", severity="information"
        )
        self.start(self.on_back_callback)

    def create_event(self, contract_data_for_event):
        pass
