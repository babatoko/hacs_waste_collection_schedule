import json
import os
import sys
from datetime import date
from unittest.mock import MagicMock, patch

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "custom_components",
            "waste_collection_schedule",
        )
    )
)

from waste_collection_schedule import Icons
from waste_collection_schedule.source.heinz_entsorgung_de import Source

SAMPLE_RESPONSE = [
    {"termin": "2026-06-01", "fraktion": "Restabfall"},
    {"termin": "2026-06-08", "fraktion": "Gelber Sack"},
    {"termin": "2026-06-15", "fraktion": "Bioabfall", "zusatz": "14-tägig"},
]


def _mock_response(payload):
    response = MagicMock()
    response.text = json.dumps(payload)
    response.raise_for_status = MagicMock()
    return response


def test_heinz_entsorgung_de():
    """Fetching parses each entry's date, waste type and icon."""
    with patch(
        "requests.get", return_value=_mock_response(SAMPLE_RESPONSE)
    ) as mock_get:
        entries = Source(param="test-param").fetch()

    mock_get.assert_called_once()
    assert mock_get.call_args.kwargs["params"] == {"param": "test-param"}

    assert len(entries) == 3
    assert entries[0].date == date(2026, 6, 1)
    assert entries[0].type == "Restabfall"
    assert entries[0].icon == Icons.GENERAL_WASTE

    assert entries[1].type == "Gelber Sack"
    assert entries[1].icon == Icons.PLASTIC_PACKAGING

    # "zusatz" is appended to the waste type but the icon lookup still
    # matches on the base fraktion name.
    assert entries[2].type == "Bioabfall (14-tägig)"
    assert entries[2].icon == Icons.BIO_KITCHEN


def test_heinz_entsorgung_de_skips_entries_without_a_date():
    payload = [{"fraktion": "Restabfall"}, *SAMPLE_RESPONSE]
    with patch("requests.get", return_value=_mock_response(payload)):
        entries = Source(param="test-param").fetch()

    assert len(entries) == 3
