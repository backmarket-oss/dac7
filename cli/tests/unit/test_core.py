from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from dac7.core import build_filename_from_xml_data


def test_build_filename_from_xml_data(mock_schema: MagicMock, mock_build_filename: MagicMock) -> None:
    # Given
    xml_data = "fake_xml_data"
    mock_build_filename.return_value = "fake_filename"
    declaration_id = 1
    mock_xml_data = MagicMock()
    mock_schema.decode.return_value = mock_xml_data

    # When
    result_filename = build_filename_from_xml_data(xml_data=xml_data, declaration_id=declaration_id)

    # Then
    mock_schema.validate.assert_called_once_with(xml_data)
    mock_schema.decode.assert_called_once_with(xml_data)
    mock_build_filename.assert_called_once_with(
        message_ref_id=mock_xml_data["dpi:MessageSpec"]["dpi:MessageRefId"],
        timestamp=mock_xml_data["dpi:MessageSpec"]["dpi:Timestamp"],
        declaration_id=declaration_id,
    )

    expected_filename = "fake_filename.xml"
    assert result_filename == expected_filename


@pytest.fixture
def mock_schema():
    with patch("xmlschema.XMLSchema10") as patched:
        yield patched.return_value


@pytest.fixture
def mock_build_filename():
    with patch("dac7.core.build_filename") as patched:
        yield patched
