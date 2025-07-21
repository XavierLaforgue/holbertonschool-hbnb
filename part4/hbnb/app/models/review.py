from app.models.baseEntity import (BaseEntity, type_validation,
                                   strlen_validation)
from app.models.place import Place
from app.models.user import User
from app import bcrypt, db
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.api.v1.apiRessources import CustomError
from sqlalchemy.ext.hybrid import hybrid_property


class Review(BaseEntity):
    """ Represents a  'Review' entity in the database"""
    __tablename__ = 'reviews'
    _text: Mapped[str] = mapped_column("text", Text, nullable=False)
    _rating: Mapped[int] = mapped_column("rating", Integer, nullable=False)
    place_id: Mapped[str] = mapped_column("place_id", String(36),
                                          ForeignKey("places.id"),
                                          nullable=False)
    _place: Mapped["Place"] = relationship("Place", back_populates="_reviews",
                                           lazy=True)
    user_id: Mapped[str] = mapped_column("user_id", String(36),
                                         ForeignKey("users.id"),
                                         nullable=False)
    _user: Mapped[User] = relationship("User", back_populates="reviews",
                                       lazy=True)

    def __init__(self, text: str, rating: int, place: Place,
                 user: User):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place
        self.user = user
        if any(((review.id != self.id) and (review.user == user))
               for review in self.place.reviews):
            raise CustomError('This user has already reviewed this place',
                              400)
        place.add_review(self)

    @hybrid_property
    def text(self):  # type: ignore
        return self._text

    @text.setter  # type: ignore
    def text(self, value):
        if value is None:
            raise ValueError("text is required: provide content for"
                             " the review")
        type_validation(value, "Text", str)
        value = value.strip()
        strlen_validation(value, "Text", 2, 500)
        self._text = value

    @hybrid_property
    def rating(self):  # type: ignore
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = self.rating_validation(value)

    def rating_validation(self, rating):
        """ Validates the review rating"""
        if rating is None:
            raise ValueError(
                "rating is required: provide an integer between 1 and 5 to"
                "rate the place")
        type_validation(rating, "Rating", int)
        if not (1 <= rating <= 5):
            raise ValueError(
                "Rating must be an integer between 1 and 5, both inclusive")
        return rating

    @hybrid_property
    def user(self):  # type: ignore
        return self._user

    @user.setter  # type: ignore
    def user(self, value):  # type: ignore
        self._user = self.set_user(value)
        self.user_id = value.id

    @user.expression
    def user(cls):
        return cls._user

    def set_user(self, user):
        if user is None:
            raise ValueError(
                "user is required: provide user who writes the review")
        type_validation(user, "User", User)
        if self.place is not None:
            if user == self.place.owner:
                raise CustomError("User cannot review their own place", 400)
        else:
            raise CustomError(
                "Place is required, review should be written for a place", 400)
        return user

    @hybrid_property
    def place(self):  # type: ignore
        return self._place

    @place.setter
    def place(self, value):  # type: ignore
        self._place = self.set_place(value)
        self.place_id = value.id

    @place.expression
    def place(cls):
        return cls._place

    def set_place(self, place):
        if place is None:
            raise ValueError(
                "place is required: provide place being reviewed")
        type_validation(place, "Place", Place)
        return place
