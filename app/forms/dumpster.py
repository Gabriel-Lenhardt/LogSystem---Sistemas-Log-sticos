"""Dumpster form."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import DecimalField, FloatField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError

from ..extensions import db
from ..models.dumpster import Dumpster, DumpsterStatus


class DumpsterForm(FlaskForm):
    identifier = StringField(
        "Identificador", validators=[DataRequired(), Length(max=20)]
    )
    size = FloatField(
        "Tamanho (m³)", validators=[DataRequired(), NumberRange(min=0.1, max=50)]
    )
    daily_rate = DecimalField(
        "Diária (R$)",
        places=2,
        rounding=None,
        validators=[DataRequired(), NumberRange(min=0)],
    )
    status = SelectField(
        "Status",
        choices=[(s.value, s.value.capitalize()) for s in DumpsterStatus],
        validators=[DataRequired()],
    )
    submit = SubmitField("Salvar")

    def __init__(self, *args, dumpster_id: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._dumpster_id = dumpster_id

    def validate_identifier(self, field: StringField) -> None:
        query = db.session.query(Dumpster).filter(Dumpster.identifier == field.data)
        if self._dumpster_id is not None:
            query = query.filter(Dumpster.id != self._dumpster_id)
        if query.first():
            raise ValidationError("O indentificador já está em uso.")
