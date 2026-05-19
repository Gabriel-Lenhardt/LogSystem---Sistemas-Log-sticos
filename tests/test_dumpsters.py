"""Dumpster CRUD tests."""

from __future__ import annotations

from decimal import Decimal

from app.models import Dumpster, DumpsterStatus


def test_create_dumpster(auth_client, db):
    response = auth_client.post(
        "/dumpsters/new",
        data={
            "identifier": "C-099",
            "size": "5.0",
            "daily_rate": "150.00",
            "status": DumpsterStatus.AVAILABLE.value,
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    record = db.session.query(Dumpster).filter_by(identifier="C-099").one()
    assert record.size == 5.0
    assert record.daily_rate == Decimal("150.00")


def test_duplicate_identifier_is_rejected(auth_client, sample_dumpster):
    response = auth_client.post(
        "/dumpsters/new",
        data={
            "identifier": sample_dumpster.identifier,
            "size": "3.0",
            "daily_rate": "100",
            "status": DumpsterStatus.AVAILABLE.value,
        },
        follow_redirects=True,
    )
    assert b"Identifier is already in use" in response.data


def test_delete_rented_dumpster_is_blocked(auth_client, db, open_rental):
    dumpster_id = open_rental.dumpster_id
    response = auth_client.post(
        f"/dumpsters/{dumpster_id}/delete", follow_redirects=True
    )
    assert b"Cannot delete a dumpster that is currently rented" in response.data
    assert db.session.get(Dumpster, dumpster_id) is not None


def test_index_filters_by_status(auth_client, sample_dumpster, db):
    db.session.add(
        Dumpster(
            identifier="C-MAINT",
            size=4.0,
            daily_rate=Decimal("100"),
            status=DumpsterStatus.MAINTENANCE.value,
        )
    )
    db.session.commit()

    response = auth_client.get("/dumpsters/?status=available")
    assert b"C-001" in response.data
    assert b"C-MAINT" not in response.data
