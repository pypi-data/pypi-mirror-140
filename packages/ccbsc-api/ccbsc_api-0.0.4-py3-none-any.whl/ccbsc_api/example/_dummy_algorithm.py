from .. import CCBSCAlgorithm
from ..device import Photo
from ..classification import Classification, Coordinates, Pollen
from typing import List


class DummyAlgorithm(CCBSCAlgorithm):
    def classify(self, photo: Photo) -> List[Classification]:
        (width, height) = photo.image.size
        return [Classification(coordinates=Coordinates(0, 0, width, height), classification=Pollen.ALTERNARIA, photo=photo)]

    def identifier(self):
        return "DummyAlgorithm"
