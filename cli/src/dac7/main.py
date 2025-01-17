import json

from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Annotated
from typing import Optional
from typing import cast

from dac7.constants import Env
from dac7.constants import FileFormat
from dac7.core import DAC7_SCHEMA
from dac7.core import build_filename_from_xml_data
from dac7.core import build_json
from dac7.core import encrypt_data
from dac7.core import json_to_xml
from dac7.models.dpi import DpiDeclaration
from dac7.models.flat import OtherPlatformOperators
from dac7.models.flat import PlatformOperator
from dac7.models.flat import ReportableEntitySeller
from dac7.models.flat import ReportableIndividualSeller
from dac7.naming import validate_filename

import typer
import xmlschema

# from dateutil.parser import parser

app = typer.Typer()


@app.command()
def validate(
    xml_path: Annotated[
        Path,
        typer.Argument(
            metavar="XML_FILE",
            allow_dash=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default=False,
        ),
    ],
    schema_path: Annotated[
        Path,
        typer.Option(
            "--xsd",
            "-x",
            metavar="SCHEMA",
            envvar="DAC7_SCHEMA",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="XSD schema to use.",
            show_default="built-in schema",
        ),
    ] = DAC7_SCHEMA,
) -> None:
    """
    Validate a XML file.

    Check that both name and contents conform to the DAC7 specification.
    """

    schema = xmlschema.XMLSchema10(schema_path)

    with typer.open_file(f"{xml_path}", mode="r") as xml_file:
        xml_data: str = xml_file.read()

    schema.validate(xml_data)

    xml_declaration = cast(dict[str, dict[str, str]], schema.decode(xml_data))
    message_ref_id = xml_declaration["dpi:MessageSpec"]["dpi:MessageRefId"]
    timestamp = xml_declaration["dpi:MessageSpec"]["dpi:Timestamp"]
    validate_filename(xml_path, message_ref_id=message_ref_id, timestamp=timestamp)


@app.command()
def name(
    xml_path: Annotated[
        Path,
        typer.Argument(
            metavar="XML_FILE",
            allow_dash=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default=False,
        ),
    ],
    declaration_id: Annotated[
        int,
        typer.Option(
            "--declaration-id",
            "-d",
            metavar="ID",
            help="Unique id or serial number.",
        ),
    ] = 1,
    file_format: Annotated[
        FileFormat,
        typer.Option(
            "--format",
            "-f",
            help="Format of the file.",
        ),
    ] = FileFormat.XML,
    schema_path: Annotated[
        Path,
        typer.Option(
            "--xsd",
            "-x",
            metavar="SCHEMA",
            envvar="DAC7_SCHEMA",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="XSD schema to use.",
            show_default="built-in schema",
        ),
    ] = DAC7_SCHEMA,
) -> None:
    """
    Return the expected name of the declaration file.
    """

    with typer.open_file(f"{xml_path}", mode="r") as xml_file:
        xml_data: str = xml_file.read()

    filename = build_filename_from_xml_data(
        xml_data=xml_data,
        file_format=file_format,
        schema_path=schema_path,
        declaration_id=declaration_id,
    )

    typer.echo(filename)


@app.command()
def build(
    env: Annotated[
        Env,
        typer.Option(
            "--env",
            "-E",
            envvar="ENV",
            help="Environment for which the file is built.",
            show_default=False,
        ),
    ],
    platform_path: Annotated[
        Path,
        typer.Option(
            "--platform-operator",
            "-p",
            metavar="PLATFORM_JSON",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="JSON file with the designated platform operator data",
            show_default=False,
        ),
    ],
    other_platforms_path: Annotated[
        Optional[Path],
        typer.Option(
            "--other-platform-operators",
            "-o",
            metavar="OTHER_PLATFORMS_JSON",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="JSON file with the assuming or assumed platforms data",
            show_default=False,
        ),
    ] = None,
    entity_sellers_path: Annotated[
        Optional[Path],
        typer.Option(
            "--entity-sellers",
            "-e",
            metavar="ENTITIES_JSON",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="JSON file with the entity sellers data",
            show_default=False,
        ),
    ] = None,
    individual_sellers_path: Annotated[
        Optional[Path],
        typer.Option(
            "--individual-sellers",
            "-i",
            metavar="INDIVIDUALS_JSON",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="JSON file with the individual sellers data",
            show_default=False,
        ),
    ] = None,
    declaration_id: Annotated[
        int,
        typer.Option(
            "--declaration-id",
            "-d",
            metavar="ID",
            help="Unique id or serial number.",
        ),
    ] = 1,
    fiscal_year: Annotated[
        int,
        typer.Option(
            "--fiscal-year",
            "-y",
            metavar="YEAR",
            help="Fiscal year",
        ),
    ] = datetime.now(UTC).year
    - 1,
    timestamp: Annotated[
        Optional[datetime],
        typer.Option(
            "--timestamp",
            "-t",
            formats=[r"%Y-%m-%dT%H:%M:%S.%f"],
            help="Timestamp of the declaration.",
            show_default="now",
        ),
    ] = None,
    output_format: Annotated[
        FileFormat,
        typer.Option(
            "--format",
            "-f",
            help="Format of the output.",
        ),
    ] = FileFormat.XML,
    output_file_path: Annotated[
        Optional[Path],
        typer.Argument(
            metavar="[OUTPUT_FILE]",
            allow_dash=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default="stdout",
        ),
    ] = None,
) -> None:
    """
    Build a XML or JSON declaration from simple, flat JSON files.

    The expected schemas for the JSON input files are available, see: dac7 schemas build --help.
    """

    result = build_json(
        env=env,
        platform_path=platform_path,
        other_platforms_path=other_platforms_path,
        entity_sellers_path=entity_sellers_path,
        individual_sellers_path=individual_sellers_path,
        declaration_id=declaration_id,
        fiscal_year=fiscal_year,
        timestamp=timestamp,
    )

    if output_format == FileFormat.XML:
        result = json_to_xml(result, schema_path=DAC7_SCHEMA)

    with typer.open_file(f"{output_file_path or '-'}", mode="w") as output_file:
        output_file.write(result)


