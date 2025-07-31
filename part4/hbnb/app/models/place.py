from app.models.baseEntity import (BaseEntity, type_validation,
                                   strlen_validation)
from app import db
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.api.v1.apiRessources import CustomError
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, Optional, TYPE_CHECKING
from .user import User
from .amenity import place_amenity
if TYPE_CHECKING:
    from .review import Review
    from .amenity import Amenity


class Place(BaseEntity):
    """ Represents a 'Place' entity in the database"""
    __tablename__ = 'places'
    _title: Mapped[str] = mapped_column("title", String(128),
                                        nullable=False)
    _description: Mapped[Optional[str]] = mapped_column("description", Text,
                                                        nullable=True)
    _price: Mapped[float] = mapped_column("price", Float,
                                          nullable=False)
    _latitude: Mapped[float] = mapped_column("latitude", Float,
                                             nullable=False)
    _longitude: Mapped[float] = mapped_column("longitude", Float,
                                              nullable=False)
    owner_id: Mapped[str] = mapped_column("owner_id",
                                          ForeignKey('users.id'))
    _owner: Mapped["User"] = relationship("User", back_populates="places",
                                          lazy=True)
    _reviews: Mapped[List["Review"]] = relationship("Review",
                                                    back_populates="_place",
                                                    lazy=True,
                                                    cascade="all,"
                                                    "delete-orphan")
    _amenities: Mapped[List["Amenity"]] = relationship("Amenity",
                                                       secondary=place_amenity,
                                                       back_populates="places")

    def __init__(self, title: str, description=None, *,
                 price: float, latitude: float,
                 longitude: float, owner: User):
        """ Initializes a new Place instance"""
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner
        self._reviews = []  # List to store related reviews
        self._amenities = []  # List to store related amenities

    @hybrid_property
    def title(self):  # type: ignore
        return self._title

    @title.setter
    def title(self, value):
        self._title = self.validate_title(value)

    def validate_title(self, title):
        """Verify if the title is a string < 100 characters."""
        if title is None:
            raise ValueError(
                'Invalid title: expected a title but received None')
        type_validation(title, "Title", str)
        title = title.strip()
        strlen_validation(title, "Title", 4, 100)
        return title

    @hybrid_property
    def description(self):  # type: ignore
        return self._description

    @description.setter  # type: ignore
    def description(self, value):
        self._description = self.validate_description(value)  # type

    def validate_description(self, description):
        """Verify if the description is a string."""
        if description is None:
            return None  # ""
        type_validation(description, "Description", str)
        description = description.strip()
        strlen_validation(description, "Description", 3, 50)
        return description

    @hybrid_property
    def price(self):  # type: ignore
        return self._price

    @price.setter
    def price(self, value):
        self._price = self.validate_price(value)

    def validate_price(self, price: float):
        """Verify is the price is an integer."""
        if price is None:
            raise ValueError(
                "Invalid price: expected float or int but received None")
        type_validation(price, "Price", (float, int))
        if price <= 0:
            raise ValueError("Price must be a positive number (larger "
                             "than 0)")
        return float(price)

    @hybrid_property
    def latitude(self):  # type: ignore
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        self._latitude = self.validate_latitude(value)

    def validate_latitude(self, latitude):
        """Verify is the latitude is a float between -90.0 & 90.0."""
        if latitude is None:
            raise ValueError(
                "Invalid latitude: expected float or int but received None")
        type_validation(latitude, "Latitude", (float, int))
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0.")
        return float(latitude)

    @hybrid_property
    def longitude(self):  # type: ignore
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        self._longitude = self.validate_longitude(value)

    def validate_longitude(self, longitude):
        """Verify is the longitude is a float between -180.0 &
        180.0."""
        if longitude is None:
            raise ValueError(
                "Invalid longitude: expected float or int but received None")
        type_validation(longitude, "Longitude", (float, int))
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude must be between -180.0 and"
                             " 180.0")
        return float(longitude)

    @hybrid_property
    def owner(self):  # type: ignore
        return self._owner

    @owner.setter  # type: ignore
    def owner(self, value):  # type: ignore
        if value is None:
            raise ValueError("Invalid owner: expected user but received None")
        type_validation(value, "owner", User)
        self._owner = value
        self.owner_id = value.id

    # Allow querying for the attribute
    @owner.expression
    def owner(cls):
        return cls._owner

    def add_review(self, review):
        """Add a review to the place."""
        if review is None:
            raise ValueError('Expected review but received None')
        from app.models.review import Review
        type_validation(review, "Review", Review)
        self.reviews.append(review)

    @hybrid_property
    def reviews(self):  # type: ignore
        return self._reviews

    @reviews.setter  # type: ignore
    def reviews(self, value):
        if value is None:
            self._reviews = []
            return None
        type_validation(value, "reviews", list)
        for review in value:
            self.add_review(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(self.amenity_validation(amenity))

    def amenity_validation(self, amenity):
        if amenity is None:
            raise ValueError(
                'Invalid amenity: expected amenity but received None')
        from app.models.amenity import Amenity
        type_validation(amenity, "Amenity", Amenity)
        if any(place_amenity == amenity
               for place_amenity in self.amenities):
            raise CustomError(
                f'Amenity "{amenity.name}" already listed for this place', 400)
        return amenity

    @hybrid_property
    def amenities(self):  # type: ignore
        return self._amenities

    @amenities.setter  # type: ignore
    def amenities(self, value):
        if value is None:
            self._amenities = []
            return None
        type_validation(value, "amenities", list)
        self._amenities = []
        for amenity in value:
            self.add_amenity(amenity)
