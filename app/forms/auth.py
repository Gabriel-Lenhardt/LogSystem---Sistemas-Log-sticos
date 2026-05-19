"""Authentication forms."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from ..extensions import db
from ..models.user import User


class LoginForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired(), Length(max=80)])
    password = PasswordField("Senha", validators=[DataRequired()])
    remember_me = BooleanField("Lembrar ?")
    submit = SubmitField("Entrar")


class RegisterForm(FlaskForm):
    username = StringField("Nome", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(
        "Senha", validators=[DataRequired(), Length(min=6, max=128)]
    )
    confirm_password = PasswordField(
        "Confirmar senha",
        validators=[DataRequired(), EqualTo("Senha", message="As senhas devem corresponder.")],
    )
    submit = SubmitField("Criar conta")

    def validate_username(self, field: StringField) -> None:
        if db.session.query(User).filter_by(username=field.data).first():
            raise ValidationError("O nome de usuário já está em uso.")

    def validate_email(self, field: StringField) -> None:
        if db.session.query(User).filter_by(email=field.data).first():
            raise ValidationError("Email já está cadastrado.")