@app.command()
def encrypt(
    env: Annotated[
        Env,
        typer.Option(
            "--env",
            "-E",
            envvar="ENV",
            help="Environment for which the file is encrypted.",
            show_default=False,
        ),
    ],
    input_file_path: Annotated[
        Path,
        typer.Argument(
            metavar="INPUT_FILE",
            allow_dash=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default=False,
        ),
    ],
    compression_requested: Annotated[
        bool,
        typer.Option(
            "--gzip",
            "-z",
            help="Compress the input file with GZIP before encrypting it.",
        ),
    ] = False,
    output_file_path: Annotated[
        Optional[Path],
        typer.Argument(
            metavar="[OUTPUT_FILE]",
            allow_dash=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default="stdout",
        ),
    ] = None,
) -> None:
    """
    Encrypt a DAC7 file, optionally after GZIP compression.

    Requires GnuPG to be installed.
    """

    with typer.open_file(f"{input_file_path}", mode="rb") as input_file:
        input_data: bytes = input_file.read()

    result = encrypt_data(
        env=env,
        input_data=input_data,
        compression_requested=compression_requested,
    )

    with typer.open_file(f"{output_file_path or '-'}", mode="wb") as output_file:
        output_file.write(result)


# Development tools


@app.command()
def json2xml(
    json_path: Annotated[
        Path,
        typer.Argument(
            metavar="JSON_FILE",
            allow_dash=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    schema_path: Annotated[
        Path,
        typer.Option(
            "--xsd",
            "-x",
            metavar="SCHEMA",
            envvar="DAC7_SCHEMA",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="XSD schema to use.",
            show_default="built-in schema",
        ),
    ] = DAC7_SCHEMA,
) -> None:
    """
    Transform a JSON file following the DAC7 schema into XML.
    """

    with typer.open_file(f"{json_path}") as json_file:
        json_data: str = json_file.read()

    DpiDeclaration.model_validate_json(json_data)

    result = json_to_xml(json_data, schema_path=schema_path)
    typer.echo(result)


@app.command()
def xml2json(
    xml_path: Annotated[
        Path,
        typer.Argument(
            metavar="XML_FILE",
            allow_dash=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    schema_path: Annotated[
        Path,
        typer.Option(
            "--xsd",
            "-x",
            metavar="SCHEMA",
            envvar="DAC7_SCHEMA",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            help="XSD schema to use.",
            show_default="built-in schema",
        ),
    ] = DAC7_SCHEMA,
) -> None:
    """
    Read an XML file and output it as JSON.
    """
    xml_schema = xmlschema.XMLSchema(schema_path)
    json_data = xmlschema.to_dict(xml_path, schema=xml_schema)
    typer.echo(json.dumps(json_data, indent=4))


schemas_app = typer.Typer()
app.add_typer(
    schemas_app,
    name="schemas",
    help="Display JSON schemas expected by the tool.",
)


@schemas_app.command("json2xml")
def show_json2xml_schema():
    """
    JSON schema expected by json2xml command.
    """
    typer.echo(json.dumps(DpiDeclaration.model_json_schema(), indent=4))


build_schemas_app = typer.Typer()
schemas_app.add_typer(
    build_schemas_app,
    name="build",
    help="JSON schemas expected by build command.",
)


@build_schemas_app.command("platform-operator")
def show_platform_schema():
    """
    JSON schema for --platform-operator input.
    """
    typer.echo(json.dumps(PlatformOperator.model_json_schema(), indent=4))


@build_schemas_app.command("other-platform-operators")
def show_others_schema():
    """
    JSON schema for --other-platform-operators input.
    """
    typer.echo(json.dumps(OtherPlatformOperators.model_json_schema(), indent=4))


@build_schemas_app.command("entity-sellers")
def show_entity_sellers_schema():
    """
    JSON schema for --entity-sellers input.
    """
    typer.echo(json.dumps(ReportableEntitySeller.model_json_schema(), indent=4))


@build_schemas_app.command("individual-sellers")
def show_individual_sellers_schema():
    """
    JSON schema for --individual-sellers input.
    """
    typer.echo(json.dumps(ReportableIndividualSeller.model_json_schema(), indent=4))
