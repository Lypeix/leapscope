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