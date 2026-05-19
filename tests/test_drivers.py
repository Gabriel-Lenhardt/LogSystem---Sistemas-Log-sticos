"""Driver CRUD tests."""

from __future__ import annotations

from app.models import Driver


DRIVER_PAYLOAD = {
    "name": "Test Driver",
    "document": "11122233344",
    "phone": "15988889999",
    "license_number": "CNH-TEST-01",
}


def test_create_driver(auth_client, db):
    response = auth_client.post(
        "/drivers/new", data=DRIVER_PAYLOAD, follow_redirects=False
    )
    assert response.status_code == 302
    record = db.session.query(Driver).filter_by(document="11122233344").one()
    assert record.name == "Test Driver"
    assert record.license_number == "CNH-TEST-01"


def test_duplicate_document_is_rejected(auth_client, sample_driver):
    payload = dict(DRIVER_PAYLOAD, document=sample_driver.document)
    response = auth_client.post("/drivers/new", data=payload, follow_redirects=True)
    assert b"Document is already registered" in response.data


def test_duplicate_license_is_rejected(auth_client, sample_driver):
    payload = dict(DRIVER_PAYLOAD, license_number=sample_driver.license_number)
    response = auth_client.post("/drivers/new", data=payload, follow_redirects=True)
    assert b"License number is already registered" in response.data


def test_edit_driver_updates_record(auth_client, db, sample_driver):
    payload = dict(
        DRIVER_PAYLOAD,
        document=sample_driver.document,
        license_number=sample_driver.license_number,
        name="Updated Driver",
    )
    response = auth_client.post(
        f"/drivers/{sample_driver.id}/edit", data=payload, follow_redirects=False
    )
    assert response.status_code == 302
    db.session.refresh(sample_driver)
    assert sample_driver.name == "Updated Driver"


def test_delete_driver_with_active_rental_is_blocked(auth_client, db, open_rental):
    driver_id = open_rental.driver_id
    response = auth_client.post(
        f"/drivers/{driver_id}/delete", follow_redirects=True
    )
    assert b"Cannot delete a driver with active rentals" in response.data
    assert db.session.get(Driver, driver_id) is not None


def test_delete_driver_without_rentals_succeeds(auth_client, db, sample_driver):
    response = auth_client.post(
        f"/drivers/{sample_driver.id}/delete", follow_redirects=False
    )
    assert response.status_code == 302
    assert db.session.get(Driver, sample_driver.id) is None


def test_drivers_index_lists_drivers(auth_client, sample_driver):
    response = auth_client.get("/drivers/")
    assert response.status_code == 200
    assert sample_driver.name.encode() in response.data
    assert sample_driver.license_number.encode() in response.data
