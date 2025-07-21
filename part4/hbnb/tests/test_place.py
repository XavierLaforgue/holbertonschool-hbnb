import unittest
from app.models.place import Place
from app.models.user import User
from app.models.review import Review
from app.models.amenity import Amenity


class TestPlace(unittest.TestCase):
    def setUp(self):
        self.owner = User(first_name="John", last_name="Doe",
                          email="john@doe.com", is_admin=False,
                          password="password")
        self.valid_data = {
            'title': 'Nice Place',
            'description': 'A lovely place to stay',
            'price': 100.0,
            'latitude': 45.0,
            'longitude': 90.0,
            'owner': self.owner
        }

    def test_place_creation_valid(self):
        place = Place(**self.valid_data)
        self.assertEqual(place.title, self.valid_data['title'])
        self.assertEqual(place.description, self.valid_data['description'])
        self.assertEqual(place.price, float(self.valid_data['price']))
        self.assertEqual(place.latitude, float(self.valid_data['latitude']))
        self.assertEqual(place.longitude, float(self.valid_data['longitude']))
        self.assertEqual(place.owner, self.owner)
        self.assertEqual(place.reviews, [])
        self.assertEqual(place.amenities, [])

    def test_invalid_title(self):
        with self.assertRaises(ValueError):
            Place(title='abc', description='desc', price=10,
                  latitude=0, longitude=0, owner=self.owner)
        with self.assertRaises(TypeError):
            Place(title=123, description='desc', # type: ignore
                  price=10, latitude=0, longitude=0, owner=self.owner)
        with self.assertRaises(ValueError):
            Place(title=None, description='desc', # type: ignore
                  price=10, latitude=0, longitude=0, owner=self.owner)

    def test_no_description(self):
        place = Place(title='Valid Title', price=10, latitude=0,
                      longitude=0, owner=self.owner)
        self.assertEqual(place.title, 'Valid Title')
        self.assertEqual(place.description, None)
        self.assertEqual(place.price, 10)
        self.assertEqual(place.latitude, 0)

    def test_invalid_description(self):
        with self.assertRaises(ValueError):
            Place(title='Valid Title', description='abc'*50, price=10,
                  latitude=0, longitude=0, owner=self.owner)
        with self.assertRaises(TypeError):
            Place(title='Valid Title', description=123, price=10,
                  latitude=0, longitude=0, owner=self.owner)

    def test_invalid_price(self):
        with self.assertRaises(TypeError):
            Place(title='Valid', description='Valid',
                  price='free', # type: ignore
                  latitude=0, longitude=0, owner=self.owner)
        with self.assertRaises(TypeError):
            Place(title='Valid', description='Valid', # type: ignore
                  latitude=0, longitude=0, owner=self.owner) 
        with self.assertRaises(ValueError):
            Place(title='Valid', description='Valid', price=-10,
                  latitude=0, longitude=0, owner=self.owner)
        with self.assertRaises(ValueError):
            Place(title='Valid', description='Valid', price=0,
                  latitude=0, longitude=0, owner=self.owner)

    def test_invalid_latitude(self):
        with self.assertRaises(TypeError):
            Place(title='Valid', description=None, price=10,
                  latitude='north', # type: ignore
                  longitude=0, owner=self.owner)
        with self.assertRaises(TypeError):
            Place(title='Valid', description='Valid', price=10,
                  longitude=0, owner=self.owner) # type: ignore
        with self.assertRaises(ValueError):
            Place(title='Valid', description='Valid', price=10,
                  latitude=100, longitude=0, owner=self.owner)
        with self.assertRaises(ValueError):
            Place(title='Valid', description='Valid', price=10,
                  latitude=-480, longitude=0, owner=self.owner)

    def test_invalid_longitude(self):
        with self.assertRaises(TypeError):
            Place(title='Valid', description='Valid', price=10,
                  latitude=0, longitude='east', # type: ignore
                  owner=self.owner)
        with self.assertRaises(TypeError):
            Place(title='Valid', description='Valid', price=10,
                  latitude=0, owner=self.owner) # type: ignore
        with self.assertRaises(TypeError):
            Place(title='Valid', description='Valid', price=10,
                  latitude=0, owner=self.owner) # type: ignore
        with self.assertRaises(ValueError):
            Place(title='Valid', description='Valid', price=10,
                  latitude=0, longitude=200, owner=self.owner)

    def test_invalid_owner(self):
        with self.assertRaises(TypeError):
            Place(title='Valid', description='Valid', price=10,
                  latitude=0, longitude=0,
                  owner='not_a_user') # type: ignore
        with self.assertRaises(TypeError):
            Place(title='Valid', description='Valid', price=10,
                  latitude=0, longitude=0) # type: ignore

    def test_add_review_and_amenity(self):
        visitor = User("Johnny", "Walker", "johnny@yahoo.com",
                       "password")
        visitor2 = User("Jamie", "Walker", "jamie@yahoo.com",
                       "password2")
        place = Place(**self.valid_data)
        # Should raise TypeError for wrong types
        with self.assertRaises(TypeError):
            place.add_review("not_a_review")
        with self.assertRaises(TypeError):
            place.add_amenity("not_an_amenity")
        # Should work for correct types
        review = Review("Great stay!", 5, place, visitor)
        amenity = Amenity("Wi-Fi")
        review2 = Review("Horrible kitchen!", 2, place, visitor2)
        amenity2 = Amenity("Kitchen")
        place.add_review(review)
        place.add_amenity(amenity)
        self.assertIn(review, place.reviews)
        self.assertIn(amenity, place.amenities)
        place.add_review(review2)
        place.add_amenity(amenity2)
        self.assertIn(review, place.reviews)
        self.assertIn(amenity, place.amenities)
        self.assertIn(review2, place.reviews)
        self.assertIn(amenity2, place.amenities)

if __name__ == "__main__":
    unittest.main()
