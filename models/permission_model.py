from enum import Enum, auto

class Permission(Enum):
    """
    Enum of all possible permissions in the Epic Event CRM.
    Naming convention:
    - {ACTION}_{RESSOURCE} for global permissions (ex: READ_CUSTOMER)
    - {ACTION}_OWN_{RESSOURCE} for permissions limited to one's own resources (ex: READ_OWN_CUSTOMERS)
    """

    # ===== Global permissions =====
    READ_OWN_PROFILE = auto()
    UPDATE_OWN_PROFILE = auto()

    # ===== Customers Permissions =====
    READ_ALL_CUSTOMERS = auto()
    CREATE_CUSTOMER = auto()
    UPDATE_OWN_CUSTOMERS = auto()

    # ===== Contracts Permissions =====
    READ_ALL_CONTRACTS = auto()
    CREATE_CONTRACT = auto()
    UPDATE_CONTRACT = auto()
    UPDATE_OWN_CONTRACTS = auto()

    # ===== Events Permissions =====
    READ_ALL_EVENTS = auto()
    CREATE_EVENT = auto()
    UPDATE_EVENT = auto()
    UPDATE_OWN_EVENTS = auto()

    # ===== Collaborators Permissions =====
    READ_ALL_COLLABORATORS = auto()
    CREATE_COLLABORATOR = auto()
    UPDATE_COLLABORATOR = auto()
    DELETE_COLLABORATOR = auto()