import unittest
from app import create_app, db
from app.models.user import User
from app.models.place import Place
import uuid # Pour générer des UUIDs valides pour les tests

class UserPlaceRelationshipTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Configure Flask app for testing"""
        # Crée une application Flask en mode test avec une base de données en mémoire
        cls.app = create_app(config_class="config.TestingConfig")
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all() # Crée les tables dans la base de données en mémoire

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are run"""
        db.session.remove()
        db.drop_all() # Supprime toutes les tables
        cls.app_context.pop()

    def setUp(self):
        """Set up for each test"""
        # Commence une nouvelle transaction pour chaque test et la rend rollbackable
        self.session = db.session
        self.session.begin_nested() # Permet le rollback sans affecter les autres tests

    def tearDown(self):
        """Clean up after each test"""
        self.session.rollback() # Annule les changements faits par le test actuel
        self.session.close() # Ferme la session

    def test_place_owner_relationship(self):
        """
        Test that a Place can be correctly associated with a User (owner)
        and that the relationship works bidirectionally.
        """
        # 1. Créer un utilisateur
        user_email = f"test_user_{uuid.uuid4()}@example.com"
        new_user = User(
            first_name="Test",
            last_name="User",
            email=user_email,
            password="password123"
        )
        self.session.add(new_user)
        self.session.commit() # Commit l'utilisateur pour qu'il ait un ID persistant
        
        # Rafraîchir l'utilisateur pour être sûr qu'il est attaché à la session après commit
        # (souvent nécessaire si l'ID est généré par la DB)
        self.session.refresh(new_user)

        # 2. Créer une place et l'associer à l'utilisateur
        place_title = "My Test Place"
        new_place = Place(
            title=place_title,
            description="A lovely test place.",
            price=100.0,
            latitude=40.7128,
            longitude=-74.0060,
            owner=new_user # Passer l'objet User directement ici
        )
        self.session.add(new_place)
        self.session.commit() # Commit la place

        # 3. Vérifier la relation depuis la place vers l'utilisateur
        retrieved_place = self.session.query(Place).filter_by(title=place_title).first()
        self.assertIsNotNone(retrieved_place)
        self.assertEqual(retrieved_place.owner.id, new_user.id)
        self.assertEqual(retrieved_place.owner.email, user_email)

        # 4. Vérifier la relation depuis l'utilisateur vers la place
        retrieved_user = self.session.query(User).filter_by(email=user_email).first()
        self.assertIsNotNone(retrieved_user)
        self.assertIn(new_place, retrieved_user.places)
        self.assertEqual(len(retrieved_user.places), 1)
        self.assertEqual(retrieved_user.places[0].title, place_title)

    def test_delete_user_cascades_to_places(self):
        """
        Test that deleting a User also deletes their associated Places
        due to cascade="all, delete-orphan".
        """
        # 1. Créer un utilisateur et une place
        user_email = f"user_to_delete_{uuid.uuid4()}@example.com"
        new_user = User(
            first_name="Delete",
            last_name="Me",
            email=user_email,
            password="password123"
        )
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        place_title = "Place to be deleted"
        new_place = Place(
            title=place_title,
            description="Should be gone soon.",
            price=50.0,
            latitude=10.0,
            longitude=10.0,
            owner=new_user
        )
        self.session.add(new_place)
        self.session.commit()

        # Vérifier que la place et l'utilisateur existent
        initial_place_count = self.session.query(Place).count()
        initial_user_count = self.session.query(User).count()
        self.assertGreater(initial_place_count, 0)
        self.assertGreater(initial_user_count, 0)

        # 2. Supprimer l'utilisateur
        self.session.delete(new_user)
        self.session.commit()

        # 3. Vérifier que l'utilisateur n'existe plus
        self.assertIsNone(self.session.query(User).filter_by(email=user_email).first())

        # 4. Vérifier que la place associée a également été supprimée (cascade)
        self.assertIsNone(self.session.query(Place).filter_by(title=place_title).first())
        
        # Ou en vérifiant le nouveau compte total (si vous n'êtes pas en nested transaction)
        # self.assertEqual(self.session.query(Place).count(), initial_place_count - 1)

# Pour exécuter les tests depuis la ligne de commande
if __name__ == '__main__':
    unittest.main()
