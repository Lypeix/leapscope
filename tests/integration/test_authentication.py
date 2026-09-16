from hashlib import sha256
from uuid import UUID

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.dependencies import get_current_device
from app.models import Device


PASSWORD = "not-so-secret-password-123"


def register_and_login(client, email):
    
    registration = client.post(
        "/auth/register",
        json={"email": email, "password": PASSWORD}
    )

    assert registration.status_code == 201, registration.text

    login = client.post(
        "/auth/login",
        json={"email": email, "password": PASSWORD}
    )

    assert login.status_code == 200, login.text

    headers = {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }

    return registration.json(), headers


def test_registration_login_current_user(client):

    user, headers = register_and_login(client, "melkor@gmail.com")

    response = client.get("/users/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == user["id"]
    assert response.json()["email"] == "melkor@gmail.com"
    assert "password_hash" not in response.json()


def test_authentication_rejects_bad_credentials(client):
    register_and_login(client, "melkor@gmail.com")

    login = client.post(
        "/auth/login",
        json = {
            "email": "melkor@gmail.com",
            "password": "invalid-password-test-123"
        }
    )
    assert login.status_code == 401
    assert "access_token" not in login.json() # makes sure server didnt assign an access token to the user who typed wrong password

    missing_token = client.get("/users/me")
    assert missing_token.status_code == 401

    invalid_token = client.get( # makes sure you cant log in with a garbage token
        "users/me",
        headers={"Authorization": "Bearer invalid-token"} 
        )
    assert invalid_token.status_code == 401


def test_collector_token_lifecycle(client, db_session):
    _, headers = register_and_login(
        client, "melkor@gmail.com"
    )

    registration = client.post(
        "/devices",
        json={"name": "Test PC"},
        headers=headers
    )
    assert registration.status_code == 201
    device_id = registration.json()["id"]

    issuance = client.post(
        f"/devices/{device_id}/token",
        headers=headers
    )
    assert issuance.status_code == 201
    assert issuance.headers["Cache-Control"] == "no-store" # tells everything that could store this response to not store it

    token = issuance.json()["collector_token"]

    device = db_session.get(Device, UUID(device_id))
    assert device is not None
    db_session.refresh(device)

    assert device.token_hash == sha256(
        token.encode("utf-8")
    ).hexdigest()

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token
    )

    authenticated_device = get_current_device(
        credentials=credentials, 
        session=db_session
        )
    assert authenticated_device.id == device.id

    repeated_issuance = client.post(
        f"/devices/{device_id}/token",
        headers=headers
    )
    assert repeated_issuance.status_code == 409

    revocation = client.post(
        f"/devices/{device_id}/revoke",
        headers=headers
    )
    assert revocation.status_code == 200
    assert revocation.json()["revoked_at"] is not None # checks whether revocation timestamp exists 


    with pytest.raises(HTTPException) as error: # checks whether the revoked token is still usable
        get_current_device(
            credentials=credentials,
            session=db_session
        )

    assert error.value.status_code == 401


def test_other_users_cant_manage_device(client, db_session):
    owner, owner_headers = register_and_login(
        client, "melkor@gmail.com"
    )

    _, other_headers = register_and_login(
        client, "sauron@gmail.com"
    )

    registration = client.post(
        "/devices",
        json={"name": "Melkor's PC"},
        headers=owner_headers
    )
    assert registration.status_code == 201
    assert registration.json()["user_id"] == owner["id"]
