#!/usr/bin/env bash

set -euxo pipefail

TEMP_FILENAME="${OUTPUT_DIR}/.declaration.xml"


# Build declaration

"${DAC7}" build \
    --env="${ENV}" \
    --declaration-id=1 \
    --fiscal-year=2025 \
    ${TIMESTAMP:+"--timestamp=${TIMESTAMP}"} \
    --platform-operator="${PLATFORM_JSON}" \
    ${OTHERS_JSON:+"--other-platform-operators=${OTHERS_JSON}"} \
    ${ENTITY_SELLERS_JSON:+"--entity-sellers=${ENTITY_SELLERS_JSON}"} \
    ${INDIVIDUAL_SELLERS_JSON:+"--individual-sellers=${INDIVIDUAL_SELLERS_JSON}"} \
    > "${TEMP_FILENAME}"


# Rename according to specification

FINAL_FILENAME="${OUTPUT_DIR}"/$("${DAC7}" name "${TEMP_FILENAME}")
mv "${TEMP_FILENAME}" "${FINAL_FILENAME}"


# Validate

"${DAC7}" validate "${FINAL_FILENAME}"


# Compress and encrypt

# "${DAC7}" encrypt -z --env="${ENV}" "${FINAL_FILENAME}" > "${FINAL_FILENAME}.gz.gpg"
