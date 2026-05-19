"""Client CRUD routes."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import login_required

from ..extensions import db
from ..forms.client import ClientForm
from ..models.client import Client

clients_bp = Blueprint("clients", __name__)


@clients_bp.route("/")
@login_required
def index():
    clients = db.session.query(Client).order_by(Client.name).all()
    return render_template("clients/index.html", clients=clients)


@clients_bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = ClientForm()
    if form.validate_on_submit():
        client = Client()
        form.populate_obj(client)
        client.state = client.state.upper()
        db.session.add(client)
        db.session.commit()
        flash("Cliente criado.", "success")
        return redirect(url_for("clients.index"))
    return render_template("clients/form.html", form=form, title="Novo cliente")


@clients_bp.route("/<int:client_id>")
@login_required
def detail(client_id: int):
    client = db.session.get(Client, client_id) or abort(404)
    return render_template("clients/detail.html", client=client)


@clients_bp.route("/<int:client_id>/edit", methods=["GET", "POST"])
@login_required
def edit(client_id: int):
    client = db.session.get(Client, client_id) or abort(404)
    form = ClientForm(obj=client, client_id=client.id)
    if form.validate_on_submit():
        form.populate_obj(client)
        client.state = client.state.upper()
        db.session.commit()
        flash("Cliente atualizado", "success")
        return redirect(url_for("clients.detail", client_id=client.id))
    return render_template(
        "clients/form.html", form=form, title=f"Editar {client.name}"
    )


@clients_bp.route("/<int:client_id>/delete", methods=["POST"])
@login_required
def delete(client_id: int):
    client = db.session.get(Client, client_id) or abort(404)
    if client.active_rentals_count > 0:
        flash("Não é possível excluir um cliente com locações ativas.", "danger")
        return redirect(url_for("clients.detail", client_id=client.id))
    db.session.delete(client)
    db.session.commit()
    flash("Cliente deletado.", "info")
    return redirect(url_for("clients.index"))
