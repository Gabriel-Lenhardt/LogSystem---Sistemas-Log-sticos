"""Client form."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError

from ..extensions import db
from ..models.client import Client


class ClientForm(FlaskForm):
    name = StringField("Nome completo", validators=[DataRequired(), Length(max=120)])
    document = StringField(
        "CPF / CNPJ", validators=[DataRequired(), Length(min=11, max=20)]
    )
    phone = StringField("Telefone", validators=[DataRequired(), Length(max=20)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    address = StringField("Endereço", validators=[DataRequired(), Length(max=200)])
    city = StringField("Cidade", validators=[DataRequired(), Length(max=80)])
    state = StringField("Estado (UF)", validators=[DataRequired(), Length(min=2, max=2)])
    zip_code = StringField("CEP", validators=[DataRequired(), Length(max=10)])
    submit = SubmitField("Salvar")

    def __init__(self, *args, client_id: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_id = client_id

    def validate_document(self, field: StringField) -> None:
        query = db.session.query(Client).filter(Client.document == field.data)
        if self._client_id is not None:
            query = query.filter(Client.id != self._client_id)
        if query.first():
            raise ValidationError("Documento ja está registrado.")
