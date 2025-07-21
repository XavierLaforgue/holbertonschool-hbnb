from app.models.baseEntity import type_validation
from app.services.ressources import is_valid_uuid4
from app.api.v1.apiRessources import validate_init_args, CustomError
from app.models.review import Review


class ReviewService:
    """ Provides business logic and operations for Review entities"""
    @classmethod
    def create_review(cls, facade, review_data):
        """ Create a new review"""
        # Get the user_id
        user_id = review_data.get('user_id')
        if user_id is None:
            raise ValueError('Review data does not contain user_id key')
        type_validation(user_id, 'user_id', str)
        if not is_valid_uuid4(user_id):
            raise ValueError(
                'Invalid user_id: given user_id is not valid UUID4')

        # Get the place_id
        place_id = review_data.get('place_id')
        if place_id is None:
            raise ValueError('Review data does not contain place_id key')
        if not is_valid_uuid4(place_id):
            raise ValueError(
                'Invalid place_id: given place_id is not valid UUID4')
        existing_user = facade.get_user(user_id)
        if existing_user is None:
            raise ValueError('No User corresponding to given ID')
        existing_place = facade.get_place(place_id)
        if existing_place is None:
            raise ValueError('No Place corresponding to given place '
                             'ID')

        # Prevent user from retrieving their own place
        if existing_user == existing_place.owner:
            raise CustomError('User cannot review their own place', 400)
        # Prevent duplicate reviews for the same place by the same user
        existing_review = facade.get_review_by_place_and_user(
            place_id, user_id)
        if existing_review is not None:
            raise ValueError(
                'User already left a review for this place')

        review_data.pop('user_id')
        review_data['user'] = existing_user
        review_data.pop('place_id')
        review_data['place'] = existing_place

        validate_init_args(Review, **review_data)
        new_review = Review(**review_data)  # Instantiate Review object
        facade.review_repo.add(new_review)
        return facade.review_repo.get(new_review.id)

    @classmethod
    def get_review(cls, facade, review_id):
        """ Get review by its ID"""
        type_validation(review_id, 'review_id', str)
        if not is_valid_uuid4(review_id):
            raise ValueError('Invalid ID: given review_id is not valid UUID4')
        return facade.review_repo.get(review_id)

    @classmethod
    def get_reviews_by_place(cls, facade, place_id):
        # Get all reviews for a specific place
        type_validation(place_id, 'place_id', str)
        if not is_valid_uuid4(place_id):
            raise ValueError('Invalid ID: given place_id is not valid UUID4')
        place = facade.get_place(place_id)
        if place is None:
            return None
        return place.reviews

    @classmethod
    def get_review_by_place_and_user(cls, facade, place_id, user_id):
        """ Get a specific review for a place written by a specific user"""
        type_validation(place_id, 'place_id', str)
        if not is_valid_uuid4(place_id):
            raise ValueError('Invalid ID: given place_id is not valid UUID4')

        existing_place = facade.get_place(place_id)
        if existing_place is None:
            raise CustomError(
                'Invalid place_id: no place corresponding to that place_id',
                400)

        type_validation(user_id, 'user_id', str)
        if not is_valid_uuid4(user_id):
            raise ValueError('Invalid ID: given user_id is not valid UUID4')

        existing_user = facade.get_user(user_id)
        if existing_user is None:
            raise CustomError(
                'Invalid user_id: no user corresponding to that user_id', 400)

        # Get all reviews for a place
        reviews = facade.get_reviews_by_place(place_id)
        if reviews is None:
            return None

        type_validation(reviews, "reviews", list)
        for review in reviews:
            if review.user.id == user_id:
                return review
        return None

    @classmethod
    def update_review(cls, facade, review_id, review_data):
        """ Updates an existing review"""
        type_validation(review_id, 'review_id', str)
        if not is_valid_uuid4(review_id):
            raise ValueError('Invalid ID: given review_id is not valid UUID4')

        # Get the review to update
        review = facade.get_review(review_id)
        if review is None:
            raise CustomError("Invalid review_id: review not found", 404)
        # Validate update data
        validate_init_args(Review, **review_data)
        facade.review_repo.update(review_id, review_data)

        updated_review = facade.review_repo.get(review_id)
        return updated_review

    @classmethod
    def delete_review(cls, facade, review_id):
        """ Deletes a review by its ID """
        type_validation(review_id, 'review_id', str)
        if not is_valid_uuid4(review_id):
            raise ValueError('Invalid ID: given review_id is not valid UUID4')

        # Get the review to ensure it exists
        review = facade.get_review(review_id)
        if review is None:
            raise CustomError('Invalid review_id: review not found', 404)
        for review_in_place in review.place.reviews:
            if review_in_place == review:
                review.place.reviews.remove(review)

        facade.review_repo.delete(review_id)
        del review
