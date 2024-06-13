from __future__ import annotations

from datetime import date
from typing import Literal
from typing import Optional
from typing import Union

from dac7.models.enums import CountryCode
from dac7.models.enums import CurrencyCode
from dac7.models.enums import EUCountryCode
from dac7.models.enums import LegalAddressType
from dac7.models.enums import NamePersonType
from dac7.models.enums import Nexus
from dac7.models.enums import OtherIdentificationNumberType
from dac7.models.enums import ProdDocSpecType
from dac7.models.enums import TestDocSpecType

import pydantic


class DpiBase(pydantic.BaseModel):
    pass


class DpiNamePersonItem(DpiBase):
    type: Optional[str] = pydantic.Field(default=None, min_length=1, max_length=200, alias="@xnlNameType")
    value: str = pydantic.Field(min_length=1, max_length=200, alias="$")


class DpiNamePerson(DpiBase):
    type: NamePersonType = pydantic.Field(alias="@nameType")
    titles: list[str] = pydantic.Field(default_factory=list, alias="dpi:Title")
    first_name: DpiNamePersonItem = pydantic.Field(alias="dpi:FirstName")
    middle_names: list[DpiNamePersonItem] = pydantic.Field(default_factory=list, alias="dpi:MiddleName")
    name_prefix: Optional[DpiNamePersonItem] = pydantic.Field(default=None, alias="dpi:NamePrefix")
    last_name: DpiNamePersonItem = pydantic.Field(alias="dpi:LastName")


class DpiTaxIdentificationNumber(DpiBase):
    unknown: bool = pydantic.Field(default=False, alias="@unknown")
    issued_by: Optional[CountryCode] = pydantic.Field(default=None, alias="@issuedBy")
    value: str = pydantic.Field(min_length=1, max_length=200, alias="$")


class DpiAddressFix(DpiBase):
    street: str = pydantic.Field(min_length=1, max_length=200, alias="dpi:Street")
    building_identifier: Optional[str] = pydantic.Field(
        default=None,
        min_length=1,
        max_length=200,
        alias="dpi:BuildingIdentifier",
    )
    floor_identifier: Optional[str] = pydantic.Field(
        default=None,
        min_length=1,
        max_length=200,
        alias="dpi:FloorIdentifier",
    )
    post_code: str = pydantic.Field(min_length=1, max_length=200, alias="dpi:PostCode")
    city: str = pydantic.Field(pattern=r".*(\S).*", min_length=1, max_length=200, alias="dpi:City")


class DpiAddress(DpiBase):
    legal_type: Optional[LegalAddressType] = pydantic.Field(default=None, alias="@legalAddressType")
    country_code: CountryCode = pydantic.Field(alias="dpi:CountryCode")
    address_fix: DpiAddressFix = pydantic.Field(alias="dpi:AddressFix")


class DpiBirthPlaceCountryInfo(DpiBase):
    country_code: CountryCode = pydantic.Field(alias="dpi:CountryCode")


class DpiBirthPlace(DpiBase):
    city: str = pydantic.Field(min_length=1, max_length=200, alias="dpi:City")
    city_subentity: Optional[str] = pydantic.Field(
        default=None,
        min_length=1,
        max_length=200,
        alias="dpi:CitySubentity",
    )
    country_info: DpiBirthPlaceCountryInfo = pydantic.Field(alias="dpi:CountryInfo")


class DpiBirthInfo(DpiBase):
    birth_date: date = pydantic.Field(alias="dpi:BirthDate")
    birth_place: Optional[DpiBirthPlace] = pydantic.Field(default=None, alias="dpi:BirthPlace")


