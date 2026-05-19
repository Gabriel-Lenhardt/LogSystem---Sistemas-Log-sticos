"""Dashboard KPI tests."""

from __future__ import annotations

from datetime import date, timedelta


def test_dashboard_shows_kpis(auth_client, open_rental):
    response = auth_client.get("/")
    body = response.data.decode()
    assert response.status_code == 200
    # 1 client, 1 dumpster (rented), 1 active rental
    assert "Clients" in body
    assert "Active rentals" in body
    assert "Available dumpsters" in body


def test_dashboard_flags_overdue_rentals(auth_client, db, open_rental):
    open_rental.expected_end_date = date.today() - timedelta(days=2)
    db.session.commit()

    response = auth_client.get("/")
    assert b"overdue" in response.data.lower()
