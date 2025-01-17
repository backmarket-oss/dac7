import pytest

from dac7.models.flat import ReportableIndividualSeller


@pytest.mark.parametrize(
    ("country_code", "value"),
    [
        # EU
        ("AT", "999999999"),
        ("BG", "9999999999"),
        ("CY", "09999999L"),
        ("CZ", "999999999"),
        ("CZ", "9999999999"),
        ("DE", "99999999999"),
        ("DK", "9999999999"),
        ("EE", "99999999999"),
        ("ES", "99999999L"),
        ("ES", "L9999999L"),
        ("ES", "K9999999L"),
        ("ES", "X9999999L"),
        ("ES", "Y9999999L"),
        ("ES", "Z9999999L"),
        ("ES", "M9999999L"),
        ("FI", "999999+999L"),
        ("FI", "999999+9999"),
        ("FI", "999999-999L"),
        ("FI", "999999-9999"),
        ("FI", "999999A999L"),
        ("FI", "999999A9999"),
        ("FR", "0999999999999"),
        ("FR", "1999999999999"),
        ("FR", "2999999999999"),
        ("FR", "3999999999999"),
        ("FR", "99999999999999"),
        ("FR", "999999999"),
        ("HR", "99999999999"),
        ("HU", "9999999999"),
        ("IE", "9999999L"),
        ("IE", "9999999LL"),
        ("IT", "LLLLLL99L99L999L"),
        ("LT", "99999999999"),
        ("LU", "9999999999999"),
        ("LV", "31127509999"),
        ("LV", "3112750-9999"),
        ("LV", "329999-99999"),
        ("LV", "32999999999"),
        ("MT", "9999999M"),
        ("MT", "9999999G"),
        ("MT", "9999999A"),
        ("MT", "9999999P"),
        ("MT", "9999999L"),
        ("MT", "9999999H"),
        ("MT", "9999999B"),
        ("MT", "9999999Z"),
        ("MT", "999999999"),
        ("NL", "999999999"),
        ("PL", "9999999999"),
        ("PL", "99999999999"),
        ("PT", "999999999"),
        ("RO", "9999999999999"),
        ("SE", "999999+9999"),
        ("SE", "999999-9999"),
        ("SI", "99999999"),
        ("SK", "999999999"),
        ("SK", "9999999999"),
        # Non-EU
        ("AR", "20258743991"),
    ],
)
def test_tax_identification_numbers(mock_declaration, build_individual_seller_data, country_code, value):
    individual_seller_data = build_individual_seller_data(
        tax_identification_number__issued_by=country_code,
        tax_identification_number__value=value,
    )
    individual_seller = ReportableIndividualSeller(
        **individual_seller_data,
    )
    individual_seller.get_dpi(mock_declaration)
