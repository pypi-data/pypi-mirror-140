__author__ = "Hugo Inzirillo"

from dataclasses import dataclass
from enum import Enum
from typing import List, Union


class Scope(Enum):
    READ = "READ"
    WRITE = "WRITE"


@dataclass
class ClientCredentials:
    client_id: str
    client_secret: str
    scope: Union[List[Scope], List[str]]

    def __post_init__(self):
        self.scope = [item.value for item in self.scope if isinstance(item, Scope)]
