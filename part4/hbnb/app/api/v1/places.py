from flask_restx import Namespace, Resource, fields, _http
from app.services import facade
from app.api.v1.apiRessources import (compare_data_and_model,
                                      CustomError)
from app.models.baseEntity import type_validation
from app.services.ressources import is_valid_uuid4
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


api = Namespace('places', description='Place operations')

# Define a model for nested amenity objects within a place response
amenity_response_model = api.model('PlaceAmenity', {
    'id': fields.String(required=True, description='Amenity ID'),
    'name': fields.String(required=True,
                          description='Name of the amenity')
})

# Define a model for nested owner (user) objects within a place response
user_response_model = api.model('PlaceOwner', {
    'id': fields.String(required=True, description='Owner ID'),
    'first_name': fields.String(required=True,
                                description='First name of the owner'),
    'last_name': fields.String(required=True,
                               description='Last name of the owner'),
    'email': fields.String(required=True,
                           description='Email of the owner')
})

# Define a model for nested review objects within a place response
review_response_model = api.model('PlaceReview', {
    'id': fields.String(required=True, description='Review ID'),
    'text': fields.String(required=True,
                          description='Text of the review'),
    'rating': fields.Integer(required=True,
                             description='Rating of the place (1-5)'),
    # 'attribute' maps the review's user object to its ID for the response
    'user_id': fields.String(
        attribute=lambda review: f"{review.user.id}",
        required=True,
        description='ID of the user who left the review')
})

# Define the data model for place input (e.g., for POST/PUT requests)
place_model = api.model('Place', {
    'title': fields.String(required=True,
                           description='Title of the place'),
    'description': fields.String(
        required=False,
        description='Description of the place'),
    'price': fields.Float(required=True,
                          description='Price per night'),
    'latitude': fields.Float(required=True,
                             description='Latitude of the place'),
    'longitude': fields.Float(required=True,
                              description='Longitude of the place'),
    # 'owner_id': fields.String(required=False, description='ID of the owner'),
    'amenities_ids': fields.List(fields.String, required=False,
                                 description="List of amenities ID's")
})

# Define the data model for place responses (full detail, including nested
# objects)
place_response_model = api.model('PlaceResponse', {
    'id': fields.String(required=True,
                        description='Unique identifier for the place'),
    'title': fields.String(required=True,
                           description='Title of the place'),
    'description': fields.String(
        required=False,
        description='Description of the place'),
    'price': fields.Float(required=True,
                          description='Price per night'),
    'latitude': fields.Float(required=True,
                             description='Latitude of the place'),
    'longitude': fields.Float(required=True,
                              description='Longitude of the place'),
    # Embeds the full owner object using the 'user_model'
    'owner': fields.Nested(user_response_model, required=True,
                           description='Owner of the place'),
    # Embeds the full amenity object using the 'amenity_model'
    'amenities': fields.List(fields.Nested(amenity_response_model),
                             required=True,
                             description='List of amenities'),
    # Embeds a list of review objects using the 'review_model'
    'reviews': fields.List(fields.Nested(review_response_model),
                           required=True,
                           description='List of reviews')
})

# Define the error response model
error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

# Define the success response model
msg_model = api.model('Message', {
    'message': fields.String(description='Message')
})


