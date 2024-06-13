from __future__ import annotations

import re

from abc import ABC
from datetime import date
from datetime import datetime
from decimal import ROUND_HALF_UP
from decimal import Decimal
from typing import Annotated
from typing import Optional
from typing import Protocol
from typing import Sequence
from typing import Union
from typing import cast
from typing import overload

from dac7.constants import Env
from dac7.models.dpi import DpiAddress
from dac7.models.dpi import DpiBase
from dac7.models.dpi import DpiBirthPlace
from dac7.models.dpi import DpiConsideration
from dac7.models.dpi import DpiCorrectableOtherReportablePlatformOperator
from dac7.models.dpi import DpiCorrectablePlatformOperator
from dac7.models.dpi import DpiCorrectableReportableSeller
from dac7.models.dpi import DpiDeclaration
from dac7.models.dpi import DpiDocSpec
from dac7.models.dpi import DpiFees
from dac7.models.dpi import DpiFinancialIdentifier
from dac7.models.dpi import DpiImmovableProperty
from dac7.models.dpi import DpiNamePerson
from dac7.models.dpi import DpiNamePersonItem
from dac7.models.dpi import DpiNumberOfActivities
from dac7.models.dpi import DpiOtherActivities
from dac7.models.dpi import DpiOtherIdentificationNumber
from dac7.models.dpi import DpiOtherPlatformOperators
from dac7.models.dpi import DpiPermanentEstablishments
from dac7.models.dpi import DpiPropertyListing
from dac7.models.dpi import DpiRelevantActivities
from dac7.models.dpi import DpiTaxes
from dac7.models.dpi import DpiTaxIdentificationNumber
from dac7.models.enums import CountryCode
from dac7.models.enums import CurrencyCode
from dac7.models.enums import DocSpecType
from dac7.models.enums import EUCountryCode
from dac7.models.enums import LegalAddressType
from dac7.models.enums import MessageSpecType
from dac7.models.enums import NamePersonType
from dac7.models.enums import Nexus
from dac7.models.enums import OtherIdentificationNumberType

import annotated_types
import pydantic

NonNegativeDecimal = Annotated[Decimal, annotated_types.Ge(0)]


class Base(pydantic.BaseModel, ABC):
    model_config = pydantic.ConfigDict(populate_by_name=True)


class TaxIdentificationNumber(Base):
    issued_by: CountryCode
    value: str

    def get_dpi(self) -> DpiTaxIdentificationNumber:
        return DpiTaxIdentificationNumber.model_validate(
            {
                "@issuedBy": self.issued_by,
                "$": self.value,
            }
        )

    @classmethod
    def get_no_tin_dpi(cls) -> DpiTaxIdentificationNumber:
        return DpiTaxIdentificationNumber.model_validate(
            {
                "@unknown": True,
                "$": "NOTIN",
            }
        )


class WithTaxIdentificationNumber(Base):
    tax_identification_numbers: list[TaxIdentificationNumber] = pydantic.Field(default_factory=list)

    def get_tins_dpi(self) -> list[DpiBase]:
        if tin_dpi_list := get_dpi_list(self.tax_identification_numbers):
            return tin_dpi_list
        return [TaxIdentificationNumber.get_no_tin_dpi()]


class MandatoryTaxIdentificationNumber(TaxIdentificationNumber):
    value: str


class OtherIdentificationNumber(Base):
    issued_by: CountryCode
    value: str
    type: OtherIdentificationNumberType

    def get_dpi(self) -> DpiOtherIdentificationNumber:
        return DpiOtherIdentificationNumber.model_validate(
            {
                "@issuedBy": self.issued_by,
                "@INType": self.type,
                "$": self.value,
            }
        )


class WithOtherIdentificationNumber(Base):
    other_identification_numbers: list[OtherIdentificationNumber] = pydantic.Field(default_factory=list)

    def get_oins_dpi(self) -> list[DpiBase]:
        return get_dpi_list(self.other_identification_numbers)


