"""Dumpster CRUD routes."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..extensions import db
from ..forms.dumpster import DumpsterForm
from ..models.dumpster import Dumpster, DumpsterStatus

dumpsters_bp = Blueprint("dumpsters", __name__)


@dumpsters_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status")
    query = db.session.query(Dumpster).order_by(Dumpster.identifier)
    if status_filter in {s.value for s in DumpsterStatus}:
        query = query.filter(Dumpster.status == status_filter)
    dumpsters = query.all()
    return render_template(
        "dumpsters/index.html",
        dumpsters=dumpsters,
        status_filter=status_filter,
        statuses=list(DumpsterStatus),
    )


@dumpsters_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = DumpsterForm()
    if form.validate_on_submit():
        dumpster = Dumpster()
        form.populate_obj(dumpster)
        db.session.add(dumpster)
        db.session.commit()
        flash("Caçamba criada.", "success")
        return redirect(url_for("dumpsters.index"))
    return render_template("dumpsters/form.html", form=form, title="Nova caçamba")


@dumpsters_bp.route("/<int:dumpster_id>/edit", methods=["GET", "POST"])
@login_required
def edit(dumpster_id: int):
    dumpster = db.session.get(Dumpster, dumpster_id) or abort(404)
    form = DumpsterForm(obj=dumpster, dumpster_id=dumpster.id)
    if form.validate_on_submit():
        form.populate_obj(dumpster)
        db.session.commit()
        flash("Caçamba atualizada.", "success")
        return redirect(url_for("dumpsters.index"))
    return render_template(
        "dumpsters/form.html",
        form=form,
        title=f"Editar caçamba {dumpster.identifier}",
    )


@dumpsters_bp.route("/<int:dumpster_id>/delete", methods=["POST"])
@login_required
def delete(dumpster_id: int):
    dumpster = db.session.get(Dumpster, dumpster_id) or abort(404)
    if dumpster.rentals:
        flash("Não é possível deletar esta caçamba pois ela possui históricos de locação vinculados.", "danger")
        return redirect(url_for("dumpsters.index"))
    db.session.delete(dumpster)
    db.session.commit()
    flash("Caçamba deletada.", "info")
    return redirect(url_for("dumpsters.index"))
