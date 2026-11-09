from enum import Enum

from collaborators.collaborator_model import DepartmentName
from permissions.permission_model import Permission


class RoleName(Enum):
    """
    Enum of user roles in the Epic Events CRM.
    Each role corresponds to a department in the database (via DepartmentName).
    """

    ADMIN = DepartmentName.ADMIN.value
    SALES = DepartmentName.SALES.value
    SUPPORT = DepartmentName.SUPPORT.value


# Mapping of roles to their associated permissions.
# Each role gets a set of permissions it is authorized to perform.
ROLE_PERMISSIONS = {
    RoleName.ADMIN: {
        # The managing team oversees collaborators and contracts.
        # They assign a member of the support team to an event.
        # === Global ===
        Permission.READ_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        # === Customers ===
        Permission.READ_ALL_CUSTOMERS,
        # === Contracts ===
        Permission.READ_ALL_CONTRACTS,
        Permission.CREATE_CONTRACT,
        Permission.UPDATE_ALL_CONTRACTS,
        # === Events ===
        Permission.READ_ALL_EVENTS,
        Permission.UPDATE_ALL_EVENTS,
        # === Collaborators ===
        Permission.READ_ALL_COLLABORATORS,
        Permission.CREATE_COLLABORATOR,
        Permission.UPDATE_COLLABORATOR,
        Permission.DELETE_COLLABORATOR,
    },
    RoleName.SALES: {
        # Sales representatives can manage their own customers and contracts.
        # They can view all customers for prospecting but only edit their own.
        # === Global ===
        Permission.READ_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        # === Customers ===
        Permission.READ_ALL_CUSTOMERS,
        Permission.CREATE_CUSTOMER,
        Permission.UPDATE_OWN_CUSTOMERS,
        Permission.CREATE_CONTACT,
        Permission.UPDATE_CONTACT,
        # === Contracts ===
        Permission.READ_ALL_CONTRACTS,
        Permission.UPDATE_OWN_CONTRACTS,
        # === Events ===
        Permission.READ_ALL_EVENTS,
        Permission.CREATE_EVENT,
    },
    RoleName.SUPPORT: {
        # Support team can manage events
        # and view related customer/contract data.
        # === Global ===
        Permission.READ_OWN_PROFILE,
        Permission.UPDATE_OWN_PROFILE,
        # === Customers ===
        Permission.READ_ALL_CUSTOMERS,
        # === Contracts ===
        Permission.READ_ALL_CONTRACTS,
        # === Events ===
        Permission.READ_ALL_EVENTS,
        Permission.UPDATE_OWN_EVENTS,
        Permission.CREATE_LOCATION,
        Permission.UPDATE_LOCATION,
    },
}
