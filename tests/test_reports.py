"""Revenue report tests."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from app.models import Dumpster, DumpsterStatus, MaterialType, Rental, RentalStatus


def _completed_rental(
    db,
    sample_client,
    sample_driver,
    *,
    identifier: str,
    return_date: date,
    start_date: date,
    daily_rate: Decimal,
    material_type: str = MaterialType.CONSTRUCTION_DEBRIS.value,
) -> Rental:
    dumpster = Dumpster(
        identifier=identifier,
        size=4.0,
        daily_rate=daily_rate,
        status=DumpsterStatus.AVAILABLE.value,
    )
    db.session.add(dumpster)
    db.session.flush()
    rental = Rental(
        client=sample_client,
        dumpster=dumpster,
        driver=sample_driver,
        delivery_address="Address",
        start_date=start_date,
        expected_end_date=return_date,
        daily_rate=daily_rate,
        status=RentalStatus.COMPLETED.value,
        return_date=return_date,
        material_type=material_type,
        total_amount=(Decimal(max(1, (return_date - start_date).days)) * daily_rate),
    )
    db.session.add(rental)
    db.session.commit()
    return rental


def test_report_blank_get_does_not_show_results(auth_client):
    response = auth_client.get("/reports/revenue")
    assert response.status_code == 200
    assert b"Total revenue" not in response.data


def test_report_sums_rentals_inside_period(
    auth_client, db, sample_client, sample_driver
):
    today = date.today()
    _completed_rental(
        db,
        sample_client,
        sample_driver,
        identifier="C-A",
        start_date=today - timedelta(days=5),
        return_date=today - timedelta(days=3),
        daily_rate=Decimal("100.00"),
    )  # 2 days × 100 = 200
    _completed_rental(
        db,
        sample_client,
        sample_driver,
        identifier="C-B",
        start_date=today - timedelta(days=2),
        return_date=today,
        daily_rate=Decimal("150.00"),
        material_type=MaterialType.SOIL.value,
    )  # 2 days × 150 = 300

    response = auth_client.get(
        "/reports/revenue",
        query_string={
            "start_date": (today - timedelta(days=10)).isoformat(),
            "end_date": today.isoformat(),
            "submit": "Generate",
        },
    )
    assert response.status_code == 200
    assert b"R$ 500.00" in response.data
    # Material labels should appear in the table
    assert b"Construction debris" in response.data
    assert b"Soil" in response.data


def test_report_excludes_rentals_outside_period(
    auth_client, db, sample_client, sample_driver
):
    today = date.today()
    _completed_rental(
        db,
        sample_client,
        sample_driver,
        identifier="C-OLD",
        start_date=today - timedelta(days=60),
        return_date=today - timedelta(days=58),
        daily_rate=Decimal("100.00"),
    )

    response = auth_client.get(
        "/reports/revenue",
        query_string={
            "start_date": (today - timedelta(days=10)).isoformat(),
            "end_date": today.isoformat(),
            "submit": "Generate",
        },
    )
    assert response.status_code == 200
    assert b"R$ 0.00" in response.data
    assert b"No completed rentals in this period" in response.data


def test_report_rejects_inverted_dates(auth_client):
    today = date.today()
    response = auth_client.get(
        "/reports/revenue",
        query_string={
            "start_date": today.isoformat(),
            "end_date": (today - timedelta(days=5)).isoformat(),
            "submit": "Generate",
        },
    )
    assert b"End date must be on or after start date" in response.data
