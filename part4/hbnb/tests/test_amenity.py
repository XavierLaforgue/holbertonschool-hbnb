import unittest
from app.models.amenity import Amenity


class TestAmenity(unittest.TestCase):

    def test_amenity_creation_valid(self):
        amenity = Amenity("Wi-Fi")
        self.assertEqual(amenity.name, "Wi-Fi")
        self.assertIsInstance(amenity.id, str)
        self.assertIsInstance(amenity.name, str)

    def test_amenity_name_empty(self):
        with self.assertRaises(ValueError) as e:
            Amenity(None)
        self.assertIn("Invalid name", str(e.exception))

    def test_amenity_name_empty_string(self):
        with self.assertRaises(ValueError) as e:
            Amenity("")
        self.assertIn("Invalid name", str(e.exception))

    def test_amenity_name_long_string(self):
        with self.assertRaises(ValueError) as e:
            Amenity("A" * 51)
        self.assertIn("Invalid name", str(e.exception))

    def test_amenity_name_type(self):
        with self.assertRaises(TypeError) as e:
            Amenity(123)
        self.assertIn("Invalid name", str(e.exception))

    def test_amenity_too_many_args(self):
        with self.assertRaises(TypeError) as e:
            Amenity("Swimming pool", "Swimsuit") # type: ignore
        self.assertIn("Amenity.__init__()", str(e.exception))

    def test_amenity_name_strip(self):
        amenity = Amenity("  Pool  ")
        self.assertEqual(amenity.name, "Pool")


if __name__ == "__main__":
    unittest.main()
