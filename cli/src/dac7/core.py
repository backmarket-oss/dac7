import gzip
import json

from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Optional
from typing import cast

from dac7.constants import Env
from dac7.constants import FileFormat
from dac7.encryption import EncryptionService
from dac7.encryption import KeyInfo
from dac7.models.flat import Declaration
from dac7.models.flat import PlatformOperator
from dac7.naming import build_filename

import xmlschema

# from dateutil.parser import parser

DAC7_SCHEMA = Path(__file__).parent / "schemas" / "DPIXML_v1.1-fr1.xsd"


def build_filename_from_xml_data(
    xml_data: str,
    file_format: FileFormat = FileFormat.XML,
    schema_path: Path = DAC7_SCHEMA,
) -> str:
    """
    Return the expected name of the declaration file.
    """

    schema = xmlschema.XMLSchema10(schema_path)

    schema.validate(xml_data)

    xml_declaration = cast(dict[str, dict[str, str]], schema.decode(xml_data))
    message_ref_id = xml_declaration["dpi:MessageSpec"]["dpi:MessageRefId"]
    timestamp = xml_declaration["dpi:MessageSpec"]["dpi:Timestamp"]

    expected_filename = build_filename(message_ref_id=message_ref_id, timestamp=timestamp)

    return f"{expected_filename}.{file_format.value.lower()}"


def build_json(
    env: Env,
    declaration_id: int,
    fiscal_year: int,
    platform_path: Path,
    other_platforms_path: Optional[Path] = None,
    entity_sellers_path: Optional[Path] = None,
    individual_sellers_path: Optional[Path] = None,
    timestamp: Optional[datetime] = None,
) -> str:
    """
    Build a XML or JSON declaration from simple, flat JSON files.

    The expected schemas for the JSON input files are available, see: dac7 schemas build --help.
    """

    platform_operator = PlatformOperator.model_validate_json(platform_path.read_text())

    other_platform_data = load_json(other_platforms_path, default={})
    entity_sellers_data = load_json(entity_sellers_path, default=[])
    individual_sellers_data = load_json(individual_sellers_path, default=[])

    declaration = Declaration(
        fiscal_year=fiscal_year,
        declaration_id=declaration_id,
        timestamp=timestamp or get_timestamp(),
        platform_operator=platform_operator,
        other_platform_operators=other_platform_data,
        reportable_entity_sellers=entity_sellers_data,
        reportable_individual_sellers=individual_sellers_data,
        env=env,
    )

    dpi_declaration = declaration.get_dpi()

    dpi_data = dpi_declaration.model_dump(by_alias=True, exclude_defaults=True, mode="json")
    dpi_json = json.dumps(dpi_data, indent=4, ensure_ascii=True)
    return dpi_json.strip()


def encrypt_data(
    env: Env,
    input_data: bytes,
    compression_requested: bool = False,
) -> bytes:
    """
    Encrypt a DAC7 file, optionally after GZIP compression.

    Requires GnuPG to be installed.
    """

    # Compress

    if compression_requested:
        input_data = gzip.compress(input_data)

    # Encrypt

    key_info = KeyInfo.for_env(env)
    service = EncryptionService(key_info=key_info)

    return service.encrypt_data(input_data)


def get_timestamp() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def load_json(path: Optional[Path], default: Any) -> Any:
    if path is None:
        return default
    return json.loads(path.read_text())


def json_to_xml(json_data: str, schema_path: Path) -> str:
    xml_schema = xmlschema.XMLSchema10(schema_path)

    xml_data = xmlschema.from_json(json_data, schema=xml_schema, converter=xmlschema.UnorderedConverter)
    xml_content: str = xmlschema.etree_tostring(  # type: ignore[assignment]
        xml_data,  # type: ignore[arg-type]
        namespaces={"dpi": "urn:oecd:ties:dpi", "stf": "urn:oecd:ties:dpistf"},
        encoding="unicode",
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_content}\n'