class Address(Base):
    legal_type: Optional[LegalAddressType] = None
    country_code: CountryCode
    street: str
    building_identifier: Optional[str] = None
    floor_identifier: Optional[str] = None
    post_code: str
    city: str

    def get_dpi(self) -> DpiAddress:
        return DpiAddress.model_validate(
            {
                "@legalAddressType": self.legal_type,
                "dpi:CountryCode": self.country_code,
                "dpi:AddressFix": {
                    "dpi:Street": self.street,
                    "dpi:BuildingIdentifier": self.building_identifier,
                    "dpi:FloorIdentifier": self.floor_identifier,
                    "dpi:PostCode": self.post_code,
                    "dpi:City": self.city,
                },
            }
        )


class WithDocSpec(Base):
    updated: bool = True
    version: int = 1

    def get_doc_spec_dpi(self, env: Env, ref_id_prefix: str) -> DpiDocSpec:
        indic_enum = DocSpecType.for_env(env)

        corr_doc_ref_id = None
        doc_type_indic = indic_enum.DATA_RESENT
        doc_ref_id = f"{ref_id_prefix}_v{self.version}"

        if self.updated:
            if self.version > 1:
                doc_type_indic = indic_enum.DATA_CORRECTED
                corr_doc_ref_id = f"{ref_id_prefix}_v{self.version - 1}"
            else:
                doc_type_indic = indic_enum.NEW_DATA

        return DpiDocSpec.model_validate(
            {
                "stf:DocTypeIndic": doc_type_indic,
                "stf:DocRefId": doc_ref_id,
                "stf:CorrDocRefId": corr_doc_ref_id,
            }
        )


class PlatformOperator(WithDocSpec, WithOtherIdentificationNumber):
    residence_country_code: EUCountryCode
    tax_identification_numbers: list[MandatoryTaxIdentificationNumber]
    vat_number: str
    legal_names: list[str]
    business_names: list[str]
    addresses: list[Address]
    nexus: Nexus

    @property
    def main_tax_identification_number(self) -> str:
        return self.tax_identification_numbers[0].value

    def get_platform_dpi(self, declaration: Declaration) -> DpiCorrectablePlatformOperator:
        assumed_reporting = declaration.other_platform_operators.assuming_platform_operator is not None

        return DpiCorrectablePlatformOperator.model_validate(
            {
                "dpi:ResCountryCode": self.residence_country_code,
                "dpi:TIN": get_dpi_list(self.tax_identification_numbers),
                "dpi:IN": self.get_oins_dpi(),
                "dpi:VAT": self.vat_number,
                "dpi:Name": [{"$": name} for name in self.legal_names],
                "dpi:PlatformBusinessName": self.business_names,
                "dpi:Address": get_dpi_list(self.addresses),
                "dpi:Nexus": self.nexus,
                "dpi:AssumedReporting": assumed_reporting,
                "dpi:DocSpec": self.get_doc_spec_dpi(env=declaration.env, ref_id_prefix=declaration.ref_id_prefix),
            }
        )


class FinancialIdentifier(Base):
    type: str
    account_number: Optional[str]
    account_holder_name: Optional[str] = None
    other_info: Optional[str] = None

    def get_dpi(self) -> DpiFinancialIdentifier:
        return DpiFinancialIdentifier.model_validate(
            {
                "dpi:Identifier": {
                    "@AccountNumberType": self.type,
                    "$": self.account_number,
                },
                "dpi:AccountHolderName": self.account_holder_name,
                "dpi:OtherInfo": self.other_info,
            }
        )


class WithConsideration(Base):
    currency_code: CurrencyCode
    consideration_amount_q1: Optional[NonNegativeDecimal]
    consideration_amount_q2: Optional[NonNegativeDecimal]
    consideration_amount_q3: Optional[NonNegativeDecimal]
    consideration_amount_q4: Optional[NonNegativeDecimal]

    def get_consideration_dpi(self) -> DpiConsideration:
        return DpiConsideration.model_validate(
            {
                "dpi:ConsQ1": {
                    "@currCode": self.currency_code,
                    "$": round_amount(self.consideration_amount_q1),
                },
                "dpi:ConsQ2": {
                    "@currCode": self.currency_code,
                    "$": round_amount(self.consideration_amount_q2),
                },
                "dpi:ConsQ3": {
                    "@currCode": self.currency_code,
                    "$": round_amount(self.consideration_amount_q3),
                },
                "dpi:ConsQ4": {
                    "@currCode": self.currency_code,
                    "$": round_amount(self.consideration_amount_q4),
                },
            }
        )


