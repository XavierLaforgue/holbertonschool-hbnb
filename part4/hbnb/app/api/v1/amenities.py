from flask_restx import Namespace, Resource, fields, _http
from app.services import facade
from app.api.v1.apiRessources import (compare_data_and_model,
                                      CustomError)
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


api = Namespace('amenities', description='Amenity operations')

# Define the amenity model for input validation and documentation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

# Define the response model for amenity operations
amenity_response_model = api.model('AmenityResponse', {
    'id': fields.String(
        required=True,
        description='Unique identifier for the amenity'),
    'name': fields.String(required=True,
                          description='Name of the amenity')
})

# Define an error response model
error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

# Define a success response model
msg_model = api.model('Message', {
    'message': fields.String(description='Message')
})


class AdminAmenityCreate(Resource):
    # Endpoint for creating a new amenity
    @api.doc('Returns the created amenity', security='Bearer')
    @api.marshal_with(amenity_response_model,
                      code=_http.HTTPStatus.CREATED,
                      description='Amenity successfully created')
    @api.expect(amenity_model, validate=False)
    @api.response(201, 'Amenity successfully created',
                  amenity_response_model)
    @api.response(400, 'Name already assigned / Invalid input data',
                  error_model)
    @jwt_required()
    def post(self):
        """Register a new amenity"""
        is_admin = get_jwt().get('is_admin', False)
        amenity_data = api.payload
        try:
            # Check for admin privileges
            if not is_admin:
                raise CustomError('Unauthorized action: admin privileges'
                                  ' required', 403)
            # Validate input data
            compare_data_and_model(amenity_data, amenity_model)

            new_amenity = facade.create_amenity(amenity_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400
        return new_amenity, 201


@api.route('/')
class AmenityList(AdminAmenityCreate):
    # Endpoint for retrieving all amenities
    @api.doc('Returns a list of all registered amenities')
    @api.marshal_list_with(
        amenity_response_model,
        code=_http.HTTPStatus.OK,
        description='List of amenities retrieved successfully')
    @api.response(200, 'List of amenities retrieved successfully',
                  amenity_response_model)
    def get(self):
        """Retrieve a list of all amenities"""
        return facade.get_all_amenities(), 200


class AdminAmenityModify(Resource):
    # Endpoint for updating an existing amenity by ID
    @api.doc('Returns the updated amenity', security='Bearer')
    @api.marshal_with(amenity_response_model,
                      code=_http.HTTPStatus.OK,
                      description='Amenity updated successfully')
    @api.expect(amenity_model, validate=False)
    @api.response(200, 'Amenity updated successfully', amenity_response_model)
    @api.response(400, 'Invalid input data', error_model)
    @api.response(403, 'Unauthorized action', error_model)
    @api.response(404, 'Amenity not found', error_model)
    @jwt_required()
    def put(self, amenity_id):
        """Update an amenity's information"""
        # Get admin status
        is_admin = get_jwt().get('is_admin')
        amenity_data = api.payload

        try:
            # Check for admin privileges
            if is_admin is None:
                raise CustomError('is_admin claim was not found in the jwt',
                                  401)
            elif not is_admin:
                raise CustomError('Admin privileges required', 403)

            # Validate input data
            compare_data_and_model(amenity_data, amenity_model)
            updated_amenity = facade.update_amenity(amenity_id,
                                                    amenity_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400
        # If the amenity is not found, return an error
        # Otherwise, return the updated amenity as a dictionary
        if updated_amenity is None:
            api.abort(404, error='Amenity not found')
            return {'error': 'Amenity not found'}, 404
        return updated_amenity, 200


class AdminPrivilegesAmenityDelete(Resource):
    # Endpoint for deleting an amenity by ID
    @api.doc('Deletes amenity', security='Bearer')
    @api.response(200, 'Amenity deleted successfully', msg_model)
    @api.response(401, 'Missing authorization header', error_model)
    @api.response(403, 'Unauthorized action', error_model)
    @api.response(404, 'Amenity not found', error_model)
    @jwt_required()
    def delete(self, amenity_id):
        """Delete a amenity"""
        try:
            # Get admin status
            is_admin = get_jwt().get('is_admin', False)
            if not is_admin:
                raise CustomError("Unauthorized action: admin privileges"
                                  "required", 403)

            # Retrieve the amenity to validate its existence
            amenity = facade.get_amenity(amenity_id)
            # Check if the amenity exists
            if amenity is None:
                raise CustomError('Invalid amenity_id: amenity not found',
                                  404)

            facade.delete_amenity(amenity_id)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(404, error=str(e))
            return {'error': str(e)}, 404
        return {
            "msg": f"Amenity {amenity_id} has been succesfully deleted"}, 200


@api.route('/<amenity_id>')
class AmenityResource(AdminAmenityModify, AdminPrivilegesAmenityDelete):
    # Endpoint for retrieving a single amenity by ID
    @api.doc('Returns amenity corresponding to given ID')
    @api.marshal_with(
        amenity_response_model,
        code=_http.HTTPStatus.OK,
        description='Amenity details retrieved successfully')
    @api.response(200, 'Amenity details retrieved successfully',
                  amenity_response_model)
    @api.response(400, 'Invalid ID: not a UUID4 / Invalid input data',
                  error_model)
    @api.response(403, 'Unauthorized action', error_model)
    @api.response(404, 'Amenity not found', error_model)
    def get(self, amenity_id):
        """Get amenity details by ID"""
        try:
            amenity = facade.get_amenity(amenity_id)
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400

        # Check if amenity exists
        if amenity is None:
            api.abort(404, error='Amenity not found')
            return {'error': 'Amenity not found'}, 404
        return amenity, 200
