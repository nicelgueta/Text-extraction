from pydantic import BaseModel
from typing import (
    Optional,
    List,
    Dict 
)

class BxInstruction(BaseModel):
    useIndex: bool 
    tagName: str
    index: Optional[int]
    attrs: Optional[dict]
    useName: Optional[bool]

class BxPath(BaseModel):
    instructions: List[BxInstruction]
    dataType: str
    regex: Optional[str]

class BxCollection(BaseModel):
    
    # Rules Format: {'field_name':[BxPath,BxPath,BxPath...]}
    
    rules: Dict[str, List[BxPath]]
