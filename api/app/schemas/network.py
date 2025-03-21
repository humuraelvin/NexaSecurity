from pydantic import BaseModel
from typing import List, Optional, Literal

class NetworkNode(BaseModel):
    id: str
    name: str
    type: str
    status: str
    ip: Optional[str] = None

class NetworkConnection(BaseModel):
    source: str
    target: str
    type: Literal["direct", "indirect"]

class NetworkMap(BaseModel):
    nodes: List[NetworkNode]
    connections: List[NetworkConnection]

class NetworkDevice(BaseModel):
    id: str
    name: str
    ip: str
    type: str
    status: str
    lastSeen: str
    vulnerabilities: int 