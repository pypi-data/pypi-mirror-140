import logging

from . import errors, methods, models
from .client import Client
from .errors import Error
from .models import (
    Comparator,
    Email,
    EmailAddress,
    EmailBodyPart,
    EmailBodyValue,
    EmailHeader,
    EmailQueryFilter,
    EmailQueryFilterCondition,
    EmailQueryFilterOperator,
    Identity,
    ListOrRef,
    Mailbox,
    MailboxQueryFilter,
    MailboxQueryFilterCondition,
    MailboxQueryFilterOperator,
    Operator,
    StrOrRef,
    Thread,
    ThreadEmail,
)
from .ref import ResultReference

__all__ = [
    "Client",
    "Comparator",
    "Email",
    "EmailAddress",
    "EmailBodyPart",
    "EmailBodyValue",
    "EmailHeader",
    "EmailQueryFilter",
    "EmailQueryFilterCondition",
    "EmailQueryFilterOperator",
    "Error",
    "Identity",
    "ListOrRef",
    "Mailbox",
    "MailboxQueryFilter",
    "MailboxQueryFilterCondition",
    "MailboxQueryFilterOperator",
    "Operator",
    "ResultReference",
    "StrOrRef",
    "Thread",
    "ThreadEmail",
    "errors",
    "methods",
    "models",
]

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(logging.NullHandler())
