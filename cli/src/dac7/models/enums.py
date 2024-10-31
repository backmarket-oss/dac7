from __future__ import annotations

from enum import EnumMeta
from enum import StrEnum

from dac7.constants import Env


class MessageSpecType(StrEnum):
    NEW_DECLARATION = "DPI401"
    CORRECTIVE_DECLARATION = "DPI402"
    EMPTY_DECLARATION = "DPI403"


class OtherIdentificationNumberType(StrEnum):
    BUSINESS_REGISTRATION_NUMBER = "BRN"
    INDIVIDUAL_IDENTIFICATION_NUMBER = "IIN"
    LEGAL_ENTITY_IDENTIFIER = "LEI"
    ENTITY_IDENTIFICATION_NUMBER = "EIN"
    OTHER = "Other"


class NamePersonType(StrEnum):
    # ALIAS_OR_OTHER = "OECD201"
    INDIVIDUAL = "OECD202"
    ALIAS = "OECD203"
    NICKNAME = "OECD204"
    ALSO_KNOWN_AS = "OECD205"
    DOING_BUSINESS_AS = "OECD206"
    LEGAL = "OECD207"
    AT_BIRTH = "OECD208"


class LegalAddressType(StrEnum):
    RESIDENTIAL_OR_BUSINESS = "OECD301"
    RESIDENTIAL = "OECD302"
    BUSINESS = "OECD303"
    REGISTERED_OFFICE = "OECD304"
    UNSPECIFIED = "OECD305"


class Nexus(StrEnum):
    RESIDENT = "RPONEX1"
    INCORPORATED = "RPONEX2"
    MANAGED = "RPONEX3"
    ESTABLISHED = "RPONEX4"
    FACILITATOR = "RPONEX5"


class DocSpecTypeMeta(EnumMeta):
    DATA_RESENT: StrEnum
    NEW_DATA: StrEnum
    DATA_CORRECTED: StrEnum
    DATA_DELETION: StrEnum


class DocSpecType(StrEnum, metaclass=DocSpecTypeMeta):
    @classmethod
    def for_env(cls, env: Env) -> DocSpecTypeMeta:
        return ProdDocSpecType if env == Env.PROD else TestDocSpecType


class ProdDocSpecType(DocSpecType):
    DATA_RESENT = "OECD0"
    NEW_DATA = "OECD1"
    DATA_CORRECTED = "OECD2"
    DATA_DELETION = "OECD3"


class TestDocSpecType(DocSpecType):
    DATA_RESENT = "OECD10"
    NEW_DATA = "OECD11"
    DATA_CORRECTED = "OECD12"
    DATA_DELETION = "OECD13"


class EUCountryCode(StrEnum):
    AUSTRIA = "AT"
    BELGIUM = "BE"
    BULGARIA = "BG"
    CYPRUS = "CY"
    CZECHIA = "CZ"
    DENMARK = "DK"
    ESTONIA = "EE"
    FINLAND = "FI"
    FRANCE = "FR"
    GERMANY = "DE"
    GREECE = "GR"
    HUNGARY = "HU"
    CROATIA = "HR"
    IRELAND = "IE"
    ITALY = "IT"
    LATVIA = "LV"
    LITUANIA = "LT"
    LUXEMBURG = "LU"
    MALTA = "MT"
    NETHERLANDS = "NL"
    POLAND = "PL"
    PORTUGAL = "PT"
    ROMANIA = "RO"
    SLOVAKIA = "SK"
    SLOVENIA = "SI"
    SPAIN = "ES"
    SWEDEN = "SE"


