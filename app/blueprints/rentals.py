"""Rental routes."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..extensions import db
from ..forms.rental import RentalCloseForm, RentalOpenForm
from ..models.client import Client
from ..models.dumpster import Dumpster, DumpsterStatus
from ..models.rental import Rental, RentalStatus

rentals_bp = Blueprint("rentals", __name__)


@rentals_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status", "active")
    query = db.session.query(Rental).order_by(Rental.start_date.desc())
    if status_filter in {s.value for s in RentalStatus}:
        query = query.filter(Rental.status == status_filter)
    rentals = query.all()
    return render_template(
        "rentals/index.html", rentals=rentals, status_filter=status_filter
    )


@rentals_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = RentalOpenForm()
    form.client_id.choices = [
        (c.id, f"{c.name} ({c.document})")
        for c in db.session.query(Client).order_by(Client.name).all()
    ]
    available_dumpsters = (
        db.session.query(Dumpster)
        .filter_by(status=DumpsterStatus.AVAILABLE.value)
        .order_by(Dumpster.identifier)
        .all()
    )
    form.dumpster_id.choices = [
        (d.id, f"{d.identifier} — {d.size} M³ — R$ {d.daily_rate}/dia")
        for d in available_dumpsters
    ]
    
    if not form.client_id.choices:
        flash("Cadastre um cliente antes de abrir uma locação.", "warning")
        return redirect(url_for("clients.create"))
    if not form.dumpster_id.choices:
        flash("Nenhuma caçamba disponível no momento.", "warning")
        return redirect(url_for("dumpsters.index"))

    if form.validate_on_submit():
        dumpster = db.session.get(Dumpster, form.dumpster_id.data)
        if dumpster is None or not dumpster.is_available:
            flash("A caçamba selecionada não está mais disponível.", "danger")
            return redirect(url_for("rentals.create"))

        client = db.session.get(Client, form.client_id.data)
        rental = Rental(
            client=client,
            dumpster=dumpster,
            delivery_address=form.delivery_address.data,
            start_date=form.start_date.data,
            expected_end_date=form.expected_end_date.data,
            daily_rate=dumpster.daily_rate,
        )
        rental.open()
        db.session.add(rental)
        db.session.commit()
        flash("Locação aberta", "success")
        return redirect(url_for("rentals.detail", rental_id=rental.id))

    return render_template("rentals/form.html", form=form, title="Nova locação")


@rentals_bp.route("/<int:rental_id>")
@login_required
def detail(rental_id: int):
    rental = db.session.get(Rental, rental_id) or abort(404)
    close_form = RentalCloseForm() if rental.is_active else None
    return render_template(
        "rentals/detail.html", rental=rental, close_form=close_form
    )


@rentals_bp.route("/<int:rental_id>/close", methods=["POST"])
@login_required
def close(rental_id: int):
    rental = db.session.get(Rental, rental_id) or abort(404)
    if not rental.is_active:
        flash("Aluguel já está fechado.", "warning")
        return redirect(url_for("rentals.detail", rental_id=rental.id))

    form = RentalCloseForm()
    if form.validate_on_submit():
        if form.return_date.data < rental.start_date:
            flash("A data de devolução não pode ser anterior à data de início.", "danger")
            return redirect(url_for("rentals.detail", rental_id=rental.id))
        rental.close(
            return_date=form.return_date.data,
            material_type=form.material_type.data,
        )
        db.session.commit()
        flash(f"locação fechada. Total: R$ {rental.total_amount}.", "success")
    else:
        flash("Envio de formulário inválido.", "danger")
    return redirect(url_for("rentals.detail", rental_id=rental.id))