@api.route('/')
class PlaceList(Resource):
    # Endpoint for creating a new place
    @api.doc('Returned the created place', security='Bearer')
    @api.marshal_with(place_response_model,
                      code=_http.HTTPStatus.CREATED,
                      description='Place successfully created')
    @api.expect(place_model, validate=False)
    @api.response(201, 'Place successfully created',
                  place_response_model)
    @api.response(400, 'Invalid input data', error_model)
    @jwt_required()  # ensure the user is authenticated
    def post(self):
        """Register a new place"""
        # Check if owner is the current user's ID
        current_user = get_jwt_identity()
        # Automatically parses and validates request JSON
        place_data = api.payload
        try:
            # Validate input data
            compare_data_and_model(place_data, place_model)
            given_owner_id = place_data.get('owner_id')

            # If owner_id is provided, assign current_user as owner
            if given_owner_id is None:
                place_data['owner_id'] = current_user
            # If owner_is is provided, ensure that current_user is the
            # provided owner
            elif current_user != facade.get_user(given_owner_id).id:
                raise CustomError('Unauthorized action: user does not match'
                                  ' the provided place owner', 403)

            # Create a new place
            new_place = facade.create_place(place_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400
        return new_place, 201

    # Endpoint for retrieving all places
    @api.doc('Returns a list of all registered places')
    @api.marshal_list_with(
        place_response_model,
        code=_http.HTTPStatus.OK,
        description='List of places retrieved successfully')
    @api.response(200, 'List of places retrieved successfully',
                  place_response_model)
    def get(self):
        """Retrieve a list of all places"""
        # Call the facade to get all places
        return facade.get_all_places(), 200


class AdminPrivilegesPlaceModify(Resource):
    # Endpoint for updating an existing place by ID
    @api.doc('Returns the updated place', security='Bearer')
    @api.marshal_with(place_response_model,
                      code=_http.HTTPStatus.OK,
                      description='Place updated successfully')
    @api.expect(place_model, validate=False)
    @api.response(200, 'Place updated successfully',
                  place_response_model)
    @api.response(400, 'Invalid input data', error_model)
    @api.response(401, 'Missing authorization header', error_model)
    @api.response(403, 'Unauthorized action', error_model)
    @api.response(404, 'Place not found', error_model)
    @jwt_required()
    def put(self, place_id):
        """Update a place's information"""
        # Automatically parses and validates request JSON
        place_data = api.payload
        try:
            # Validate input data
            compare_data_and_model(place_data, place_model)
            # Retrieve the place
            place = facade.get_place(place_id)
            # Check if the place exists
            if place is None:
                raise CustomError('Invalid place_id: place not found',
                                  404)

            # Get current user ID
            current_user_id = get_jwt_identity()
            # Get admin status
            is_admin = get_jwt().get("is_admin", False)

            # Check if the owner is the current user
            if not is_admin and current_user_id != place.owner.id:
                raise CustomError('Unauthorized action: user is not owner of'
                                  ' place', 403)
            given_owner_id = place_data.get('owner_id')

            # If owner_id is not provided, current owner is retained
            if given_owner_id is None:
                place_data['owner_id'] = place.owner.id
            # If owner_id is provided, non-admin user must match the
            # authenticated user
            elif not is_admin and (given_owner_id != current_user_id):
                raise CustomError("Unauthorized action: given owner_id doesn't"
                                  " match authenticated user", 403)
            # Admin cannot change the owner of a place
            elif is_admin and given_owner_id != place.owner.id:
                raise CustomError('Unauthorized action: not even an admin can'
                                  ' change the owner of a place', 403)
            # Update place
            updated_place = facade.update_place(place_id,
                                                place_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400
        if updated_place is None:
            api.abort(404, error='Place not found')
            return {'error': 'Place not found'}, 404
        return updated_place, 200


class AdminPrivilegesPlaceDelete(Resource):
    # Endpoint for deleting a place by ID
    @api.doc('Deletes place', security='Bearer')
    @api.response(200, 'Place deleted successfully', msg_model)
    @api.response(401, 'Missing authorization header', error_model)
    @api.response(403, 'Unauthorized action', error_model)
    @api.response(404, 'Place not found', error_model)
    @jwt_required()
    def delete(self, place_id):
        """Delete a place"""
        try:
            # Get current user ID
            current_user_id = get_jwt_identity()
            # Get admin status
            is_admin = get_jwt().get('is_admin', False)
            # Retrieve the place to validate ownership
            place = facade.get_place(place_id)
            # Check if the place exists
            if place is None:
                raise CustomError('Invalid place_id: place not found', 404)
            # Check if the user is the owner or admin
            elif not is_admin and current_user_id != place.owner.id:
                raise CustomError('Unauthorized action: user is not the owner'
                                  ' of the place', 403)

            # Delete place
            facade.delete_place(place_id)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(404, error=str(e))
            return {'error': str(e)}, 404
        return {"msg": f"Place {place_id} has been succesfully deleted"}, 200


@api.route('/<place_id>')
class PlaceResource(AdminPrivilegesPlaceModify, AdminPrivilegesPlaceDelete):
    # Endpoint for retrieving a single place by ID
    @api.doc('Returns place corresponding to given ID')
    @api.marshal_with(
        place_response_model,
        code=_http.HTTPStatus.OK,
        description='Review details retrieved successfully')
    @api.response(200, 'Place details retrieved successfully',
                  place_response_model)
    @api.response(400, 'Invalid ID: not a UUID4', error_model)
    @api.response(404, 'Place not found', error_model)
    def get(self, place_id):
        """Get place details by ID"""
        try:
            place = facade.get_place(place_id)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400
        if place is None:
            api.abort(404, error='Place not found')
            return {'error': 'Place not found'}, 404
        return place, 200


@api.route('/<place_id>/reviews')
class PlaceReviewsList(Resource):
    # Endpoint for retrieving all reviews associated with a specific place
    @api.doc('Returns list of reviews given to the concerned place')
    @api.marshal_list_with(review_response_model,
                           code=_http.HTTPStatus.OK,
                           description='List of reviews given to the'
                           ' place retrieved successfully')
    @api.response(200, 'List of reviews retrieved successfully',
                  review_response_model)
    @api.response(400, "Invalid ID", error_model)
    @api.response(404, 'Place not found', error_model)
    def get(self, place_id):
        """Get list of reviews for a place given its ID"""
        try:
            # Retrieve reviews
            reviews_by_place = facade.get_reviews_by_place(place_id)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400

        # Check if the place exists
        if reviews_by_place is None:
            api.abort(404, error='Place not found')
            return {'error': 'Place not found'}, 404
        return reviews_by_place, 200
