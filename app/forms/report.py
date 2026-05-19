"""Report forms."""

from __future__ import annotations

from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField
from wtforms.validators import DataRequired, ValidationError


def _first_day_of_month() -> date:
    today = date.today()
    return today.replace(day=1)


class RevenueReportForm(FlaskForm):
    class Meta:
        csrf = False  # read-only GET form, safe without CSRF

    start_date = DateField(
        "Data de início", default=_first_day_of_month, validators=[DataRequired()]
    )
    end_date = DateField("Data final", default=date.today, validators=[DataRequired()])
    submit = SubmitField("Gerar")

    def validate_end_date(self, field: DateField) -> None:
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("A data de término deve ser igual ou posterior à data de início.")
