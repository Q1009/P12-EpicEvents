import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Collaborator, Permission, RoleName, ROLE_PERMISSIONS
from services import PermissionServices, PermissionError
from config.settings import settings
from typing import Tuple

SALES_REP_ID = 1
SUPPORT_REP_ID = 4
ADMIN_REP_ID = 6

@pytest.fixture(scope="module")  # Shared across all tests in this module
def db_session():
    """
    Fixture that provides a database session for testing.

    Scope:
        Module-level (shared across all tests in this file to optimize performance)

    Lifecycle:
        1. Creates engine and session before the first test
        2. Yields the session to test functions
        3. Rolls back all changes, closes the session, and disposes the engine after the last test

    Returns:
        sqlalchemy.orm.Session: Database session for test operations

    Note:
        Uses rollback to ensure no test data persists in the database
    """

    engine = create_engine(settings.DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session  # Tests run here

    # Cleanup: Rollback to discard any changes, then close resources
    session.rollback()
    session.close()
    engine.dispose()

@pytest.fixture(scope="module")
def collab(db_session: Session) -> Tuple[Collaborator, Collaborator, Collaborator]:
    """
    Fixture that provides collaborator instances for testing.

    Retrieves pre-seeded collaborators with known roles for consistent testing.
    Uses hardcoded IDs based on the seed.py data structure.

    Returns:
        tuple[Collaborator, Collaborator, Collaborator]:
            - [0]: Sales representative (ID=1)
            - [1]: Support representative (ID=4)
            - [2]: Administrator (ID=6)

    Raises:
        AssertionError: If any expected collaborator is not found in the database
    """
    sales_rep = db_session.query(Collaborator).filter_by(id=SALES_REP_ID).first()
    support_rep = db_session.query(Collaborator).filter_by(id=SUPPORT_REP_ID).first()
    admin_rep = db_session.query(Collaborator).filter_by(id=ADMIN_REP_ID).first()

    # Verify all test subjects exist
    assert sales_rep is not None, "Sales representative (ID=1) not found in database"
    assert support_rep is not None, "Support representative (ID=4) not found in database"
    assert admin_rep is not None, "Administrator (ID=6) not found in database"

    return sales_rep, support_rep, admin_rep

class TestPermissionServices:
    """
    Test cases for the PermissionServices class functionality.

    This test class verifies:
    - Correct role resolution from collaborator's department
    - Accurate permission assignment based on role
    - Proper permission checking for individual users
    """

    def test_get_role(self, collab: Tuple[Collaborator, Collaborator, Collaborator]):
        """
        Test that get_role returns the correct RoleName enum for each collaborator.

        Verifies:
            - Sales collaborator (ID=1) returns RoleName.SALES
            - Support collaborator (ID=4) returns RoleName.SUPPORT
            - Admin collaborator (ID=6) returns RoleName.ADMIN

        Methodology:
            - Compares the returned RoleName enum directly (not string values)
            - Ensures role is determined by collaborator.department.name

        Expected Behavior:
            The role should match the collaborator's department name exactly.
        """
        sales_rep, support_rep, admin_rep = collab

        # Get roles for each collaborator
        sales_role = PermissionServices.get_role(sales_rep)
        support_role = PermissionServices.get_role(support_rep)
        admin_role = PermissionServices.get_role(admin_rep)

        # Verify roles match expected enums
        assert sales_role == RoleName.SALES, \
            f"Expected SALES role for sales rep, got {sales_role}"
        assert support_role == RoleName.SUPPORT, \
            f"Expected SUPPORT role for support rep, got {support_role}"
        assert admin_role == RoleName.ADMIN, \
            f"Expected ADMIN role for admin, got {admin_role}"

    def test_get_permissions(self, collab: Tuple[Collaborator, Collaborator, Collaborator]):
        """
        Test that get_permissions returns the correct permission set for each role.

        Verifies:
            - Returns a set of Permission enum values
            - Each role has its expected permissions
            - No missing permissions for any role
            - Return type is always a set (even if empty)

        Methodology:
            - Compares returned permissions against ROLE_PERMISSIONS mapping
            - Checks for presence of all expected permissions
            - Validates return type

        Expected Behavior:
            Each role should have exactly the permissions defined in ROLE_PERMISSIONS.
        """
        sales_rep, support_rep, admin_rep = collab

        # Get permissions for each role
        sales_permissions = PermissionServices.get_permissions(sales_rep)
        support_permissions = PermissionServices.get_permissions(support_rep)
        admin_permissions = PermissionServices.get_permissions(admin_rep)

        # Verify return types
        assert isinstance(sales_permissions, set), \
            "get_permissions() should return a set"
        assert isinstance(support_permissions, set), \
            "get_permissions() should return a set"
        assert isinstance(admin_permissions, set), \
            "get_permissions() should return a set"

        # Verify non-empty results
        assert len(sales_permissions) > 0, \
            "Sales role should have at least one permission"
        assert len(support_permissions) > 0, \
            "Support role should have at least one permission"
        assert len(admin_permissions) > 0, \
            "Admin role should have at least one permission"
        
        # Verify all expected permissions are present for each role
        expected_sales_perms = ROLE_PERMISSIONS[RoleName.SALES]
        for permission in expected_sales_perms:
            assert permission in sales_permissions, \
                f"Sales role missing permission: {permission.name}"

        expected_support_perms = ROLE_PERMISSIONS[RoleName.SUPPORT]
        for permission in expected_support_perms:
            assert permission in support_permissions, \
                f"Support role missing permission: {permission.name}"

        expected_admin_perms = ROLE_PERMISSIONS[RoleName.ADMIN]
        for permission in expected_admin_perms:
            assert permission in admin_permissions, \
                f"Admin role missing permission: {permission.name}"

    def test_has_permission(self, collab: Tuple[Collaborator, Collaborator, Collaborator]):
        """
        Test that has_permission correctly verifies if a user has a specific permission.

        Verifies:
            - Returns True for permissions the user's role possesses
            - Returns False for permissions the user's role does NOT possess
            - Works correctly for all three roles

        Methodology:
            - Tests both positive cases (has permission) and negative cases (lacks permission)
            - Uses permissions from ROLE_PERMISSIONS as the source of truth

        Expected Behavior:
            A user should have exactly the permissions defined for their role in ROLE_PERMISSIONS.
        """
        sales_rep, support_rep, admin_rep = collab

        # --- Positive Tests: Users should have their role's permissions ---
        for permission in ROLE_PERMISSIONS[RoleName.SALES]:
            assert PermissionServices.has_permission(sales_rep, permission), \
                f"Sales rep should have {permission.name} permission"

        for permission in ROLE_PERMISSIONS[RoleName.SUPPORT]:
            assert PermissionServices.has_permission(support_rep, permission), \
                f"Support rep should have {permission.name} permission"

        for permission in ROLE_PERMISSIONS[RoleName.ADMIN]:
            assert PermissionServices.has_permission(admin_rep, permission), \
                f"Admin should have {permission.name} permission"

        # --- Negative Tests: Users should NOT have other role-only's permissions ---
        # Test role-only permissions (e.g., CREATE_COLLABORATOR for admin)
        sales_only_permissions = ROLE_PERMISSIONS[RoleName.SALES] - \
                                (ROLE_PERMISSIONS[RoleName.ADMIN] | ROLE_PERMISSIONS[RoleName.SUPPORT])
        support_only_permissions = ROLE_PERMISSIONS[RoleName.SUPPORT] - \
                                (ROLE_PERMISSIONS[RoleName.SALES] | ROLE_PERMISSIONS[RoleName.ADMIN])
        admin_only_permissions = ROLE_PERMISSIONS[RoleName.ADMIN] - \
                                (ROLE_PERMISSIONS[RoleName.SALES] | ROLE_PERMISSIONS[RoleName.SUPPORT])
        
        for permission in sales_only_permissions:
            assert not PermissionServices.has_permission(support_rep, permission), \
                f"Support rep should NOT have {permission.name} permission"
            assert not PermissionServices.has_permission(admin_rep, permission), \
                f"Admin rep should NOT have {permission.name} permission"

        for permission in support_only_permissions:
            assert not PermissionServices.has_permission(sales_rep, permission), \
                f"Sales rep should NOT have {permission.name} permission"
            assert not PermissionServices.has_permission(admin_rep, permission), \
                f"Admin rep should NOT have {permission.name} permission"

        for permission in admin_only_permissions:
            assert not PermissionServices.has_permission(sales_rep, permission), \
                f"Sales rep should NOT have {permission.name} permission"
            assert not PermissionServices.has_permission(support_rep, permission), \
                f"Support rep should NOT have {permission.name} permission"

    def test_check_permission_decorator(self, collab: Tuple[Collaborator, Collaborator, Collaborator]):
        """
        Test that the check_permission decorator properly enforces permissions.

        Verifies:
            - Allows execution when user has the permission
            - Raises PermissionError when user lacks the permission
            - Works with both global and resource-specific permissions
        """
        sales_rep, support_rep, admin_rep = collab

        @PermissionServices.check_permission(Permission.READ_ALL_CUSTOMERS)
        def function_protected_by_one_permission(user: Collaborator):
            return "User has the required permission"

        @PermissionServices.check_permission(
            Permission.READ_ALL_CUSTOMERS,
            Permission.CREATE_CUSTOMER
        )
        def function_protected_by_multiple_permission(user: Collaborator):
            return "User has all required permissions"

        # Sales rep should have READ_ALL_CUSTOMERS and CREATE_CUSTOMER
        can_access = function_protected_by_one_permission(
            user=sales_rep
        )
        assert can_access == "User has the required permission"
        can_access = function_protected_by_multiple_permission(
            user=sales_rep
        )
        assert can_access == "User has all required permissions"

        # Support rep should have READ_ALL_CUSTOMERS but NOT have CREATE_CUSTOMER
        can_access = function_protected_by_one_permission(
            user=support_rep
        )
        assert can_access == "User has the required permission"

        with pytest.raises(PermissionError) as exc_info:
            function_protected_by_multiple_permission(
                user=support_rep
            )

        assert "lacks permissions" in str(exc_info.value)
        assert "CREATE_CUSTOMER" in str(exc_info.value)
        assert support_rep.email in str(exc_info.value)

        # Test with no user provided
        with pytest.raises(PermissionError) as exc_info:
            function_protected_by_one_permission()  # Missing user argument

        assert "Authentication required" in str(exc_info.value)