class CountryCode(StrEnum):
    AFGHANISTAN = "AF"
    # ALAND_ISLANDS = "AX"
    ALBANIA = "AL"
    ALGERIA = "DZ"
    AMERICAN_SAMOA = "AS"
    ANDORRA = "AD"
    ANGOLA = "AO"
    ANGUILLA = "AI"
    ANTARCTICA = "AQ"
    ANTIGUA_AND_BARBUDA = "AG"
    ARGENTINA = "AR"
    ARMENIA = "AM"
    ARUBA = "AW"
    AUSTRALIA = "AU"
    AUSTRIA = "AT"
    AZERBAIJAN = "AZ"
    BAHAMAS = "BS"
    BAHRAIN = "BH"
    BANGLADESH = "BD"
    BARBADOS = "BB"
    BELARUS = "BY"
    BELGIUM = "BE"
    BELIZE = "BZ"
    BENIN = "BJ"
    BERMUDA = "BM"
    BHUTAN = "BT"
    BOLIVIA = "BO"
    BONAIRE = "BQ"
    BOSNIA_AND_HERZEGOVINA = "BA"
    BOTSWANA = "BW"
    BOUVET_ISLAND = "BV"
    BRAZIL = "BR"
    BRITISH_INDIAN_OCEAN_TERRITORY = "IO"
    BRUNEI_DARUSSALAM = "BN"
    BULGARIA = "BG"
    BURKINA_FASO = "BF"
    BURUNDI = "BI"
    CAMBODIA = "KH"
    CAMEROON = "CM"
    CANADA = "CA"
    CABO_VERDE = "CV"
    CAYMAN_ISLANDS = "KY"
    CENTRAL_AFRICAN_REPUBLIC = "CF"
    CHAD = "TD"
    CHILE = "CL"
    CHINA = "CN"
    CHRISTMAS_ISLAND = "CX"
    COCOS_ISLANDS = "CC"
    COLOMBIA = "CO"
    COMOROS = "KM"
    CONGO_BRAZZAVILLE = "CG"
    CONGO_KINSHASA = "CD"
    COOK_ISLANDS = "CK"
    COSTA_RICA = "CR"
    IVORY_COAST = "CI"
    CROATIA = "HR"
    CUBA = "CU"
    CURACAO = "CW"
    CYPRUS = "CY"
    CZECHIA = "CZ"
    DENMARK = "DK"
    DJIBOUTI = "DJ"
    DOMINICA = "DM"
    DOMINICAN_REPUBLIC = "DO"
    ECUADOR = "EC"
    EGYPT = "EG"
    EL_SALVADOR = "SV"
    EQUATORIAL_GUINEA = "GQ"
    ERITREA = "ER"
    ESTONIA = "EE"
    ETHIOPIA = "ET"
    FALKLAND_ISLANDS = "FK"
    FAROE_ISLANDS = "FO"
    FIJI = "FJ"
    FINLAND = "FI"
    FRANCE = "FR"
    FRENCH_GUIANA = "GF"
    FRENCH_POLYNESIA = "PF"
    FRENCH_SOUTHERN_TERRITORIES = "TF"
    GABON = "GA"
    GAMBIA = "GM"
    GEORGIA = "GE"
    GERMANY = "DE"
    GHANA = "GH"
    GIBRALTAR = "GI"
    GREECE = "GR"
    GREENLAND = "GL"
    GRENADA = "GD"
    # GUADELOUPE = "GP"
    GUAM = "GU"
    GUATEMALA = "GT"
    GUERNSEY = "GG"
    GUINEA = "GN"
    GUINEA_BISSAU = "GW"
    # GUYANA = "GY"
    HAITI = "HT"
    HEARD_AND_MCDONALD_ISLANDS = "HM"
    VATICAN = "VA"
    HONDURAS = "HN"
    HONG_KONG = "HK"
    HUNGARY = "HU"
    ICELAND = "IS"
    INDIA = "IN"
    INDONESIA = "ID"
    IRAN = "IR"
    IRAQ = "IQ"
    IRELAND = "IE"
    ISLE_OF_MAN = "IM"
    ISRAEL = "IL"
    ITALY = "IT"
    JAMAICA = "JM"
    JAPAN = "JP"
    JERSEY = "JE"
    JORDAN = "JO"
    KAZAKHSTAN = "KZ"
    KENYA = "KE"
    KIRIBATI = "KI"
    NORTH_KOREA = "KP"
    SOUTH_KOREA = "KR"
    KUWAIT = "KW"
    KYRGYZSTAN = "KG"
    LAOS = "LA"
    LATVIA = "LV"
    LEBANON = "LB"
    LESOTHO = "LS"
    LIBERIA = "LR"
    LIBYA = "LY"
    LIECHTENSTEIN = "LI"
    LITHUANIA = "LT"
    LUXEMBOURG = "LU"
    MACAO = "MO"
    NORTH_MACEDONIA = "MK"
    MADAGASCAR = "MG"
    MALAWI = "MW"
    MALAYSIA = "MY"
    MALDIVES = "MV"
    MALI = "ML"
    MALTA = "MT"
    MARSHALL_ISLANDS = "MH"
    # MARTINIQUE = "MQ"
    MAURITANIA = "MR"
    MAURITIUS = "MU"
    # MAYOTTE = "YT"
    MEXICO = "MX"
    MICRONESIA = "FM"
    MOLDOVA = "MD"
    MONACO = "MC"
    MONGOLIA = "MN"
    MONTENEGRO = "ME"
    MONTSERRAT = "MS"
    MOROCCO = "MA"
    MOZAMBIQUE = "MZ"
    MYANMAR = "MM"
    NAMIBIA = "NA"
    NAURU = "NR"
    NEPAL = "NP"
    NETHERLANDS = "NL"
    NEW_CALEDONIA = "NC"
    NEW_ZEALAND = "NZ"
    NICARAGUA = "NI"
    NIGER = "NE"
    NIGERIA = "NG"
    NIUE = "NU"
    NORFOLK_ISLAND = "NF"
    NORTHERN_MARIANA_ISLANDS = "MP"
    NORWAY = "NO"
    OMAN = "OM"
    PAKISTAN = "PK"
    PALAU = "PW"
    PALESTINE = "PS"
    PANAMA = "PA"
    PAPUA_NEW_GUINEA = "PG"
    PARAGUAY = "PY"
    PERU = "PE"
    PHILIPPINES = "PH"
    PITCAIRN = "PN"
    POLAND = "PL"
    PORTUGAL = "PT"
    PUERTO_RICO = "PR"
    QATAR = "QA"
    # REUNION = "RE"
    ROMANIA = "RO"
    RUSSIA = "RU"
    RWANDA = "RW"
    SAINT_BARTHELEMY = "BL"
    SAINT_HELENA_ASCENSION_AND_TRISTAN_DA_CUNHA = "SH"
    SAINT_KITTS_AND_NEVIS = "KN"
    SAINT_LUCIA = "LC"
    SAINT_MARTIN = "MF"
    SAINT_PIERRE_AND_MIQUELON = "PM"
    SAINT_VINCENT_AND_THE_GRENADINES = "VC"
    SAMOA = "WS"
    SAN_MARINO = "SM"
    SAO_TOME_AND_PRINCIPE = "ST"
    SAUDI_ARABIA = "SA"
    SENEGAL = "SN"
    SERBIA = "RS"
    SEYCHELLES = "SC"
    SIERRA_LEONE = "SL"
    SINGAPORE = "SG"
    SINT_MAARTEN = "SX"
    SLOVAKIA = "SK"
    SLOVENIA = "SI"
    SOLOMON_ISLANDS = "SB"
    SOMALIA = "SO"
    SOUTH_AFRICA = "ZA"
    SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS = "GS"
    SOUTH_SUDAN = "SS"
    SPAIN = "ES"
    SRI_LANKA = "LK"
    SUDAN = "SD"
    SURINAME = "SR"
    SVALBARD_AND_JAN_MAYEN = "SJ"
    ESWATINI = "SZ"
    SWEDEN = "SE"
    SWITZERLAND = "CH"
    SYRIA = "SY"
    TAIWAN = "TW"
    TAJIKISTAN = "TJ"
    TANZANIA = "TZ"
    THAILAND = "TH"
    TIMOR_LESTE = "TL"
    TOGO = "TG"
    TOKELAU = "TK"
    TONGA = "TO"
    TRINIDAD_AND_TOBAGO = "TT"
    TUNISIA = "TN"
    TURKEY = "TR"
    TURKMENISTAN = "TM"
    TURKS_AND_CAICOS_ISLANDS = "TC"
    TUVALU = "TV"
    UGANDA = "UG"
    UKRAINE = "UA"
    UNITED_ARAB_EMIRATES = "AE"
    UNITED_KINGDOM = "GB"
    UNITED_STATES = "US"
    UNITED_STATES_MINOR_OUTLYING_ISLANDS = "UM"
    URUGUAY = "UY"
    UZBEKISTAN = "UZ"
    VANUATU = "VU"
    VENEZUELA = "VE"
    VIET_NAM = "VN"
    BRITISH_VIRGIN_ISLANDS = "VG"
    US_VIRGIN_ISLANDS = "VI"
    WALLIS_AND_FUTUNA = "WF"
    WESTERN_SAHARA = "EH"
    YEMEN = "YE"
    ZAMBIA = "ZM"
    ZIMBABWE = "ZW"
    KOSOVO = "XK"
    # STATELESS = "X5"
    # OTHER_COUNTRY = "XX"


