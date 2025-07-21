from flask_restx import Namespace, Resource, fields, _http
from flask_jwt_extended import (create_access_token, jwt_required,
                                get_jwt, get_jwt_identity,)
from app.services import facade
from app.api.v1.apiRessources import compare_data_and_model

api = Namespace('auth', description='Authentication operations')

# Model for input validation
login_model = api.model('Login', {
    'email': fields.String(required=True,
                           description='User email'),
    'password': fields.String(required=True,
                              description='User password')
})

# Model for token response
token_model = api.model('Token', {
    'access_token': fields.String(description='JWT access token')
})

# Model for error response
error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

# Model for protected access response
protected_access_model = api.model('ProtectedAccess', {
    'message': fields.String(required=True,
                             description='Protected ressource has been\
                                accessed')
})


@api.route('/login')
class Login(Resource):
    @api.doc('Returns the created access token')
    @api.expect(login_model, validate=False)
    @api.response(200, 'Token created successsfully', token_model)
    @api.response(401, 'Invalid credentials', error_model)
    def post(self):
        """Authenticate user and return a JWT token"""
        # Get the email and password from the request payload
        credentials = api.payload
        try:
            compare_data_and_model(credentials, login_model)
        # Step 1: Retrieve the user based on the provided email
            user = facade.get_user_by_email(credentials['email'])
        except Exception as e:
            api.abort(400, error=str(e))
            return {'error': str(e)}, 400
        # Step 2: Check if the user exists and the password is correct
        if (not user or not user.verify_password(credentials['password'])):
            return {'error': 'Invalid credentials'}, 401

        # Step 3: Create a JWT token with the user's id and is_admin flag
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'id': str(user.id),
                               'is_admin': user.is_admin}
            )

        # Step 4: Return the JWT token to the client
        return {'access_token': access_token}, 200
