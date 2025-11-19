from datetime import UTC
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from dac7.models.enums import Env
from dac7.models.flat import Declaration
from dac7.models.flat import WithReportableSellers


@pytest.mark.parametrize(
    ("env", "expected_message_ref_indic"),
    [
        (Env.PROD, "OP_2025_123456789_d1"),
        (Env.TEST, "OP_2025_123456789_t1_d1"),
    ],
)
def test_get_dpi(mock_dpi_declaration_class: MagicMock, env: Env, expected_message_ref_indic: str) -> None:
    # Given
    mock_reportable_entity_sellers = MagicMock()
    mock_reportable_individual_sellers = MagicMock()
    mock_timestamp = MagicMock()
    mock_platform_operator = MagicMock(main_tax_identification_number="123456789")
    mock_other_platform_operators = MagicMock()

    declaration = Declaration.model_construct(
        reportable_entity_sellers=mock_reportable_entity_sellers,
        reportable_individual_sellers=mock_reportable_individual_sellers,
        fiscal_year=2025,
        declaration_id=1,
        timestamp=mock_timestamp,
        platform_operator=mock_platform_operator,
        other_platform_operators=mock_other_platform_operators,
        env=env,
    )

    # When
    with (
        patch.object(Declaration, "get_timestamp_dpi") as mock_get_timestamp_dpi,
        patch.object(WithReportableSellers, "get_reportable_sellers_dpi") as mock_get_reportable_sellers_dpi,
    ):
        dpi_declaration = declaration.get_dpi()

    # Then
    mock_get_timestamp_dpi.assert_called_once_with()
    mock_platform_operator.get_platform_dpi.assert_called_once_with(declaration=declaration)
    mock_other_platform_operators.get_dpi.assert_called_once_with(declaration=declaration)
    mock_get_reportable_sellers_dpi.assert_called_once_with(declaration=declaration)
    mock_dpi_declaration_class.model_validate.assert_called_once_with(
        {
            "@xmlns:dpi": "urn:oecd:ties:dpi",
            "@xmlns:stf": "urn:oecd:ties:dpistf",
            "@version": "1.0",
            "dpi:MessageSpec": {
                "dpi:TransmittingCountry": "FR",
                "dpi:ReceivingCountry": "FR",
                "dpi:MessageType": "DPI",
                "dpi:MessageRefId": expected_message_ref_indic,
                "dpi:MessageTypeIndic": "DPI403",
                "dpi:ReportingPeriod": "2025-12-31",
                "dpi:Timestamp": mock_get_timestamp_dpi.return_value,
            },
            "dpi:DPIBody": {
                "dpi:PlatformOperator": mock_platform_operator.get_platform_dpi.return_value,
                "dpi:OtherPlatformOperators": mock_other_platform_operators.get_dpi.return_value,
                "dpi:ReportableSeller": mock_get_reportable_sellers_dpi.return_value,
            },
        }
    )
    assert dpi_declaration == mock_dpi_declaration_class.model_validate.return_value


@pytest.mark.parametrize(
    ("timezone", "expected_timestamp_dpi"),
    [
        (None, "2025-01-12T04:05:06.987"),
        (ZoneInfo("Europe/Paris"), "2025-01-12T04:05:06.987"),
        (UTC, "2025-01-12T05:05:06.987"),
    ],
)
def test_get_timestamp_dpi(timezone: ZoneInfo | None, expected_timestamp_dpi: str) -> None:
    # Given
    timestamp = datetime(2025, 1, 12, 4, 5, 6, microsecond=987654)
    if timezone:
        timestamp = timestamp.replace(tzinfo=timezone)

    mock_reportable_entity_sellers = MagicMock()
    mock_reportable_individual_sellers = MagicMock()
    mock_platform_operator = MagicMock(main_tax_identification_number="123456789")
    mock_other_platform_operators = MagicMock()
    mock_env = MagicMock()

    declaration = Declaration.model_construct(
        reportable_entity_sellers=mock_reportable_entity_sellers,
        reportable_individual_sellers=mock_reportable_individual_sellers,
        fiscal_year=2025,
        declaration_id=1,
        timestamp=timestamp,
        platform_operator=mock_platform_operator,
        other_platform_operators=mock_other_platform_operators,
        env=mock_env,
    )

    # When
    timestamp_dpi = declaration.get_timestamp_dpi()

    # Then
    assert timestamp_dpi == expected_timestamp_dpi
