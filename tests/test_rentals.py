"""Rental lifecycle tests."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from app.models import Dumpster, DumpsterStatus, MaterialType, Rental, RentalStatus


def test_rental_open_locks_dumpster(open_rental, sample_driver):
    assert open_rental.is_active
    assert open_rental.dumpster.status == DumpsterStatus.RENTED.value
    assert open_rental.daily_rate == Decimal("120.00")
    assert open_rental.driver_id == sample_driver.id


def test_rental_close_computes_total_and_frees_dumpster(db, open_rental):
    return_date = open_rental.start_date + timedelta(days=2)
    open_rental.close(
        return_date=return_date,
        material_type=MaterialType.CONSTRUCTION_DEBRIS.value,
    )
    db.session.commit()

    assert open_rental.status == RentalStatus.COMPLETED.value
    assert open_rental.return_date == return_date
    assert open_rental.total_amount == Decimal("240.00")
    assert open_rental.material_type == MaterialType.CONSTRUCTION_DEBRIS.value
    assert open_rental.material_type_label == "Construction debris"
    assert open_rental.dumpster.status == DumpsterStatus.AVAILABLE.value


def test_rental_close_uses_minimum_one_day(db, open_rental):
    open_rental.close(
        return_date=open_rental.start_date,
        material_type=MaterialType.MIXED.value,
    )
    db.session.commit()
    assert open_rental.total_amount == Decimal("120.00")


def test_rental_is_overdue_after_expected_end(db, open_rental):
    open_rental.expected_end_date = date.today() - timedelta(days=1)
    db.session.commit()
    assert open_rental.is_overdue is True


def test_open_rental_via_form(
    auth_client, db, sample_client, sample_dumpster, sample_driver
):
    today = date.today()
    response = auth_client.post(
        "/rentals/new",
        data={
            "client_id": str(sample_client.id),
            "dumpster_id": str(sample_dumpster.id),
            "driver_id": str(sample_driver.id),
            "delivery_address": "Rua Teste, 1",
            "start_date": today.isoformat(),
            "expected_end_date": (today + timedelta(days=5)).isoformat(),
        },
        follow_redirects=False,
    )
    assert response.status_code == 302

    rental = db.session.query(Rental).one()
    assert rental.dumpster.status == DumpsterStatus.RENTED.value
    assert rental.daily_rate == Decimal("120.00")
    assert rental.driver_id == sample_driver.id


def test_open_rental_form_redirects_when_no_driver_registered(
    auth_client, db, sample_client, sample_dumpster
):
    # No driver fixture — expect redirect with warning
    response = auth_client.get("/rentals/new", follow_redirects=False)
    assert response.status_code == 302
    assert "/drivers/new" in response.headers["Location"]


def test_close_rental_via_form_computes_total_and_records_material(
    auth_client, db, open_rental
):
    return_date = open_rental.start_date + timedelta(days=3)
    response = auth_client.post(
        f"/rentals/{open_rental.id}/close",
        data={
            "return_date": return_date.isoformat(),
            "material_type": MaterialType.SOIL.value,
        },
        follow_redirects=False,
    )
    assert response.status_code == 302

    db.session.refresh(open_rental)
    assert open_rental.status == RentalStatus.COMPLETED.value
    assert open_rental.total_amount == Decimal("360.00")  # 3 days × R$ 120
    assert open_rental.material_type == MaterialType.SOIL.value
    assert db.session.get(Dumpster, open_rental.dumpster_id).status == (
        DumpsterStatus.AVAILABLE.value
    )


def test_close_rental_without_material_type_is_rejected(auth_client, db, open_rental):
    response = auth_client.post(
        f"/rentals/{open_rental.id}/close",
        data={"return_date": date.today().isoformat()},
        follow_redirects=True,
    )
    db.session.refresh(open_rental)
    # Form invalid — rental still active
    assert open_rental.is_active
    assert open_rental.material_type is None
    assert b"Invalid form submission" in response.data


def test_cannot_open_rental_with_unavailable_dumpster(
    auth_client, db, sample_client, sample_dumpster, sample_driver
):
    sample_dumpster.status = DumpsterStatus.MAINTENANCE.value
    db.session.commit()

    response = auth_client.get("/rentals/new", follow_redirects=False)
    # Should redirect because no available dumpsters
    assert response.status_code == 302
    assert "/dumpsters" in response.headers["Location"]
