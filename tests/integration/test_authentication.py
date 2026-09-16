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
    assert response.json("email") == "melkor@gmail.com"
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