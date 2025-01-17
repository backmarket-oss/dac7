from pathlib import Path
from typing import Generator
from unittest import mock

import pytest
import typer.testing

from dac7.main import app

runner = typer.testing.CliRunner()


def test__all_parameters(
    mock_xmlschema_class: mock.MagicMock,
    schema_path: Path,
    data_path: Path,
) -> None:
    # Given
    mock_schema: mock.MagicMock = mock_xmlschema_class.return_value

    # When
    runner.invoke(app, ["validate", "-x", f"{schema_path}", f"{data_path}"])

    # Then
    mock_xmlschema_class.assert_called_once_with(schema_path)
    mock_schema.validate.assert_called_once_with(data_path.read_text())


@pytest.fixture
def schema_path(tmp_path: Path) -> Path:
    file_path = tmp_path / "schema.xsd"
    file_path.write_text("fake schema")
    return file_path


@pytest.fixture
def data_path(tmp_path: Path) -> Path:
    file_path = tmp_path / "data.xml"
    file_path.touch()
    return file_path


@pytest.fixture
def mock_xmlschema_class() -> Generator[mock.MagicMock, None, None]:
    with mock.patch("dac7.main.xmlschema.XMLSchema10") as patched:
        yield patched
