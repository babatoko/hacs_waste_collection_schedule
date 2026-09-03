"""
Test for Midlothian Council waste collection source.
"""

import os
import sys
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

# Put the core library on sys.path directly (matching test_source_components.py)
# rather than importing through custom_components.waste_collection_schedule,
# whose __init__ pulls in homeassistant just to reach this pure-python source.
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "custom_components",
            "waste_collection_schedule",
        )
    ),
)

from waste_collection_schedule.source import midlothian_gov_uk

# Test data
TEST_UPRN = "120001401"
TEST_POSTCODE = "EH26 8AG"

# The AchieveForms-style flow behind this source: an auth call that hands
# back a session id, a domain lookup that's fetched but otherwise ignored,
# and a runLookup POST whose "rows_data" holds the actual collections.
ROWS_DATA = {
    "0": {"Date": "27/04/2026 00:00:00", "Service": "Food Collection Service"},
    "1": {"Date": "27/04/2026 00:00:00", "Service": "Residual Collection Service"},
    "2": {"Date": "04/05/2026 00:00:00", "Service": "Garden Collection Service"},
}


def _response(json_data=None, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.raise_for_status = MagicMock()
    response.json.return_value = json_data
    return response


def _mock_session(rows_data=ROWS_DATA, auth_session="test-sid"):
    session = MagicMock()
    session.get.side_effect = [
        _response({"auth-session": auth_session}),  # AUTH_URL
        _response({}),  # DOMAIN_URL
    ]
    session.post.return_value = _response(
        {"integration": {"transformed": {"rows_data": rows_data}}}
    )
    return session


@pytest.fixture
def source():
    return midlothian_gov_uk.Source(uprn=TEST_UPRN, postcode=TEST_POSTCODE)


@patch("waste_collection_schedule.source.midlothian_gov_uk.requests.Session")
def test_fetch_returns_collections(mock_session_cls, source):
    """Test that fetch returns a non-empty list of collections."""
    mock_session_cls.return_value = _mock_session()
    collections = source.fetch()
    assert isinstance(collections, list)
    assert len(collections) == 3


@patch("waste_collection_schedule.source.midlothian_gov_uk.requests.Session")
def test_collections_have_required_fields(mock_session_cls, source):
    """Test that each collection has date, type, and icon fields."""
    mock_session_cls.return_value = _mock_session()
    for collection in source.fetch():
        assert collection.date is not None
        assert collection.type is not None
        assert collection.icon is not None


@patch("waste_collection_schedule.source.midlothian_gov_uk.requests.Session")
def test_collection_dates_are_parsed(mock_session_cls, source):
    """Test that the council's DD/MM/YYYY HH:MM:SS dates are parsed correctly."""
    mock_session_cls.return_value = _mock_session()
    collections = source.fetch()
    dates_by_type = {c.type: c.date for c in collections}
    assert dates_by_type["Food Collection Service"] == date(2026, 4, 27)
    assert dates_by_type["Garden Collection Service"] == date(2026, 5, 4)


@patch("waste_collection_schedule.source.midlothian_gov_uk.requests.Session")
def test_icons_match_collection_types(mock_session_cls, source):
    """Test that icons are correctly mapped to their collection types."""
    mock_session_cls.return_value = _mock_session()
    for collection in source.fetch():
        expected_icon = midlothian_gov_uk.ICON_MAP.get(collection.type)
        assert collection.icon == expected_icon


def test_source_initialization():
    """Test that Source class initializes correctly with UPRN and postcode."""
    source = midlothian_gov_uk.Source(uprn=TEST_UPRN, postcode=TEST_POSTCODE)
    assert isinstance(source, midlothian_gov_uk.Source)


@patch("waste_collection_schedule.source.midlothian_gov_uk.requests.Session")
def test_no_rows_raises_source_argument_not_found(mock_session_cls, source):
    """An empty rows_data means the council returned no data for this address."""
    from waste_collection_schedule.exceptions import SourceArgumentNotFound

    mock_session_cls.return_value = _mock_session(rows_data={})
    with pytest.raises(SourceArgumentNotFound):
        source.fetch()
