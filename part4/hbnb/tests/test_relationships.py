import unittest
import uuid
from app import create_app, db
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review
from app.models.baseEntity import BaseEntity

place_amenity_association = db.Table(
    'place_amenity_association',
    BaseEntity.metadata,
    db.Column('place_id', db.String(36), db.ForeignKey('places.id'), primary_key=True),
    db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id'), primary_key=True)
)

class RelationshipsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Configure Flask app for testing"""
        cls.app = create_app(config_class="config.TestingConfig")
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all() # Crée toutes les tables, y compris les tables d'association

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are run"""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """Set up for each test"""
        self.session = db.session
        self.session.begin_nested() # Permet le rollback pour isoler les tests

        # Créer un utilisateur et une place de base pour les tests qui en ont besoin
        self.user_email = f"test_user_{uuid.uuid4()}@example.com"
        self.test_user = User(
            first_name="Test",
            last_name="User",
            email=self.user_email,
            password="password123"
        )
        self.session.add(self.test_user)
        self.session.commit()
        self.session.refresh(self.test_user)

        self.place_title = f"Test Place {uuid.uuid4()}"
        self.test_place = Place(
            title=self.place_title,
            description="A generic test place.",
            price=100.0,
            latitude=40.0,
            longitude=-70.0,
            owner=self.test_user
        )
        self.session.add(self.test_place)
        self.session.commit()
        self.session.refresh(self.test_place)

    def tearDown(self):
        """Clean up after each test"""
        self.session.rollback() # Annule les changements faits par le test actuel
        self.session.close()


    ## Tests de la relation User-Place

    def test_place_owner_relationship(self):
        """
        Test that a Place is correctly associated with its User owner
        and that the relationship works bidirectionally.
        """
        # Vérifier la relation depuis la place vers l'utilisateur
        retrieved_place = self.session.query(Place).get(self.test_place.id)
        self.assertIsNotNone(retrieved_place)
        self.assertEqual(retrieved_place.owner.id, self.test_user.id)
        self.assertEqual(retrieved_place.owner.email, self.test_user.email)

        # Vérifier la relation depuis l'utilisateur vers la place
        retrieved_user = self.session.query(User).get(self.test_user.id)
        self.assertIsNotNone(retrieved_user)
        self.assertIn(self.test_place, retrieved_user.places)
        self.assertEqual(len(retrieved_user.places), 1)
        self.assertEqual(retrieved_user.places[0].title, self.test_place.title)

    def test_delete_user_cascades_to_places(self):
        """
        Test that deleting a User also deletes their associated Places
        due to cascade="all, delete-orphan".
        """
        # Créer un utilisateur et une place spécifiquement pour ce test de suppression
        user_to_delete_email = f"delete_user_{uuid.uuid4()}@example.com"
        user_to_delete = User(
            first_name="Temp", last_name="Delete", email=user_to_delete_email, password="password"
        )
        self.session.add(user_to_delete)
        self.session.commit()
        self.session.refresh(user_to_delete)

        place_to_delete_title = f"Temp Place {uuid.uuid4()}"
        place_to_delete = Place(
            title=place_to_delete_title, description="Temp", price=1.0,
            latitude=1.0, longitude=1.0, owner=user_to_delete
        )
        self.session.add(place_to_delete)
        self.session.commit()

        # Supprimer l'utilisateur
        self.session.delete(user_to_delete)
        self.session.commit()

        # Vérifier que la place est supprimée en cascade
        self.assertIsNone(self.session.query(Place).filter_by(title=place_to_delete_title).first())
        self.assertIsNone(self.session.query(User).filter_by(email=user_to_delete_email).first())


    ## Tests de la relation User-Reviews

    def test_user_reviews_relationship(self):
        """
        Test that a User can write Reviews and the relationship is correct.
        """
        review_text = "Great place, loved it!"
        new_review = Review(
            text=review_text,
            rating=5,
            user=self.test_user,  # L'utilisateur qui écrit la critique
            place=self.test_place  # La place critiquée
        )
        self.session.add(new_review)
        self.session.commit()
        self.session.refresh(new_review)

        # Vérifier depuis l'utilisateur
        retrieved_user = self.session.query(User).get(self.test_user.id)
        self.assertIsNotNone(retrieved_user)
        self.assertIn(new_review, retrieved_user.reviews)
        self.assertEqual(len(retrieved_user.reviews), 1)
        self.assertEqual(retrieved_user.reviews[0].text, review_text)


    ## Tests de la relation Place-Reviews

    def test_place_reviews_relationship(self):
        """
        Test that a Place can receive Reviews and the relationship is correct.
        """
        review_text = "Wonderful experience!"
        new_review = Review(
            text=review_text,
            rating=4,
            user=self.test_user,
            place=self.test_place
        )
        self.session.add(new_review)
        self.session.commit()
        self.session.refresh(new_review)

        # Vérifier depuis la place
        retrieved_place = self.session.query(Place).get(self.test_place.id)
        self.assertIsNotNone(retrieved_place)
        self.assertIn(new_review, retrieved_place.reviews)
        self.assertEqual(len(retrieved_place.reviews), 1)
        self.assertEqual(retrieved_place.reviews[0].text, review_text)

    def test_delete_place_cascades_to_reviews(self):
        """
        Test that deleting a Place also deletes its associated Reviews.
        """
        # Créer une place spécifiquement pour ce test
        place_to_delete_title = f"Place For Review Delete {uuid.uuid4()}"
        place_to_delete = Place(
            title=place_to_delete_title, description="Temp", price=1.0,
            latitude=1.0, longitude=1.0, owner=self.test_user
        )
        self.session.add(place_to_delete)
        self.session.commit()
        self.session.refresh(place_to_delete)

        # Créer une critique pour cette place
        review_text = "This review should be deleted."
        review_to_delete = Review(
            text=review_text, rating=4, user=self.test_user, place=place_to_delete
        )
        self.session.add(review_to_delete)
        self.session.commit()

        # Vérifier que la critique existe initialement
        self.assertIsNotNone(self.session.query(Review).filter_by(text=review_text).first())

        # Supprimer la place
        self.session.delete(place_to_delete)
        self.session.commit()

        # Vérifier que la critique a été supprimée en cascade
        self.assertIsNone(self.session.query(Review).filter_by(text=review_text).first())


    ## Tests de la relation Place-Amenities (Many-to-Many)

    def test_place_amenities_relationship(self):
        """
        Test that a Place can have multiple Amenities and vice-versa.
        """
        # 1. Créer des commodités
        amenity1 = Amenity(name=f"WiFi {uuid.uuid4()}")
        amenity2 = Amenity(name=f"Pool {uuid.uuid4()}")
        self.session.add_all([amenity1, amenity2])
        self.session.commit()
        self.session.refresh(amenity1)
        self.session.refresh(amenity2)

        # 2. Associer les commodités à la place
        # Ceci suppose que votre modèle Place a une méthode add_amenity
        # qui ajoute l'objet Amenity à la collection 'amenities' de la relation SQLAlchemy.
        self.test_place.add_amenity(amenity1)
        self.test_place.add_amenity(amenity2)
        self.session.commit() # Commit pour persister les associations Many-to-Many

        # 3. Vérifier depuis la place vers les commodités
        retrieved_place = self.session.query(Place).get(self.test_place.id)
        self.assertIsNotNone(retrieved_place)
        self.assertEqual(len(retrieved_place.amenities), 2)
        self.assertIn(amenity1, retrieved_place.amenities)
        self.assertIn(amenity2, retrieved_place.amenities)

        # 4. Vérifier depuis les commodités vers la place
        retrieved_amenity1 = self.session.query(Amenity).get(amenity1.id)
        retrieved_amenity2 = self.session.query(Amenity).get(amenity2.id)
        self.assertIsNotNone(retrieved_amenity1)
        self.assertIsNotNone(retrieved_amenity2)
        self.assertIn(self.test_place, retrieved_amenity1.places)
        self.assertIn(self.test_place, retrieved_amenity2.places)
        self.assertEqual(len(retrieved_amenity1.places), 1)
        self.assertEqual(len(retrieved_amenity2.places), 1)


# Pour exécuter les tests depuis la ligne de commande
if __name__ == '__main__':
    unittest.main()
