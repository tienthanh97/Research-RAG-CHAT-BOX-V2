from dataclasses import dataclass

@dataclass
class RetrievedDocument:
    id:str
    score:float
    text:str
    metadata:dict[str,any]
