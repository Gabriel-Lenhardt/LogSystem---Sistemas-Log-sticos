"""Report routes."""

from __future__ import annotations

from decimal import Decimal

from flask import Blueprint, render_template, request
from flask_login import login_required

from ..extensions import db
from ..forms.report import RevenueReportForm
from ..models.rental import Rental, RentalStatus

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/revenue", methods=["GET"])
@login_required
def revenue():
    form = RevenueReportForm(request.args, meta={"csrf": False})

    rentals: list[Rental] = []
    total_revenue = Decimal("0.00")
    total_days = 0

    submitted = bool(request.args) and form.validate()
    if submitted:
        rentals = (
            db.session.query(Rental)
            .filter(
                Rental.status == RentalStatus.COMPLETED.value,
                Rental.return_date >= form.start_date.data,
                Rental.return_date <= form.end_date.data,
            )
            .order_by(Rental.return_date.desc())
            .all()
        )
        total_revenue = sum(
            (r.total_amount for r in rentals if r.total_amount is not None),
            start=Decimal("0.00"),
        )
        total_days = sum(r.days_elapsed for r in rentals)

    return render_template(
        "reports/revenue.html",
        form=form,
        rentals=rentals,
        total_revenue=total_revenue,
        total_days=total_days,
        submitted=submitted,
    )
