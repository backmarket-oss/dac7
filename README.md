# DAC7 (France report for 2024 earnings)

> [!CAUTION]
> All content shared in this repository is provided "as is" without any warranty of any kind from its authors.
> Users are responsible for verifying their own compliance with DAC7 obligations.

## Quick-start

```sh
poetry install

# Build a XML declaration from dedicated JSON files
poetry run dac7 build -E PROD -f XML \
                      -p platform_operator.json \
                      -o other_platform_operators.json \
                      -e entity_sellers.json \
                      -i individual_sellers.json \
                      > declaration.xml

# Rename the file according to the specification
filename=$(poetry run dac7 name declaration.xml)
mv declaration.xml ${filename}

# Validate a XML declaration, both name and content
poetry run dac7 validate ${filename}

# Compress and encrypt. Require GnuPG to be installed
poetry run dac7 encrypt -z -E PROD ${filename} > ${filename}.gz.gpg
```

## Contents of the repository

This repository is focused on the French version of DAC7, the requirements of
which have been published by the _Direction générale des Finances publiques_,
or DGFiP, on October 24, 2024 ([_cahier des charges_ v1.4][dgfip-cdc],
[schema v1.1][dgfip-schema]
:fr:).
They differ from the
[original OECD standard][oecd]
on a couple of points that are small yet enough to break compatibility
(see below).

> [!NOTE]
> Please open an issue, or even better a PR, if you would like to extend this
> repository to cover other tax authorities.

This repository contains:

- **a revised XSD schema** based on one released by DGFiP, implementing
  additional checks
- **a Python CLI** to build an XML declaration and encrypt it according to
  the DGFiP requirements

### Revised XML schema

The [DGFiP specification][dgfip-cdc] :fr: is not compatible with the
[OECD standard v1][oecd]
on at least the following points:

- The URIs for the XML namespaces `dpi` and `stf` ends with `:v1` in the OECD
  schema and not in the DGFiP schema
- The DGFiP schema uses `TaxesQn` elements instead of the `TaxQn` required by
  the OECD schema

For this reason, the French tax authority has provided its own XSD schema.
Unfortunately, its
[version v1.1][dgfip-schema]
:fr:
does not implement all the requirements stated in the
[specification document][dgfip-cdc] :fr: released at the same time.

For this reason, we provide a revised version of the French schema in the
[schemas/xml](./schemas/xml) folder that includes the following additional
checks:

1. The `version` attribute of the `<dpi:DPI_OECD>` element is mandatory, and
   its value must be `1.0`, even in the version v1.1 of the DGFiP schema
1. The value in a `<dpi:MessageRefId>` element must have between 1 and
   88 characters and contain the SIREN of the platform
1. The value in a `<ConsQn>`, `<NumbQn>`, `<FeesQn>`, or `<TaxesQn>` element
   must be greater or equal to zero
1. The value in a `<dpi:ResCountryCode>` element must be a country covered by
   DAC7, i.e. within the EU

Those schemas are adapted from the schemas included in the DGFiP specification
documents ([_Cahier des charges DPI-DAC7_][dgfip-cdc]), which are published under the
[Etalab-2.0 license](./examples/LICENSE.md).

### Python CLI

This repository also includes a Python CLI `dac7` that can be used to:

- Encrypt a French DAC7 declaration using the DGFiP keys
- Get the name an XML declaration should have to match
  [the naming convention][dgfip-naming]
  :fr: issued by DGFiP
- Check the conformity of an XML declaration with both the revised schema and
  the naming convention
- Build an XML declaration from dedicated flat JSON files:
  - A file for the main digital platform information
  - A file for the entity sellers
  - A file for the individual sellers
  - If applicable, a file for the platform assuming the declaration in place of
    the main platform, or the platforms whose declaration is assumed by it

The corresponding JSON schemas are included in the
[schemas/json](./schemas/json) folder.

## How-To

### Install and prerequisites

To run the `dac7` CLI, you need:

- Python 3.12
- Poetry 1.8.3
- GnuPG, if you want to encrypt the declaration file