class WithNumberOfActivities(Base):
    activities_number_q1: Optional[int]
    activities_number_q2: Optional[int]
    activities_number_q3: Optional[int]
    activities_number_q4: Optional[int]

    def get_activities_dpi(self) -> DpiNumberOfActivities:
        return DpiNumberOfActivities.model_validate(
            {f"dpi:NumbQ{quarter}": getattr(self, f"activities_number_q{quarter}") or 0 for quarter in [1, 2, 3, 4]}
        )


class WithFees(Base):
    currency_code: CurrencyCode
    fees_amount_q1: Optional[NonNegativeDecimal]
    fees_amount_q2: Optional[NonNegativeDecimal]
    fees_amount_q3: Optional[NonNegativeDecimal]
    fees_amount_q4: Optional[NonNegativeDecimal]

    def get_fees_dpi(self) -> DpiFees:
        return DpiFees.model_validate(
            {
                f"dpi:FeesQ{quarter}": {
                    "@currCode": self.currency_code,
                    "$": round_amount(getattr(self, f"fees_amount_q{quarter}")),
                }
                for quarter in [1, 2, 3, 4]
            }
        )


class WithTaxes(Base):
    currency_code: CurrencyCode
    taxes_amount_q1: Optional[NonNegativeDecimal]
    taxes_amount_q2: Optional[NonNegativeDecimal]
    taxes_amount_q3: Optional[NonNegativeDecimal]
    taxes_amount_q4: Optional[NonNegativeDecimal]

    def get_taxes_dpi(self) -> DpiTaxes:
        return DpiTaxes.model_validate(
            {
                f"dpi:TaxesQ{quarter}": {
                    "@currCode": self.currency_code,
                    "$": round_amount(getattr(self, f"taxes_amount_q{quarter}")),
                }
                for quarter in [1, 2, 3, 4]
            }
        )


def _validate_quarter_consideration(other_activites: OtherActivities, quarter: int) -> Decimal:
    activities_number = getattr(other_activites, f"activities_number_q{quarter}") or 0
    consideration = getattr(other_activites, f"consideration_amount_q{quarter}") or 0
    if activities_number > 0 and consideration == 0:
        raise ValueError(
            f"Consideration for Q{quarter} is null while if the number of activities is positive",
        )
    return cast(NonNegativeDecimal, consideration)


class OtherActivities(WithConsideration, WithNumberOfActivities, WithFees, WithTaxes):
    @pydantic.model_validator(mode="after")
    def ensure_consideration_is_positive_when_needed(self) -> OtherActivities:
        consideration_amount_total = Decimal("0.")

        for quarter in [1, 2, 3, 4]:
            consideration_amount_total += _validate_quarter_consideration(self, quarter=quarter)

        if consideration_amount_total == 0:
            raise ValueError("Total consideration is null or negative")

        return self

    def get_dpi(self) -> DpiOtherActivities:
        return DpiOtherActivities.model_validate(
            {
                "dpi:Consideration": self.get_consideration_dpi(),
                "dpi:NumberOfActivities": self.get_activities_dpi(),
                "dpi:Fees": self.get_fees_dpi(),
                "dpi:Taxes": self.get_taxes_dpi(),
            }
        )


class WithPermanentEstablishments(Base):
    residence_country_code: Optional[EUCountryCode] = None
    establishment_country_codes: list[EUCountryCode] = pydantic.Field(default_factory=list)

    @pydantic.model_validator(mode="after")
    def remove_residence_country_code(self) -> WithPermanentEstablishments:
        self.establishment_country_codes = [
            code for code in self.establishment_country_codes if code != self.residence_country_code
        ]
        return self

    def get_establishment_country_codes_dpi(self) -> Optional[DpiPermanentEstablishments]:
        if not self.establishment_country_codes:
            return None
        return DpiPermanentEstablishments.model_validate(
            {"dpi:PermanentEstablishment": self.establishment_country_codes}
        )


class PropertyListing(OtherActivities):
    address: Address
    land_registration_number: str
    property_type: str
    rented_days: int

    def get_dpi(self) -> DpiPropertyListing:
        return DpiPropertyListing.model_validate(
            {
                "dpi:Address": self.address.get_dpi(),
                "dpi:LandRegistrationNumber": self.land_registration_number,
                "dpi:PropertyType": self.property_type,
                "dpi:RentedDays": self.rented_days,
                "dpi:Consideration": self.get_consideration_dpi(),
                "dpi:NumberOfActivities": self.get_activities_dpi(),
                "dpi:Fees": self.get_fees_dpi(),
                "dpi:Taxes": self.get_taxes_dpi(),
            }
        )


