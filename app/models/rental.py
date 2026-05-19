"""Rental model with business helpers."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from ..extensions import db
from .dumpster import DumpsterStatus


class RentalStatus(StrEnum):
    ACTIVE = "Ativa"
    COMPLETED = "Fechado"


class MaterialType(StrEnum):
    CONSTRUCTION_DEBRIS = "construction_debris"
    SOIL = "soil"
    WOOD = "wood"
    VEGETATION = "vegetation"
    MIXED = "mixed"
    OTHER = "other"


MATERIAL_TYPE_LABELS: dict[str, str] = {
    MaterialType.CONSTRUCTION_DEBRIS.value: "Entulho",
    MaterialType.SOIL.value: "Terra",
    MaterialType.WOOD.value: "Madeira",
    MaterialType.VEGETATION.value: "Mato/Vegetação",
    MaterialType.MIXED.value: "Misturado",
    MaterialType.OTHER.value: "Outros",
}


class Rental(db.Model):
    __tablename__ = "rentals"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    dumpster_id = db.Column(db.Integer, db.ForeignKey("dumpsters.id"), nullable=False)

    delivery_address = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    expected_end_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)

    daily_rate = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=True)

    material_type = db.Column(db.String(30), nullable=True)

    status = db.Column(
        db.String(20), nullable=False, default=RentalStatus.ACTIVE.value, index=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    client = db.relationship("Client", back_populates="rentals")
    dumpster = db.relationship("Dumpster", back_populates="rentals")

    @property
    def is_active(self) -> bool:
        return self.status == RentalStatus.ACTIVE.value

    @property
    def is_overdue(self) -> bool:
        return self.is_active and self.expected_end_date < date.today()

    @property
    def days_elapsed(self) -> int:
        reference = self.return_date or date.today()
        delta = (reference - self.start_date).days
        return max(1, delta)

    @property
    def material_type_label(self) -> str | None:
        if self.material_type is None:
            return None
        return MATERIAL_TYPE_LABELS.get(self.material_type, self.material_type)

    def open(self) -> None:
        """Mark the rental as active and lock the dumpster."""
        self.status = RentalStatus.ACTIVE.value
        self.dumpster.status = DumpsterStatus.RENTED.value

    def close(self, return_date: date | None = None, material_type: str | None = None) -> None:
        """Close the rental, compute total amount, record material, free the dumpster."""
        self.return_date = return_date or date.today()
        days = max(1, (self.return_date - self.start_date).days)
        self.total_amount = (Decimal(days) * Decimal(self.daily_rate)).quantize(Decimal("0.01"))
        self.material_type = material_type
        self.status = RentalStatus.COMPLETED.value
        self.dumpster.status = DumpsterStatus.AVAILABLE.value

    def __repr__(self) -> str:
        return f"<Rental #{self.id} client={self.client_id} dumpster={self.dumpster_id}>"
