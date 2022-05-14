from pydantic import BaseModel
from typing import List

####### Strategy Models #######

class BaseStrategyModel(BaseModel):
    # Add subscripting capabilities.
    def __getitem__(self, item):
        return getattr(self, item)
    
    def __setitem__(self, attr, item):
        self.__dict__[attr] = item
