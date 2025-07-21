from flask_restx import Namespace, Resource, fields, _http
from app.services import facade
from app.api.v1.apiRessources import (compare_data_and_model,
                                      CustomError)
from app.models.baseEntity import type_validation
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the '
                          'review'),
    'rating': fields.Integer(required=True, description='Rating of the'
                             ' place (1-5)'),
    # 'user_id': fields.String(required=False, description='ID of the '
    #                          'user'),
    'place_id': fields.String(required=True, description='ID of the '
                              'place')
})

# Define the data model for review responses (full detail, including linked
# IDs)
review_response_model = api.model('ReviewResponse', {
    'id': fields.String(required=True, description='ID of the review'),
    # 'attribute' maps the review's user object to its ID for the response
    'user_id': fields.String(
        attribute=lambda review: f"{review.user.id}",
        required=True, description='ID of the user'),
    'place_id': fields.String(
        attribute=lambda review: f"{review.place.id}",
        required=True, description='ID of the place'),
    'text': fields.String(required=True,
                          description='Text of the review'),
    'rating': fields.Integer(required=True,
                             description='Rating of the place (1-5)')
})

# Define the update review response model
update_review_model = api.model('UpdateReview', {
    'text': fields.String(required=False, description='New text of the'
                          ' review'),
    'rating': fields.Integer(required=False, description='New rating '
                             'of the place (1-5)')})

# Define error response model
error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

# Define success response model
msg_model = api.model('Message', {
    'message': fields.String(description='Message')
})


