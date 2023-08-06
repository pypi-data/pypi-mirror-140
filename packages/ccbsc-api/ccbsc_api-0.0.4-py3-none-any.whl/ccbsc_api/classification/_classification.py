from typing import Dict
from . import Pollen
from ..device import Photo


class Coordinates:
    """ Describes coordinates of a rectangle with (x, y) at upper left corner and (width, height) as rectangle dimensions. """

    def __init__(self, x: int, width: int, y: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self) -> str:
        return "({x}, {y}, {width}, {height})".format(x=self.x, y=self.y, width=self.width, height=self.height)


class Classification:
    """ Describes a classification which is basically the detected pollen type and coordinates where the pollen was detected 
        in returned photo. Optionally, a dict of features can be returned which contains detection details of the pollen. """

    def __init__(self, coordinates: Coordinates, classification: Pollen, photo: Photo, features: Dict = None):
        self.coordinates = coordinates
        self.classification = classification
        self.photo = photo
        self.features = features

    def __str__(self) -> str:
        return "{classification} @ {coordinates}".format(classification=self.classification, coordinates=self.coordinates)
