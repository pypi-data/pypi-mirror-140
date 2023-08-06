from typing import List

from .device import Photo
from .classification import Classification


class CCBSCAlgorithm:
    """ Informal interface an algorithm should implement to be called to make classifications. """

    def classify(self, photo: Photo) -> List[Classification]:
        """ Takes the given photo and return a list of classifications found in the photo. Override 
            this method in you algorithm. """
        pass

    def identifier(self):
        """ Returns the identifier of the actual algorithm. """
        pass
