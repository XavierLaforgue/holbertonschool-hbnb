import unittest
from app.models.review import Review
from app.models.place import Place
from app.models.user import User
from app.api.v1.apiRessources import CustomError


class TestReview(unittest.TestCase):
    def setUp(self):
        self.user = User(first_name="John", last_name="Doe",
                         email="john@example.com", 
                         password = "password", is_admin=False)
        self.user2 = User(first_name="Jane", last_name="Doe",
                         email="jane@example.com", 
                         password = "password", is_admin=False)
        self.user3 = User(first_name="Jim", last_name="Doe",
                         email="jim@example.com", 
                         password = "password", is_admin=False)
        self.owner = User(first_name="Jane", last_name="McDonald",
                          email="jane@example.com", 
                          password="password")
        self.place = Place(title="Test Place", description="A place",
                           price=10.0, latitude=0.0, longitude=0.0,
                           owner=self.owner)
        self.valid_data = {
            'text': 'Great place!',
            'rating': 5,
            'place': self.place,
            'user': self.user
        }

    def test_review_creation_valid(self):
        review = Review(**self.valid_data)
        self.assertEqual(review.text, self.valid_data['text'])
        self.assertEqual(review.rating, self.valid_data['rating'])
        self.assertEqual(review.place, self.place)
        self.assertEqual(review.user, self.user)
        self.assertIn(review, self.place.reviews)

    def test_missing_required_fields(self):
        with self.assertRaises(ValueError):
            Review(text=None, # type: ignore
                   rating=5, place=self.place, user=self.user)
        with self.assertRaises(ValueError):
            Review(text='Nice', rating=None, # type: ignore
                   place=self.place, user=self.user)
        with self.assertRaises(ValueError):
            Review(text='Nice', rating=5, place=None, # type: ignore
                   user=self.user)
        with self.assertRaises(ValueError):
            Review(text='Nice', rating=5, place=self.place, 
                   user=None) # type: ignore

    def test_invalid_text_type_and_length(self):
        with self.assertRaises(ValueError):
            Review(text='', rating=5, place=self.place, user=self.user)
        with self.assertRaises(TypeError):
            Review(text=123, # type: ignore
                   rating=5, place=self.place, user=self.user)
        with self.assertRaises(ValueError):
            Review(text='A', rating=5, place=self.place, user=self.user)
        with self.assertRaises(ValueError):
            Review(text='A'*501, rating=5, place=self.place, user=self.user)

    def test_invalid_rating_type_and_range(self):
        with self.assertRaises(TypeError):
            Review(text='Nice', rating='bad', # type: ignore
                   place=self.place, user=self.user)
        with self.assertRaises(ValueError):
            Review(text='Nice', rating=0, place=self.place,
                   user=self.user)
        with self.assertRaises(ValueError):
            Review(text='Nice', rating=6, place=self.place, user=self.user)

    def test_invalid_place_and_user_type(self):
        with self.assertRaises(TypeError):
            Review(text='Nice', rating=5,
                   place='not_a_place', # type: ignore
                   user=self.user)
        with self.assertRaises(TypeError):
            Review(text='Nice', rating=5, place=self.place, 
                   user='not_a_user') # type: ignore

    def test_unauthorized_place_user_pair(self):
        Review(**self.valid_data)
        with self.assertRaises(CustomError) as e:
            Review(text='Perfect place, my place', rating=5,
                   place=self.place, user=self.owner)
        self.assertIn('User cannot review their own place',
                      str(e.exception))
        self.assertEqual(400, e.exception.status_code)
        
        with self.assertRaises(CustomError) as e:
            Review(text='Someone else\'s place', rating=3,
                   place=self.place, user=self.user)
        self.assertIn('This user has already reviewed this place',
                      str(e.exception))
        self.assertEqual(400, e.exception.status_code)

    def test_review_added_to_place(self):
        review = Review(**self.valid_data)
        self.assertIn(review, self.place.reviews)
        self.assertEqual(len(self.place.reviews), 1)
        review2 = Review(text='Another review', rating=4,
                        place=self.place, user=self.user2)
        self.assertIn(review2, self.place.reviews)
        self.assertEqual(len(self.place.reviews), 2)
        review3 = Review(text='And another review', rating=3,
                        place=self.place, user=self.user3)
        self.assertIn(review3, self.place.reviews)
        self.assertEqual(len(self.place.reviews), 3)
        


if __name__ == "__main__":
    unittest.main()
