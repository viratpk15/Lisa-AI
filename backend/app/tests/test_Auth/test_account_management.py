"""
Jarvis AIOS — Authentication Account Management Tests
------------------------------------------------------
Tests for password change and account deletion features:
- Password change with correct current password succeeds
- Password change with incorrect current password raises 400
- Login works with updated password and rejects previous password
- Account deletion with incorrect password fails
- Account deletion with correct password permanently removes user and data
"""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from app.Auth.database import UserDatabase
from app.Auth.service import AuthService
from app.main import app


@pytest.fixture
def temp_db_path() -> str:
    """Provide a temporary database path for test isolation."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def auth_service_isolated(temp_db_path: str) -> AuthService:
    """Provide an AuthService with an isolated test SQLite DB."""
    test_db = UserDatabase(db_path=temp_db_path)
    return AuthService(db=test_db)


def test_service_change_password(auth_service_isolated: AuthService) -> None:
    """Verify password change service logic."""
    user = auth_service_isolated.register("testuser@jarvis.ai", "OldPassword123")

    # Wrong current password fails
    with pytest.raises(ValueError, match="Current password is incorrect"):
        auth_service_isolated.change_password(user.id, "WrongPass123", "NewPassword456")

    # Short new password fails
    with pytest.raises(ValueError, match="at least 8 characters"):
        auth_service_isolated.change_password(user.id, "OldPassword123", "short")

    # Correct change succeeds
    assert auth_service_isolated.change_password(user.id, "OldPassword123", "NewPassword456") is True

    # Old password no longer works for login
    with pytest.raises(ValueError, match="Invalid email or password"):
        auth_service_isolated.login("testuser@jarvis.ai", "OldPassword123")

    # New password works for login
    token = auth_service_isolated.login("testuser@jarvis.ai", "NewPassword456")
    assert token.access_token is not None


def test_service_delete_account(auth_service_isolated: AuthService) -> None:
    """Verify account deletion service logic."""
    user = auth_service_isolated.register("todelete@jarvis.ai", "MySecretPassword123")

    # Wrong password fails
    with pytest.raises(ValueError, match="Incorrect password"):
        auth_service_isolated.delete_account(user.id, "WrongPassword123")

    # Correct password deletes account
    assert auth_service_isolated.delete_account(user.id, "MySecretPassword123") is True

    # User no longer exists
    assert auth_service_isolated.get_user(user.id) is None
    with pytest.raises(ValueError, match="Invalid email or password"):
        auth_service_isolated.login("todelete@jarvis.ai", "MySecretPassword123")


def test_routes_change_password_and_delete() -> None:
    """Verify change-password and delete-account API endpoints with TestClient."""
    from app.Auth.dependencies import get_current_user
    prev_override = app.dependency_overrides.pop(get_current_user, None)
    try:
        import time
        unique_email = f"account_{int(time.time() * 1000)}@testcase.org"
        client = TestClient(app)

        reg_resp = client.post("/auth/register", json={
            "email": unique_email,
            "password": "InitialPassword123!"
        })
        assert reg_resp.status_code == 201

        login_resp = client.post("/auth/login", json={
            "email": unique_email,
            "password": "InitialPassword123!"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Change password with wrong password
        err_resp = client.post("/auth/change-password", headers=headers, json={
            "current_password": "WrongPassword999",
            "new_password": "BrandNewPassword123!"
        })
        assert err_resp.status_code == 400

        # 2. Change password successfully
        ok_resp = client.post("/auth/change-password", headers=headers, json={
            "current_password": "InitialPassword123!",
            "new_password": "BrandNewPassword123!"
        })
        assert ok_resp.status_code == 200
        assert ok_resp.json()["success"] is True

        # 3. Old password login rejected
        bad_login = client.post("/auth/login", json={
            "email": unique_email,
            "password": "InitialPassword123!"
        })
        assert bad_login.status_code == 401

        # 4. New password login succeeds
        good_login = client.post("/auth/login", json={
            "email": unique_email,
            "password": "BrandNewPassword123!"
        })
        assert good_login.status_code == 200
        new_token = good_login.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        # 5. Delete account with wrong password fails
        del_fail = client.request("DELETE", "/auth/account", headers=new_headers, json={
            "password": "WrongPassword"
        })
        assert del_fail.status_code == 400

        # 6. Delete account with correct password succeeds
        del_ok = client.request("DELETE", "/auth/account", headers=new_headers, json={
            "password": "BrandNewPassword123!"
        })
        assert del_ok.status_code == 200
        assert del_ok.json()["success"] is True
    finally:
        if prev_override is not None:
            app.dependency_overrides[get_current_user] = prev_override
