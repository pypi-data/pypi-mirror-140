from .enums import uSwidGlobalMap as uSwidGlobalMap
from .errors import NotSupportedError as NotSupportedError
from enum import IntEnum
from typing import Any, List, Optional

class uSwidEntityRole(IntEnum):
    TAG_CREATOR: int
    SOFTWARE_CREATOR: int
    AGGREGATOR: int
    DISTRIBUTOR: int
    LICENSOR: int
    MAINTAINER: int

class uSwidEntity:
    name: Any
    regid: Any
    roles: Any
    def __init__(self, name: Optional[str] = ..., regid: Optional[str] = ..., roles: Optional[List[uSwidEntityRole]] = ...) -> None: ...
