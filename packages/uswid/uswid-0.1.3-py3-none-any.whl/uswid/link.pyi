from .enums import uSwidGlobalMap as uSwidGlobalMap
from .errors import NotSupportedError as NotSupportedError
from enum import IntEnum
from typing import Any, Optional

class uSwidLinkRel(IntEnum):
    ANCESTOR: int
    COMPONENT: int
    FEATURE: int
    INSTALLATIONMEDIA: int
    PACKAGEINSTALLER: int
    PARENT: int
    PATCHES: int
    REQUIRES: int
    SEE_ALSO: int
    SUPERSEDES: int
    SUPPLEMENTAL: int

class uSwidLink:
    href: Any
    rel: Any
    def __init__(self, href: Optional[str] = ..., rel: Optional[str] = ...) -> None: ...
