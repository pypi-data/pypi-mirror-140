

import abc


class PredictionFormat(abc.ABC):

    def __init__(self):
        pass
        
    @abc.abstractmethod
    def check_validity(self,) -> bool:
        pass
    
    @abc.abstractmethod
    def to_payload(self,) -> dict:
        pass

    