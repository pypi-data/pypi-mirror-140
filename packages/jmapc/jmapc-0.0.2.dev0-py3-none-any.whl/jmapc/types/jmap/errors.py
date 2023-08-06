from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from ..util import JsonDataClass

__all__ = ["JMAPError", "JMAPServerFail"]


@dataclass
class JMAPError(JsonDataClass):
    type: str

    @staticmethod
    def _errors_map() -> Dict[str, Type[JMAPError]]:
        return {
            "invalidArguments": JMAPInvalidArguments,
            "serverFail": JMAPServerFail,
        }

    @classmethod
    def from_dict(cls, *args: Any, **kwargs: Any) -> JMAPError:
        res = super().from_dict(*args, **kwargs)
        if cls == JMAPError:
            errors_map = cls._errors_map()
            if res.type in errors_map:
                return errors_map[res.type].from_dict(*args, **kwargs)
            return res
        return res


@dataclass
class JMAPInvalidArguments(JMAPError):
    arguments: List[str]


@dataclass
class JMAPServerFail(JMAPError):
    description: Optional[str]
