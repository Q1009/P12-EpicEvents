"""Permission management services for Epic Events CRM.

This module provides a centralized Role-Based Access Control (RBAC) system.
It implements permission checking, role resolution, and decorators for
protecting methods based on user permissions.

The system uses three roles:
- ADMIN: Can manage collaborators of Epic Events
- SALES: Can manage their own customers and contracts
- SUPPORT: Can manage their assigned events

Dependencies:
- models: Collaborator, Permission, RoleName
- models.role_model: ROLE_PERMISSIONS
"""

from collections.abc import Callable
from functools import wraps

from collaborators.collaborator_model import Collaborator
from permissions.permission_model import Permission
from permissions.role_model import ROLE_PERMISSIONS, RoleName


class PermissionError(Exception):
    """Exception raised when a user lacks the required permission.

    Attributes:
        message (str): Explanation of the permission error
    """

    def __init__(self, message: str = "Permission denied"):
        """Initialize the PermissionError with a custom message.

        Args:
            message: Human-readable error message
        """
        self.message = message
        super().__init__(self.message)

class PermissionServices:
    """Centralized service for managing and verifying user permissions.

    This service provides:
    - Role resolution based on user's department
    - Permission retrieval for users
    - Permission verification
    - Decorators for method protection

    The service is stateless and all methods are static for easy testing
    and dependency injection.
    """

    @staticmethod
    def get_role(user: Collaborator) -> RoleName:
        """
        Get the role of a user based on their department.
        Accesses the department name via the relationship (user.department.name).

        Args:
            user: Collaborator instance from the database

        Returns:
            RoleName: The enum value representing the user's role
                    (ADMIN, SALES, or SUPPORT)

        Raises:
            ValueError: If the department name doesn't match any defined role
        """

        # Get the department name from the relationship
        user_department_name = user.department.name.value

        # Find the matching role
        for role in RoleName:
            if role.value == user_department_name:
                return role

        # Only raise if no role matched (after checking all roles)
        raise ValueError(
            f"Unknown department name for role mapping: {user_department_name}. "
            f"Valid roles are: {[role.value for role in RoleName]}"
        )
    
    @staticmethod
    def get_permissions(user: Collaborator) -> set[Permission]:
        """
        Get all permissions for a user based on their role.

        Args:
            user: Collaborator instance from the database

        Returns:
            Set[Permission]: Set of all permissions granted to the user's role.
                            Returns an empty set if the role has no defined permissions.
        """

        user_role = PermissionServices.get_role(user)
        # Return a copy of the permissions set to avoid external modifications
        return set(ROLE_PERMISSIONS.get(user_role, set()))

    @staticmethod
    def has_permission(user: Collaborator, permission: Permission) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            user: Collaborator instance from the database
            permission: Permission enum to check

        Returns:
            bool: True if the user has the permission, False otherwise
        """

        return permission in PermissionServices.get_permissions(user)
    
    @staticmethod
    def check_permission(*required_permissions: Permission) -> Callable:
        """
        Decorator to verify a user has ALL required permissions.

        Args:
            *required_permissions: Variable number of Permission enum values.
                                User must have ALL of them to proceed.

        Usage:
            # Single permission
            @PermissionServices.check_permission(Permission.READ_ALL_CUSTOMERS)
            def get_customers(user: Collaborator):
                ...

            # Multiple permissions (user must have ALL)
            @PermissionServices.check_permission(
                Permission.READ_ALL_CUSTOMERS,
                Permission.CREATE_CUSTOMER
            )
            def create_customer(user: Collaborator):
                ...

        Returns:
            Decorated function that enforces permission checks

        Raises:
            PermissionError: If user lacks any required permission
            ValueError: If no user is provided
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func) # Preserves the metadata of the original function (useful for debugging)
            def wrapper(*args, **kwargs):
                # Extract user from kwargs or args (first positional arg)
                user = kwargs.get('user')
                if not user and len(args) >= 1:
                    user = args[0]  # Assume user is first argument

                if not user:
                    raise PermissionError("Authentication required: no user provided")

                # Check ALL required permissions
                missing_permissions = [
                    perm for perm in required_permissions
                    if not PermissionServices.has_permission(user, perm)
                ]

                if missing_permissions:
                    raise PermissionError(
                        f"User {user.email} lacks permissions: "
                        f"{', '.join(p.name for p in missing_permissions)}"
                    )

                return func(*args, **kwargs)
            return wrapper
        return decorator