class WithImmovableProperties(Base):
    immovable_properties: list[PropertyListing] = pydantic.Field(default_factory=list)

    def get_immovable_properties_dpi(self) -> Optional[DpiImmovableProperty]:
        if not self.immovable_properties:
            return None
        return DpiImmovableProperty.model_validate(
            {
                "dpi:PropertyListing": get_dpi_list(self.immovable_properties),
            }
        )


class WithReportableActivities(WithImmovableProperties):
    immovable_properties: list[PropertyListing] = pydantic.Field(default_factory=list)
    personal_services: Optional[OtherActivities] = None
    sale_of_goods: Optional[OtherActivities] = None
    transportation_rental: Optional[OtherActivities] = None

    @pydantic.model_validator(mode="after")
    def check_relevant_activities(self) -> WithReportableActivities:
        if (
            not self.immovable_properties
            and not self.personal_services
            and not self.sale_of_goods
            and not self.transportation_rental
        ):
            raise ValueError("Need at least one relevant activity")
        return self

    def get_reportable_activities_dpi(self) -> DpiRelevantActivities:
        personal_services_dpi = get_dpi(self.personal_services)
        sale_of_goods_dpi = get_dpi(self.sale_of_goods)
        transportation_rental_dpi = get_dpi(self.transportation_rental)

        return DpiRelevantActivities.model_validate(
            {
                "dpi:ImmovableProperty": self.get_immovable_properties_dpi(),
                "dpi:PersonalServices": personal_services_dpi,
                "dpi:SaleOfGoods": sale_of_goods_dpi,
                "dpi:TransportationRental": transportation_rental_dpi,
            }
        )


class ReportableEntitySeller(
    WithTaxIdentificationNumber,
    WithOtherIdentificationNumber,
    WithReportableActivities,
    WithDocSpec,
    WithPermanentEstablishments,
):
    seller_id: str
    vat_number: Optional[str] = None
    legal_names: list[str]
    addresses: list[Address] = pydantic.Field(min_length=1)
    financial_identifiers: list[FinancialIdentifier] = pydantic.Field(default_factory=list)

    def get_dpi(self, declaration: Declaration) -> DpiCorrectableReportableSeller:
        reportable_activities_dpi = self.get_reportable_activities_dpi()

        ref_id_prefix = f"{declaration.ref_id_prefix}_{self.seller_id}"

        return DpiCorrectableReportableSeller.model_validate(
            {
                "dpi:Identity": {
                    "dpi:EntitySeller": {
                        "dpi:Standard": {
                            "dpi:EntSellerID": {
                                "dpi:ResCountryCode": self.residence_country_code,
                                "dpi:TIN": self.get_tins_dpi(),
                                "dpi:IN": self.get_oins_dpi(),
                                "dpi:VAT": self.vat_number or None,
                                "dpi:Name": [{"$": name} for name in self.legal_names],
                                "dpi:Address": get_dpi_list(self.addresses),
                            },
                            "dpi:FinancialIdentifier": get_dpi_list(self.financial_identifiers),
                            "dpi:PermanentEstablishments": self.get_establishment_country_codes_dpi(),
                        }
                    },
                },
                "dpi:RelevantActivities": reportable_activities_dpi,
                "dpi:DocSpec": self.get_doc_spec_dpi(env=declaration.env, ref_id_prefix=ref_id_prefix),
            }
        )


class WithName(Base):
    name_type: NamePersonType
    titles: list[str] = pydantic.Field(default_factory=list)
    first_name: str
    first_name_type: Optional[str] = None
    middle_names: list[DpiNamePersonItem] = pydantic.Field(default_factory=list)
    name_prefix: Optional[DpiNamePersonItem] = None
    last_name: str
    last_name_type: Optional[str] = None

    def get_name_dpi(self) -> DpiNamePerson:
        return DpiNamePerson.model_validate(
            {
                "@nameType": self.name_type,
                "dpi:Title": self.titles,
                "dpi:FirstName": {
                    "@xnlNameType": self.first_name_type,
                    "$": self.first_name,
                },
                "dpi:MiddleName": self.middle_names,
                "dpi:NamePrefix": self.name_prefix,
                "dpi:LastName": {
                    "@xnlNameType": self.last_name_type,
                    "$": self.last_name,
                },
            }
        )