class CurrencyCode(StrEnum):
    UAE_DIRHAM = "AED"
    AFGHANI = "AFN"
    LEK = "ALL"
    ARMENIAN_DRAM = "AMD"
    NETHERLANDS_ANTILLEAN_GUILDER = "ANG"
    KWANZA = "AOA"
    ARGENTINE_PESO = "ARS"
    AUSTRALIAN_DOLLAR = "AUD"
    ARUBAN_FLORIN = "AWG"
    AZERBAIJAN_MANAT = "AZN"
    CONVERTIBLE_MARK = "BAM"
    BARBADOS_DOLLAR = "BBD"
    TAKA = "BDT"
    BULGARIAN_LEV = "BGN"
    BAHRAINI_DINAR = "BHD"
    BURUNDI_FRANC = "BIF"
    BERMUDIAN_DOLLAR = "BMD"
    BRUNEI_DOLLAR = "BND"
    BOLIVIANO = "BOB"
    MVDOL = "BOV"
    BRAZILIAN_REAL = "BRL"
    BAHAMIAN_DOLLAR = "BSD"
    NGULTRUM = "BTN"
    PULA = "BWP"
    BELARUSIAN_RUBLE = "BYN"
    BELARUSSIAN_RUBLE = "BYR"
    BELIZE_DOLLAR = "BZD"
    CANADIAN_DOLLAR = "CAD"
    CONGOLESE_FRANC = "CDF"
    WIR_EURO = "CHE"
    SWISS_FRANC = "CHF"
    WIR_FRANC = "CHW"
    UNIDAD_DE_FOMENTO = "CLF"
    CHILEAN_PESO = "CLP"
    YUAN_RENMINBI = "CNY"
    COLOMBIAN_PESO = "COP"
    UNIDAD_DE_VALOR_REAL = "COU"
    COSTA_RICAN_COLON = "CRC"
    PESO_CONVERTIBLE = "CUC"
    CUBAN_PESO = "CUP"
    CABO_VERDE_ESCUDO = "CVE"
    CZECH_KORUNA = "CZK"
    DJIBOUTI_FRANC = "DJF"
    DANISH_KRONE = "DKK"
    DOMINICAN_PESO = "DOP"
    ALGERIAN_DINAR = "DZD"
    EGYPTIAN_POUND = "EGP"
    NAKFA = "ERN"
    ETHIOPIAN_BIRR = "ETB"
    EURO = "EUR"
    FIJI_DOLLAR = "FJD"
    FALKLAND_ISLANDS_POUND = "FKP"
    POUND_STERLING = "GBP"
    LARI = "GEL"
    GHANA_CEDI = "GHS"
    GIBRALTAR_POUND = "GIP"
    DALASI = "GMD"
    GUINEAN_FRANC = "GNF"
    QUETZAL = "GTQ"
    GUYANA_DOLLAR = "GYD"
    HONG_KONG_DOLLAR = "HKD"
    LEMPIRA = "HNL"
    KUNA = "HRK"
    GOURDE = "HTG"
    FORINT = "HUF"
    RUPIAH = "IDR"
    NEW_ISRAELI_SHEQEL = "ILS"
    INDIAN_RUPEE = "INR"
    IRAQI_DINAR = "IQD"
    IRANIAN_RIAL = "IRR"
    ICELAND_KRONA = "ISK"
    JAMAICAN_DOLLAR = "JMD"
    JORDANIAN_DINAR = "JOD"
    YEN = "JPY"
    KENYAN_SHILLING = "KES"
    SOM = "KGS"
    RIEL = "KHR"
    COMORIAN_FRANC_ = "KMF"
    NORTH_KOREAN_WON = "KPW"
    WON = "KRW"
    KUWAITI_DINAR = "KWD"
    CAYMAN_ISLANDS_DOLLAR = "KYD"
    TENGE = "KZT"
    LAO_KIP = "LAK"
    LEBANESE_POUND = "LBP"
    SRI_LANKA_RUPEE = "LKR"
    LIBERIAN_DOLLAR = "LRD"
    LOTI = "LSL"
    LITHUANIAN_LITAS = "LTL"
    LATVIAN_LATS = "LVL"
    LIBYAN_DINAR = "LYD"
    MOROCCAN_DIRHAM = "MAD"
    MOLDOVAN_LEU = "MDL"
    MALAGASY_ARIARY = "MGA"
    DENAR = "MKD"
    KYAT = "MMK"
    TUGRIK = "MNT"
    PATACA = "MOP"
    HISTORIC_OUGUIYA = "MRO"
    OUGUIYA = "MRU"
    MAURITIUS_RUPEE = "MUR"
    RUFIYAA = "MVR"
    MALAWI_KWACHA = "MWK"
    MEXICAN_PESO = "MXN"
    MEXICAN_UNIDAD_DE_INVERSION = "MXV"
    MALAYSIAN_RINGGIT = "MYR"
    MOZAMBIQUE_METICAL = "MZN"
    NAMIBIA_DOLLAR = "NAD"
    NAIRA = "NGN"
    CORDOBA_ORO = "NIO"
    NORWEGIAN_KRONE = "NOK"
    NEPALESE_RUPEE = "NPR"
    NEW_ZEALAND_DOLLAR = "NZD"
    RIAL_OMANI = "OMR"
    BALBOA = "PAB"
    SOL = "PEN"
    KINA = "PGK"
    PHILIPPINE_PESO = "PHP"
    PAKISTAN_RUPEE = "PKR"
    ZLOTY = "PLN"
    GUARANI = "PYG"
    QATARI_RIAL = "QAR"
    ROMANIAN_LEU = "RON"
    SERBIAN_DINAR = "RSD"
    RUSSIAN_RUBLE = "RUB"
    RWANDA_FRANC = "RWF"
    SAUDI_RIYAL = "SAR"
    SOLOMON_ISLANDS_DOLLAR = "SBD"
    SEYCHELLES_RUPEE = "SCR"
    SUDANESE_POUND = "SDG"
    SWEDISH_KRONA = "SEK"
    SINGAPORE_DOLLAR = "SGD"
    SAINT_HELENA_POUND = "SHP"
    LEONE = "SLL"
    SOMALI_SHILLING = "SOS"
    SURINAM_DOLLAR = "SRD"
    SOUTH_SUDANESE_POUND = "SSP"
    HISTORIC_DOBRA = "STD"
    DOBRA = "STN"
    EL_SALVADOR_COLON = "SVC"
    SYRIAN_POUND = "SYP"
    LILANGENI = "SZL"
    BAHT = "THB"
    SOMONI = "TJS"
    TURKMENISTAN_NEW_MANAT = "TMT"
    TUNISIAN_DINAR = "TND"
    PAANGA = "TOP"
    TURKISH_LIRA = "TRY"
    TRINIDAD_AND_TOBAGO_DOLLAR = "TTD"
    NEW_TAIWAN_DOLLAR = "TWD"
    TANZANIAN_SHILLING = "TZS"
    HRYVNIA = "UAH"
    UGANDA_SHILLING = "UGX"
    US_DOLLAR = "USD"
    US_DOLLAR_NEXT_DAY = "USN"
    US_DOLLAR_SAME_DAY = "USS"
    URUGUAY_PESO_EN_UNIDADES_INDEXADAS = "UYI"
    PESO_URUGUAYO = "UYU"
    UNIDAD_PREVISIONAL = "UYW"
    UZBEKISTAN_SUM = "UZS"
    BOLIVAR = "VEF"
    BOLIVAR_SOBERANO = "VES"
    DONG = "VND"
    VATU = "VUV"
    TALA = "WST"
    CFA_FRANC = "XAF"
    SILVER = "XAG"
    GOLD = "XAU"
    EAST_CARIBBEAN_DOLLAR = "XCD"
    SPECIAL_DRAWING_RIGHT = "XDR"
    CFA_FRANC_BCEAO = "XOF"
    PALLADIUM = "XPD"
    CFP_FRANC = "XPF"
    PLATINUM = "XPT"
    SUCRE = "XSU"
    NO_CURRENCY = "XXX"
    YEMENI_RIAL = "YER"
    RAND = "ZAR"
    ZAMBIAN_KWACHA = "ZMW"
    ZIMBABWE_DOLLAR = "ZWL"