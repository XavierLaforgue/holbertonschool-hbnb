"""
UserService module.

Provides class methods for user-related business logic, including
creation, retrieval, and update operations.

Classes:
    UserService: Contains class methods to manage User entities using
    a facade to access the persistence.

Methods:
    create_user(facade, user_data):
        Create a new user with the provided data. Raises ValueError if
        email is missing or already registered.
    get_user(facade, user_id):
        Retrieve a user by their UUID4 ID. Raises ValueError if the ID
        is not valid.
    get_all_users(facade):
        Retrieve all users from the repository.
    get_user_by_email(facade, email):
        Retrieve a user by their email address.
    update_user(facade, user_id, user_data):
        Update an existing user's data. Raises ValueError if the email
        is used by another user. Raises TypeError if provided data
        doesn't lead to acceptable inputs for the User class.
"""

from app.models.user import User
from app.services.ressources import is_valid_uuid4
from app.api.v1.apiRessources import (validate_init_args, CustomError)
from validate_email_address import validate_email
from app.models.baseEntity import type_validation


class UserService:
    """
    Service class for user-related business logic.

    All methods are class methods and operate from and through the
    facade.
    """

    @classmethod
    def create_user(cls, facade, user_data):
        """Create a new user with the provided data.

        Args:
            facade: The business logic facade with user_repo.
            user_data (dict): Data for the new user.
        Returns:
            User: The created user object.
        Raises:
            ValueError: If email is missing or already registered.
        """
        email = user_data.get('email')
        type_validation(email, 'email', str)
        if email is None:
            raise ValueError('Invalid email: email is required')

        # Check for existing user with the same email
        existing_user = cls.get_user_by_email(facade, email)
        if existing_user:
            raise CustomError('Invalid email: email already registered', 400)

        validate_init_args(User, **user_data)
        user = User(**user_data)
        facade.user_repo.add(user)
        return facade.user_repo.get(user.id)

    @classmethod
    def get_user(cls, facade, user_id):
        """Retrieve a user by their ID.

        Args:
            facade: The business logic facade linked to the
                persistence.
            user_id (str): The user's UUID4 ID.
        Returns:
            User or None: The user object if found, else None.
        Raises:
            ValueError: If user_id is not a valid UUID4.
        """
        type_validation(user_id, 'user_id', str)
        if not is_valid_uuid4(user_id):
            raise ValueError('Invalid ID: given user_id is not a valid'
                             ' UUID4')
        return facade.user_repo.get(user_id)

    @classmethod
    def get_all_users(cls, facade):
        """Retrieve all users from the repository.

        Args:
            facade: The business logic facade linking with the
                persistence.
        Returns:
            list: List of all user objects.
        """
        return facade.user_repo.get_all()

    @classmethod
    def get_user_by_email(cls, facade, email):
        """Retrieve a user by their email address.

        Args:
            facade: The business logic facade linking with the
                persistence.
            email (str): The user's email address.
        Returns:
            User or None: The user object if found, else None.
        """
        type_validation(email, 'email', str)
        if not validate_email(email):
            raise ValueError("Invalid email: email must have format"
                             " example@exam.ple")
        return facade.user_repo.get_by_attribute('email', email)

    @classmethod
    def update_user(cls, facade, user_id, user_data):
        """Update an existing user's data.

        Args:
            facade: The business logic facade linking with the
                persistence.
            user_id (str): The user's UUID4 ID.
            user_data (dict): The new data for the user.
        Returns:
            User or None: The updated user object if found, else None.
        Raises:
            ValueError: If the email is used by another user.
            TypeError: If any argument required by the User class is
                missing from the provided data or if, on the contrary,
                an unexpected key-value pair is contained in the
                provided data.
        """
        type_validation(user_id, 'user_id', str)
        user = cls.get_user(facade, user_id)
        if user is None:
            return None

        # Check if email is unique, if email is being updated
        if user_data.get('email') is not None:
            user_by_email = cls.get_user_by_email(
                facade, user_data.get('email'))
            if user_by_email and user_by_email.id != user.id:
                raise ValueError(
                    'Invalid email: email already used by another user')
        # We do not need to provide all input arguments of User, only
        # those we want to change:
        # validate_init_args(User, **user_data)
        facade.user_repo.update(user_id, user_data)
        updated_user = facade.user_repo.get(user_id)
        return updated_user

    @classmethod
    def delete_user(cls, facade, user_id):
        """ Deletes a user"""
        type_validation(user_id, 'user_id', str)
        if not is_valid_uuid4(user_id):
            raise ValueError('Invalid ID: given user_id is not valid UUID4')
        user = facade.get_user(user_id)
        if user is None:
            raise CustomError('Invalid user_id: user not found', 404)
        from run import app
        deleted_user_email = app.config.get("DELETED_USER_EMAIL", None)
        deleted_user = None
        if deleted_user_email is not None:
            deleted_user = facade.get_user_by_email(deleted_user_email)
        if deleted_user is None:
            raise CustomError(
                "User stand-in was not found, user and every related entity"
                "may be deleted in its absence", 404)
        for review in user.reviews:
            review.user = deleted_user
        # it shouldn't be necessary to delete manually the places
        # associated, SQLAlchemy should take care
        facade.user_repo.delete(user_id)
        # del user