class DpiPersonParty(DpiBase):
    residence_country_code: EUCountryCode = pydantic.Field(alias="dpi:ResCountryCode")
    tax_identification_numbers: list[DpiTaxIdentificationNumber] = pydantic.Field(alias="dpi:TIN", min_length=1)
    vat_number: Optional[str] = pydantic.Field(default=None, min_length=1, max_length=200, alias="dpi:VAT")
    name: DpiNamePerson = pydantic.Field(alias="dpi:Name")
    addresses: list[DpiAddress] = pydantic.Field(alias="dpi:Address", min_length=1)
    birth_info: DpiBirthInfo = pydantic.Field(alias="dpi:BirthInfo")

    @pydantic.field_validator("tax_identification_numbers")
    @classmethod
    def check_tax_identification_numbers(
        cls, tax_identification_numbers: list[DpiTaxIdentificationNumber], info: pydantic.ValidationInfo
    ) -> list[DpiTaxIdentificationNumber]:
        unknown_tins = [tin for tin in tax_identification_numbers if tin.unknown]
        if len(tax_identification_numbers) > len(unknown_tins) > 0:
            raise ValueError("Unknown TIN mixed with known TINs")
        return tax_identification_numbers

    @pydantic.model_validator(mode="after")
    def check_tax_identification_numbers_and_birth_place(self) -> DpiPersonParty:
        if self.birth_info.birth_place is not None:
            return self
        if self.tax_identification_numbers[0].unknown:
            raise ValueError("TIN or birth place is mandatory")
        return self


class DpiMonetaryAmount(DpiBase):
    currency_code: CurrencyCode = pydantic.Field(alias="@currCode")
    amount: pydantic.NonNegativeInt = pydantic.Field(alias="$")


class DpiNameOrganization(DpiBase):
    type: Optional[NamePersonType] = pydantic.Field(default=None, alias="@nameType")
    value: str = pydantic.Field(pattern=r".*(\S).*", min_length=1, max_length=200, alias="$")


class DpiMessageSpec(DpiBase):
    transmitting_country: Literal["FR"] = pydantic.Field(alias="dpi:TransmittingCountry")
    receiving_country: Literal["FR"] = pydantic.Field(alias="dpi:ReceivingCountry")
    message_type: Literal["DPI"] = pydantic.Field(alias="dpi:MessageType")
    message_ref_id: str = pydantic.Field(
        pattern=r"^OP_(202[3-9]|20[3-9]\d)_(\d{9})_.+$",
        min_length=1,
        max_length=88,
        alias="dpi:MessageRefId",
    )
    message_type_indic: str = pydantic.Field(alias="dpi:MessageTypeIndic")
    reporting_period: str = pydantic.Field(alias="dpi:ReportingPeriod")
    timestamp: str = pydantic.Field(alias="dpi:Timestamp")


class DpiOtherIdentificationNumber(DpiBase):
    issued_by: CountryCode = pydantic.Field(alias="@issuedBy")
    type: OtherIdentificationNumberType = pydantic.Field(alias="@INType")
    value: str = pydantic.Field(pattern=r".*(\S).*", min_length=1, max_length=200, alias="$")


class DpiOrganizationParty(DpiBase):
    residence_country_code: EUCountryCode = pydantic.Field(alias="dpi:ResCountryCode")
    tax_identification_numbers: list[DpiTaxIdentificationNumber] = pydantic.Field(alias="dpi:TIN")
    other_identification_numbers: list[DpiOtherIdentificationNumber] = pydantic.Field(
        default_factory=list, alias="dpi:IN"
    )
    vat_number: Optional[str] = pydantic.Field(default=None, min_length=1, max_length=200, alias="dpi:VAT")
    legal_names: list[DpiNameOrganization] = pydantic.Field(alias="dpi:Name")
    addresses: list[DpiAddress] = pydantic.Field(alias="dpi:Address", min_length=1)


class DpiDocSpec(DpiBase):
    doc_type_indic: Union[ProdDocSpecType, TestDocSpecType] = pydantic.Field(alias="stf:DocTypeIndic")
    doc_ref_id: str = pydantic.Field(
        pattern=r"[\da-zA-Z+-.:=_]{1,200}",
        min_length=1,
        max_length=200,
        alias="stf:DocRefId",
    )
    corr_doc_ref_id: Optional[str] = pydantic.Field(
        default=None,
        pattern=r"[\da-zA-Z+-.:=_]{1,200}",
        min_length=1,
        max_length=200,
        alias="stf:CorrDocRefId",
    )


class DpiCorrectablePlatformOperator(DpiOrganizationParty):
    business_names: list[str] = pydantic.Field(min_length=1, max_length=200, alias="dpi:PlatformBusinessName")
    nexus: Nexus = pydantic.Field(alias="dpi:Nexus")
    assumed_reporting: bool = pydantic.Field(alias="dpi:AssumedReporting")
    doc_spec: DpiDocSpec = pydantic.Field(alias="dpi:DocSpec")


