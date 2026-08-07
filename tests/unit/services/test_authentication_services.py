import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from services import PasswordServices, TokenServices, AuthenticationError, AuthenticationServices
from datetime import datetime, timedelta, timezone
from keys import get_private_key
from tokens import load_tokens, save_tokens
from pathlib import Path
from config import settings
from models import Collaborator
import jwt

@pytest.fixture(scope='module')
def expired_access_token():
    """
    Fixture to create an expired access token for testing.

    This fixture generates a JWT access token that is already expired.
    It can be used in tests that require an expired token scenario.
    """
    user_id = 1
    private_key = get_private_key()

    payload = {
        'sub': str(user_id),
        'jti': '123456789abcdef',
        'type': 'access',
        # Set expiration in the past
        'exp': datetime.now(timezone.utc) - timedelta(seconds=1),
        'iat': datetime.now(timezone.utc)
    }

    return jwt.encode(
        payload,
        private_key,
        algorithm='RS256'
    )

@pytest.fixture(scope='module')
def expired_refresh_token():
    """
    Fixture to create an expired refresh token for testing.

    This fixture generates a JWT refresh token that is already expired.
    It can be used in tests that require an expired token scenario.
    """
    user_id = 1
    # Create a token that expires immediately (or in the past)
    private_key = get_private_key()

    payload = {
        'sub': str(user_id),
        'jti': 'abcdef123456789',
        'type': 'refresh',
        # Set expiration in the past
        'exp': datetime.now(timezone.utc) - timedelta(seconds=1),
        'iat': datetime.now(timezone.utc)
    }

    return jwt.encode(
        payload,
        private_key,
        algorithm='RS256'
    )

@pytest.fixture(scope="module")
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
def valid_user(db_session):
    """
    Fixture that provides a valid user for testing.

    Scope:
        Module-level (shared across all tests in this file to optimize performance)
    
    """
    # Gets the collaborator with id 1 from the database for testing purposes
    return db_session.query(Collaborator).filter_by(id=1).first()


class TestPasswordServices:
    """
    Test cases for the PasswordServices class functionality.

    This test class verifies:
    - Correct password hashing
    - Correct password verification
    """

    def test_hashing_password(self):
        """
        Test the hashing of a password.

        This test verifies that:
        - A password can be hashed successfully.
        - The hashed password is not the same as the original password.
        """
        password = 'password_to_hash'
        expected_hashed_bit = '$2b$12$' # bcrypt hashed passwords start with this prefix

        hashed_password = PasswordServices.hash_password(password)

        assert hashed_password is not None
        assert expected_hashed_bit in hashed_password

    def test_verifying_password(self):
        """
        Test the verification of a password against its hash.

        This test verifies that:
        - The correct password verifies successfully against the hashed password.
        - An incorrect password does not verify against the hashed password.
        """
        password = 'right_password'
        hashed_password = PasswordServices.hash_password(password)

        # Verify the correct password
        assert PasswordServices.verify_password(password, hashed_password) is True

        # Verify an incorrect password
        assert PasswordServices.verify_password('wrong_password', hashed_password) is False

