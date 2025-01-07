from unittest.mock import MagicMock

import factory
import pytest

from dac7.models.enums import CountryCode
from dac7.models.enums import CurrencyCode
from dac7.models.enums import EUCountryCode


@pytest.fixture
def mock_declaration():
    return MagicMock()


class AddressData(factory.Factory):
    class Meta:
        model = dict

    country_code = factory.Faker("random_element", elements=[code.value for code in CountryCode])
    street = factory.Faker("street_address")
    post_code = factory.Faker("postcode")
    city = factory.Faker("city")


class OtherActivitiesData(factory.Factory):
    class Meta:
        model = dict

    currency_code = factory.Faker("random_element", elements=[code.value for code in CurrencyCode])
    activities_number_q1 = factory.Faker("pyint", max_value=1000)
    activities_number_q2 = factory.Faker("pyint", max_value=1000)
    activities_number_q3 = factory.Faker("pyint", max_value=1000)
    activities_number_q4 = factory.Faker("pyint", max_value=1000)
    consideration_amount_q1 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    consideration_amount_q2 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    consideration_amount_q3 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    consideration_amount_q4 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    fees_amount_q1 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    fees_amount_q2 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    fees_amount_q3 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    fees_amount_q4 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    taxes_amount_q1 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    taxes_amount_q2 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    taxes_amount_q3 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)
    taxes_amount_q4 = factory.Faker("pydecimal", positive=True, right_digits=2, max_value=100000)


class TaxIdentificationNumberData(factory.Factory):
    class Meta:
        model = dict

    issued_by = "BE"
    value = factory.Faker("numerify", text="############")


class IndividualSellerData(factory.Factory):
    class Meta:
        model = dict

    class Params:
        tax_identification_number = factory.SubFactory(TaxIdentificationNumberData)

    seller_id = "seller-id"
    name_type = "OECD202"
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    residence_country_code = factory.Faker("random_element", elements=[code.value for code in EUCountryCode])
    vat_number = None
    tax_identification_numbers = factory.LazyAttribute(
        lambda o: [o.tax_identification_number] if o.tax_identification_number else []
    )
    birth_date = factory.Faker("date")
    birth_city = factory.Faker("city")
    birth_country_code = factory.Faker("random_element", elements=[code.value for code in CountryCode])
    addresses = factory.List(
        [
            factory.SubFactory(AddressData),
        ]
    )
    sale_of_goods = factory.SubFactory(OtherActivitiesData)


@pytest.fixture
def build_individual_seller_data():
    return IndividualSellerData.create