@api.route('/')
class ReviewList(Resource):
    # Endpoint for creating a new review
    @api.doc('Returns the created review', security='Bearer')
    @api.marshal_with(review_response_model,
                      code=_http.HTTPStatus.CREATED,
                      description='Review successfully created')
    @api.expect(review_model, validate=False)
    @api.response(201, 'Review successfully created',
                  review_response_model)
    @api.response(400, 'Invalid input data', error_model)
    @api.response(404, 'Place not found', error_model)
    @jwt_required()
    def post(self):
        """Register a new review"""
        # Automatically parses and validates request JSON
        review_data = api.payload
        try:
            # Validate input data
            compare_data_and_model(review_data, review_model)
            # Get current user ID
            current_user_id = get_jwt_identity()
            given_user_id = review_data.get('user_id')
            if given_user_id is None:
                # Set user_id to the authenticated user's ID
                review_data['user_id'] = current_user_id
            elif current_user_id != given_user_id:
                raise CustomError(
                    'Unauthorized action: authenticated user does not match'
                    ' provided review author. User is not allowed to create a'
                    ' review for another user', 403)
            # Retrieve the place_id
            given_place_id = review_data.get('place_id')
            if given_place_id is None:
                raise CustomError('Expected place_id but received None', 400)
            # Retrieve the place to validate ownership
            place = facade.get_place(given_place_id)
            if place is None:
                raise CustomError("Invalid place_id: given place_id doesn't"
                                  " correspond to an registered place", 400)
            # Check if the current user tries to review their own place
            if place.owner.id == current_user_id:
                raise CustomError('User can not review their own place', 403)
            # Check if the review already exists
            existing_review = facade.get_review_by_place_and_user(
                given_place_id, current_user_id)
            if existing_review is not None:
                raise CustomError('User has already reviewed this place', 403)

            # Create new review
            new_review = facade.create_review(review_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400
        return new_review, 201

    # Endpoint for retrieving all reviews
    @api.doc('Returns a list of all reviews')
    @api.marshal_list_with(review_response_model,
                           code=_http.HTTPStatus.OK,
                           description='List of reviews retrieved'
                           ' successfully')
    @api.response(200, 'List of reviews retrieved successfully',
                  review_response_model)
    def get(self):
        """Retrieve a list of all reviews"""
        return facade.get_all_reviews(), 200


class AdminPrivilegesReviewModify(Resource):
    """ Handles updating an existing review 
    Requires the author of the review or the admin privileges"""
    # Endpoint for updating an existing review by ID
    @api.doc('Returns the updated review', security='Bearer')
    @api.marshal_with(review_response_model, code=_http.HTTPStatus.OK,
                      description='Review updated successfully')
    @api.expect(update_review_model, validate=False)
    @api.response(200, 'Review updated successfully',
                  review_response_model)
    @api.response(400, 'Invalid input data', error_model)
    @api.response(403, 'Unauthorized action', error_model)
    @api.response(404, 'Review not found', error_model)
    @jwt_required()
    def put(self, review_id):
        """Update a review's information"""
        review_data = api.payload
        try:
            # Validate the input data
            compare_data_and_model(review_data, update_review_model)
            # Retrieve the review
            review = facade.get_review(review_id)

            # Check if the review exists
            if review is None:
                raise CustomError('Invalid review_id: review not found', 404)
            # Get the current user ID
            current_user_id = get_jwt_identity()
            # Check if user tries to change a review given to their place
            if current_user_id == review.place.owner.id:
                raise CustomError('Unauthorized action: user can not leave a'
                                  ' review on their own place', 403)

            # Get the admin status
            is_admin = get_jwt().get('is_admin', False)
            # Check if the author of the review is the authenticated user
            if not is_admin and current_user_id != review.user.id:
                raise CustomError('Unauthorized action: user is not the author'
                                  ' of the review', 403)

            # The current_user_id should match the user_id
            given_user_id = review_data.get('user_id')
            if given_user_id is None:
                review_data['user_id'] = current_user_id
            elif not is_admin and (current_user_id != given_user_id):
                raise CustomError("Unauthorized action: given user_id doesn't"
                                  " match authenticated user", 403)
            elif is_admin and (given_user_id != review.user.id):
                raise CustomError('Unauthorized action: not even an admin can'
                                  ' change the author of a review', 403)

            # Prevent changing place_id
            given_place_id = review_data.get('place_id')
            if given_place_id is None:
                review_data['place_id'] = review.place.id
            elif given_place_id != review.place.id:
                raise CustomError(
                    'Unauthorized action: user can not change the place for'
                    ' which the original review was given', 403)

            review_data.pop('user_id')
            review_data['user'] = review.user
            review_data.pop('place_id')
            review_data['place'] = review.place

            # Update review
            updated_review = facade.update_review(review_id,
                                                  review_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400
        if updated_review is None:
            api.abort(404, error='Updated review not found')
            return {'error': 'Updated review not found'}, 404
        return updated_review, 200


class AdminPrivilegesReviewDelete(Resource):
    # Endpoint for deleting a review by ID
    @api.doc('Deletes review', security='Bearer')
    @api.response(200, 'Review deleted successfully', msg_model)
    @api.response(401, 'Missing authorization header', error_model)
    @api.response(403, 'Unauthorized action', error_model)
    @api.response(404, 'Review not found', error_model)
    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        try:
            # Get current user ID
            current_user_id = get_jwt_identity()
            # Get admin status
            is_admin = get_jwt().get('is_admin', False)
            # Retrieve the review to validate ownership
            review = facade.get_review(review_id)

            # Check if the review already exists
            if review is None:
                raise CustomError('Invalid review_id: review not found', 404)
            # Check if the creator of the review is the current user
            elif not is_admin and current_user_id != review.user.id:
                raise CustomError('Unauthorized action: user is not the author'
                                  ' of the review', 403)

            # Delete review
            facade.delete_review(review_id)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(404, error=str(e))
            return {'error': str(e)}, 404
        return {"msg": f"Review {review_id} has been succesfully deleted"}, 200


@api.route('/<review_id>')
class ReviewResource(AdminPrivilegesReviewModify, AdminPrivilegesReviewDelete):
    # Endpoint for retrieving a single review by ID
    @api.doc('Returns review corresponding to given ID')
    @api.marshal_with(review_response_model,
                      code=_http.HTTPStatus.OK,
                      description='Review details retrieved successfully')
    @api.response(200, 'Review details retrieved successfully',
                  review_response_model)
    @api.response(400, 'Invalid ID: not a UUID4', error_model)
    @api.response(404, 'Review not found', error_model)
    def get(self, review_id):
        """Get review details by ID"""
        try:
            # Retrieve review
            review = facade.get_review(review_id)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error', str(e)}, 400
        if review is None:
            api.abort(404, error='Review not found')
            return {'error': 'Review not found'}, 404
        return review, 200


@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    # Endpoint for retrieving reviews specific to a place
    @api.doc('Returns the list of reviews given to the concerned '
             ' place')
    @api.marshal_list_with(review_response_model,
                           code=_http.HTTPStatus.OK,
                           description='List of reviews given to the place'
                           ' retrieved successfully')
    @api.response(200, 'List of reviews for the place retrieved successfully',
                  review_response_model)
    @api.response(400, 'Invalid ID', error_model)
    @api.response(404, 'Place not found', error_model)
    def get(self, place_id):
        """Get all reviews for a specific place"""
        try:
            # Retrieve all reviews for a place
            reviews_by_place = facade.get_reviews_by_place(place_id)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400

        # Check if the list is empty
        if reviews_by_place is None:
            api.abort(404, error='Place not found')
            return {'error': 'Place not found'}, 404
        return reviews_by_place, 200
