from flask_restx import Namespace, Resource, fields, _http
from app.services import facade
from app.api.v1.apiRessources import (compare_data_and_model,
                                      CustomError)
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True,
                                description='First name of the user'),
    'last_name': fields.String(required=True,
                               description='Last name of the user'),
    'email': fields.String(required=True,
                           description='Email of the user'),
    'password': fields.String(required=True,
                              description='Password of the user')
})

# Define the user response model
user_response_model = api.model('UserResponse', {
    'id': fields.String(required=True,
                        description='ID of the user'),
    'first_name': fields.String(required=True,
                                description='First name of the user',
                                attribute='first_name'),
    'last_name': fields.String(required=True,
                               description='Last name of the user',
                               attribute='last_name'),
    'email': fields.String(required=True,
                           description='Email of the user', attribute='email')
})

# Define the updating user data response model
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(required=False,
                                description='First name of the user',
                                attribute='first_name'),
    'last_name': fields.String(required=False,
                               description='Last name of the user',
                               attribute='last_name'),
    'email': fields.String(required=False,
                           description='Email of the user',
                           attribute='email'),
    'password': fields.String(required=False,
                              description='Password of the user',
                              attribute='password')
})

# Define an error response model
error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

# Define a success response model
msg_model = api.model('Message', {
    'message': fields.String(description='Message')
})


class AdminUserCreate(Resource):
    """ Handles creating user accounts requiring admin privileges"""
    @api.doc('Returns the created user', security='Bearer')
    @api.marshal_with(user_response_model,
                      code=_http.HTTPStatus.CREATED,
                      description='User successfully created')
    @api.expect(user_model, validate=False)
    @api.response(201, 'User successfully created',
                  user_response_model)
    @api.response(400, 'Email already registered / Invalid input data',
                  error_model)
    @api.response(403, 'Admin privilees required', error_model)
    @jwt_required()
    def post(self):
        """Register a new user"""
        # Get current user ID
        current_user = get_jwt()

        # Check if the authenticated user is admin
        if not current_user.get('is_admin'):
            api.abort(403, error='Admin privileges required')
            return {'error': 'Admin privileges required'}, 403

        # Automatically parses and validates request JSON
        user_data = api.payload
        try:
            # Validate input data
            compare_data_and_model(user_data, user_model)
            new_user = facade.create_user(user_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400

        # Unexpected facade behavior
        if new_user is None:
            api.abort(500,
                      error='Something happened and the user was not created')
            return {
                'error': 'Something happened and the user was not created'}, 400
        return new_user, 201


@api.route('/')
class UserList(AdminUserCreate):
    @api.doc('Returns list of registered users')
    @api.marshal_list_with(user_response_model,
                           code=_http.HTTPStatus.OK,
                           description='List of users retrieved successfully')
    @api.response(200, 'List of users retrieved successfully',
                  user_response_model)
    def get(self):
        """Get a list of registered users"""
        return facade.get_all_users(), 200


class AdminPrivilegesUserModify(Resource):
    """Handles updating user
    Require admin privileges"""
    @api.doc('Returns the updated user', security='Bearer')
    @api.marshal_with(user_response_model,
                      code=_http.HTTPStatus.OK,
                      description='User updated successfully')
    @api.expect(user_update_model, validate=False)
    @api.response(200, 'User successfully updated',
                  user_response_model)
    @api.response(400, 'Invalid input data', error_model)
    @api.response(401, 'Missing authorization header', error_model)
    @api.response(403, 'Unauthorized action', error_model)
    @api.response(404, 'User not found', error_model)
    @jwt_required()  # ensure the user is authenticated
    def put(self, user_id):
        """Update the user data of a registered user by ID"""
        user_data = api.payload
        try:
            # Validate input data
            compare_data_and_model(user_data, user_update_model)
            # Retrieve the user to be updated
            user = facade.get_user(user_id)

            # Check if the user exists
            if user is None:
                raise CustomError(
                    'Invalid user_id: no user found corresponding to that'
                    ' user_id', 404)

            # Get current user ID
            current_user = get_jwt_identity()
            # Get admin status
            is_admin = get_jwt().get('is_admin', False)
            # Check the user_id in the URL matches the authenticated user
            if not is_admin and current_user != user.id:
                raise CustomError(
                    'Unauthorized action: you can not modify the user account'
                    ' of somebody else', 403)

            # Restrictions for non-admin users attempting to change
            # email and password
            given_email = user_data.get('email')
            given_password = user_data.get("password")
            if not is_admin and (
                (given_email is not None and user.email != given_email) or
                (given_password is not None and not user.verify_password
                 (given_password))):
                raise CustomError(
                    'You cannot modify email or password action', 400)

            # Update user
            updated_user = facade.update_user(user_id, user_data)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400
        if updated_user is None:
            api.abort(404, error='User not found')
            return {'error': 'User not found'}, 404
        return updated_user, 200


class AdminPrivilegesUserDelete(Resource):
    # Endpoint for deleting a user by ID
    @api.doc('Deletes user', security='Bearer')
    @api.response(200, 'User deleted successfully', msg_model)
    @api.response(401, 'Missing authorization header', error_model)
    @api.response(403, 'Unauthorized action', error_model)
    @api.response(404, 'User not found', error_model)
    @jwt_required()  # Requires authentication
    def delete(self, user_id):
        """Delete a user"""
        try:
            # Get current user ID
            current_user_id = get_jwt_identity()
            # Get admin status
            is_admin = get_jwt().get('is_admin', False)
            # Retrieve the user to validate its existence
            user = facade.get_user(user_id)
            # Check if the user exists
            if user is None:
                raise CustomError('Invalid user_id: user not found', 404)
            # Check if the owner of the place is the current user
            elif not is_admin and current_user_id != user.id:
                raise CustomError(
                    'Unauthorized action: user can not delete other users',
                    403)

            # Delete user
            facade.delete_user(user_id)
        except CustomError as e:
            api.abort(e.status_code, error=str(e))
            return {'error': str(e)}, e.status_code
        except Exception as e:
            api.abort(404, error=str(e))
            return {'error': str(e)}, 404
        return {"msg": f"User {user_id} has been succesfully deleted"}, 200


@api.route('/<user_id>')
class UserResource(AdminPrivilegesUserModify, AdminPrivilegesUserDelete):
    @api.doc('Returns user corresponding to given ID')
    @api.marshal_with(user_response_model,
                      code=_http.HTTPStatus.OK,
                      description='User details retrieved successfully')
    @api.response(200, 'User details retrieved successfully',
                  user_response_model)
    @api.response(400, 'Invalid ID: not a UUID4 / Invalid input data',
                  error_model)
    @api.response(404, 'User not found', error_model)
    def get(self, user_id):
        """Get user details by ID"""
        try:
            # Retrieve user
            user = facade.get_user(user_id)
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400

        # Check if user exists
        if user is None:
            api.abort(404, error='User not found')
            return {'error': 'User not found'}, 404
        return user, 200
