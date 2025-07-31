from app import create_app
from flask import redirect

app = create_app(config_class="config.DevelopmentConfig")

if __name__ == '__main__':
    try:
        from app.models.user import User
        from app.models.place import Place
        from app.models.amenity import Amenity
        from app.models.review import Review
        with app.app_context():
            User.query.count()
            Place.query.count()
            Amenity.query.count()
            Review.query.count()
    except Exception as e:
        # exit(str(e))
        exit("Database or some table(s) does not exist. Execute create_tables.sql script before proceeding.")
    app.run()


##########################
########## TODO ##########
##########################
# Status code DELETE 204
# Place not found when searching all reviews for a place
# Implement PATCH if possible
# Implement add amenity
# Check that email and name (unique keys) are case-independent and that
#   name is independent of number of spaces between words
# Error due to conflict (e.g., Amenity name already exists) is code 409
# Add a message to all server responses: "{{msg: User created
# successfully}, {id: "00diunfw", name: "john", ...}} instead of just
# the object or the error message.
# Avoid amenities with same name with just different capitalization
# Avoid adding the same amenitiy multiple times to a Place