class WithBirthPlace(Base):
    birth_city: str
    birth_country_code: CountryCode
    birth_city_subentity: Optional[str] = None

    def get_birth_place_dpi(self) -> DpiBirthPlace:
        return DpiBirthPlace.model_validate(
            {
                "dpi:City": self.birth_city,
                "dpi:CitySubentity": self.birth_city_subentity,
                "dpi:CountryInfo": {
                    "dpi:CountryCode": self.birth_country_code,
                },
            }
        )


class ReportableIndividualSeller(
    WithName,
    WithBirthPlace,
    WithTaxIdentificationNumber,
    WithReportableActivities,
    WithDocSpec,
):
    seller_id: str
    residence_country_code: EUCountryCode
    vat_number: Optional[str] = None
    birth_date: date
    addresses: list[Address]
    financial_identifiers: list[FinancialIdentifier] = pydantic.Field(default_factory=list)

    @pydantic.model_validator(mode="after")
    def check_tax_identification_number_or_birth_place(self) -> ReportableIndividualSeller:
        if self.birth_country_code is not None or self.tax_identification_numbers:
            return self
        raise ValueError("TIN or birth place is mandatory")

    def get_dpi(self, declaration: Declaration) -> DpiCorrectableReportableSeller:
        reportable_activities_dpi = self.get_reportable_activities_dpi()
        birth_place_dpi = self.get_birth_place_dpi()
        ref_id_prefix = f"{declaration.ref_id_prefix}_{self.seller_id}"

        return DpiCorrectableReportableSeller.model_validate(
            {
                "dpi:Identity": {
                    "dpi:IndividualSeller": {
                        "dpi:Standard": {
                            "dpi:IndSellerID": {
                                "dpi:ResCountryCode": self.residence_country_code,
                                "dpi:TIN": self.get_tins_dpi(),
                                "dpi:VAT": self.vat_number,
                                "dpi:Name": self.get_name_dpi(),
                                "dpi:Address": get_dpi_list(self.addresses),
                                "dpi:BirthInfo": {
                                    "dpi:BirthDate": self.birth_date.isoformat(),
                                    "dpi:BirthPlace": birth_place_dpi,
                                },
                            },
                            "dpi:FinancialIdentifier": get_dpi_list(self.financial_identifiers),
                        },
                    }
                },
                "dpi:RelevantActivities": reportable_activities_dpi,
                "dpi:DocSpec": self.get_doc_spec_dpi(env=declaration.env, ref_id_prefix=ref_id_prefix),
            }
        )


class OtherPlatformOperator(WithDocSpec):
    residence_country_codes: list[CountryCode]
    tax_identification_numbers: list[MandatoryTaxIdentificationNumber]
    legal_name: str
    address: Address

    def get_dpi(self, declaration: Declaration) -> DpiCorrectableOtherReportablePlatformOperator:
        main_tin = re.sub(r"[^0-9a-zA-Z+-.:=_]", "", self.tax_identification_numbers[0].value)
        ref_id_prefix = f"{declaration.ref_id_prefix}_{main_tin}"
        return DpiCorrectableOtherReportablePlatformOperator.model_validate(
            {
                "dpi:ResCountryCode": self.residence_country_codes,
                "dpi:TIN": get_dpi_list(self.tax_identification_numbers),
                "dpi:Name": {"$": self.legal_name},
                "dpi:Address": self.address.get_dpi(),
                "dpi:DocSpec": self.get_doc_spec_dpi(env=declaration.env, ref_id_prefix=ref_id_prefix),
            }
        )


class OtherPlatformOperators(Base):
    assuming_platform_operator: Optional[OtherPlatformOperator] = None
    assumed_platform_operators: list[OtherPlatformOperator] = pydantic.Field(default_factory=list)

    def get_dpi(self, declaration: Declaration) -> Optional[DpiOtherPlatformOperators]:
        if not self.assuming_platform_operator and not self.assumed_platform_operators:
            return None

        return DpiOtherPlatformOperators.model_validate(
            {
                "dpi:AssumingPlatformOperator": get_dpi(self.assuming_platform_operator, declaration=declaration),
                "dpi:AssumedPlatformOperator": get_dpi_list(self.assumed_platform_operators, declaration=declaration),
            }
        )


