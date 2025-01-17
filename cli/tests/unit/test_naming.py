from dac7.naming import build_filename


def test_build_filename():
    # Given
    message_ref_id = "OP_2024_123456789_doesntmatter"
    timestamp = "2025-01-02T03:04:05.678"
    declaration_id = 1

    # When
    result_filename = build_filename(
        message_ref_id=message_ref_id,
        timestamp=timestamp,
        declaration_id=declaration_id,
    )

    # Then
    assert result_filename == "DPIDAC7_2024_123456789_001_20250102030405"
