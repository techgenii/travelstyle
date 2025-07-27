# This file is part of TravelSytle AI.
#
# Copyright (C) 2025  Trailyn Ventures, LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
from collections import namedtuple
from types import SimpleNamespace

from app.utils.error_handlers import custom_http_exception_handler
from app.utils.user_utils import extract_user_profile
from fastapi.responses import JSONResponse


class DummyUser:
    def __init__(
        self,
        id=None,
        email=None,
        user_metadata=None,
        created_at=None,
        updated_at=None,
        email_confirmed_at=None,
        last_sign_in_at=None,
    ):
        self.id = id
        self.email = email
        self.user_metadata = user_metadata
        self.created_at = created_at
        self.updated_at = updated_at
        self.email_confirmed_at = email_confirmed_at
        self.last_sign_in_at = last_sign_in_at


def test_extract_user_profile_with_dict_metadata():
    DummyUser = namedtuple(
        "DummyUser",
        [
            "id",
            "email",
            "user_metadata",
            "created_at",
            "updated_at",
            "email_confirmed_at",
            "last_sign_in_at",
        ],
    )
    user = DummyUser(
        id="u1",
        email="test@example.com",
        user_metadata={
            "first_name": "Alice",
            "last_name": "Smith",
            "selected_style_names": ["Bohemian", "Minimalist"],
        },
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z",
        email_confirmed_at="2023-01-01T01:00:00Z",
        last_sign_in_at="2023-01-03T00:00:00Z",
    )
    profile = extract_user_profile(user)
    assert profile is not None
    assert profile["id"] == "u1"
    assert profile["email"] == "test@example.com"
    assert profile["first_name"] == "Alice"
    assert profile["last_name"] == "Smith"
    assert profile["created_at"] == "2023-01-01T00:00:00Z"
    assert profile["updated_at"] == "2023-01-02T00:00:00Z"
    assert profile["email_confirmed_at"] == "2023-01-01T01:00:00Z"
    assert profile["last_sign_in_at"] == "2023-01-03T00:00:00Z"
    assert profile["selected_style_names"] == ["Bohemian", "Minimalist"]


def test_extract_user_profile_with_object_metadata():
    metadata = SimpleNamespace(first_name="Bob", last_name="Jones")
    user = DummyUser(
        id="u2",
        email="bob@example.com",
        user_metadata=metadata,
        created_at=None,
        updated_at=None,
        email_confirmed_at=None,
        last_sign_in_at=None,
    )
    profile = extract_user_profile(user)
    assert profile is not None
    assert profile["id"] == "u2"
    assert profile["email"] == "bob@example.com"
    assert profile["first_name"] == "Bob"
    assert profile["last_name"] == "Jones"
    assert profile["created_at"] is None
    assert profile["updated_at"] is None
    assert profile["email_confirmed_at"] is None
    assert profile["last_sign_in_at"] is None


def test_extract_user_profile_with_no_metadata():
    user = DummyUser(id="u3", email="no.meta@example.com", user_metadata=None)
    profile = extract_user_profile(user)
    assert profile is not None
    assert profile["id"] == "u3"
    assert profile["email"] == "no.meta@example.com"
    assert profile["first_name"] is None
    assert profile["last_name"] is None


def test_extract_user_profile_with_missing_attributes():
    # User missing created_at, updated_at, etc.
    user = DummyUser(id="u4", email="missing@example.com", user_metadata={"first_name": "X"})
    profile = extract_user_profile(user)
    assert profile is not None
    assert profile["id"] == "u4"
    assert profile["email"] == "missing@example.com"
    assert profile["first_name"] == "X"
    assert profile["last_name"] is None
    assert profile["created_at"] is None
    assert profile["updated_at"] is None
    assert profile["email_confirmed_at"] is None
    assert profile["last_sign_in_at"] is None


def test_extract_user_profile_with_none_user():
    assert extract_user_profile(None) is None


class DummyRequest:
    url = "http://testserver/test"


def test_custom_http_exception_handler_non_http_exception():
    request = DummyRequest()
    exc = ValueError("Some error")
    response = asyncio.run(custom_http_exception_handler(request, exc))
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500
    assert response.body is not None
    assert b"Internal server error" in response.body
