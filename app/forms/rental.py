"""Rental forms."""

from __future__ import annotations

from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from ..models.rental import MATERIAL_TYPE_LABELS, MaterialType


class RentalOpenForm(FlaskForm):
    client_id = SelectField("Cliente", coerce=int, validators=[DataRequired(message="Este campo é obrigatório.")])
    dumpster_id = SelectField(
        "Caçamba (Disponível)", coerce=int, validators=[DataRequired(message="Este campo é obrigatório.")]
    )
    
    delivery_address = StringField(
        "Endereço de entrega", validators=[DataRequired(message="Este campo é obrigatório."), Length(max=200)]
    )
    start_date = DateField(
        "Data de início", default=date.today, validators=[DataRequired(message="Este campo é obrigatório.")]
    )
    expected_end_date = DateField(
        "Prazo final", validators=[DataRequired(message="Este campo é obrigatório.")]
    )
    submit = SubmitField("Locação aberta")

    def validate_expected_end_date(self, field: DateField) -> None:
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("A data de término prevista deve ser igual ou posterior à data de início.")


class RentalCloseForm(FlaskForm):
    return_date = DateField(
        "Data de retorno", default=date.today, validators=[DataRequired()]
    )
    material_type = SelectField(
        "Material descartado",
        choices=[(m.value, MATERIAL_TYPE_LABELS[m.value]) for m in MaterialType],
        validators=[DataRequired()],
    )
    submit = SubmitField("Fechamento locação")
