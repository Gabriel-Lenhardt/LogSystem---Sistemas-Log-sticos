"""Populate the database with sample data and a default admin user."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import (  # noqa: E402
    Client,
    Dumpster,
    DumpsterStatus,
    Rental,
    User,
)


def seed() -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        if db.session.query(User).count() == 0:
            admin = User(username="admin", email="admin@alfacacambas.com")
            admin.set_password("admin123")
            db.session.add(admin)
            print("Created admin user — username: admin / password: admin123")

        if db.session.query(Client).count() == 0:
            clients = [
                Client(
                    name="João da Silva",
                    document="12345678901",
                    phone="15999990001",
                    email="joao@example.com",
                    address="Rua das Flores, 123",
                    city="Votorantim",
                    state="SP",
                    zip_code="18110000",
                ),
                Client(
                    name="Construtora Beta Ltda",
                    document="12345678000199",
                    phone="15999990002",
                    email="contato@beta.com",
                    address="Av. Industrial, 500",
                    city="Sorocaba",
                    state="SP",
                    zip_code="18080000",
                ),
            ]
            db.session.add_all(clients)

        
        if db.session.query(Dumpster).count() == 0:
            dumpsters = [
                Dumpster(
                    identifier="C-001",
                    size=4.0,
                    daily_rate=Decimal("120.00"),
                    status=DumpsterStatus.AVAILABLE.value,
                ),
                Dumpster(
                    identifier="C-002",
                    size=4.0,
                    daily_rate=Decimal("120.00"),
                    status=DumpsterStatus.AVAILABLE.value,
                ),
                Dumpster(
                    identifier="C-003",
                    size=6.0,
                    daily_rate=Decimal("160.00"),
                    status=DumpsterStatus.AVAILABLE.value,
                ),
                Dumpster(
                    identifier="C-004",
                    size=6.0,
                    daily_rate=Decimal("160.00"),
                    status=DumpsterStatus.MAINTENANCE.value,
                ),
            ]
            db.session.add_all(dumpsters)

        db.session.commit()

        if db.session.query(Rental).count() == 0:
            client = db.session.query(Client).first()
            dumpster = (
                db.session.query(Dumpster)
                .filter_by(status=DumpsterStatus.AVAILABLE.value)
                .first()
            )
            if client and dumpster:
                rental = Rental(
                    client=client,
                    dumpster=dumpster,
                    delivery_address="Rua das Flores, 123 — Votorantim/SP",
                    start_date=date.today() - timedelta(days=2),
                    expected_end_date=date.today() + timedelta(days=3),
                    daily_rate=dumpster.daily_rate,
                )
                rental.open()
                db.session.add(rental)
                db.session.commit()
                print(f"Opened sample rental #{rental.id}")

        print("Seed complete.")


if __name__ == "__main__":
    seed()