It may work with other versions, maybe. Don't hesitate to open a PR to update
the documentation and/or the code!

Once you have cloned the repository, you can use [Poetry](https://python-poetry.org/) to create a virtual environment
and install the project in it with all its dependencies:

```sh
poetry install
```

Then you can explore all the available `dac7` commands with

```sh
poetry run dac7 --help
```

### Compress and encrypt an XML declaration

> [!NOTE]
> You need GnuPG to be installed on your system to be able to encrypt the file

The DGFiP test and prod platforms expect a compressed-then-encrypted file, using the corresponding test and prod
encryption keys.

The `encrypt` command can do both in one go:

```sh
poetry run dac7 encrypt -z -E PROD declaration.xml > declaration.xml.gz.gpg
```

Or, for a test file,

```sh
poetry run dac7 encrypt -z -E TEST declaration.xml > declaration.xml.gz.gpg
```

To get more help,

```sh
poetry run dac7 encrypt --help
```

### Validate an XML declaration

To check both the content of the file and its name,

```sh
poetry run dac7 validate declaration.xml
```

To get more help,

```sh
poetry run dac7 validate --help
```

### Get the expected name of an XML declaration file

If you already have a file `declaration.xml`, you can get the name it should have to match
[the DGFiP naming convention][dgfip-naming] :fr:
with

```sh
poetry run dac7 name declaration.xml
```

### Build an XML declaration from dedicated flat JSON files

The DAC7 schema is not always very practicable.
It is indeed very nested: for instance, the `<dpi:Address>` element contains the
country code in a `<dpi:CountryCode>` element and the rest of the address in
`<dpi:AddressFix>`.
When the data comes flat from a relational database, nesting it the right way
is cumbersome.

Furthermore, a DAC7 declaration mixes different elements in one file:

- The platform operator data, which is small and almost never changes
- Entity sellers, which are companies and require specific information
- Individual sellers, which require very different information

We propose to split those elements between different flat JSON files,
and then assemble them together to produce the expected XML file:

```sh
poetry run dac7 build -E PROD -f XML \
                      -p platform_operator.json \
                      [-o other_platform_operators.json] \
                      [-e entity_sellers.json] \
                      [-i individual_sellers.json] \
                      > declaration.xml
```

Compared to the XML validation performed by `dac7 validate`, some additional
2nd-level validation rules from the DGFiP specification are performed
when using `dac7 build`:

- Rule 2: one quarterly consideration is less than zero, or a seller's overall
  consideration is zero
- Rule 12: the birthplace of an individual seller is mandatory if they don't
  have a Tax Identification Number
- Rule 33: any seller needs to report at least one relevant activity
- Rule 34-1 and 34-2: a `NOTIN` value is not allowed for a platform or seller
  among other proper Tax Identification Numbers

To get more help,

```sh
poetry run dac7 build --help
```

To get the JSON schemas for each of the input files,

```sh
poetry run dac7 schemas build --help
```

### Examples

In the [examples](./examples) folder, we provide files adapted from the examples
included in the DGFiP specification documents
([_Cahier des charges DPI-DAC7_][dgfip-cdc]), which are published under the
[Etalab-2.0 license](./examples/LICENSE.md).

#### 1. Entity and individual sellers for immovable properties

[Example 1](./examples/examples/1_initial_immovable_properties) is an initial
declaration for a platform operator with one entity seller and one individual
seller, both for immovable properties.

You can rebuild the XML declaration with

```sh
poetry run dac7 build -E PROD \
   -p examples/1_initial_immovable_properties/input/platform_operator.json \
   -e examples/1_initial_immovable_properties/input/entity_sellers.json \
   -i examples/1_initial_immovable_properties/input/individual_sellers.json \
   > declaration.xml
```

#### 2. Entity and individual sellers for sale of goods

[Example 2](./examples/2_initial_sale_of_goods) is an initial declaration for a
platform operator with two entity sellers and one individual sellers, all for
the sale of goods.

You can rebuild the XML declaration with

```sh
poetry run dac7 build -E PROD \
   -p examples/2_initial_sale_of_goods/input/platform_operator.json \
   -e examples/2_initial_sale_of_goods/input/entity_sellers.json \
   -i examples/2_initial_sale_of_goods/input/individual_sellers.json \
   > declaration.xml
```

#### 3. Additional individual seller

[Example 3](./examples/3_additional) is an additional declaration for one
individual seller that was missing from the initial declaration.

You can rebuild the XML declaration with

```sh
poetry run dac7 build -E PROD \
   -p examples/3_additional/input/platform_operator.json \
   -i examples/3_additional/input/individual_sellers.json \
   > declaration.xml
```

#### 4. Correction for platform operator and individual seller

[Example 4](./examples/4_corrective) is a corrective declaration for both the
platform operator and one individual seller.

You can rebuild the XML declaration with

```sh
poetry run dac7 build -E PROD \
   -p examples/4_corrective/input/platform_operator.json \
   -i examples/4_corrective/input/individual_sellers.json \
   > declaration.xml
```

#### 5. Platform operator assuming the declaration of another

[Example 5](./examples/5_initial_assuming) is the initial declaration for a
platform operator with individual sellers, that also assumes the declaration of
another operator.

You can rebuild the XML declaration with

```sh
poetry run dac7 build -E PROD \
   -p examples/5_initial_assuming/input/platform_operator.json \
   -o examples/5_initial_assuming/input/other_platform_operators.json \
   -i examples/5_initial_assuming/input/individual_sellers.json \
   > declaration.xml
```

#### 6. Platform operator assumed by another

[Example 6](./examples/6_initial_assumed) is the initial declaration for a
platform operator whose declaration is assumed by another operator.

You can rebuild the XML declaration with

```sh
poetry run dac7 build -E PROD \
   -p examples/6_initial_assumed/input/platform_operator.json \
   -o examples/6_initial_assumed/input/other_platform_operators.json \
   > declaration.xml
```

## Development

PRs are welcome! But please take notice of the
[code of conduct](./CODE_OF_CONDUCT.md).

Use the `make` command to set up your local environment and run the tests:

```sh
# Creates the virtual environment with poetry
# Install the project and all the dependencies
# Configure the pre-commit hook
make init

# Run all the tests
make test

# Regenerate the schemas
make schemas
```

## Links

- [Original DPI Schema (v1.0)][oecd] published by the OECD
- [Directive 2021/514 of March 22, 2021](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32021L0514) amending [Directive 2011/16 of February 15, 2011 (consolidated)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02011L0016-20230101)
- [Regulation 2022/1467 of September 5,  2022](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022R1467) amending [Regulation 2015/2378 of December 15, 2015 (consolidated)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02015R2378-20230101), which includes the OECD schema
- [French specification for DPI-DAC7 data transfer][dgfip] :fr: published by DGFiP, which includes
  - a human-readable specification document
  - a schema for the content of the XML file
  - a "naming convention" for the file

[dgfip]: https://www.impots.gouv.fr/transfert-dinformations-en-application-des-dispositifs-dpi-dac7-plateformes-deconomie-collaborative
[dgfip-cdc]: https://www.impots.gouv.fr/sites/default/files/media/1_metier/3_partenaire/tiers_declarants/cdc_td_bilateral/cdc-dac7-v.1.4.pdf
[dgfip-naming]: https://www.impots.gouv.fr/sites/default/files/media/1_metier/3_partenaire/tiers_declarants/cdc_td_bilateral/nommage_collecte-dpi-dac7.pdf
[dgfip-schema]: https://www.impots.gouv.fr/sites/default/files/media/1_metier/3_partenaire/tiers_declarants/cdc_td_bilateral/schema-xsd-de-collecte-dpi-dac7---revenus-2024.zip
[oecd]: https://www.oecd.org/tax/exchange-of-tax-information/model-rules-for-reporting-by-platform-operators-with-respect-to-sellers-in-the-sharing-and-gig-economy.htm
