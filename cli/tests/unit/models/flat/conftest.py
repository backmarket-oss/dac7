from unittest.mock import patch

import pytest


@pytest.fixture
def mock_dpi_declaration_class():
    with patch("dac7.models.flat.DpiDeclaration") as patched:
        yield patched
