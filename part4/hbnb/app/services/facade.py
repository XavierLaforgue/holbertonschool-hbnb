from app.persistence.repository import SQLAlchemyRepository
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review
from app.services.UserService import UserService
from app.services.PlaceService import PlaceService
from app.services.AmenityService import AmenityService
from app.services.ReviewService import ReviewService


class HBnBFacade:
    def __init__(self):
        self.user_repo = SQLAlchemyRepository(User)
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)

# Services for User CRUD operations ####

    def create_user(self, user_data):
        """Create a new user with the provided data."""
        return UserService.create_user(self, user_data)

    def get_user(self, user_id):
        """Retrieve a user by their ID."""
        return UserService.get_user(self, user_id)

    def get_all_users(self):
        """Retrieve all users from the repository."""
        return self.user_repo.get_all()

    def get_user_by_email(self, email):
        """Retrieve a user by their email address."""
        return UserService.get_user_by_email(self, email)

    def update_user(self, user_id, user_data):
        """Update an existing user's data."""
        return UserService.update_user(self, user_id, user_data)

    def delete_user(self, user_id):
        """ Delete a user """
        return UserService.delete_user(self, user_id)

# Services for Amenity CRUD operations ########

    def create_amenity(self, amenity_data):
        """Create a new amenity with the provided data."""
        return AmenityService.create_amenity(self, amenity_data)

    def get_amenity(self, amenity_id):
        """ Retrieve an amenity by its ID """
        return AmenityService.get_amenity(self, amenity_id)

    def get_all_amenities(self):
        """ Retrieve all amenities """
        return self.amenity_repo.get_all()

    def get_amenity_by_name(self, name):
        return AmenityService.get_amenity_by_name(self, name)

    def update_amenity(self, amenity_id, amenity_data):
        """ Update an amenity with the provided data """
        return AmenityService.update_amenity(self, amenity_id,
                                             amenity_data)

    def delete_amenity(self, amenity_id):
        """ Delete an amenity """
        return AmenityService.delete_amenity(self, amenity_id)

# Services for Place CRUD operations ####

    def create_place(self, place_data):
        """ Create a new place with the provided data """
        return PlaceService.create_place(self, place_data)

    def get_place(self, place_id):
        """ Retrieve a place by its ID """
        return PlaceService.get_place(self, place_id)

    def get_all_places(self):
        """ Retrieve all places """
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        """ Update a place with the provided data """
        return PlaceService.update_place(self, place_id, place_data)

    def delete_place(self, place_id):
        """ Delete a place """
        return PlaceService.delete_place(self, place_id)

# Services for Review CRUD operations ########

    def create_review(self, review_data):
        return ReviewService.create_review(self, review_data)

    def get_review(self, review_id):
        return ReviewService.get_review(self, review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return ReviewService.get_reviews_by_place(self, place_id)

    def get_review_by_place_and_user(self, place_id, user_id):
        return ReviewService.get_review_by_place_and_user(
            self, place_id, user_id)

    def update_review(self, review_id, review_data):
        return ReviewService.update_review(self, review_id,
                                           review_data)

    def delete_review(self, review_id):
        ReviewService.delete_review(self, review_id)
