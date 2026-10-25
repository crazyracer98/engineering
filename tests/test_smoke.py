"""Smoke test keeping the pytest hook green until real tests exist."""

import taxonomy


def test_import() -> None:
    assert taxonomy.__doc__
