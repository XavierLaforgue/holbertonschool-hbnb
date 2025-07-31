from app.models.baseEntity import type_validation
from app.services.ressources import is_valid_uuid4
from app.api.v1.apiRessources import validate_init_args, CustomError
from app.models.place import Place


class PlaceService:
    """ Provides business logic and operations for Place entities"""
    @classmethod
    def create_place(cls, facade, place_data):
        """ Creates a new place with the provided data"""
        # Owner validation
        owner_id = place_data.get('owner_id')
        if owner_id is None:
            raise ValueError('Place data does not contain owner_id key')

        type_validation(owner_id, 'owner_id', str)
        if not is_valid_uuid4(owner_id):
            raise ValueError('Invalid owner_id: given owner_id is not '
                             'valid UUID4')

        # Fetch the User object
        existing_user = facade.get_user(owner_id)
        if existing_user is None:
            raise ValueError('Invalid user: no user corresponding to owner_id')

        # Replace 'owner_id' with the actual User object
        place_data.pop('owner_id')
        place_data['owner'] = existing_user

        amenities_ids = place_data.get('amenities_ids')
        if amenities_ids is not None:
            place_data.pop('amenities_ids')
            type_validation(amenities_ids, 'amenities_ids', (str | list))
        validate_init_args(Place, **place_data)
        new_place = Place(**place_data)
        facade.place_repo.add(new_place)
        if amenities_ids is not None:
            if isinstance(amenities_ids, str):
                amenities_ids = [amenities_ids]
            if isinstance(amenities_ids, list):
                for amenity_id in amenities_ids:
                    type_validation(amenity_id, 'amenity_id', str)
                    if len(amenity_id.strip()) == 0:
                        continue  # Skip empty string IDs
                    if not is_valid_uuid4(amenity_id):
                        raise ValueError(f"Given amenity_id "
                                         "'{amenity_id}' is not a "
                                         "valid UUID4")

                    # Fetch Amenity object
                    current_amenity = facade.get_amenity(amenity_id)
                    if not current_amenity:
                        raise ValueError(f"Amenity with id "
                                         "'{amenity_id}' was not "
                                         "found")
                    new_place.add_amenity(current_amenity)
        # Add to db
        facade.place_repo.add(new_place)
        return facade.place_repo.get(new_place.id)

    @classmethod
    def get_place(cls, facade, place_id):
        """ Retrieve a place by its ID """
        type_validation(place_id, 'place_id', str)
        if not is_valid_uuid4(place_id):
            raise ValueError('Invalid ID: given place_id is not a '
                             'valid UUID4')
        return facade.place_repo.get(place_id)

    @classmethod
    def update_place(cls, facade, place_id, place_data):
        """ Updates an existing place with the given data"""
        type_validation(place_id, 'place_id', str)
        # Get the place to update
        place = facade.get_place(place_id)
        # Check if place exists
        if place is None:
            return None
        owner_id = place_data.get('owner_id')
        if owner_id is None:
            raise ValueError('Place data does not contain owner_id key')
        type_validation(owner_id, 'owner_id', str)
        if not is_valid_uuid4(owner_id):
            raise ValueError('Invalid owner_id: given owner_id is not '
                             'valid UUID4')

        # Fetch the User object
        existing_user = facade.get_user(owner_id)
        if existing_user is None:
            raise CustomError('Invalid owner_id: no user corresponding'
                              ' to owner_id', 404)

        # Replace 'owner_id' with the actual User object
        place_data.pop('owner_id')
        place_data['owner'] = existing_user
        amenities_ids = place_data.get('amenities_ids')
        amenities = []
        if amenities_ids is not None:
            # Remove from update data
            place_data.pop('amenities_ids')
            type_validation(amenities_ids, 'amenities', (str | list))
            if isinstance(amenities_ids, str):
                amenities_ids = [amenities_ids]

            for amenity_id in amenities_ids:
                type_validation(amenity_id, 'amenity_id', str)
                if len(amenity_id.strip()) == 0:
                    continue  # Skip empty string IDs
                if not is_valid_uuid4(amenity_id):
                    raise ValueError(f"Given amenity_id '{amenity_id}' is not"
                                     "a valid UUID4")

                # Fetch Amenity object
                current_amenity = facade.get_amenity(amenity_id)
                if current_amenity is None:
                    raise CustomError(
                        f"Amenity with id '{amenity_id}' was not found", 404)
                amenities.append(current_amenity)
        validate_init_args(Place, **place_data)
        place_data['amenities'] = amenities
        # Update the place
        facade.place_repo.update(place_id, place_data)
        updated_place = facade.place_repo.get(place_id)
        return updated_place

    @classmethod
    def delete_place(cls, facade, place_id):
        """ Delete a place by its ID"""
        type_validation(place_id, 'place_id', str)
        if not is_valid_uuid4(place_id):
            raise ValueError('Invalid ID: given place_id is not valid UUID4')

        # Get place to make sure it exists
        place = facade.get_place(place_id)
        if place is None:
            raise CustomError('Invalid place_id: place not found', 404)
        # it shouldn't be necessary to delete manually the reviews
        # associated, SQLAlchemy should take care
        facade.place_repo.delete(place_id)
        # del place
