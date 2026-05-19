"""Client CRUD tests."""

from __future__ import annotations

from app.models import Client


CLIENT_PAYLOAD = {
    "name": "Test Client",
    "document": "99999999999",
    "phone": "15999991234",
    "email": "test@example.com",
    "address": "Rua Teste, 1",
    "city": "Votorantim",
    "state": "sp",
    "zip_code": "18110000",
}


def test_create_client(auth_client, db):
    response = auth_client.post(
        "/clients/new", data=CLIENT_PAYLOAD, follow_redirects=False
    )
    assert response.status_code == 302
    record = db.session.query(Client).filter_by(document="99999999999").one()
    assert record.name == "Test Client"
    assert record.state == "SP"  # uppercased by the route


def test_duplicate_document_is_rejected(auth_client, sample_client):
    payload = dict(CLIENT_PAYLOAD, document=sample_client.document)
    response = auth_client.post("/clients/new", data=payload, follow_redirects=True)
    assert response.status_code == 200
    assert b"Document is already registered" in response.data


def test_edit_client_updates_record(auth_client, db, sample_client):
    payload = dict(CLIENT_PAYLOAD, document=sample_client.document, name="Updated Name")
    response = auth_client.post(
        f"/clients/{sample_client.id}/edit", data=payload, follow_redirects=False
    )
    assert response.status_code == 302
    db.session.refresh(sample_client)
    assert sample_client.name == "Updated Name"


def test_delete_client_with_active_rental_is_blocked(auth_client, db, open_rental):
    client_id = open_rental.client_id
    response = auth_client.post(
        f"/clients/{client_id}/delete", follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Cannot delete a client with active rentals" in response.data
    assert db.session.get(Client, client_id) is not None


def test_delete_client_without_rentals_succeeds(auth_client, db, sample_client):
    response = auth_client.post(
        f"/clients/{sample_client.id}/delete", follow_redirects=False
    )
    assert response.status_code == 302
    assert db.session.get(Client, sample_client.id) is None
