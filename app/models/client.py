"""Client model."""

from __future__ import annotations

from datetime import datetime

from ..extensions import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    document = db.Column(db.String(20), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    rentals = db.relationship(
        "Rental",
        back_populates="client",
        cascade="all, delete-orphan",
        order_by="Rental.start_date.desc()",
    )

    @property
    def active_rentals_count(self) -> int:
        from .rental import RentalStatus

        return sum(1 for r in self.rentals if r.status == RentalStatus.ACTIVE)

    def __repr__(self) -> str:
        return f"<Client {self.name}>"