class DpiIdentifier(DpiBase):
    account_number_type: Optional[str] = pydantic.Field(
        default=None,
        min_length=1,
        max_length=200,
        alias="@AccountNumberType",
    )
    value: str = pydantic.Field(min_length=1, max_length=200, alias="$")


class DpiFinancialIdentifier(DpiBase):
    identifier: DpiIdentifier = pydantic.Field(alias="dpi:Identifier")
    account_holder_name: Optional[str] = pydantic.Field(
        default=None,
        min_length=1,
        max_length=200,
        alias="dpi:AccountHolderName",
    )
    other_info: Optional[str] = pydantic.Field(default=None, min_length=1, max_length=400, alias="dpi:OtherInfo")


class DpiConsideration(DpiBase):
    consideration_q1: DpiMonetaryAmount = pydantic.Field(alias="dpi:ConsQ1")
    consideration_q2: DpiMonetaryAmount = pydantic.Field(alias="dpi:ConsQ2")
    consideration_q3: DpiMonetaryAmount = pydantic.Field(alias="dpi:ConsQ3")
    consideration_q4: DpiMonetaryAmount = pydantic.Field(alias="dpi:ConsQ4")

    @pydantic.model_validator(mode="after")
    def check_consideration_is_positive(self) -> DpiConsideration:
        total = (
            self.consideration_q1.amount
            + self.consideration_q2.amount
            + self.consideration_q3.amount
            + self.consideration_q4.amount
        )
        if total == 0:
            raise ValueError("Total consideration is null")
        return self


class DpiNumberOfActivities(DpiBase):
    activities_number_q1: pydantic.NonNegativeInt = pydantic.Field(alias="dpi:NumbQ1")
    activities_number_q2: pydantic.NonNegativeInt = pydantic.Field(alias="dpi:NumbQ2")
    activities_number_q3: pydantic.NonNegativeInt = pydantic.Field(alias="dpi:NumbQ3")
    activities_number_q4: pydantic.NonNegativeInt = pydantic.Field(alias="dpi:NumbQ4")


class DpiFees(DpiBase):
    fees_q1: DpiMonetaryAmount = pydantic.Field(alias="dpi:FeesQ1")
    fees_q2: DpiMonetaryAmount = pydantic.Field(alias="dpi:FeesQ2")
    fees_q3: DpiMonetaryAmount = pydantic.Field(alias="dpi:FeesQ3")
    fees_q4: DpiMonetaryAmount = pydantic.Field(alias="dpi:FeesQ4")


class DpiTaxes(DpiBase):
    taxes_q1: DpiMonetaryAmount = pydantic.Field(alias="dpi:TaxesQ1")
    taxes_q2: DpiMonetaryAmount = pydantic.Field(alias="dpi:TaxesQ2")
    taxes_q3: DpiMonetaryAmount = pydantic.Field(alias="dpi:TaxesQ3")
    taxes_q4: DpiMonetaryAmount = pydantic.Field(alias="dpi:TaxesQ4")


class DpiOtherActivities(DpiBase):
    consideration: DpiConsideration = pydantic.Field(alias="dpi:Consideration")
    number_of_activities: DpiNumberOfActivities = pydantic.Field(alias="dpi:NumberOfActivities")
    fees: DpiFees = pydantic.Field(alias="dpi:Fees")
    taxes: DpiTaxes = pydantic.Field(alias="dpi:Taxes")


class DpiPropertyListing(DpiOtherActivities):
    address: DpiAddress = pydantic.Field(alias="dpi:Address")
    land_registration_number: str = pydantic.Field(alias="dpi:LandRegistrationNumber")
    property_type: str = pydantic.Field(alias="dpi:PropertyType")
    rented_days: int = pydantic.Field(alias="dpi:RentedDays")


class DpiPermanentEstablishments(DpiBase):
    permanent_establishments: list[EUCountryCode] = pydantic.Field(alias="dpi:PermanentEstablishment")


class DpiStandardEntitySeller(DpiBase):
    entity_seller_details: DpiOrganizationParty = pydantic.Field(alias="dpi:EntSellerID")
    financial_identifiers: list[DpiFinancialIdentifier] = pydantic.Field(
        default_factory=list,
        alias="dpi:FinancialIdentifier",
    )
    permanent_establishments: Optional[DpiPermanentEstablishments] = pydantic.Field(
        default=None,
        alias="dpi:PermanentEstablishments",
    )


