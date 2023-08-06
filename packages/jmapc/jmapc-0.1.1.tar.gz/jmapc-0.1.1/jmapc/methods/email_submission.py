from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .. import constants
from ..models import EmailSubmission
from .base import Set, SetResponse


@dataclass
class EmailSubmissionSet(Set):
    def __post_init__(self) -> None:
        self.name = "EmailSubmission/set"
        self.using = set([constants.JMAP_URN_SUBMISSION])

    create: Optional[Dict[str, EmailSubmission]] = None
    on_success_update_email: Optional[Dict[str, Any]] = None
    on_success_destroy_email: Optional[List[str]] = None


@dataclass
class EmailSubmissionSetResponse(SetResponse):
    created: Optional[Dict[str, EmailSubmission]]
    updated: Optional[Dict[str, EmailSubmission]]
