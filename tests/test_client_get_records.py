"""Tests for Dynite client get records functionality."""

from logging import getLogger

import pytest
import responses

from dynite import Dynite
from dynite.exceptions import InvalidResponseError

logger = getLogger(__name__)
# Set log level to debug
logger.setLevel("DEBUG")


class TestClientGetRecords:
    """Tests for Dynite client get records functionality."""

    URL: str = "https://api.dynite.com/v1/records"
    AUTH: tuple[str, str] = ("username", "password")
    CLIENT: Dynite = Dynite(base_url=URL, auth=AUTH)

    @responses.activate
    def test_get_records_without_pagination(self) -> None:
        """Test successful retrieval of records."""

        responses.add(
            responses.GET,
            f"{self.URL}/items",
            json={
                "value": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"},
                ]
            },
            status=200,
        )

        records = self.CLIENT.get_records("items")

        assert len(records) == 2
        assert records[0]["id"] == 1
        assert records[1]["name"] == "Item 2"
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_records_with_pagination(self) -> None:
        """Test retrieval of records with pagination."""

        responses.add(
            responses.GET,
            f"{self.URL}/items",
            json={
                "value": [
                    {"id": 1, "name": "Item 1"},
                    {"id": 2, "name": "Item 2"},
                ],
                "@odata.nextLink": f"{self.URL}/items?page=2",
            },
            status=200,
        )

        responses.add(
            responses.GET,
            f"{self.URL}/items?page=2",
            json={
                "value": [
                    {"id": 3, "name": "Item 3"},
                    {"id": 4, "name": "Item 4"},
                ]
            },
            status=200,
        )

        records = self.CLIENT.get_records("items")

        assert len(records) == 4
        assert records[2]["id"] == 3
        assert records[3]["name"] == "Item 4"
        assert len(responses.calls) == 2

    @responses.activate
    def test_get_records_empty_response(self) -> None:
        """Test retrieval of records with an empty response."""

        responses.add(
            responses.GET,
            f"{self.URL}/items",
            json={"value": []},
            status=200,
        )

        records = self.CLIENT.get_records("items")

        assert len(records) == 0
        assert len(responses.calls) == 1

    @responses.activate
    def test_get_records_invalid_response(self) -> None:
        """Test retrieval of records with an invalid response."""

        responses.add(
            responses.GET,
            f"{self.URL}/items",
            body="Invalid JSON",
            status=200,
        )
        with pytest.raises(InvalidResponseError):
            self.CLIENT.get_records("items")