class DpiStandardIndividualSeller(DpiBase):
    individual_seller_details: DpiPersonParty = pydantic.Field(alias="dpi:IndSellerID")
    financial_identifiers: list[DpiFinancialIdentifier] = pydantic.Field(
        default_factory=list,
        alias="dpi:FinancialIdentifier",
    )


class DpiEntitySeller(DpiBase):
    standard: DpiStandardEntitySeller = pydantic.Field(alias="dpi:Standard")


class DpiIndividualSeller(DpiBase):
    standard: DpiStandardIndividualSeller = pydantic.Field(alias="dpi:Standard")


class DpiIdentity(DpiBase):
    entity_seller: Optional[DpiEntitySeller] = pydantic.Field(default=None, alias="dpi:EntitySeller")
    individual_seller: Optional[DpiIndividualSeller] = pydantic.Field(default=None, alias="dpi:IndividualSeller")


class DpiImmovableProperty(DpiBase):
    property_listings: list[DpiPropertyListing] = pydantic.Field(alias="dpi:PropertyListing")


class DpiRelevantActivities(DpiBase):
    immovable_property: Optional[DpiImmovableProperty] = pydantic.Field(default=None, alias="dpi:ImmovableProperty")
    personal_services: Optional[DpiOtherActivities] = pydantic.Field(default=None, alias="dpi:PersonalServices")
    sale_of_goods: Optional[DpiOtherActivities] = pydantic.Field(default=None, alias="dpi:SaleOfGoods")
    transportation_rental: Optional[DpiOtherActivities] = pydantic.Field(default=None, alias="dpi:TransportationRental")

    @pydantic.model_validator(mode="after")
    def check_activities(self) -> DpiRelevantActivities:
        for activity in ["immovable_property", "personal_services", "sale_of_goods", "transportation_rental"]:
            if getattr(self, activity) is not None:
                return self
        raise ValueError("No activity")


class DpiReportableSeller(DpiBase):
    identity: DpiIdentity = pydantic.Field(alias="dpi:Identity")
    relevant_activities: DpiRelevantActivities = pydantic.Field(alias="dpi:RelevantActivities")


class DpiCorrectableReportableSeller(DpiReportableSeller):
    doc_spec: DpiDocSpec = pydantic.Field(alias="dpi:DocSpec")


class DpiOtherReportablePlatformOperator(DpiBase):
    residence_country_code: list[CountryCode] = pydantic.Field(alias="dpi:ResCountryCode")
    tax_identification_numbers: list[DpiTaxIdentificationNumber] = pydantic.Field(alias="dpi:TIN")
    legal_name: DpiNameOrganization = pydantic.Field(alias="dpi:Name")
    address: DpiAddress = pydantic.Field(alias="dpi:Address")


class DpiCorrectableOtherReportablePlatformOperator(DpiOtherReportablePlatformOperator):
    doc_spec: DpiDocSpec = pydantic.Field(alias="dpi:DocSpec")


class DpiOtherPlatformOperators(DpiBase):
    assuming_platform_operator: Optional[DpiCorrectableOtherReportablePlatformOperator] = pydantic.Field(
        default=None,
        alias="dpi:AssumingPlatformOperator",
    )
    assumed_platform_operators: list[DpiCorrectableOtherReportablePlatformOperator] = pydantic.Field(
        default_factory=list,
        alias="dpi:AssumedPlatformOperator",
    )


class DpiBody(DpiBase):
    platform_operator: DpiCorrectablePlatformOperator = pydantic.Field(alias="dpi:PlatformOperator")
    other_platform_operators: Optional[DpiOtherPlatformOperators] = pydantic.Field(
        default=None,
        alias="dpi:OtherPlatformOperators",
    )
    reportable_sellers: list[DpiCorrectableReportableSeller] = pydantic.Field(
        default_factory=list,
        alias="dpi:ReportableSeller",
    )


class DpiDeclaration(DpiBase):
    dpi_namespace: Literal["urn:oecd:ties:dpi"] = pydantic.Field(alias="@xmlns:dpi")
    stf_namespace: Literal["urn:oecd:ties:dpistf"] = pydantic.Field(alias="@xmlns:stf")
    schema_version: Literal["1.0"] = pydantic.Field(alias="@version")
    message_spec: DpiMessageSpec = pydantic.Field(alias="dpi:MessageSpec")
    body: DpiBody = pydantic.Field(alias="dpi:DPIBody")