class TestTokenServices:
    """
    Test cases for the TokenServices class functionality.

    This test class verifies:
    - Correct access token creation
    - Correct refresh token creation
    - Correct token verification for both access and refresh tokens
    - Correct refresh token logic, including token rotation and invalidation
    """

    def test_create_access_token(self):
        """
        Test the creation of an access token.

        This test verifies that:
        - The access token is created successfully.
        - The token contains 3 parts separated by dots.
        - The token starts with 'ey' when base64 encoded.
        """
        user_id = 1
        access_token = TokenServices.create_access_token(user_id)

        assert access_token is not None
        # JWTs have three parts separated by dots
        assert access_token.count('.') == 2
        # JWTs typically start with 'ey' when base64 encoded
        assert access_token.startswith('ey')

    def test_verify_access_token(self, expired_access_token):
        """
        Test the verification of an access token.

        This test verifies that:
        - The access token is decoded.
        - The decoded token has a payload.
        - The payload contains the correct user ID.
        - The payload contains the correct token unique identifier.
        - The payload contains the correct token type.
        - The payload contains the correct issued at and expiration timestamps.
        - The type claim matches the expected token type.
        - Raises an exception if the token is invalid or expired.
        """
        user_id = 1
        valid_access_token = TokenServices.create_access_token(user_id)

        payload = TokenServices.verify_token(valid_access_token, 'access')

        # Test that the payload is not None and contains expected claims
        assert payload is not None
        assert payload['sub'] == str(user_id)
        assert payload['jti'] is not None
        assert payload['type'] == 'access'
        assert payload['iat'] is not None
        assert payload['exp'] is not None

        # Test that expired tokens raise an AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            TokenServices.verify_token(expired_access_token, 'access')
        assert 'Token has expired' in str(exc_info.value)
        assert 'type' not in str(exc_info.value)

        # Test that invalid tokens raise an AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            TokenServices.verify_token('invalid.token.string', 'access')
        assert 'Invalid token' in str(exc_info.value)
        assert 'expired' not in str(exc_info.value)

        # Test that providing the wrong token type raises an AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            TokenServices.verify_token(valid_access_token, 'refresh')
        assert 'Invalid token type' in str(exc_info.value)
        assert 'expired' not in str(exc_info.value)

    def test_create_refresh_token(self):
        """
        Test the creation of a refresh token.

        This test verifies that:
        - The refresh token is created successfully.
        - The token contains 3 parts separated by dots.
        - The token starts with 'ey' when base64 encoded.
        """
        user_id = 1
        refresh_token = TokenServices.create_refresh_token(user_id)

        assert refresh_token is not None
        # JWTs have three parts separated by dots
        assert refresh_token.count('.') == 2
        # JWTs typically start with 'ey' when base64 encoded
        assert refresh_token.startswith('ey')

    def test_verify_refresh_token(self, expired_refresh_token):
        """
        Test the verification of a refresh token.

        This test verifies that:
        - The refresh token is decoded.
        - The decoded token has a payload.
        - The payload contains the correct user ID.
        - The payload contains the correct token unique identifier.
        - The payload contains the correct token type.
        - The payload contains the correct issued at and expiration timestamps.
        - The type claim matches the expected token type.
        - Raises an exception if the token is invalid or expired.
        """
        user_id = 1
        valid_refresh_token = TokenServices.create_refresh_token(user_id)

        payload = TokenServices.verify_token(valid_refresh_token, 'refresh')

        # Test that the payload is not None and contains expected claims
        assert payload is not None
        assert payload['sub'] == str(user_id)
        assert payload['jti'] is not None
        assert payload['type'] == 'refresh'
        assert payload['iat'] is not None
        assert payload['exp'] is not None

        # Test that expired tokens raise an AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            TokenServices.verify_token(expired_refresh_token, 'refresh')
        assert 'Token has expired' in str(exc_info.value)
        assert 'type' not in str(exc_info.value)

        # Test that invalid tokens raise an AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            TokenServices.verify_token('invalid.token.string', 'refresh')
        assert 'Invalid token' in str(exc_info.value)
        assert 'expired' not in str(exc_info.value)

        # Test that providing the wrong token type raises an AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            TokenServices.verify_token(valid_refresh_token, 'access')
        assert 'Invalid token type' in str(exc_info.value)
        assert 'expired' not in str(exc_info.value)

    def test_refresh_token(self, expired_refresh_token):
        """
        Test the refresh token logic, including token rotation and invalidation.

        This test verifies that:
        - A new access token is generated from a valid refresh token.
        - The new access token is valid and contains the correct claims.
        - A new refresh token is generated (token rotation).
        - The new refresh token is valid and contains the correct claims.
        - The old refresh token is invalidated after use (not implemented in this test).
        - Using an invalid refresh token raises an AuthenticationError.
        """
        user_id = 1
        # Create a valid refresh token
        valid_refresh_token = TokenServices.create_refresh_token(user_id)

        # Get new tokens by simulating the use of the refresh token
        TokenServices.refresh_access_token(valid_refresh_token)
        # Load refreshed tokens
        tokens = load_tokens()

        # Verify the new access token
        payload = TokenServices.verify_token(tokens['access_token'], 'access')
        assert payload['sub'] == str(user_id)
        assert payload['jti'] is not None
        assert payload['type'] == 'access'
        assert payload['iat'] is not None
        assert payload['exp'] is not None

        # Verify the new refresh token
        payload = TokenServices.verify_token(tokens['refresh_token'], 'refresh')
        assert payload['sub'] == str(user_id)
        assert payload['jti'] is not None
        assert payload['type'] == 'refresh'
        assert payload['iat'] is not None
        assert payload['exp'] is not None

        # Simulate invalidating the old refresh token (not implemented in services)
        TokenServices.invalidate_refresh_token(valid_refresh_token)

        # Test that using expired refresh token raises an AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            TokenServices.refresh_access_token(expired_refresh_token)
        assert 'Token has expired' in str(exc_info.value)
        assert 'type' not in str(exc_info.value)

        # Test that using invalid refresh token raises an AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            TokenServices.refresh_access_token('invalid.token.string')
        assert 'Invalid token' in str(exc_info.value)
        assert 'expired' not in str(exc_info.value)

        # Test that using a valid access token raises an AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            TokenServices.refresh_access_token(tokens['access_token'])
        assert 'Invalid token type' in str(exc_info.value)
        assert 'expired' not in str(exc_info.value)

