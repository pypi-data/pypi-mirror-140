from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ergo.util import uniqueid


@dataclass
class Scope:
    id: str = field(default_factory=uniqueid)
    data: dict = field(default_factory=dict)
    reply_to: Optional[str] = None
    parent: Optional[Scope] = None
