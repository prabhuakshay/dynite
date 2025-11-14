import responses

from dynite import Dynite


class TestClientNextPageLink:
    """Tests for the _get_next_page_link method of the Dynite class."""

    @responses.activate
    def test_client_next_page_link_present(self) -> None:
        """Test the _get_next_page_link method when the next page link is present."""
        url = "https://example.com/odata/entities"
        next_link = "https://example.com/odata/entities?$skip=10"

        responses.add(
            method=responses.GET,
            url=url,
            json={"value": [{"id": 1}, {"id": 2}], "@odata.nextLink": next_link},
            status=200,
        )

        client = Dynite(base_url="https://example.com/odata/", auth=("user", "pass"))
        response = client._get(url)
        extracted_link = client._get_next_page_link(response)

        assert extracted_link == next_link

    @responses.activate
    def test_client_next_page_link_absent(self) -> None:
        """Test the _get_next_page_link method when the next page link is absent."""
        url = "https://example.com/odata/entities"

        responses.add(
            method=responses.GET,
            url=url,
            json={"value": [{"id": 1}, {"id": 2}]},
            status=200,
        )

        client = Dynite(base_url="https://example.com/odata/", auth=("user", "pass"))
        response = client._get(url)
        extracted_link = client._get_next_page_link(response)

        assert extracted_link is None
