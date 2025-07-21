from app.models.amenity import Amenity
from app.services.ressources import is_valid_uuid4
from app.api.v1.apiRessources import validate_init_args, CustomError
from app.models.baseEntity import type_validation


class AmenityService:
    """ Provides business logic and operations for Amenity entities"""
    @classmethod
    def create_amenity(cls, facade, amenity_data):
        """Create a new amenity with the provided data."""
        name = amenity_data.get('name')
        type_validation(name, 'name', str)
        if name is None:
            raise ValueError('Invalid name: name is required')
        # Strip white spaces
        name = name.strip()

        # Check if an amenity already exists with the same name
        all_existing_amenities = cls.get_all_amenities(facade)
        for existing_amenity in all_existing_amenities:
            if existing_amenity.name.casefold() == name.casefold():
                raise ValueError('Invalid name: name already registered')

        # Validate amenity_data matches the arguments of Amenity
        validate_init_args(Amenity, **amenity_data)
        # Create new amenity
        new_amenity = Amenity(**amenity_data)
        facade.amenity_repo.add(new_amenity)
        return facade.amenity_repo.get(new_amenity.id)

    @classmethod
    def get_amenity(cls, facade, amenity_id):
        """ Retrieve an amenity by its ID """
        type_validation(amenity_id, 'amenity_id', str)
        if not is_valid_uuid4(amenity_id):
            raise ValueError('Invalid ID: amenity_id is not a valid '
                             'UUID4')
        return facade.amenity_repo.get(amenity_id)

    @classmethod
    def get_all_amenities(cls, facade):
        """ Retrieve all amenities """
        return facade.amenity_repo.get_all()

    @classmethod
    def get_amenity_by_name(cls, facade, name):
        """ Retrieve an amenity by its name"""
        if name is None or (isinstance(name, str) and
                            len(name.strip()) == 0):
            raise ValueError('Invalid name: name is required')
        type_validation(name, 'name', str)
        return facade.amenity_repo.get_by_attribute('name', name)

    @classmethod
    def update_amenity(cls, facade, amenity_id, amenity_data):
        """ Update an amenity with the provided data """
        type_validation(amenity_id, 'amenity_id', str)
        # Get the amenity to update
        amenity = cls.get_amenity(facade, amenity_id)
        if amenity is None:
            return None
        amenity_by_name = cls.get_amenity_by_name(
                facade,
                amenity_data.get('name'))
        if amenity_by_name and amenity_by_name.id != amenity.id:
            raise ValueError('Invalid name: name is already used for '
                             'another amenity')

        # Validate update amenity_data matches the arguments of Amenity
        validate_init_args(Amenity, **amenity_data)
        # Update the amenity in the repository
        facade.amenity_repo.update(amenity_id, amenity_data)
        updated_amenity = facade.amenity_repo.get(amenity_id)
        return updated_amenity

    @classmethod
    def delete_amenity(cls, facade, amenity_id):
        """ Deletes an amenity by its ID"""
        type_validation(amenity_id, 'amenity_id', str)
        if not is_valid_uuid4(amenity_id):
            raise ValueError('Invalid ID: given amenity_id is not valid UUID4')
        # Get amenity to ensure it exists
        amenity = facade.get_amenity(amenity_id)
        if amenity is None:
            raise CustomError('Invalid amenity_id: amenity not found', 404)
        # it shouldn't be necessary to delete manually the amenities
        # associated, SQLAlchemy should take care of that
        facade.amenity_repo.delete(amenity_id)
        # del place