class TestAuthenticationServices:

    def test_login(self, db_session, valid_user):
        """
        Test the login functionality of the AuthenticationServices.

        This test verifies that:
        - A user can log in with valid credentials and receive access and refresh tokens.
        - The tokens are saved locally in the expected file path.
        - Logging when already logged in replaces tokens with new ones.
        - Logging in with invalid email raises an AuthenticationError.
        - Logging in with invalid password raises an AuthenticationError.
        """
        # Setup:
        valid_email = valid_user.email
        valid_password = settings.COLLAB_PASSWORD_1
        invalid_email = 'thisemailisinvalid@example.com'
        invalid_password = 'wrongpassword'

        # Login with valid credentials
        AuthenticationServices.login(db_session, valid_email, valid_password)
        # Load tokens
        tokens = load_tokens()

        # Verify that the returned tokens are valid
        access_payload = TokenServices.verify_token(tokens['access_token'], 'access')
        refresh_payload = TokenServices.verify_token(tokens['refresh_token'], 'refresh')

        # Test that the payloads are not None and that the tokens are valid
        assert access_payload is not None
        assert refresh_payload is not None

        # Test that the tokens were saved locally
        token_file_path = Path.home() / ".epicevents" / "tokens.json"
        assert token_file_path.exists()

        # Test that login when already logged in:
        # - creates new tokens
        # - the new tokens are different from the old ones
        # - the token file still exists
        AuthenticationServices.login(db_session, valid_email, valid_password)

        # Test token file still exists
        assert token_file_path.exists()
        # Load tokens
        new_tokens = load_tokens()

        # Test new tokens are different than previous tokens
        assert new_tokens['access_token'] != tokens['access_token']
        assert new_tokens['refresh_token']!= tokens['refresh_token']

        # Get payloads
        new_access_payload = TokenServices.verify_token(new_tokens['access_token'], 'access')
        new_refresh_payload = TokenServices.verify_token(new_tokens['refresh_token'], 'refresh')

        # Test new payloads are different then previous payloads
        assert new_access_payload['jti'] != access_payload['jti']
        assert new_refresh_payload['jti'] != refresh_payload['jti']

        # Test that login with invalid email raises AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            AuthenticationServices.login(db_session, invalid_email, valid_password)
        assert 'Invalid email or password' in str(exc_info.value)

        # Test that login with invalid password raises AuthenticationError
        with pytest.raises(AuthenticationError) as exc_info:
            AuthenticationServices.login(db_session, valid_email, invalid_password)
        assert 'Invalid email or password' in str(exc_info.value)

    def test_get_user_id_by_token(self, db_session, valid_user):
        """Test the get_user_id_by_token authentication service method.

        Verifies that the method correctly extracts user ID from a valid access token
        and properly raises AuthenticationError for invalid tokens.

        Test scenarios:
            - Valid access token returns the expected user_id matching the authenticated user
            - Invalid token string raises AuthenticationError with 'Invalid token' message
            - Error message for invalid token does not contain 'expired' (distinguishing from
            expired token cases)
        """
        # Setup
        valid_email = valid_user.email
        valid_password = settings.COLLAB_PASSWORD_1

        # Login to get tokens
        AuthenticationServices.login(db_session, valid_email, valid_password)
        # Load tokens
        tokens = load_tokens()

        # Test get_user_id_by_token
        user_id = AuthenticationServices.get_user_id_by_token(tokens['access_token'])
        assert user_id == valid_user.id

        # Test with an invalid token
        with pytest.raises(AuthenticationError) as exc_info:
            AuthenticationServices.get_user_id_by_token('invalid.token.string')
        assert 'Invalid token' in str(exc_info.value)
        assert 'expired' not in str(exc_info.value)

    def test_logout(self, db_session, valid_user):
        """
        Test the logout functionality of the AuthenticationServices.

        This test verifies that:
        - The logout method clears the stored authentication tokens
        by deleting the token file.
        - If the token file does not exist, no errors are raised.
        """
        # Setup:
        valid_email = valid_user.email
        valid_password = settings.COLLAB_PASSWORD_1

        # Login to create token file
        AuthenticationServices.login(db_session, valid_email, valid_password)

        # Test when the token file is present
        AuthenticationServices.logout()
        assert not (Path.home() / ".epicevents" / "tokens.json").exists()
        assert not load_tokens()

        # Test when the token file is not present
        AuthenticationServices.logout()
        assert not (Path.home() / ".epicevents" / "tokens.json").exists()
        assert not load_tokens()

    def test_check_authentication_decorator(self, db_session, valid_user, expired_access_token, expired_refresh_token):
        """Test the check_authentication decorator functionality.

        Verifies that the decorator correctly handles authentication scenarios:
            - Allows execution when valid tokens are present
            - Returns None when no tokens exist
            - Handles expired access token by refreshing with valid refresh token
            - Returns None when both tokens are expired or invalid
            - Adds user info to kwargs when authentication succeeds
        """
        # Create a test function to decorate
        @AuthenticationServices.check_authentication
        def function_requiring_authentication(*args, **kwargs):
            return 'authentication_provided'

        # Test 1: No tokens exist - should raise AuthenticationError
        AuthenticationServices.logout()
        with pytest.raises(AuthenticationError) as exc_info:
            function_requiring_authentication()

        assert 'Authentication required' in str(exc_info.value)

        # Test 2: Valid tokens exist - should execute function and add user to kwargs
        valid_email = valid_user.email
        valid_password = settings.COLLAB_PASSWORD_1
        AuthenticationServices.login(db_session, valid_email, valid_password)

        # The function_requiring_authentication should execute successfully with valid tokens
        result = function_requiring_authentication()
        assert result is not None
        assert result == 'authentication_provided'

        # Test 3: Expired access token with valid refresh token - should refresh and execute
        tokens = load_tokens()
        tokens['access_token'] = expired_access_token
        save_tokens(tokens['access_token'], tokens['refresh_token'])

        result = function_requiring_authentication()
        assert result is not None
        assert result == 'authentication_provided'

        # Test 4: Both tokens expired - should raise AuthenticationError
        tokens = load_tokens()
        tokens['access_token'] = expired_access_token
        tokens['refresh_token'] = expired_refresh_token
        save_tokens(tokens['access_token'], tokens['refresh_token'])

        with pytest.raises(AuthenticationError) as exc_info:
            function_requiring_authentication()

        assert 'Session expired' in str(exc_info.value)