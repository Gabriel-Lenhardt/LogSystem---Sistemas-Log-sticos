"""Main / dashboard routes."""

from __future__ import annotations

from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required

from ..extensions import db
from ..models.client import Client
from ..models.dumpster import Dumpster, DumpsterStatus
from ..models.rental import Rental, RentalStatus

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    today = date.today()

    stats = {
        "total_clients": db.session.query(Client).count(),
        "total_dumpsters": db.session.query(Dumpster).count(),
        "available_dumpsters": db.session.query(Dumpster)
        .filter_by(status=DumpsterStatus.AVAILABLE.value)
        .count(),
        "rented_dumpsters": db.session.query(Dumpster)
        .filter_by(status=DumpsterStatus.RENTED.value)
        .count(),
        "active_rentals": db.session.query(Rental)
        .filter_by(status=RentalStatus.ACTIVE.value)
        .count(),
        "overdue_rentals": db.session.query(Rental)
        .filter(
            Rental.status == RentalStatus.ACTIVE.value,
            Rental.expected_end_date < today,
        )
        .count(),
    }

    recent_rentals = (
        db.session.query(Rental).order_by(Rental.created_at.desc()).limit(5).all()
    )

    return render_template(
        "dashboard.html", stats=stats, recent_rentals=recent_rentals
    )
