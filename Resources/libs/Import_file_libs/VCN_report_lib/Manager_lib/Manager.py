from abc import ABCMeta, abstractmethod

class Manager() :
    __metaclass__ = ABCMeta

    @abstractmethod
    def expected_trans(self):
        raise NotImplementedError
    
    @abstractmethod   
    def generate(self):
        raise NotImplementedError
