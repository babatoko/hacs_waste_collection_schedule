import os
import sys
from datetime import date, timedelta

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

from waste_collection_schedule.service import ArcGis
from waste_collection_schedule.source import darebin_vic_gov_au

# Darebin's date selection (get_next_n_dates / most_recent_weekday) now lives
# in the shared ArcGis service (used by ~20 other sources), not in
# darebin_vic_gov_au itself. These tests exercise it through that module.


class FixedDate(date):
    @classmethod
    def today(cls):
        # Fix today's date for test consistency
        return date(2025, 8, 9)


def test_past_date_moves_forward(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    start_date = date(2025, 8, 1)
    n = 2
    delta = timedelta(days=7)
    expected = [date(2025, 8, 15), date(2025, 8, 22)]

    results = ArcGis.get_next_n_dates(start_date, n, delta)
    assert results == expected, (
        f"Expected dates {expected} for start_date={start_date}, "
        f"n={n}, delta={delta}, but got {results}"
    )


def test_start_date_is_today(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    start_date = date(2025, 8, 9)
    n = 2
    delta = timedelta(days=7)
    expected = [date(2025, 8, 9), date(2025, 8, 16)]

    results = ArcGis.get_next_n_dates(start_date, n, delta)
    assert results == expected, (
        f"Expected {expected} for start_date={start_date}, "
        f"n={n}, delta={delta}, but got {results}"
    )


def test_start_date_after_today_no_skip(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    start_date = date(2025, 8, 15)
    n = 2
    delta = timedelta(days=14)
    expected = [date(2025, 8, 15), date(2025, 8, 29)]

    results = ArcGis.get_next_n_dates(start_date, n, delta)
    assert results == expected, (
        f"Expected {expected} for start_date={start_date}, "
        f"n={n}, delta={delta}, but got {results}"
    )


def test_multiple_weeks_ahead(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    start_date = date(2025, 9, 1)
    n = 3
    delta = timedelta(weeks=6)
    expected = [date(2025, 9, 1), date(2025, 10, 13), date(2025, 11, 24)]

    results = ArcGis.get_next_n_dates(start_date, n, delta)
    assert results == expected, (
        f"Expected {expected} for start_date={start_date}, "
        f"n={n}, delta={delta}, but got {results}"
    )


def test_future_date_less_than_delta(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    start_date = date(2025, 8, 15)
    n = 2
    delta = timedelta(days=14)
    expected = [date(2025, 8, 15), date(2025, 8, 29)]

    results = ArcGis.get_next_n_dates(start_date, n, delta)
    assert results == expected, (
        f"Expected {expected} for start_date={start_date}, "
        f"n={n}, delta={delta}, but got {results}"
    )


def test_most_recent_weekday_monday(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    collection_day = "Monday"
    expected = date(2025, 8, 4)

    results = ArcGis.most_recent_weekday(darebin_vic_gov_au.WEEKDAY_MAP[collection_day])
    assert results == expected, (
        f"Expected {expected} for day_of_week={collection_day}, but got {results}"
    )


def test_most_recent_weekday_tuesday(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    collection_day = "Tuesday"
    expected = date(2025, 8, 5)

    results = ArcGis.most_recent_weekday(darebin_vic_gov_au.WEEKDAY_MAP[collection_day])
    assert results == expected, (
        f"Expected {expected} for day_of_week={collection_day}, but got {results}"
    )


def test_most_recent_weekday_wednesday(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    collection_day = "Wednesday"
    expected = date(2025, 8, 6)

    results = ArcGis.most_recent_weekday(darebin_vic_gov_au.WEEKDAY_MAP[collection_day])
    assert results == expected, (
        f"Expected {expected} for day_of_week={collection_day}, but got {results}"
    )


def test_most_recent_weekday_thursday(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    collection_day = "Thursday"
    expected = date(2025, 8, 7)

    results = ArcGis.most_recent_weekday(darebin_vic_gov_au.WEEKDAY_MAP[collection_day])
    assert results == expected, (
        f"Expected {expected} for day_of_week={collection_day}, but got {results}"
    )


def test_most_recent_weekday_friday(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    collection_day = "Friday"
    expected = date(2025, 8, 8)

    results = ArcGis.most_recent_weekday(darebin_vic_gov_au.WEEKDAY_MAP[collection_day])
    assert results == expected, (
        f"Expected {expected} for day_of_week={collection_day}, but got {results}"
    )


def test_most_recent_weekday_saturday(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    collection_day = "Saturday"
    expected = date(2025, 8, 9)

    results = ArcGis.most_recent_weekday(darebin_vic_gov_au.WEEKDAY_MAP[collection_day])
    assert results == expected, (
        f"Expected {expected} for day_of_week={collection_day}, but got {results}"
    )


def test_most_recent_weekday_sunday(monkeypatch):
    monkeypatch.setattr(ArcGis, "date", FixedDate)
    collection_day = "Sunday"
    expected = date(2025, 8, 3)

    results = ArcGis.most_recent_weekday(darebin_vic_gov_au.WEEKDAY_MAP[collection_day])
    assert results == expected, (
        f"Expected {expected} for day_of_week={collection_day},  but got {results}"
    )