class WithReportableSellers(Base):
    reportable_entity_sellers: list[ReportableEntitySeller] = pydantic.Field(default_factory=list)
    reportable_individual_sellers: list[ReportableIndividualSeller] = pydantic.Field(default_factory=list)

    def get_reportable_sellers_dpi(self, declaration: Declaration) -> list[DpiBase]:
        dpi_entity_sellers = get_dpi_list(self.reportable_entity_sellers, declaration=declaration)
        dpi_individual_sellers = get_dpi_list(self.reportable_individual_sellers, declaration=declaration)
        return dpi_entity_sellers + dpi_individual_sellers


class Declaration(WithReportableSellers):
    fiscal_year: int
    declaration_id: int
    timestamp: datetime
    platform_operator: PlatformOperator
    other_platform_operators: OtherPlatformOperators
    env: Env

    @property
    def ref_id_prefix(self) -> str:
        parts = [
            "OP",
            f"{self.fiscal_year}",
            f"{self.platform_operator.main_tax_identification_number}",
        ]

        if self.env == Env.TEST:
            parts.append(f"t{self.declaration_id}")

        return "_".join(parts)

    def get_dpi(self) -> DpiDeclaration:
        message_type_indic = MessageSpecType.NEW_DECLARATION
        if self.other_platform_operators.assuming_platform_operator:
            message_type_indic = MessageSpecType.EMPTY_DECLARATION

        return DpiDeclaration.model_validate(
            {
                "@xmlns:dpi": "urn:oecd:ties:dpi",
                "@xmlns:stf": "urn:oecd:ties:dpistf",
                "@version": "1.0",
                "dpi:MessageSpec": {
                    "dpi:TransmittingCountry": "FR",
                    "dpi:ReceivingCountry": "FR",
                    "dpi:MessageType": "DPI",
                    "dpi:MessageRefId": f"{self.ref_id_prefix}_d{self.declaration_id}",
                    "dpi:MessageTypeIndic": f"{message_type_indic}",
                    "dpi:ReportingPeriod": f"{self.fiscal_year}-12-31",
                    "dpi:Timestamp": self.timestamp.isoformat()[:-3],
                },
                "dpi:DPIBody": {
                    "dpi:PlatformOperator": self.platform_operator.get_platform_dpi(declaration=self),
                    "dpi:OtherPlatformOperators": self.other_platform_operators.get_dpi(declaration=self),
                    "dpi:ReportableSeller": self.get_reportable_sellers_dpi(declaration=self),
                },
            }
        )


class WithGetDpi(Protocol):
    def get_dpi(self) -> DpiBase: ...


class WithGetDpiUsingDeclaration(Protocol):
    def get_dpi(self, declaration: Declaration) -> DpiBase: ...


@overload
def get_dpi(model: Optional[WithGetDpi]) -> Optional[DpiBase]: ...


@overload
def get_dpi(model: Optional[WithGetDpiUsingDeclaration], declaration: Declaration) -> Optional[DpiBase]: ...


def get_dpi(
    model: Union[Optional[WithGetDpi], Optional[WithGetDpiUsingDeclaration]], declaration: Optional[Declaration] = None
) -> Optional[DpiBase]:
    if model is None:
        return None
    kwargs = {"declaration": declaration} if declaration else {}
    return model.get_dpi(**kwargs)


@overload
def get_dpi_list(models: Sequence[WithGetDpi]) -> list[DpiBase]: ...


@overload
def get_dpi_list(models: Sequence[WithGetDpiUsingDeclaration], declaration: Declaration) -> list[DpiBase]: ...


def get_dpi_list(
    models: Union[Sequence[WithGetDpi], Sequence[WithGetDpiUsingDeclaration]], declaration: Optional[Declaration] = None
) -> list[DpiBase]:
    kwargs = {"declaration": declaration} if declaration else {}
    return [input_value.get_dpi(**kwargs) for input_value in models]


def round_amount(value: Optional[Decimal]) -> Decimal:
    if value is None:
        return Decimal("0.")
    return value.quantize(Decimal("1."), rounding=ROUND_HALF_UP)
