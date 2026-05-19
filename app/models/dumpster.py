"""Dumpster model."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from ..extensions import db


class DumpsterStatus(StrEnum):
    AVAILABLE = "Disponivel"
    RENTED = "Alugado"
    MAINTENANCE = "Manutenção"


class Dumpster(db.Model):
    __tablename__ = "dumpsters"

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(20), unique=True, nullable=False, index=True)
    size = db.Column(db.Float, nullable=False)
    daily_rate = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default=DumpsterStatus.AVAILABLE.value, index=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    rentals = db.relationship(
        "Rental",
        back_populates="dumpster",
        order_by="Rental.start_date.desc()",
    )

    @property
    def is_available(self) -> bool:
        return self.status == DumpsterStatus.AVAILABLE.value

    @property
    def status_label(self) -> str:
        return self.status.capitalize()

    def __repr__(self) -> str:
        return f"<Dumpster {self.identifier}>"
