"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import TestingConfig
from app.extensions import db as _db
from app.models import Client, Driver, Dumpster, DumpsterStatus, Rental, User


@pytest.fixture
def app() -> Iterator[Flask]:
    """Application bound to a fresh in-memory database for each test."""
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app: Flask):
    return _db


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def admin_user(db) -> User:
    user = User(username="admin", email="admin@example.com")
    user.set_password("admin123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_client(client: FlaskClient, admin_user: User) -> FlaskClient:
    """Test client with an authenticated session."""
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    return client


@pytest.fixture
def sample_client(db) -> Client:
    record = Client(
        name="João da Silva",
        document="12345678901",
        phone="15999990001",
        email="joao@example.com",
        address="Rua das Flores, 123",
        city="Votorantim",
        state="SP",
        zip_code="18110000",
    )
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture
def sample_dumpster(db) -> Dumpster:
    record = Dumpster(
        identifier="C-001",
        size=4.0,
        daily_rate=Decimal("120.00"),
        status=DumpsterStatus.AVAILABLE.value,
    )
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture
def sample_driver(db) -> Driver:
    record = Driver(
        name="Carlos Pereira",
        document="22233344455",
        phone="15988880001",
        license_number="CNH001",
    )
    db.session.add(record)
    db.session.commit()
    return record


@pytest.fixture
def open_rental(
    db,
    sample_client: Client,
    sample_dumpster: Dumpster,
    sample_driver: Driver,
) -> Rental:
    rental = Rental(
        client=sample_client,
        dumpster=sample_dumpster,
        driver=sample_driver,
        delivery_address="Rua das Flores, 123",
        start_date=date.today() - timedelta(days=2),
        expected_end_date=date.today() + timedelta(days=3),
        daily_rate=sample_dumpster.daily_rate,
    )
    rental.open()
    db.session.add(rental)
    db.session.commit()
    return rental
