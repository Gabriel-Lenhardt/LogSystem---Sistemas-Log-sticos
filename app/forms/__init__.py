"""WTForms forms."""

from .auth import LoginForm, RegisterForm
from .client import ClientForm
from .dumpster import DumpsterForm
from .rental import RentalCloseForm, RentalOpenForm
from .report import RevenueReportForm

__all__ = [
    "ClientForm",
    "DumpsterForm",
    "LoginForm",
    "RegisterForm",
    "RentalCloseForm",
    "RentalOpenForm",
    "RevenueReportForm",
]
